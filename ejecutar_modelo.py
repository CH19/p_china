"""
Standalone execution of the new quadrant-based inventory engine.
Runs the logic directly against the data files.
"""
import numpy as np
import pandas as pd
from scipy import stats
import math

PARAMETROS = {
    'flete_cbm': 85.0,
    'capacidad_contenedor_cbm': 68.0,
    'tasa_mantenimiento': 0.15,
    'costo_orden_admin': 50.0,
    'lead_time_semanas': 15,
    'ciclo_revision_semanas': 13,
    'percentil_ss': 90,
    'adi_umbral': 1.32,
    'cv2_umbral': 0.49,
    'winsor_percentil': 0.95,        # P95 de ventas positivas para acotar outliers
    'lookback_weeks': 52,            # 1 año (52 semanas) de historial para pronóstico y ROP/EOQ
}
LT = PARAMETROS['lead_time_semanas']

print("Cargando transacciones...")
reports = [i + 4 for i in range(12)]
df_temp = [pd.read_csv(f"reporte ({r}).csv", encoding="latin1", low_memory=False) for r in reports]
df_trans = pd.concat(df_temp, ignore_index=True)
col_art  = [c for c in df_trans.columns if 'digo' in c and 'rt' in c][0]
col_fecha = [c for c in df_trans.columns if 'Fecha' in c][0]
df_trans = df_trans[[col_art, col_fecha, 'Cantidad', 'Total']].copy()
df_trans.columns = ['sku', 'fecha', 'cantidad', 'total_venta']
df_trans['sku'] = df_trans['sku'].astype(str).str.strip()
df_trans['cantidad'] = pd.to_numeric(df_trans['cantidad'], errors='coerce').fillna(0.0)
df_trans['total_venta'] = pd.to_numeric(df_trans['total_venta'].astype(str).str.replace(',', ''), errors='coerce').fillna(0.0)
df_trans['fecha'] = pd.to_datetime(df_trans['fecha'], format='mixed', dayfirst=True)
df_trans = df_trans[df_trans['sku'] != 'MASS1575']

print("Cargando metadata...")
df_art = pd.read_csv('articulos.csv', encoding='latin1')
col_art_art = [c for c in df_art.columns if 'digo' in c and 'rt' in c][0]
col_exist   = [c for c in df_art.columns if 'Existencia' in c][0]
df_art = df_art[[col_art_art, col_exist]].rename(columns={col_art_art: 'sku', col_exist: 'stock_actual'})
df_art['sku'] = df_art['sku'].astype(str).str.strip()
df_art['stock_actual'] = pd.to_numeric(df_art['stock_actual'].astype(str).str.replace(',', ''), errors='coerce').fillna(0.0)
df_art = df_art.drop_duplicates(subset=['sku'], keep='last')
df_art = df_art[df_art['sku'] != 'MASS1575']

df_cons = pd.read_csv('consolidado.csv', encoding='latin1')
df_cons = df_cons[['codigo', 'costo', 'cantidad_por_caja', 'CBMM']].dropna(subset=['codigo'])
df_cons['costo'] = pd.to_numeric(df_cons['costo'].astype(str).str.replace('$','',regex=False).str.replace(',',''), errors='coerce')
df_cons['cantidad_por_caja'] = pd.to_numeric(df_cons['cantidad_por_caja'], errors='coerce')
df_cons['CBMM'] = pd.to_numeric(df_cons['CBMM'], errors='coerce')
df_cons_exp = (
    df_cons.assign(sku=df_cons['codigo'].astype(str).str.strip().str.split(r'\n|[\n\s]+'))
    .explode('sku').dropna(subset=['sku'])
)
df_cons_exp['sku'] = df_cons_exp['sku'].str.strip()
df_cons_exp = df_cons_exp[df_cons_exp['sku'] != ''].drop_duplicates(subset=['sku'], keep='last')
df_cons_exp = df_cons_exp[df_cons_exp['sku'] != 'MASS1575']
df_cons_exp = df_cons_exp[['sku', 'costo', 'cantidad_por_caja', 'CBMM']]

print("Construyendo matriz semanal...")
df_semanal = df_trans.groupby(
    ['sku', pd.Grouper(key='fecha', freq='W-MON')]
)['cantidad'].sum().unstack(fill_value=0.0)

# Edad del SKU = fin del período de observación - primera venta del SKU.
# NO se usa max(fecha_sku) - min(fecha_sku), porque eso mide la dispersión
# entre transacciones, no la antigüedad real en el catálogo.
# Un SKU con 2 ventas en 1 semana hace 3 años aparecería como "nuevo" con el
# método incorrecto.
fecha_max_dataset = df_trans['fecha'].max()
history_len = df_trans.groupby('sku')['fecha'].agg(first_sale='min')
history_len['weeks_history'] = (fecha_max_dataset - history_len['first_sale']).dt.days / 7.0

print("Calculando cuadrantes y politicas...")
resultados = []
for sku in df_semanal.index:
    ts = df_semanal.loc[sku]
    if ts.sum() == 0:
        resultados.append({'sku': sku, 'cuadrante': 'sin_datos', 'mu_incondicional': 0,
                           'adi': 0, 'cv2': np.nan, 'n_pos': 0, 'mu_sba': 0,
                           'demanda_esperada_lt': 0, 'ss_empirico': 0, 'rop': 0,
                           'mu_semanal_global': 0.0, 'std_semanal_global': 0.0, 'n_semanas_historia': 0})
        continue

    # ts_trim: desde first_sale hasta fecha_max_dataset.
    # - Ceros ANTES de first_sale = estructurales (producto no existía). Se excluyen.
    # - Ceros DESPUÉS de first_sale = intermitencia real. Se mantienen.
    first_nonzero = ts.ne(0).idxmax()
    ts_trim = ts.loc[first_nonzero:]
    
    # Aplicar ventana de historial (lookback)
    lookback = PARAMETROS['lookback_weeks']
    if lookback is not None and len(ts_trim) > lookback:
        ts_win_slice = ts_trim.iloc[-lookback:]
    else:
        ts_win_slice = ts_trim

    n_periodos = len(ts_win_slice)       # Períodos de vida observable en la ventana
    pos_mask = ts_win_slice > 0
    pos_sales = ts_win_slice[pos_mask]
    n_pos = len(pos_sales)

    # ADI y CV² se calculan sobre datos CRUDOS (pre-winsorización) de la ventana
    # para que la clasificación de cuadrante refleje la naturaleza reciente de la demanda.
    adi = n_periodos / n_pos if n_pos > 0 else float('inf')

    if n_pos <= 1:
        cuadrante = 'sin_datos'
        cv2 = np.nan
    else:
        mu_pos = pos_sales.mean()
        std_pos = pos_sales.std(ddof=1)
        cv2 = (std_pos / mu_pos) ** 2 if mu_pos > 0 else 0

        if adi < PARAMETROS['adi_umbral'] and cv2 < PARAMETROS['cv2_umbral']:
            cuadrante = 'smooth'
        elif adi >= PARAMETROS['adi_umbral'] and cv2 < PARAMETROS['cv2_umbral']:
            cuadrante = 'intermittent'
        elif adi < PARAMETROS['adi_umbral'] and cv2 >= PARAMETROS['cv2_umbral']:
            cuadrante = 'erratic'
        else:
            cuadrante = 'lumpy'

    # ── WINSORIZACIÓN ──
    # Acotar valores extremos al P95 de ventas positivas de la ventana.
    if n_pos >= 2:
        clip_upper = pos_sales.quantile(PARAMETROS['winsor_percentil'])
        ts_win = ts_win_slice.clip(upper=clip_upper)
    else:
        ts_win = ts_win_slice.copy()

    # mu_incondicional sobre la serie WINSORIZADA
    mu_incondicional = ts_win.mean()

    # SBA correccion de sesgo (solo para intermittent)
    if cuadrante == 'intermittent' and not np.isnan(cv2) if isinstance(cv2, float) else False:
        mu_sba = mu_incondicional * (1 - cv2 / 2)
        mu_sba = max(0, mu_sba)
    else:
        mu_sba = mu_incondicional

    demanda_esperada_lt = mu_sba * LT

    # SS empírico: ventanas rodantes sobre serie WINSORIZADA en la ventana.
    if cuadrante in ('lumpy', 'intermittent') and len(ts_win) >= LT:
        rolling_demand = ts_win.rolling(window=LT).sum().dropna()
        errors = rolling_demand - demanda_esperada_lt
        ss_empirico = max(0, float(np.percentile(errors, PARAMETROS['percentil_ss'])))
    elif cuadrante in ('smooth', 'erratic') and len(ts_win) > 1:
        std_global = ts_win.std(ddof=1)
        ss_empirico = max(0, 1.645 * std_global * math.sqrt(LT))  # Z=1.645 ~ 95%
    else:
        ss_empirico = 0.0

    rop = demanda_esperada_lt + ss_empirico
    resultados.append({
        'sku': sku, 'cuadrante': cuadrante,
        'adi': round(adi, 3),
        'cv2': round(float(cv2), 4) if not (isinstance(cv2, float) and np.isnan(cv2)) else np.nan,
        'n_pos': n_pos,
        'mu_incondicional': mu_incondicional,
        'mu_sba': mu_sba,
        'demanda_esperada_lt': demanda_esperada_lt,
        'ss_empirico': ss_empirico,
        'rop': rop,
        'mu_semanal_global': ts_win_slice.mean(),
        'std_semanal_global': ts_win_slice.std(ddof=1) if len(ts_win_slice) > 1 else 0.0,
        'n_semanas_historia': len(ts_trim),
    })

df_sku = pd.DataFrame(resultados)
df_sku = df_sku.merge(
    history_len[['weeks_history']].reset_index().rename(columns={'index': 'sku'}),
    on='sku', how='left'
)

# Merge metadata
df_sku = df_sku.merge(df_art, on='sku', how='left')
df_sku['stock_actual'] = df_sku['stock_actual'].fillna(0.0)
df_sku = df_sku.merge(df_cons_exp, on='sku', how='left')
df_sku['costo_final'] = df_sku['costo'].fillna(1.0).replace(0.0, np.nan).fillna(1.0)
df_sku['cantidad_por_caja'] = df_sku['cantidad_por_caja'].fillna(1.0).clip(lower=1.0)
df_sku['CBMM'] = df_sku['CBMM'].fillna(0.05).clip(lower=0.001)

# ABC
ventas_totales_sku = df_trans.groupby('sku')['total_venta'].sum().reset_index().rename(columns={'total_venta': 'total_ventas'})
df_sku = df_sku.merge(ventas_totales_sku, on='sku', how='left')
df_sku['total_ventas'] = df_sku['total_ventas'].fillna(0)
df_sku = df_sku.sort_values('total_ventas', ascending=False).reset_index(drop=True)
tot = df_sku['total_ventas'].sum()
df_sku['pct_acum'] = df_sku['total_ventas'].cumsum() / tot if tot > 0 else 0
df_sku['clase_abc'] = np.select(
    [df_sku['pct_acum'] <= 0.50, df_sku['pct_acum'] <= 0.80, df_sku['pct_acum'] <= 0.95],
    ['AA', 'A', 'B'], default='C'
)

# Nivel de servicio
NIVEL_MAP = {'AA': 0.97, 'A': 0.95, 'B': 0.90, 'C': 0.85}
df_sku['nivel_servicio'] = df_sku['clase_abc'].map(NIVEL_MAP).fillna(0.85)

# Recalcular SS Gaussiano con Z correcto para smooth/erratic
mask_gauss = df_sku['cuadrante'].isin(['smooth', 'erratic'])
z_scores = stats.norm.ppf(df_sku.loc[mask_gauss, 'nivel_servicio'])
df_sku.loc[mask_gauss, 'ss_empirico'] = np.maximum(
    0, z_scores * df_sku.loc[mask_gauss, 'std_semanal_global'] * math.sqrt(LT)
)
df_sku.loc[mask_gauss, 'rop'] = (
    df_sku.loc[mask_gauss, 'demanda_esperada_lt'] + df_sku.loc[mask_gauss, 'ss_empirico']
)

# Cantidad a pedir
FLETE_CBM = PARAMETROS['flete_cbm']
CICLO = PARAMETROS['ciclo_revision_semanas']
df_sku['cbm_unitario'] = df_sku['CBMM'] / df_sku['cantidad_por_caja']
df_sku['costo_flete_unit'] = df_sku['cbm_unitario'] * FLETE_CBM
df_sku['costo_puesto'] = df_sku['costo_final'] + df_sku['costo_flete_unit']
df_sku['h'] = df_sku['costo_puesto'] * PARAMETROS['tasa_mantenimiento']
df_sku['demanda_anual'] = df_sku['mu_incondicional'] * 52.0
df_sku['eoq_unidades'] = np.where(
    df_sku['h'] > 0,
    np.sqrt((2 * df_sku['demanda_anual'] * PARAMETROS['costo_orden_admin']) / df_sku['h']),
    0.0
)
df_sku['cobertura_ciclo_unidades'] = df_sku['mu_incondicional'] * CICLO

mediana_cbm_caja = df_cons_exp['CBMM'].median()
df_sku['qty_base'] = np.select(
    [
        df_sku['cuadrante'].isin(['smooth', 'erratic']),
        df_sku['cuadrante'].isin(['lumpy', 'intermittent']),
    ],
    [df_sku['eoq_unidades'], df_sku['cobertura_ciclo_unidades']],
    default=df_sku['cantidad_por_caja']  # sin_datos: 1 caja minima
)

df_sku['cajas_a_pedir'] = np.ceil(df_sku['qty_base'] / df_sku['cantidad_por_caja']).clip(lower=1).astype(int)
df_sku['unidades_a_pedir'] = df_sku['cajas_a_pedir'] * df_sku['cantidad_por_caja'].astype(int)
df_sku['cbm_total_pedido'] = df_sku['cajas_a_pedir'] * df_sku['CBMM']
df_sku['inversion_fob_usd'] = df_sku['unidades_a_pedir'] * df_sku['costo_final']

# Decision de reorden
df_sku['posicion_inventario'] = df_sku['stock_actual']
df_sku['requiere_pedido'] = df_sku['posicion_inventario'] <= df_sku['rop']
df_sku['estado'] = np.where(df_sku['requiere_pedido'], 'REORDENAR', 'OK')
for col in ['cajas_a_pedir', 'unidades_a_pedir', 'cbm_total_pedido', 'inversion_fob_usd']:
    df_sku[col] = np.where(df_sku['requiere_pedido'], df_sku[col], 0)

# Exportar
columnas_export = [
    'sku', 'cuadrante', 'clase_abc', 'nivel_servicio',
    'stock_actual', 'rop', 'demanda_esperada_lt', 'ss_empirico',
    'mu_incondicional', 'mu_sba', 'adi', 'cv2', 'n_pos', 'n_semanas_historia', 'weeks_history',
    'cajas_a_pedir', 'unidades_a_pedir', 'cbm_total_pedido', 'inversion_fob_usd',
    'costo_final', 'cantidad_por_caja', 'CBMM', 'estado', 'requiere_pedido'
]
df_export = df_sku[[c for c in columnas_export if c in df_sku.columns]].copy()
df_export = df_export.rename(columns={'sku': 'Codigo Articulo'})
df_export.to_csv('pedidos_requeridos.csv', index=False, encoding='utf-8-sig')

print("=" * 60)
print("MOTOR CUADRANTE - RESUMEN FINAL")
print("=" * 60)
print("\nDistribucion cuadrantes:")
print(df_sku['cuadrante'].value_counts().to_string())
print(f"\nSKUs totales procesados:  {len(df_sku)}")
print(f"SKUs que requieren orden: {df_sku['requiere_pedido'].sum()}")
print(f"Inversion total FOB:      ${df_sku['inversion_fob_usd'].sum():,.0f}")
print(f"CBM total pedidos:        {df_sku['cbm_total_pedido'].sum():,.1f}")
print(f"Contenedores estimados:   {df_sku['cbm_total_pedido'].sum() / 68.0:.1f}")
print(f"\nValidacion MASS2221:")
m = df_sku[df_sku['sku'] == 'MASS2221']
if len(m):
    r = m.iloc[0]
    print(f"  Cuadrante:               {r['cuadrante']}")
    print(f"  mu_incondicional (sem):  {r['mu_incondicional']:.4f}")
    print(f"  Demanda esperada LT:     {r['demanda_esperada_lt']:.2f}")
    print(f"  SS empirico P90:         {r['ss_empirico']:.2f}")
    print(f"  ROP NUEVO:               {r['rop']:.2f}   <-- (anterior: 6.87)")
else:
    print("  MASS2221 no encontrado")
print("\npedidos_requeridos.csv actualizado.")

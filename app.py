import streamlit as st
import pandas as pd
import numpy as np
import math
import os
from scipy import stats
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Configuracion de pagina Masshopping
st.set_page_config(
    page_title="Masshopping Admin | Planificador Logistico & Contenedores",
    page_icon="Masshoping_logo.png" if os.path.exists("Masshoping_logo.png") else "\U0001F4E6",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS Personalizados con la paleta de Masshopping (#5AA06E / #141E32)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Header principal */
    .masshopping-header {
        background: linear-gradient(135deg, #141E32 0%, #1D2E45 60%, #2A4535 100%);
        color: white;
        padding: 18px 24px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 18px;
        box-shadow: 0 4px 15px rgba(20, 30, 50, 0.12);
        border: 1px solid rgba(90, 160, 110, 0.25);
    }
    
    .masshopping-title {
        font-size: 23px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        color: #FFFFFF;
    }
    
    .masshopping-subtitle {
        font-size: 13px;
        color: #A3D4B1;
        margin-top: 3px;
        font-weight: 500;
    }
    
    .badge-brand {
        background-color: #5AA06E;
        color: #FFFFFF;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    /* Tarjetas de Metricas de Contenedor */
    .metric-box {
        background: #FFFFFF;
        border: 1px solid #D5E7DB;
        border-top: 4px solid #5AA06E;
        border-radius: 10px;
        padding: 14px 16px;
        box-shadow: 0 2px 6px rgba(90, 160, 110, 0.08);
    }
    
    .metric-label {
        font-size: 11px;
        font-weight: 700;
        color: #5A6E60;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-value {
        font-size: 22px;
        font-weight: 800;
        color: #141E32;
        margin-top: 2px;
        white-space: nowrap;
        overflow: visible;
    }
    
    .metric-delta {
        font-size: 11px;
        font-weight: 600;
        color: #5AA06E;
        margin-top: 2px;
    }
    
    /* Cuadricula de KPIs para la Ficha de Producto */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
        margin-top: 10px;
    }
    
    .kpi-card {
        background: #F4F8F5;
        border: 1px solid #D5E7DB;
        border-radius: 8px;
        padding: 10px 8px;
        text-align: center;
    }
    
    .kpi-title {
        font-size: 10.5px;
        font-weight: 700;
        color: #5A6E60;
        text-transform: uppercase;
        margin-bottom: 3px;
        line-height: 1.2;
    }
    
    .kpi-number {
        font-size: 16px;
        font-weight: 800;
        color: #141E32;
        white-space: nowrap;
        overflow: visible;
    }
    
    .badge-status-reorden {
        background-color: #E65100;
        color: white;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 800;
        display: inline-block;
    }
    
    .badge-status-ok {
        background-color: #2E7D32;
        color: white;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 800;
        display: inline-block;
    }
    
    /* Chips de Multiselect Compactos */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #EAF3ED !important;
        border: 1px solid #5AA06E !important;
        color: #141E32 !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        border-radius: 6px !important;
        padding: 1px 6px !important;
        margin: 1px !important;
    }
    
    /* Botones primarios */
    .stButton > button, .stDownloadButton > button {
        background: linear-gradient(135deg, #5AA06E 0%, #467864 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 8px 20px !important;
        font-size: 13px !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 3px 8px rgba(90, 160, 110, 0.25) !important;
    }
    
    .stButton > button:hover, .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #6AB57F 0%, #528C74 100%) !important;
        transform: translateY(-1px);
        box-shadow: 0 5px 12px rgba(90, 160, 110, 0.35) !important;
    }
    
    /* Barra de progreso Masshopping */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #5AA06E 0%, #438855 100%) !important;
    }
    
    /* Footer */
    .masshopping-footer {
        text-align: center;
        padding: 25px 0 10px 0;
        color: #6C8274;
        font-size: 12px;
        font-weight: 500;
        border-top: 1px solid #D5E7DB;
        margin-top: 35px;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 1. FUNCION DE LIMPIEZA DE TEXTO (CORRIGE MOJIBAKE EN TILDES Y N)
# ══════════════════════════════════════════════════════════════════════════════
def limpiar_mojibake(texto):
    if not isinstance(texto, str):
        return ''
    if any(m in texto for m in ['Ã¡', 'Ã©', 'Ã\xad', 'Ã³', 'Ãº', 'Ã±', 'Ã\xad', 'Ã\x81', 'Ã\x89', 'Ã\x8d', 'Ã\x93', 'Ã\x9a', 'Ã\x91', 'Â']):
        try:
            return texto.encode('latin1').decode('utf-8')
        except Exception:
            pass
    reemplazos = {
        'Ã¡': 'a', 'Ã©': 'e', 'Ã\xad': 'i', 'Ã³': 'o', 'Ãº': 'u',
        'Ã\x81': 'A', 'Ã\x89': 'E', 'Ã\x8d': 'I',
        'Ã\x93': 'O', 'Ã\x9a': 'U', 'Ã±': 'n', 'Ã\x91': 'N',
        'Â°': '', 'Â': '', '\xe2\x80\x93': '-', '\xe2\x80\x99': "'",
    }
    for k, v in reemplazos.items():
        texto = texto.replace(k, v)
    return texto

# ══════════════════════════════════════════════════════════════════════════════
# 2. CARGA DE DATOS EN CACHE
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="Cargando base de datos Masshopping...")
def cargar_datos_base():
    # 1. Transacciones
    reports = [i + 4 for i in range(12)]
    df_temp = [pd.read_csv(f"reporte ({r}).csv", encoding="latin1", low_memory=False) for r in reports]
    df_trans = pd.concat(df_temp, ignore_index=True)
    
    col_art = [c for c in df_trans.columns if 'digo' in c and 'rt' in c][0]
    col_fecha = [c for c in df_trans.columns if 'Fecha' in c][0]
    col_nom_trans = [c for c in df_trans.columns if 'ombre' in c and 'rt' in c][0]
    
    df_clean = df_trans[[col_art, col_fecha, col_nom_trans, 'Cantidad', 'Total', 'Total Costo', 'Costo Unitario']].copy()
    df_clean.columns = ['sku', 'fecha', 'nombre_trans', 'cantidad', 'total_venta', 'total_costo', 'costo_unit_trans']
    df_clean['sku'] = df_clean['sku'].astype(str).str.strip()
    df_clean['nombre_trans'] = df_clean['nombre_trans'].astype(str).apply(limpiar_mojibake)
    df_clean['cantidad'] = pd.to_numeric(df_clean['cantidad'], errors='coerce').fillna(0.0)
    df_clean['total_venta'] = pd.to_numeric(df_clean['total_venta'].astype(str).str.replace(',', ''), errors='coerce').fillna(0.0)
    df_clean['total_costo'] = pd.to_numeric(df_clean['total_costo'].astype(str).str.replace(',', ''), errors='coerce').fillna(0.0)
    df_clean['costo_unit_trans'] = pd.to_numeric(df_clean['costo_unit_trans'].astype(str).str.replace(',', ''), errors='coerce').fillna(0.0)
    df_clean['fecha'] = pd.to_datetime(df_clean['fecha'], format='mixed', dayfirst=True)
    df_clean = df_clean[df_clean['sku'] != 'MASS1575']
    
    # 2. Extraer fallback de nombres de las transacciones
    df_nombres_trans = df_clean[['sku', 'nombre_trans']].drop_duplicates(subset=['sku'], keep='last')
    
    # 2b. Articulos (Stock actual, Categoria y Nombre)
    df_art = pd.read_csv('articulos.csv', encoding='latin1')
    col_art_art = [c for c in df_art.columns if 'digo' in c and 'rt' in c][0]
    col_exist = [c for c in df_art.columns if 'Existencia' in c][0]
    col_nom_art = [c for c in df_art.columns if ('rt' in c or 'culo' in c) and 'digo' not in c][0]
    col_cat = [c for c in df_art.columns if 'teg' in c.lower() and 'digo' not in c.lower()][0]
    
    df_art_clean = df_art[[col_art_art, col_exist, col_nom_art, col_cat]].rename(
        columns={col_art_art: 'sku', col_exist: 'stock_actual', col_nom_art: 'nombre_articulo', col_cat: 'categoria'}
    )
    df_art_clean['sku'] = df_art_clean['sku'].astype(str).str.strip()
    df_art_clean['stock_actual'] = pd.to_numeric(df_art_clean['stock_actual'].astype(str).str.replace(',', ''), errors='coerce').fillna(0.0)
    df_art_clean['nombre_articulo'] = df_art_clean['nombre_articulo'].astype(str).apply(limpiar_mojibake)
    df_art_clean['categoria'] = df_art_clean['categoria'].fillna('GENERAL').astype(str).str.strip()
    df_art_clean = df_art_clean.drop_duplicates(subset=['sku'], keep='last')
    df_art_clean = df_art_clean[df_art_clean['sku'] != 'MASS1575']
    
    # 3. Metadata logistica + Stock en Transito
    df_cons = pd.read_csv('consolidado.csv', encoding='latin1')
    
    # Extraer stock en transito (CONTENEDORES JULIO + CONTENEDOR EGIPTO)
    contenedores_transito = ['CONTENEDORES JULIO', 'CONTENEDOR EGIPTO']
    df_transit = df_cons[df_cons['contenedor'].isin(contenedores_transito)].copy()
    df_transit['codigo'] = df_transit['codigo'].astype(str).str.strip()
    df_transit['cantidad'] = pd.to_numeric(df_transit['cantidad'], errors='coerce').fillna(0)
    # Explode multi-sku codes (e.g. "MASS2305 MASS2405 MASS2699")
    df_transit_exp = (
        df_transit.assign(sku=df_transit['codigo'].str.split(r'\n|[\n\s]+'))
        .explode('sku').dropna(subset=['sku'])
    )
    df_transit_exp['sku'] = df_transit_exp['sku'].str.strip()
    df_transit_exp = df_transit_exp[df_transit_exp['sku'] != '']
    # Sum transit quantities per SKU (could be in both containers)
    df_stock_transito = df_transit_exp.groupby('sku')['cantidad'].sum().reset_index()
    df_stock_transito.columns = ['sku', 'stock_transito']
    df_stock_transito = df_stock_transito[df_stock_transito['sku'] != 'MASS1575']
    
    # Metadata de costos/empaque (todas las filas)
    df_cons_meta = df_cons[['codigo', 'costo', 'cantidad_por_caja', 'CBMM']].dropna(subset=['codigo'])
    df_cons_meta['costo'] = pd.to_numeric(df_cons_meta['costo'].astype(str).str.replace('$', '', regex=False).str.replace(',', ''), errors='coerce')
    df_cons_meta['cantidad_por_caja'] = pd.to_numeric(df_cons_meta['cantidad_por_caja'], errors='coerce')
    df_cons_meta['CBMM'] = pd.to_numeric(df_cons_meta['CBMM'], errors='coerce')
    df_cons_exp = (
        df_cons_meta.assign(sku=df_cons_meta['codigo'].astype(str).str.strip().str.split(r'\n|[\n\s]+'))
        .explode('sku').dropna(subset=['sku'])
    )
    df_cons_exp['sku'] = df_cons_exp['sku'].str.strip()
    df_cons_exp = df_cons_exp[df_cons_exp['sku'] != ''].drop_duplicates(subset=['sku'], keep='last')
    df_metadata = df_cons_exp[['sku', 'costo', 'cantidad_por_caja', 'CBMM']]
    df_metadata = df_metadata[df_metadata['sku'] != 'MASS1575']
    
    # 4. Catalogo de Imagenes y Nombres (IMAGES.csv)
    df_images = pd.read_csv('IMAGES.csv', encoding='latin1')
    df_images = df_images[['CODIGO', 'NOMBRE', 'IMAGEN']].rename(
        columns={'CODIGO': 'sku', 'NOMBRE': 'nombre', 'IMAGEN': 'imagen_url'}
    )
    df_images['sku'] = df_images['sku'].astype(str).str.strip()
    df_images['nombre'] = df_images['nombre'].astype(str).apply(limpiar_mojibake)
    df_images['imagen_url'] = df_images['imagen_url'].astype(str).str.strip()
    df_images = df_images.drop_duplicates(subset=['sku'], keep='last')
    
    # Unir informacion descriptiva
    df_info_prod = pd.merge(df_images, df_art_clean[['sku', 'nombre_articulo', 'categoria']], on='sku', how='outer')
    df_info_prod = pd.merge(df_info_prod, df_nombres_trans, on='sku', how='outer')
    
    # Prioridad: IMAGES -> articulos.csv -> reporte transacciones -> 'Sin Descripcion'
    df_info_prod['nombre_final'] = df_info_prod['nombre'].fillna(df_info_prod['nombre_articulo']).fillna(df_info_prod['nombre_trans']).fillna('Sin Descripcion')
    df_info_prod['nombre'] = df_info_prod['nombre_final'].replace('nan', 'Sin Descripcion')
    df_info_prod['categoria'] = df_info_prod['categoria'].fillna('GENERAL')
    df_info_prod = df_info_prod[['sku', 'nombre', 'categoria', 'imagen_url']]
    
    import json
    try:
        with open('p2p.json', 'r', encoding='utf-8') as f:
            p2p_data = json.load(f)
        
        dates = pd.to_datetime(p2p_data['categories'])
        sell_item = next(item for item in p2p_data['items'] if 'SELL' in item['tm'])
        p2p_values = sell_item['values']
        
        df_p2p = pd.DataFrame({'fecha': dates, 'usd_rate': p2p_values})
        df_p2p = df_p2p.sort_values('fecha').drop_duplicates('fecha', keep='last')
        df_p2p['var_pct'] = df_p2p['usd_rate'].pct_change() * 100
        df_p2p['var_pct'] = df_p2p['var_pct'].fillna(0)
    except Exception as e:
        # Fallback empty df in case file is missing or structure changes
        df_p2p = pd.DataFrame({'fecha': [], 'usd_rate': [], 'var_pct': []})
    
    return df_clean, df_art_clean[['sku', 'stock_actual', 'categoria']], df_metadata, df_info_prod, df_stock_transito, df_p2p

df_trans, df_art, df_metadata, df_info_prod, df_stock_transito, df_p2p = cargar_datos_base()

# Excluir de forma global y permanente el SKU MASS1350 de todo el sistema
df_trans = df_trans[df_trans['sku'] != 'MASS1350']
df_art = df_art[df_art['sku'] != 'MASS1350']

# ══════════════════════════════════════════════════════════════════════════════
# 3. SIDEBAR CORPORATIVO MASSHOPPING
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    if os.path.exists("Masshoping_logo.png"):
        st.image("Masshoping_logo.png", width=170)
    st.markdown("### Motor de logística para compras masivas")
    st.caption("Panel de Control y Compras Estratégicas")
    st.divider()
    
    st.subheader("Ventana Temporal de Demanda")
    opcion_tiempo = st.selectbox(
        "Período analizado:",
        ["Último Año", "Últimos 6 meses", "Últimos 3 meses", "Todo el historial"],
        key="sidebar_periodo"
    )
    
    fecha_max = df_trans['fecha'].max()
    if "Año" in opcion_tiempo:
        fecha_corte = fecha_max - pd.DateOffset(years=1)
        df_trans_filtrada = df_trans[df_trans['fecha'] >= fecha_corte].copy()
    elif "6 meses" in opcion_tiempo:
        fecha_corte = fecha_max - pd.DateOffset(months=6)
        df_trans_filtrada = df_trans[df_trans['fecha'] >= fecha_corte].copy()
    elif "3 meses" in opcion_tiempo:
        fecha_corte = fecha_max - pd.DateOffset(months=3)
        df_trans_filtrada = df_trans[df_trans['fecha'] >= fecha_corte].copy()
    else:
        df_trans_filtrada = df_trans.copy()
        
    st.divider()
    st.subheader("Configuración de Pronóstico")
    opcion_lookback = st.selectbox(
        "Historial para ROP y EOQ:",
        ["Últimas 52 semanas (1 año)", "Últimas 26 semanas (6 meses)", "Últimas 12 semanas (3 meses)", "Todo el historial disponible"],
        key="sidebar_lookback"
    )
    
    if "52" in opcion_lookback:
        lookback_weeks = 52
    elif "26" in opcion_lookback:
        lookback_weeks = 26
    elif "12" in opcion_lookback:
        lookback_weeks = 12
    else:
        lookback_weeks = None
    
    st.divider()
    st.subheader("Parámetros del Contenedor")
    capacidad_cont = st.number_input("Capacidad Contenedor 40HQ (CBM):", value=68.0, step=1.0)
    flete_cbm = st.number_input("Flete por CBM (USD):", value=500.0, step=5.0)
    lead_time = st.slider("Lead Time Proveedor (Semanas):", min_value=1, max_value=30, value=15)
    costo_orden = st.number_input("Costo Administrativo Orden (USD):", value=50.0, step=5.0)
    tasa_mant = st.slider("Tasa Mantenimiento Inv. (% anual):", min_value=0.05, max_value=0.40, value=0.15, step=0.01)
    
    st.divider()
    st.caption("Masshopping Supply Chain Portal v3.0")

# ══════════════════════════════════════════════════════════════════════════════
# 4. MOTOR VECTORIZADO DE CALCULO
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def ejecutar_motor(df_t, _df_a, _df_m, _df_info, _df_transit, lt, flete, cap_cont, tasa, c_orden, lookback_weeks):
    df_semanal = df_t.groupby(['sku', pd.Grouper(key='fecha', freq='W-MON')])['cantidad'].sum().unstack(fill_value=0.0)
    
    # ── CÁLCULO SKU POR SKU (Alineado con ejecutar_modelo.py) ──
    resultados = []
    adi_umbral = 1.32
    cv2_umbral = 0.49
    percentil_ss = 90
    winsor_percentil = 0.95
    
    for sku in df_semanal.index:
        ts = df_semanal.loc[sku]
        if ts.sum() == 0:
            resultados.append({
                'sku': sku, 'cuadrante': 'sin_datos', 'adi': 0, 'cv': np.nan, 'n_pos': 0,
                'demanda_semanal_prom': 0.0, 'demanda_semanal_std': 0.0, 'mu_sba': 0.0,
                'demanda_esperada_lt': 0.0, 'ss_empirico': 0.0, 'rop': 0.0
            })
            continue

        first_nonzero = ts.ne(0).idxmax()
        ts_trim = ts.loc[first_nonzero:]
        
        # Limitar a lookback_weeks
        if lookback_weeks is not None and len(ts_trim) > lookback_weeks:
            ts_win_slice = ts_trim.iloc[-lookback_weeks:]
        else:
            ts_win_slice = ts_trim
            
        n_periodos = len(ts_win_slice)
        pos_mask = ts_win_slice > 0
        pos_sales = ts_win_slice[pos_mask]
        n_pos = len(pos_sales)
        
        adi = n_periodos / n_pos if n_pos > 0 else float('inf')
        
        if n_pos <= 1:
            cuadrante = 'sin_datos'
            cv2 = np.nan
            cv = np.nan
        else:
            mu_pos = pos_sales.mean()
            std_pos = pos_sales.std(ddof=1)
            cv2 = (std_pos / mu_pos) ** 2 if mu_pos > 0 else 0
            cv = std_pos / mu_pos if mu_pos > 0 else 0
            
            if adi < adi_umbral and cv2 < cv2_umbral:
                cuadrante = 'smooth'
            elif adi >= adi_umbral and cv2 < cv2_umbral:
                cuadrante = 'intermittent'
            elif adi < adi_umbral and cv2 >= cv2_umbral:
                cuadrante = 'erratic'
            else:
                cuadrante = 'lumpy'
                
        # Winsorización
        if n_pos >= 2:
            clip_upper = pos_sales.quantile(winsor_percentil)
            ts_win = ts_win_slice.clip(upper=clip_upper)
        else:
            ts_win = ts_win_slice.copy()
            
        mu_incondicional = ts_win.mean()
        
        # SBA
        if cuadrante == 'intermittent' and not np.isnan(cv2):
            mu_sba = mu_incondicional * (1 - cv2 / 2)
            mu_sba = max(0, mu_sba)
        else:
            mu_sba = mu_incondicional
            
        demanda_esperada_lt = mu_sba * lt
        
        # SS empírico para lumpy/intermittent
        if cuadrante in ('lumpy', 'intermittent') and len(ts_win) >= lt:
            rolling_demand = ts_win.rolling(window=lt).sum().dropna()
            errors = rolling_demand - demanda_esperada_lt
            ss_empirico = max(0, float(np.percentile(errors, percentil_ss)))
        else:
            ss_empirico = 0.0 # Se refinará para Smooth/Erratic después de asignar clase_abc y nivel_servicio
            
        rop = demanda_esperada_lt + ss_empirico
        
        resultados.append({
            'sku': sku,
            'cuadrante': cuadrante,
            'adi': adi,
            'cv': cv if not np.isnan(cv) else 0.0,
            'n_pos': n_pos,
            'demanda_semanal_prom': mu_incondicional,
            'demanda_semanal_std': ts_win_slice.std(ddof=1) if len(ts_win_slice) > 1 else 0.0,
            'mu_sba': mu_sba,
            'demanda_esperada_lt': demanda_esperada_lt,
            'ss_empirico': ss_empirico,
            'rop': rop
        })
        
    df_calc = pd.DataFrame(resultados)
    
    # ── COMBINACIÓN CON METADATA Y CLASIFICACIONES ──
    ventas = df_t.groupby('sku').agg(
        total_ventas=('total_venta', 'sum'),
        total_unidades=('cantidad', 'sum'),
        costo_unit_trans_prom=('costo_unit_trans', 'mean')
    ).reset_index()
    
    df_calc = pd.merge(df_calc, ventas, on='sku', how='left')
    df_calc = pd.merge(df_calc, _df_a[['sku', 'stock_actual']], on='sku', how='left')
    df_calc['stock_actual'] = df_calc['stock_actual'].fillna(0.0)
    
    # Stock en Transito
    df_calc = pd.merge(df_calc, _df_transit, on='sku', how='left')
    df_calc['stock_transito'] = df_calc['stock_transito'].fillna(0.0)
    df_calc['stock_total_disponible'] = df_calc['stock_actual'] + df_calc['stock_transito']
    
    df_calc = pd.merge(df_calc, _df_m, on='sku', how='left')
    df_calc['costo'] = df_calc['costo'].fillna(df_calc['costo_unit_trans_prom']).replace(0.0, np.nan).fillna(1.0)
    df_calc['cantidad_por_caja'] = pd.to_numeric(df_calc['cantidad_por_caja'], errors='coerce').fillna(1).clip(lower=1).astype(int)
    df_calc['CBMM'] = df_calc['CBMM'].fillna(0.05).clip(lower=0.001)
    
    df_calc = pd.merge(df_calc, _df_info, on='sku', how='left')
    df_calc['nombre'] = df_calc['nombre'].fillna('Sin Nombre')
    df_calc['categoria'] = df_calc['categoria'].fillna('GENERAL')
    df_calc['imagen_url'] = df_calc['imagen_url'].fillna('')
    
    # ABC
    df_calc = df_calc.sort_values('total_ventas', ascending=False).reset_index(drop=True)
    v_tot = df_calc['total_ventas'].sum()
    pct_acum = (df_calc['total_ventas'] / v_tot).cumsum() if v_tot > 0 else 0
    df_calc['clase_abc'] = np.select(
        [pct_acum <= 0.50, pct_acum <= 0.80, pct_acum <= 0.95],
        ['AA', 'A', 'B'], default='C'
    )
    
    # XYZ
    df_calc['clase_xyz'] = np.select(
        [df_calc['cv'] <= 0.5, df_calc['cv'] <= 1.0],
        ['X', 'Y'], default='Z'
    )
    df_calc['clase_abc_xyz'] = df_calc['clase_abc'] + '-' + df_calc['clase_xyz']
    
    # Nivel de Servicio
    ns_map = {
        ('AA', 'X'): 0.98, ('AA', 'Y'): 0.97, ('AA', 'Z'): 0.95,
        ('A',  'X'): 0.95, ('A',  'Y'): 0.93, ('A',  'Z'): 0.90,
        ('B',  'X'): 0.90, ('B',  'Y'): 0.88, ('B',  'Z'): 0.85,
        ('C',  'X'): 0.85, ('C',  'Y'): 0.80, ('C',  'Z'): 0.75,
    }
    df_calc['nivel_servicio'] = [ns_map.get((a, x), 0.85) for a, x in zip(df_calc['clase_abc'], df_calc['clase_xyz'])]
    
    # Recalcular ROP y SS Gaussiano para Smooth/Erratic con Z dinámico
    mask_gauss = df_calc['cuadrante'].isin(['smooth', 'erratic'])
    z_scores = stats.norm.ppf(df_calc.loc[mask_gauss, 'nivel_servicio'])
    df_calc.loc[mask_gauss, 'ss_empirico'] = np.maximum(
        0.0,
        z_scores * df_calc.loc[mask_gauss, 'demanda_semanal_std'] * math.sqrt(lt)
    )
    df_calc.loc[mask_gauss, 'rop'] = df_calc.loc[mask_gauss, 'demanda_esperada_lt'] + df_calc.loc[mask_gauss, 'ss_empirico']
    
    # ROP y EOQ generales
    df_calc['cbm_unitario'] = df_calc['CBMM'] / df_calc['cantidad_por_caja']
    df_calc['flete_unitario_usd'] = df_calc['cbm_unitario'] * flete
    df_calc['costo_puesto'] = df_calc['costo'] + df_calc['flete_unitario_usd']
    
    h = df_calc['costo_puesto'] * tasa
    d_anual = df_calc['demanda_semanal_prom'] * 52.0
    eoq = np.where(h > 0, np.sqrt((2 * d_anual * c_orden) / h), 0.0)
    eoq = np.nan_to_num(eoq, nan=0.0)
    
    # Decision de pedido
    df_calc['requiere_pedido'] = df_calc['stock_total_disponible'] <= df_calc['rop']
    df_calc['estado'] = np.where(df_calc['requiere_pedido'], 'REORDENAR', 'OK')
    
    cajas_sug = np.where(
        df_calc['requiere_pedido'],
        np.ceil(eoq / df_calc['cantidad_por_caja']).astype(int),
        0
    )
    df_calc['cajas_sugeridas'] = cajas_sug
    df_calc['pedir_cajas'] = df_calc['cajas_sugeridas']
    df_calc['incluir_en_pedido'] = df_calc['requiere_pedido']
    
    return df_calc

df_modelo = ejecutar_motor(df_trans_filtrada, df_art, df_metadata, df_info_prod, df_stock_transito, lead_time, flete_cbm, capacidad_cont, tasa_mant, costo_orden, lookback_weeks)

# ══════════════════════════════════════════════════════════════════════════════
# 4.5 MOTOR SECUNDARIO: AGREGACIÓN MENSUAL (Para Fichas Visuales)
# ══════════════════════════════════════════════════════════════════════════════
df_agrupado_m = df_trans_filtrada.groupby(['sku', pd.Grouper(key='fecha', freq='MS')])['cantidad'].sum().unstack(fill_value=0.0)
d_prom_m = df_agrupado_m.mean(axis=1)
d_std_m = df_agrupado_m.std(axis=1, ddof=1).fillna(0.0)
cv_m = np.where(d_prom_m > 0, d_std_m / d_prom_m, 0.0)

df_mensual_abc_xyz = pd.DataFrame({'sku': df_agrupado_m.index, 'demanda_mensual_prom': d_prom_m.values, 'cv': cv_m})
df_mensual_abc_xyz = pd.merge(df_mensual_abc_xyz, df_modelo[['sku', 'nombre', 'categoria', 'clase_abc', 'total_ventas', 'requiere_pedido']], on='sku', how='inner')

df_mensual_abc_xyz['clase_xyz'] = np.select(
    [df_mensual_abc_xyz['cv'] <= 0.5, df_mensual_abc_xyz['cv'] <= 1.0],
    ['X', 'Y'], default='Z'
)
df_mensual_abc_xyz['clase_abc_xyz'] = df_mensual_abc_xyz['clase_abc'] + '-' + df_mensual_abc_xyz['clase_xyz']

# ══════════════════════════════════════════════════════════════════════════════
# 5. HEADER CORPORATIVO MASSHOPPING
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="masshopping-header">
    <div>
        <div class="masshopping-title">MASSHOPPING | Portal de Administracion y Planificacion Logistica</div>
        <div class="masshopping-subtitle">Control de Inventarios - Clasificacion ABC-XYZ </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 6. PESTANAS PRINCIPALES
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab7, tab3, tab4, tab5, tab6, tab2, tab8 = st.tabs([
    "Armado y Simulacion de Contenedor",
    "Generador de Pedido Optimo",
    "Ficha Visual y Comparador",
    "Totalizacion por Categoria",
    "Analisis Visual ABC",
    "Analisis Visual XYZ",
    "Matriz Estrategica ABC-XYZ",
    "Sobre Stock y Stock Muerto"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: ARMADO DE CONTENEDOR
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("#### Constructor de Pedido para Contenedor Masshopping")
    st.caption("Filtra el catalogo por categoria, estado o texto. El volumen CBM y el costo FOB se recalculan en tiempo real.")
    
    with st.container():
        r1_col1, r1_col2 = st.columns([2.5, 1.5])
        with r1_col1:
            etiquetas_opciones_t1 = (df_modelo['sku'] + " -- " + df_modelo['nombre']).tolist()
            busqueda_skus = st.multiselect(
                "Buscar producto por Codigo SKU o Descripcion (Autocompletado):",
                options=etiquetas_opciones_t1,
                placeholder="Escribe codigo o palabra para buscar...",
                key="multiselect_busqueda_sku_t1"
            )
        with r1_col2:
            todas_categorias = sorted(df_modelo['categoria'].unique().tolist())
            f_categoria = st.multiselect(
                "Categoria de Producto:",
                options=todas_categorias,
                default=[],
                placeholder="Todas las categorias"
            )
        
        r2_col1, r2_col2, r2_col3 = st.columns([1.2, 1.2, 1.2])
        with r2_col1:
            f_estado = st.multiselect("Estado de Stock:", ["REORDENAR", "OK"], default=["REORDENAR"])
        with r2_col2:
            f_abc = st.multiselect("Clasificacion ABC:", ["AA", "A", "B", "C"], default=["AA", "A", "B", "C"])
        with r2_col3:
            f_xyz = st.multiselect("Variabilidad XYZ:", ["X", "Y", "Z"], default=["X", "Y", "Z"])
    
    # Aplicar filtros
    mask = (
        df_modelo['estado'].isin(f_estado) &
        df_modelo['clase_abc'].isin(f_abc) &
        df_modelo['clase_xyz'].isin(f_xyz) &
        (~df_modelo['sku'].isin(['MASS3063', 'MASS3065', 'MASS3066']))
    )
    if f_categoria:
        mask = mask & (df_modelo['categoria'].isin(f_categoria))
        
    if busqueda_skus:
        codigos_buscar = [s.split(" -- ")[0] for s in busqueda_skus]
        mask = mask & (df_modelo['sku'].isin(codigos_buscar))
    
    df_vista = df_modelo[mask].copy()
    
    st.caption(f"Mostrando **{len(df_vista):,}** productos de {len(df_modelo):,} totales.")
    
    seleccionar_todos = st.checkbox("Marcar todos los productos mostrados para incluirlos en el pedido")
    if seleccionar_todos:
        df_vista['incluir_en_pedido'] = True
    else:
        df_vista['incluir_en_pedido'] = False
        
    # Tabla editable
    cols_editor = [
        'incluir_en_pedido', 'imagen_url', 'sku', 'nombre', 'categoria', 'clase_abc_xyz',
        'stock_actual', 'stock_transito', 'rop', 'demanda_semanal_prom', 'pedir_cajas',
        'cantidad_por_caja', 'CBMM', 'costo', 'costo_puesto'
    ]
    
    df_editado = st.data_editor(
        df_vista[cols_editor],
        column_config={
            "incluir_en_pedido": st.column_config.CheckboxColumn("Incluir", help="Marcar para sumar al contenedor"),
            "imagen_url": st.column_config.ImageColumn("Foto", help="Foto oficial del producto Masshopping"),
            "sku": st.column_config.TextColumn("Codigo SKU", width="small"),
            "nombre": st.column_config.TextColumn("Nombre del Producto", width="large"),
            "categoria": st.column_config.TextColumn("Categoria", width="medium"),
            "pedir_cajas": st.column_config.NumberColumn("Cajas a Pedir", min_value=0, step=1),
            "stock_actual": st.column_config.NumberColumn("Stock", format="%.0f"),
            "stock_transito": st.column_config.NumberColumn("En Transito", format="%.0f", help="Stock en contenedores Julio/Egipto"),
            "rop": st.column_config.NumberColumn("ROP", format="%.1f"),
            "demanda_semanal_prom": st.column_config.NumberColumn("Demanda/Sem", format="%.1f"),
            "CBMM": st.column_config.NumberColumn("CBM/Caja", format="%.3f"),
            "costo": st.column_config.NumberColumn("Costo FOB ($)", format="$%.2f"),
            "costo_puesto": st.column_config.NumberColumn("Costo DDP ($)", format="$%.2f", help="Costo FOB + Flete unitario"),
        },
        disabled=['imagen_url', 'sku', 'nombre', 'categoria', 'clase_abc_xyz', 'stock_actual', 'stock_transito', 'rop', 'demanda_semanal_prom', 'cantidad_por_caja', 'CBMM', 'costo', 'costo_puesto'],
        use_container_width=True,
        height=420,
        key="editor_masshopping_cont"
    )
    
    # Calculos en tiempo real
    seleccionados = df_editado[df_editado['incluir_en_pedido'] & (df_editado['pedir_cajas'] > 0)].copy()
    seleccionados['cbm_total'] = seleccionados['pedir_cajas'] * seleccionados['CBMM']
    seleccionados['unidades_total'] = seleccionados['pedir_cajas'] * seleccionados['cantidad_por_caja']
    seleccionados['inversion_fob'] = seleccionados['unidades_total'] * seleccionados['costo']
    seleccionados['costo_total_ddp'] = seleccionados['unidades_total'] * seleccionados['costo_puesto']
    
    cbm_acumulado = seleccionados['cbm_total'].sum()
    inversion_acumulada = seleccionados['inversion_fob'].sum()
    inversion_ddp_acumulada = seleccionados['costo_total_ddp'].sum()
    cajas_acumuladas = seleccionados['pedir_cajas'].sum()
    unidades_acumuladas = seleccionados['unidades_total'].sum()
    pct_llenado = min(100.0, (cbm_acumulado / capacidad_cont) * 100) if capacidad_cont > 0 else 0
    contenedores_totales = cbm_acumulado / capacidad_cont if capacidad_cont > 0 else 0
    
    st.markdown("<br>", unsafe_allow_html=True)
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Volumen Total CBM</div>
            <div class="metric-value">{cbm_acumulado:,.2f} m3</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Inversion FOB / DDP</div>
            <div class="metric-value">${inversion_acumulada:,.2f}</div>
            <div class="metric-delta">DDP Est.: ${inversion_ddp_acumulada:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Empaque Total</div>
            <div class="metric-value">{cajas_acumuladas:,} cajas</div>
            <div class="metric-delta">{unidades_acumuladas:,} unidades ({len(seleccionados)} SKUs)</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col4:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">Ocupacion de Contenedor</div>
            <div class="metric-value">{contenedores_totales:.2f} cont.</div>
            <div class="metric-delta">{pct_llenado:.1f}% del 1er contenedor</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.progress(pct_llenado / 100.0)
    
    if cbm_acumulado > capacidad_cont:
        st.warning(f"El volumen supera la capacidad de 1 contenedor ({capacidad_cont} CBM). Se requieren **{math.ceil(contenedores_totales)} contenedores**.")
    elif pct_llenado >= 90:
        st.success(f"Contenedor optimizado. Nivel de ocupacion: **{pct_llenado:.1f}%**.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    csv_pedido = seleccionados[['sku', 'nombre', 'categoria', 'pedir_cajas', 'unidades_total', 'cbm_total', 'costo', 'inversion_fob', 'costo_puesto', 'costo_total_ddp']].to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="Descargar Orden de Compra Masshopping (CSV)",
        data=csv_pedido,
        file_name="orden_compra_masshopping_contenedor.csv",
        mime="text/csv",
        use_container_width=True
    )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: MATRIZ ABC-XYZ
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Matriz de Segmentacion de Demanda Masshopping")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown("### Conteo de SKUs por Cuadrante")
        st.dataframe(pd.crosstab(df_modelo['clase_abc'], df_modelo['clase_xyz'], margins=True, margins_name='Total'), use_container_width=True)
    with col_m2:
        st.markdown("### % que Requiere Reorden Inmediato")
        pct_reord = df_modelo.groupby(['clase_abc', 'clase_xyz'])['requiere_pedido'].mean().unstack(fill_value=0) * 100
        st.dataframe(pct_reord.style.format("{:.1f}%"), use_container_width=True)

    st.markdown("---")
    st.subheader("Simulación de Matriz Estratégica (Agregación Mensual)")
    st.caption("Esta matriz muestra cómo se distribuyen los productos si la variabilidad (XYZ) se calcula agrupando las ventas por mes.")
    col_m3, col_m4 = st.columns(2)
    with col_m3:
        st.markdown("### Conteo de SKUs Mensual")
        st.dataframe(pd.crosstab(df_mensual_abc_xyz['clase_abc'], df_mensual_abc_xyz['clase_xyz'], margins=True, margins_name='Total'), use_container_width=True)
    with col_m4:
        st.markdown("### % que Requiere Reorden Inmediato (Matriz Mensual)")
        pct_reord_m = df_mensual_abc_xyz.groupby(['clase_abc', 'clase_xyz'])['requiere_pedido'].mean().unstack(fill_value=0) * 100
        st.dataframe(pct_reord_m.style.format("{:.1f}%"), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: EXPLORADOR VISUAL & COMPARADOR (SIN ROP LINE, CON TENDENCIA)
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Ficha Tecnica y Comparador Historico de Productos")
    st.caption("Selecciona uno o varios productos para comparar su evolucion historica de demanda semanal con linea de tendencia.")
    
    df_opciones = df_modelo[['sku', 'nombre']].copy()
    df_opciones['etiqueta'] = df_opciones['sku'] + " -- " + df_opciones['nombre']
    lista_etiquetas = df_opciones['etiqueta'].tolist()
    
    # Persistir la seleccion del producto a traves de cambios de filtro
    if 'multiselect_comparador_tab3' not in st.session_state:
        import random
        skus_aa_a = df_modelo[df_modelo['clase_abc'].isin(['AA', 'A'])]['sku'].tolist()
        if skus_aa_a:
            random_sku = random.choice(skus_aa_a)
            random_etiq = df_opciones[df_opciones['sku'] == random_sku]['etiqueta'].values[0]
            st.session_state['multiselect_comparador_tab3'] = [random_etiq]
        else:
            st.session_state['multiselect_comparador_tab3'] = [lista_etiquetas[0]] if lista_etiquetas else []
            
    # Preserve current selections if they fall out of filtered options
    current_selection = st.session_state.get('multiselect_comparador_tab3', [])
    for sel in current_selection:
        if sel not in lista_etiquetas:
            lista_etiquetas.append(sel)
    
    skus_seleccionados = st.multiselect(
        "Selecciona uno o varios productos para comparar:",
        options=lista_etiquetas,
        key="multiselect_comparador_tab3"
    )
    
    if skus_seleccionados:
        skus_codigos = [s.split(" -- ")[0] for s in skus_seleccionados]
        
        # 1. Ficha del Producto Principal (primer seleccionado)
        sku_principal = skus_codigos[0]
        item_df = df_modelo[df_modelo['sku'] == sku_principal]
        if len(item_df) > 0:
            item = item_df.iloc[0]
            
            st.divider()
            col_img, col_info = st.columns([1, 2.2])
            
            with col_img:
                if item['imagen_url'] and str(item['imagen_url']).startswith('http'):
                    st.image(item['imagen_url'], caption=f"{item['sku']} | Masshopping Store", use_container_width=True)
                else:
                    st.info("Foto oficial no disponible en IMAGES.csv")
            
            with col_info:
                st.markdown(f"<h3 style='margin:0; color:#141E32;'>{item['nombre']}</h3>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:#5AA06E; font-weight:700; margin-top:4px;'>Codigo SKU: <span style='color:#141E32;'>{item['sku']}</span> | Categoria: <span style='color:#141E32;'>{item['categoria']}</span> | Segmento: <span style='color:#141E32;'>{item['clase_abc_xyz']}</span></p>", unsafe_allow_html=True)
                
                estado_html = f'<span class="badge-status-reorden">REORDENAR</span>' if item['estado'] == 'REORDENAR' else f'<span class="badge-status-ok">OK</span>'
                
                transit_val = item.get('stock_transito', 0)
                
                st.markdown(f"""
                <div class="kpi-grid">
                    <div class="kpi-card">
                        <div class="kpi-title">Stock Actual</div>
                        <div class="kpi-number">{item['stock_actual']:,.0f} uds</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-title">En Transito</div>
                        <div class="kpi-number">{transit_val:,.0f} uds</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-title">Punto Reorden (ROP)</div>
                        <div class="kpi-number">{item['rop']:,.1f} uds</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-title">Estado</div>
                        <div style="margin-top:2px;">{estado_html}</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-title">Costo FOB</div>
                        <div class="kpi-number">${item['costo']:,.2f}</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-title">Costo Puesto DDP</div>
                        <div class="kpi-number">${item['costo_puesto']:,.2f}</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-title">CBM / Caja</div>
                        <div class="kpi-number">{item['CBMM']:.3f} m3</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-title">Nivel Servicio</div>
                        <div class="kpi-number">{item['nivel_servicio']:.0%}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # 2. Grafico Comparativo con TENDENCIA e IMPACTO CAMBIARIO (P2P)
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Comparativa Historica de Demanda Semanal vs Variacion Cambiaria")
        st.caption("Linea de tendencia = promedio movil de 4 semanas. Linea naranja de fondo = Variacion porcentual interdiaria del USDT (Binance P2P).")
        
        # Local Date Range Filter for the Chart
        fecha_min_global = df_trans['fecha'].min().date() if not df_trans.empty else datetime.date(2023,1,1)
        fecha_max_global = df_trans['fecha'].max().date() if not df_trans.empty else datetime.date(2026,12,31)
        
        import datetime
        
        col_rango, col_chk1, col_chk2 = st.columns([2, 1, 1])
        with col_rango:
            rango_local = st.date_input(
                "Rango de Fechas Específicas (Gráfico)",
                value=(fecha_min_global, fecha_max_global),
                key="rango_grafico_tab3"
            )
            
        with col_chk1:
            mostrar_tendencia = st.checkbox("Mostrar Tendencia (Promedio Movil)", value=False)
        with col_chk2:
            mostrar_p2p = st.checkbox("Mostrar Variacion USDT (P2P)", value=False)
            
        # Apply local date filter to df_trans (full history)
        df_plot_trans = df_trans
        if isinstance(rango_local, tuple):
            if len(rango_local) == 2:
                start_loc, end_loc = rango_local
                df_plot_trans = df_trans[
                    (df_trans['fecha'].dt.date >= start_loc) &
                    (df_trans['fecha'].dt.date <= end_loc)
                ]
            elif len(rango_local) == 1:
                start_loc = rango_local[0]
                df_plot_trans = df_trans[
                    df_trans['fecha'].dt.date >= start_loc
                ]
        
        from plotly.subplots import make_subplots
        paleta_colores = ['#5AA06E', '#141E32', '#E65100', '#00897B', '#7B1FA2', '#1E88E5', '#D81B60', '#FDD835']
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Graficar Variacion P2P en el eje secundario (fondo)
        if mostrar_p2p and not df_p2p.empty:
            # Obtener fecha minima de los skus seleccionados
            df_plot_skus = df_plot_trans[df_plot_trans['sku'].isin(skus_codigos)]
            fecha_min_sku = df_plot_skus['fecha'].min() if not df_plot_skus.empty else fecha_min_global
            
            df_p2p_f = df_p2p[df_p2p['fecha'] >= pd.to_datetime(fecha_min_sku)]
            if isinstance(rango_local, tuple) and len(rango_local) == 2:
                df_p2p_f = df_p2p_f[
                    (df_p2p_f['fecha'].dt.date >= rango_local[0]) &
                    (df_p2p_f['fecha'].dt.date <= rango_local[1])
                ]
                
            fig.add_trace(go.Scatter(
                x=df_p2p_f['fecha'],
                y=df_p2p_f['var_pct'],
                mode='lines',
                name='Variacion USDT (P2P)',
                line=dict(width=1, color='rgba(230, 81, 0, 0.4)'), # Naranja semi-transparente
                fill='tozeroy',
                fillcolor='rgba(230, 81, 0, 0.05)',
                hovertemplate="<b>USDT P2P</b><br>Fecha: %{x|%d %b %Y}<br>Variacion: <b>%{y:.2f}%</b><extra></extra>"
            ), secondary_y=True)
        
        for idx, sku_code in enumerate(skus_codigos):
            df_hist_sku = df_plot_trans[df_plot_trans['sku'] == sku_code].copy()
            serie = df_hist_sku.groupby(pd.Grouper(key='fecha', freq='W-MON'))['cantidad'].sum().reset_index()
            serie = serie.sort_values('fecha')
            
            # Nombre para la leyenda
            nombre_label = df_modelo[df_modelo['sku'] == sku_code]['nombre'].values
            nombre_label = nombre_label[0] if len(nombre_label) > 0 else sku_code
            if len(nombre_label) > 30:
                nombre_label = nombre_label[:30] + '...'
            legend_name = f"{sku_code} ({nombre_label})"
            
            color_linea = paleta_colores[idx % len(paleta_colores)]
            
            # Linea de demanda real
            fig.add_trace(go.Scatter(
                x=serie['fecha'],
                y=serie['cantidad'],
                mode='lines+markers',
                name=legend_name,
                line=dict(width=2, color=color_linea),
                marker=dict(size=4),
                hovertemplate="<b>" + sku_code + "</b><br>Fecha: %{x|%d %b %Y}<br>Cantidad: <b>%{y:,.0f} uds</b><extra></extra>"
            ), secondary_y=False)
            
            # Linea de tendencia (promedio movil de 4 semanas)
            if mostrar_tendencia and len(serie) >= 4:
                serie['tendencia'] = serie['cantidad'].rolling(window=4, min_periods=2).mean()
                fig.add_trace(go.Scatter(
                    x=serie['fecha'],
                    y=serie['tendencia'],
                    mode='lines',
                    name=f"Tendencia {sku_code}",
                    line=dict(width=2.5, color=color_linea, dash='dash'),
                    hovertemplate="<b>Tendencia " + sku_code + "</b><br>Fecha: %{x|%d %b %Y}<br>Promedio movil: <b>%{y:,.1f} uds</b><extra></extra>",
                    showlegend=True
                ), secondary_y=False)
        
        fig.update_layout(
            height=650,
            margin=dict(l=20, r=20, t=30, b=30),
            hovermode="x unified",
            xaxis=dict(
                title="Fecha",
                tickformat="%b %Y",
                showgrid=True,
                gridcolor="#EBF4EE"
            ),
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            ),
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF"
        )
        
        # Calcular y1_max para alinear ceros
        y1_max = 0
        for sku_code in skus_codigos:
            df_hist_sku = df_plot_trans[df_plot_trans['sku'] == sku_code]
            if not df_hist_sku.empty:
                serie_cant = df_hist_sku.groupby(pd.Grouper(key='fecha', freq='W-MON'))['cantidad'].sum()
                if not serie_cant.empty:
                    y1_max = max(y1_max, serie_cant.max())
        y1_max = max(y1_max, 1)

        # Calcular y2_min y y2_max
        if mostrar_p2p and not df_p2p.empty and 'df_p2p_f' in locals() and not df_p2p_f.empty:
            y2_min = df_p2p_f['var_pct'].min()
            y2_max = df_p2p_f['var_pct'].max()
        else:
            y2_min, y2_max = 0, 0

        # Configurar rangos alineando el cero
        if y2_min < 0 < y2_max:
            y1_min = y1_max * (y2_min / y2_max)
            fig.update_yaxes(title_text="Unidades Vendidas / Semana", showgrid=True, gridcolor="#EBF4EE", range=[y1_min, y1_max * 1.1], secondary_y=False)
            fig.update_yaxes(title_text="Variacion USDT (%)", showgrid=False, range=[y2_min, y2_max * 1.1], secondary_y=True)
        else:
            fig.update_yaxes(title_text="Unidades Vendidas / Semana", showgrid=True, gridcolor="#EBF4EE", range=[0, y1_max * 1.1], secondary_y=False)
            if y2_min != y2_max:
                fig.update_yaxes(title_text="Variacion USDT (%)", showgrid=False, range=[y2_min * 1.1, y2_max * 1.1], secondary_y=True)
            else:
                fig.update_yaxes(title_text="Variacion USDT (%)", showgrid=False, secondary_y=True)

        # Agregar linea de referencia para el 0 de ambos ejes (coinciden en la misma altura)
        fig.add_hline(y=0, line_dash="dash", line_color="rgba(230, 81, 0, 0.8)", line_width=2, yref="y2")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Aggregate totals for selected SKUs in the selected date range
        df_plot_skus = df_plot_trans[df_plot_trans['sku'].isin(skus_codigos)]
        if not df_plot_skus.empty:
            total_unidades = df_plot_skus['cantidad'].sum()
            # Calculate total USD: merge with df_modelo to get costo
            df_plot_usd = pd.merge(df_plot_skus, df_modelo[['sku', 'costo']], on='sku', how='left')
            df_plot_usd['costo'] = df_plot_usd['costo'].fillna(0)
            total_usd = (df_plot_usd['cantidad'] * df_plot_usd['costo']).sum()
            
            st.markdown("---")
            st.markdown("### Totales Agregados del Período Seleccionado")
            t_col1, t_col2 = st.columns(2)
            with t_col1:
                st.metric("Total Unidades Vendidas", f"{total_unidades:,.0f}")
            with t_col2:
                st.metric("Total Ventas (Aprox USD Costo)", f"${total_usd:,.2f}")
        else:
            st.info("No hay datos de venta en el rango seleccionado para los productos elegidos.")

        # =========================================================
        # ANALISIS MENSUAL ADICIONAL (Agregación por Mes)
        # =========================================================
        st.markdown("---")
        st.subheader("Simulación de Agregación Mensual")
        st.caption("Si agregamos las ventas por MES en lugar de por semana, la variabilidad (CV2) y la intermitencia (ADI) se suavizan drásticamente. Observa cómo cambiaría la clasificación (Cuadrante) de los productos seleccionados bajo un modelo mensual.")
        
        if len(skus_codigos) > 0:
            fig_m = make_subplots(specs=[[{"secondary_y": False}]])
            resultados_mensuales = []
            
            for idx, sku_code in enumerate(skus_codigos):
                df_hist_sku = df_plot_trans[df_plot_trans['sku'] == sku_code].copy()
                
                # Agregación mensual (MS = Month Start)
                ts_mensual = df_hist_sku.groupby(pd.Grouper(key='fecha', freq='MS'))['cantidad'].sum()
                serie_m = ts_mensual.reset_index().sort_values('fecha')
                
                color_linea = paleta_colores[idx % len(paleta_colores)]
                fig_m.add_trace(go.Scatter(
                    x=serie_m['fecha'], y=serie_m['cantidad'],
                    mode='lines+markers', name=sku_code,
                    line=dict(width=2, color=color_linea),
                    marker=dict(size=6),
                    hovertemplate="<b>" + sku_code + "</b><br>Mes: %{x|%b %Y}<br>Cantidad: <b>%{y:,.0f} uds</b><extra></extra>"
                ))
                
                # Calculo de cuadrante mensual
                if ts_mensual.sum() > 0:
                    first_nonzero_m = ts_mensual.ne(0).idxmax()
                    ts_trim_m = ts_mensual.loc[first_nonzero_m:]
                    n_periodos_m = len(ts_trim_m)
                    pos_sales_m = ts_trim_m[ts_trim_m > 0]
                    n_pos_m = len(pos_sales_m)
                    
                    adi_m = n_periodos_m / n_pos_m if n_pos_m > 0 else float('inf')
                    if n_pos_m > 1:
                        mu_pos_m = pos_sales_m.mean()
                        std_pos_m = pos_sales_m.std(ddof=1)
                        cv2_m = (std_pos_m / mu_pos_m) ** 2 if mu_pos_m > 0 else 0
                    else:
                        cv2_m = np.nan
                        
                    if adi_m < 1.32 and cv2_m < 0.49:
                        cuad_m = 'smooth'
                    elif adi_m >= 1.32 and cv2_m < 0.49:
                        cuad_m = 'intermittent'
                    elif adi_m < 1.32 and cv2_m >= 0.49:
                        cuad_m = 'erratic'
                    else:
                        cuad_m = 'lumpy'
                else:
                    adi_m = 0
                    cv2_m = np.nan
                    cuad_m = 'sin_datos'
                    
                # Calculo de cuadrante SEMANAL (Real)
                ts_semanal = df_hist_sku.groupby(pd.Grouper(key='fecha', freq='W-MON'))['cantidad'].sum()
                if ts_semanal.sum() > 0:
                    first_nonzero_w = ts_semanal.ne(0).idxmax()
                    ts_trim_w = ts_semanal.loc[first_nonzero_w:]
                    n_periodos_w = len(ts_trim_w)
                    pos_sales_w = ts_trim_w[ts_trim_w > 0]
                    n_pos_w = len(pos_sales_w)
                    
                    adi_w = n_periodos_w / n_pos_w if n_pos_w > 0 else float('inf')
                    if n_pos_w > 1:
                        mu_pos_w = pos_sales_w.mean()
                        std_pos_w = pos_sales_w.std(ddof=1)
                        cv2_w = (std_pos_w / mu_pos_w) ** 2 if mu_pos_w > 0 else 0
                    else:
                        cv2_w = np.nan
                        
                    if adi_w < 1.32 and cv2_w < 0.49:
                        cuad_w = 'smooth'
                    elif adi_w >= 1.32 and cv2_w < 0.49:
                        cuad_w = 'intermittent'
                    elif adi_w < 1.32 and cv2_w >= 0.49:
                        cuad_w = 'erratic'
                    else:
                        cuad_w = 'lumpy'
                else:
                    adi_w = 0
                    cv2_w = np.nan
                    cuad_w = 'sin_datos'
                
                resultados_mensuales.append({
                    'SKU': sku_code,
                    'Intermitencia (SEMANAL)': str(cuad_w).upper(),
                    'ADI (Semanal)': f"{adi_w:.2f}",
                    'CV2 (Semanal)': f"{cv2_w:.2f}" if not np.isnan(cv2_w) else 'N/A',
                    'Venta/Sem': f"{ts_semanal.mean():.1f}",
                    '|': '|',
                    'Intermitencia (MENSUAL)': str(cuad_m).upper(),
                    'ADI (Mensual)': f"{adi_m:.2f}",
                    'CV2 (Mensual)': f"{cv2_m:.2f}" if not np.isnan(cv2_m) else 'N/A',
                    'Venta/Mes': f"{ts_mensual.mean():.1f}"
                })
            
            fig_m.update_layout(
                height=400, margin=dict(l=20, r=20, t=30, b=30),
                hovermode="x unified",
                xaxis=dict(title="Mes", tickformat="%b %Y", showgrid=True, gridcolor="#EBF4EE"),
                yaxis=dict(title="Unidades Vendidas / Mes", showgrid=True, gridcolor="#EBF4EE"),
                plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF"
            )
            
            st.plotly_chart(fig_m, use_container_width=True)
            
            # Tabla comparativa
            st.markdown("**Comparativa de Diagnóstico (Semanal vs Mensual):**")
            st.dataframe(pd.DataFrame(resultados_mensuales), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4: TOTALIZACION POR CATEGORIA
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("Totalizacion de Inventario por Categoria")
    st.caption("Vista consolidada de cantidades y montos por categoria de producto.")
    
    # Agrupar por categoria
    df_cat = df_modelo.groupby('categoria').agg(
        total_skus=('sku', 'nunique'),
        total_unidades_vendidas=('total_unidades', 'sum'),
        total_ventas_usd=('total_ventas', 'sum'),
        stock_total=('stock_actual', 'sum'),
        stock_transito_total=('stock_transito', 'sum'),
        skus_reorden=('requiere_pedido', 'sum'),
    ).reset_index().sort_values('total_ventas_usd', ascending=False)
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("### Unidades Vendidas por Categoria")
        fig_units = px.bar(
            df_cat.head(15),
            x='categoria',
            y='total_unidades_vendidas',
            color='total_unidades_vendidas',
            color_continuous_scale=['#D5E7DB', '#5AA06E', '#141E32'],
            labels={'total_unidades_vendidas': 'Unidades', 'categoria': 'Categoria'},
        )
        fig_units.update_layout(
            height=400,
            xaxis_tickangle=-45,
            showlegend=False,
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_units, use_container_width=True)
    
    with col_chart2:
        st.markdown("### Ingresos por Ventas (USD) por Categoria")
        fig_revenue = px.bar(
            df_cat.head(15),
            x='categoria',
            y='total_ventas_usd',
            color='total_ventas_usd',
            color_continuous_scale=['#D5E7DB', '#5AA06E', '#141E32'],
            labels={'total_ventas_usd': 'Ventas ($)', 'categoria': 'Categoria'},
        )
        fig_revenue.update_layout(
            height=400,
            xaxis_tickangle=-45,
            showlegend=False,
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    # Tabla resumen
    st.markdown("### Resumen por Categoria")
    st.dataframe(
        df_cat.rename(columns={
            'categoria': 'Categoria',
            'total_skus': 'SKUs',
            'total_unidades_vendidas': 'Unidades Vendidas',
            'total_ventas_usd': 'Ventas (USD)',
            'stock_total': 'Stock Actual',
            'stock_transito_total': 'En Transito',
            'skus_reorden': 'SKUs en Reorden',
        }).style.format({
            'Unidades Vendidas': '{:,.0f}',
            'Ventas (USD)': '${:,.2f}',
            'Stock Actual': '{:,.0f}',
            'En Transito': '{:,.0f}',
        }),
        use_container_width=True,
        height=400
    )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5: ANALISIS VISUAL ABC
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("Grafico de Pareto - Clasificacion ABC")
    st.caption("Distribucion de ventas acumuladas por producto (Regla 80/20)")
    
    # Sort by total_ventas descending
    df_abc = df_modelo.sort_values('total_ventas', ascending=False).reset_index(drop=True)
    df_abc['pct_acum'] = (df_abc['total_ventas'].cumsum() / df_abc['total_ventas'].sum()) * 100
    df_abc['sku_num'] = np.arange(1, len(df_abc) + 1)
    
    color_map = {'AA': '#141E32', 'A': '#5AA06E', 'B': '#FDD835', 'C': '#E65100'}
    
    fig_abc = make_subplots(specs=[[{"secondary_y": True}]])
    
    for clase in ['AA', 'A', 'B', 'C']:
        mask_clase = df_abc['clase_abc'] == clase
        if mask_clase.any():
            fig_abc.add_trace(go.Bar(
                x=df_abc[mask_clase]['sku'],
                y=df_abc[mask_clase]['total_ventas'],
                name=f"Clase {clase}",
                marker_color=color_map.get(clase),
                hovertemplate="<b>%{x}</b><br>Clase: " + clase + "<br>Ventas Totales: $%{y:,.2f}<extra></extra>"
            ), secondary_y=False)
            
    fig_abc.add_trace(go.Scatter(
        x=df_abc['sku'],
        y=df_abc['pct_acum'],
        mode='lines',
        name='% Acumulado',
        line=dict(color='#E65100', width=3),
        hovertemplate="<b>%{x}</b><br>% Acumulado: %{y:.1f}%<extra></extra>"
    ), secondary_y=True)
    
    fig_abc.update_layout(
        height=500,
        title="Pareto ABC por Ingresos",
        xaxis=dict(showticklabels=False, title="Productos ordenados por Ventas", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    fig_abc.update_yaxes(title_text="Ventas Totales ($)", secondary_y=False, showgrid=True, gridcolor="#EBF4EE")
    fig_abc.update_yaxes(title_text="% Acumulado", secondary_y=True, range=[0, 105], showgrid=False)
    
    st.plotly_chart(fig_abc, use_container_width=True)
    
    st.markdown("""
    **¿Cómo funciona el Análisis ABC?**
    Clasifica los productos según su contribución total a los ingresos (Principio de Pareto).
    * **Clase AA (Top 50%)**: Muy pocos productos que generan la mitad de las ventas. Requieren control estricto y alto nivel de servicio.
    * **Clase A (50% - 80%)**: Productos de alta importancia comercial.
    * **Clase B (80% - 95%)**: Productos de rotación e importancia media.
    * **Clase C (95% - 100%)**: Gran volumen de SKUs que aportan muy poco al ingreso total. Control flexible.
    """)
    
    df_abc_table = df_abc[['sku', 'nombre', 'total_ventas', 'pct_acum', 'clase_abc']].copy()
    df_abc_table['pct_venta'] = (df_abc_table['total_ventas'] / df_abc_table['total_ventas'].sum()) * 100
    df_abc_table = df_abc_table[['sku', 'nombre', 'total_ventas', 'pct_venta', 'pct_acum', 'clase_abc']]
    
    search_abc = st.text_input("Buscar producto por código o nombre (ABC):", key="search_abc").strip().lower()
    if search_abc:
        df_abc_table = df_abc_table[
            df_abc_table['sku'].str.lower().str.contains(search_abc) | 
            df_abc_table['nombre'].str.lower().str.contains(search_abc)
        ]
    
    def color_abc(val):
        colors = {'AA': '#141E32', 'A': '#5AA06E', 'B': '#FDD835', 'C': '#E65100'}
        color = colors.get(val, 'black')
        return f'color: {color}; font-weight: bold;'
        
    st.dataframe(
        df_abc_table.style.format({
            'total_ventas': '${:,.2f}',
            'pct_venta': '{:.2f}%',
            'pct_acum': '{:.2f}%'
        }).map(color_abc, subset=['clase_abc']),
        use_container_width=True
    )
    
    st.markdown("---")
    st.subheader("Simulación de Análisis ABC (Agregación Mensual)")
    st.caption("Nota matemática: La clasificación ABC se basa en el **Total de Ventas** del período. La suma de ventas es idéntica independientemente de si se suma día a día, semana a semana o mes a mes. Por tanto, el gráfico y las clasificaciones ABC no cambian al usar agregación mensual.")

    fig_abc_m = make_subplots(specs=[[{"secondary_y": True}]])
    
    for clase in ['AA', 'A', 'B', 'C']:
        mask_clase_m = df_abc['clase_abc'] == clase
        if mask_clase_m.any():
            fig_abc_m.add_trace(go.Bar(
                x=df_abc[mask_clase_m]['sku'],
                y=df_abc[mask_clase_m]['total_ventas'],
                name=f"Clase {clase} (Mensual)",
                marker_color=color_map.get(clase),
                hovertemplate="<b>%{x}</b><br>Clase: " + clase + "<br>Ventas Totales: $%{y:,.2f}<extra></extra>"
            ), secondary_y=False)
            
    fig_abc_m.add_trace(go.Scatter(
        x=df_abc['sku'],
        y=df_abc['pct_acum'],
        mode='lines',
        name='% Acumulado',
        line=dict(color='#E65100', width=3),
        hovertemplate="<b>%{x}</b><br>% Acumulado: %{y:.1f}%<extra></extra>"
    ), secondary_y=True)
    
    fig_abc_m.update_layout(
        height=500,
        title="Pareto ABC por Ingresos (Perspectiva Mensual)",
        xaxis=dict(showticklabels=False, title="Productos ordenados por Ventas", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    fig_abc_m.update_yaxes(title_text="Ventas Totales ($)", secondary_y=False, showgrid=True, gridcolor="#EBF4EE")
    fig_abc_m.update_yaxes(title_text="% Acumulado", secondary_y=True, range=[0, 105], showgrid=False)
    
    st.plotly_chart(fig_abc_m, use_container_width=True)

    df_abc_table_m = df_abc[['sku', 'nombre', 'total_ventas', 'pct_acum', 'clase_abc']].copy()
    df_abc_table_m['pct_venta'] = (df_abc_table_m['total_ventas'] / df_abc_table_m['total_ventas'].sum()) * 100
    df_abc_table_m = df_abc_table_m[['sku', 'nombre', 'total_ventas', 'pct_venta', 'pct_acum', 'clase_abc']]
    
    search_abc_m = st.text_input("Buscar producto por código o nombre (ABC Mensual):", key="search_abc_m").strip().lower()
    if search_abc_m:
        df_abc_table_m = df_abc_table_m[
            df_abc_table_m['sku'].str.lower().str.contains(search_abc_m) | 
            df_abc_table_m['nombre'].str.lower().str.contains(search_abc_m)
        ]
        
    st.dataframe(
        df_abc_table_m.style.format({
            'total_ventas': '${:,.2f}',
            'pct_venta': '{:.2f}%',
            'pct_acum': '{:.2f}%'
        }).map(color_abc, subset=['clase_abc']),
        use_container_width=True
    )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6: ANALISIS VISUAL XYZ
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.subheader("Dispersion XYZ (Demanda vs Variabilidad)")
    st.caption("Identificacion de productos estables (X), variables (Y) y erraticos (Z).")
    
    fig_xyz = px.scatter(
        df_modelo,
        x='demanda_semanal_prom',
        y='cv',
        color='clase_xyz',
        color_discrete_map={'X': '#5AA06E', 'Y': '#FDD835', 'Z': '#E65100'},
        hover_name='sku',
        hover_data=['nombre', 'clase_abc'],
        labels={'demanda_semanal_prom': 'Demanda Promedio (Semanal)', 'cv': 'Coeficiente de Variacion (CV)'}
    )
    
    fig_xyz.add_hline(y=0.5, line_dash="dash", line_color="gray", annotation_text="Limite X-Y (0.5)")
    fig_xyz.add_hline(y=1.0, line_dash="dash", line_color="gray", annotation_text="Limite Y-Z (1.0)")
    
    fig_xyz.update_layout(
        height=500,
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        xaxis=dict(showgrid=True, gridcolor="#EBF4EE"),
        yaxis=dict(showgrid=True, gridcolor="#EBF4EE")
    )
    
    st.plotly_chart(fig_xyz, use_container_width=True)
    
    st.markdown("""
    **¿Cómo funciona el Análisis XYZ?**
    Clasifica los productos según la volatilidad y previsibilidad de su demanda usando el Coeficiente de Variación (CV).
    * **Clase X (CV ≤ 0.5)**: Demanda estable y muy predecible. Rara vez sufren quiebres o excesos sorpresivos.
    * **Clase Y (0.5 < CV ≤ 1.0)**: Demanda variable. Pueden tener fluctuaciones estacionales o tendencias.
    * **Clase Z (CV > 1.0)**: Demanda muy errática e impredecible (Lumpy / Intermitente). Requieren mayor stock de seguridad relativo o políticas de pedido bajo demanda.
    """)
    
    df_xyz_table = df_modelo[['sku', 'nombre', 'demanda_semanal_prom', 'cv', 'clase_xyz']].copy()
    df_xyz_table = df_xyz_table.sort_values('cv', ascending=False).reset_index(drop=True)
    
    search_xyz = st.text_input("Buscar producto por código o nombre (XYZ):", key="search_xyz").strip().lower()
    if search_xyz:
        df_xyz_table = df_xyz_table[
            df_xyz_table['sku'].str.lower().str.contains(search_xyz) | 
            df_xyz_table['nombre'].str.lower().str.contains(search_xyz)
        ]
    
    def color_xyz(val):
        colors = {'X': '#5AA06E', 'Y': '#FDD835', 'Z': '#E65100'}
        color = colors.get(val, 'black')
        return f'color: {color}; font-weight: bold;'
        
    st.dataframe(
        df_xyz_table.style.format({
            'demanda_semanal_prom': '{:.1f}',
            'cv': '{:.3f}'
        }).map(color_xyz, subset=['clase_xyz']),
        use_container_width=True
    )

    st.markdown("---")
    st.subheader("Simulación XYZ (Agregación Mensual)")
    st.caption("Identificación de volatilidad usando un Coeficiente de Variación (CV) basado en demandas **Mensuales**. Notarás que muchos SKUs migran hacia X o Y.")
    
    fig_xyz_m = px.scatter(
        df_mensual_abc_xyz,
        x='demanda_mensual_prom',
        y='cv',
        color='clase_xyz',
        color_discrete_map={'X': '#5AA06E', 'Y': '#FDD835', 'Z': '#E65100'},
        hover_name='sku',
        hover_data=['nombre', 'clase_abc'],
        labels={'demanda_mensual_prom': 'Demanda Promedio (Mensual)', 'cv': 'CV (Mensual)'}
    )
    fig_xyz_m.add_hline(y=0.5, line_dash="dash", line_color="gray", annotation_text="Limite X-Y (0.5)")
    fig_xyz_m.add_hline(y=1.0, line_dash="dash", line_color="gray", annotation_text="Limite Y-Z (1.0)")
    
    fig_xyz_m.update_layout(
        height=500, plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
        xaxis=dict(showgrid=True, gridcolor="#EBF4EE"),
        yaxis=dict(showgrid=True, gridcolor="#EBF4EE")
    )
    st.plotly_chart(fig_xyz_m, use_container_width=True)
    
    df_xyz_table_m = df_mensual_abc_xyz[['sku', 'nombre', 'demanda_mensual_prom', 'cv', 'clase_xyz']].copy()
    df_xyz_table_m = df_xyz_table_m.sort_values('cv', ascending=False).reset_index(drop=True)
    
    search_xyz_m = st.text_input("Buscar producto por código o nombre (XYZ Mensual):", key="search_xyz_m").strip().lower()
    if search_xyz_m:
        df_xyz_table_m = df_xyz_table_m[
            df_xyz_table_m['sku'].str.lower().str.contains(search_xyz_m) | 
            df_xyz_table_m['nombre'].str.lower().str.contains(search_xyz_m)
        ]
        
    st.dataframe(
        df_xyz_table_m.style.format({
            'demanda_mensual_prom': '{:.1f}',
            'cv': '{:.3f}'
        }).map(color_xyz, subset=['clase_xyz']),
        use_container_width=True
    )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 7: GENERADOR DE PEDIDO OPTIMO
# ══════════════════════════════════════════════════════════════════════════════
with tab7:
    st.subheader("Generador Automatico de Pedido Optimo")
    st.info("Este generador selecciona EXCLUSIVAMENTE productos Clase AA o A, que NO tienen stock en transito, cuyo stock actual ha caido por debajo del Punto de Reorden (ROP) y pertenece al intervalo de tiempo seleccionado.")
    
    df_optimo = df_modelo[
        (df_modelo['stock_actual'] < df_modelo['rop']) &
        (df_modelo['stock_transito'] == 0) &
        (df_modelo['clase_abc'].isin(['AA', 'A'])) &
        (df_modelo['pedir_cajas'] > 0) &
        (df_modelo['total_unidades'] > 0) &
        (~df_modelo['sku'].isin(['MASS3063', 'MASS3065', 'MASS3066']))
    ].copy()
    
    if df_optimo.empty:
        st.success("No hay productos que cumplan los criterios de urgencia extrema en este momento.")
    else:
        st.write(f"Se encontraron **{len(df_optimo)}** productos criticos para reponer inmediatamente.")
        
        # Calculate optimal order metrics based on unfiltered df_optimo
        opt_fob = (df_optimo['pedir_cajas'] * df_optimo['cantidad_por_caja'] * df_optimo['costo']).sum()
        
        col_btn, col_srch = st.columns([1, 3])
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            
            def update_tab3_selection(etiquetas):
                st.session_state['multiselect_comparador_tab3'] = etiquetas
                
            df_opciones_opt = df_optimo[['sku', 'nombre']].copy()
            etiquetas_opt = (df_opciones_opt['sku'] + " -- " + df_opciones_opt['nombre']).tolist()
            
            st.button("Ver Estadísticas (Ficha Visual)", on_click=update_tab3_selection, args=(etiquetas_opt,))
        with col_srch:
            search_opt = st.text_input("Buscar producto por código o nombre (Pedido Óptimo):", key="search_opt").strip().lower()
            
        if search_opt:
            df_optimo_show = df_optimo[
                df_optimo['sku'].str.lower().str.contains(search_opt) | 
                df_optimo['nombre'].str.lower().str.contains(search_opt)
            ]
        else:
            df_optimo_show = df_optimo
        
        st.dataframe(
            df_optimo_show[['sku', 'nombre', 'clase_abc_xyz', 'stock_actual', 'stock_transito', 'rop', 'pedir_cajas', 'costo']].style.format({
                'stock_actual': '{:,.0f}',
                'stock_transito': '{:,.0f}',
                'rop': '{:,.1f}',
                'pedir_cajas': '{:,.0f}',
                'costo': '${:,.2f}'
            }),
            use_container_width=True,
            height=300
        )
        
        csv_optimo = df_optimo[['sku', 'nombre', 'categoria', 'pedir_cajas', 'costo']].to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="Descargar Pedido Optimo (CSV)",
            data=csv_optimo,
            file_name="pedido_optimo_urgente_AA_A.csv",
            mime="text/csv",
            type="primary"
        )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 8: SOBRE STOCK Y STOCK MUERTO
# ══════════════════════════════════════════════════════════════════════════════
with tab8:
    st.markdown("#### Análisis de Sobre Stock y Stock Inactivo (Lento Movimiento)")
    st.caption("Identifica productos que tienen stock disponible pero registran pocas o nulas ventas en los últimos 6 meses.")
    
    # ── 1. CÁLCULO DE VENTAS ACUMULADAS EN LOS ÚLTIMOS 6 MESES ──
    fecha_max_t = df_trans['fecha'].max()
    fecha_limite_6m = fecha_max_t - pd.DateOffset(months=6)
    df_trans_6m = df_trans[df_trans['fecha'] >= fecha_limite_6m]
    
    ventas_6m_df = df_trans_6m.groupby('sku')['cantidad'].sum().reset_index().rename(columns={'cantidad': 'ventas_6m'})
    
    # Combinar con el catálogo de df_modelo para obtener el stock y costos actuales
    df_sobre_stock = pd.merge(
        df_modelo[['sku', 'nombre', 'categoria', 'stock_actual', 'costo', 'CBMM', 'cantidad_por_caja', 'stock_transito']], 
        ventas_6m_df, 
        on='sku', 
        how='left'
    )
    df_sobre_stock['ventas_6m'] = df_sobre_stock['ventas_6m'].fillna(0.0)
    
    # ── 2. CONTROLES DEL REPORTE ──
    col_ctrl1, col_ctrl2 = st.columns(2)
    with col_ctrl1:
        max_ventas = st.slider(
            "Ventas máximas acumuladas en los últimos 6 meses (Uds):",
            min_value=0, max_value=50, value=4, step=1,
            key="slider_max_ventas_t8"
        )
    with col_ctrl2:
        min_stock = st.slider(
            "Stock mínimo en inventario para auditar (Uds):",
            min_value=1, max_value=100, value=1, step=1,
            key="slider_min_stock_t8"
        )
        
    col_ctrl3, col_ctrl4 = st.columns([1.5, 2.5])
    with col_ctrl3:
        cats_t8 = sorted(df_sobre_stock['categoria'].unique().tolist())
        selected_cats_t8 = st.multiselect(
            "Filtrar por Categoría:",
            options=cats_t8,
            default=[],
            placeholder="Todas las categorías",
            key="multiselect_cats_t8"
        )
    with col_ctrl4:
        search_txt_t8 = st.text_input(
            "Buscar producto (código o nombre):", 
            key="search_txt_t8"
        ).strip().lower()

    # ── 3. FILTRADO DE LA DATA ──
    mask_t8 = (df_sobre_stock['stock_actual'] >= min_stock) & (df_sobre_stock['ventas_6m'] <= max_ventas)
    
    if selected_cats_t8:
        mask_t8 = mask_t8 & (df_sobre_stock['categoria'].isin(selected_cats_t8))
        
    if search_txt_t8:
        mask_t8 = mask_t8 & (
            df_sobre_stock['sku'].str.lower().str.contains(search_txt_t8) | 
            df_sobre_stock['nombre'].str.lower().str.contains(search_txt_t8)
        )
        
    df_sobre_stock_filtrado = df_sobre_stock[mask_t8].copy()
    
    # Métricas calculadas para los SKUs inactivos
    df_sobre_stock_filtrado['valor_inventario_fob'] = df_sobre_stock_filtrado['stock_actual'] * df_sobre_stock_filtrado['costo']
    df_sobre_stock_filtrado['cbm_ocupado'] = df_sobre_stock_filtrado['stock_actual'] * (df_sobre_stock_filtrado['CBMM'] / df_sobre_stock_filtrado['cantidad_por_caja'])
    
    total_capital_fob = df_sobre_stock_filtrado['valor_inventario_fob'].sum()
    total_cbm_ocupado = df_sobre_stock_filtrado['cbm_ocupado'].sum()
    total_skus_inactivos = len(df_sobre_stock_filtrado)
    total_uds_inactivas = df_sobre_stock_filtrado['stock_actual'].sum()
    
    # ── 4. TARJETAS DE INDICADORES (KPI CARDS) ──
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.markdown(f"""
        <div class="kpi-card" style="border-left: 4px solid #D9534F;">
            <div class="kpi-label">CAPITAL INMOVILIZADO (FOB)</div>
            <div class="kpi-value" style="color: #D9534F;">${total_capital_fob:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col2:
        st.markdown(f"""
        <div class="kpi-card" style="border-left: 4px solid #F0AD4E;">
            <div class="kpi-label">VOLUMEN OCUPADO EN BODEGA</div>
            <div class="kpi-value" style="color: #F0AD4E;">{total_cbm_ocupado:,.2f} m³</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col3:
        st.markdown(f"""
        <div class="kpi-card" style="border-left: 4px solid #141E32;">
            <div class="kpi-label">PRODUCTOS (SKUs) SIN MOVIMIENTO</div>
            <div class="kpi-value" style="color: #141E32;">{total_skus_inactivos:,.0f} uds</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col4:
        st.markdown(f"""
        <div class="kpi-card" style="border-left: 4px solid #5AA06E;">
            <div class="kpi-label">EXISTENCIA FÍSICA INACTIVA</div>
            <div class="kpi-value" style="color: #5AA06E;">{total_uds_inactivas:,.0f} uds</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ── 5. TABLA DE DETALLE ──
    if not df_sobre_stock_filtrado.empty:
        df_show_t8 = df_sobre_stock_filtrado[['sku', 'nombre', 'categoria', 'stock_actual', 'stock_transito', 'ventas_6m', 'costo', 'valor_inventario_fob', 'cbm_ocupado']].copy()
        
        # Ordenar por valor de inventario descendente
        df_show_t8 = df_show_t8.sort_values('valor_inventario_fob', ascending=False)
        
        # Renombrar columnas para visualización clara
        df_show_t8.columns = [
            'Código SKU', 'Descripción', 'Categoría', 'Stock Actual', 'En Tránsito', 
            'Ventas (6 Meses)', 'Costo FOB (Unit)', 'Valor Inventario ($)', 'Volumen Ocupado (m³)'
        ]
        
        st.dataframe(
            df_show_t8.style.format({
                'Stock Actual': '{:,.0f}',
                'En Tránsito': '{:,.0f}',
                'Ventas (6 Meses)': '{:,.0f}',
                'Costo FOB (Unit)': '${:,.2f}',
                'Valor Inventario ($)': '${:,.2f}',
                'Volumen Ocupado (m³)': '{:,.3f}'
            }),
            use_container_width=True,
            height=400
        )
        
        # Botón de Descarga
        csv_t8 = df_sobre_stock_filtrado.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="Descargar Reporte de Sobre Stock (CSV)",
            data=csv_t8,
            file_name="reporte_sobre_stock_muerto.csv",
            mime="text/csv",
            key="btn_descarga_t8"
        )
    else:
        st.info("No se encontraron productos que coincidan con los criterios seleccionados.")

# Footer Masshopping
st.markdown("""
<div class="masshopping-footer">
    2026 MASSHOPPING - Sistema de Gestion Logistica y Planificacion Inteligente de Inventarios
</div>
""", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import numpy as np
import math
import os
import datetime
import requests
from scipy import stats
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Configuracion de pagina Masshopping
st.set_page_config(
    page_title="Masshopping Admin | Planificador Logistico & Contenedores",
    page_icon=os.path.join("assets", "logo.png") if os.path.exists(os.path.join("assets", "logo.png")) else ("Masshoping_logo.png" if os.path.exists("Masshoping_logo.png") else "\U0001F4E6"),
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
# GOOGLE SHEETS SCHEMA & DIALOG MODAL
# ══════════════════════════════════════════════════════════════════════════════
GOOGLE_SHEET_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwPxrh1w7_6oOYgrKS5TJQ9HECimcSsVOUNsAADd1voEvEEiOiON0_kFCHxY3e_SLrc/exec"

def construir_df_intermedio_gsheet(df_sel, flete_cbm_val=500.0, df_catalogo=None):
    """
    Construye el DataFrame Intermedio adaptado exactamente al Schema de Google Sheets (31 columnas):
    ['CODIGO', 'FOTO', 'PRODUCTO', 'CANTIDAD', 'COSTO', 'CANTIDAD POR CAJA',
     'CANTIDAD DE CAJAS', 'CM_A', 'CM_L', 'CM_P', 'CBM', 'TOTAL CBM',
     'COSTO CAJA', 'COSTO TOTAL ENVIO', 'COSTO ENVIO UNIT',
     'COSTO UNITARIO PROD', 'COSTO TOTAL', 'VENTA MAYOR', 'GANANCIA MAYOR',
     'GANANCIA MAYOR %', 'GANANCIA TOTAL MAYOR', 'MARGEN SEDE',
     'MARGEN ESTE', '% TASA', 'COMI_CASHEA', 'COMI_MELI', 'COSTO CASHEA',
     'VENTA CASHEA', 'GANANCIA CASHEA', 'GANANCIA CASHEA %',
     'GANANCIA TOTAL']
    """
    df_work = df_sel.copy()
    
    # Si faltan cm_a, cm_l, cm_p en df_sel, unirlas desde el catalogo general si está disponible
    if df_catalogo is not None and not df_catalogo.empty:
        cols_missing = [c for c in ['cm_a', 'cm_l', 'cm_p'] if c not in df_work.columns and c in df_catalogo.columns]
        if cols_missing:
            df_work = pd.merge(df_work, df_catalogo[['sku'] + cols_missing].drop_duplicates('sku'), on='sku', how='left')

    df_out = pd.DataFrame(index=df_work.index)
    
    def get_series_num(df, col, default=0.0):
        if col in df.columns:
            return pd.to_numeric(df[col], errors='coerce').fillna(default)
        return pd.Series(default, index=df.index)

    def get_series_str(df, col, default=''):
        if col in df.columns:
            return df[col].fillna(default).astype(str).str.strip()
        return pd.Series(default, index=df.index)

    # 1. CODIGO
    df_out['CODIGO'] = get_series_str(df_work, 'sku', '')
    
    # 2. FOTO
    df_out['FOTO'] = get_series_str(df_work, 'imagen_url', '')
    
    # 3. PRODUCTO
    df_out['PRODUCTO'] = get_series_str(df_work, 'nombre', 'Sin Nombre')
    
    # Cantidades base
    cajas = get_series_num(df_work, 'pedir_cajas', 0).astype(int)
    uds_caja = get_series_num(df_work, 'cantidad_por_caja', 1).clip(lower=1).astype(int)
    total_uds = cajas * uds_caja
    costo_fob = get_series_num(df_work, 'costo', 0.0)
    
    # 4. CANTIDAD (Total Uds)
    df_out['CANTIDAD'] = total_uds
    
    # 5. COSTO (FOB Unit)
    df_out['COSTO'] = np.where(costo_fob > 0, costo_fob.round(2), '')
    
    # 6. CANTIDAD POR CAJA
    df_out['CANTIDAD POR CAJA'] = uds_caja
    
    # 7. CANTIDAD DE CAJAS
    df_out['CANTIDAD DE CAJAS'] = cajas
    
    # Dimensiones
    cm_a = get_series_num(df_work, 'cm_a', 0.0)
    cm_l = get_series_num(df_work, 'cm_l', 0.0)
    cm_p = get_series_num(df_work, 'cm_p', 0.0)
    has_dims = (cm_a > 0) & (cm_l > 0) & (cm_p > 0)
    
    # 8. CM_A, 9. CM_L, 10. CM_P (si no existen, dejar estrictamente en blanco "")
    df_out['CM_A'] = np.where(cm_a > 0, cm_a.round(1), '')
    df_out['CM_L'] = np.where(cm_l > 0, cm_l.round(1), '')
    df_out['CM_P'] = np.where(cm_p > 0, cm_p.round(1), '')
    
    # 11. CBM (por caja) - Si existe CBMM > 0 o dimensiones completas, calcularlo. Si no existe, dejar estrictamente en blanco ("")
    cbm_raw = get_series_num(df_work, 'CBMM', 0.0)
    cbm_calc = np.where(cbm_raw > 0, cbm_raw, np.where(has_dims, (cm_a * cm_l * cm_p) / 1000000.0, 0.0))
    has_cbm = cbm_calc > 0
    df_out['CBM'] = np.where(has_cbm, np.round(cbm_calc, 4), '')
    
    # 12. TOTAL CBM (si no hay CBM válido, en blanco)
    total_cbm = np.where(has_cbm, cajas * cbm_calc, 0.0)
    df_out['TOTAL CBM'] = np.where(has_cbm & (total_cbm > 0), np.round(total_cbm, 4), '')
    
    # 13. COSTO CAJA (Costo FOB * Uds por caja)
    costo_caja = costo_fob * uds_caja
    df_out['COSTO CAJA'] = np.where(costo_fob > 0, costo_caja.round(2), '')
    
    # 14. COSTO TOTAL ENVIO (si no hay CBM, en blanco)
    costo_total_envio = np.where(has_cbm, total_cbm * float(flete_cbm_val), 0.0)
    df_out['COSTO TOTAL ENVIO'] = np.where(has_cbm & (costo_total_envio > 0), np.round(costo_total_envio, 2), '')
    
    # 15. COSTO ENVIO UNIT (si no hay CBM, en blanco)
    cbm_unit = np.where(has_cbm & (uds_caja > 0), cbm_calc / uds_caja, 0.0)
    costo_envio_unit = np.where(has_cbm & (uds_caja > 0), cbm_unit * float(flete_cbm_val), 0.0)
    df_out['COSTO ENVIO UNIT'] = np.where(has_cbm & (costo_envio_unit > 0), np.round(costo_envio_unit, 2), '')
    
    # 16. COSTO UNITARIO PROD (DDP) (si no hay CBM, en blanco)
    costo_unit_prod = np.where(has_cbm & (costo_fob > 0), costo_fob + costo_envio_unit, 0.0)
    df_out['COSTO UNITARIO PROD'] = np.where(has_cbm & (costo_unit_prod > 0), np.round(costo_unit_prod, 2), '')
    
    # 17. COSTO TOTAL (Total DDP) (si no hay CBM, en blanco)
    costo_total = np.where(has_cbm & (total_uds > 0) & (costo_unit_prod > 0), total_uds * costo_unit_prod, 0.0)
    df_out['COSTO TOTAL'] = np.where(has_cbm & (costo_total > 0), np.round(costo_total, 2), '')
    
    # 18 a 31: Precios de venta, márgenes y comisiones
    # Dejados en blanco ("") para llenado o fórmulas en Google Sheets
    df_out['VENTA MAYOR'] = ''
    df_out['GANANCIA MAYOR'] = ''
    df_out['GANANCIA MAYOR %'] = ''
    df_out['GANANCIA TOTAL MAYOR'] = ''
    df_out['MARGEN SEDE'] = ''
    df_out['MARGEN ESTE'] = ''
    df_out['% TASA'] = ''
    df_out['COMI_CASHEA'] = ''
    df_out['COMI_MELI'] = ''
    df_out['COSTO CASHEA'] = ''
    df_out['VENTA CASHEA'] = ''
    df_out['GANANCIA CASHEA'] = ''
    df_out['GANANCIA CASHEA %'] = ''
    df_out['GANANCIA TOTAL'] = ''
    
    columnas_schema = [
        'CODIGO', 'FOTO', 'PRODUCTO', 'CANTIDAD', 'COSTO', 'CANTIDAD POR CAJA',
        'CANTIDAD DE CAJAS', 'CM_A', 'CM_L', 'CM_P', 'CBM', 'TOTAL CBM',
        'COSTO CAJA', 'COSTO TOTAL ENVIO', 'COSTO ENVIO UNIT',
        'COSTO UNITARIO PROD', 'COSTO TOTAL', 'VENTA MAYOR', 'GANANCIA MAYOR',
        'GANANCIA MAYOR %', 'GANANCIA TOTAL MAYOR', 'MARGEN SEDE',
        'MARGEN ESTE', '% TASA', 'COMI_CASHEA', 'COMI_MELI', 'COSTO CASHEA',
        'VENTA CASHEA', 'GANANCIA CASHEA', 'GANANCIA CASHEA %',
        'GANANCIA TOTAL'
    ]
    return df_out[columnas_schema]

def reset_seleccion_estado():
    for k in ['editor_masshopping_cont', 'editor_pedido_optimo_tab7', 'chk_seleccionar_todos_opt', 'chk_seleccionar_todos_t1']:
        if k in st.session_state:
            del st.session_state[k]

@st.dialog("🚢 Asignar Productos a Contenedor en Google Sheets", width="large")
def modal_asignar_contenedor_gsheet(df_sel, flete_cbm_val=500.0, df_catalogo=None):
    df_intermedio = construir_df_intermedio_gsheet(df_sel, flete_cbm_val, df_catalogo)
    
    st.markdown(f"Estás a punto de exportar **{len(df_intermedio)} productos seleccionados** estructurados con el **Schema oficial de Google Sheets (31 Columnas)**.")
    
    cajas_tot = int(pd.to_numeric(df_intermedio['CANTIDAD DE CAJAS'], errors='coerce').fillna(0).sum())
    cbm_tot = float(pd.to_numeric(df_intermedio['TOTAL CBM'], errors='coerce').fillna(0.0).sum())
    
    # Calcular costo FOB y DDP total numéricos
    fob_calc = pd.to_numeric(df_intermedio['CANTIDAD'], errors='coerce').fillna(0) * pd.to_numeric(df_intermedio['COSTO'], errors='coerce').fillna(0.0)
    fob_tot = float(fob_calc.sum())
    ddp_tot = float(pd.to_numeric(df_intermedio['COSTO TOTAL'], errors='coerce').fillna(0.0).sum())
    
    col_k1, col_k2, col_k3, col_k4 = st.columns(4)
    with col_k1:
        st.metric("Total Cajas", f"{cajas_tot:,}")
    with col_k2:
        st.metric("Volumen CBM", f"{cbm_tot:,.2f} m³")
    with col_k3:
        st.metric("Inversión FOB", f"${fob_tot:,.2f}")
    with col_k4:
        st.metric("Costo Total DDP", f"${ddp_tot:,.2f}")
    
    st.markdown("---")
    contenedor_nombre = st.text_input(
        "Nombre de la Pestaña / Contenedor en Google Sheets:",
        placeholder="Ej: Contenedor Moscú, Egipto Julio, etc.",
        key="input_nombre_contenedor_modal"
    )
    
    st.caption("📋 Vista previa del DataFrame Intermedio a exportar (31 Columnas):")
    st.dataframe(
        df_intermedio,
        column_config={
            "FOTO": st.column_config.ImageColumn("Foto", help="Foto del producto"),
            "COSTO": st.column_config.NumberColumn("Costo FOB ($)", format="$%.2f"),
            "CBM": st.column_config.NumberColumn("CBM/Caja", format="%.3f"),
            "TOTAL CBM": st.column_config.NumberColumn("Total CBM", format="%.3f"),
            "COSTO CAJA": st.column_config.NumberColumn("Costo Caja ($)", format="$%.2f"),
            "COSTO TOTAL ENVIO": st.column_config.NumberColumn("Flete Total ($)", format="$%.2f"),
            "COSTO ENVIO UNIT": st.column_config.NumberColumn("Flete Unit ($)", format="$%.2f"),
            "COSTO UNITARIO PROD": st.column_config.NumberColumn("Costo DDP ($)", format="$%.2f"),
            "COSTO TOTAL": st.column_config.NumberColumn("Costo Total DDP ($)", format="$%.2f"),
        },
        use_container_width=True,
        height=260
    )
    
    if st.button("🚀 Confirmar y Cargar a Google Sheets (31 Columnas)", type="primary", use_container_width=True):
        if not contenedor_nombre or not contenedor_nombre.strip():
            st.error("⚠️ Por favor ingresa un nombre para el contenedor u hoja.")
            return
        
        with st.spinner(f"Escribiendo {len(df_intermedio)} productos en la hoja '{contenedor_nombre.strip()}'..."):
            df_enviar = df_intermedio.copy()
            # Formatear la columna FOTO con la fórmula =IMAGE("url") para renderizar la imagen directamente en Google Sheets
            df_enviar['FOTO'] = df_enviar['FOTO'].apply(lambda x: f'=IMAGE("{x}")' if isinstance(x, str) and str(x).strip().startswith('http') else x)
            filas_para_enviar = df_enviar.fillna('').values.tolist()
            payload = {
                "container": contenedor_nombre.strip(),
                "headers": list(df_intermedio.columns),
                "items": filas_para_enviar
            }
            
            try:
                res = requests.post(GOOGLE_SHEET_WEBHOOK_URL, json=payload, timeout=120)
                if res.status_code == 200:
                    try:
                        res_json = res.json()
                        if res_json.get("status") == "success":
                            st.session_state['gsheet_success_msg'] = f"✅ ¡Éxito! Se registraron {len(filas_para_enviar)} productos con 31 columnas en la pestaña '{contenedor_nombre.strip()}' de Google Sheets."
                            reset_seleccion_estado()
                            st.rerun()
                        else:
                            st.error(f"Error devuelto por Google: {res_json.get('message')}")
                    except Exception:
                        st.session_state['gsheet_success_msg'] = f"✅ ¡Éxito! Se registraron {len(filas_para_enviar)} productos con 31 columnas en la pestaña '{contenedor_nombre.strip()}' de Google Sheets."
                        reset_seleccion_estado()
                        st.rerun()
                else:
                    st.error(f"Error en servidor Google (Status {res.status_code}): {res.text}")
            except Exception as ex:
                st.error(f"Error de conexión: {ex}")

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
# 2. CARGA DE DATOS EN CACHE (DESDE data/)
# ══════════════════════════════════════════════════════════════════════════════
def obtener_ruta_data(nombre_archivo):
    """Busca el archivo en data/ primero, y luego en la raíz como fallback."""
    ruta_data = os.path.join('data', nombre_archivo)
    if os.path.exists(ruta_data):
        return ruta_data
    return nombre_archivo

@st.cache_data(show_spinner="Cargando base de datos consolidada Masshopping...")
def cargar_datos_base(mtime_tranz=0.0, mtime_ventas=0.0, mtime_art=0.0, mtime_cons=0.0):
    # 1. Transacciones unificadas (Prioridad: data/tranzabilidad.csv como fuente única de verdad)
    ruta_tranz = obtener_ruta_data('tranzabilidad.csv')
    ruta_ventas = obtener_ruta_data('ventas.csv')
    df_fco_ult = pd.DataFrame(columns=['sku', 'ultima_fecha_fco'])
    
    if os.path.exists(ruta_tranz):
        try:
            df_tranz = pd.read_csv(ruta_tranz, encoding='utf-8-sig', low_memory=False)
        except Exception:
            df_tranz = pd.read_csv(ruta_tranz, encoding='latin1', low_memory=False)
            
        col_art = 'Artículo' if 'Artículo' in df_tranz.columns else [c for c in df_tranz.columns if 'rt' in c.lower() and 'digo' not in c.lower()][0]
        col_tipo = [c for c in df_tranz.columns if 'Tipo' in c and 'Trans' in c][0]
        col_fecha = [c for c in df_tranz.columns if 'Fecha' in c and 'Trans' in c][0]
        col_cant = [c for c in df_tranz.columns if 'Cantidad' in c][0]
        
        df_tranz['sku'] = df_tranz[col_art].astype(str).apply(lambda x: x.split('-')[0].strip())
        df_tranz['nombre_trans'] = df_tranz[col_art].astype(str).apply(lambda x: x.split('-', 1)[1].strip() if '-' in x else x)
        df_tranz['fecha'] = pd.to_datetime(df_tranz[col_fecha], format='mixed', dayfirst=True)
        df_tranz['cantidad'] = pd.to_numeric(df_tranz[col_cant].astype(str).str.replace(',', '', regex=False), errors='coerce').fillna(0.0)
        
        tipo_str = df_tranz[col_tipo].astype(str)
        is_fve = tipo_str.str.startswith('FVE')
        is_ncv = tipo_str.str.startswith('NCV')
        is_fco = tipo_str.str.startswith('FCO')
        
        # Demanda Real: Ventas netas = FVE (+) menos NCV (-)
        # Excluye explícitamente ajustes y traslados internos: AJE, AJS, TRE, TRS, REQ, NDV
        df_ventas = df_tranz[is_fve | is_ncv].copy()
        df_ventas['cantidad'] = np.where(df_ventas[col_tipo].astype(str).str.startswith('FVE'), df_ventas['cantidad'], -df_ventas['cantidad'])
        
        df_clean = df_ventas[['sku', 'fecha', 'nombre_trans', 'cantidad']].copy()
        df_clean['total_venta'] = df_clean['cantidad'] * 1.0
        df_clean['total_costo'] = df_clean['cantidad'] * 1.0
        df_clean['costo_unit_trans'] = 1.0
        df_clean['sku'] = df_clean['sku'].astype(str).str.strip()
        df_clean = df_clean[df_clean['sku'] != 'MASS1575']
        
        # Historial de compras FCO para trazabilidad de reposición
        df_fco = df_tranz[is_fco].copy()
        df_fco_ult = df_fco.groupby('sku')['fecha'].max().reset_index()
        df_fco_ult.columns = ['sku', 'ultima_fecha_fco']
        df_fco_ult['sku'] = df_fco_ult['sku'].astype(str).str.strip()
        df_fco_ult = df_fco_ult[df_fco_ult['sku'] != 'MASS1575']
        
        # Reposición Neta Histórica = FCO (+) menos DEC (-)
        is_dec = tipo_str.str.startswith('DEC')
        df_repo = df_tranz[is_fco | is_dec].copy()
        df_repo['cantidad'] = np.where(df_repo[col_tipo].astype(str).str.startswith('FCO'), df_repo['cantidad'], -df_repo['cantidad'])
        df_reposicion = df_repo[['sku', 'fecha', 'cantidad']].copy()
        df_reposicion['sku'] = df_reposicion['sku'].astype(str).str.strip()
        df_reposicion = df_reposicion[df_reposicion['sku'] != 'MASS1575']
    elif os.path.exists(ruta_ventas):
        df_reposicion = pd.DataFrame(columns=['sku', 'fecha', 'cantidad'])
        try:
            df_trans = pd.read_csv(ruta_ventas, encoding='utf-8-sig', low_memory=False)
        except Exception:
            df_trans = pd.read_csv(ruta_ventas, encoding='latin1', low_memory=False)
            
        col_art = [c for c in df_trans.columns if 'digo' in c and 'rt' in c][0]
        col_fecha = [c for c in df_trans.columns if 'Fecha' in c][0]
        col_nom_trans = [c for c in df_trans.columns if 'ombre' in c and 'rt' in c][0]
        
        df_clean = df_trans[[col_art, col_fecha, col_nom_trans, 'Cantidad', 'Total', 'Total Costo', 'Costo Unitario']].copy()
        df_clean.columns = ['sku', 'fecha', 'nombre_trans', 'cantidad', 'total_venta', 'total_costo', 'costo_unit_trans']
        df_clean['sku'] = df_clean['sku'].astype(str).str.strip()
        df_clean['cantidad'] = pd.to_numeric(df_clean['cantidad'], errors='coerce').fillna(0.0)
        df_clean['total_venta'] = pd.to_numeric(df_clean['total_venta'].astype(str).str.replace(',', ''), errors='coerce').fillna(0.0)
        df_clean['total_costo'] = pd.to_numeric(df_clean['total_costo'].astype(str).str.replace(',', ''), errors='coerce').fillna(0.0)
        df_clean['costo_unit_trans'] = pd.to_numeric(df_clean['costo_unit_trans'].astype(str).str.replace(',', ''), errors='coerce').fillna(0.0)
        df_clean['fecha'] = pd.to_datetime(df_clean['fecha'], format='mixed', dayfirst=True)
        df_clean = df_clean[df_clean['sku'] != 'MASS1575']
    else:
        df_reposicion = pd.DataFrame(columns=['sku', 'fecha', 'cantidad'])
        # Fallback a reportes individuales si existieran
        reports = [i + 4 for i in range(12)]
        dfs = [pd.read_csv(f"reporte ({r}).csv", encoding="latin1", low_memory=False) for r in reports if os.path.exists(f"reporte ({r}).csv")]
        df_trans = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
        if not df_trans.empty:
            col_art = [c for c in df_trans.columns if 'digo' in c and 'rt' in c][0]
            col_fecha = [c for c in df_trans.columns if 'Fecha' in c][0]
            col_nom_trans = [c for c in df_trans.columns if 'ombre' in c and 'rt' in c][0]
            df_clean = df_trans[[col_art, col_fecha, col_nom_trans, 'Cantidad', 'Total', 'Total Costo', 'Costo Unitario']].copy()
            df_clean.columns = ['sku', 'fecha', 'nombre_trans', 'cantidad', 'total_venta', 'total_costo', 'costo_unit_trans']
            df_clean['sku'] = df_clean['sku'].astype(str).str.strip()
            df_clean['cantidad'] = pd.to_numeric(df_clean['cantidad'], errors='coerce').fillna(0.0)
            df_clean['total_venta'] = pd.to_numeric(df_clean['total_venta'].astype(str).str.replace(',', ''), errors='coerce').fillna(0.0)
            df_clean['total_costo'] = pd.to_numeric(df_clean['total_costo'].astype(str).str.replace(',', ''), errors='coerce').fillna(0.0)
            df_clean['costo_unit_trans'] = pd.to_numeric(df_clean['costo_unit_trans'].astype(str).str.replace(',', ''), errors='coerce').fillna(0.0)
            df_clean['fecha'] = pd.to_datetime(df_clean['fecha'], format='mixed', dayfirst=True)
            df_clean = df_clean[df_clean['sku'] != 'MASS1575']
        else:
            df_clean = pd.DataFrame(columns=['sku', 'fecha', 'nombre_trans', 'cantidad', 'total_venta', 'total_costo', 'costo_unit_trans'])
    
    # 2. Extraer fallback de nombres de las transacciones (limpieza optimizada solo en SKUs únicos)
    df_nombres_trans = df_clean[['sku', 'nombre_trans']].drop_duplicates(subset=['sku'], keep='last').copy()
    df_nombres_trans['nombre_trans'] = df_nombres_trans['nombre_trans'].astype(str).apply(limpiar_mojibake)
    
    # 2b. Articulos (Stock actual actualizado desde data/articulos.xlsx)
    ruta_xlsx = obtener_ruta_data('articulos.xlsx')
    ruta_art_csv = obtener_ruta_data('articulos.csv')
    df_art = None
    if os.path.exists(ruta_xlsx):
        try:
            df_art = pd.read_excel(ruta_xlsx)
        except Exception:
            pass
        if df_art is None or df_art.empty:
            try:
                import zipfile, xml.etree.ElementTree as ET
                with zipfile.ZipFile(ruta_xlsx, 'r') as z:
                    sst = []
                    if 'xl/sharedStrings.xml' in z.namelist():
                        sst_root = ET.fromstring(z.read('xl/sharedStrings.xml'))
                        ns_sst = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                        for si in sst_root.findall('.//ns:si', ns_sst):
                            texts = [t.text or '' for t in si.findall('.//ns:t', ns_sst)]
                            sst.append(''.join(texts))
                    sheet_path = next((name for name in z.namelist() if name.lower() == 'xl/worksheets/sheet1.xml'), None)
                    if sheet_path:
                        root = ET.fromstring(z.read(sheet_path))
                        ns = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                        rows = []
                        for row in root.findall('.//ns:row', ns):
                            r_vals = []
                            for c in row.findall('ns:c', ns):
                                t = c.get('t')
                                v = c.find('ns:v', ns)
                                val = v.text if v is not None else ''
                                if t == 's' and val and val.isdigit():
                                    idx = int(val)
                                    val = sst[idx] if idx < len(sst) else val
                                r_vals.append(val)
                            if any(r_vals):
                                rows.append(r_vals)
                        if rows:
                            df_art = pd.DataFrame(rows[1:], columns=rows[0])
            except Exception:
                pass
                
    if df_art is None or df_art.empty:
        if os.path.exists(ruta_art_csv):
            df_art = pd.read_csv(ruta_art_csv, encoding='latin1')

    col_art_art = [c for c in df_art.columns if 'digo' in c and 'rt' in c][0]
    col_exist = [c for c in df_art.columns if 'Existencia' in c or 'Disponible' in c][0]
    col_nom_art = [c for c in df_art.columns if ('rt' in c or 'culo' in c) and 'digo' not in c][0]
    col_cat = [c for c in df_art.columns if 'teg' in c.lower() and 'digo' not in c.lower()][0]
    
    df_art_clean = df_art[[col_art_art, col_exist, col_nom_art, col_cat]].rename(
        columns={col_art_art: 'sku', col_exist: 'stock_actual', col_nom_art: 'nombre_articulo', col_cat: 'categoria'}
    )
    df_art_clean['sku'] = df_art_clean['sku'].astype(str).str.strip()
    df_art_clean['stock_actual'] = pd.to_numeric(df_art_clean['stock_actual'].astype(str).str.replace(',', ''), errors='coerce').fillna(0.0)
    df_art_clean['nombre_articulo'] = df_art_clean['nombre_articulo'].astype(str).apply(limpiar_mojibake)
    df_art_clean['categoria'] = df_art_clean['categoria'].fillna('GENERAL').astype(str).str.strip()
    
    # Agrupar por SKU sumando el stock actual si hay múltiples ubicaciones/lotes
    df_art_clean = df_art_clean.groupby('sku', as_index=False).agg({
        'stock_actual': 'sum',
        'nombre_articulo': 'first',
        'categoria': 'first'
    })
    df_art_clean = df_art_clean[df_art_clean['sku'] != 'MASS1575']
    
    # 3. Metadata logistica + Stock en Transito (desde data/consolidado.csv)
    ruta_cons = obtener_ruta_data('consolidado.csv')
    df_cons = pd.read_csv(ruta_cons, encoding='latin1')
    
    # Extraer stock en transito
    contenedores_transito = [
        'CONTENEDORES JULIO',
        'CONTENEDOR EGIPTO',
        'CONTENEDOR  REVESTIMIENTO ',
        'CONTENEDOR REVESTIMIENTO',
        'CONTENEDOR SEPTIEMBRE'
    ]
    df_transit = df_cons[df_cons['contenedor'].astype(str).str.strip().isin([c.strip() for c in contenedores_transito]) | df_cons['contenedor'].isin(contenedores_transito)].copy()
    df_transit['codigo'] = df_transit['codigo'].astype(str).str.strip()
    df_transit['cantidad'] = pd.to_numeric(df_transit['cantidad'].astype(str).str.replace(',', '', regex=False), errors='coerce').fillna(0)
    df_transit_exp = (
        df_transit.assign(sku=df_transit['codigo'].str.split(r'\n|[\n\s]+'))
        .explode('sku').dropna(subset=['sku'])
    )
    df_transit_exp['sku'] = df_transit_exp['sku'].str.strip()
    df_transit_exp = df_transit_exp[df_transit_exp['sku'] != '']
    df_stock_transito = df_transit_exp.groupby('sku')['cantidad'].sum().reset_index()
    df_stock_transito.columns = ['sku', 'stock_transito']
    df_stock_transito = df_stock_transito[df_stock_transito['sku'] != 'MASS1575']
    
    # Metadata de costos/empaque
    df_cons_meta = df_cons[['codigo', 'costo', 'cantidad_por_caja', 'CBMM', 'cm_a', 'cm_l', 'cm_p']].dropna(subset=['codigo'])
    df_cons_meta['costo'] = pd.to_numeric(df_cons_meta['costo'].astype(str).str.replace('$', '', regex=False).str.replace(',', ''), errors='coerce')
    df_cons_meta['cantidad_por_caja'] = pd.to_numeric(df_cons_meta['cantidad_por_caja'], errors='coerce')
    df_cons_meta['CBMM'] = pd.to_numeric(df_cons_meta['CBMM'], errors='coerce')
    df_cons_meta['cm_a'] = pd.to_numeric(df_cons_meta['cm_a'], errors='coerce')
    df_cons_meta['cm_l'] = pd.to_numeric(df_cons_meta['cm_l'], errors='coerce')
    df_cons_meta['cm_p'] = pd.to_numeric(df_cons_meta['cm_p'], errors='coerce')
    df_cons_exp = (
        df_cons_meta.assign(sku=df_cons_meta['codigo'].astype(str).str.strip().str.split(r'\n|[\n\s]+'))
        .explode('sku').dropna(subset=['sku'])
    )
    df_cons_exp['sku'] = df_cons_exp['sku'].str.strip()
    df_cons_exp = df_cons_exp[df_cons_exp['sku'] != ''].drop_duplicates(subset=['sku'], keep='last')
    df_metadata = df_cons_exp[['sku', 'costo', 'cantidad_por_caja', 'CBMM', 'cm_a', 'cm_l', 'cm_p']]
    df_metadata = df_metadata[df_metadata['sku'] != 'MASS1575']
    
    # 4. Catalogo de Imagenes (desde data/images.csv o IMAGES.csv)
    ruta_images = obtener_ruta_data('images.csv')
    if not os.path.exists(ruta_images):
        ruta_images = obtener_ruta_data('IMAGES.csv')
        
    df_images = pd.read_csv(ruta_images, encoding='latin1')
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
    
    df_info_prod['nombre_final'] = df_info_prod['nombre'].fillna(df_info_prod['nombre_articulo']).fillna(df_info_prod['nombre_trans']).fillna('Sin Descripcion')
    df_info_prod['nombre'] = df_info_prod['nombre_final'].replace('nan', 'Sin Descripcion')
    df_info_prod['categoria'] = df_info_prod['categoria'].fillna('GENERAL')
    df_info_prod = df_info_prod[['sku', 'nombre', 'categoria', 'imagen_url']]
    
    import json
    ruta_p2p = obtener_ruta_data('p2p.json')
    try:
        with open(ruta_p2p, 'r', encoding='utf-8') as f:
            p2p_data = json.load(f)
        
        dates = pd.to_datetime(p2p_data['categories'])
        sell_item = next(item for item in p2p_data['items'] if 'SELL' in item['tm'])
        p2p_values = sell_item['values']
        
        df_p2p = pd.DataFrame({'fecha': dates, 'usd_rate': p2p_values})
        df_p2p = df_p2p.sort_values('fecha').drop_duplicates('fecha', keep='last')
        df_p2p['var_pct'] = df_p2p['usd_rate'].pct_change() * 100
        df_p2p['var_pct'] = df_p2p['var_pct'].fillna(0)
    except Exception:
        df_p2p = pd.DataFrame({'fecha': [], 'usd_rate': [], 'var_pct': []})
    
    return df_clean, df_art_clean[['sku', 'stock_actual', 'categoria']], df_metadata, df_info_prod, df_stock_transito, df_p2p, df_fco_ult, df_reposicion

# Timestamps de invalidacion de cache
p_tr = obtener_ruta_data('tranzabilidad.csv')
p_v = obtener_ruta_data('ventas.csv')
p_a = obtener_ruta_data('articulos.xlsx')
p_c = obtener_ruta_data('consolidado.csv')
mtime_tranz = os.path.getmtime(p_tr) if os.path.exists(p_tr) else 0.0
mtime_ventas = os.path.getmtime(p_v) if os.path.exists(p_v) else 0.0
mtime_art = os.path.getmtime(p_a) if os.path.exists(p_a) else 0.0
mtime_cons = os.path.getmtime(p_c) if os.path.exists(p_c) else 0.0

df_trans, df_art, df_metadata, df_info_prod, df_stock_transito, df_p2p, df_fco_ult, df_reposicion = cargar_datos_base(mtime_tranz, mtime_ventas, mtime_art, mtime_cons)

# Excluir de forma global y permanente el SKU MASS1350 de todo el sistema
df_trans = df_trans[df_trans['sku'] != 'MASS1350']
df_art = df_art[df_art['sku'] != 'MASS1350']
if not df_reposicion.empty:
    df_reposicion = df_reposicion[df_reposicion['sku'] != 'MASS1350']

# ══════════════════════════════════════════════════════════════════════════════
# 3. SIDEBAR CORPORATIVO MASSHOPPING
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    logo_path = os.path.join('assets', 'logo.png') if os.path.exists(os.path.join('assets', 'logo.png')) else 'Masshoping_logo.png'
    if os.path.exists(logo_path):
        st.image(logo_path, width=170)
    st.markdown("### Motor de logística para compras masivas")
    st.caption("Panel de Control y Compras Estratégicas")
    
    if st.button("🔄 Recargar Base de Datos (Limpiar Caché)", use_container_width=True, help="Fuerza la recarga de data/ventas.csv y data/articulos.xlsx"):
        st.cache_data.clear()
        st.rerun()
        
    st.divider()
    
    st.subheader("Ventana Temporal de Demanda")
    opcion_tiempo = st.selectbox(
        "Período analizado:",
        ["Último Año", "Últimos 6 meses", "Últimos 3 meses", "Todo el historial", "Personalizado"],
        key="sidebar_periodo"
    )
    
    fecha_max = df_trans['fecha'].max()
    fecha_min = df_trans['fecha'].min()
    if "Año" in opcion_tiempo:
        fecha_corte = fecha_max - pd.DateOffset(years=1)
        df_trans_filtrada = df_trans[df_trans['fecha'] >= fecha_corte].copy()
    elif "6 meses" in opcion_tiempo:
        fecha_corte = fecha_max - pd.DateOffset(months=6)
        df_trans_filtrada = df_trans[df_trans['fecha'] >= fecha_corte].copy()
    elif "3 meses" in opcion_tiempo:
        fecha_corte = fecha_max - pd.DateOffset(months=3)
        df_trans_filtrada = df_trans[df_trans['fecha'] >= fecha_corte].copy()
    elif "Personalizado" in opcion_tiempo:
        d_min = fecha_min.date() if pd.notnull(fecha_min) else datetime.date(2024, 1, 1)
        d_max = fecha_max.date() if pd.notnull(fecha_max) else datetime.date.today()
        rango_custom = st.date_input(
            "Rango de Fechas:",
            value=(d_min, d_max),
            min_value=d_min,
            max_value=d_max,
            key="sidebar_rango_custom"
        )
        if isinstance(rango_custom, (tuple, list)) and len(rango_custom) == 2:
            f_ini, f_fin = rango_custom
            df_trans_filtrada = df_trans[
                (df_trans['fecha'].dt.date >= f_ini) &
                (df_trans['fecha'].dt.date <= f_fin)
            ].copy()
        elif isinstance(rango_custom, (tuple, list)) and len(rango_custom) == 1:
            f_ini = rango_custom[0]
            df_trans_filtrada = df_trans[df_trans['fecha'].dt.date >= f_ini].copy()
        else:
            df_trans_filtrada = df_trans.copy()
    else:
        df_trans_filtrada = df_trans.copy()
        
    st.divider()
    st.subheader("Configuración de Abastecimiento")
    lead_time = st.slider(
        "Tiempo de Entrega / Lead Time (Semanas):",
        min_value=1,
        max_value=52,
        value=15,
        step=1,
        help="Tiempo en semanas que tarda el proveedor en entregar el pedido. Modifica dinámicamente la Demanda Esperada en Lead Time y el ROP.",
        key="sidebar_lead_time"
    )
    
    factor_ss_pct = st.slider(
        "Margen de Stock de Seguridad (% adicional):",
        min_value=0,
        max_value=100,
        value=0,
        step=5,
        help="Por defecto en 0% para no sobrestimar pedidos. Un valor de 0% calcula el ROP exactamente sobre la Demanda Esperada en Lead Time sin colchón adicional.",
        key="sidebar_factor_ss"
    )
    factor_ss = factor_ss_pct / 100.0
    
    lt_m_equiv = 3.5 if lead_time == 15 else round(lead_time / (52.0 / 12.0), 1)
    st.caption(f"🗓️ *Lead Time equivalente modelo mensual: **{lt_m_equiv} meses**.*")
    
    st.divider()
    st.subheader("Parámetros del Contenedor")
    capacidad_cont = st.number_input("Capacidad Contenedor 40HQ (CBM):", value=68.0, step=1.0, key="sidebar_cap_cont")
    flete_cbm = st.number_input("Flete por CBM (USD):", value=500.0, step=5.0, key="sidebar_flete")
    costo_orden = st.number_input("Costo Administrativo Orden (USD):", value=50.0, step=5.0, key="sidebar_costo_orden")
    tasa_mant = st.slider("Tasa Mantenimiento Inv. (% anual):", min_value=0.05, max_value=0.40, value=0.15, step=0.01, key="sidebar_tasa_mant")
    
    st.divider()
    st.caption("Masshopping Supply Chain Portal v3.0")

# ══════════════════════════════════════════════════════════════════════════════
# 4. MOTOR VECTORIZADO DE CALCULO
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def ejecutar_motor(df_t, _df_a, _df_m, _df_info, _df_transit, _df_fco, lt, flete, cap_cont, tasa, c_orden, lookback_weeks=None, factor_ss=0.0):
    lt = int(lt)
    # Lead Time mensual equivalente (3.5 meses para 15 semanas)
    lt_m = 3.5 if lt == 15 else round(lt / (52.0 / 12.0), 2)
    lt_m_roll = max(1, int(round(lt_m)))
    df_semanal = df_t.groupby(['sku', pd.Grouper(key='fecha', freq='W-MON')])['cantidad'].sum().unstack(fill_value=0.0)
    df_mensual = df_t.groupby(['sku', pd.Grouper(key='fecha', freq='MS')])['cantidad'].sum().unstack(fill_value=0.0)
    
    # ── CÁLCULO SKU POR SKU ULTRA OPTIMIZADO (NUMPY 2D) ──
    skus = df_semanal.index.tolist()
    w_mat = df_semanal.values
    m_mat = df_mensual.values
    n_skus = len(skus)
    
    adi_umbral = 1.32
    cv2_umbral = 0.49
    percentil_ss = 90
    winsor_percentil = 0.95
    
    resultados = []
    for i in range(n_skus):
        sku = skus[i]
        w_row = w_mat[i]
        m_row = m_mat[i]
        
        # ── 1. MOTOR SEMANAL ──
        if w_row.sum() == 0:
            res_sku = {
                'sku': sku, 'cuadrante': 'sin_datos', 'adi': 0, 'cv': np.nan, 'n_pos': 0,
                'demanda_semanal_prom': 0.0, 'demanda_semanal_std': 0.0,
                'media_movil_4sem': 0.0, 'tendencia': 'Sin Datos',
                'mu_sba': 0.0, 'demanda_esperada_lt': 0.0, 'ss_empirico': 0.0, 'rop': 0.0
            }
        else:
            nz = np.nonzero(w_row)[0]
            first_idx = nz[0]
            ts_trim = w_row[first_idx:]
            
            if lookback_weeks is not None and len(ts_trim) > lookback_weeks:
                ts_win_slice = ts_trim[-lookback_weeks:]
            else:
                ts_win_slice = ts_trim
                
            n_per = len(ts_win_slice)
            pos = ts_win_slice[ts_win_slice > 0]
            n_pos = len(pos)
            adi = n_per / n_pos if n_pos > 0 else float('inf')
            
            if n_pos <= 1:
                cuad = 'sin_datos'
                cv2 = np.nan
                cv = np.nan
            else:
                mu_p = pos.mean()
                std_p = pos.std(ddof=1)
                cv2 = (std_p / mu_p)**2 if mu_p > 0 else 0.0
                cv = std_p / mu_p if mu_p > 0 else 0.0
                if adi < adi_umbral and cv2 < cv2_umbral:
                    cuad = 'smooth'
                elif adi >= adi_umbral and cv2 < cv2_umbral:
                    cuad = 'intermittent'
                elif adi < adi_umbral and cv2 >= cv2_umbral:
                    cuad = 'erratic'
                else:
                    cuad = 'lumpy'
                    
            if n_pos >= 2:
                clip_val = np.percentile(pos, winsor_percentil * 100)
                ts_win = np.clip(ts_win_slice, a_min=None, a_max=clip_val)
            else:
                ts_win = ts_win_slice.copy()
                
            mu_incond = ts_win.mean()
            mu_4w = ts_win[-4:].mean() if len(ts_win) >= 4 else mu_incond
            
            # Cálculo de tendencia porcentual (últimas 4 semanas vs 4 semanas anteriores)
            if len(ts_win) >= 8:
                prev_4w = ts_win[-8:-4].mean()
                if prev_4w > 0:
                    var_trend = ((mu_4w - prev_4w) / prev_4w) * 100.0
                elif mu_4w > 0:
                    var_trend = 100.0
                else:
                    var_trend = 0.0
                tendencia_txt = f"{'📈 +' if var_trend > 5 else ('📉 ' if var_trend < -5 else '➡️ ')}{var_trend:+.0f}%"
            elif len(ts_win) >= 4:
                tendencia_txt = "📈 Activo" if mu_4w > 0 else "➡️ Estable"
            else:
                tendencia_txt = "➡️ Estable"
            
            if len(ts_win) > 1:
                alpha = 2.0 / (min(8, len(ts_win)) + 1.0)
                weights = (1 - alpha) ** np.arange(len(ts_win))[::-1]
                mu_ewma = (ts_win * weights).sum() / weights.sum()
            else:
                mu_ewma = mu_incond
                
            if len(ts_win) <= 12 and ts_win[0] > 2.0 * max(mu_4w, 0.1):
                mu_vel = min(mu_ewma, mu_4w)
            elif mu_4w < mu_incond:
                mu_vel = 0.7 * mu_4w + 0.3 * mu_incond
            else:
                mu_vel = mu_incond
                
            if cuad == 'intermittent' and not np.isnan(cv2):
                mu_sba = max(0.0, mu_vel * (1.0 - cv2 / 2.0))
            else:
                mu_sba = mu_vel
                
            dem_lt = mu_sba * lt
            
            if cuad in ('lumpy', 'intermittent') and len(ts_win) >= lt:
                roll_sums = np.convolve(ts_win, np.ones(lt), mode='valid')
                errors = roll_sums - dem_lt
                ss_emp = max(0.0, float(np.percentile(errors, percentil_ss))) * factor_ss
            else:
                ss_emp = 0.0
                
            rop_w = dem_lt + ss_emp
            res_sku = {
                'sku': sku, 'cuadrante': cuad, 'adi': adi, 'cv': cv if not np.isnan(cv) else 0.0,
                'n_pos': n_pos, 'demanda_semanal_prom': mu_vel,
                'demanda_semanal_std': float(ts_win_slice.std(ddof=1)) if len(ts_win_slice) > 1 else 0.0,
                'media_movil_4sem': float(round(mu_4w, 1)),
                'tendencia': tendencia_txt,
                'mu_sba': mu_sba, 'demanda_esperada_lt': dem_lt, 'ss_empirico': ss_emp, 'rop': rop_w
            }
            
        # ── 2. MOTOR MENSUAL (LT = 3.5 meses) ──
        if m_row.sum() == 0:
            res_sku.update({
                'cuadrante_mensual': 'sin_datos', 'adi_mensual': 0, 'cv_mensual': 0.0, 'cv2_mensual': 0.0,
                'demanda_mensual_prom': 0.0, 'demanda_mensual_std': 0.0, 'mu_sba_mensual': 0.0,
                'demanda_esperada_lt_mensual': 0.0, 'ss_empirico_mensual': 0.0, 'rop_mensual': 0.0
            })
        else:
            nz_m = np.nonzero(m_row)[0]
            first_m_idx = nz_m[0]
            ts_trim_m = m_row[first_m_idx:]
            n_per_m = len(ts_trim_m)
            pos_m = ts_trim_m[ts_trim_m > 0]
            n_pos_m = len(pos_m)
            adi_m = n_per_m / n_pos_m if n_pos_m > 0 else float('inf')
            
            if n_pos_m <= 1:
                cuad_m = 'sin_datos'
                cv2_m = np.nan
                cv_m = np.nan
            else:
                mu_p_m = pos_m.mean()
                std_p_m = pos_m.std(ddof=1)
                cv2_m = (std_p_m / mu_p_m)**2 if mu_p_m > 0 else 0.0
                cv_m = std_p_m / mu_p_m if mu_p_m > 0 else 0.0
                if adi_m < adi_umbral and cv2_m < cv2_umbral:
                    cuad_m = 'smooth'
                elif adi_m >= adi_umbral and cv2_m < cv2_umbral:
                    cuad_m = 'intermittent'
                elif adi_m < adi_umbral and cv2_m >= cv2_umbral:
                    cuad_m = 'erratic'
                else:
                    cuad_m = 'lumpy'
                    
            if n_pos_m >= 2:
                clip_val_m = np.percentile(pos_m, winsor_percentil * 100)
                ts_win_m = np.clip(ts_trim_m, a_min=None, a_max=clip_val_m)
            else:
                ts_win_m = ts_trim_m.copy()
                
            mu_incond_m = ts_win_m.mean()
            mu_3m = ts_win_m[-3:].mean() if len(ts_win_m) >= 3 else mu_incond_m
            
            if len(ts_win_m) > 1:
                alpha_m = 2.0 / (min(4, len(ts_win_m)) + 1.0)
                weights_m = (1 - alpha_m) ** np.arange(len(ts_win_m))[::-1]
                mu_ewma_m = (ts_win_m * weights_m).sum() / weights_m.sum()
            else:
                mu_ewma_m = mu_incond_m
                
            if len(ts_win_m) <= 4 and ts_win_m[0] > 2.0 * max(mu_3m, 0.1):
                mu_vel_m = min(mu_ewma_m, mu_3m)
            elif mu_3m < mu_incond_m:
                mu_vel_m = 0.7 * mu_3m + 0.3 * mu_incond_m
            else:
                mu_vel_m = mu_incond_m
                
            if cuad_m == 'intermittent' and not np.isnan(cv2_m):
                mu_sba_m = max(0.0, mu_vel_m * (1.0 - cv2_m / 2.0))
            else:
                mu_sba_m = mu_vel_m
                
            dem_lt_m = mu_sba_m * lt_m
            
            if cuad_m in ('lumpy', 'intermittent') and len(ts_win_m) >= lt_m_roll:
                roll_sums_m = np.convolve(ts_win_m, np.ones(lt_m_roll), mode='valid')
                errors_m = roll_sums_m - (mu_sba_m * lt_m_roll)
                ss_emp_m = max(0.0, float(np.percentile(errors_m, percentil_ss))) * factor_ss
            else:
                ss_emp_m = 0.0
                
            rop_m = dem_lt_m + ss_emp_m
            res_sku.update({
                'cuadrante_mensual': cuad_m, 'adi_mensual': adi_m,
                'cv_mensual': cv_m if not np.isnan(cv_m) else 0.0,
                'cv2_mensual': cv2_m if not np.isnan(cv2_m) else 0.0,
                'demanda_mensual_prom': mu_vel_m,
                'demanda_mensual_std': float(ts_trim_m.std(ddof=1)) if len(ts_trim_m) > 1 else 0.0,
                'mu_sba_mensual': mu_sba_m, 'demanda_esperada_lt_mensual': dem_lt_m,
                'ss_empirico_mensual': ss_emp_m, 'rop_mensual': rop_m
            })
        resultados.append(res_sku)
            
    df_calc = pd.DataFrame(resultados)
    
    # ── COMBINACIÓN CON METADATA Y CLASIFICACIONES ──
    ventas = df_t.groupby('sku').agg(
        total_ventas=('total_venta', 'sum'),
        total_unidades=('cantidad', 'sum'),
        costo_unit_trans_prom=('costo_unit_trans', 'mean')
    ).reset_index()
    ventas['precio_venta_prom'] = np.where(ventas['total_unidades'] > 0, ventas['total_ventas'] / ventas['total_unidades'], 0.0)
    
    df_calc = pd.merge(df_calc, ventas, on='sku', how='left')
    df_calc['precio_venta_prom'] = df_calc['precio_venta_prom'].fillna(0.0)
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
    df_calc['cm_a'] = pd.to_numeric(df_calc['cm_a'], errors='coerce').fillna(0.0)
    df_calc['cm_l'] = pd.to_numeric(df_calc['cm_l'], errors='coerce').fillna(0.0)
    df_calc['cm_p'] = pd.to_numeric(df_calc['cm_p'], errors='coerce').fillna(0.0)
    
    df_calc = pd.merge(df_calc, _df_info, on='sku', how='left')
    df_calc['nombre'] = df_calc['nombre'].fillna('Sin Nombre')
    df_calc['categoria'] = df_calc['categoria'].fillna('GENERAL')
    df_calc['imagen_url'] = df_calc['imagen_url'].fillna('')
    
    # Historial de compras FCO y estado de reposición
    if _df_fco is not None and not _df_fco.empty:
        df_calc = pd.merge(df_calc, _df_fco, on='sku', how='left')
    else:
        df_calc['ultima_fecha_fco'] = pd.NaT
        
    fecha_max_global = df_t['fecha'].max() if not df_t.empty else datetime.datetime.now()
    df_calc['dias_desde_fco'] = (fecha_max_global - df_calc['ultima_fecha_fco']).dt.days
    df_calc['estado_fco'] = np.where(
        df_calc['ultima_fecha_fco'].isna(),
        'Sin histórico de compra',
        df_calc['dias_desde_fco'].fillna(0).astype(int).astype(str) + ' d sin FCO'
    )
    
    # ABC
    df_calc = df_calc.sort_values('total_ventas', ascending=False).reset_index(drop=True)
    v_tot = df_calc['total_ventas'].sum()
    pct_acum = (df_calc['total_ventas'] / v_tot).cumsum() if v_tot > 0 else 0
    df_calc['clase_abc'] = np.select(
        [pct_acum <= 0.50, pct_acum <= 0.80, pct_acum <= 0.95],
        ['AA', 'A', 'B'], default='C'
    )
    
    # XYZ (Semanal)
    df_calc['clase_xyz'] = np.select(
        [df_calc['cv'] <= 0.5, df_calc['cv'] <= 1.0],
        ['X', 'Y'], default='Z'
    )
    df_calc['clase_abc_xyz'] = df_calc['clase_abc'] + '-' + df_calc['clase_xyz']
    
    # XYZ (Mensual)
    df_calc['clase_xyz_mensual'] = np.select(
        [df_calc['cv_mensual'] <= 0.5, df_calc['cv_mensual'] <= 1.0],
        ['X', 'Y'], default='Z'
    )
    df_calc['clase_abc_xyz_mensual'] = df_calc['clase_abc'] + '-' + df_calc['clase_xyz_mensual']
    
    # Nivel de Servicio
    ns_map = {
        ('AA', 'X'): 0.98, ('AA', 'Y'): 0.97, ('AA', 'Z'): 0.95,
        ('A',  'X'): 0.95, ('A',  'Y'): 0.93, ('A',  'Z'): 0.90,
        ('B',  'X'): 0.90, ('B',  'Y'): 0.88, ('B',  'Z'): 0.85,
        ('C',  'X'): 0.85, ('C',  'Y'): 0.80, ('C',  'Z'): 0.75,
    }
    df_calc['nivel_servicio'] = [ns_map.get((a, x), 0.85) for a, x in zip(df_calc['clase_abc'], df_calc['clase_xyz'])]
    
    # Recalcular ROP y SS Gaussiano SEMANAL para Smooth/Erratic con factor_ss
    mask_gauss = df_calc['cuadrante'].isin(['smooth', 'erratic'])
    z_scores = stats.norm.ppf(df_calc.loc[mask_gauss, 'nivel_servicio'])
    df_calc.loc[mask_gauss, 'ss_empirico'] = np.maximum(
        0.0,
        z_scores * df_calc.loc[mask_gauss, 'demanda_semanal_std'] * math.sqrt(lt) * factor_ss
    )
    df_calc.loc[mask_gauss, 'rop'] = df_calc.loc[mask_gauss, 'demanda_esperada_lt'] + df_calc.loc[mask_gauss, 'ss_empirico']
    
    # Recalcular ROP y SS Gaussiano MENSUAL para Smooth/Erratic con factor_ss
    mask_gauss_m = df_calc['cuadrante_mensual'].isin(['smooth', 'erratic'])
    z_scores_m = stats.norm.ppf(df_calc.loc[mask_gauss_m, 'nivel_servicio'])
    df_calc.loc[mask_gauss_m, 'ss_empirico_mensual'] = np.maximum(
        0.0,
        z_scores_m * df_calc.loc[mask_gauss_m, 'demanda_mensual_std'] * math.sqrt(lt_m) * factor_ss
    )
    df_calc.loc[mask_gauss_m, 'rop_mensual'] = df_calc.loc[mask_gauss_m, 'demanda_esperada_lt_mensual'] + df_calc.loc[mask_gauss_m, 'ss_empirico_mensual']
    
    # Umbrales Críticos de Stock (30% ROP)
    df_calc['umbral_rop_30'] = df_calc['rop'] * 0.30
    df_calc['umbral_rop_30_mensual'] = df_calc['rop_mensual'] * 0.30
    
    # ROP y EOQ generales (Semanal)
    df_calc['cbm_unitario'] = df_calc['CBMM'] / df_calc['cantidad_por_caja']
    df_calc['flete_unitario_usd'] = df_calc['cbm_unitario'] * flete
    df_calc['costo_puesto'] = df_calc['costo'] + df_calc['flete_unitario_usd']
    
    h = df_calc['costo_puesto'] * tasa
    d_anual = df_calc['demanda_semanal_prom'] * 52.0
    eoq = np.where(h > 0, np.sqrt(np.maximum(0.0, (2 * d_anual * c_orden) / h)), 0.0)
    eoq = np.nan_to_num(eoq, nan=0.0)
    
    # Decision de pedido SEMANAL
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
    
    # Decisión de pedido MENSUAL
    d_anual_m = df_calc['demanda_mensual_prom'] * 12.0
    eoq_m = np.where(h > 0, np.sqrt((2 * d_anual_m * c_orden) / h), 0.0)
    eoq_m = np.nan_to_num(eoq_m, nan=0.0)
    df_calc['eoq_mensual'] = eoq_m
    df_calc['requiere_pedido_mensual'] = df_calc['stock_total_disponible'] <= df_calc['rop_mensual']
    df_calc['estado_mensual'] = np.where(df_calc['requiere_pedido_mensual'], 'REORDENAR', 'OK')
    df_calc['cajas_sugeridas_mensual'] = np.where(
        df_calc['requiere_pedido_mensual'],
        np.ceil(eoq_m / df_calc['cantidad_por_caja']).astype(int),
        0
    )
    
    return df_calc

df_modelo = ejecutar_motor(df_trans_filtrada, df_art, df_metadata, df_info_prod, df_stock_transito, df_fco_ult, lead_time, flete_cbm, capacidad_cont, tasa_mant, costo_orden, factor_ss=factor_ss)

# ══════════════════════════════════════════════════════════════════════════════
# 4.5 MOTOR SECUNDARIO: AGREGACIÓN MENSUAL (Para Fichas Visuales y Matrices)
# ══════════════════════════════════════════════════════════════════════════════
df_mensual_abc_xyz = df_modelo[[
    'sku', 'nombre', 'categoria', 'clase_abc', 'total_ventas',
    'demanda_mensual_prom', 'cv_mensual', 'cuadrante_mensual',
    'rop_mensual', 'requiere_pedido_mensual', 'clase_xyz_mensual', 'clase_abc_xyz_mensual'
]].copy()
df_mensual_abc_xyz['cv'] = df_mensual_abc_xyz['cv_mensual']
df_mensual_abc_xyz['clase_xyz'] = df_mensual_abc_xyz['clase_xyz_mensual']
df_mensual_abc_xyz['clase_abc_xyz'] = df_mensual_abc_xyz['clase_abc_xyz_mensual']
df_mensual_abc_xyz['requiere_pedido'] = df_mensual_abc_xyz['requiere_pedido_mensual']

# Listas de opciones cacheadas en memoria para agilizar renderizado de selectores
etiquetas_catalogo = (df_modelo['sku'] + " -- " + df_modelo['nombre']).tolist()
todas_categorias_catalogo = sorted(df_modelo['categoria'].dropna().unique().tolist())

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
tab1, tab7, tab3, tab5, tab6, tab2, tab8 = st.tabs([
    "Armado y Simulacion de Contenedor",
    "Generador de Pedido Optimo",
    "Ficha Visual y Comparador",
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
    st.caption(f"Filtra el catálogo por categoría, estado o texto. Tiempo de entrega activo: **{lead_time} semanas**. El volumen CBM, el ROP y el costo FOB se recalculan en tiempo real.")
    
    with st.container():
        r1_col1, r1_col2 = st.columns([2.5, 1.5])
        with r1_col1:
            busqueda_skus = st.multiselect(
                "Buscar producto por Codigo SKU o Descripcion (Autocompletado):",
                options=etiquetas_catalogo,
                placeholder="Escribe codigo o palabra para buscar...",
                key="multiselect_busqueda_sku_t1"
            )
        with r1_col2:
            f_categoria = st.multiselect(
                "Categoria de Producto:",
                options=todas_categorias_catalogo,
                default=[],
                placeholder="Todas las categorias",
                key="multiselect_cat_t1"
            )
        
        r2_col1, r2_col2, r2_col3 = st.columns([1.2, 1.2, 1.2])
        with r2_col1:
            f_estado = st.multiselect("Estado de Stock:", ["REORDENAR", "OK"], default=["REORDENAR"])
        with r2_col2:
            f_abc = st.multiselect("Clasificacion ABC:", ["AA", "A", "B", "C"], default=["AA", "A", "B", "C"])
        with r2_col3:
            f_xyz = st.multiselect("Variabilidad XYZ:", ["X", "Y", "Z"], default=["X", "Y", "Z"])
    
    # Aplicar filtros: si se busca un producto específico, mostrarlo directamente
    if busqueda_skus:
        codigos_buscar = [s.split(" -- ")[0] for s in busqueda_skus]
        mask = df_modelo['sku'].isin(codigos_buscar)
    else:
        mask = (
            df_modelo['estado'].isin(f_estado) &
            df_modelo['clase_abc'].isin(f_abc) &
            df_modelo['clase_xyz'].isin(f_xyz) &
            (~df_modelo['sku'].isin(['MASS3063', 'MASS3065', 'MASS3066']))
        )
        if f_categoria:
            mask = mask & (df_modelo['categoria'].isin(f_categoria))
    
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
        'estado_fco', 'stock_actual', 'stock_transito', 'rop', 'rop_mensual', 'demanda_semanal_prom', 'demanda_mensual_prom', 'pedir_cajas',
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
            "clase_abc_xyz": st.column_config.TextColumn("Segmento", width="small"),
            "estado_fco": st.column_config.TextColumn("Última Compra", width="medium", help="Fecha o días transcurridos desde la última FCO"),
            "pedir_cajas": st.column_config.NumberColumn("Cajas a Pedir", min_value=0, step=1),
            "stock_actual": st.column_config.NumberColumn("Stock", format="%.0f"),
            "stock_transito": st.column_config.NumberColumn("En Transito", format="%.0f", help="Stock en contenedores Julio/Egipto"),
            "rop": st.column_config.NumberColumn("ROP Semanal", format="%.1f", help=f"Punto de reorden semanal (LT={lead_time} sem)"),
            "rop_mensual": st.column_config.NumberColumn("ROP Mensual", format="%.1f", help="Punto de reorden mensual (LT=3.5 meses)"),
            "demanda_semanal_prom": st.column_config.NumberColumn("Demanda/Sem", format="%.1f"),
            "demanda_mensual_prom": st.column_config.NumberColumn("Demanda/Mes", format="%.1f"),
            "CBMM": st.column_config.NumberColumn("CBM/Caja", format="%.3f"),
            "costo": st.column_config.NumberColumn("Costo FOB ($)", format="$%.2f"),
            "costo_puesto": st.column_config.NumberColumn("Costo DDP ($)", format="$%.2f", help="Costo FOB + Flete unitario"),
        },
        disabled=['imagen_url', 'sku', 'nombre', 'categoria', 'clase_abc_xyz', 'estado_fco', 'stock_actual', 'stock_transito', 'rop', 'rop_mensual', 'demanda_semanal_prom', 'demanda_mensual_prom', 'cantidad_por_caja', 'CBMM', 'costo', 'costo_puesto'],
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
    if 'gsheet_success_msg' in st.session_state:
        st.success(st.session_state.pop('gsheet_success_msg'))
        
    col_btn_csv, col_btn_gsheet = st.columns([1, 1])
    with col_btn_csv:
        csv_pedido = seleccionados[['sku', 'nombre', 'categoria', 'pedir_cajas', 'unidades_total', 'cbm_total', 'costo', 'inversion_fob', 'costo_puesto', 'costo_total_ddp']].to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Descargar Orden de Compra (CSV)",
            data=csv_pedido,
            file_name="orden_compra_masshopping_contenedor.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_btn_gsheet:
        if st.button("🚢 Cargar Seleccionados a Google Sheets", type="primary", use_container_width=True, key="btn_gsheet_tab1"):
            if seleccionados.empty:
                st.warning("⚠️ Debes marcar al menos un producto con cajas a pedir (> 0) en la tabla para cargarlo al contenedor.")
            else:
                modal_asignar_contenedor_gsheet(seleccionados, flete_cbm, df_modelo)

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
    
    lista_etiquetas = list(etiquetas_catalogo)
    
    # Persistir la seleccion del producto a traves de cambios de filtro
    if 'multiselect_comparador_tab3' not in st.session_state:
        import random
        skus_aa_a = df_modelo[df_modelo['clase_abc'].isin(['AA', 'A'])]['sku'].tolist()
        if skus_aa_a:
            random_sku = random.choice(skus_aa_a)
            match_etiqs = [e for e in lista_etiquetas if e.startswith(random_sku + " -- ")]
            st.session_state['multiselect_comparador_tab3'] = [match_etiqs[0]] if match_etiqs else [lista_etiquetas[0]]
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
                estado_m_html = f'<span class="badge-status-reorden">REORDENAR</span>' if item['estado_mensual'] == 'REORDENAR' else f'<span class="badge-status-ok">OK</span>'
                
                transit_val = item.get('stock_transito', 0)
                
                st.markdown(f"""
                <div class="kpi-grid" style="grid-template-columns: repeat(6, 1fr);">
                    <div class="kpi-card">
                        <div class="kpi-title">Stock Actual</div>
                        <div class="kpi-number">{item['stock_actual']:,.0f} unidades</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-title">En Tránsito</div>
                        <div class="kpi-number">{transit_val:,.0f} unidades</div>
                    </div>
                    <div class="kpi-card" style="border-top: 3px solid #E65100;">
                        <div class="kpi-title" style="color:#C62828;">Umbral Crítico (30%)</div>
                        <div class="kpi-number" style="color:#C62828;">{item['umbral_rop_30_mensual']:,.1f} unidades</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-title">ROP Semanal (15 sem)</div>
                        <div class="kpi-number">{item['rop']:,.1f} unidades</div>
                    </div>
                    <div class="kpi-card" style="border-top: 3px solid #1E88E5;">
                        <div class="kpi-title" style="color:#1565C0;">ROP Mensual (3.5 m)</div>
                        <div class="kpi-number" style="color:#1565C0;">{item['rop_mensual']:,.1f} unidades</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-title">Estado (Sem / Mes)</div>
                        <div style="margin-top:2px; font-size:11px;">{estado_html} / {estado_m_html}</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-title">Demanda Semanal</div>
                        <div class="kpi-number">{item['demanda_semanal_prom']:,.1f} unidades</div>
                    </div>
                    <div class="kpi-card" style="border-top: 3px solid #1E88E5;">
                        <div class="kpi-title" style="color:#1565C0;">Demanda Mensual</div>
                        <div class="kpi-number" style="color:#1565C0;">{item['demanda_mensual_prom']:,.1f} unidades</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-title">Última Compra (FCO)</div>
                        <div class="kpi-number" style="font-size:12px; font-weight:700; color:#141E32;">{item.get('estado_fco', 'N/A')}</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-title">Cuadrante Sem / Mes</div>
                        <div class="kpi-number" style="font-size:13px;">{str(item['cuadrante']).upper()} / {str(item['cuadrante_mensual']).upper()}</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-title">Costo FOB / DDP</div>
                        <div class="kpi-number" style="font-size:13px;">${item['costo']:,.2f} / ${item['costo_puesto']:,.2f}</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-title">Nivel de Servicio</div>
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
                
        col_rango, col_chk1, col_chk2, col_chk3 = st.columns([2, 1, 1, 1.2])
        with col_rango:
            rango_local = st.date_input(
                "Rango de Fechas Específicas (Gráfico)",
                value=(fecha_min_global, fecha_max_global),
                key="rango_grafico_tab3"
            )
            
        with col_chk1:
            mostrar_tendencia = st.checkbox("Mostrar Tendencia", value=False)
        with col_chk2:
            mostrar_p2p = st.checkbox("Mostrar Variación USDT", value=False)
        with col_chk3:
            mostrar_reposicion = st.checkbox("Mostrar Reposición (FCO - DEC)", value=True, help="Muestra gráficos de compras netas efectivas (FCO - DEC)")
            
        # Apply local date filter to df_trans (full history)
        df_plot_trans = df_trans
        df_plot_repo = df_reposicion
        if isinstance(rango_local, tuple):
            if len(rango_local) == 2:
                start_loc, end_loc = rango_local
                df_plot_trans = df_trans[
                    (df_trans['fecha'].dt.date >= start_loc) &
                    (df_trans['fecha'].dt.date <= end_loc)
                ]
                if not df_reposicion.empty:
                    df_plot_repo = df_reposicion[
                        (df_reposicion['fecha'].dt.date >= start_loc) &
                        (df_reposicion['fecha'].dt.date <= end_loc)
                    ]
            elif len(rango_local) == 1:
                start_loc = rango_local[0]
                df_plot_trans = df_trans[
                    df_trans['fecha'].dt.date >= start_loc
                ]
                if not df_reposicion.empty:
                    df_plot_repo = df_reposicion[
                        df_reposicion['fecha'].dt.date >= start_loc
                    ]
        
        from plotly.subplots import make_subplots
        paleta_colores = ['#5AA06E', '#141E32', '#E65100', '#00897B', '#7B1FA2', '#1E88E5', '#D81B60', '#FDD835']
        paleta_azul = ['#1E88E5', '#0D47A1', '#42A5F5', '#1565C0', '#29B6F6', '#0288D1', '#3949AB', '#00ACC1']
        
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
                st.metric("Total Costo", f"${total_usd:,.2f}")
        else:
            st.info("No hay datos de venta en el rango seleccionado para los productos elegidos.")

        # ── GRÁFICO DE REPOSICIÓN NETA SEMANAL (FCO - DEC) ──
        if mostrar_reposicion and len(skus_codigos) > 0:
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("Histórico de Reposición Neta Semanal (FCO - DEC)")
            st.caption("Compras netas recibidas en inventario (Facturas de Compra FCO menos Devoluciones DEC) agrupadas por semana.")
            
            fig_repo_w = go.Figure()
            for idx, sku_code in enumerate(skus_codigos):
                df_repo_sku = df_plot_repo[df_plot_repo['sku'] == sku_code].copy()
                if not df_repo_sku.empty:
                    s_repo_w = df_repo_sku.groupby(pd.Grouper(key='fecha', freq='W-MON'))['cantidad'].sum().reset_index().sort_values('fecha')
                else:
                    s_repo_w = pd.DataFrame({'fecha': [], 'cantidad': []})
                    
                nombre_label = df_modelo[df_modelo['sku'] == sku_code]['nombre'].values
                nombre_label = nombre_label[0] if len(nombre_label) > 0 else sku_code
                if len(nombre_label) > 30:
                    nombre_label = nombre_label[:30] + '...'
                legend_name = f"{sku_code} ({nombre_label})"
                color_azul = paleta_azul[idx % len(paleta_azul)]
                
                fig_repo_w.add_trace(go.Scatter(
                    x=s_repo_w['fecha'],
                    y=s_repo_w['cantidad'],
                    mode='lines+markers',
                    name=legend_name,
                    line=dict(width=2.5, color=color_azul),
                    marker=dict(size=6, color=color_azul),
                    hovertemplate="<b>" + sku_code + " (Reposición Neta)</b><br>Semana: %{x|%d %b %Y}<br>FCO - DEC: <b>%{y:,.0f} uds</b><extra></extra>"
                ))
                
            fig_repo_w.update_layout(
                height=420,
                margin=dict(l=20, r=20, t=30, b=30),
                hovermode="x unified",
                xaxis=dict(title="Fecha (Semana)", tickformat="%b %Y", showgrid=True, gridcolor="#EBF4EE"),
                yaxis=dict(title="Unidades Repuestas (FCO - DEC) / Semana", showgrid=True, gridcolor="#EBF4EE"),
                legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF"
            )
            st.plotly_chart(fig_repo_w, use_container_width=True)
            
            # Totales agregados de reposición
            df_plot_repo_skus = df_plot_repo[df_plot_repo['sku'].isin(skus_codigos)]
            if not df_plot_repo_skus.empty:
                total_repo_uds = df_plot_repo_skus['cantidad'].sum()
                df_plot_repo_usd = pd.merge(df_plot_repo_skus, df_modelo[['sku', 'costo']], on='sku', how='left')
                df_plot_repo_usd['costo'] = df_plot_repo_usd['costo'].fillna(0)
                total_repo_fob = (df_plot_repo_usd['cantidad'] * df_plot_repo_usd['costo']).sum()
                
                r_col1, r_col2 = st.columns(2)
                with r_col1:
                    st.metric("Total Unidades Repuestas (FCO - DEC)", f"{total_repo_uds:,.0f}")
                with r_col2:
                    st.metric("Inversión Repuesta Estimada (FOB)", f"${total_repo_fob:,.2f}")

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
                
                # Obtener métricas calculadas completas de df_modelo
                m_row = df_modelo[df_modelo['sku'] == sku_code]
                if not m_row.empty:
                    mr = m_row.iloc[0]
                    cuad_w_str = str(mr['cuadrante']).upper()
                    adi_w_val = f"{mr['adi']:.2f}"
                    cv2_w_val = f"{(mr['cv']**2):.2f}" if not np.isnan(mr['cv']) else 'N/A'
                    dem_w_val = f"{mr['demanda_semanal_prom']:.1f}"
                    ss_w_val = f"{mr['ss_empirico']:.1f}"
                    rop_w_val = f"{mr['rop']:.1f}"
                    cajas_w_val = f"{mr['cajas_sugeridas']:,.0f}"
                    est_w_val = mr['estado']
                    
                    cuad_m_str = str(mr['cuadrante_mensual']).upper()
                    adi_m_val = f"{mr['adi_mensual']:.2f}"
                    cv2_m_val = f"{(mr['cv_mensual']**2):.2f}" if not np.isnan(mr['cv_mensual']) else 'N/A'
                    dem_m_val = f"{mr['demanda_mensual_prom']:.1f}"
                    ss_m_val = f"{mr['ss_empirico_mensual']:.1f}"
                    rop_m_val = f"{mr['rop_mensual']:.1f}"
                    cajas_m_val = f"{mr['cajas_sugeridas_mensual']:,.0f}"
                    est_m_val = mr['estado_mensual']
                else:
                    cuad_w_str, adi_w_val, cv2_w_val, dem_w_val, ss_w_val, rop_w_val, cajas_w_val, est_w_val = ('-', '-', '-', '-', '-', '-', '-', '-')
                    cuad_m_str, adi_m_val, cv2_m_val, dem_m_val, ss_m_val, rop_m_val, cajas_m_val, est_m_val = ('-', '-', '-', '-', '-', '-', '-', '-')
                
                resultados_mensuales.append({
                    'SKU': sku_code,
                    'Cuadrante (SEM)': cuad_w_str,
                    'ADI (Sem)': adi_w_val,
                    'CV² (Sem)': cv2_w_val,
                    'Demanda/Sem': dem_w_val,
                    'SS (Sem)': ss_w_val,
                    'ROP Sem (15 sem)': rop_w_val,
                    'Cajas (Sem)': cajas_w_val,
                    'Estado (Sem)': est_w_val,
                    '|': '║',
                    'Cuadrante (MES)': cuad_m_str,
                    'ADI (Mes)': adi_m_val,
                    'CV² (Mes)': cv2_m_val,
                    'Demanda/Mes': dem_m_val,
                    'SS (Mes)': ss_m_val,
                    'ROP Mes (3.5 m)': rop_m_val,
                    'Cajas (Mes)': cajas_m_val,
                    'Estado (Mes)': est_m_val,
                })
            
            fig_m.update_layout(
                height=400, margin=dict(l=20, r=20, t=30, b=30),
                hovermode="x unified",
                xaxis=dict(title="Mes", tickformat="%b %Y", showgrid=True, gridcolor="#EBF4EE"),
                yaxis=dict(title="Unidades Vendidas / Mes", showgrid=True, gridcolor="#EBF4EE"),
                plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF"
            )
            
            st.plotly_chart(fig_m, use_container_width=True)
            
            # ── GRÁFICO DE REPOSICIÓN NETA MENSUAL (FCO - DEC) ──
            if mostrar_reposicion:
                st.markdown("#### Histórico de Reposición Neta Mensual (FCO - DEC)")
                st.caption("Compras netas recibidas en inventario (FCO - DEC) agrupadas mensualmente.")
                
                fig_repo_m = go.Figure()
                for idx, sku_code in enumerate(skus_codigos):
                    df_repo_sku = df_plot_repo[df_plot_repo['sku'] == sku_code].copy()
                    if not df_repo_sku.empty:
                        s_repo_m = df_repo_sku.groupby(pd.Grouper(key='fecha', freq='MS'))['cantidad'].sum().reset_index().sort_values('fecha')
                    else:
                        s_repo_m = pd.DataFrame({'fecha': [], 'cantidad': []})
                        
                    nombre_label = df_modelo[df_modelo['sku'] == sku_code]['nombre'].values
                    nombre_label = nombre_label[0] if len(nombre_label) > 0 else sku_code
                    if len(nombre_label) > 30:
                        nombre_label = nombre_label[:30] + '...'
                    legend_name = f"{sku_code} ({nombre_label})"
                    color_azul = paleta_azul[idx % len(paleta_azul)]
                    
                    fig_repo_m.add_trace(go.Scatter(
                        x=s_repo_m['fecha'],
                        y=s_repo_m['cantidad'],
                        mode='lines+markers',
                        name=legend_name,
                        line=dict(width=2.5, color=color_azul),
                        marker=dict(size=7, color=color_azul),
                        hovertemplate="<b>" + sku_code + " (Reposición Neta)</b><br>Mes: %{x|%b %Y}<br>FCO - DEC: <b>%{y:,.0f} uds</b><extra></extra>"
                    ))
                    
                fig_repo_m.update_layout(
                    height=380,
                    margin=dict(l=20, r=20, t=30, b=30),
                    hovermode="x unified",
                    xaxis=dict(title="Mes", tickformat="%b %Y", showgrid=True, gridcolor="#EBF4EE"),
                    yaxis=dict(title="Unidades Repuestas (FCO - DEC) / Mes", showgrid=True, gridcolor="#EBF4EE"),
                    legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
                    plot_bgcolor="#FFFFFF",
                    paper_bgcolor="#FFFFFF"
                )
                st.plotly_chart(fig_repo_m, use_container_width=True)
            
            # Tabla comparativa
            st.markdown("#### Comparativa Integral de Estadísticas y Parámetros: Semanal (LT=15 sem) vs Mensual (LT=3.5 meses)")
            st.dataframe(pd.DataFrame(resultados_mensuales), use_container_width=True)



# ══════════════════════════════════════════════════════════════════════════════
# TAB 5: ANALISIS VISUAL ABC
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("Grafico de Pareto - Clasificacion ABC")
    st.caption("Distribucion de ventas acumuladas por producto (Regla 80/20)")
    
    # Sort by total_ventas descending (excluyendo producto temporal MASS3063)
    df_abc = df_modelo[df_modelo['sku'] != 'MASS3063'].sort_values('total_ventas', ascending=False).reset_index(drop=True)
    df_abc['pct_acum'] = (df_abc['total_ventas'].cumsum() / df_abc['total_ventas'].sum()) * 100
    df_abc['sku_num'] = np.arange(1, len(df_abc) + 1)
    
    color_map = {'AA': '#141E32', 'A': '#5AA06E', 'B': '#FDD835', 'C': '#E65100'}
    
    fig_abc = make_subplots(specs=[[{"secondary_y": True}]])
    df_abc_chart = df_abc.head(100)
    
    for clase in ['AA', 'A', 'B', 'C']:
        mask_clase = df_abc_chart['clase_abc'] == clase
        if mask_clase.any():
            fig_abc.add_trace(go.Bar(
                x=df_abc_chart[mask_clase]['sku'],
                y=df_abc_chart[mask_clase]['total_ventas'],
                name=f"Clase {clase}",
                marker_color=color_map.get(clase),
                hovertemplate="<b>%{x}</b><br>Clase: " + clase + "<br>Ventas Totales: $%{y:,.2f}<extra></extra>"
            ), secondary_y=False)
            
    fig_abc.add_trace(go.Scatter(
        x=df_abc_chart['sku'],
        y=df_abc_chart['pct_acum'],
        mode='lines',
        name='% Acumulado',
        line=dict(color='#E65100', width=3),
        hovertemplate="<b>%{x}</b><br>% Acumulado: %{y:.1f}%<extra></extra>"
    ), secondary_y=True)
    
    fig_abc.update_layout(
        height=500,
        title="Pareto ABC por Ingresos (Top 100 SKUs)",
        xaxis=dict(showticklabels=False, title="Productos ordenados por Ventas (Top 100)", showgrid=False),
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
        mask_clase_m = df_abc_chart['clase_abc'] == clase
        if mask_clase_m.any():
            fig_abc_m.add_trace(go.Bar(
                x=df_abc_chart[mask_clase_m]['sku'],
                y=df_abc_chart[mask_clase_m]['total_ventas'],
                name=f"Clase {clase} (Mensual)",
                marker_color=color_map.get(clase),
                hovertemplate="<b>%{x}</b><br>Clase: " + clase + "<br>Ventas Totales: $%{y:,.2f}<extra></extra>"
            ), secondary_y=False)
            
    fig_abc_m.add_trace(go.Scatter(
        x=df_abc_chart['sku'],
        y=df_abc_chart['pct_acum'],
        mode='lines',
        name='% Acumulado',
        line=dict(color='#E65100', width=3),
        hovertemplate="<b>%{x}</b><br>% Acumulado: %{y:.1f}%<extra></extra>"
    ), secondary_y=True)
    
    fig_abc_m.update_layout(
        height=500,
        title="Pareto ABC por Ingresos (Perspectiva Mensual - Top 100)",
        xaxis=dict(showticklabels=False, title="Productos ordenados por Ventas (Top 100)", showgrid=False),
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
    st.info("Este generador selecciona productos con demanda activa que cumplen dos condiciones de calificación estrictas: 1) Sin órdenes de compra (FCO) en los últimos 60 días (o sin compras previas registradas); 2) Stock actual crítico (≤ 30% del Punto de Reorden ROP).")
    
    # ── 1. FILTROS Y CONFIGURACIÓN DEL PEDIDO ÓPTIMO ──
    with st.container():
        r1_col1, r1_col2 = st.columns([2.5, 1.5])
        with r1_col1:
            criterio_rop_opt = st.radio(
                "Modelo de Punto de Reorden (ROP):",
                [f"📅 ROP Semanal (LT = {lead_time} sem)", f"🗓️ ROP Mensual (LT = {round(float(lead_time) / 4, 2)} meses)"],
                index=1,
                horizontal=True,
                key="radio_criterio_rop_opt"
            )
        with r1_col2:
            todas_cats_opt = sorted(df_modelo['categoria'].unique().tolist())
            f_cat_opt = st.multiselect(
                "Categoria de Producto:",
                options=todas_cats_opt,
                default=[],
                placeholder="Todas las categorias",
                key="multiselect_cat_opt"
            )
            
        r2_col1, r2_col2, r2_col3 = st.columns([2.0, 1.0, 1.0])
        with r2_col1:
            busqueda_skus_opt = st.multiselect(
                "Buscar producto por Codigo SKU o Descripcion (Autocompletado):",
                options=etiquetas_catalogo,
                placeholder="Escribe codigo o palabra para buscar...",
                key="multiselect_busqueda_sku_opt"
            )
        with r2_col2:
            f_abc_opt = st.multiselect("Clasificacion ABC:", ["AA", "A", "B", "C"], default=["AA", "A", "B", "C"], key="multiselect_abc_opt")
        with r2_col3:
            f_xyz_opt = st.multiselect("Variabilidad XYZ:", ["X", "Y", "Z"], default=["X", "Y", "Z"], key="multiselect_xyz_opt")

    usar_mensual_opt = "Mensual" in criterio_rop_opt
    rop_eval_col = 'rop_mensual' if usar_mensual_opt else 'rop'
    umbral_eval_col = 'umbral_rop_30_mensual' if usar_mensual_opt else 'umbral_rop_30'
    cajas_eval_col = 'cajas_sugeridas_mensual' if usar_mensual_opt else 'cajas_sugeridas'
    
    # Exclusiones intencionales
    skus_excluidos_intencionales = ['MASS3063', 'MASS3065', 'MASS3066', 'MASS0722']
    
    # ── FILTRADO VECTORIZADO EN 1 SOLO PASO ULTRA RÁPIDO ──
    if busqueda_skus_opt:
        codigos_opt_buscar = [s.split(" -- ")[0] for s in busqueda_skus_opt]
        mask_opt = df_modelo['sku'].isin(codigos_opt_buscar)
    else:
        mask_opt = (
            ((df_modelo['dias_desde_fco'].isna()) | (df_modelo['dias_desde_fco'] > 60)) &
            (df_modelo['stock_actual'] <= df_modelo[umbral_eval_col]) &
            (df_modelo[rop_eval_col] > 0) &
            (df_modelo['stock_transito'] == 0) &
            (df_modelo['total_unidades'] > 0) &
            (~df_modelo['sku'].isin(skus_excluidos_intencionales)) &
            (df_modelo['clase_abc'].isin(f_abc_opt)) &
            (df_modelo['clase_xyz'].isin(f_xyz_opt))
        )
        if f_cat_opt:
            mask_opt = mask_opt & (df_modelo['categoria'].isin(f_cat_opt))
            
    df_optimo_filtrado = df_modelo[mask_opt]
    
    # Ordenar únicamente el subconjunto filtrado para no sobrecargar la CPU
    if not busqueda_skus_opt and len(df_optimo_filtrado) > 100:
        df_optimo_vista = df_optimo_filtrado.sort_values(by=['stock_actual', rop_eval_col], ascending=[True, False]).head(100).copy()
    else:
        df_optimo_vista = df_optimo_filtrado.sort_values(by=['stock_actual', rop_eval_col], ascending=[True, False]).copy()
        
    df_optimo_vista['pedir_cajas'] = df_optimo_vista[cajas_eval_col]
    
    if df_optimo_vista.empty:
        st.success("No hay productos que cumplan los criterios seleccionados en este momento.")
    else:
        st.caption(f"Mostrando **{len(df_optimo_vista)}** productos críticos calificados.")
        
        col_chk_all, col_btn_ficha = st.columns([3, 1.2])
        with col_chk_all:
            seleccionar_todos_opt = st.checkbox(
                "Marcar todos los productos mostrados para incluirlos en el pedido",
                key="chk_seleccionar_todos_opt"
            )
            df_optimo_vista['incluir_en_pedido'] = bool(seleccionar_todos_opt)
        with col_btn_ficha:
            def update_tab3_from_opt(etiquetas):
                st.session_state['multiselect_comparador_tab3'] = etiquetas
                
            etiquetas_opt_vista = (df_optimo_vista['sku'] + " -- " + df_optimo_vista['nombre']).tolist()
            st.button("📊 Ver en Ficha Visual", on_click=update_tab3_from_opt, args=(etiquetas_opt_vista,), key="btn_ver_ficha_opt")

        # ── 4. TABLA INTERACTIVA (DATA EDITOR) ──
        cols_editor_opt = [
            'incluir_en_pedido', 'imagen_url', 'sku', 'nombre', 'categoria', 'clase_abc_xyz',
            'estado_fco', 'stock_actual', 'stock_transito', 'demanda_semanal_prom', 'demanda_mensual_prom',
            'media_movil_4sem', 'tendencia', 'rop', 'rop_mensual', umbral_eval_col, 'pedir_cajas',
            'cantidad_por_caja', 'CBMM', 'costo', 'costo_puesto'
        ]
        
        rop_label_sem = f"ROP Sem ({lead_time}s)"
        rop_label_mes = "ROP Mes (3.5m)"
        
        df_optimo_editado = st.data_editor(
            df_optimo_vista[cols_editor_opt],
            column_config={
                "incluir_en_pedido": st.column_config.CheckboxColumn("Incluir", help="Marcar para sumar al contenedor"),
                "imagen_url": st.column_config.ImageColumn("Foto", help="Foto oficial del producto"),
                "sku": st.column_config.TextColumn("Código SKU", width="small"),
                "nombre": st.column_config.TextColumn("Nombre del Producto", width="large"),
                "categoria": st.column_config.TextColumn("Categoría", width="medium"),
                "clase_abc_xyz": st.column_config.TextColumn("Segmento", width="small"),
                "estado_fco": st.column_config.TextColumn("Última Compra", width="medium", help="Fecha o días transcurridos desde la última FCO"),
                "pedir_cajas": st.column_config.NumberColumn("Cajas Sugeridas", min_value=0, step=1, help="Editable: Cajas a ordenar"),
                "stock_actual": st.column_config.NumberColumn("Stock", format="%.0f"),
                "stock_transito": st.column_config.NumberColumn("En Tránsito", format="%.0f"),
                "demanda_semanal_prom": st.column_config.NumberColumn("Demanda/Sem", format="%.1f"),
                "demanda_mensual_prom": st.column_config.NumberColumn("Demanda/Mes", format="%.1f"),
                "media_movil_4sem": st.column_config.NumberColumn("Media Móvil (4s)", format="%.1f", help="Promedio de unidades vendidas en las últimas 4 semanas"),
                "tendencia": st.column_config.TextColumn("Tendencia (4s)", help="Variación porcentual reciente (últimas 4 sem vs 4 sem previas)"),
                "rop": st.column_config.NumberColumn(rop_label_sem, format="%.1f"),
                "rop_mensual": st.column_config.NumberColumn(rop_label_mes, format="%.1f"),
                umbral_eval_col: st.column_config.NumberColumn("Umbral (30% ROP)", format="%.1f"),
                "CBMM": st.column_config.NumberColumn("CBM/Caja", format="%.3f"),
                "costo": st.column_config.NumberColumn("Costo FOB ($)", format="$%.2f"),
                "costo_puesto": st.column_config.NumberColumn("Costo DDP ($)", format="$%.2f", help="Costo FOB + Flete unitario estimado"),
            },
            disabled=[
                'imagen_url', 'sku', 'nombre', 'categoria', 'clase_abc_xyz', 'estado_fco',
                'stock_actual', 'stock_transito', 'demanda_semanal_prom', 'demanda_mensual_prom',
                'media_movil_4sem', 'tendencia', 'rop', 'rop_mensual', umbral_eval_col,
                'cantidad_por_caja', 'CBMM', 'costo', 'costo_puesto'
            ],
            use_container_width=True,
            height=420,
            key="editor_pedido_optimo_tab7"
        )
        
        # ── 5. CÁLCULO DE CONTENEDOR EN TIEMPO REAL PARA SELECCIONADOS ──
        seleccionados_opt = df_optimo_editado[df_optimo_editado['incluir_en_pedido'] & (df_optimo_editado['pedir_cajas'] > 0)].copy()
        seleccionados_opt['cbm_total'] = seleccionados_opt['pedir_cajas'] * seleccionados_opt['CBMM']
        seleccionados_opt['unidades_total'] = seleccionados_opt['pedir_cajas'] * seleccionados_opt['cantidad_por_caja']
        seleccionados_opt['inversion_fob'] = seleccionados_opt['unidades_total'] * seleccionados_opt['costo']
        seleccionados_opt['costo_total_ddp'] = seleccionados_opt['unidades_total'] * seleccionados_opt['costo_puesto']
        
        cbm_opt_acum = seleccionados_opt['cbm_total'].sum()
        fob_opt_acum = seleccionados_opt['inversion_fob'].sum()
        ddp_opt_acum = seleccionados_opt['costo_total_ddp'].sum()
        cajas_opt_acum = seleccionados_opt['pedir_cajas'].sum()
        uds_opt_acum = seleccionados_opt['unidades_total'].sum()
        pct_llenado_opt = min(100.0, (cbm_opt_acum / capacidad_cont) * 100) if capacidad_cont > 0 else 0
        contenedores_totales_opt = cbm_opt_acum / capacidad_cont if capacidad_cont > 0 else 0
        
        st.markdown("<br>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Volumen Total CBM</div>
                <div class="metric-value">{cbm_opt_acum:,.2f} m³</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Inversión FOB / DDP</div>
                <div class="metric-value">${fob_opt_acum:,.2f}</div>
                <div class="metric-delta">DDP Est.: ${ddp_opt_acum:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Empaque Total</div>
                <div class="metric-value">{cajas_opt_acum:,} cajas</div>
                <div class="metric-delta">{uds_opt_acum:,} unidades ({len(seleccionados_opt)} SKUs)</div>
            </div>
            """, unsafe_allow_html=True)
        with m4:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">Ocupación de Contenedor</div>
                <div class="metric-value">{contenedores_totales_opt:.2f} cont.</div>
                <div class="metric-delta">{pct_llenado_opt:.1f}% del 1er contenedor</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.progress(pct_llenado_opt / 100.0)
        
        if cbm_opt_acum > capacidad_cont:
            st.warning(f"El volumen de productos seleccionados supera la capacidad de 1 contenedor ({capacidad_cont} CBM). Se requieren **{math.ceil(contenedores_totales_opt)} contenedores**.")
        elif pct_llenado_opt >= 90:
            st.success(f"Contenedor optimizado. Nivel de ocupación: **{pct_llenado_opt:.1f}%**.")
            
        # ── 6. BOTONES DE DESCARGA Y ENVÍO A GOOGLE SHEETS ──
        col_d1, col_d2 = st.columns([1, 1])
        with col_d1:
            # Si hay seleccionados, exporta los seleccionados; si no, exporta la vista completa
            df_export_opt = seleccionados_opt if not seleccionados_opt.empty else df_optimo_vista
            cols_csv_opt = ['sku', 'nombre', 'categoria', 'pedir_cajas', 'costo']
            csv_optimo = df_export_opt[[c for c in cols_csv_opt if c in df_export_opt.columns]].to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label=f"📥 Descargar Pedido Óptimo ({len(df_export_opt)} productos) [CSV]",
                data=csv_optimo,
                file_name="pedido_optimo_masshopping.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_d2:
            if st.button("🚢 Cargar Seleccionados a Google Sheets", type="primary", use_container_width=True, key="btn_gsheet_optimo"):
                if seleccionados_opt.empty:
                    st.warning("⚠️ Debes marcar con el checkbox al menos un producto con cajas (> 0) en la tabla para cargarlo al contenedor.")
                else:
                    modal_asignar_contenedor_gsheet(seleccionados_opt, flete_cbm, df_modelo)

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
            file_name="reporte_sobre_stock.csv",
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

"""
Módulo de Gestión de Inventarios y Clasificación ABC-XYZ
Motor vectorizado de alto rendimiento para catálogos masivos (3000+ SKUs)
"""

import math
import numpy as np
import pandas as pd
from scipy import stats


def procesar_demanda_semanal(df_trans: pd.DataFrame, col_sku: str = 'sku', col_fecha: str = 'fecha', col_cant: str = 'cantidad') -> pd.DataFrame:
    """
    Construye la matriz semanal de demanda (SKU x Semana) de forma vectorizada.
    """
    df_semanal = df_trans.groupby([col_sku, pd.Grouper(key=col_fecha, freq='W-MON')])[col_cant].sum().unstack(fill_value=0.0)
    return df_semanal


def calcular_clasificacion_abc(df_sku: pd.DataFrame, col_ventas: str = 'total_ventas') -> pd.Series:
    """
    Clasificación ABC por valor acumulado de ventas (Pareto):
    - AA: <= 50%
    - A:  50% - 80%
    - B:  80% - 95%
    - C:  > 95%
    """
    ventas_totales = df_sku[col_ventas].sum()
    pct_ventas = df_sku[col_ventas] / ventas_totales
    pct_acum = pct_ventas.cumsum()

    clase_abc = np.select(
        [
            pct_acum <= 0.50,
            pct_acum <= 0.80,
            pct_acum <= 0.95,
            pct_acum > 0.95,
        ],
        ['AA', 'A', 'B', 'C'],
        default='C'
    )
    return pd.Series(clase_abc, index=df_sku.index, name='clase_abc')


def calcular_clasificacion_xyz(df_sku: pd.DataFrame, col_cv: str = 'cv') -> pd.Series:
    """
    Clasificación XYZ por coeficiente de variación (CV = std / media):
    - X: CV <= 0.5 (Demanda estable)
    - Y: 0.5 < CV <= 1.0 (Demanda variable)
    - Z: CV > 1.0 (Demanda errática / intermitente)
    """
    clase_xyz = np.select(
        [
            df_sku[col_cv] <= 0.5,
            df_sku[col_cv] <= 1.0,
            df_sku[col_cv] > 1.0,
        ],
        ['X', 'Y', 'Z'],
        default='Z'
    )
    return pd.Series(clase_xyz, index=df_sku.index, name='clase_xyz')


def asignar_nivel_servicio(df_sku: pd.DataFrame, col_abc: str = 'clase_abc', col_xyz: str = 'clase_xyz') -> pd.Series:
    """
    Asigna el nivel de servicio dinámico según la celda en la matriz ABC-XYZ (12 celdas).
    """
    tabla_servicio = {
        ('AA', 'X'): 0.98, ('AA', 'Y'): 0.97, ('AA', 'Z'): 0.95,
        ('A',  'X'): 0.95, ('A',  'Y'): 0.93, ('A',  'Z'): 0.90,
        ('B',  'X'): 0.90, ('B',  'Y'): 0.88, ('B',  'Z'): 0.85,
        ('C',  'X'): 0.85, ('C',  'Y'): 0.80, ('C',  'Z'): 0.75,
    }
    servicios = [
        tabla_servicio.get((a, x), 0.85)
        for a, x in zip(df_sku[col_abc], df_sku[col_xyz])
    ]
    return pd.Series(servicios, index=df_sku.index, name='nivel_servicio')


def calcular_modelo_inventario_vectorizado(
    df_sku: pd.DataFrame,
    lead_time_semanas: int = 15,
    flete_cbm: float = 85.0,
    capacidad_contenedor_cbm: float = 68.0,
    tasa_mantenimiento: float = 0.15,
    costo_orden_admin: float = 50.0,
) -> pd.DataFrame:
    """
    Ejecuta el cálculo completo de inventario (ROP, EOQ, Reorden, CBM, Contenedores)
    de forma 100% vectorizada sobre todo el DataFrame.
    """
    df = df_sku.copy()

    # 1. Costos y Flete
    df['cbm_unitario'] = df['CBMM'] / df['cantidad_por_caja']
    df['costo_flete_unitario'] = df['cbm_unitario'] * flete_cbm
    df['costo_puesto'] = df['costo_final'] + df['costo_flete_unitario']

    # 2. Demandas
    df['demanda_anual'] = df['demanda_semanal_prom'] * 52.0
    df['demanda_esperada_lt'] = df['demanda_semanal_prom'] * lead_time_semanas

    # 3. Punto de Reorden (ROP) y Stock de Seguridad
    z_scores = stats.norm.ppf(df['nivel_servicio'])
    std_lt = df['demanda_semanal_std'] * math.sqrt(lead_time_semanas)
    df['rop'] = df['demanda_esperada_lt'] + z_scores * std_lt
    df['stock_seguridad'] = np.maximum(0.0, df['rop'] - df['demanda_esperada_lt'])

    # 4. Lote Económico de Compra (EOQ) redondeado a cajas
    h = df['costo_puesto'] * tasa_mantenimiento
    df['eoq_teorico'] = np.where(
        h > 0,
        np.sqrt((2 * df['demanda_anual'] * costo_orden_admin) / h),
        0.0
    )
    df['cajas_a_pedir'] = np.ceil(df['eoq_teorico'] / df['cantidad_por_caja']).astype(int)
    df['unidades_a_pedir'] = df['cajas_a_pedir'] * df['cantidad_por_caja'].astype(int)
    df['cbm_total_pedido'] = df['cajas_a_pedir'] * df['CBMM']
    df['inversion_fob_usd'] = df['unidades_a_pedir'] * df['costo_final']

    # 5. Decisión de Reorden
    df['posicion_inventario'] = df['stock_actual']
    df['requiere_pedido'] = df['posicion_inventario'] <= df['rop']
    df['estado'] = np.where(df['requiere_pedido'], 'REORDENAR', 'OK')

    # Ajustar compras a cero si no se requiere pedido
    for c in ['cajas_a_pedir', 'unidades_a_pedir', 'cbm_total_pedido', 'inversion_fob_usd']:
        df[c] = np.where(df['requiere_pedido'], df[c], 0)

    df['porcentaje_contenedor'] = (df['cbm_total_pedido'] / capacidad_contenedor_cbm) * 100

    return df
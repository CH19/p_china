# Especificación técnica: Diagnóstico ADI-CV² y tratamiento de demanda intermitente

## 1. Contexto del problema

El modelo actual clasifica cada SKU en X/Y/Z usando únicamente el coeficiente
de variación (CV = desviación estándar / media) de la demanda semanal. Con el
dataset actual, **99.8% de los SKUs (2045 de 2048) caen en clase Z**, lo cual
indica que el CV solo ya no discrimina nada — no es que el catálogo sea
uniformemente errático, es que la métrica se satura cuando hay muchas semanas
en cero en la serie.

**Objetivo de este trabajo:** introducir una segunda métrica (ADI — intervalo
promedio entre ventas) para separar "intermitente pero predecible" de
"genuinamente errático", y aplicar el método de forecasting correcto a cada
grupo en vez de tratar el 99.8% del catálogo de la misma forma.

---

## 2. Qué construir

### 2.1. Función `calcular_adi(serie_semanal)`

**Input:** una serie temporal semanal de `Cantidad` por SKU (ya agregada,
mismo objeto `serie_semanal` que ya se genera en el pipeline actual — no se
necesita nueva fuente de datos).

**Cálculo:**
```
ADI = número total de semanas en la serie / número de semanas con venta > 0
```

Ejemplo: si un SKU tiene 52 semanas de historial y vendió en 13 de ellas,
`ADI = 52 / 13 = 4.0` (en promedio, vende cada 4 semanas).

**Output:** un float. Si `semanas_con_venta == 0`, retornar `None` o `inf`
(SKU sin demanda registrada en el período — no clasificable, tratar aparte).

### 2.2. Función `calcular_cv2_semanal(serie_semanal)`

Ya existe una función equivalente en el pipeline (`calcular_cv_semanal`), pero
para la clasificación de 2 ejes se necesita el **CV al cuadrado** (CV²), que
es el estándar en la literatura de Syntetos-Boylan, no el CV simple:

```
CV² = (desviación estándar de la demanda POSITIVA / media de la demanda POSITIVA) ** 2
```

**Importante:** este CV² se calcula **solo sobre las semanas con venta > 0**
(excluyendo los ceros), a diferencia del CV actual del pipeline que se calcula
sobre toda la serie incluyendo ceros. Son métricas distintas — no reemplazar
la función existente, agregar esta nueva.

Aplicar el mismo capping al percentil 95 que ya usa el resto del pipeline
antes de calcular media y desviación, por consistencia.

### 2.3. Función `clasificar_syntetos_boylan(adi, cv2)`

Clasifica el SKU en uno de 4 cuadrantes según los umbrales estándar de la
literatura (Syntetos & Boylan, 2005):

| | CV² ≤ 0.49 | CV² > 0.49 |
|---|---|---|
| **ADI ≤ 1.32** | `smooth` | `erratic` |
| **ADI > 1.32** | `intermittent` | `lumpy` |

```python
def clasificar_syntetos_boylan(adi: float, cv2: float) -> str:
    if adi is None or cv2 is None:
        return 'sin_datos'
    if adi <= 1.32 and cv2 <= 0.49:
        return 'smooth'
    elif adi <= 1.32 and cv2 > 0.49:
        return 'erratic'
    elif adi > 1.32 and cv2 <= 0.49:
        return 'intermittent'
    else:
        return 'lumpy'
```

Estos umbrales (1.32 y 0.49) son los valores publicados en la literatura
académica — no ajustarlos arbitrariamente sin justificación, pero sí correr
el diagnóstico primero antes de decidir si aplican bien a este catálogo
específico (ver sección 4).

### 2.4. Integración al loop principal

En el loop existente (donde ya se calcula `serie_semanal` una vez por SKU),
agregar el cálculo de `adi`, `cv2_positivo` y `cuadrante_syntetos_boylan` como
columnas adicionales del resultado — **sin eliminar** la clasificación XYZ
actual (CV sobre toda la serie), que sigue siendo útil para el cruce con ABC
por ingresos. El cuadrante Syntetos-Boylan es un diagnóstico adicional, no un
reemplazo.

### 2.5. Método de forecasting condicional por cuadrante

Una vez clasificado cada SKU, aplicar el método correspondiente **solo** en
el cálculo del ROP (no cambia nada del EOQ ni de la lógica de contenedor):

- **`smooth`** → mantener el método actual (percentil empírico / fallback
  paramétrico Normal), sin cambios.
- **`erratic`** → mantener método actual, pero asegurar que el capping de
  picos (percentil 95, ya implementado) esté activo — es el caso donde ese
  filtro sí importa.
- **`intermittent`** → implementar **Croston/SBA** (ver sección 3).
- **`lumpy`** → no usar ROP estadístico. Usar una **política de cobertura
  fija en semanas** (ej. mantener stock equivalente a N semanas de venta
  histórica promedio, con N definido por la clase ABC del SKU) en vez de
  intentar calcular un ROP por percentil — con este nivel de erraticidad el
  ROP estadístico no es confiable.

---

## 3. Método Croston/SBA (para clase `intermittent`)

Croston separa la serie en dos componentes y los suaviza independientemente
con suavizado exponencial simple (SES):

1. **Tamaño de la demanda cuando ocurre** (`z_t`): solo los valores donde
   `Cantidad > 0`.
2. **Intervalo entre ocurrencias** (`p_t`): número de períodos entre una
   venta y la siguiente.

**Algoritmo:**

```
Para cada nueva observación con venta > 0 (en el período t):
    z_hat = z_hat + alpha * (z_t - z_hat)     # suaviza el tamaño
    p_hat = p_hat + alpha * (p_t - p_hat)     # suaviza el intervalo

Estimado de demanda promedio por período:
    demanda_estimada = z_hat / p_hat
```

`alpha` típico: 0.1–0.3 (empezar con 0.1, es más conservador para demanda
intermitente con pocos datos).

**Corrección SBA (Syntetos-Boylan Approximation):** Croston puro tiene un
sesgo positivo conocido (sobreestima). SBA lo corrige con un factor:

```
demanda_estimada_sba = (1 - alpha/2) * (z_hat / p_hat)
```

**Uso recomendado:** implementar SBA directamente (no Croston puro), ya que
la corrección es simple y evita el sesgo sistemático.

**Salida esperada:** `demanda_estimada_sba` reemplaza a `demanda_semanal_prom`
únicamente para los SKUs en clase `intermittent`, y a partir de ahí el
cálculo de ROP puede seguir usando el mismo fallback paramétrico Normal ya
existente en el pipeline (`demanda_esperada_lt = demanda_estimada_sba *
lead_time_semanas`), sin necesidad de reescribir esa parte.

---

## 4. Paso previo obligatorio: correr el diagnóstico antes de implementar Croston

**No implementar Croston/SBA a ciegas sobre el 99.8% clasificado como Z.**
Primero correr `calcular_adi` + `calcular_cv2_semanal` +
`clasificar_syntetos_boylan` sobre todo el catálogo y reportar la
distribución real entre los 4 cuadrantes (`value_counts()` de
`cuadrante_syntetos_boylan`).

**Criterio de aceptación de este paso:** un reporte con el conteo de SKUs en
cada uno de los 4 cuadrantes (`smooth`, `erratic`, `intermittent`, `lumpy`),
más el % de inversión FOB (`inversion_fob_usd`) y de valor ABC concentrado en
cada uno. Esto valida si la hipótesis (la mayoría de los "Z" son en realidad
`intermittent`, no `lumpy`) se cumple antes de invertir tiempo en Croston.

Solo después de ver esa distribución se decide si Croston/SBA aplica a una
porción grande o pequeña del catálogo, y si la política de cobertura fija
para `lumpy` necesita afinarse.

---

## 5. Resumen de entregables

1. `calcular_adi(serie_semanal) -> float`
2. `calcular_cv2_semanal(serie_semanal, capping_quantile=0.95) -> float`
3. `clasificar_syntetos_boylan(adi, cv2) -> str`
4. Integración de las 3 funciones anteriores al loop principal existente,
   agregando columnas `adi`, `cv2_positivo`, `cuadrante_syntetos_boylan` a
   `df_planificacion`
5. Reporte de distribución por cuadrante (paso 4 de esta spec) — **entregar
   este resultado antes de continuar** con el punto 6
6. `forecast_croston_sba(serie_semanal, alpha=0.1) -> float` — implementar
   solo si el reporte del punto 5 justifica que vale la pena
7. Lógica condicional en el cálculo de ROP: `intermittent` usa Croston/SBA,
   `lumpy` usa cobertura fija en semanas, `smooth`/`erratic` mantienen el
   método actual sin cambios
# 6 NOTA IMPORTANTE

Todos los entregables tendran que integrarse despues al modelo de Streamlit 
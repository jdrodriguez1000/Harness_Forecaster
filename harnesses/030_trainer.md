# Harness 030 — Trainer

**Tipo:** Pipeline  
**Bloque de construcción:** B (posición 6 de 11)  
**Hito al que pertenece:** Hito B — Ciclo de valor completo  
**Disparador:** Evento `refinery_complete` emitido por 025 Refinery

---

## Propósito

Tomar los datos Gold y producir modelos de pronóstico entrenados y validados para cada combinación cliente × producto activa. El Trainer es el corazón técnico del sistema — aquí vive todo el riesgo ML. Su salida es un conjunto de artefactos de modelo que 035 Predictor usa para generar los números de pronóstico.

El feature engineering es un sub-proceso interno de este harness. No existe como paso separado porque el pipeline de transformación de features es parte inseparable del artefacto del modelo: para hacer inferencia correcta en 035, se debe aplicar exactamente el mismo pipeline de features con el que se entrenó (DEC-024).

---

## Entradas

| Entrada | Descripción | Fuente |
|---------|-------------|--------|
| `timeseries_gold.parquet` | Series de tiempo por combinación cliente × producto | 025 Refinery |
| `combinations_metadata.parquet` | Nivel de confianza, modo cold start, frecuencia de pedido por combinación | 025 Refinery |
| `inventory_gold.parquet` | Datos de producción e inventario cruzados (si aplica) | 025 Refinery |
| `onboarding_config.json` | Horizonte de pronóstico configurado para el cliente | 010 Discovery |
| `client_profile.json` | Nivel de confianza cold start global, jerarquías disponibles | 010 Discovery |
| Evento `refinery_complete` | Señal de inicio con path al Gold | 025 Refinery |

---

## Procesos

### P1 — Clasificación de combinaciones por estrategia de modelo

Antes de entrenar, el harness lee `combinations_metadata.parquet` y asigna a cada combinación cliente × producto una estrategia de entrenamiento:

| Nivel de confianza | Estrategia | Criterio |
|-------------------|------------|----------|
| **Alta** | Modelo local completo | ≥ 3 años de historial con demanda regular |
| **Estándar** | Modelo local con regularización | 2–3 años de historial |
| **Reducida** | Modelo de categoría compartido | 1–2 años de historial |
| **Experimental** | Cascada cold start | < 1 año de historial |

Las combinaciones con estrategia Reducida se agrupan por categoría de producto. Se entrena un modelo por categoría que luego se especializa por combinación vía ajuste fino.

### P2 — Feature engineering (sub-proceso interno)

Para cada combinación, el harness construye la matriz de features. El pipeline de transformación se entrena sobre el conjunto de entrenamiento y luego se serializa junto con el modelo.

**Features de series de tiempo:**

| Feature | Descripción | Aplica a |
|---------|-------------|----------|
| `lag_1` … `lag_N` | Demanda en los N períodos anteriores (N = horizonte de pronóstico × 2) | Todas |
| `rolling_mean_3` | Media móvil de los últimos 3 períodos | Todas |
| `rolling_mean_6` | Media móvil de los últimos 6 períodos | Alta / Estándar |
| `rolling_mean_12` | Media móvil de los últimos 12 períodos | Alta |
| `rolling_std_3` | Desviación estándar de los últimos 3 períodos | Todas |
| `rolling_std_6` | Desviación estándar de los últimos 6 períodos | Alta / Estándar |

**Features de calendario:**

| Feature | Descripción | Condición |
|---------|-------------|-----------|
| `mes_del_año` | 1–12 (numérico cíclico) | Siempre |
| `trimestre` | 1–4 | Siempre |
| `es_fin_de_año` | Bool — meses 11 y 12 | Si estacionalidad detectada |
| `semana_del_año` | 1–52 (si granularidad semanal) | Solo granularidad semanal |

**Features de comportamiento de la combinación:**

| Feature | Descripción |
|---------|-------------|
| `frecuencia_promedio_dias` | Días promedio entre pedidos de esta combinación |
| `dias_desde_ultimo_pedido` | Contador de períodos consecutivos sin pedido |
| `es_periodo_sin_pedido` | Bool — período inferido como demanda cero |
| `minimo_contractual` | Cantidad mínima comprometida (si el cliente lo informó) |
| `tendencia_lineal` | Pendiente de la regresión lineal sobre los últimos 12 períodos |

**Features de inventario (solo si Esquema 2 activo):**

| Feature | Descripción |
|---------|-------------|
| `stock_disponible_lag1` | Stock al final del período anterior |
| `agotado_lag1` | Bool — hubo agotamiento en el período anterior |
| `ratio_stock_demanda` | `stock_disponible / demanda_promedio_3p` |

**Transformaciones del pipeline:**
- Escalado numérico: StandardScaler por feature
- Codificación de features categóricas (categoría, subcategoría): OrdinalEncoder
- El pipeline completo (fit + parámetros) se serializa y forma parte del artefacto del modelo

### P3 — Separación entrenamiento / validación

Para cada combinación, los datos se dividen de la siguiente forma:

```
|←——————————— Conjunto de entrenamiento ———————————→|← Holdout →|
[inicio del historial]                      [últimos N períodos]

N = max(horizonte_pronóstico × 2, 6 períodos)
```

El holdout nunca se toca durante el entrenamiento ni la búsqueda de hiperparámetros. Se usa exclusivamente para calcular el MAPE de validación del modelo final.

### P4 — Selección y entrenamiento de modelos

El harness aplica una estrategia de modelo diferente según el nivel de confianza:

**Estrategia Alta / Estándar — Modelo local por combinación:**

Se entrena un modelo de gradient boosting (LightGBM) por combinación, optimizado para minimizar el error absoluto porcentual medio (MAPE). La búsqueda de hiperparámetros usa validación cruzada con ventana deslizante (time-series cross-validation, 3 folds) sobre el conjunto de entrenamiento.

Hiperparámetros optimizados:
- `num_leaves`, `learning_rate`, `n_estimators`, `min_child_samples`
- Regularización L1 y L2 (más agresiva en Estándar que en Alta)

**Estrategia Reducida — Modelo compartido por categoría:**

Se entrena un modelo LightGBM sobre todas las combinaciones de la misma categoría de producto juntas, con `id_combinacion` como feature adicional. El modelo captura el patrón general de la categoría. Si el historial acumulado de la categoría es suficiente, el modelo produce mejores estimaciones que un modelo local con datos insuficientes.

**Estrategia Experimental — Cascada cold start (DEC-013):**

| Paso | Condición | Acción |
|------|-----------|--------|
| 1 | Existen ≥ 5 combinaciones de la misma categoría con nivel Alta o Estándar | Usar el modelo de categoría compartido con ajuste de escala |
| 2 | No hay modelo de categoría, pero el mismo cliente tiene ≥ 3 combinaciones Alta/Estándar | Usar el modelo más cercano del mismo cliente como prior |
| 3 | Ninguna analogía disponible | Marcar como `pendiente_acumulacion` — se pronostica solo cuando la combinación acumule 3 meses de historial propio |

Las combinaciones en paso 3 se excluyen del ciclo de predicción actual y se monitorean en cada reentrenamiento para detectar cuándo pasan al paso 2 o 1.

### P5 — Evaluación sobre holdout

Con el modelo final entrenado sobre el conjunto de entrenamiento completo, el harness calcula el MAPE sobre el holdout:

```
MAPE = (1/N) × Σ |( demanda_real - demanda_predicha ) / demanda_real| × 100
```

**Casos especiales:**
- Períodos con demanda real = 0 se excluyen del denominador del MAPE (división por cero)
- Períodos con `_periodo_sin_pedido = true` se excluyen de la evaluación

El MAPE de holdout se compara contra el SLA comprometido según el ISD del cliente (DEC-009):

| ISD del cliente | SLA MAPE | Estado |
|-----------------|----------|--------|
| ≥ 95% | ≤ 15% | Verde si MAPE holdout ≤ 15% |
| 70–94% | ≤ 25% | Verde si MAPE holdout ≤ 25% |
| < 70% | Sin garantía | Se registra el MAPE pero no hay umbral |

Si el modelo no alcanza el SLA en holdout, se registra la advertencia en el `training_report.json` y se notifica al operador de Triple S. **El entrenamiento no se aborta** — el pronóstico se entrega igualmente, pero el operador decide si escalar la advertencia al cliente.

### P6 — Serialización de artefactos de modelo

Por cada combinación (o grupo de combinaciones en Reducida), el harness serializa:

```
tenants/{tenant_id}/models/
├── {combination_id}/
│   ├── model.pkl              ← Modelo LightGBM entrenado
│   ├── feature_pipeline.pkl   ← Pipeline de features (scaler + encoders)
│   └── model_metadata.json    ← Metadatos del modelo
└── category_{cat_id}/
    ├── model.pkl              ← Modelo compartido de categoría (Reducida)
    ├── feature_pipeline.pkl
    └── model_metadata.json
```

**Contenido de `model_metadata.json`:**

```json
{
  "combination_id": "CLI001_PRD042",
  "strategy": "local_alta",
  "algorithm": "lightgbm",
  "training_date": "2026-06-08T14:32:00Z",
  "training_samples": 847,
  "holdout_samples": 12,
  "mape_holdout": 8.4,
  "sla_mape": 15.0,
  "sla_status": "verde",
  "horizon": "mensual",
  "feature_count": 18,
  "features_used": ["lag_1", "lag_2", "rolling_mean_3", "mes_del_año", "..."],
  "hyperparameters": { "num_leaves": 31, "learning_rate": 0.05, "..." },
  "model_version": "v1.0",
  "cold_start_mode": "none"
}
```

### P7 — Generación del reporte de entrenamiento

```json
{
  "tenant_id": "...",
  "timestamp": "...",
  "combinaciones_total": 1847,
  "por_estrategia": {
    "local_alta": 892,
    "local_estandar": 631,
    "categoria_reducida": 289,
    "cold_start_analogia_categoria": 21,
    "cold_start_analogia_cliente": 8,
    "pendiente_acumulacion": 6
  },
  "mape_promedio_holdout": 11.2,
  "combinaciones_bajo_sla": 47,
  "combinaciones_sobre_sla": 12,
  "advertencias": [
    "12 combinaciones no alcanzan el SLA comprometido en holdout. Notificar al operador.",
    "6 combinaciones en espera de acumulación de historial — excluidas del próximo pronóstico."
  ]
}
```

### P8 — Registro en base de datos

| Tabla | Registro |
|-------|---------|
| `model_registry` | Una fila por combinación: version, algoritmo, MAPE holdout, SLA status, path del artefacto |
| `training_log` | Una fila por ejecución completa del harness: timestamp, conteos por estrategia, MAPE promedio |
| `clients` | `last_trained_at`, `models_ready = true` |

### P9 — Emisión del evento de completitud

```
EVENT: trainer_complete
  tenant_id: {id}
  timestamp: {ISO-8601}
  models_path: tenants/{id}/models/
  combinaciones_listas: 1841
  combinaciones_excluidas: 6
  mape_promedio_holdout: 11.2
  next_harness: 035_predictor
```

---

## Cadencia de reentrenamiento

| Modo de ingesta | Cuándo se reentrena |
|-----------------|---------------------|
| **Batch** | Al recibir el archivo histórico inicial + cada vez que el cliente entregue un archivo nuevo |
| **Incremental** | Semanalmente, independientemente de si hubo entregas esa semana — el scheduler de Prefect dispara el ciclo 015 → 025 → 030 con el Bronze acumulado actualizado (DEC-012) |

En el reentrenamiento incremental, si ningún dato nuevo fue incorporado desde el último entrenamiento, 030 detecta la condición y omite el reentrenamiento (emite `trainer_complete` con `skipped = true`).

---

## Salidas

### Archivos generados

| Archivo | Descripción | Destino |
|---------|-------------|---------|
| `model.pkl` por combinación | Modelo LightGBM serializado | `tenants/{id}/models/{combination_id}/` |
| `feature_pipeline.pkl` por combinación | Pipeline de features serializado | `tenants/{id}/models/{combination_id}/` |
| `model_metadata.json` por combinación | Metadatos: versión, MAPE holdout, SLA status, hiperparámetros | `tenants/{id}/models/{combination_id}/` |
| `training_report.json` | Resumen del ciclo completo de entrenamiento | `tenants/{id}/models/` |

### Registros actualizados en base de datos

| Tabla | Actualización |
|-------|--------------|
| `model_registry` | Upsert de artefactos activos por combinación |
| `training_log` | Nueva fila por ejecución |
| `clients` | `last_trained_at`, `models_ready = true` |

### Evento emitido

```
trainer_complete → dispara 035 Predictor
```

---

## Condiciones de completitud

El harness 030 se considera **completo** cuando:

1. Todas las combinaciones activas tienen un artefacto de modelo (o están marcadas como `pendiente_acumulacion`)
2. Los artefactos incluyen el modelo y el feature pipeline serializado juntos
3. El MAPE de holdout está calculado y registrado para cada combinación
4. Los modelos que no alcanzan el SLA en holdout están registrados con advertencia
5. El `training_report.json` existe en Storage
6. El `model_registry` en base de datos está actualizado
7. El evento `trainer_complete` fue emitido

---

## Lo que este harness NO hace

- No lee desde Bronze ni Silver — solo desde Gold
- No genera números de pronóstico para el cliente — eso es 035 Predictor
- No detecta anomalías en los pedidos históricos — eso es 035 Predictor
- No publica nada al cliente
- No gestiona pagos ni ciclo de vida del cliente

---

## Dependencias

| Tipo | Harness / Sistema | Detalle |
|------|-------------------|---------|
| Anterior | 025 Refinery | Lee desde Gold — no puede entrenar sin Gold válido |
| Siguiente | 035 Predictor | Usa los artefactos de modelo para generar pronósticos |
| Scheduler | Prefect | Dispara el ciclo semanal de reentrenamiento en Modo Incremental |

---

## Notas de diseño

- **Feature pipeline como parte del artefacto:** El error más común en sistemas ML en producción es aplicar una transformación de features diferente en inferencia respecto al entrenamiento (train-test skew). Al serializar el pipeline junto con el modelo, 035 Predictor no puede invocarlos por separado — siempre obtiene los dos juntos, garantizando coherencia (DEC-024).
- **LightGBM como algoritmo base:** Maneja bien features tabulares con pocas muestras, tiene regularización nativa, es rápido para reentrenamiento semanal con miles de combinaciones, y no requiere infraestructura GPU. Es la elección pragmática para una empresa manufacturera B2B con series de tiempo moderadas.
- **MAPE de holdout no es el MAPE real:** El MAPE que ve el cliente en el dashboard (generado por 045 Monitor) es el MAPE real calculado sobre demanda observada vs. pronóstico del mes anterior. El MAPE de holdout aquí es la estimación interna de Triple S sobre qué tan bueno es el modelo antes de usarlo. Ambos se registran pero tienen propósitos distintos.
- **Combinaciones `pendiente_acumulacion`:** No fallan el harness — simplemente se excluyen del ciclo de predicción actual. En cada reentrenamiento semanal se reevalúan y cuando acumulan 3 meses de historial propio pasan automáticamente a estrategia Experimental con cascada.

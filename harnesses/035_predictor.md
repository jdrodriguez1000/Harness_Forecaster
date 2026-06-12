# Harness 035 — Predictor

**Tipo:** Pipeline  
**Bloque de construcción:** B (posición 7 de 11)  
**Hito al que pertenece:** Hito B — Ciclo de valor completo  
**Disparadores:**
- **Mensual (principal):** Scheduler de Prefect — día 1 hábil de cada mes, para todos los clientes activos
- **Ad-hoc:** Evento `trainer_complete` en el primer ciclo de entrenamiento de un cliente nuevo

---

## Propósito

Tomar los modelos entrenados por 030 Trainer y producir los pronósticos de demanda del mes. Es el harness que genera el número que el cliente finalmente consume. Además de los pronósticos, detecta y clasifica anomalías en la demanda reciente — comportamientos que se apartan del patrón histórico y que el cliente necesita ver para actuar.

La detección de anomalías vive aquí, no en un harness separado, porque la anomalía solo tiene significado en el contexto del modelo de demanda: un pedido es atípico respecto a lo que el modelo esperaba, no en abstracto (DEC-024).

---

## Cadencia de ejecución

| Ciclo | Cuándo | Qué hace |
|-------|--------|----------|
| **Mensual** | Día 1 hábil del mes (todos los clientes activos en paralelo) | Genera el pronóstico oficial para entrega al cliente |
| **Primer ciclo** | Inmediatamente después del primer `trainer_complete` de un cliente nuevo | Genera el pronóstico inaugural — puede ocurrir en cualquier día del mes |
| **Ad-hoc** | Solicitado manualmente por el operador de Triple S | Re-genera el pronóstico si hubo corrección de datos o modelo |

**Relación con 030 Trainer en Modo Incremental:**
030 Trainer reentrena los modelos semanalmente. 035 Predictor corre mensualmente usando los modelos más recientes disponibles. El pronóstico oficial siempre usa el modelo del último reentrenamiento completo exitoso.

---

## Entradas

| Entrada | Descripción | Fuente |
|---------|-------------|--------|
| `model.pkl` + `feature_pipeline.pkl` | Artefactos de modelo por combinación | 030 Trainer / `tenants/{id}/models/` |
| `model_metadata.json` | Metadatos: versión, MAPE holdout, SLA status, nivel de confianza | 030 Trainer |
| `timeseries_gold.parquet` | Historial reciente — ventana de inferencia para construir los features | 025 Refinery |
| `combinations_metadata.parquet` | Nivel de confianza, cold start mode, frecuencia de pedido por combinación | 025 Refinery |
| `inventory_gold.parquet` | Datos de inventario recientes (si Esquema 2 activo) | 025 Refinery |
| `onboarding_config.json` | Horizonte de pronóstico, granularidad, jerarquías disponibles | 010 Discovery |
| `events_registry` | Eventos conocidos registrados en el sistema (temporadas, cierres, promociones) | Base de datos — cargados por el operador |

---

## Procesos

### P1 — Carga de artefactos de modelo

El harness carga desde Storage el `model.pkl` y el `feature_pipeline.pkl` de cada combinación activa. Solo se cargan modelos cuyo `model_metadata.json` indica estado `ready` — los modelos de combinaciones en `pendiente_acumulacion` (DEC-013) se omiten.

Si un modelo tiene más de 45 días desde su última fecha de entrenamiento (`training_date`), se registra una advertencia en el `prediction_report.json` pero el pronóstico se genera igualmente.

### P2 — Construcción de la ventana de inferencia

Para cada combinación, el harness extrae del Gold los últimos N períodos de demanda histórica, donde N es el número de lags y rolling features que necesita el modelo (definido en `model_metadata.json`). Esta ventana es el input al feature pipeline.

El feature pipeline (cargado de `feature_pipeline.pkl`) transforma la ventana con exactamente las mismas transformaciones aplicadas durante el entrenamiento — garantizando que no haya discrepancia entre features de entrenamiento e inferencia.

### P3 — Generación de pronósticos por combinación

El harness aplica el modelo a la ventana de inferencia y produce un pronóstico para cada período del horizonte configurado.

**Salida por combinación:**

| Campo | Descripción |
|-------|-------------|
| `combination_id` | `{id_cliente}_{id_producto}` |
| `periodo` | Fecha del período pronosticado |
| `cantidad_pronosticada` | Valor puntual del pronóstico |
| `intervalo_inferior_80` | Límite inferior del intervalo de confianza al 80% |
| `intervalo_superior_80` | Límite superior del intervalo de confianza al 80% |
| `nivel_confianza` | Alta / Estándar / Reducida / Experimental |
| `cold_start_mode` | `none` / `analogia_categoria` / `analogia_cliente` / `acumulacion` |

Los intervalos de confianza se calculan mediante bootstrap sobre las predicciones del modelo (100 muestras con perturbación de los features). Esto aplica a todos los niveles de confianza — los intervalos serán más amplios para combinaciones con menos historial.

### P4 — Agregación a múltiples niveles jerárquicos

El pronóstico se genera primero a nivel de combinación SKU × sede (nivel más granular). Luego se agregan hacia arriba siguiendo la jerarquía disponible del cliente:

```
SKU × Sede  (granularidad base)
    ↓ suma
SKU × Cliente consolidado  (suma de todas las sedes del cliente XYZ)
    ↓ suma
Categoría × Sede  (suma de todos los SKUs de la categoría)
    ↓ suma
Categoría × Cliente consolidado  (máximo nivel de agregación)
```

**Regla de consistencia jerárquica:** Los pronósticos agregados son siempre la suma exacta de sus componentes. No se ajustan de forma independiente. Esto garantiza que el planificador de demanda (nivel SKU) y el directivo (nivel categoría) estén viendo números coherentes entre sí (DEC-022).

Los niveles disponibles dependen de la jerarquía que el cliente declaró en 010 Discovery — si el cliente solo tiene un nivel geográfico, solo se generan los dos primeros niveles.

### P5 — Detección de anomalías en demanda reciente

El harness analiza el período inmediatamente anterior al pronóstico (el último período con demanda real observada) y lo compara contra lo que el modelo esperaba para ese período.

**Umbral de anomalía:**

```
demanda_esperada = predicción del modelo para ese período (generada en el ciclo anterior)
error_relativo = |demanda_real - demanda_esperada| / demanda_esperada

Si error_relativo > 0.5 (50% de desviación) → candidato a anomalía
```

Adicionalmente, se evalúa la desviación respecto al patrón histórico de la combinación:

```
z_score = (demanda_real - media_histórica) / desviación_estándar_histórica

Si |z_score| > 3 → candidato a anomalía por desviación histórica
```

Un período se marca como anomalía si supera **cualquiera** de los dos umbrales.

### P6 — Clasificación de anomalías

Cada candidato a anomalía pasa por una clasificación binaria:

| Clasificación | Condición | Acción en dashboard |
|--------------|-----------|---------------------|
| **Extraordinario legítimo** | La fecha del pedido atípico coincide con un evento registrado en `events_registry` (temporada alta, promoción, cierre de planta, etc.) | Se muestra con etiqueta del evento — no requiere acción del cliente |
| **Anomalía sin explicación** | No hay evento registrado que lo justifique | Se presenta al cliente para confirmación — botón "Es correcto" / "Es un error" |

Los eventos en `events_registry` son registrados por el operador de Triple S (en Fase 1) o por el propio cliente desde el dashboard en una sección restringida (en Fase 3). El cliente no puede agregar eventos retroactivamente para justificar anomalías ya ocurridas — el registro debe ser previo o simultáneo al período.

**Impacto de la clasificación en el modelo:**
- Extraordinario legítimo: el período se conserva en el historial con la etiqueta del evento. En el próximo reentrenamiento, 030 Trainer lo trata como señal real.
- Anomalía confirmada por el cliente como error: el período se excluye del próximo reentrenamiento. No se modifica Bronze ni Silver — se agrega a una tabla `excluded_periods` que 030 Trainer consulta.
- Anomalía no respondida por el cliente: se conserva como dato real hasta que el cliente responda o pasen 30 días, momento en que se clasifica automáticamente como legítimo.

### P7 — Generación de metadatos de explicabilidad

Para cada combinación pronosticada, el harness genera los metadatos que el dashboard necesita para mostrar la explicación del pronóstico (DEC-022):

```json
{
  "combination_id": "CLI001_PRD042",
  "forecast_value": 1240,
  "nivel_confianza": "Alta",
  "tendencia_reciente": "creciente",
  "tendencia_periodos": 3,
  "tendencia_pct": 12.4,
  "evento_activo": null,
  "anomalia_reciente": {
    "periodo": "2026-05",
    "demanda_real": 2100,
    "demanda_esperada": 1180,
    "clasificacion": "sin_explicacion",
    "pendiente_confirmacion": true
  }
}
```

**Valores posibles de `tendencia_reciente`:** `creciente` / `decreciente` / `estable`  
Calculado sobre los últimos 3 períodos del historial real — no sobre el pronóstico.

### P8 — Consolidación de artefactos de pronóstico

El harness genera un único archivo de pronóstico consolidado por cliente:

```
tenants/{tenant_id}/forecasts/
└── {YYYY_MM}/
    ├── forecast_skus.parquet          ← Pronósticos nivel SKU × Sede
    ├── forecast_clients.parquet       ← Pronósticos nivel SKU × Cliente consolidado
    ├── forecast_categories.parquet    ← Pronósticos nivel Categoría × Sede
    ├── forecast_summary.parquet       ← Pronósticos nivel Categoría × Cliente consolidado
    ├── anomalies.parquet              ← Anomalías detectadas con clasificación
    ├── explainability.parquet         ← Metadatos de explicabilidad por combinación
    └── prediction_report.json         ← Reporte de ejecución
```

### P9 — Generación del reporte de predicción

```json
{
  "tenant_id": "...",
  "timestamp": "...",
  "periodo_pronosticado": "2026-07",
  "combinaciones_pronosticadas": 1841,
  "combinaciones_excluidas_cold_start": 6,
  "niveles_generados": ["sku_sede", "sku_cliente", "categoria_sede", "categoria_cliente"],
  "anomalias_detectadas": 14,
  "anomalias_extraordinarias": 9,
  "anomalias_sin_explicacion": 5,
  "modelos_con_advertencia_antiguedad": 3,
  "sla_status": "verde"
}
```

### P10 — Registro en base de datos y emisión del evento

| Tabla | Registro |
|-------|---------|
| `forecasts` | Una fila por combinación × período: valor, intervalos, nivel de confianza |
| `anomalies` | Una fila por anomalía: clasificación, estado de confirmación del cliente |
| `prediction_log` | Una fila por ejecución del harness: timestamp, conteos, SLA status |
| `clients` | `last_forecast_at`, `forecast_ready = true` |

```
EVENT: predictor_complete
  tenant_id: {id}
  timestamp: {ISO-8601}
  periodo_pronosticado: "2026-07"
  forecast_path: tenants/{id}/forecasts/2026_07/
  anomalias_pendientes_confirmacion: 5
  next_harness: 040_publisher
```

---

## Salidas

### Archivos generados

| Archivo | Descripción | Destino |
|---------|-------------|---------|
| `forecast_skus.parquet` | Pronósticos granulares: SKU × Sede, con intervalos de confianza | `tenants/{id}/forecasts/{YYYY_MM}/` |
| `forecast_clients.parquet` | Pronósticos por cliente XYZ consolidado | `tenants/{id}/forecasts/{YYYY_MM}/` |
| `forecast_categories.parquet` | Pronósticos por categoría × Sede | `tenants/{id}/forecasts/{YYYY_MM}/` |
| `forecast_summary.parquet` | Pronósticos máxima agregación — vista directiva | `tenants/{id}/forecasts/{YYYY_MM}/` |
| `anomalies.parquet` | Anomalías detectadas con clasificación y estado de confirmación | `tenants/{id}/forecasts/{YYYY_MM}/` |
| `explainability.parquet` | Metadatos de explicabilidad por combinación | `tenants/{id}/forecasts/{YYYY_MM}/` |
| `prediction_report.json` | Reporte de ejecución: conteos, SLA status, advertencias | `tenants/{id}/forecasts/{YYYY_MM}/` |

### Registros actualizados en base de datos

| Tabla | Actualización |
|-------|--------------|
| `forecasts` | Pronósticos del período por combinación |
| `anomalies` | Anomalías detectadas con estado inicial `pendiente` |
| `prediction_log` | Nueva fila por ejecución |
| `clients` | `last_forecast_at`, `forecast_ready = true` |

### Evento emitido

```
predictor_complete → dispara 040 Publisher
```

---

## Condiciones de completitud

El harness 035 se considera **completo** cuando:

1. Todos los pronósticos están generados para todas las combinaciones activas (o marcadas como excluidas con razón)
2. Los cuatro niveles de agregación están calculados y son consistentes entre sí
3. La detección y clasificación de anomalías está completa
4. Los metadatos de explicabilidad están generados para cada combinación
5. Los artefactos Parquet existen en Storage bajo el directorio del período
6. Los registros en `forecasts` y `anomalies` están en base de datos
7. El `prediction_report.json` existe en Storage
8. El evento `predictor_complete` fue emitido

---

## Lo que este harness NO hace

- No entrena ni modifica modelos — eso es 030 Trainer
- No publica nada al cliente — eso es 040 Publisher
- No calcula el MAPE real contra demanda observada — eso es 045 Monitor (el MAPE real solo se puede calcular cuando la demanda del período pronosticado ya ocurrió)
- No limpia ni transforma datos

---

## Dependencias

| Tipo | Harness / Sistema | Detalle |
|------|-------------------|---------|
| Anterior | 030 Trainer | Requiere artefactos de modelo válidos |
| Anterior | 025 Refinery | Requiere Gold actualizado como ventana de inferencia |
| Siguiente | 040 Publisher | Recibe todos los artefactos de pronóstico para publicarlos |
| Transversal | 045 Monitor | Consume `forecasts` de ciclos anteriores para calcular MAPE real |

---

## Notas de diseño

- **MAPE de holdout vs. MAPE real:** 030 Trainer calcula el MAPE sobre datos históricos retenidos (estimación interna). 045 Monitor calcula el MAPE real comparando el pronóstico del mes pasado contra la demanda real observada ese mes. Solo el MAPE real es el que se reporta al cliente y el que determina el cumplimiento del SLA. Esta distinción es crítica — en este harness solo existe el primero.
- **Intervalo de confianza al 80%:** Se eligió 80% (en lugar del convencional 95%) porque en forecasting de demanda B2B los intervalos al 95% son tan amplios que pierden valor práctico para el planificador. Al 80% el intervalo es accionable: el planificador puede usarlo para definir stock de seguridad.
- **Anomalías pendientes de confirmación:** No bloquean la publicación del pronóstico. Se publican junto con el pronóstico y el cliente las responde desde el dashboard a su ritmo. 030 Trainer solo las incorpora en el siguiente reentrenamiento si ya tienen respuesta.
- **Consistencia jerárquica forzada:** Los agregados son siempre suma exacta de los componentes. No se usa reconciliación probabilística (como MinT o BU) porque el cliente no tiene capacidad técnica para interpretar discrepancias entre niveles — la coherencia absoluta genera más confianza en el número.

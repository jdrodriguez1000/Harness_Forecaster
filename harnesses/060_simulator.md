# Harness 060 — Simulator

**Tipo:** On-demand  
**Bloque de construcción:** E (posición 11 de 11)  
**Hito al que pertenece:** Hito E — Funcionalidad avanzada  
**Disparadores:**
- Evento `predictor_complete` — ciclo mensual: el Simulator corre automáticamente junto al pronóstico oficial
- Solicitud manual del operador de Triple S — re-ejecución ad-hoc para un cliente específico

---

## Propósito

Producir pronósticos alternativos bajo escenarios hipotéticos predefinidos por Triple S. El cliente recibe, además de su pronóstico oficial, una sección de simulaciones que le permite ver qué pasaría con su demanda bajo condiciones distintas a las esperadas — sin que tenga que solicitar nada ni entender cómo funcionan los modelos.

Los artefactos del Simulator **nunca se mezclan con los pronósticos oficiales**. Son informativos, no compromisos. El cliente los usa para planificar contingencias; las decisiones de producción se basan en el pronóstico oficial (DEC-025).

---

## Escenarios estándar (Fase 1 y 2)

Triple S define y ejecuta automáticamente 3–5 escenarios por cliente en cada ciclo mensual. Los escenarios son iguales para todos los clientes en Fase 1 — en Fase 3 evolucionan a levers ajustables dentro de rangos que Triple S controla.

| ID | Nombre | Descripción | Método de modificación |
|----|--------|-------------|------------------------|
| SC-01 | **Optimista** | ¿Qué pasa si la demanda crece más de lo esperado? | Multiplica la tendencia reciente × 1.20 en los features de entrada |
| SC-02 | **Pesimista** | ¿Qué pasa si la demanda cae moderadamente? | Multiplica la tendencia reciente × 0.80 en los features de entrada |
| SC-03 | **Choque de demanda** | ¿Qué pasa si la demanda cae abruptamente? | Aplica un multiplicador de 0.60 sobre el pronóstico base de cada combinación |
| SC-04 | **Aceleración de temporada** | ¿Qué pasa si la temporada alta empieza antes de lo previsto? | Desplaza las features de estacionalidad 4 semanas hacia adelante (solo si se detectó estacionalidad en onboarding) |
| SC-05 | **Demanda sostenida** | ¿Qué pasa si la demanda se estabiliza al nivel promedio de los últimos 3 meses, sin tendencia? | Fija los features de tendencia a cero; mantiene el resto |

Triple S puede agregar, remover o ajustar los parámetros de estos escenarios desde 055 Command sin necesidad de modificar código — los escenarios están definidos como configuración en la tabla `scenario_definitions`.

---

## Entradas

| Entrada | Descripción | Fuente |
|---------|-------------|--------|
| `model.pkl` + `feature_pipeline.pkl` | Artefactos de modelo por combinación | 030 Trainer |
| `timeseries_gold.parquet` | Ventana de inferencia — igual que usa 035 Predictor | 025 Refinery |
| `combinations_metadata.parquet` | Nivel de confianza, cold start, frecuencia | 025 Refinery |
| `forecast_skus.parquet` | Pronóstico oficial del mes — usado como línea base de comparación | 035 Predictor |
| `scenario_definitions` | Tabla con los escenarios activos y sus parámetros de modificación | Base de datos / 055 Command |
| `onboarding_config.json` | Horizonte, granularidad, jerarquías | 010 Discovery |
| Evento `predictor_complete` | Señal de inicio | 035 Predictor |

---

## Procesos

### P1 — Carga de escenarios activos

El harness consulta la tabla `scenario_definitions` para obtener los escenarios configurados para este cliente. Cada escenario tiene:

```json
{
  "scenario_id": "SC-01",
  "name": "Optimista",
  "description": "Crecimiento moderadamente superior al esperado",
  "modification_type": "trend_multiplier",
  "modification_value": 1.20,
  "applies_to": "all_combinations",
  "active": true
}
```

Si un cliente no tiene escenarios personalizados, se aplican los 5 estándar. El operador puede desactivar escenarios específicos para clientes donde no aplican (ej. SC-04 se desactiva si no hubo estacionalidad detectada).

### P2 — Construcción de ventanas de inferencia modificadas

Para cada escenario, el harness toma la ventana de inferencia original (la misma que usó 035 Predictor en P2) y aplica la modificación definida:

**Tipo `trend_multiplier`** (SC-01, SC-02):
```
features_modificados = features_originales
features_modificados["tendencia_lineal"] = tendencia_lineal_original × modification_value
features_modificados["rolling_mean_3"]  = rolling_mean_3_original × modification_value
features_modificados["rolling_mean_6"]  = rolling_mean_6_original × modification_value
```

**Tipo `output_multiplier`** (SC-03):
```
No se modifican los features de entrada.
El multiplicador se aplica directamente sobre el output del modelo.
resultado_escenario = resultado_modelo × modification_value
```
Este tipo es el más simple pero el menos sofisticado. Se usa cuando el escenario representa un shock externo que no está capturado en los features históricos (ej. una caída de demanda repentina por crisis).

**Tipo `seasonality_shift`** (SC-04):
```
features_modificados = features_originales
Desplazar los features de calendario N semanas hacia adelante:
  mes_del_año → mes_del_año equivalente a 4 semanas antes
  semana_del_año → semana_del_año - 4
Solo aplica a combinaciones donde _estacionalidad_detectada = true
```

**Tipo `trend_zero`** (SC-05):
```
features_modificados = features_originales
features_modificados["tendencia_lineal"] = 0
features_modificados["rolling_mean_3"]  = mean(rolling_mean_3_últimos_3_meses)
features_modificados["rolling_mean_6"]  = features_originales["rolling_mean_6"]
```

### P3 — Ejecución del modelo con inputs modificados

Para cada escenario y cada combinación activa, el harness corre el mismo modelo cargado en P1 con los features modificados de P2. El feature pipeline se aplica sobre los features modificados antes de pasarlos al modelo.

```
resultado_escenario[escenario][combinación] = model.predict(
    feature_pipeline.transform(features_modificados[escenario][combinación])
)
```

Los intervalos de confianza no se calculan para los escenarios — son pronósticos puntuales. La incertidumbre inherente de un escenario hipotético hace que los intervalos sean demasiado amplios para ser útiles.

### P4 — Agregación a niveles jerárquicos

Igual que en 035 Predictor (P4), los resultados de cada escenario se agregan hacia arriba por la jerarquía del cliente:

```
SKU × Sede → SKU × Cliente consolidado → Categoría × Sede → Categoría × Cliente consolidado
```

La consistencia jerárquica se mantiene: los agregados son siempre la suma exacta de sus componentes.

### P5 — Cálculo de la diferencia vs. pronóstico oficial

Para cada escenario, combinación y nivel jerárquico, el harness calcula la desviación respecto al pronóstico oficial:

```
delta_absoluto  = resultado_escenario - pronóstico_oficial
delta_relativo  = delta_absoluto / pronóstico_oficial × 100   (en %)
```

Esta diferencia es lo que el cliente realmente necesita ver: no el número del escenario en abstracto, sino cuánto más o cuánto menos tendría que producir respecto a su plan base.

**Ejemplo de salida por combinación:**

```
Combinación: CLI001 × PRD042
Pronóstico oficial: 1.240 unidades
─────────────────────────────────
SC-01 Optimista:       +248 unidades (+20%)  → preparar stock adicional para 1.488
SC-02 Pesimista:       -248 unidades (-20%)  → mínimo de producción: 992
SC-03 Choque demanda:  -496 unidades (-40%)  → mínimo en crisis: 744
SC-05 Demanda estable: +12  unidades (+1%)   → sin cambio significativo
```

### P6 — Generación de la narrativa de cada escenario

Para cada escenario, el harness genera un texto en lenguaje de negocio que acompaña los números en el dashboard:

| Escenario | Texto generado |
|-----------|----------------|
| SC-01 Optimista | "Si la demanda crece un 20% más de lo esperado, necesitarías {X} unidades adicionales en stock. Las categorías más impactadas serían: {top 3 categorías}." |
| SC-02 Pesimista | "Si la demanda cae un 20%, el mínimo de producción recomendado es {X} unidades. Estas {N} combinaciones podrían llegar a demanda cero: {lista}." |
| SC-03 Choque | "En un escenario de caída abrupta del 40%, la demanda total caería a {X} unidades. El impacto más fuerte sería en {categoría o cliente XYZ principal}." |
| SC-04 Temporada anticipada | "Si la temporada alta comienza 4 semanas antes de lo histórico, el pico de demanda se adelantaría al {fecha estimada}. Necesitarías tener stock listo para {fecha - 2 semanas}." |
| SC-05 Estabilización | "Si la demanda se estabiliza en el nivel promedio reciente, el pronóstico varía apenas {X}% respecto al oficial. No habría cambios significativos en el plan de producción." |

Los textos usan los valores reales calculados, no plantillas genéricas.

### P7 — Construcción de los artefactos de simulación

```
tenants/{tenant_id}/forecasts/{YYYY_MM}/simulations/
├── SC-01_optimista.parquet
├── SC-02_pesimista.parquet
├── SC-03_choque_demanda.parquet
├── SC-04_temporada_anticipada.parquet    ← solo si estacionalidad detectada
├── SC-05_demanda_estable.parquet
├── scenarios_summary.parquet            ← todos los escenarios + delta vs. oficial en un solo archivo
└── simulator_report.json
```

**Contenido de `scenarios_summary.parquet`:** una fila por combinación × escenario con: `combination_id`, `scenario_id`, `scenario_name`, `periodo`, `forecast_base`, `forecast_escenario`, `delta_absoluto`, `delta_relativo`.

**Contenido de `simulator_report.json`:**
```json
{
  "tenant_id": "...",
  "timestamp": "...",
  "periodo": "2026-07",
  "escenarios_ejecutados": 5,
  "combinaciones_evaluadas": 1841,
  "escenarios_omitidos": ["SC-04"],
  "razon_omision": { "SC-04": "Estacionalidad no detectada para este cliente" },
  "mayor_impacto_positivo": { "escenario": "SC-01", "combinacion": "CLI001_PRD042", "delta_pct": 32.4 },
  "mayor_impacto_negativo": { "escenario": "SC-03", "combinacion": "CLI007_PRD018", "delta_pct": -61.2 }
}
```

### P8 — Notificación a 040 Publisher

El harness notifica a 040 Publisher que los artefactos de simulación están listos para ser publicados en la sección diferenciada del dashboard:

```
EVENT: simulator_complete
  tenant_id: {id}
  timestamp: {ISO-8601}
  periodo: "2026-07"
  simulations_path: tenants/{id}/forecasts/2026_07/simulations/
  escenarios_disponibles: ["SC-01", "SC-02", "SC-03", "SC-05"]
```

040 Publisher ya recibió `predictor_complete`. Al recibir `simulator_complete`, agrega la sección de simulaciones al dashboard y al exportable Excel (hoja `Simulaciones`).

**Separación en el dashboard:**
- Sección principal: "Tu pronóstico de {mes}" → datos oficiales de 035 Predictor
- Sección diferenciada: "Escenarios alternativos" → datos de 060 Simulator, con etiqueta visual clara "Simulación — no oficial"

---

## Evolución hacia Fase 3: levers ajustables por el cliente

En Fase 3, el Simulator evoluciona para permitir que el cliente ajuste parámetros dentro de rangos que Triple S define y controla (DEC-025). Los levers quedan en el dashboard como sliders o campos numéricos acotados:

| Lever | Rango permitido | Qué modifica |
|-------|-----------------|--------------|
| Variación de demanda general | -30% a +30% | Multiplica el forecast base |
| Cliente XYZ específico | -50% a +100% | Modifica features de ese cliente solo |
| Categoría de producto | -40% a +40% | Modifica features de las combinaciones de esa categoría |
| Inicio anticipado/tardío de temporada | -8 a +8 semanas | Solo si estacionalidad detectada |

El cliente mueve los levers y ve el resultado en tiempo real (< 5 segundos). El resultado es una simulación, nunca el pronóstico oficial. Triple S controla que los levers no puedan salirse de rangos razonables — no se puede simular un crecimiento del 500% que produciría números absurdos.

Esta funcionalidad requiere que 060 Simulator exponga un endpoint de API interna (no pública) que el dashboard llama on-demand, distinto del flujo batch mensual.

---

## Salidas

### Archivos generados

| Archivo | Descripción | Destino |
|---------|-------------|---------|
| `SC-XX_{nombre}.parquet` | Pronóstico del escenario por combinación × nivel | `tenants/{id}/forecasts/{YYYY_MM}/simulations/` |
| `scenarios_summary.parquet` | Todos los escenarios + delta vs. oficial | `tenants/{id}/forecasts/{YYYY_MM}/simulations/` |
| `simulator_report.json` | Reporte de ejecución: escenarios ejecutados, omitidos, mayores impactos | `tenants/{id}/forecasts/{YYYY_MM}/simulations/` |

### Registros actualizados en base de datos

| Tabla | Actualización |
|-------|--------------|
| `simulation_log` | Nueva fila por ejecución: escenarios corridos, timestamp, estado |
| `clients` | `last_simulation_at` |

### Evento emitido

```
simulator_complete → consumido por 040 Publisher
                     para publicar sección de simulaciones en el dashboard
```

---

## Condiciones de completitud

El harness 060 se considera **completo** cuando:

1. Todos los escenarios activos fueron ejecutados (o marcados como omitidos con razón)
2. Los artefactos Parquet de cada escenario existen en Storage
3. El `scenarios_summary.parquet` consolida todos los escenarios con deltas calculados
4. El `simulator_report.json` existe con el resumen de la ejecución
5. El registro en `simulation_log` fue creado
6. El evento `simulator_complete` fue emitido a 040 Publisher

---

## Lo que este harness NO hace

- No modifica los modelos entrenados — los usa tal cual, solo cambia los inputs
- No genera el pronóstico oficial — eso es exclusivamente 035 Predictor
- No publica directamente al cliente — notifica a 040 Publisher para que lo haga en la sección correcta
- No permite al cliente definir escenarios libremente (Fase 1 y 2) — los escenarios son definidos y controlados por Triple S

---

## Dependencias

| Tipo | Harness / Sistema | Detalle |
|------|-------------------|---------|
| Anterior | 030 Trainer | Requiere los mismos artefactos de modelo que usa 035 |
| Anterior | 035 Predictor | Requiere el pronóstico oficial como línea base para calcular los deltas |
| Anterior | 025 Refinery | Requiere Gold actualizado como ventana de inferencia |
| Posterior | 040 Publisher | Recibe `simulator_complete` para publicar la sección de simulaciones |
| Configuración | 055 Command | Operador define y gestiona los escenarios activos vía `scenario_definitions` |

---

## Notas de diseño

- **Escenarios como configuración, no como código:** Los parámetros de cada escenario (tipo de modificación y valor) están en la tabla `scenario_definitions`, no hardcodeados. Agregar un nuevo escenario estándar o ajustar el multiplicador del pesimista de -20% a -25% es una operación de base de datos, no un deploy. Esto le da al equipo de Triple S flexibilidad operativa para refinar los escenarios con lo que aprenden de los clientes.
- **Sin intervalos de confianza en escenarios:** Un intervalo de confianza sobre un escenario hipotético sería de una amplitud tan grande que perdería cualquier valor informativo. El cliente necesita entender que el escenario es una dirección ("si pasa X, la demanda sería más o menos Y"), no una predicción estadística. Presentar intervalos crearía una falsa precisión.
- **La sección "Escenarios" nunca se confunde con el pronóstico oficial:** El nombre, el color y la etiqueta en el dashboard son deliberadamente distintos. En ningún exportable Excel el pronóstico de escenario aparece en la misma hoja que el pronóstico oficial. Esta separación es una regla de diseño de UI tan importante como cualquier regla de código (DEC-025).
- **060 se construye al final porque depende de todo lo anterior (DEC-026):** Para que los escenarios sean significativos se necesitan modelos entrenados con datos reales (030), un pronóstico base real (035), y un Publisher que ya sabe cómo presentar resultados (040). Construirlo antes sería construir una capa de presentación sin contenido.

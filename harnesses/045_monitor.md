# Harness 045 — Monitor

**Tipo:** Pipeline  
**Bloque de construcción:** D (posición 9 de 11)  
**Hito al que pertenece:** Hito D — Excelencia operativa  
**Disparadores:**
- Evento `publisher_complete` — ciclo mensual de cálculo de MAPE real y KPIs
- Timer diario (06:00 UTC) — verificación de salud del pipeline
- Evento `trainer_complete` — verificación post-entrenamiento de calidad de modelos

---

## Propósito

Observar el sistema desde afuera para detectar problemas que ningún harness individual puede ver: si los pronósticos del mes pasado fueron precisos, si los modelos están derivando, si algún paso del pipeline falló o fue lento. Es el sistema nervioso de Triple S — sin él, los problemas se descubren cuando el cliente se queja, no antes.

Solo tiene sentido construirlo después de que existan pronósticos reales que monitorear (DEC-026). Su audiencia es el equipo interno de Triple S, no el cliente.

---

## Cadencia de ejecución

| Ciclo | Cuándo | Qué hace |
|-------|--------|----------|
| **Mensual** | Tras `publisher_complete` del mes en curso | MAPE real del mes anterior + KPIs + reporte de SLA |
| **Diario** | 06:00 UTC todos los días | Salud del pipeline: ejecuciones, latencias, datos frescos |
| **Post-entrenamiento** | Tras `trainer_complete` | Validación de calidad de los modelos recién entrenados |

---

## Entradas

| Entrada | Descripción | Fuente |
|---------|-------------|--------|
| Tabla `forecasts` | Pronósticos históricos por combinación × período (generados por 035) | Base de datos |
| `timeseries_gold.parquet` | Demanda real observada por combinación × período (actualizada por 025) | 025 Refinery |
| Tabla `isd_history` | Historial de ISD por cliente por ciclo | 020 Diagnosis |
| Tabla `model_registry` | Metadatos de modelos: versión, MAPE holdout, fecha de entrenamiento | 030 Trainer |
| Tabla `training_log` | Historial de ejecuciones de entrenamiento | 030 Trainer |
| Tabla `prediction_log` | Historial de ejecuciones de predicción | 035 Predictor |
| Tabla `publication_log` | Historial de publicaciones con timestamps y SLA status | 040 Publisher |
| Tabla `clients` | Estado actual de cada cliente: status, plan, categoría | 050 Lifecycle |
| Tabla `invoices` | Historial de facturas y pagos | 050 Lifecycle |
| Tabla `sla_violations` | Violaciones de SLA registradas por 040 Publisher | 040 Publisher |

---

## Procesos

### P1 — Cálculo del MAPE real por combinación

**Ejecutado en:** Ciclo mensual

El MAPE real es la medida que importa para el SLA. Se calcula comparando el pronóstico que 035 generó para el período M contra la demanda real observada en el período M (disponible en Gold una vez que llegaron los datos del período).

```
Para cada combinación cliente × producto, para el período M:

  MAPE_real = |( demanda_real_M - demanda_pronosticada_M ) / demanda_real_M| × 100

Excluir del cálculo:
  - Períodos donde demanda_real_M = 0 (denominador nulo)
  - Períodos marcados como anomalía confirmada por el cliente como error
    (esos registros están en la tabla excluded_periods)

MAPE_cliente = promedio de MAPE_real sobre todas las combinaciones activas del cliente
```

El MAPE real por cliente se compara contra el SLA comprometido según su ISD vigente en ese período (DEC-009):

| ISD del cliente (período M) | SLA MAPE | Resultado |
|----------------------------|----------|-----------|
| ≥ 95% | ≤ 15% | `verde` si MAPE_cliente ≤ 15%, `rojo` si no |
| 70–94% | ≤ 25% | `verde` si MAPE_cliente ≤ 25%, `rojo` si no |
| < 70% | Sin garantía | Se registra el MAPE pero no hay umbral de SLA |

Toda violación de SLA se persiste en `sla_violations` con el MAPE observado, el umbral comprometido y el período.

### P2 — Descomposición del error por combinación

Para cada cliente con MAPE_cliente > umbral SLA, el harness identifica qué combinaciones específicas concentran el error:

```
Top N combinaciones con mayor MAPE_real individual
→ ¿Tienen bajo historial (Reducida / Experimental)?
→ ¿Hubo una anomalía no clasificada en ese período?
→ ¿El modelo de esa combinación tiene advertencia de antigüedad?
→ ¿El ISD empeoró significativamente respecto al período anterior?
```

Este diagnóstico acompaña la alerta al operador de Triple S — no es solo "fallaste el SLA", sino "estas 5 combinaciones lo explican y estas son las causas posibles".

### P3 — Detección de deriva de modelos

**Ejecutado en:** Ciclo mensual + post-entrenamiento

La deriva (drift) ocurre cuando un modelo que era preciso se vuelve progresivamente menos preciso a lo largo del tiempo, sin que haya un evento puntual que lo explique.

**Método de detección:**

Para cada combinación, el harness mantiene una ventana deslizante de los últimos 6 MAPE reales mensuales:

```
Si tendencia_lineal(MAPE_real_últimos_6_meses) > 0 Y pendiente > 2% por mes
→ combinación marcada como _drift_detectado = true
```

Si más del 20% de las combinaciones de un cliente muestran drift simultáneo, se escala como alerta de nivel cliente (el problema probablemente es un cambio estructural en el negocio del cliente, no un fallo de modelo individual).

**Causas comunes de drift que el harness registra:**
- Cambio en el patrón de frecuencia de pedido (frecuencia real vs. frecuencia del modelo)
- ISD cayendo (datos de peor calidad degradan los features)
- Tiempo excesivo desde el último reentrenamiento (modelo obsoleto)
- Combinación nueva activa que está siendo estimada por analogía

### P4 — Verificación de salud del pipeline

**Ejecutado en:** Timer diario

El harness verifica que cada etapa del pipeline haya completado exitosamente dentro de sus ventanas de SLA:

| Harness | SLA de ejecución | Verificación |
|---------|-----------------|-------------|
| 015 Intake | < 2h desde recepción del archivo | Consulta `intake_log` — ¿el último intake completó en tiempo? |
| 020 Diagnosis | < 4h desde `intake_complete` | Consulta `isd_history` — ¿el ISD del período actual existe? |
| 025 Refinery | < 6h desde `intake_complete` | Consulta `refinery_log` — ¿el Gold fue actualizado? |
| 030 Trainer | < 12h desde `refinery_complete` | Consulta `training_log` — ¿hay modelos más recientes que el Gold? |
| 035 Predictor | Día 1 hábil del mes | Consulta `prediction_log` — ¿el pronóstico del período existe? |
| 040 Publisher | Día ≤ 5 hábil del mes | Consulta `publication_log` + `sla_violations` |

Si cualquier verificación falla (el paso no completó o lo hizo fuera de tiempo), el harness genera una alerta interna clasificada por severidad:

| Severidad | Condición | Acción |
|-----------|-----------|--------|
| **Crítica** | Pipeline bloqueado — cliente sin pronóstico pasado el día 5 hábil | Notificación inmediata al operador + escalada por correo |
| **Alta** | Paso tardío — completó pero fuera del SLA interno | Alerta en el portal interno de Triple S |
| **Media** | Advertencia — modelo antiguo (> 45 días sin reentrenar en Modo Incremental) | Nota en el reporte diario |

### P5 — Verificación de frescura de datos

**Ejecutado en:** Timer diario

Para clientes en Modo Incremental, el harness verifica que los datos estén llegando en la frecuencia acordada:

```
días_desde_último_intake = fecha_actual - clients.last_intake_at

Si modo = incremental_diario  Y días_desde_último_intake > 2 → alerta
Si modo = incremental_semanal Y días_desde_último_intake > 9 → alerta
```

Si los datos dejan de llegar, el modelo se entrena con información cada vez más antigua y los pronósticos pierden precisión sin que el sistema lo note. La detección temprana permite que el operador contacte al cliente antes de que el impacto llegue al pronóstico.

### P6 — Cálculo de los 6 KPIs internos de Triple S

**Ejecutado en:** Ciclo mensual

Los KPIs se calculan sobre la población completa de clientes activos (DEC-023):

**KPI 1 — Tasa de conversión onboarding → activo**
```
clientes que pasaron a estado 'activo' en los últimos 90 días
────────────────────────────────────────────────────────────
clientes que iniciaron onboarding en los últimos 90 días
```
Meta: > 80%. Una tasa baja indica problemas en el mes 1 o en la entrega del primer diagnóstico.

**KPI 2 — Tiempo promedio al primer pronóstico**
```
promedio( predictor_complete_first - onboarding_start_date )
sobre clientes que completaron su primer pronóstico en los últimos 90 días
```
Meta: ≤ 60 días (máximo mes 3, DEC-004). Un promedio alto indica cuellos de botella en la ingesta o en el entrenamiento.

**KPI 3 — Tasa de retención mensual**
```
clientes activos al cierre del mes
───────────────────────────────────
clientes activos al inicio del mes
```
Meta: > 95% mensual. La inversa es el churn rate.

**KPI 4 — Evolución promedio del ISD por cohorte**

Para clientes que llevan 1, 3 y 6 meses en el sistema:
```
ISD promedio de la cohorte en el mes 1
ISD promedio de la cohorte en el mes 3
ISD promedio de la cohorte en el mes 6
```
Meta: ISD creciente mes a mes. Si el ISD no mejora, el trabajo de diagnóstico mensual no está generando cambios en el cliente.

**KPI 5 — MAPE real vs. comprometido**
```
clientes con MAPE_real ≤ umbral_SLA este mes
─────────────────────────────────────────────
total de clientes con SLA de precisión activo (ISD ≥ 70%)
```
Meta: > 90% de los clientes dentro del SLA de precisión.

**KPI 6 — Distribución de clientes por plan**
```
{
  mensual:    N clientes (X%)
  trimestral: N clientes (X%)
  anual:      N clientes (X%)
}
```
No tiene una meta de porcentaje fija — es informativo para la estrategia comercial. Triple S quiere tendencia hacia planes más largos (mejor flujo de caja).

### P7 — Generación del reporte mensual de monitoreo

El harness consolida todos los resultados en un reporte interno de Triple S:

```
tenants/internal/monitoring/
└── {YYYY_MM}/
    ├── monitoring_report.json    ← Datos completos para el portal interno
    └── monitoring_summary.pdf   ← Resumen ejecutivo para el equipo Triple S
```

**Contenido del reporte:**
- MAPE real por cliente: tabla con estado verde/rojo vs. SLA
- Clientes con drift detectado: lista con causa probable
- Alertas de pipeline activas: harness, severidad, cliente afectado
- 6 KPIs del período con tendencia vs. mes anterior
- Clientes en riesgo (mora, suspendidos, próximos a cancelar)

### P8 — Actualización del portal interno de Triple S

El portal interno (Streamlit en Fase 2, FastAPI + React en Fase 3) consume las tablas que este harness actualiza:

| Tabla | Contenido |
|-------|-----------|
| `mape_history` | MAPE real por cliente × período × combinación |
| `drift_flags` | Combinaciones con drift activo y su causa probable |
| `pipeline_health` | Estado de cada harness por cliente: último run, latencia, status |
| `kpis_monthly` | Los 6 KPIs del mes con serie histórica |
| `sla_compliance` | Estado de cumplimiento de SLA por cliente y período |

### P9 — Emisión de alertas al equipo de Triple S

Las alertas no van al cliente — van al operador de Triple S. Los canales:

| Canal | Cuándo |
|-------|--------|
| Notificación en portal interno | Toda alerta Media, Alta y Crítica |
| Correo al operador | Alertas Altas y Críticas |
| Correo al lead técnico | Alertas Críticas solamente |

---

## Salidas

### Archivos generados

| Archivo | Descripción | Destino |
|---------|-------------|---------|
| `monitoring_report.json` | Reporte completo: MAPE real, drift, salud, KPIs | `tenants/internal/monitoring/{YYYY_MM}/` |
| `monitoring_summary.pdf` | Resumen ejecutivo del mes para el equipo Triple S | `tenants/internal/monitoring/{YYYY_MM}/` |

### Registros actualizados en base de datos

| Tabla | Actualización |
|-------|--------------|
| `mape_history` | MAPE real por combinación × período |
| `drift_flags` | Upsert de combinaciones con drift activo |
| `pipeline_health` | Estado de salud de cada harness por cliente |
| `kpis_monthly` | 6 KPIs del mes |
| `sla_compliance` | Estado de cumplimiento por cliente |
| `sla_violations` | Violaciones de MAPE real (si ocurrieron) |

---

## Condiciones de completitud

El harness 045 se considera **completo por ciclo mensual** cuando:

1. El MAPE real fue calculado para todos los clientes con pronóstico del período anterior
2. La comparación contra SLA fue evaluada y registrada
3. La detección de drift fue ejecutada sobre las últimas 6 observaciones
4. Los 6 KPIs del mes fueron calculados y registrados
5. El `monitoring_report.json` y el PDF existen en Storage
6. Las tablas de monitoreo en base de datos están actualizadas
7. Las alertas correspondientes fueron enviadas

---

## Lo que este harness NO hace

- No genera pronósticos ni modifica modelos
- No entrega ningún resultado al cliente — todo va al equipo interno de Triple S
- No corrige datos ni re-ejecuta harnesses fallidos — detecta y alerta; el operador decide la acción
- No gestiona pagos ni estados de clientes

---

## Dependencias

| Tipo | Harness / Sistema | Detalle |
|------|-------------------|---------|
| Datos | Todos los harnesses anteriores | Lee tablas de log y resultados de 015, 020, 025, 030, 035, 040, 050 |
| Posterior | 055 Command | Consume `kpis_monthly` y `sla_compliance` para el portal de operaciones internas |
| Externo | SendGrid | Envío de alertas al equipo de Triple S |

---

## Notas de diseño

- **MAPE real vs. MAPE de holdout:** 030 Trainer calcula el MAPE sobre datos históricos retenidos — es una estimación de la calidad del modelo antes de desplegarlo. 045 Monitor calcula el MAPE real sobre demanda observada vs. pronóstico publicado — es la medida de cumplimiento del SLA. Solo el segundo tiene consecuencias contractuales.
- **Monitoreo de drift como señal preventiva:** La deriva de un modelo es gradual. Detectarla en el mes 2 o 3 de tendencia creciente permite a Triple S reentrenar con una estrategia diferente antes de que el cliente note la pérdida de precisión. Sin este harness, el deterioro solo se descubre cuando el cliente se queja — demasiado tarde.
- **El harness no actúa — alerta:** 045 Monitor es observador, no actuador. Cuando detecta que 030 Trainer produce modelos de mala calidad, no los rechaza ni vuelve a entrenar — alerta al operador. Esto es una decisión de diseño deliberada: las acciones correctivas en ML requieren juicio humano sobre si el problema es de datos, de modelo o de cambio estructural en el negocio del cliente.
- **Los 6 KPIs alimentan la estrategia comercial de Triple S:** El KPI de distribución por plan (KPI 6) guía las decisiones de precio. El KPI de ISD por cohorte (KPI 4) mide si el servicio de diagnóstico realmente mejora la calidad de datos del cliente. El KPI de conversión (KPI 1) es la señal más temprana de si el onboarding está funcionando.

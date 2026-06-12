---
name: discovery-rubric
description: Rúbrica de evaluación de 7 dimensiones con anclas few-shot para la Instancia C
  del harness 010 Discovery de FARO. Define los criterios de scoring por dimensión (0.0, 0.5,
  1.0), las reglas de veto automático (D4, D5, D7), el gate de aprobación (≥ 0.80) y cuatro
  ejemplos globales calibrados (scores 0.2, 0.5, 0.8, 1.0). Usar cuando discovery-evaluator
  aplica la rúbrica a los artefactos del harness 010.
user-invocable: false
---

## Propósito de esta skill

Proporciona al evaluador (Instancia C) todos los criterios de scoring necesarios para
auditar la ejecución completa del harness 010 Discovery de forma objetiva y reproducible.

**Regla de uso:** Cargar esta skill ANTES de leer cualquier artefacto. Los criterios aquí
definen qué buscar — no al revés.

---

## Resumen de dimensiones

| ID | Dimensión | Artefacto principal | ¿Veto? |
|----|-----------|--------------------|---------| 
| D1 | Completitud de campos | `session_data.json` | No |
| D2 | Consistencia ITO-Categoría | `analysis_report.json` | No |
| D3 | Cold start documentado | `analysis_report.json` | No |
| D4 | Registros BD creados | `010_discovery/db_records/*.json` | **Sí** |
| D5 | Storage del tenant creado | `010_discovery/storage_local/tenants/` | **Sí** |
| D6 | Guía de datos generada y entregada | `010_discovery/data_intake_guide.md` | No |
| D7 | Evento de cierre emitido | `600_persistence/events/onboarding_discovery_complete.json` | **Sí** |

**Gate de aprobación:** promedio de D1–D7 ≥ 0.80 **y** ningún veto activo.

---

## Reglas de veto automático

Un veto convierte el veredicto en `REJECTED` sin importar el promedio:

- **Veto D4** — `db_records/clients.json` no existe → sin identidad del cliente en el sistema, el onboarding no puede continuar.
- **Veto D5** — Carpeta del tenant no existe → los harnesses 015 y 020 no tienen dónde escribir los datos.
- **Veto D7** — `onboarding_discovery_complete.json` no existe o `tenant_id` es nulo → el harness 015 Intake nunca se activa.

Cuando se activa un veto: registrar en `vetos_activos` dentro de `verdict.json` y en la sección `major` de hallazgos.

---

## D1 — Completitud de campos

**Artefacto:** `010_discovery/session_data.json`

**Qué verificar:** Que todos los campos obligatorios existen, no son nulos y no tienen
el valor `"MISSING"`.

### Campos obligatorios a revisar

| Campo | Tipo esperado |
|-------|--------------|
| `razon_social` | string no vacío |
| `sector` | string no vacío |
| `contacto_principal.nombre` | string no vacío |
| `contacto_principal.correo` | string con `@` |
| `contacto_principal.telefono` | string no vacío |
| `responsable_pagos.nombre` | string no vacío |
| `responsable_pagos.correo` | string con `@` |
| `skus_activos` | entero > 0 |
| `clientes_xyz` | entero > 0 |
| `pedidos_por_mes` | entero > 0 |
| `anios_historial` | número > 0 |
| `modo_ingesta` | `"Batch"` o `"Incremental"` |
| `horizonte_pronostico` | `"días"`, `"semanas"`, `"meses"` o `"múltiples meses"` |
| `jerarquia_producto` | array con al menos 1 elemento |
| `jerarquia_geografica` | array con al menos 1 elemento |
| `tiene_esquema2` | `true` o `false` |
| `plan_suscripcion` | `"Mensual"`, `"Trimestral"` o `"Anual"` |
| `criterios_exito` | array con al menos 1 elemento |

**Campo condicional:**

| Campo | Condición |
|-------|-----------|
| `frecuencia_incremental` | Obligatorio si `modo_ingesta == "Incremental"` |

### Anclas D1

| Score | Criterio |
|-------|----------|
| **1.0** | Todos los campos obligatorios presentes, no nulos, sin ningún `"MISSING"`. Campos condicionales también presentes cuando aplican. |
| **0.5** | Entre 1 y 3 campos obligatorios marcados como `"MISSING"`, pero con razón documentada en `campos_missing` y registro de escalamiento en `harness-state.json`. Ningún campo es un bloqueante ITO (`skus_activos`, `clientes_xyz`, `pedidos_por_mes`, `anios_historial`). |
| **0.0** | Al menos 1 campo obligatorio ausente (no existe en el JSON), nulo sin registro, o `"MISSING"` sin escalamiento. O algún campo ITO bloqueante faltante. |

---

## D2 — Consistencia ITO-Categoría

**Artefacto:** `010_discovery/analysis_report.json`

**Qué verificar:** Que el campo `categoria.confirmada` es consistente con `ito.ito_calculado`
según los umbrales provisionales. Si hubo discrepancia, que fue escalada y resuelta.

### Umbrales ITO (escala normalizada 0–100, provisional hasta T-030)

| Rango ITO calculado | Categoría esperada |
|---------------------|--------------------|
| ITO ≤ 33.00 | M |
| 33.01 – 66.00 | L |
| ITO > 66.00 | XL |

> El ITO usa normalización: `norm = min(valor / max_ref, 1.0) × 100` para cada componente,
> luego `ITO = 0.40 × norm_skus + 0.35 × norm_clientes + 0.25 × norm_pedidos`.
> Ver `discovery-analysis-schema` para las referencias máximas y pesos provisionales.

### Lectura del campo de discrepancia

El `analysis_report.json` expone `categoria.discrepancia` con tres valores posibles:
- `"ninguna"` — `calculada == comercial`
- `"advertencia"` — diferencia de 1 nivel (M↔L o L↔XL)
- `"critica"` — diferencia de 2 niveles (M↔XL), `discrepancia_critica: true`

### Anclas D2

| Score | Criterio |
|-------|----------|
| **1.0** | `categoria.confirmada` es consistente con los umbrales y el ITO calculado. O bien: hubo discrepancia pero `discrepancia_critica: true` fue escalada, el operador resolvió y el ajuste está documentado en `harness-state.json` bajo `escalations`. |
| **0.5** | Discrepancia de exactamente 1 nivel detectada (`discrepancia: "advertencia"`). La categoría confirmada difiere de la calculada pero la resolución no está documentada en `harness-state.json`. |
| **0.0** | `categoria.confirmada` no coincide con los umbrales ITO en 2 niveles sin evidencia de escalamiento. O `ito.ito_calculado` es null (ITO no fue calculado). |

---

## D3 — Cold start documentado

**Artefacto:** `010_discovery/analysis_report.json`

**Qué verificar:** Que el nivel de confianza cold start está asignado y, si el historial
es menor a 1 año, el paso de cascada aplicable está especificado.

### Tabla de niveles válidos

| Valor `cold_start.codigo` | Valor `cold_start.nivel` | Condición de aplicación |
|---------------------------|--------------------------|------------------------|
| `CS-ALTA` | `"Alta"` | `anios_historial ≥ 3` |
| `CS-ESTANDAR` | `"Estándar"` | `2 ≤ anios_historial < 3` |
| `CS-REDUCIDA` | `"Reducida"` | `1 ≤ anios_historial < 2` |
| `CS-EXPERIMENTAL` | `"Experimental"` | `anios_historial < 1` |

### Regla de cascada

Si `codigo == "CS-EXPERIMENTAL"`: `cascada_paso` debe ser 1, 2 o 3 (no null) y
`cascada_descripcion` debe ser un string no vacío.

En Fase 1 se espera `cascada_paso: 3` como valor activo.

### Caso de cold start inviable

Si `cold_start.inviable == true` (historial < 3 meses): verificar que existe registro de
escalamiento en `harness-state.json` bajo `escalations`. Sin ese registro, el análisis
no está completo.

### Anclas D3

| Score | Criterio |
|-------|----------|
| **1.0** | `codigo` y `nivel` tienen valores válidos y coherentes con `anios_historial`. Si `CS-EXPERIMENTAL`, `cascada_paso` y `cascada_descripcion` están especificados. Si `inviable: true`, hay escalamiento registrado. |
| **0.5** | Nivel asignado y válido, pero falta `cascada_paso` cuando `codigo == "CS-EXPERIMENTAL"`. O `inviable: true` sin registro de escalamiento. |
| **0.0** | `cold_start.codigo` o `cold_start.nivel` son null, vacíos o tienen valores no reconocidos. |

---

## D4 — Registros BD creados ⚠️ VETO

**Artefactos:** `010_discovery/db_records/clients.json`, `contacts.json`, `client_config.json`, `subscriptions.json`

**Qué verificar:** Los 4 archivos existen y contienen los campos mínimos requeridos.

### Campos mínimos por archivo

**`clients.json`** — campos mínimos:
`tenant_id` (no vacío), `razon_social` (no vacío), `categoria` (`M`, `L` o `XL`),
`estado` (debe ser `"onboarding"`), `fecha_inicio_onboarding` (no vacío), `plan_suscripcion` (no vacío)

**`contacts.json`** — campos mínimos:
`tenant_id` (no vacío), al menos un contacto de tipo `"principal"` con `nombre` y `correo`

**`client_config.json`** — campos mínimos:
`tenant_id` (no vacío), `modo_ingesta` (`"Batch"` o `"Incremental"`), `horizonte_pronostico` (no vacío)

**`subscriptions.json`** — campos mínimos:
`tenant_id` (no vacío), `plan` (no vacío), `monto_mensual_efectivo_usd` (número > 0),
`fecha_primer_cobro` (no vacío), `estado` (debe ser `"onboarding_gratuito"`)

### Consistencia global del `tenant_id` (fuente única — DEC-047)

El `tenant_id` lo genera **una sola vez** el governor en E10-A y lo persiste en
`600_persistence/harness-state.json`. **Todos** los artefactos del harness deben usar ese
mismo valor (el slug), **nunca** la razón social ni un valor regenerado. Tomar el
`tenant_id` de `harness-state.json` como referencia y verificar que coincide **exactamente**
(carácter por carácter) en cada uno de estos artefactos:

| Artefacto | Campo |
|-----------|-------|
| `600_persistence/harness-state.json` | `tenant_id` (referencia) |
| `010_discovery/support/synthesis_report.json` | `tenant_id` |
| `010_discovery/support/open_questions.json` | `tenant_id` |
| `010_discovery/support/session_data.json` | `tenant_id` |
| `010_discovery/support/analysis_report.json` | `tenant_id` |
| `010_discovery/deliverables/client_profile.json` | `tenant_id` |
| `010_discovery/db_records/*.json` | `tenant_id` (los 4) |
| `600_persistence/events/onboarding_discovery_complete.json` | `tenant_id` |

Una divergencia frecuente y específica a vigilar: que un artefacto de `support/`
(`synthesis_report.json` u `open_questions.json`) lleve la **razón social** en vez del slug
— ese es el defecto que motivó esta verificación. Detectarlo aunque los artefactos
canónicos (db_records, evento) sí sean consistentes.

### Anclas D4

| Score | Criterio |
|-------|----------|
| **1.0** | Los 4 archivos BD existen con todos los campos mínimos requeridos presentes y no nulos, **y** el `tenant_id` coincide exactamente con el de `harness-state.json` en TODOS los artefactos de la tabla de consistencia global (incluidos los de `support/`). |
| **0.5** | 3 de los 4 archivos BD existen con campos completos (el faltante tiene registro de fallo en `execution-state.json` bajo `worker_errors`, `clients.json` existe). **O** los 4 BD están completos y consistentes pero un artefacto de `support/` lleva un `tenant_id` divergente de `harness-state.json` (p. ej. la razón social). |
| **0.0** | `clients.json` no existe. O menos de 3 archivos BD existen. O el `tenant_id` diverge en un artefacto **canónico** (db_records o evento). → **VETO AUTOMÁTICO.** |

---

## D5 — Storage del tenant creado ⚠️ VETO

**Artefacto:** `1000_storage_local/tenants/{tenant_id}/` (Fase 1) o Supabase Storage (Fase 3)

**Qué verificar:** La carpeta del tenant existe con las 6 subcarpetas obligatorias.

### Subcarpetas obligatorias

`1000_data/005_bronze/`, `1000_data/007_silver/`, `1000_data/009_gold/`, `1010_models/`, `1020_forecasts/`, `1030_exports/`

**Cómo obtener el `tenant_id`:** leer `010_discovery/deliverables/client_profile.json` campo `tenant_id`.

**En Fase 1:** verificar existencia de `1000_storage_local/tenants/{tenant_id}/` y sus 6 subdirectorios.

**En Fase 3:** verificar el path en Supabase Storage indicado en `execution-state.json` bajo `artifacts.storage_tenant`.

### Anclas D5

| Score | Criterio |
|-------|----------|
| **1.0** | La carpeta del tenant existe con las 6 subcarpetas. |
| **0.5** | La carpeta existe pero le faltan 1 o 2 subcarpetas. Las subcarpetas faltantes tienen registro en `execution-state.json`. |
| **0.0** | La carpeta del tenant no existe. → **VETO AUTOMÁTICO.** |

---

## D6 — Guía de datos generada y entregada

**Artefacto:** `010_discovery/data_intake_guide.md`

**Qué verificar:** El archivo existe, está personalizado con los datos reales del cliente
y no contiene jerga técnica ni marcadores sin reemplazar.

### Criterios de personalización

El archivo debe contener el nombre del cliente (razón social) y no debe tener ninguno de
estos indicadores de plantilla sin reemplazar: `{razon_social}`, `{SECCION_ESQUEMA2}`,
`{SECCION_MODO_INGESTA}`, `{frecuencia_incremental}`, `{fecha_generacion}`.

### Palabras prohibidas (jerga técnica)

El archivo **no debe contener** ninguna de estas palabras o siglas:
`ITO`, `Bronze`, `Silver`, `Gold`, `medallón`, `pipeline`, `Supabase`, `DuckDB`,
`Prefect`, `RLS`, `tenant`, `harness`, `worker`, `orquestador`, `MAPE`, `ISD`.

### Verificación de envío

- Fase 3 con SendGrid: verificar que no existe `600_persistence/pending_email.json` (o `_pendiente_envio: false`).
- Fase 1: verificar que existe `600_persistence/pending_email.json` con `_pendiente_envio: true` y `adjunto` apuntando a la guía.

### Anclas D6

| Score | Criterio |
|-------|----------|
| **1.0** | Archivo existe, personalizado (razón social presente, sin marcadores sin reemplazar), sin jerga técnica, y hay confirmación de envío por correo (Fase 3) o registro de pendiente manual (Fase 1). |
| **0.5** | Archivo existe y está personalizado, pero no hay confirmación de envío ni registro de pendiente manual. O el archivo existe pero contiene 1–2 palabras de jerga técnica no bloqueante. |
| **0.0** | Archivo no existe. O contiene marcadores sin reemplazar (`{...}`). O contiene jerga técnica abundante que hace la guía incomprensible para el cliente. |

---

## D7 — Evento de cierre emitido ⚠️ VETO

**Artefacto:** `600_persistence/events/onboarding_discovery_complete.json`

**Qué verificar:** El archivo existe y contiene los tres campos obligatorios con valores válidos.

### Campos obligatorios del evento

| Campo | Valor esperado |
|-------|---------------|
| `event` | `"onboarding_discovery_complete"` (literal exacto) |
| `tenant_id` | string no vacío, debe coincidir con el `tenant_id` de `client_profile.json` |
| `timestamp` | string en formato ISO 8601 (`YYYY-MM-DDTHH:mm:ssZ`) |
| `next_harness` | `"015_intake"` |

### Anclas D7

| Score | Criterio |
|-------|----------|
| **1.0** | Archivo existe con los 4 campos presentes, `tenant_id` no vacío y coincide con `client_profile.json`, `timestamp` en formato ISO 8601, `next_harness` correcto. |
| **0.5** | Archivo existe y `tenant_id` es válido, pero falta `next_harness` o el `timestamp` no es ISO 8601 válido. |
| **0.0** | Archivo no existe. O `tenant_id` es nulo o vacío. → **VETO AUTOMÁTICO.** |

---

## Fórmula de scoring global

```
score_global = (D1 + D2 + D3 + D4 + D5 + D6 + D7) / 7
```

Todos los pesos son iguales (1/7 cada dimensión).

### Determinación del veredicto

```
Si (D4 == 0.0) OR (D5 == 0.0) OR (D7 == 0.0):
    veredicto = REJECTED   ← veto — no importa el promedio

Si score_global >= 0.80:
    veredicto = APPROVED
Si score_global < 0.80:
    veredicto = REJECTED
```

---

## Anclas globales few-shot (ejemplos completos)

### Score global ≈ 0.20 — Ejecución fallida desde el inicio

**Perfil:** La sesión no fue completada. El analyst y el configurator no se ejecutaron.

- D1 = 0.0 — Solo nombre y contacto capturados. Faltan SKUs, clientes XYZ, pedidos y modos de ingesta. Ningún campo ITO disponible.
- D2 = 0.0 — `analysis_report.json` no existe. ITO no calculado.
- D3 = 0.0 — Nivel cold start ausente.
- D4 = 0.0 — Ningún archivo en `db_records/`. **VETO activo.**
- D5 = 0.0 — Carpeta del tenant no existe. **VETO activo.**
- D6 = 0.0 — Guía no generada.
- D7 = 0.0 — Evento no emitido. **VETO activo.**

> Score global: (0+0+0+0+0+0+0)/7 = **0.00** → REJECTED (3 vetos activos)

**Diagnóstico típico:** La sesión con el cliente fue interrumpida o el interviewer no terminó.
El governor nunca llegó al analyst ni al configurator.

---

### Score global ≈ 0.50 — Análisis correcto, configuración incompleta

**Perfil:** La sesión fue completa y el análisis fue correcto, pero el configurator falló
a mitad del Modo COMMIT.

- D1 = 1.0 — Todos los campos obligatorios capturados correctamente en `session_data.json`.
- D2 = 1.0 — ITO calculado = 28.40 → categoría M. La comercial era M. Sin discrepancia.
- D3 = 1.0 — Historial = 2.1 años → CS-ESTANDAR. Sin cascada requerida.
- D4 = 0.5 — `clients.json` y `contacts.json` existen. Faltan `client_config.json` y `subscriptions.json`. El fallo está registrado en `execution-state.json`.
- D5 = 0.0 — Carpeta del tenant no existe. **VETO activo.**
- D6 = 0.5 — La guía existe y está personalizada, pero no hay registro de envío ni pendiente.
- D7 = 0.0 — Evento no emitido. **VETO activo.**

> Score global: (1.0+1.0+1.0+0.5+0.0+0.5+0.0)/7 = **0.57** → REJECTED (2 vetos activos)

**Diagnóstico típico:** El configurator completó el Modo DRAFT y el operador aprobó, pero el
Modo COMMIT falló después de crear los primeros dos registros BD. El flujo quedó incompleto.

---

### Score global ≈ 0.80 — Flujo completo con entrega de guía sin confirmación

**Perfil:** Todo el flujo se completó correctamente. El único gap es que la guía existe
pero no hay registro de envío por correo ni pendiente manual documentado.

- D1 = 1.0 — Todos los campos obligatorios presentes y válidos.
- D2 = 1.0 — ITO calculado = 54.20 → categoría L. La comercial era L. Sin discrepancia.
- D3 = 1.0 — Historial = 1.3 años → CS-REDUCIDA. Sin cascada requerida (umbral 1 año).
- D4 = 1.0 — Los 4 archivos BD existen con todos los campos mínimos.
- D5 = 1.0 — Carpeta del tenant con las 6 subcarpetas verificadas.
- D6 = 0.5 — Guía existe y personalizada, sin marcadores ni jerga. Pero `correo_pendiente.json` no existe y no hay confirmación de envío.
- D7 = 1.0 — Evento emitido con `tenant_id`, `timestamp` ISO 8601 y `next_harness` correctos.

> Score global: (1.0+1.0+1.0+1.0+1.0+0.5+1.0)/7 = **0.93** → APPROVED (sin vetos)

**Diagnóstico típico:** Ejecución sólida. El gap en D6 es menor: la guía está generada pero
el operador debe confirmar que fue enviada al cliente por otro canal.

---

### Score global = 1.00 — Ejecución perfecta

**Perfil:** Todos los artefactos completos, sin discrepancias, guía enviada con confirmación,
evento correctamente emitido.

- D1 = 1.0 — 18 campos obligatorios capturados. Ningún `"MISSING"`. `frecuencia_incremental` presente porque `modo_ingesta == "Incremental"`.
- D2 = 1.0 — ITO calculado = 21.95 (skus=120, clientes=18, pedidos=380). Categoría M confirmada. Comercial era M. Ninguna discrepancia.
- D3 = 1.0 — Historial = 2.5 años → CS-ESTANDAR. Sin cascada. `cascada_paso: null` correcto.
- D4 = 1.0 — Los 4 archivos BD: `clients` (tenant_id + estado=onboarding + categoría=M), `contacts` (principal + pagos), `client_config` (modo=Incremental + frecuencia=Semanal + horizonte=meses), `subscriptions` (monto=350 USD + primer_cobro fechado).
- D5 = 1.0 — `1000_storage_local/tenants/alimentos-abc-3207/` con 6 subcarpetas: `1000_data/005_bronze`, `1000_data/007_silver`, `1000_data/009_gold`, `1010_models`, `1020_forecasts`, `1030_exports`.
- D6 = 1.0 — `data_intake_guide.md` personalizado con "Alimentos ABC S.A.", sin marcadores ni jerga técnica. `600_persistence/pending_email.json` con `_pendiente_envio: true` (Fase 1 — registrado correctamente).
- D7 = 1.0 — `onboarding_discovery_complete.json` con `tenant_id: "alimentos-abc-3207"`, `timestamp: "2026-06-08T15:32:07Z"`, `next_harness: "015_intake"`.

> Score global: (1.0+1.0+1.0+1.0+1.0+1.0+1.0)/7 = **1.00** → APPROVED (sin vetos)

---

## Clasificación de hallazgos

Todos los hallazgos se reportan en `verdict.json` bajo `hallazgos`:

**Major** (score < 0.5 en la dimensión o veto activo):
- Cualquier dimensión con score 0.0
- Veto activo (D4, D5 o D7 = 0.0)
- Campo ITO ausente o nulo
- `tenant_id` nulo o inconsistente entre artefactos

**Minor** (score 0.5–0.79 en la dimensión):
- Campo obligatorio MISSING con escalamiento documentado
- Discrepancia de categoría de 1 nivel resuelta
- Guía existente sin confirmación de envío
- Subcarpeta de storage faltante con registro de error

---

## Nota sobre evolución de la rúbrica

Los **umbrales ITO** (M ≤ 33, L ≤ 66, XL > 66) y los **pesos de normalización** son
provisionales hasta que T-030 calibre los valores definitivos con datos del primer piloto.
Cuando T-030 se cierre, actualizar esta skill y `discovery-analysis-schema/SKILL.md`
de forma coordinada antes de ejecutar cualquier evaluación posterior.

# Plan de Construcción — 015 Intake Harness
## Harness Forecaster — Sabbia Solutions & Software

**Tipo de harness:** Pipeline (determinístico)
**Bloque de construcción:** A (posición 2 de 11)
**Hito:** A — Primer piloto ejecutable
**Disparador:** El cliente entrega su(s) archivo(s) de datos al sistema, existiendo ya el evento `onboarding_discovery_complete` del 010

---

### Checklist de completitud

El harness completo debe contener estas 7 secciones:
- [x] Sección 1 — Fase 0: Definición Estructural
- [x] Sección 2 — Fase 1: Diseño Agéntico (6 sub-secciones)
- [x] Sección 3 — Sprint Contract (plantilla)
- [x] Sección 4 — Rúbrica de Evaluación (con few-shot y anclas)
- [x] Sección 5 — Handoff Artifact → 020 Diagnosis + 025 Refinery (fan-out paralelo)
- [x] Sección 6 — Flujo del Arnés (12.1–12.5)
- [x] Sección 7 — Notas de Construcción

> **Nota de diseño rectora (E4 + P6).** El 015 es un **pipeline determinístico**, no un harness de razonamiento como el 010. La estructura A/B/C de gobernanza se mantiene (contrato, ejecución, auditoría independiente), pero el peso de cada instancia cambia: el trabajo del Worker es **código testeable con TDD real**, no juicio LLM. El LLM interviene solo en los pocos puntos de ambigüedad genuina (encoding/delimitador no resueltos, hoja/cabecera de Excel, redacción del reporte). El esfuerzo se mueve de "razonamiento agéntico" a **rigor de validación + cobertura de casos de prueba**. Ver DEC-057.

---

## Sección 1 — Fase 0: Definición Estructural

### Propósito

Recibir el/los archivo(s) de datos del cliente, validar que tienen la estructura mínima requerida, y crear la copia **Bronce** — exacta e inmutable — de los datos originales. A partir de este momento el sistema tiene datos con qué trabajar. Lo que entra aquí es lo más cercano posible a la realidad del cliente: **nada se corrige, nada se interpreta**. El 015 es el guardián de la verdad cruda; corregir es trabajo exclusivo del 025 Refinery, y medir la salud es del 020 Diagnosis.

### Inputs

**Del sistema (generados por 010 Discovery):**

| # | Input | Descripción | Fuente |
|---|-------|-------------|--------|
| I-1 | `client_config` | Modo de ingesta (batch/incremental), frecuencia, `tiene_esquema2`, jerarquías, historial declarado | 010 — tabla `client_config` / `onboarding_config.json` |
| I-2 | Evento `onboarding_discovery_complete` | Señal de que el sistema está listo para recibir datos de este tenant | 010 — `600_persistence/events/` |
| I-3 | Carpeta del tenant en Storage | `tenants/{tenant_id}/.../005_bronze/` ya creada por el 010 | 010 — Storage |
| I-4 | Huella de formato (si existe) | Hoja/cabecera/delimitador/encoding de entregas previas | `client_config` (escrita por el 015 en la 1ª entrega) |

**Del cliente (snapshot tabular — ver costura de adaptador, §7):**

| Input | Descripción | Obligatorio | Formatos aceptados |
|-------|-------------|-------------|--------------------|
| Archivo Esquema 1 | Historial de pedidos (DEC-014) | **Sí** | CSV (delim. `,` `;` `\|`), Excel `.xlsx` / `.xls` |
| Archivo Esquema 2 | Producción e inventario de ABC (DEC-014) | Solo si `tiene_esquema2 = true` | Igual que Esquema 1 |

**Campos mínimos — Esquema 1 (rechazo de estructura si falta alguno):** `fecha_pedido`, `id_cliente`, `id_producto`, `cantidad_solicitada`.
**Campos ideales — Esquema 1 (no rechazan; alimentan el ISD del 020):** hasta 17 campos (DEC-014) — precio unitario, cantidad entregada, fechas de entrega prometida/real, motivo de cancelación, región, sede, categoría, etc.
**Campos mínimos — Esquema 2 (rechazo si Esquema 2 activo y se entrega el archivo):** `fecha`, `id_producto`, `cantidad_producida`, `stock_disponible`, `costo_unitario`, `stock_minimo`.

### Proceso (P1–P8)

1. **P1 — Recepción y detección de formato.** El adaptador de fuente entrega el snapshot tabular (en Fase 1: el operador deja el archivo en la carpeta del tenant). El worker detecta formato (CSV/Excel), **delimitador** (`,` `;` `\|`) y **encoding** (utf-8 → utf-8-sig → cp1252/latin-1). Para Excel, resuelve hoja y fila de cabecera (huella de formato o confirmación del operador — ver §2.4). Archivo no-CSV/Excel, vacío o corrupto → **rechazo inmediato**.
2. **P2 — Validación de estructura (GATE).** Verifica los campos mínimos del esquema correspondiente. Falta ≥ 1 campo mínimo → **rechazo** (genera `intake_rejection.json`, no se crea Bronce). Todos presentes → continúa. Los campos ideales faltantes se registran como déficit, no detienen.
3. **P3 — Validación de tipos (no detiene).** Por cada campo mínimo verifica coherencia de tipo (`fecha_pedido` parseable, `id_cliente`/`id_producto` texto no vacío, `cantidad_solicitada` numérico ≥ 0). Los errores se **cuentan** y registran en `intake_report.json`; alimentan el ISD del 020. No detienen el proceso.
4. **P4 — Detección de duplicados.** Clave compuesta `(fecha_pedido, id_cliente, id_producto)`. **Batch:** duplicados internos se registran como anomalía, **no se eliminan** (se copian a Bronce; el 020 los contabiliza en Unicidad). **Incremental:** además compara contra la unión lógica del Bronce acumulado (vía `_manifest.json`); registros ya existentes se excluyen, solo los nuevos se persisten en el archivo de esta entrega.
5. **P5 — Evaluación del rango temporal.** Calcula fecha mínima/máxima, días cubiertos, y compara contra el historial declarado en el 010. Diferencia > 20% → se registra como `warning` en `intake_report.json`. No detiene.
6. **P6 — Creación de la copia Bronce (write-once).** Tras superar P2, escribe Bronce: **Batch** = archivo completo tal cual se recibió; **Incremental** = un archivo nuevo e inmutable por entrega, con `timestamp` propio. Calcula **SHA-256** de cada archivo. Actualiza `_manifest.json`. Bronce es **inmutable**: ningún harness posterior escribe en `005_bronze/`. (Decisiones e/f — DEC-057.)
7. **P7 — Generación del reporte de ingesta.** Produce `intake_report.json` (conteos, rango de fechas, encoding/delimitador detectados, errores de tipo, duplicados, campos ideales faltantes, warnings) y la fila de `intake_log` (con `files` JSONB: path + sha256 + rows + date_range por archivo).
8. **P8 — Emisión del evento (ÚLTIMO paso = checkpoint canónico).** Solo cuando Bronce está completo y verificado, emite `intake_complete` apuntando a `bronze_path`, `manifest_path`, `intake_report_path` y `next_harnesses: [020_diagnosis, 025_refinery]`. Si algo falla antes de P8, **no hay evento** → los consumidores nunca arrancan sobre datos parciales.

### Outputs (artefactos)

| Artefacto | Path | Descripción |
|-----------|------|-------------|
| Copia Bronce Esquema 1 | `…/tenants/{id}/1000_data/005_bronze/orders_{batch\|incremental}_{YYYYMMDD}.csv` | Réplica exacta e inmutable del archivo de pedidos |
| Copia Bronce Esquema 2 | `…/005_bronze/inventory_{batch}_{YYYYMMDD}.csv` | Réplica exacta (si Esquema 2 activo y entregado) |
| `_manifest.json` | `…/005_bronze/_manifest.json` | Registro autoritativo de entregas: archivo, esquema, sha256, rango, timestamp |
| `intake_report.json` | `…/005_bronze/intake_report.json` | Reporte cuantificado de la entrega |
| Fila `intake_log` | tabla `intake_log` (Fase 1: JSON local `_pendiente_supabase: true`) | Metadatos consultables de la entrega, `files` JSONB |
| Actualización `tenants.last_intake_at` | tabla `tenants` | Timestamp de la última ingesta |

**Evento disparado al completarse:**
```
EVENT: intake_complete
  tenant_id        : {id}
  delivery_id      : {YYYYMMDD}
  mode             : batch | incremental
  timestamp        : {ISO-8601}
  bronze_path      : …/005_bronze/
  manifest_path    : …/005_bronze/_manifest.json
  intake_report_path: …/005_bronze/intake_report.json
  next_harnesses   : [020_diagnosis, 025_refinery]   ← corren en PARALELO (DEC-024)
```

### Criterio de Done

El harness 015 se considera **completo** cuando:
1. El archivo pasó la validación de estructura (P2) — o fue rechazado con `intake_rejection.json` y notificación al operador.
2. La validación de tipos (P3) fue ejecutada y sus resultados registrados.
3. La detección de duplicados (P4) fue ejecutada y sus resultados registrados.
4. La copia Bronce existe en Storage, es **bit-exacta** a la entrada y es inmutable (SHA-256 calculado y persistido).
5. El `_manifest.json` y el `intake_report.json` existen junto al Bronce.
6. La fila de `intake_log` fue creada y `tenants.last_intake_at` actualizado.
7. El evento `intake_complete` fue emitido como último paso, con payload completo.

### Tipo de artefacto y ciclo adaptado

El 015 produce **código de pipeline + datos** (Bronce), no documentos ni configuración. A diferencia del 010, el ciclo SDD+TDD usa **TDD real** (columna de código de la metodología §7):

| Ciclo estándar | Adaptación para 015 Intake |
|----------------|----------------------------|
| SPEC | Define esquemas mínimos, reglas de validación, contrato de Bronce e inmutabilidad |
| HUMAN REVIEW | Operador aprueba el Sprint Contract; en Excel ambiguo, confirma hoja/cabecera (1ª entrega) |
| RED | **Tests unitarios reales** + ~20 fixtures de archivos deliberadamente rotos (E9) que deben fallar/pasar según lo esperado |
| GREEN | Implementa parser, validador de estructura/tipos, deduplicador, escritor de Bronce hasta que los tests pasan |
| REFACTOR | Limpia módulos, sin alterar comportamiento verificado |
| EVAL | Auditoría de C con rúbrica de **integridad y fidelidad** (Bronce bit-a-bit, conteos, rechazo correcto) |

---

## Sección 2 — Fase 1: Diseño Agéntico

### 2.1 Instancias y Roles

| Instancia | Rol | Responsabilidades | Escribe en |
|-----------|-----|-------------------|------------|
| A — Governor | Director de la Ingesta | Define Sprint Contract; gestiona gates; decide Avanzar/Repetir; reporta al operador | `600_persistence/harness-state.json` |
| B — Phase Orchestrator | Coordinador Técnico | Lee contrato; persiste `orchestration_plan`; coordina el Worker; actualiza checkpoints | `600_persistence/execution-state.json` · `600_persistence/claude-progress.txt` |
| C — Phase Evaluator | Auditor Independiente | Lee Bronce y reportes sin contexto de ejecución; aplica rúbrica de fidelidad; emite APPROVED/REJECTED | `605_eval/verdict.json` · `605_eval/metrics_summary.json` · `600_persistence/claude-progress.txt` |

**Regla de Escritor Único (Single Writer Rule):**
- `600_persistence/harness-state.json` → **solo A**. C nunca escribe aquí aunque apruebe.
- `600_persistence/execution-state.json` → **solo B**.
- `600_persistence/claude-progress.txt` → el orquestador activo (A, B o C).
- **Bronce (`005_bronze/`) → solo el Worker del 015, una vez (write-once).** Ningún otro harness escribe ahí jamás.

Jerarquía de llamadas (nunca se viola): A → B (ejecutar), A → C (auditar), nunca simultáneo. A no llama al Worker directamente; **B es el único spawner del Worker**; C no llama a nadie, solo lee del filesystem/Storage/BD. B comunica completitud a A solo vía `execution-state.json` = `EXECUTION_COMPLETE`.

### 2.2 Workers Especializados

| Worker | Micro-tarea | Inputs que recibe | Output (path) |
|--------|-------------|-------------------|---------------|
| `intake-processor` | Ejecuta el pipeline secuencial P1→P8: detección de formato, validación de estructura/tipos, deduplicación, creación de Bronce inmutable con hash, manifest, reporte, evento | `client_config`, path del snapshot del cliente, `_manifest.json` previo (si incremental) | Bronce + `_manifest.json` + `intake_report.json` + `intake_log` (o `intake_rejection.json`) + evento |

**Un único Worker (decisión a — DEC-057).** Los pasos P1→P8 son una **cadena secuencial determinística** (no se puede deduplicar antes de parsear, ni crear Bronce antes de validar estructura): no hay nada que paralelizar ni especializaciones cognitivas distintas. El paralelismo real del sistema está **después** del 015 (020 ‖ 025), no dentro.

> **"Un Worker" ≠ "un archivo de código gigante".** Internamente el `intake-processor` orquesta **módulos de código bien separados y testeables**: `source_adapter` (costura de fuente, §7), `format_detector`, `schema_validator`, `type_validator`, `deduplicator`, `bronze_writer` (write-once + SHA-256), `report_builder`. La separación vive en el **código** (con sus tests unitarios), no en la multiplicación de agentes.

> **Nota E7 — Paralelización:** No aplica *dentro* del 015 (cadena secuencial). Aplica al *salir* (handoff fan-out a 020 ‖ 025, §5).

> **Nota E8 — Extended Thinking:** Reservado para los **únicos puntos de juicio**: encoding/delimitador ambiguos no resueltos por heurística, o resolución de hoja/cabecera de Excel atípico. La validación determinística **no** usa extended thinking — es código.

Cada Worker escribe su artefacto al filesystem/Storage y reporta a B **solo el path** (Regla E6 — Referencias Ligeras).

### 2.3 Política de Herramientas

| Worker | Herramientas permitidas |
|--------|------------------------|
| `intake-processor` | `Read`, `Write`, `Bash`/Python (pandas/openpyxl para parseo, `hashlib` para SHA-256, `chardet`/heurística para encoding); Fase 3: Supabase Storage SDK + PostgREST/driver; Fase 1: filesystem local |

**Política de Fallback ante fallo de herramienta (3 niveles, metodología §6):**
1. **Reintento** (hasta 2×): fallos transitorios de lectura/escritura (Storage busy, timeout).
2. **Fallback:** si Supabase Storage no responde (Fase 3) → escribir Bronce en `1000_storage_local/` (Fase 1) y marcar `_pendiente_supabase: true`. Si la detección automática de encoding/delimitador falla → escalar al operador (no adivinar).
3. **Escalamiento:** si no se puede escribir Bronce ni siquiera local, o el archivo es irrecuperable tras 2 reintentos → marcar `BLOCKED` en `execution-state.json`, **detener** y escalar con log completo. Nunca crear un Bronce parcial o degradado — un bloqueo explícito es preferible a un Bronce que mienta.

### 2.4 Política de Escalamiento

Escalar al operador Triple S (detener flujo) en:
1. **Rechazo de estructura (P2):** falta ≥ 1 campo mínimo → generar `intake_rejection.json` con la lista de faltantes; no crear Bronce; notificar al operador (el operador contacta al cliente con la guía de corrección). No es un error del sistema — es flujo normal de rechazo.
2. **Encoding/delimitador irresoluble:** la heurística no puede determinar con confianza cómo leer el archivo → escalar antes de crear Bronce (un Bronce mal-decodificado corrompe `id_cliente`/`id_producto` y rompe el dedupe).
3. **Excel ambiguo (1ª entrega):** múltiples hojas con datos o cabecera no detectable → el worker propone hoja/fila por heurística y **el operador confirma**; la huella confirmada se persiste en `client_config` y se reutiliza en entregas siguientes (decisión Excel — DEC-057).
4. **Esquema 2 esperado pero no recibido:** `tiene_esquema2 = true` pero no llega el archivo → **NO bloquea**; se crea Bronce del Esquema 1, se registra el Esquema 2 como "esperado, no recibido" en `intake_report.json`, el operador gestiona (decisión d — esquemas independientes).
5. **Fallo irrecuperable de Storage tras 2 reintentos** → escalar con log.

A registra todo bloqueo en `harness-state.json` bajo `escalations` con archivo, razón y próxima acción.

### 2.5 Checkpoints Canónicos

| ID | Momento | Qué persiste B |
|----|---------|----------------|
| CP-01 | Tras P1–P2 (formato + estructura) | Resultado del gate: aprobado o rechazado; formato/encoding/delimitador detectados |
| CP-02 | Tras P3–P5 (tipos, duplicados, rango) | Conteos de errores, duplicados, rango temporal, warnings |
| CP-03 | Tras P6 (Bronce escrito + hash) | Paths de archivos Bronce, SHA-256 de cada uno, `_manifest.json` actualizado |
| CP-04 | Tras P7 (reportes) | Paths de `intake_report.json` e `intake_log` |
| CP-05 | Tras P8 (evento) | Confirmación del evento `intake_complete` emitido — `EXECUTION_COMPLETE` |

**Recuperación (E5):** ante fallo, reanudar desde el último CP. **Caso crítico:** si el fallo ocurre entre CP-03 y CP-05 (Bronce escrito pero reporte/evento a medias), el Worker **verifica idempotencia por SHA-256**: si el archivo Bronce ya existe con el hash esperado, no lo reescribe (write-once respetado) — solo completa reporte y evento. Nunca duplica ni reescribe Bronce.

### 2.6 Trigger de Context Reset

Criterios (el que ocurra primero):
- **Conductual (primario):** señales de degradación — declarar "Bronce creado" sin verificar el SHA-256, omitir el conteo de duplicados o de errores de tipo, marcar CP sin que el paso haya terminado, emitir el evento antes de que el reporte exista, o "aprobar" un archivo sin haber corrido la validación de estructura.
- **Cuantitativo (secundario):** ≥ 70% de tokens.

Acción: continuar desde el último CP en `execution-state.json`. Nunca reiniciar desde cero. La inmutabilidad write-once + hash hace la reanudación segura (no hay riesgo de doble escritura).

### 2.7 Evaluación Temprana (E9) — la mayor palanca del 015

Como el 015 es determinístico, la evaluación temprana es **genuinamente poderosa** aquí (más que en el 010). Al completar el primer módulo funcional (el `schema_validator` + `bronze_writer`), B selecciona una muestra de **~20 fixtures representativos** y C los evalúa:

| Categoría de fixture | Ejemplos |
|----------------------|----------|
| Estructura | falta `id_producto`; cabecera en fila 3; columnas extra |
| Formato | CSV `;`; CSV `\|`; Excel multi-hoja; `.xls` legacy; encoding cp1252 con acentos |
| Tipos | `cantidad_solicitada` negativa; fecha en 3 formatos; `id_cliente` vacío |
| Duplicados | duplicados internos (batch); registros repetidos vs Bronce previo (incremental) |
| Rango | historial real 3.4 años vs declarado 2 años (warning) |
| Bronce | verificar bit-exactitud y SHA-256; verificar que un 2º intento no reescribe |

Si el score de C ≥ 0.7 → continuar. Si < 0.7 → ajustar la spec **antes** de seguir. B registra el resultado en `execution-state.json` bajo `early_eval`.

---

## Sección 3 — Sprint Contract (Plantilla)

Template que A propone al operador antes de spawnear B. Requiere aprobación explícita.

```
SPRINT CONTRACT — 015 Intake
============================
Objetivo    : Recibir los datos del cliente {NOMBRE_CLIENTE}, validarlos y crear la copia
              Bronce exacta e inmutable; emitir intake_complete hacia 020 ‖ 025
Fase        : 015 — Intake
Modo        : [INICIO | CONTINUACIÓN]
Tenant      : {tenant_id} — Modo de ingesta: {batch | incremental}

Inputs disponibles:
  - Evento 010            : onboarding_discovery_complete [presente | AUSENTE → no arrancar]
  - client_config         : {path / referencia} (modo, tiene_esquema2, historial declarado)
  - Carpeta Bronce        : tenants/{id}/1000_data/005_bronze/ [existe | crear]
  - Archivo Esquema 1     : {path al snapshot | PENDIENTE de entrega}
  - Archivo Esquema 2     : {path | N/A si tiene_esquema2=false}
  - Huella de formato     : {presente de entrega previa | a determinar en 1ª entrega}

Worker activado:
  1. intake-processor  → 005_bronze/orders_{mode}_{fecha}.csv
                         005_bronze/inventory_{mode}_{fecha}.csv  (si Esquema 2)
                         005_bronze/_manifest.json
                         005_bronze/intake_report.json
                         intake_log (fila)  +  tenants.last_intake_at
                         Evento: intake_complete → [020_diagnosis, 025_refinery]

Checkpoints  : CP-01..CP-05
Criterio Done: (1) estructura validada o rechazada, (2) tipos validados, (3) duplicados
               detectados, (4) Bronce bit-exacto e inmutable con SHA-256, (5) manifest+report,
               (6) intake_log + last_intake_at, (7) evento emitido como último paso

Riesgos identificados:
  - [archivo no entregado / formato no aceptado / archivo corrupto]
  - [falta de campo mínimo → rechazo de estructura]
  - [encoding o delimitador ambiguo → escalamiento]
  - [Excel multi-hoja sin huella → confirmación del operador]
  - [Esquema 2 esperado y no recibido → no bloquea, se registra]

Próxima acción: spawnear intake-processor con client_config y path del snapshot del cliente
```

---

## Sección 4 — Rúbrica de Evaluación (Instancia C)

Rúbrica de **integridad y fidelidad** (no de razonamiento). Las dimensiones son más binarias y verificables que las del 010.

### Dimensiones de evaluación

| ID | Dimensión | Descripción | Score |
|----|-----------|-------------|-------|
| D1 | Detección de formato | Formato, delimitador (`,`/`;`/`\|`), encoding y (Excel) hoja/cabecera detectados correctamente y registrados en `intake_report` | 0.0–1.0 |
| D2 | Validación de estructura | El gate de rechazo se aplicó correctamente: rechaza si falta campo mínimo, acepta si están todos. Sin falsos positivos/negativos | 0.0–1.0 |
| D3 | Validación de tipos y conteos | Errores de tipo contados con exactitud, sin detener el flujo; campos ideales faltantes registrados | 0.0–1.0 |
| D4 | Detección de duplicados | Clave compuesta aplicada; comportamiento correcto según modo (batch registra/no elimina; incremental excluye vs Bronce acumulado) | 0.0–1.0 |
| D5 | Fidelidad e inmutabilidad de Bronce | Bronce **bit-exacto** a la entrada; SHA-256 correcto y persistido; un archivo por entrega + manifest; nada reescrito (write-once) | 0.0–1.0 |
| D6 | Completitud de reportes | `intake_report.json`, `_manifest.json` e `intake_log` completos: conteos, rango, errores, duplicados, warnings, `files` JSONB con hash por archivo | 0.0–1.0 |
| D7 | Evento emitido | `intake_complete` existe como **último paso**, con payload completo (paths + next_harnesses) y solo tras Bronce verificado | 0.0–1.0 |

**Gate de paso:** Score promedio ≥ 0.80.
**Reglas de veto (rechazo automático):**
- **D5 = 0.0** → Bronce no es copia exacta o no tiene hash → todo el medallón aguas abajo es inválido. Rechazo.
- **D2 = 0.0** → el gate de estructura no funciona (datos inválidos entran a Bronce, o válidos se rechazan). Rechazo.
- **D7 = 0.0** → sin evento, 020 y 025 nunca arrancan. Rechazo.

### Anclas de calibración (few-shot)

**Score 0.2** — El archivo se leyó con encoding equivocado (acentos corruptos en `id_cliente`). La validación de estructura no detectó un campo mínimo faltante. El "Bronce" no coincide byte-a-byte con la entrada y no tiene SHA-256. Sin manifest. Sin evento.

> Ejemplo: un CSV `cp1252` se leyó como utf-8, `Categoría` quedó como `Categorâ€¦`. El validador aceptó el archivo aunque faltaba `cantidad_solicitada`. Se escribió un archivo "Bronce" ya alterado por el parseo.

**Score 0.5** — Formato, estructura y tipos correctos. Pero el Bronce en Modo Incremental se creó **reescribiendo** un único archivo acumulado (viola inmutabilidad) en vez de un archivo por entrega + manifest. El SHA-256 no se persistió. El evento se emitió pero antes de que el reporte existiera.

> Ejemplo: la validación fue impecable, pero el `bronze_writer` concatenó sobre el archivo previo, perdiendo la trazabilidad temporal y rompiendo el write-once. El reporte quedó incompleto.

**Score 0.8** — Formato/estructura/tipos/duplicados correctos. Bronce bit-exacto, write-once, SHA-256 calculado y en el manifest. Evento emitido como último paso con payload completo. Único faltante: el `intake_report` no registró el `warning` de discrepancia de rango temporal (P5) que sí ocurría.

> Ejemplo: todo el pipeline correcto y verificable; el historial real (3.4 años) difería del declarado (2 años) pero el reporte no lo anotó como warning. No invalida el Bronce, pero el 020 pierde una señal.

**Score 1.0** — Formato, delimitador y encoding detectados y registrados. Estructura validada con el gate correcto. Errores de tipo contados con exactitud. Duplicados tratados según el modo. Bronce **bit-exacto** a la entrada (verificable), inmutable (write-once), con SHA-256 por archivo persistido en `_manifest.json`. `intake_report.json` e `intake_log` completos (incluido `files` JSONB y warnings). Evento `intake_complete` emitido como último paso, con `bronze_path`, `manifest_path`, `intake_report_path` y `next_harnesses: [020, 025]`.

> Ejemplo: CSV `;` en cp1252 detectado correctamente; 45.230 filas; rango 2023-01-01 → 2026-05-31 (1.246 días); 12 errores en `cantidad_solicitada`; 34 duplicados internos registrados (batch, no eliminados); Bronce `orders_batch_20260608.csv` con SHA-256 `a3f…`; manifest e intake_report completos; warning de rango anotado; `intake_complete` emitido y escuchado por 020 y 025.

### Output de C

```json
// /605_eval/verdict.json
{
  "phase": "015_intake",
  "tenant_id": "",
  "delivery_id": "",
  "verdict": "APPROVED | REJECTED",
  "scores": {
    "D1_format_detection": 0.0,
    "D2_structure_validation": 0.0,
    "D3_type_and_counts": 0.0,
    "D4_duplicate_detection": 0.0,
    "D5_bronze_fidelity_immutability": 0.0,
    "D6_reports_completeness": 0.0,
    "D7_event_emitted": 0.0
  },
  "average": 0.0,
  "veto_triggered": false,
  "veto_dimension": null,
  "rejection_reasons": [],
  "recommendations": []
}
```

```json
// /605_eval/metrics_summary.json  (estructura mínima — metodología §8.2)
{
  "pipeline_data": {
    "phase": "015_intake",
    "tenant_id": "",
    "delivery_id": "",
    "mode": "batch | incremental",
    "started_at": "",
    "execution_complete_at": "",
    "audit_complete_at": ""
  },
  "artifact_status": {
    "bronze_schema1": { "path": "", "sha256": "", "rows": 0, "status": "CREATED | MISSING" },
    "bronze_schema2": { "path": "", "sha256": "", "rows": 0, "status": "CREATED | NOT_EXPECTED | EXPECTED_NOT_RECEIVED" },
    "manifest_json": { "status": "COMPLETE | MISSING" },
    "intake_report_json": { "version": 1, "revisions": 0, "status": "APPROVED | REJECTED", "score": 0.0 },
    "intake_log": { "status": "CREATED | MISSING" },
    "event_emitted": { "event": "intake_complete", "status": "CONFIRMED | MISSING" }
  },
  "timeline_metrics": {
    "total_phase_duration_min": 0,
    "cp01_to_cp03_min": 0,
    "cp03_to_cp05_min": 0
  },
  "change_requests": []
}
```

---

## Sección 5 — Handoff Artifact → 020 Diagnosis + 025 Refinery (fan-out paralelo)

El 015 entrega a **dos** consumidores que corren en **paralelo** (DEC-024). El *por qué* del paralelo es el invariante del medallón: **020 mide la salud real leyendo Bronce tal cual; si 025 lo limpiara primero, el ISD saldría artificialmente bueno.** Ambos leen Bronce al mismo tiempo, ninguno antes que el otro.

```
Artefactos en Storage (lectura por ambos):
  └── tenants/{tenant_id}/1000_data/005_bronze/
      ├── orders_{mode}_{fecha}.csv     → datos crudos (inmutables, verificar SHA-256)
      ├── inventory_{mode}_{fecha}.csv  → si Esquema 2
      ├── _manifest.json                → registro de entregas + hashes (unión lógica del histórico)
      └── intake_report.json            → primer documento de la cadena de evidencia del ISD

Evento escuchado por 020 y 025:
  └── intake_complete  { tenant_id, delivery_id, mode, bronze_path, manifest_path,
                         intake_report_path, next_harnesses: [020_diagnosis, 025_refinery] }
```

**Tres garantías del handoff:**
1. **Atomicidad:** `intake_complete` se emite **solo** cuando Bronce está completo y verificado (P8 = último paso). Fallo antes de P8 → sin evento → consumidores no arrancan sobre datos parciales.
2. **Verificabilidad:** cada consumidor recalcula el SHA-256 de Bronce contra el manifest antes de procesar. Si no coincide → Bronce alterado → detenerse.
3. **Solo-lectura:** **ni 020 ni 025 tienen permiso de escritura sobre `005_bronze/`.** 025 escribe en Plata (`007_silver/`), nunca en Bronce. Esto protege el invariante de DEC-024.

**Condición de activación del 015 (entrada):** debe existir el evento `onboarding_discovery_complete` del 010 con `tenant_id` válido y el `harness-state.json` del 010 en `PHASE_COMPLETE`. Sin ambas, el 015 no arranca.

**Orquestación del fan-out — Fase 1 (decisión handoff — DEC-057):** el `intake_complete` se deja como archivo JSON `estado: pendiente` en `600_persistence/events/`; el **conductor/operador** lo lee y spawnea 020 y 025 (modelo conductor, DEC-051). En Fase 3 lo hace Supabase Realtime o el scheduler (Prefect). El brief construye solo el mecanismo de Fase 1.

**Incremental:** cada entrega exitosa = **exactamente un** `intake_complete`. El 015 no decide *con qué frecuencia* 020/025 actúan (p. ej. el reentrenamiento semanal de DEC-012 lo gestiona el 030, no el 015): el 015 solo garantiza que cada vez que congela datos nuevos, avisa.

**Lo que el handoff NO incluye:** datos de negocio en el payload (solo referencias, E6); ninguna corrección o transformación (eso es 025); ningún cálculo de salud (eso es 020).

---

## Sección 6 — Flujo del Arnés (12.1–12.5)

### 12.1 Inicialización (Instancia A)

**Determinación del modo:**
- No existe `600_persistence/harness-state.json` → **Inicio** (Ritual E10-A)
- Existe e íntegro → **Continuación** (Ritual E10-B)
- Existe pero corrupto → `git restore 600_persistence/harness-state.json`; si persiste, detener y reportar al operador

**Ritual E10-A — Inicio:**
1. Verificar directorio y ambiente (Python + pandas/openpyxl disponibles, acceso a Storage).
2. **Verificar precondición de entrada:** existe el evento `onboarding_discovery_complete` y el 010 está en `PHASE_COMPLETE`. Si no → detener y escalar (el 015 no puede arrancar sin el 010).
3. Crear jerarquía: `/015_intake/`, `/600_persistence/`, `/605_eval/`, `/610_knowledge/`, `/615_changes/`. La carpeta Bronce ya la creó el 010.
4. Inicializar `harness-state.json`, `execution-state.json`, `claude-progress.txt` con esquemas vacíos.
5. `git init` + enlace al remote en GitHub (si el proyecto de prueba aún no lo tiene).
6. Prueba de sanidad: leer `client_config`, verificar escritura en Storage local.
7. Registrar arranque en `claude-progress.txt`.
8. Presentar Sprint Contract al operador.

**Ritual E10-B — Continuación:**
1. Verificar directorio y ambiente.
2. `git log --oneline -10`.
3. Leer `claude-progress.txt` (estado narrativo).
4. Cargar `harness-state.json` (Sprint Contract vigente) y `execution-state.json` (último CP).
5. Verificar integridad de Bronce ya escrito (SHA-256 vs manifest) si lo hubiera.
6. Seleccionar siguiente tarea según el último CP.

**Reporte al operador (obligatorio):** estado encontrado (modo, integridad, precondición del 010, sanidad), Sprint Contract propuesto/vigente, próxima acción.

**Gate de aprobación del operador:** Aprobado → A escribe el contrato en `harness-state.json` y spawnea B. Ajuste → reincorpora y re-presenta. Cancelación → registra y detiene.

### 12.2 Ejecución Técnica (Instancia B + Worker)

1. B lee el Sprint Contract desde `harness-state.json` (referencia, no inline).
2. B consulta **obligatoriamente** `/610_knowledge/decisions_library.md` y `lessons_learned.md`. Si no existen (primer proyecto), lo registra en `execution-state.json` y continúa.
3. B persiste `orchestration_plan` completo en `execution-state.json` **antes de spawnear el Worker** (E12).
4. B spawnea `intake-processor` con: `client_config`, path del snapshot del cliente, `_manifest.json` previo (si incremental).
5. `intake-processor` ejecuta P1→P2. Si **rechazo de estructura**: escribe `intake_rejection.json`, reporta a B, B registra CP-01 con `REJECTED`, A notifica al operador y el flujo termina sin Bronce ni evento.
6. Si **aprobado**: el Worker continúa P3→P5, reporta paths, B registra CP-01 y CP-02.
7. El Worker ejecuta P6 (Bronce + SHA-256 + manifest), reporta paths, B registra CP-03.
8. El Worker ejecuta P7 (reportes) y P8 (evento como último paso), reporta, B registra CP-04 y CP-05.
9. B marca `EXECUTION_COMPLETE` en `execution-state.json` y actualiza `claude-progress.txt` — señal que A lee. No existe canal directo B → A.

### 12.3 Auditoría y Gate de Aprobación (Instancia C + A)

**Paso 1 — Gate intermedio (A):** A verifica `EXECUTION_COMPLETE`. Si rechazo de estructura, A ya cerró el flujo en 12.2 (no hay nada que auditar para C; se documenta como rechazo de entrada, no de calidad). Si Bronce creado, A spawnea C pasando paths.

**Paso 2 — Auditoría (C):**
- C lee Bronce, `_manifest.json`, `intake_report.json`, `intake_log` directamente del filesystem/Storage.
- C **recalcula el SHA-256** de Bronce y lo compara con el manifest (verificación de fidelidad).
- C compara Bronce contra el snapshot de entrada para verificar bit-exactitud (D5).
- C evalúa contra la rúbrica (Sección 4) con las anclas.
- C escribe solo en sus archivos — **nunca en `harness-state.json`**: `/605_eval/verdict.json`, `/605_eval/metrics_summary.json`.
- C registra en `claude-progress.txt`.

**Paso 3 — Decisión final (A — GateKeeper):**
- A lee `/605_eval/verdict.json`.
- **APPROVED** → A marca `PHASE_COMPLETE` en `harness-state.json`; notifica al operador. (El conductor/operador procede a spawnear 020 y 025 leyendo el evento.)
- **REJECTED** → A activa protocolo 12.4.

### 12.4 Protocolo de Rechazo y Reintento

**Rechazo Técnico** (C emite REJECTED — Bronce/reportes/evento no cumplen rúbrica):
- C escribe el rechazo en `/605_eval/verdict.json`. No contacta a B directamente.
- A marca `IN_REWORK` en `harness-state.json` y re-spawnea B con la referencia al rechazo.
- B consulta `lessons_learned.md` y re-ejecuta `intake-processor` **solo en los pasos fallidos**. Por inmutabilidad: si el Bronce ya es correcto (hash válido) no se reescribe; solo se reparan reportes/evento. Si el Bronce es el defecto (D5), se requiere re-creación: B confirma con A que se sobreescribe el Bronce defectuoso (excepción controlada al write-once, registrada).

Casos específicos:
- **D2 falla (gate de estructura):** revisar el validador; re-correr desde P2.
- **D5 = 0.0 (Bronce no fiel):** re-crear Bronce desde el snapshot original; máximo 2 reintentos; luego escalar.
- **D7 = 0.0 (evento):** re-emitir el evento (Bronce y reportes intactos).

**Rechazo Estratégico / de entrada** (el archivo del cliente es el problema, no el harness):
- Archivo no entregado, formato no aceptado, o rechazo de estructura → no es rework del 015; A marca `HOLD`, notifica al operador, el cliente re-entrega desde P1.

**Gestión de Cambios (CR):** ante un cambio sobre un Bronce ya aprobado (caso raro — Bronce es inmutable), A registra el CR en `harness-state.json`; B documenta en `/615_changes/CR_XXX_*.md` el impacto (re-ingesta = nueva entrega, no modificación del Bronce existente); C re-audita; A cierra.

**Registro de aprendizaje:** todo rechazo lo registra C en `lessons_learned.md` al cierre (qué falló, en qué módulo, cuántos reintentos, regla para evitarlo).

### 12.5 Cierre

1. A marca `PHASE_COMPLETE` en `harness-state.json`.
2. C actualiza `/610_knowledge/lessons_learned.md` con hallazgos del ciclo.
3. A consolida decisiones de arquitectura en `/610_knowledge/decisions_library.md`.
4. A notifica al operador: Bronce creado (con hashes), reportes, `intake_log`, evento confirmado, y que 020 ‖ 025 están listos para dispararse.
5. A registra cierre en `claude-progress.txt` con timestamp, resumen, tenant_id y delivery_id.
6. A hace commit final: `feat(015-intake): bronze creado — {tenant_id} entrega {delivery_id}`.

---

## Sección 7 — Notas de Construcción

### Agentes a crear

| Nombre | Tipo | Descripción |
|--------|------|-------------|
| `intake-governor` | Instancia A | Gobierna la fase; gates; decisión final; reporta al operador |
| `intake-orchestrator` | Instancia B | Coordina el Worker; persiste `orchestration_plan`; gestiona checkpoints |
| `intake-processor` | Worker | Pipeline P1→P8 con módulos de código testeables (parser, validadores, deduplicador, bronze_writer) |
| `intake-evaluator` | Instancia C | Auditoría de fidelidad/integridad; recalcula hashes; aplica rúbrica |

> En el modelo conductor (DEC-051), la **sesión principal** es la única que spawnea agentes; governor y orchestrator gestionan estado y emiten señales de despacho. Replicar el patrón del 010 (governor/orchestrator de un solo paso + conductor que spawnea).

### Skills / módulos de código requeridos

- Parseo CSV con detección de delimitador (`,`/`;`/`\|`) y encoding (`chardet` o heurística utf-8→utf-8-sig→cp1252).
- Parseo Excel `.xlsx` y `.xls` (openpyxl / pandas) con resolución de hoja y fila de cabecera (huella + confirmación).
- `hashlib` para SHA-256 de cada archivo Bronce.
- Validador de esquema (campos mínimos por Esquema 1 / Esquema 2).
- Validador de tipos con conteo de errores (no detiene).
- Deduplicador por clave compuesta `(fecha_pedido, id_cliente, id_producto)`, con modo batch/incremental.
- `bronze_writer` write-once + actualización de `_manifest.json`.
- Adaptador de fuente (`source_adapter`) — **costura para conectores futuros**.
- Schemas de referencia (estilo discovery-*-schema): `intake-report-schema`, `intake-manifest-schema`, `intake-log-schema`, `intake-rubric`, `intake-state-schema`.

### Consideraciones de implementación

- **Costura de adaptador de fuente (decisión fuentes — DEC-057):** el `intake-processor` recibe siempre un **snapshot tabular** vía una interfaz `source_adapter` que devuelve `(bytes, formato, metadata_de_fuente)`. En **Fase 1** el único adaptador implementado es el **manual/operador** (el operador deja el archivo en la carpeta del tenant). El brief documenta —sin construir— adaptadores futuros (SFTP, conector ERP, extracción de BD): cualquier conector es pieza *upstream* que materializa un snapshot antes de tocar el 015. El medallón obliga a esto: incluso una fuente viva (ERP/BD) debe congelarse como snapshot para ser Bronce.
- **Huella de formato con memoria (decisión Excel — DEC-057):** en la 1ª entrega, heurística + confirmación del operador para hoja/cabecera/delimitador/encoding; la huella confirmada se persiste en `client_config` y se reutiliza en entregas siguientes (re-confirmando solo si el formato cambia). Esto evita tocar el schema del 010 — la metadata nace contra el archivo real, no contra la entrevista.
- **Persistencia (decisión persistencia — DEC-057):** alcance = rebanada del intake. Bronce → Storage (Fase 1: `1000_storage_local/tenants/{id}/1000_data/005_bronze/`, DEC-044; Fase 3: Supabase Storage). `intake_log` = una fila por entrega con `files` JSONB (path + sha256 + rows + date_range por archivo); el `_manifest.json` es la fuente autoritativa, la tabla la indexa. Reconciliación de nombre: tabla **`tenants`** (no `clients`), DEC-047. **No** se diseña cobro (subscriptions/payments): T-030 (pesos ITO) y T-031 (pasarela) **no bloquean** el 015. Fallback JSON `_pendiente_supabase: true` igual que el 010.
- **Inmutabilidad (decisión e):** write-once + SHA-256 verificable. En Fase 1 es convención + el código nunca abre Bronce en modo escritura tras crearlo; en Fase 3, permisos de solo-lectura sobre `005_bronze/`. El hash convierte "no lo toqué" en "lo pruebo".
- **Incremental como unión lógica (decisión f):** un archivo Bronce inmutable por entrega + `_manifest.json`; el "Bronce acumulado" es la unión de archivos, no un archivo que se reescribe. Da inmutabilidad real + auditoría temporal (qué datos existían en qué fecha).
- **El paralelo del handoff** (020 ‖ 025) es lógico en Fase 1 (conductor spawnea ambos); real en Fase 3 (Realtime/scheduler). Ambos verifican el hash de Bronce antes de procesar.
- **Esquemas independientes (decisión d):** el Esquema 1 es el corazón del pronóstico; el Esquema 2 enriquece. Faltar el Esquema 2 nunca bloquea el Bronce del Esquema 1.
- El 015 **NO**: corrige/transforma (025), calcula ISD (020), modifica el origen del cliente, ni notifica directamente al cliente (todo pasa por el operador en Fase 1).
```

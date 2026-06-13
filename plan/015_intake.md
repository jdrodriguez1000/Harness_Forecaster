# Plan de Trabajo — Construcción del Harness 015 Intake
## FARO — Sabbia Solutions & Software

**Referencia:** `brief/015_intake.md`
**Fase objetivo:** Fase 1 (CSV/Excel — sin Supabase, sin Realtime, sin Prefect — filesystem local + fallback JSON)
**Condición de inicio:** Brief 015 revisado y aprobado (T-060 implementada) · Harness 010 TERMINADO
**Responsable de ejecución:** Operador Triple S + Claude Code

> **Nota rectora (DEC-057, decisión 3).** El 015 es un **pipeline determinístico**, no un harness de razonamiento como el 010. Por eso este plan **invierte el peso**: lo grueso no son los prompts de los agentes sino los **módulos de código del pipeline con TDD real** y la **batería de ~20 fixtures de archivos rotos (E9)**. Cada módulo se construye en orden RED → GREEN → REFACTOR. El LLM solo interviene en los puntos de juicio (encoding/delimitador irresoluble, hoja/cabecera de Excel atípico, redacción del reporte).

> **Arquitectura de dos terminales (LEC-053).** La **construcción** descrita en este plan (módulos, tests, agentes, skills) se hace en **esta** terminal (repo fuente `Harness_Forecaster`). La **corrida e2e** con un tenant real (consumir el evento del 010, montar Bronce) se ejecuta en una carpeta de prueba dedicada (`Test_Forecaster/Test_NNN/`) — ver PASO 16.

---

## Lectura obligatoria antes de empezar

En este orden:

1. `brief/015_intake.md` — diseño completo del harness (7 secciones, P1→P8, rúbrica)
2. `progress/decisions.md` — **DEC-057** (las 10 decisiones de diseño que rigen todo), y además DEC-012 (modos de ingesta), DEC-014 (Esquema 1 / Esquema 2 y sus campos), DEC-024 (fan-out paralelo 020 ‖ 025), DEC-044 (Storage local Fase 1), DEC-047 (tabla `tenants`, no `clients`), DEC-051 (modelo conductor), DEC-055 (persistencia acoplada al 015)
3. `progress/lessons.md` — lecciones del 010 (Single Writer Rule, timestamps reales, modelo conductor)
4. `documents/supabase_persistence_guide.md` — §6 (Capa 1), §8 (medallón), §10 (conmutación fallback)
5. `harnesses/015_intake.md` — documentación funcional de referencia

---

## Prerrequisitos

| # | Prerrequisito | Verificación |
|---|--------------|--------------|
| P-1 | Python ≥ 3.11 instalado | `python --version` |
| P-2 | `pandas`, `openpyxl`, `xlrd` (para `.xls`), `chardet`, `pytest` instalados | `pip install pandas openpyxl xlrd chardet pytest` → `pytest --version` |
| P-3 | FORGE/agentes desplegados en el directorio de trabajo | Existen `.claude/agents/` y `.claude/skills/` |
| P-4 | Para la corrida e2e (PASO 16): existe el evento `onboarding_discovery_complete` del 010 con `tenant_id` válido y el `harness-state.json` del 010 en `PHASE_COMPLETE` | El JSON del evento existe en el `600_persistence/events/` del proyecto de prueba |
| P-5 | Para la corrida e2e: la carpeta Bronce del tenant ya existe (la creó el 010) | `ls tenants/{id}/1000_data/005_bronze/` |

> **Importante:** los PASOS 1–15 (construcción y pruebas unitarias) NO requieren P-4 ni P-5. Se construyen y testean con **fixtures sintéticos**, sin depender de una corrida real del 010.

---

## Mapa de módulos a construir

El `intake-processor` orquesta P1→P8 sobre módulos separados y testeables (DEC-057, decisión 4). Esta es la correspondencia paso → módulo → paso del plan:

| Proceso (brief) | Módulo de código | Paso del plan |
|-----------------|------------------|---------------|
| P1 — Recepción | `source_adapter.py` | PASO 4 |
| P1 — Detección de formato | `format_detector.py` | PASO 5 |
| P2 — Validación de estructura (GATE) | `schema_validator.py` | PASO 6 |
| P3 — Validación de tipos | `type_validator.py` | PASO 7 |
| P4 — Detección de duplicados | `deduplicator.py` | PASO 8 |
| P5 — Rango temporal | `range_evaluator.py` | PASO 7 (anexo) |
| P6 — Bronce write-once + hash | `bronze_writer.py` | PASO 9 |
| P7 — Reportes | `report_builder.py` | PASO 10 |
| P1–P8 — Orquestación + P8 evento | `pipeline.py` (el processor) | PASO 11 |

Todos viven en `scripts/015_intake/pipeline/`; sus tests en `scripts/015_intake/tests/`; los fixtures en `scripts/015_intake/tests/fixtures/`. Los schemas JSON de referencia (PASO 3) en `templates/015_intake/schemas/`.

---

## Pasos de construcción

### PASO 1 — Crear estructura de carpetas del harness

> **Reconciliación con la arquitectura de dos terminales (LEC-053).** En el **repo fuente** (`Harness_Forecaster`) solo vive lo que se construye: código, tests, plantillas, schemas, agentes y skills. Las carpetas de **estado runtime** (`600_persistence/`, `605_eval/`, `610_knowledge/`, `615_changes/`) y el working dir `015_intake/` **NO** se crean en el repo fuente — las crea el ritual E10-A durante la corrida e2e en la terminal de prueba (PASO 16). Esto sigue la convención real del 010: `scripts/010_discovery/` (código), `templates/010_discovery/` (plantillas + schemas), `.claude/agents|skills/`.

Carpetas a crear **en el repo fuente**:

```
scripts/015_intake/
  pipeline/              ← módulos de código del pipeline (+ __init__.py)
  tests/                 ← tests unitarios (pytest)
    fixtures/            ← ~20 archivos rotos/válidos (E9)
templates/015_intake/
  schemas/               ← schemas JSON de referencia
  (plantilla de intake_rejection, etc.)
```

Agentes (`.claude/agents/intake-*.md`) y skills (`.claude/skills/intake-*/`) se crean en los PASOS 13 y 3.

**Verificación:** `ls scripts/015_intake templates/015_intake` muestra las carpetas; `pipeline/__init__.py` existe (paquete importable). En pruebas unitarias el Bronce se escribe en un `tmp_path` de pytest, nunca en una carpeta real.

---

### PASO 2 — Inicializar archivos de estado vacíos

**`600_persistence/harness-state.json`** — propiedad exclusiva de A (Governor):

```json
{
  "harness": "015_intake",
  "status": "INITIALIZING",
  "tenant_id": null,
  "delivery_id": null,
  "mode": null,
  "sprint_contract": null,
  "operator_approvals": [],
  "escalations": [],
  "change_requests": []
}
```

**`600_persistence/execution-state.json`** — propiedad exclusiva de B (Orchestrator):

```json
{
  "harness": "015_intake",
  "orchestration_plan": null,
  "last_checkpoint": null,
  "checkpoints": {
    "CP-01": null,
    "CP-02": null,
    "CP-03": null,
    "CP-04": null,
    "CP-05": null
  },
  "early_eval": null,
  "artifact_paths": {}
}
```

**`600_persistence/claude-progress.txt`:**

```
[INIT] Harness 015 Intake — en espera de Sprint Contract
```

**Verificación:** los tres archivos existen y el JSON valida (`python -m json.tool`). Los CP del 015 son CP-01..CP-05 con el significado de §2.5 del brief (formato+estructura / tipos+dup+rango / Bronce+hash / reportes / evento).

---

### PASO 3 — Crear schemas JSON de referencia (y skills correspondientes)

Cinco schemas + skills, replicando el patrón `discovery-*-schema` del 010. Los schemas viven en `015_intake/schemas/`; las skills (documentación de escritura) en `.claude/skills/`.

**3a — `intake-report-schema`** → `015_intake/schemas/intake_report_schema.json`

```json
{
  "_description": "Output P7 del intake-processor — reporte cuantificado de la entrega",
  "tenant_id": "",
  "delivery_id": "",
  "mode": "batch | incremental",
  "timestamp": "",
  "format": { "tipo": "csv | xlsx | xls", "delimitador": null, "encoding": "", "hoja": null, "fila_cabecera": null },
  "schema1": {
    "rows": 0,
    "campos_minimos_presentes": [],
    "campos_ideales_presentes": [],
    "campos_ideales_faltantes": [],
    "errores_tipo": { "fecha_pedido": 0, "id_cliente": 0, "id_producto": 0, "cantidad_solicitada": 0 },
    "duplicados": { "internos": 0, "vs_bronce_previo": 0 },
    "rango_temporal": { "fecha_min": "", "fecha_max": "", "dias_cubiertos": 0 }
  },
  "schema2": { "status": "CREATED | NOT_EXPECTED | EXPECTED_NOT_RECEIVED", "rows": 0, "errores_tipo": {} },
  "warnings": [],
  "rango_declarado_vs_real": { "declarado_anios": null, "real_anios": null, "discrepancia_pct": null, "warning": false }
}
```

**3b — `intake-manifest-schema`** → `015_intake/schemas/manifest_schema.json` (fuente autoritativa de Bronce):

```json
{
  "_description": "_manifest.json — registro autoritativo de entregas Bronce (unión lógica del histórico)",
  "tenant_id": "",
  "entregas": [
    {
      "delivery_id": "YYYYMMDD",
      "mode": "batch | incremental",
      "timestamp": "",
      "archivo": "orders_batch_YYYYMMDD.csv",
      "esquema": 1,
      "sha256": "",
      "rows": 0,
      "rango": { "fecha_min": "", "fecha_max": "" }
    }
  ]
}
```

**3c — `intake-log-schema`** → `015_intake/schemas/intake_log_schema.json` (fila de tabla, fallback JSON con `_pendiente_supabase: true`):

```json
{
  "_description": "Fila intake_log — una por entrega; files JSONB con hash por archivo",
  "_pendiente_supabase": true,
  "tenant_id": "",
  "delivery_id": "",
  "mode": "batch | incremental",
  "created_at": "",
  "files": [
    { "path": "", "esquema": 1, "sha256": "", "rows": 0, "date_range": { "min": "", "max": "" } }
  ],
  "report_path": "",
  "event_emitted": false
}
```

**3d — `intake-rubric`** → `.claude/skills/intake-rubric/` (rúbrica de 7 dimensiones D1–D7 de la Sección 4 del brief, con anclas 0.2/0.5/0.8/1.0, gate ≥ 0.80, vetos D2/D5/D7=0.0). Copiar fielmente desde la Sección 4 del brief.

**3e — `intake-state-schema`** → `.claude/skills/intake-state-schema/` (Single Writer Rule de los tres archivos de persistencia: `harness-state.json` solo A, `execution-state.json` solo B, `claude-progress.txt` el orquestador activo; Bronce solo el Worker, write-once). **Absorbe el PASO 2:** documenta las estructuras iniciales que crea E10-A (los archivos de estado son runtime — no se materializan en el repo fuente), los checkpoints CP-01..CP-05 mapeados a P1→P8, y los estados del flujo (incluido `REJECTED_STRUCTURE`).

**Verificación:** los 5 schemas/skills existen; los 3 JSON validan; la rúbrica reproduce D1–D7, el gate ≥ 0.80 y los 3 vetos (D2/D5/D7); el state-schema cubre lo que iba a ser el PASO 2. ✅ COMPLETADO.

---

### PASO 4 — `source_adapter.py` (P1 — recepción) — TDD

**Contrato.** Interfaz que devuelve siempre un snapshot tabular crudo: `read_snapshot(path) -> (raw_bytes, formato_declarado, source_metadata)`. En **Fase 1** solo se implementa el adaptador `ManualOperatorAdapter` (lee un archivo del filesystem que el operador dejó en la carpeta del tenant). La interfaz documenta —sin construir— conectores futuros (SFTP/ERP/BD): cualquier conector materializa un snapshot **antes** de tocar el 015 (lo obliga el invariante Bronce, DEC-057 decisión 2).

**RED — tests (`tests/test_source_adapter.py`):**
- Lee un archivo existente → devuelve bytes idénticos al archivo en disco (`open(path,'rb').read()`).
- Archivo inexistente → excepción clara `SourceNotFound`.
- Archivo vacío (0 bytes) → bandera `vacio=True` (P1 lo rechaza después).

**GREEN:** implementar `ManualOperatorAdapter.read_snapshot`. **No** decodifica ni interpreta — solo entrega bytes + metadata de fuente (ruta, tamaño, mtime).

**Verificación:** `pytest tests/test_source_adapter.py -q` pasa. El adaptador nunca modifica el archivo origen.

---

### PASO 5 — `format_detector.py` (P1 — detección de formato) — TDD

**Contrato.** `detect_format(raw_bytes, filename, huella=None) -> FormatSpec`. Detecta:
- **Tipo:** CSV vs Excel (`.xlsx`/`.xls`) por magic bytes + extensión.
- **Encoding (CSV):** cascada `utf-8 → utf-8-sig → cp1252/latin-1` (usar `chardet` como apoyo, pero confirmar decodificación sin reemplazos).
- **Delimitador (CSV):** `,` `;` `|` por conteo de consistencia entre filas (`csv.Sniffer` + verificación de nº de columnas estable).
- **Excel:** resolver **hoja** y **fila de cabecera** por heurística; si `huella` (de `client_config`) existe, usarla directamente.
- Si la heurística **no resuelve con confianza** → devolver `FormatSpec.ambiguo=True` con la mejor propuesta → el processor **escala al operador** (Política §2.4.2/2.4.3), nunca adivina.

**RED — tests (`tests/test_format_detector.py`):**
- CSV `,` utf-8 → detecta coma + utf-8.
- CSV `;` cp1252 con acentos (`Categoría`) → detecta `;` + cp1252, acentos **intactos** (no `Categorâ€¦`).
- CSV `|` → detecta pipe.
- `.xlsx` con cabecera en fila 1 → detecta hoja única + fila 1.
- `.xlsx` con cabecera en fila 3 → propone fila 3.
- `.xlsx` multi-hoja → `ambiguo=True` (requiere confirmación del operador).
- `.xls` legacy → detecta tipo `xls`.
- Archivo binario corrupto / no tabular → `corrupto=True` (P1 rechaza).
- Con `huella` provista → la respeta sin re-detectar.

**GREEN:** implementar la cascada de encoding y la detección de delimitador/hoja. **REFACTOR:** extraer la cascada de encoding a una función pura testeable.

**Verificación:** todos los casos pasan. El acento NO se corrompe en cp1252 (esto bloquearía el dedupe — es crítico, D1/D5).

---

### PASO 6 — `schema_validator.py` (P2 — GATE de estructura) — TDD

**Contrato.** `validate_structure(df, esquema:int) -> StructureResult`. Verifica campos mínimos:
- **Esquema 1:** `fecha_pedido`, `id_cliente`, `id_producto`, `cantidad_solicitada`.
- **Esquema 2:** `fecha`, `id_producto`, `cantidad_producida`, `stock_disponible`, `costo_unitario`, `stock_minimo`.
- Falta ≥ 1 mínimo → `aprobado=False` + lista de faltantes (el processor genera `intake_rejection.json`, **no** crea Bronce).
- Todos presentes → `aprobado=True`; registra campos ideales presentes/faltantes (hasta 17 ideales de DEC-014; no rechazan).
- Tolerancia de nombres: normalizar cabeceras (trim, minúsculas, sinónimos comunes) **sin** alterar Bronce — el matching es lógico, el archivo se copia tal cual.

**RED — tests (`tests/test_schema_validator.py`):**
- Esquema 1 con los 4 mínimos → aprobado.
- Esquema 1 sin `id_producto` → rechazado, faltantes=`[id_producto]`.
- Esquema 1 con mínimos + 6 ideales → aprobado, registra ideales presentes/faltantes.
- Esquema 2 activo con los 6 mínimos → aprobado.
- Cabeceras con espacios / mayúsculas → reconocidas (matching normalizado).
- **Falso negativo / falso positivo = 0** (es el veto D2).

**GREEN + REFACTOR.** **Verificación:** el gate rechaza si y solo si falta un mínimo; nunca al revés.

---

### PASO 7 — `type_validator.py` (P3) + `range_evaluator.py` (P5) — TDD

**`type_validator.py` — contrato:** `validate_types(df, esquema) -> TypeResult`. Por cada campo mínimo **cuenta** (no detiene):
- `fecha_pedido` parseable (acepta varios formatos: `DD/MM/YYYY`, `YYYY-MM-DD`, etc.).
- `id_cliente` / `id_producto` texto no vacío.
- `cantidad_solicitada` numérico ≥ 0.
Devuelve conteo de errores por campo → alimenta el ISD del 020. **Nunca lanza ni filtra filas.**

**`range_evaluator.py` — contrato (P5):** `evaluate_range(df, anios_declarados) -> RangeResult`. Calcula `fecha_min/max`, `dias_cubiertos`, `anios_real`; compara con lo declarado en el 010; discrepancia > 20% → `warning=True`. No detiene.

**RED — tests:**
- `cantidad_solicitada` con 3 negativas y 2 no-numéricas → cuenta 5 errores, NO elimina filas.
- `fecha_pedido` en 3 formatos distintos → todas parseables, 0 errores.
- `id_cliente` con 2 vacíos → cuenta 2 errores.
- Historial real 3.4 años vs declarado 2 → `warning=True`, discrepancia ≈ 70%.
- Historial real 2.1 vs declarado 2 → sin warning (< 20%).

**GREEN + REFACTOR.** **Verificación:** los conteos son exactos y el flujo nunca se detiene por tipos (D3).

---

### PASO 8 — `deduplicator.py` (P4) — TDD

**Contrato.** Clave compuesta `(fecha_pedido, id_cliente, id_producto)`.
- **Batch:** `count_internal_duplicates(df) -> int`. Los duplicados internos se **registran como anomalía, NO se eliminan** (se copian a Bronce; el 020 los contabiliza en Unicidad).
- **Incremental:** `diff_against_bronze(df, manifest_path) -> (df_nuevos, n_excluidos)`. Compara contra la **unión lógica** del Bronce acumulado (vía `_manifest.json` → archivos previos); registros ya existentes se excluyen, **solo los nuevos** se persisten en el archivo de esta entrega.

**RED — tests (`tests/test_deduplicator.py`):**
- Batch con 34 duplicados internos → cuenta 34, `df` devuelto **conserva** las 34 filas (no elimina).
- Incremental: 100 filas nuevas, 30 ya en Bronce previo → devuelve 70 nuevas, `n_excluidos=30`.
- Incremental sin manifest previo (primera entrega incremental) → 0 excluidos, todas nuevas.
- Clave compuesta exacta: misma fecha+cliente pero distinto producto → NO es duplicado.

**GREEN + REFACTOR.** **Verificación:** comportamiento correcto por modo (D4) — batch nunca elimina, incremental nunca re-persiste lo ya existente.

---

### PASO 9 — `bronze_writer.py` (P6) — TDD — **módulo crítico (veto D5)**

**Contrato.**
- `write_bronze(raw_bytes, bronze_dir, mode, delivery_id, esquema) -> BronzeFile`. Escribe el archivo **bit-exacto a la entrada** (los mismos bytes del snapshot; NO se re-serializa desde el DataFrame — eso alteraría el contenido). Nombre: `orders_{batch|incremental}_{YYYYMMDD}.csv` / `inventory_{batch}_{YYYYMMDD}.csv`.
- Calcula **SHA-256** del archivo escrito.
- **Write-once:** si el archivo ya existe con el hash esperado → NO reescribe (idempotencia para recuperación CP-03↔CP-05, §2.5). Si existe con hash distinto → error (no sobrescribe Bronce salvo excepción controlada de rework D5, registrada).
- **Incremental = un archivo inmutable por entrega** + actualización de `_manifest.json` (append a `entregas`). **Nunca** concatena ni reescribe un archivo acumulado.
- Actualiza `_manifest.json` y devuelve la entrada del manifest.

**RED — tests (`tests/test_bronze_writer.py`):**
- Bronce escrito es **byte-idéntico** a la entrada (`hashlib.sha256(entrada) == hashlib.sha256(bronce)`).
- SHA-256 calculado y persistido en el manifest.
- Segundo intento con el mismo contenido → **no reescribe** (mtime intacto / idempotente).
- Segundo intento con contenido distinto y mismo nombre → **error** (protege write-once).
- Incremental: dos entregas → **dos archivos** distintos + 2 entradas en manifest (no un solo archivo reescrito).
- El acento cp1252 sobrevive byte-a-byte en Bronce (encadena con PASO 5).

**GREEN + REFACTOR.** **Verificación:** Bronce bit-exacto, write-once probado criptográficamente. Este módulo materializa el invariante del medallón — sus tests son innegociables (D5 = veto).

---

### PASO 10 — `report_builder.py` (P7) — TDD

**Contrato.** `build_report(...) -> intake_report.json` e `build_intake_log(...) -> fila intake_log`. Consolida todo lo de P1–P6: formato/encoding/delimitador, conteos de filas, campos ideales faltantes, errores de tipo, duplicados, rango temporal, warnings, y el `files` JSONB (path + sha256 + rows + date_range por archivo). La fila `intake_log` lleva `_pendiente_supabase: true` (fallback Fase 1). Conforme a los schemas del PASO 3.

**RED — tests (`tests/test_report_builder.py`):**
- Report contiene todos los conteos y el `warning` de rango cuando aplica (ancla 0.8 del brief: olvidar el warning baja el score).
- `intake_log.files` tiene una entrada por archivo Bronce con su hash.
- Esquema 2 esperado y no recibido → `schema2.status = EXPECTED_NOT_RECEIVED` (no bloquea).
- JSON producido valida contra `schemas/intake_report_schema.json`.

**GREEN + REFACTOR.** **Verificación:** reportes completos (D6); el warning de rango nunca se omite si P5 lo detectó.

---

### PASO 11 — `pipeline.py` — orquestación P1→P8 + emisión del evento — TDD de integración

**Contrato.** `run_intake(client_config, snapshot_path, persistence) -> IntakeResult`. Encadena los módulos en orden estricto y respeta los gates:
1. P1 `source_adapter` + `format_detector` → si corrupto/vacío/ambiguo: rechazo o escalamiento.
2. P2 `schema_validator` (**GATE**) → si rechazo: escribe `intake_rejection.json`, **no** crea Bronce, **no** emite evento, retorna `REJECTED_STRUCTURE`.
3. P3 `type_validator`, P4 `deduplicator`, P5 `range_evaluator` (cuentan, no detienen).
4. P6 `bronze_writer` (Bronce + SHA-256 + manifest).
5. P7 `report_builder` (`intake_report.json` + `intake_log` + `tenants.last_intake_at`).
6. **P8 — emisión del evento como ÚLTIMO paso**: solo si Bronce está completo y verificado, escribe `600_persistence/events/intake_complete.json` con `estado: pendiente`, `bronze_path`, `manifest_path`, `intake_report_path`, `next_harnesses: [020_diagnosis, 025_refinery]`. Si algo falla antes de P8 → **no hay evento**.

**RED — tests (`tests/test_pipeline.py`):**
- Camino feliz (CSV `;` cp1252 válido) → Bronce + manifest + report + intake_log + evento, en ese orden.
- Falta `cantidad_solicitada` → `REJECTED_STRUCTURE`, `intake_rejection.json` creado, **sin** Bronce ni evento.
- Excel multi-hoja sin huella → escala (estado escalamiento), sin Bronce.
- Esquema 2 `tiene_esquema2=true` pero ausente → Bronce del Esquema 1 OK, evento emitido, `schema2=EXPECTED_NOT_RECEIVED`.
- El evento NO existe si el report falló (atomicidad, garantía 1 del handoff).
- Recuperación: Bronce ya escrito con hash esperado + report a medias → completa report+evento sin reescribir Bronce (idempotencia §2.5).

**GREEN + REFACTOR.** **Verificación:** orden P1→P8 respetado; el evento es siempre el último artefacto; el rechazo de estructura nunca produce Bronce.

---

### PASO 12 — Batería de fixtures (~20 archivos) — E9, la mayor palanca de calidad

Crear en `tests/fixtures/` los archivos representativos de cada categoría (§2.7 del brief). Cada fixture tiene un resultado esperado documentado en `tests/fixtures/README.md`:

| Categoría | Fixtures concretos | Resultado esperado |
|-----------|--------------------|--------------------|
| Estructura | `missing_id_producto.csv`; `header_row_3.xlsx`; `extra_columns.csv` | rechazo / cabecera fila 3 / acepta + ideales |
| Formato | `orders_semicolon.csv`; `orders_pipe.csv`; `multi_sheet.xlsx`; `legacy.xls`; `cp1252_acentos.csv` | delimitador/encoding/hoja correctos |
| Tipos | `cantidad_negativa.csv`; `fechas_3_formatos.csv`; `id_cliente_vacio.csv` | conteo exacto, no detiene |
| Duplicados | `dup_internos_batch.csv`; `incremental_repetidos.csv` (+ manifest previo) | batch cuenta/no elimina; incremental excluye |
| Rango | `historial_34_anios.csv` (declarado 2) | warning de rango |
| Bronce | `bronce_bitexacto.csv`; rerun del mismo → no reescribe | bit-exacto + idempotencia |
| Corrupto/vacío | `vacio.csv` (0 bytes); `binario_corrupto.bin` | rechazo inmediato |

**Verificación:** ≥ 20 fixtures existen, cada uno con su expectativa documentada; `pytest -q` ejercita todos y pasa.

---

### PASO 13 — Crear definiciones de agentes (`.claude/agents/`)

Replicar el **modelo conductor** del 010 (DEC-051): governor y orchestrator de un solo paso emiten señales de despacho; la **sesión principal (conductor)** es la única que spawnea. Workers livianos (el peso está en el código + tests).

**13a — `intake-governor.md`** (Instancia A): rituales E10-A (Inicio) / E10-B (Continuación) de §12.1; verifica precondición de entrada (evento `onboarding_discovery_complete` + 010 en `PHASE_COMPLETE`); presenta Sprint Contract (plantilla Sección 3); gestiona gates; decisión final APPROVED/REJECTED leyendo `verdict.json`; despacha con bloque `GOVERNOR_RESULT`. Escribe solo `harness-state.json` + `claude-progress.txt`.

**13b — `intake-orchestrator.md`** (Instancia B): modos PLAN (persiste `orchestration_plan`) y CHECKPOINT (registra CP-01..CP-05); consulta obligatoria de `decisions_library.md` y `lessons_learned.md` (§12.2 paso 2); gestiona el `early_eval` (E9); marca `EXECUTION_COMPLETE`. Escribe solo `execution-state.json`.

**13c — `intake-processor.md`** (Worker): ejecuta `pipeline.py` (P1→P8); reporta a B **solo paths** (E6); usa extended thinking solo en los puntos de juicio (E8: encoding/delimitador/Excel ambiguos); aplica la política de fallback de 3 niveles (§2.3) y de escalamiento (§2.4). Herramientas: `Read`, `Write`, `Bash`/Python.

**13d — `intake-evaluator.md`** (Instancia C): contexto fresco; lee Bronce/manifest/report/intake_log del filesystem; **recalcula el SHA-256** y compara con el manifest; verifica bit-exactitud contra el snapshot; aplica `intake-rubric` (D1–D7); emite `verdict.json` + `metrics_summary.json`; nunca escribe en `harness-state.json` ni contacta a otro agente.

**Verificación:** los 4 agentes existen con frontmatter válido (`name`, `description`, `tools`); el `description` de cada uno deja claro el modo conductor y qué archivo escribe (Single Writer Rule).

---

### PASO 14 — Crear archivos de conocimiento inicial

**`610_knowledge/decisions_library.md`** — resumen ejecutivo de las decisiones que el 015 debe respetar: DEC-012 (modos), DEC-014 (esquemas + campos), DEC-024 (paralelo 020‖025 y su porqué), DEC-044 (Storage local), DEC-047 (tabla `tenants`), DEC-057 (las 10 decisiones del 015). B lo consulta obligatoriamente al inicio.

**`610_knowledge/lessons_learned.md`** — encabezado vacío:

```markdown
# Lecciones Aprendidas — 015 Intake

_Este archivo se completa al cierre del primer ciclo de ejecución del harness._
```

**Verificación:** ambos archivos existen; `decisions_library.md` cubre las 6 decisiones listadas.

---

### PASO 15 — Evaluación temprana (E9) — gate de calidad de construcción

Al completar el primer módulo funcional verificable (`schema_validator` + `bronze_writer`, PASOS 6 y 9), ejercitar la muestra de ~20 fixtures (PASO 12) y que C aplique la rúbrica de fidelidad:
- Score de C ≥ 0.7 → continuar la construcción.
- Score < 0.7 → ajustar la spec/los módulos **antes** de seguir.
- B registra el resultado en `execution-state.json` bajo `early_eval`.

**Verificación:** `early_eval` registrado con score ≥ 0.7; si fue < 0.7, queda anotada la corrección aplicada.

---

### PASO 16 — Prueba de humo / corrida e2e (terminal de prueba)

> **Se ejecuta en `Test_Forecaster/Test_NNN/`** (LEC-053), con un tenant que ya pasó el 010 (P-4, P-5). Esta terminal (repo fuente) aplica fixes si la corrida los revela.

**Insumos de prueba:**
- Tenant con evento `onboarding_discovery_complete` y `client_config` (modo Batch, `tiene_esquema2=false`, historial declarado 2.5 años).
- Un `orders.csv` real-ish: CSV `;`, cp1252 con acentos, ~varios miles de filas, con algunas cantidades negativas y unos duplicados internos sembrados.

**Verificaciones de la corrida (el flujo completo A→B→Worker→C→A):**
1. A detecta Inicio, verifica precondición del 010, presenta Sprint Contract; operador aprueba.
2. B persiste `orchestration_plan`; conductor spawnea `intake-processor`.
3. P1: detecta CSV `;` + cp1252 (acentos intactos). P2: estructura aprobada. CP-01 registrado.
4. P3–P5: errores de tipo contados (negativas), duplicados internos contados, rango evaluado. CP-02.
5. P6: Bronce `orders_batch_{fecha}.csv` byte-idéntico a la entrada + SHA-256 en `_manifest.json`. CP-03.
6. P7: `intake_report.json` + `intake_log` (con `files` JSONB) + `tenants.last_intake_at`. CP-04.
7. P8: `intake_complete.json` emitido como último paso, `estado: pendiente`, `next_harnesses: [020_diagnosis, 025_refinery]`. CP-05 / `EXECUTION_COMPLETE`.
8. C recalcula el SHA-256 (coincide), verifica bit-exactitud, aplica rúbrica → APPROVED ≥ 0.80.
9. A marca `PHASE_COMPLETE`; commit `feat(015-intake): bronze creado — {tenant_id} entrega {delivery_id}`.
10. **Camino de rechazo (segunda mini-corrida):** entregar un CSV sin `cantidad_solicitada` → `intake_rejection.json`, sin Bronce, sin evento, A notifica al operador (HOLD).

**Verificación:** los 9 puntos del camino feliz pasan + el punto 10 (rechazo) se comporta como flujo normal de entrada, no como error del sistema.

---

## Verificación final — Criterio de Done del Plan

El plan de construcción está completo cuando:

- [ ] Las carpetas del harness existen (PASO 1)
- [ ] Los 3 archivos de estado tienen esquemas válidos con CP-01..CP-05 (PASO 2)
- [ ] Los 5 schemas/skills existen y validan; la rúbrica reproduce D1–D7 + vetos (PASO 3)
- [ ] Los 8 módulos del pipeline existen con tests que pasan (`pytest -q` verde) (PASOS 4–10)
- [ ] `pipeline.py` orquesta P1→P8 con el evento como último paso (PASO 11)
- [ ] ≥ 20 fixtures con expectativa documentada, todos ejercitados (PASO 12)
- [ ] Los 4 agentes existen con frontmatter válido y modo conductor (PASO 13)
- [ ] `decisions_library.md` + `lessons_learned.md` existen (PASO 14)
- [ ] `early_eval` registrado con score ≥ 0.7 (PASO 15)
- [ ] La corrida e2e pasa el camino feliz (9 puntos) + el camino de rechazo (PASO 16)

---

## Qué viene después (fuera de este plan)

1. Registrar hallazgos de la corrida e2e en `610_knowledge/lessons_learned.md` y en `progress/lessons.md`.
2. Cualquier ajuste menor no bloqueante detectado → registrar como tarea diferida (como se hizo con el 010).
3. Iniciar el plan de trabajo del **020 Diagnosis** (brief T-061) y del **025 Refinery** (brief T-063) — los dos consumidores paralelos del `intake_complete`.
4. La migración de la rebanada de persistencia a Fase 3 (Supabase Storage + `intake_log` real + Realtime para el fan-out) se planifica por separado junto con la Capa 1 (T-171); no bloquea la corrida del 015 en Fase 1.

---

## Notas de construcción

- **TDD real, no decorativo (DEC-057 decisión 3).** Cada módulo de los PASOS 4–11 se construye RED → GREEN → REFACTOR: el test se escribe y falla **antes** de la implementación. Es la diferencia central con el 010, que no tenía tests de código.
- **El `bronze_writer` es bit-exacto desde los bytes del snapshot, no desde el DataFrame.** Re-serializar un DataFrame a CSV cambia comillas, separadores decimales y orden — eso rompería D5. Bronce = los mismos bytes que entraron; el DataFrame es solo para validar/contar.
- **El acento cp1252 es el canario.** Si los acentos se corrompen en la detección de encoding (PASO 5), `id_cliente`/`id_producto` cambian y el dedupe miente. Cualquier fixture con acentos debe sobrevivir byte-a-byte hasta Bronce.
- **El evento es siempre el último artefacto (P8).** Ningún test ni corrida puede emitir `intake_complete` antes de que Bronce + reportes existan y verifiquen. Es la garantía de atomicidad del handoff.
- **Fallback Fase 1 idéntico al 010:** todo lo que sería Supabase se escribe como JSON local con `_pendiente_supabase: true`; el Storage Bronce vive en `1000_storage_local/tenants/{id}/1000_data/005_bronze/` (DEC-044).
- **No se diseña cobro:** T-030 (pesos ITO) y T-031 (pasarela) **no** bloquean el 015 (DEC-057 decisión 9). La rebanada de persistencia del intake es independiente del módulo de subscriptions/payments.
- **El operador Triple S es humano.** El gate de aprobación del Sprint Contract y la confirmación de hoja/cabecera de Excel ambiguo (1ª entrega) requieren su intervención explícita — A no se auto-aprueba.

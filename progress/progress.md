# Estado del Proyecto — FARO (Harness Forecaster)

## Última actualización
2026-06-13 (sesión 42)

---

## LEER PRIMERO — estado en una frase

**El harness 010 Discovery está TERMINADO. La CONSTRUCCIÓN del harness 015 Intake (T-070) está EN CURSO siguiendo `plan/015_intake.md` (16 pasos). Hechos: PASOS 1–3 (andamiaje, estado, 5 contratos) y módulos PASO 4 (`source_adapter`), 5 (`format_detector`, canario cp1252), 6 (`schema_validator`, GATE veto D2), 7 (`type_validator` P3 + `range_evaluator` P5), 8 (`deduplicator` P4), 9 (`bronze_writer` P6, veto D5), 10 (`report_builder` P7), 11 (`pipeline.py` — orquestación P1→P8 con `run_intake`, evento como ÚLTIMO artefacto) y 12 (batería de 20 fixtures E9 + `test_fixtures.py`) con TDD real — 85 tests verdes (`pytest -q`). PASO 13 ✅ — los 4 agentes (`intake-governor/orchestrator/processor/evaluator`) en `.claude/agents/`, modelo conductor (DEC-051). PASO 14 ✅ — conocimiento inicial curado como **plantillas** en `templates/015_intake/`; el `intake-governor` E10-A.8 las copia a `610_knowledge/` en runtime. PASO 15 ✅ — early-eval (E9): C aplicó la `intake-rubric` sobre los 20 fixtures + verificación independiente del camino feliz (SHA-256 recalculado == manifest, Bronce bit-exacto, evento como último artefacto) → **score 1.00, APPROVED** (supera el gate de construcción ≥ 0.7 y el operacional ≥ 0.80); evidencia en `scripts/015_intake/tests/EARLY_EVAL.md`. De paso se corrigió un bug de higiene de test (`.gitattributes` contado como fixture; 85 tests verdes). ➡️ **Los PASOS 1–15 del 015 están TERMINADOS; solo falta el PASO 16 (corrida e2e en la terminal de prueba), que está BLOQUEADO por el rediseño de despliegue acordado en la sesión 42 (DEC-058). El SIGUIENTE PASO REAL es T-185: `deploy-harness.ps1` no copia el paquete `pipeline/`, así que el `intake-processor` no encontraría el código en el proyecto de prueba.** Ver el bloque "⭐ SIGUIENTE PASO REAL — Rediseño de despliegue" en `tasks.md` (T-185..T-190) y DEC-058. El detalle paso a paso del 015 vive en `tasks.md` (bloque "Construcción del 015 — desglose por PASO").**

---

## Qué es FARO (contexto mínimo)

**FARO** (Forecasting Agentic Results & Operations) es un sistema agéntico de pronóstico de demanda B2B. Modelo de negocio **Service as a Software**: **Sabbia Solutions & Software (Triple S)** opera todo y entrega pronósticos como servicio a empresas manufactureras. Las reglas de negocio completas (precios M/L/XL, ciclo de cobro, arquitectura medallón Bronce/Plata/Oro, SLAs, retención) están en **`CLAUDE.md`** — leerlo es obligatorio antes de implementar.

El sistema se construye como una cadena de **11 harnesses** (010 Discovery → 015 Intake → 020 Diagnosis → 025 Refinery → 030 Trainer → 035 Predictor → 040 Publisher → 045 Monitor → 050 Lifecycle → 055 Command → 060 Simulator). Se construyen en orden; cada harness produce un handoff que el siguiente consume.

---

## Harness 010 Discovery — TERMINADO

Captura el contexto del cliente (entrevistas multi-stakeholder), calcula el ITO (categoría M/L/XL), evalúa el cold start, genera los deliverables de onboarding y emite el evento que arranca el 015.

- **Validado end-to-end** en 3 corridas e2e: Test_004A (refactor conductor), Test_005_Flexempaque (APPROVED 1.0) y **Test_006 (APPROVED 1.0, ciclo completo con gates CP-03/CP-04 + evaluador C ejercitados)**.
- Arquitectura: **modelo conductor** (DEC-051) — la sesión principal (conductor) es la única que spawnea agentes; el governor y el orchestrator solo gestionan estado y emiten señales de despacho. El interviewer corre inline.
- Agentes en `.claude/agents/` (governor, orchestrator, interviewer, synthesizer, analyst, configurator, evaluator); skills en `.claude/skills/`; comandos FARO en `commands/`; flujo en `flows/010_discovery_flow.md`; brief de referencia en `brief/010_discovery.md`.
- **Ajustes menores NO bloqueantes diferidos** (no impiden avanzar): T-172 (transliteración del slug), T-178 (calibración ITO/T-030), T-179 (campo de tolerancia de error asimétrica), T-180 (timestamps internos del interviewer), y validar T-181 (timestamps de bitácora, ya aplicado) en una corrida futura. Detalle en `tasks.md`.

---

## CONSTRUCCIÓN DEL 015 EN CURSO (T-070) — dónde vamos y qué sigue

**El plan de construcción está escrito** (`plan/015_intake.md`, T-183 implementada) — 16 pasos, derivado de `brief/015_intake.md`. La construcción se ejecuta paso a paso. **Estado por paso, autoritativo, en `tasks.md`** (bloque "Construcción del 015 — desglose por PASO").

**Hecho hasta ahora (sesiones 39–40):**
- **PASO 1 ✅** — Andamiaje en el **repo fuente** (no carpetas runtime): `scripts/015_intake/{pipeline,tests/fixtures}/` (con `README.md` y `pipeline/__init__.py`) y `templates/015_intake/schemas/`. Entorno verificado: Python 3.12.10 + pandas/openpyxl/chardet/pytest; `xlrd` instalado (2.0.2, solo `.xls`).
- **PASO 2 ✅ (absorbido)** — Los archivos de estado son **runtime** (los crea E10-A en la terminal de prueba); su estructura quedó documentada en la skill `intake-state-schema`, no como archivos en el repo fuente.
- **PASO 3 ✅** — Los **5 contratos de referencia**: 3 JSON-schema en `templates/015_intake/schemas/` (`intake_report_schema.json`, `manifest_schema.json`, `intake_log_schema.json`) + 5 skills en `.claude/skills/` (`intake-report-schema`, `intake-manifest-schema`, `intake-log-schema`, `intake-rubric`, `intake-state-schema`).

- **PASO 4 ✅** — `source_adapter.py` (P1 recepción): `ManualOperatorAdapter.read_snapshot(path) -> Snapshot(raw_bytes, formato_declarado, source_metadata, vacio)`; interfaz `SourceAdapter` (ABC) documenta conectores futuros sin construirlos; `SourceNotFound`. 7 tests + `pytest.ini` (`pythonpath = .`).
- **PASO 5 ✅** — `format_detector.py` (P1 detección): `detect_format(raw_bytes, filename, huella=None) -> FormatSpec`. Tipo por magic bytes (zip→xlsx, OLE2→xls), encoding por cascada estricta (utf-8/utf-8-sig/cp1252/latin-1 — **el canario cp1252 sobrevive byte-a-byte**), delimitador por consistencia de columnas, hoja/fila-cabecera Excel; `ambiguo=True` escala al operador, `corrupto=True` (byte nulo) rechaza, `huella` se respeta sin re-detectar. 11 tests verdes.
- **PASO 6 ✅** — `schema_validator.py` (P2 GATE, veto D2): `validate_structure(df, esquema) -> StructureResult`. Mínimos Esquema 1 (4) / Esquema 2 (6) + 17 ideales del Esquema 1 (DEC-014). Matching normalizado (trim/acentos/espacios→'_') + sinónimos curados; igualdad por nombre canónico, **nunca substring** (D2: falso positivo = falso negativo = 0). Rechaza ⟺ falta un mínimo; ideales faltantes = déficit que no rechaza. 9 tests verdes.
- **PASO 7 ✅** — `type_validator.py` (P3): `validate_types(df, esquema) -> TypeResult` cuenta errores por campo (fecha no parseable, texto vacío, num<0/no-numérico) sin filtrar filas (D3); expone `parse_fecha`/`_a_numero`/`_resolver_columna`. `range_evaluator.py` (P5): `evaluate_range(df, anios_declarados, campo_fecha) -> RangeResult` calcula fecha_min/max, días, años reales; discrepancia > 20% vs declarado → `warning=True`; ignora fechas no parseables. 11 tests verdes.
- **PASO 8 ✅** — `deduplicator.py` (P4): clave compuesta `(fecha_pedido, id_cliente, id_producto)` normalizada a string. `count_internal_duplicates(df)` (batch) cuenta sin eliminar; `diff_against_bronze(df, manifest_path) -> (df_nuevos, n_excluidos)` (incremental) excluye lo ya presente leyendo la unión lógica del Bronce vía `_manifest.json` (relee archivos previos cp1252 con el detector). 5 tests verdes.
- **PASO 9 ✅** — `bronze_writer.py` (P6, **veto D5**): `write_bronze(raw_bytes, bronze_dir, mode, delivery_id, esquema, …) -> BronzeFile`. Escribe los **bytes del snapshot** (bit-exacto, no re-serializa el DataFrame); nombre `orders_/inventory_{mode}_{delivery_id}.{ext}`; SHA-256 en `_manifest.json`; **write-once** idempotente (mismo hash → no reescribe, `rewritten=False`) y `BronzeImmutabilityError` si el nombre existe con hash distinto; incremental = un archivo por entrega + append a `entregas` (manifest no se duplica). 8 tests verdes.
- **PASO 10 ✅** — `report_builder.py` (P7): `build_report(...) -> intake_report` (formato, conteos, errores de tipo, duplicados, rango, campos ideales faltantes; warning de rango duplicado en `rango_declarado_vs_real` + lista `warnings`) y `build_intake_log(...) -> fila intake_log` (`files` JSONB con path+sha256+rows+date_range por archivo, `_pendiente_supabase: true`). Conforme a los schemas del PASO 3. 7 tests verdes.
- **PASO 11 ✅** — `pipeline.py` (orquestación P1→P8): `run_intake(client_config, snapshot_path, Persistence) -> IntakeResult`. Encadena los módulos en orden estricto. Gates: P1 vacío/corrupto → `WORKER_FAILED` (+`intake_rejection.json`), P1 ambiguo (Excel multi-hoja sin huella) → `PENDING_OPERATOR_INPUT` (escalamiento, sin Bronce), P2 falta mínimo → `REJECTED_STRUCTURE` (+`intake_rejection.json`, **sin Bronce ni evento**). P3/P4/P5 cuentan sin detener; P6 Bronce bit-exacto desde los **bytes del snapshot**; P7 report+intake_log; **P8 evento `intake_complete` como ÚLTIMO artefacto** (atomicidad: si el report falla, no hay evento). Idempotencia de recuperación (re-correr no reescribe Bronce). Esquema 2 ausente → `EXPECTED_NOT_RECEIVED`, no bloquea. 9 tests verdes. **Decisión de reconciliación:** el brief P4 dice "en incremental solo los nuevos se persisten", pero D5 (Bronce bit-exacto) es veto duro → se mantiene la bit-exactitud y `diff_against_bronze` se usa **solo para el conteo** `vs_bronce_previo`; la deduplicación lógica del histórico vive en el manifest (documentado en el docstring de `pipeline.py`).
- **PASO 12 ✅** — Batería de 20 fixtures (E9) en `scripts/015_intake/tests/fixtures/` (generador reproducible `_build_fixtures.py` + `README.md` con la expectativa por fixture) y `tests/test_fixtures.py` (18 tests). Cubre estructura (rechazo/ideales/cabecera fila 3), formato (`,`/`;`/`|`/utf-8-sig/cp1252-canario/xlsx/xls real vía xlwt build-time/multi-hoja→escala), tipos (negativas+no-numéricas, 3 formatos de fecha, vacíos), duplicados (batch cuenta/no elimina; incremental excluye), rango (warning), Bronce (bit-exacto+idempotente) y corrupto/vacío (`WORKER_FAILED`). **Hallazgo diferido T-184:** `type_validator` no cuenta celdas numéricas vacías (`NaN`) como error de tipo — no bloqueante.

**PASO 13 ✅ (sesión 42)** — Los 4 agentes en `.claude/agents/intake-{governor,orchestrator,processor,evaluator}.md`, modelo conductor (DEC-051). Claves de diseño, adaptadas a que el 015 tiene un **solo Worker** que corre todo `run_intake` (P1→P8) en una llamada: el **governor** (modos `INIT/EXECUTE/POST_EXECUTION/POST_AUDIT/CLOSE/SUSPEND`) verifica la precondición del 010 en E10-A, despacha de a un paso vía bloques `dispatch` (`agent`/`prompt`/`then`), y su tabla EXECUTE tiene solo 7 filas (PLAN → WORKER → CHECKPOINT → uno de EXECUTION_COMPLETE/REJECTED_STRUCTURE/PENDING_OPERATOR_INPUT/EXECUTION_FAILED). El **orchestrator** (PLAN + un único `CHECKPOINT` que registra CP-01..CP-05 de una vez a partir del `PROCESSOR_RESULT.estado`, porque el pipeline es atómico). El **processor** (Worker) localiza el paquete `pipeline`, ejecuta `run_intake` vía un runner Python efímero que imprime el `IntakeResult` como JSON, y reporta `PROCESSOR_RESULT` con paths+conteos (E6); el juicio LLM solo aparece en `PENDING_OPERATOR_INPUT`. El **evaluator** (C) recalcula el SHA-256 y verifica bit-exactitud contra el snapshot (núcleo de D5), aplica `intake-rubric` y emite `verdict.json`. Frontmatter validado con PyYAML (cuidado: `: ` en descripciones multilínea rompe el YAML — usar `—`).

**PASO 14 ✅ (sesión 42)** — Conocimiento inicial. El contenido curado se materializó como **dos plantillas** en `templates/015_intake/` (no como archivos runtime en el repo fuente, respetando LEC-067): `decisions_library_template.md` (Parte A = fundamentos de diseño fijos resumiendo DEC-012/014/024/044/047/057 que B consulta en Modo PLAN; Parte B = log append-only por tenant, patrón `discovery-knowledge-schema`, vacío) y `lessons_learned_template.md` (encabezado + formato de entrada). El `deploy-harness.ps1` ya las copia a `{destino}/015_intake/templates/`; el `intake-governor` E10-A.8 se reescribió para **copiar** estas plantillas a `610_knowledge/{decisions_library,lessons_learned}.md` en runtime (sin reescribir si existen, con fallback a encabezado mínimo si la plantilla falta).

**PASO 15 ✅ (sesión 42)** — Early-eval (E9). C aplicó la `intake-rubric` (7 dimensiones) sobre la batería de 20 fixtures (PASO 12) y verificó **independientemente** el camino feliz (canario `cp1252_acentos.csv`): recálculo del SHA-256 que coincide con el manifest, Bronce byte-idéntico a la entrada, write-once (`rewritten=False` al re-correr), reporte completo, y evento `intake_complete` como último artefacto con `next_harnesses:[020,025]`. **Las 7 dimensiones = 1.0 → score global 1.00, sin vetos, APPROVED.** Evidencia en `scripts/015_intake/tests/EARLY_EVAL.md`. Hallazgo de higiene corregido en el paso: `test_existen_20_fixtures` contaba el `.gitattributes` (intencional para proteger los fixtures byte-sensibles de la normalización de Git) como un fixture → ahora excluye dotfiles; **85 tests verdes**.

**PASO 16 (pendiente, BLOQUEADO)** — Prueba de humo / corrida e2e en `Test_Forecaster/Test_NNN/` (terminal de prueba, LEC-053). Flujo completo A→B→Worker→C→A con un tenant que ya pasó el 010 (P-4, P-5): consumir el evento `onboarding_discovery_complete`, presentar Sprint Contract, montar Bronce bit-exacto + manifest, emitir `intake_complete`, y C aprueba ≥ 0.80. Incluye la mini-corrida de rechazo (CSV sin `cantidad_solicitada` → `intake_rejection.json`, sin Bronce ni evento). Es el ÚLTIMO paso del plan de construcción del 015. **No se puede ejecutar hasta resolver T-185** (el deploy no lleva el `pipeline/` al proyecto de prueba). Para el dataset de prueba: un `orders.csv` `;` cp1252 con acentos, varios miles de filas, con negativas y duplicados internos sembrados (+ un CSV sin `cantidad_solicitada` para el rechazo); el tenant debe tener el handoff del 010 (evento + `client_config` + carpeta Bronce) — ofrecí generar el dataset, pendiente de hacerlo en la corrida.

---

## ⭐ SIGUIENTE PASO REAL (definido sesión 42, por ejecutar) — Rediseño de despliegue: carga perezosa por harness (DEC-058)

**Decisión de la sesión 42** (ver **DEC-058** completa). El operador pidió que los agentes/skills de un harness NO se instalen todos de golpe (Claude Code carga la **descripción** de cada agente/skill al iniciar sesión → contexto inútil en la fase activa). Se acordó **carga perezosa just-in-time por fase**, modelo **"switch"** (instalar el nuevo harness + **podar** el anterior — su handoff ya vive en disco), y un **comando conductor genérico `/faro-run`** (Opción B) que detecta el único `*-governor.md` instalado y lo conduce.

**UX objetivo por transición:** el harness termina → el sistema pregunta *"¿despliego el {siguiente}?"* → operador dice **"sí"** → el conductor ejecuta `deploy-harness.ps1 -Harness {N}` (+ poda) vía `$env:FARO_HOME` → instruye **reiniciar Claude Code** (los agentes se escanean al iniciar sesión; el reinicio activa el nuevo harness y resetea el contexto al mínimo) → operador reinicia y corre **`/faro-run`**.

**Plan de implementación (T-185..T-190 en `tasks.md`), en orden:**
1. **T-185 (EMPEZAR AQUÍ, desbloquea el PASO 16):** `deploy-harness.ps1` debe copiar `scripts/{NNN}_{prefijo}/pipeline/` recursivo (hoy `:158` solo copia archivos de primer nivel).
2. **T-186:** poda del harness previo (switch). Matiz DEC-058: no podar los transversales 045/050/055 cuando existan.
3. **T-187:** mapa "harness actual → siguiente" (cadena DEC-026; bifurcación 020‖025 ofrece ambos).
4. **T-188:** `faro-setup.ps1` instala solo el 010 (delega a `deploy-harness -Harness 010`); conserva andamiaje + `FARO_HOME`.
5. **T-189:** crear `commands/faro-run.md` genérico (reusar patrón de `commands/faro-discovery.md`); deprecar `/faro-discovery`.
6. **T-190:** el cierre del governor (en `conductor_loop.md`, lo ejecuta la sesión principal — DEC-051) ofrece el salto + instrucción de reinicio.

**Recomendación de secuencia:** hacer **T-185 primero** (es chico y desbloquea el e2e del 015); luego, si se quiere, correr el PASO 16 del 015 con el deploy ya funcional; y completar T-186..T-190 (el modelo switch completo) en la misma o siguiente sesión.

---

### Orientación al código del 015 (para una sesión nueva)

**Dónde está todo:** `scripts/015_intake/` — `pipeline/` (módulos), `tests/` (pytest), `tests/fixtures/` (20 fixtures E9 + `_build_fixtures.py` + `README.md`), `pytest.ini` (`pythonpath = .`). Schemas de referencia en `templates/015_intake/schemas/`.

**Cómo correr los tests** (desde `scripts/015_intake/`):
```
cd "scripts/015_intake" && python -m pytest -q
```
Estado actual: **85 tests verdes**. Entorno: Python 3.12.10 + pandas/openpyxl/xlrd/chardet/pytest (+ xlwt solo build-time para generar el fixture `.xls`).

**Mapa P→módulo→función pública** (todos en `pipeline/`):

| Proceso | Módulo | Entrada → Salida principal |
|---|---|---|
| P1 recepción | `source_adapter.py` | `ManualOperatorAdapter().read_snapshot(path) -> Snapshot(raw_bytes, formato_declarado, source_metadata, vacio)`; excepción `SourceNotFound` |
| P1 detección | `format_detector.py` | `detect_format(raw_bytes, filename, huella=None) -> FormatSpec(tipo, encoding, delimitador, hoja, fila_cabecera, hojas_disponibles, ambiguo, corrupto, fuente)` |
| P2 GATE | `schema_validator.py` | `validate_structure(df, esquema) -> StructureResult(aprobado, campos_minimos_*, campos_ideales_*, mapeo)`; constantes `MINIMOS_ESQUEMA1/2`, `IDEALES_ESQUEMA1`, helper `_canonico` |
| P3 tipos | `type_validator.py` | `validate_types(df, esquema) -> TypeResult(errores:dict, filas_evaluadas)`; helpers puros `parse_fecha`, `_a_numero`, `_resolver_columna` |
| P5 rango | `range_evaluator.py` | `evaluate_range(df, anios_declarados, campo_fecha="fecha_pedido") -> RangeResult(fecha_min/max, dias_cubiertos, anios_real, discrepancia_pct, warning)` |
| P4 dedupe | `deduplicator.py` | `count_internal_duplicates(df) -> int`; `diff_against_bronze(df, manifest_path) -> (df_nuevos, n_excluidos)`; `keys_from_df`, `load_bronze_keys` |
| P6 Bronce | `bronze_writer.py` | `write_bronze(raw_bytes, bronze_dir, mode, delivery_id, esquema, *, tenant_id, extension, rows, rango, timestamp) -> BronzeFile(path, archivo, sha256, rewritten, manifest_entry)`; excepción `BronzeImmutabilityError` |
| P7 reportes | `report_builder.py` | `build_report(...) -> dict` (intake_report); `build_intake_log(*, bronze_files, ...) -> dict` |
| P1–P8 orquestación | `pipeline.py` | `run_intake(client_config, snapshot_path, persistence) -> IntakeResult(estado, bronze_files, report, report_path, manifest_path, intake_log, event, event_path, rejection, escalation)`; `Persistence(bronze_dir, events_dir)`; estados `EXECUTION_COMPLETE`/`REJECTED_STRUCTURE`/`PENDING_OPERATOR_INPUT`/`WORKER_FAILED` |

**Invariantes de código que el PASO 11 debe respetar** (no romper al integrar):
- **Resolución de nombres canónica y compartida:** P2/P3/P4/P5 resuelven columnas vía `_canonico`/`_resolver_columna` (normaliza trim/acentos/espacios + sinónimos). Reusar, no reimplementar.
- **Bronce bit-exacto desde los BYTES del snapshot**, nunca re-serializando el DataFrame (rompería D5). El DataFrame solo valida/cuenta.
- **El evento es el ÚLTIMO artefacto (P8).** Si algo falla antes, no se emite `intake_complete`. Rechazo de estructura (P2) → `intake_rejection.json`, sin Bronce ni evento, estado `REJECTED_STRUCTURE`.
- **Write-once idempotente:** re-correr con el mismo Bronce no reescribe (`rewritten=False`) → soporta recuperación CP-03↔CP-05.
- **El canario cp1252** debe sobrevivir byte-a-byte de P1 a Bronce (si se corrompe el encoding, el dedupe miente).
- **Fallback Fase 1:** lo que sería Supabase se escribe como JSON local con `_pendiente_supabase: true`; Storage Bronce en `1000_storage_local/tenants/{id}/1000_data/005_bronze/` (DEC-044).

---

> **Ajuste de plan importante (LEC-067):** el PASO 1 y el PASO 2 del plan heredaron de `plan/010_discovery.md` (escrito antes de LEC-053) una lista de carpetas **runtime** que NO van en el repo fuente. Se corrigió el plan: en el repo fuente solo vive lo que se construye (código en `scripts/015_intake/`, plantillas/schemas en `templates/015_intake/`, agentes/skills en `.claude/`); las carpetas `600_persistence/`, `605_eval/`, etc. las crea E10-A durante la corrida e2e en la terminal de prueba.

**Qué hace el 015:** consume el handoff del 010 (`client_config` + evento `onboarding_discovery_complete`) e ingiere los datos históricos del cliente para montar la capa **Bronce** (copia exacta intocable, write-once + SHA-256), emitiendo `intake_complete` que dispara 020 ‖ 025 en paralelo. Pipeline determinístico P1→P8, un único worker (`intake-processor`) con módulos de código testeables; el LLM solo interviene en los puntos de juicio (encoding/delimitador/Excel). Las 10 decisiones de diseño que lo rigen están en **DEC-057**.

**Insumos disponibles:**
- **Plan de construcción (la hoja de ruta): `plan/015_intake.md`** — 16 pasos con verificación.
- Brief de diseño: `brief/015_intake.md` (7 secciones, P1→P8, rúbrica).
- Documentación funcional: `harnesses/015_intake.md`.
- Guía de persistencia: `documents/supabase_persistence_guide.md` (§6 Capa 1, §8 medallón, §10 conmutación).
- Patrón de referencia: `brief/010_discovery.md`, `plan/010_discovery.md` y los agentes/skills `discovery-*` ya construidos.

**Persistencia (DEC-055):** la **Capa 1 de persistencia** (esquema operacional Supabase: tenants/contacts/client_config/subscriptions/events + adaptador fallback) **se acopla al diseño del 015**, no se construye antes en aislamiento (el 015 es su primer consumidor real). Guía: `documents/supabase_persistence_guide.md`. Mientras tanto los agentes escriben JSON local con `_pendiente_supabase: true` (fallback Fase 1). Dos decisiones abiertas frenan parte del detalle de cobro: T-031 (pasarela de pagos) y T-030 (pesos del ITO).

---

## Convenciones e invariantes del proyecto

- **Idioma:** documentación en **español**; nombres de archivo en **inglés**, contenido en español.
- **Arquitectura de dos terminales (LEC-053)** para pruebas e2e: la corrida vive en una carpeta de prueba dedicada (`Test_Forecaster/Test_NNN/`); esta carpeta `Harness_Forecaster` es el **repo fuente / soporte** (aplica fixes, audita artefactos). El diseño/construcción de un harness (escribir su brief) SÍ se hace en esta terminal.
- **Dónde está cada cosa:** decisiones formales en `progress/decisions.md` (última: DEC-057); lecciones en `progress/lessons.md` (última: LEC-068); registro atómico de tareas en `progress/tasks.md`.
- **Historial completo del harness 010** (todo el detalle de las sesiones 1–37, hallazgos y fixes) archivado en **`progress/history/`** (`progress_harness010.md`, `tasks_harness010.md`, `refactor_conductor_T166.md`). Consultar ahí si se necesita el porqué de algún fix del 010.
- **Repositorio GitHub:** `https://github.com/jdrodriguez1000/Harness_Forecaster.git` (rama `main`).

---

## Instrucciones para agentes (resumen de CLAUDE.md)

1. Leer **`CLAUDE.md`** (reglas de negocio) y este `progress.md` al inicio.
2. Consultar `progress/decisions.md` antes de proponer arquitecturas — puede haber una decisión ya tomada.
3. Consultar `progress/lessons.md` antes de implementar para no repetir errores.
4. Registrar toda tarea nueva en `progress/tasks.md` y mantener su estado actualizado.
5. Actualizar este `progress.md` al cerrar una sesión de trabajo significativa.

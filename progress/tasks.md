# Tareas del Proyecto — FARO (Harness Forecaster)

Estados posibles: `no iniciada` | `en ejecución` | `implementada`

> **El registro completo de tareas ya implementadas** (todo el harness 010, sesiones 1–37) está archivado en **`progress/history/tasks_harness010.md`**. Este archivo conserva solo lo **pendiente** y el **siguiente paso**.

---

## ⭐ SIGUIENTE PASO

| ID | Tarea | Estado |
|---|---|---|
| **T-060** | **Crear `brief/015_intake.md` — Plan de Construcción del harness 015 Intake.** 7 secciones siguiendo el patrón de `brief/010_discovery.md`. Precedido por una sesión de entendimiento (Fase 0 + E11) que cerró 10 decisiones de diseño (ver **DEC-057**): formatos, fuente agnóstica + costura de adaptador, peso agéntico (A/B/C con workers livianos + TDD real), worker único, esquemas independientes, inmutabilidad write-once+SHA-256, incremental = archivo/entrega + manifest, Excel con memoria, persistencia (rebanada del intake, sin cobro), handoff atómico a 020‖025. Brief redactado y persistido. | `implementada` |
| **T-183** | **Crear `plan/015_intake.md` — Plan de Trabajo de construcción del harness 015 Intake.** Plan paso a paso siguiendo el patrón de `plan/010_discovery.md`, derivado de `brief/015_intake.md`. Adapta el formato a un pipeline determinístico con **TDD real**: introduce pytest + estructura de tests + ~20 fixtures (E9), un paso por módulo de código (RED→GREEN), agentes A/B/C+Worker, schemas/skills, conocimiento, early-eval y smoke test e2e. **16 pasos en `plan/015_intake.md`.** | `implementada` |
| **T-070** | **Construir el harness 015 Intake** según `brief/015_intake.md` y `plan/015_intake.md`: agentes `intake-governor`, `intake-orchestrator`, `intake-processor`, `intake-evaluator`; skills/schemas (`intake-report-schema`, `intake-manifest-schema`, `intake-log-schema`, `intake-rubric`, `intake-state-schema`); módulos de código del pipeline P1→P8 con TDD real + ~20 fixtures (E9). Acopla la rebanada de persistencia del intake (`intake_log` + Storage Bronce + evento) con fallback JSON Fase 1. Ver DEC-057. **Desglose por PASO abajo.** | `en ejecución` |

### Construcción del 015 — desglose por PASO (T-070)

Sigue `plan/015_intake.md`. Esta tabla es el estado autoritativo de avance de la construcción.

| PASO | Qué | Entregable (repo fuente) | Estado |
|---|---|---|---|
| 1 | Andamiaje de carpetas | `scripts/015_intake/{pipeline,tests/fixtures}/` + `templates/015_intake/schemas/` (README + `__init__.py`); entorno verificado (`xlrd` instalado) | `implementada` |
| 2 | Archivos de estado | **Absorbido en PASO 3e** — son runtime (los crea E10-A); estructura en `intake-state-schema` | `implementada` |
| 3 | Schemas + skills (contratos) | 3 JSON en `templates/015_intake/schemas/` + 5 skills `.claude/skills/intake-*` | `implementada` |
| 4 | `source_adapter.py` (P1 recepción) + test | `scripts/015_intake/pipeline/source_adapter.py` + `tests/test_source_adapter.py` (7 tests verdes) + `pytest.ini` | `implementada` |
| 5 | `format_detector.py` (P1 CSV delim/encoding, Excel hoja/cabecera) + test | `pipeline/format_detector.py` + test (canario acentos cp1252) — 11 tests verdes; `_detect_encoding`/`_detect_delimiter` puras (REFACTOR) | `implementada` |
| 6 | `schema_validator.py` (P2 GATE, veto D2) + test | `pipeline/schema_validator.py` + test — 9 tests verdes; matching normalizado (acentos/sinónimos), igualdad canónica sin substring (D2: FP=FN=0) | `implementada` |
| 7 | `type_validator.py` (P3) + `range_evaluator.py` (P5) + tests | `pipeline/{type_validator,range_evaluator}.py` + tests — 11 tests verdes; cuentan errores/rango sin detener (D3); `parse_fecha`/`_a_numero` puras | `implementada` |
| 8 | `deduplicator.py` (P4 batch/incremental) + test | `pipeline/deduplicator.py` + test — 5 tests verdes; clave compuesta normalizada, batch cuenta/no elimina, incremental excluye vía unión lógica del manifest (relee Bronce cp1252) | `implementada` |
| 9 | `bronze_writer.py` (P6 write-once + SHA-256 + manifest, veto D5) + test | `pipeline/bronze_writer.py` + test — 8 tests verdes; bit-exacto desde bytes del snapshot, SHA-256 en manifest, write-once idempotente + `BronzeImmutabilityError`, append por entrega | `implementada` |
| 10 | `report_builder.py` (P7 intake_report + intake_log) + test | `pipeline/report_builder.py` + test — 7 tests verdes; consolida P1–P6, warning de rango en `rango_declarado_vs_real` + `warnings`, `files` JSONB por archivo, conforme a schemas del PASO 3 | `implementada` |
| 11 | `pipeline.py` (orquestación P1→P8 + P8 evento) + test integración | `pipeline/pipeline.py` + `tests/test_pipeline.py` — 9 tests verdes; `run_intake(client_config, snapshot_path, Persistence)`; gates P1 (vacío/corrupto→WORKER_FAILED, ambiguo→PENDING_OPERATOR_INPUT) y P2 (REJECTED_STRUCTURE, sin Bronce ni evento); evento como ÚLTIMO artefacto; idempotencia de recuperación; esquema2 EXPECTED_NOT_RECEIVED no bloquea | `implementada` |
| 12 | ~20 fixtures (E9) con expectativas | `scripts/015_intake/tests/fixtures/` (20 archivos) + `_build_fixtures.py` (generador reproducible) + README con expectativa por fixture + `tests/test_fixtures.py` (18 tests verdes) | `implementada` |
| 13 | Agentes A/B/C+Worker | `.claude/agents/intake-{governor,orchestrator,processor,evaluator}.md` — 4 agentes, modelo conductor (DEC-051), frontmatter válido + skills verificadas | `implementada` |
| 14 | Conocimiento inicial | `templates/015_intake/{decisions_library,lessons_learned}_template.md` (plantillas curadas, deployadas a `015_intake/templates/`; el governor E10-A.8 las copia a `610_knowledge/` en runtime) | `implementada` |
| 15 | Early-eval (E9, gate ≥ 0.7) | `scripts/015_intake/tests/EARLY_EVAL.md` — C aplica `intake-rubric` sobre los fixtures + verificación independiente del camino feliz (SHA-256 recalculado, bit-exactitud, evento). **Score 1.00, APPROVED.** Bug de higiene corregido (`.gitattributes` contado como fixture). El registro en `execution-state.json.early_eval` es runtime | `implementada` |
| 16 | Smoke test / corrida e2e | en `Test_Forecaster/Test_007_Conservas/` (terminal de ejecución) — **DESBLOQUEADO** (T-185 hecha). Material listo en `test_data/015_intake_e2e/`. Ver T-191/T-192 abajo | `no iniciada` |

> **Estado del 015:** los PASOS 1–15 están **implementados** (85 tests verdes, early-eval APPROVED 1.00). Solo falta el PASO 16 (corrida e2e), ya **desbloqueado** por T-185 (sesión 43). Se ejecutará como cadena completa 010→015 en `Test_007_Conservas` con material ya preparado y validado (T-191). Ver DEC-059.

---

## ⭐ Corrida e2e 010→015 en `Test_007_Conservas` (PASO 16) — DEC-059

Cadena completa con el cliente ficticio **Conservas del Pacífico S.A.S.** Dos terminales (LEC-053): la **ejecución** corre en `Test_Forecaster/Test_007_Conservas/` (sesión aparte); **esta** terminal (repo fuente) es la de **supervisión/apoyo** — observa, responde dudas, audita artefactos y aplica fixes; **no ejecuta el harness**.

| ID | Tarea | Estado |
|---|---|---|
| **T-191** | **Preparar y validar el material de prueba e2e** en `test_data/015_intake_e2e/`: `brief.md` (Conservas del Pacífico, consistente con el dataset por construcción), `orders.csv` (~4.050 filas, `;` cp1252 con acentos, 40 negativas + 50 duplicados sembrados), `orders_sin_cantidad.csv` (rechazo), `_build_dataset.py` (generador reproducible) y `README.md` (receta + convención `800_inputs/` + resultados esperados). **Validado** contra los módulos reales del pipeline: cp1252/`;`, estructura aprobada vs rechazada, 40 negativas, 50 duplicados, warning de rango 26,8% (2,20 vs 3 años). | `implementada` |
| **T-192** | **Ejecutar la corrida e2e 010→015 en `Test_007_Conservas`** (terminal de ejecución) y **supervisarla desde esta terminal**. (1) Deploy/`faro-setup` del 010, `brief.md` → `800_inputs/`, correr 010 hasta `PHASE_COMPLETE` (handoff: `client_config` + evento). (2) Deploy "switch" del 015, `orders.csv` → `800_inputs/`, correr 015 → Bronce bit-exacto + `intake_complete` + C aprueba ≥ 0.80. (3) opcional: `orders_sin_cantidad.csv` → `REJECTED_STRUCTURE`. **Auditar desde el repo fuente:** SHA-256 del Bronce vs manifest, bit-exactitud, evento como último artefacto, conteos del `intake_report` (40 negativas / 50 dups / warning de rango), `verdict.json`. **Verificar el mapeo** `client_config.anios_historial_disponible` → `run_intake.historial_declarado_anios` en el `intake-processor`. | `no iniciada` ⬅ **SIGUIENTE** |

---

## Rediseño de despliegue: carga perezosa por harness (DEC-058) — NO bloquea la corrida e2e

Acordado en la sesión 42. Cambia el despliegue de "instalar los 11 harnesses de una vez" a **just-in-time por fase** con modelo **"switch"** (instalar el nuevo + podar el previo). Reduce el contexto del sistema (Claude Code carga la descripción de cada agente/skill al iniciar sesión). **T-185 (prerrequisito del PASO 16) ya está IMPLEMENTADA** (sesión 43); T-186..T-190 son mejoras de UX del despliegue que **no bloquean** la corrida e2e (el deploy del 015 puede hacerse a mano mientras tanto). Detalle completo en **DEC-058**.

| ID | Tarea | Estado |
|---|---|---|
| **T-185** | **`deploy-harness.ps1` — copia recursiva de `scripts/{NNN}_{prefijo}/pipeline/`.** ✅ Tras copiar los archivos de primer nivel, el script ahora itera los **subdirectorios de código** y los copia recursivos (`Copy-Item -Recurse`), **excluyendo** `tests/`, `.pytest_cache/` y `__pycache__/` (el Worker solo necesita `pipeline/` + `pytest.ini`; los fixtures byte-sensibles no van al runtime). Poda cachés residuales tras copiar. **Verificado:** deploy real del 015 → `015_intake/pipeline/` con los 10 módulos, sin `tests/` ni cachés; `from pipeline.pipeline import run_intake` importa OK desde el destino. Desbloquea el PASO 16. | `implementada` |
| **T-186** | **`deploy-harness.ps1` — modelo "switch": podar el harness previo.** Añadir parámetro/lógica para remover los `{prefijo_previo}-*` agentes y skills al desplegar el nuevo (ya existe lógica de borrado de `{prefijo}-*` antes de copiar — extenderla al harness anterior). El handoff persiste en disco, así que es seguro. Respetar el matiz de DEC-058: no podar harnesses transversales (045/050/055) cuando se definan. | `no iniciada` ⬅ siguiente del bloque de despliegue (no bloquea la corrida e2e) |
| **T-187** | **`deploy-harness.ps1` — mapa "harness actual → siguiente".** Codificar la cadena (DEC-026 + pipeline `015→{020‖025}→030→035→040`). El fan-out 020‖025 es el único punto con dos siguientes — ofrecer ambos. | `no iniciada` |
| **T-188** | **`faro-setup.ps1` — instalar solo el harness de arranque (010).** Quitar la copia indiscriminada de todos los agentes/skills; conservar el andamiaje (CLAUDE.md, settings, commands, workflows, `800_inputs/brief.md`, `FARO_HOME`) y **delegar agentes/skills/scripts a `deploy-harness.ps1 -Harness 010`**. | `no iniciada` |
| **T-189** | **Crear `commands/faro-run.md` — comando conductor genérico (Opción B).** Detecta el **único** `*-governor.md` instalado y lo conduce (arranque `MODO: INIT` o continuación, según el estado que lee el governor). Reemplaza `/faro-discovery`, `/faro-intake`, etc. Reusar el patrón de `commands/faro-discovery.md` (verificar governor → cargar `conductor_loop.md` → spawnear governor). Deprecar `/faro-discovery` (lo absorbe `/faro-run`). | `no iniciada` |
| **T-190** | **Ajustar el cierre del `discovery-governor.md` (y patrón para todo governor) para ofrecer el salto.** Al `PHASE_COMPLETE`, señalar "siguiente harness disponible: {N}"; el conductor pregunta *"¿despliego el {N}?"* y con el "sí" ejecuta `& "$env:FARO_HOME\deploy-harness.ps1" -Harness {N} -Destino .` (+ poda), luego instruye **reiniciar Claude Code** y correr `/faro-run`. La transición vive en el `conductor_loop.md` (la ejecuta la sesión principal, no el governor — DEC-051). | `no iniciada` |

---

## Persistencia (acoplada al 015 — DEC-055)

| ID | Tarea | Estado |
|---|---|---|
| T-171 | Construir la **Capa 1 de persistencia** (esquema operacional Supabase: tenants/contacts/client_config/subscriptions/events) + adaptador de escritura fallback JSON↔Supabase + backfill de tenants existentes. Se planifica **junto/después** del diseño del 015 (su primer consumidor real). Guía: `documents/supabase_persistence_guide.md` §6 y §10. **Prerequisitos abiertos:** T-031 (pasarela de pagos, D-B), T-030 (pesos ITO, D-F), D-D (RLS), D-E (PostgREST vs driver). | `no iniciada` |

---

## Briefs de construcción de los harnesses siguientes (orden de construcción)

| ID | Tarea | Estado |
|---|---|---|
| T-061 | Crear `brief/020_diagnosis.md` — Plan de Construcción del harness 020 Diagnosis | `no iniciada` |
| T-062 | Crear `brief/050_lifecycle.md` — Plan de Construcción del harness 050 Lifecycle | `no iniciada` |
| T-063 | Crear `brief/025_refinery.md` — Plan de Construcción del harness 025 Refinery | `no iniciada` |
| T-064 | Crear `brief/030_trainer.md` — Plan de Construcción del harness 030 Trainer | `no iniciada` |
| T-065 | Crear `brief/035_predictor.md` — Plan de Construcción del harness 035 Predictor | `no iniciada` |
| T-066 | Crear `brief/040_publisher.md` — Plan de Construcción del harness 040 Publisher | `no iniciada` |
| T-067 | Crear `brief/045_monitor.md` — Plan de Construcción del harness 045 Monitor | `no iniciada` |
| T-068 | Crear `brief/055_command.md` — Plan de Construcción del harness 055 Command | `no iniciada` |
| T-069 | Crear `brief/060_simulator.md` — Plan de Construcción del harness 060 Simulator | `no iniciada` |

---

## Diseño de arquitectura (módulos transversales — pendientes)

| ID | Tarea | Estado |
|---|---|---|
| T-036 | Diseñar modelo de datos (esquema de tablas/colecciones) | `no iniciada` |
| T-037 | Diseñar pipeline de transformación Bronce → Plata → Oro | `no iniciada` |
| T-038 | Diseñar módulo de gestión de clientes y suscripciones | `no iniciada` |
| T-039 | Diseñar módulo de salud de datos y diagnóstico | `no iniciada` |
| T-040 | Diseñar módulo de pronóstico de demanda | `no iniciada` |
| T-041 | Diseñar Sprint Contract del Bloque A (010 + 015 + 020) | `no iniciada` |
| T-042 | Diseñar Sprint Contract de 050 Lifecycle | `no iniciada` |
| T-043 | Diseñar Sprint Contract del Bloque B (025 + 030 + 035 + 040) | `no iniciada` |
| T-044 | Diseñar Sprint Contract del Bloque D (045 + 055) | `no iniciada` |
| T-045 | Diseñar Sprint Contract de 060 Simulator | `no iniciada` |

---

## Decisiones de negocio abiertas

| ID | Tarea | Estado |
|---|---|---|
| T-029 | Responder preguntas del bloque 2.8 del problem statement: integración y operaciones | `en ejecución` |
| T-030 | Definir pesos (w1, w2, w3) y umbrales del ITO para clasificación M/L/XL (afecta `tenants.categoria`; ligado a T-178) | `no iniciada` |
| T-031 | Definir proveedor de pasarela de pagos (bloquea el detalle de cobro de la Capa 1 de persistencia) | `no iniciada` |

---

## Ajustes menores del harness 010 — diferidos, NO bloqueantes

Detectados en las corridas e2e. Ninguno impide avanzar al 015 (Test_006 dio APPROVED 1.0 con ellos presentes). Plegar idealmente al diseñar su harness consumidor o en una pasada de limpieza.

| ID | Tarea | Estado |
|---|---|---|
| T-181 | **Validar** en una corrida e2e futura el fix ya aplicado de timestamps de bitácora (regla universal + autochequeo + anti-duplicado para etiquetas improvisadas en `discovery-governor.md`). | `implementada` (pendiente validación runtime) |
| T-172 | Transliteración de acentos del slug del `tenant_id` (á→a, ñ→n…) + truncado en frontera de guion, en el Paso C del governor. Confirmar si ya funciona en código o salió bien por casualidad en Test_006. NO bloqueante. | `no iniciada` |
| T-178 | Recalibrar el ITO: la dimensión **pedidos** está casi inerte (`PEDIDOS_MAX=2000`) y hay ambigüedad pedidos vs líneas. Fijar la definición en el schema y la pregunta del interviewer. Se resuelve dentro de T-030. | `no iniciada` |
| T-179 | Añadir campo estructurado de **tolerancia de error asimétrica** (`prioridad_precision` / `segmentos_criticos`: dónde el MAPE debe ser más bajo) al schema del synthesizer/`session_data` y propagarlo en el configurator. Hoy se pierde al comprimir `criterios_exito`. Alimenta 035 Predictor / 045 Monitor. | `no iniciada` |
| T-180 | Anclar los timestamps internos de `session_notes.json` al reloj real de ejecución (el interviewer los redacta narrados, no con `Get-Date` real). Higiene de datos menor. | `no iniciada` |

## Ajustes menores del harness 015 — diferidos, NO bloqueantes

| ID | Tarea | Estado |
|---|---|---|
| T-184 | **`type_validator` (P3) no cuenta celdas numéricas vacías como error de tipo.** `_a_numero` recibe `NaN` (float, lo produce pandas para una celda vacía) y lo trata como número válido (`nan < 0` es `False`), así que un `cantidad_solicitada` vacío NO se contabiliza. En CSVs reales las celdas vacías son comunes → el conteo de errores de tipo que alimenta el ISD del 020 puede quedar subestimado. Fix: en `_a_numero` o en el conteo `num_nonneg`, tratar `NaN`/vacío como error. Requiere su propio test. Detectado en el PASO 12 (fixture `cantidad_negativa.csv`). NO bloqueante (no afecta Bronce ni vetos). | `no iniciada` |

---

## Convenciones

- Cada tarea es lo más atómica posible — una sola responsabilidad.
- Al iniciar una tarea: cambiar estado a `en ejecución`. Al completarla: `implementada`.
- Nuevas tareas se agregan con ID correlativo (el último usado es **T-192**; T-070 es el bloque de construcción del 015, T-185..T-190 el rediseño de despliegue DEC-058, T-191/T-192 la corrida e2e DEC-059).
- El detalle histórico de cualquier tarea ya implementada del 010 está en `progress/history/tasks_harness010.md`.

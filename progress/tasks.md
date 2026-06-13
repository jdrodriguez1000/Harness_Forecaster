# Tareas del Proyecto — FARO (Harness Forecaster)

Estados posibles: `no iniciada` | `en ejecución` | `implementada`

> **El registro completo de tareas ya implementadas** (todo el harness 010, sesiones 1–37) está archivado en **`progress/history/tasks_harness010.md`**. Este archivo conserva solo lo **pendiente** y el **siguiente paso**.

---

## ⭐ SIGUIENTE PASO

| ID | Tarea | Estado |
|---|---|---|
| **T-060** | **Crear `brief/015_intake.md` — Plan de Construcción del harness 015 Intake.** 7 secciones siguiendo el patrón de `brief/010_discovery.md`: (1) definición estructural, (2) diseño agéntico (instancias A/B/C + workers + herramientas + escalamiento + checkpoints), (3) Sprint Contract, (4) rúbrica de evaluación con anclas few-shot, (5) handoff al 020, (6) flujo del arnés, (7) notas de construcción. Insumos: `harnesses/015_intake.md` (doc funcional), schema ampliado de `onboarding_config.json` (T-145), `brief/010_discovery.md` (referencia). El 015 consume `onboarding_config.json` + evento `onboarding_discovery_complete` del 010 e ingiere los datos del cliente para montar la capa **Bronce**. Ver DEC-055. | `no iniciada` |

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

---

## Convenciones

- Cada tarea es lo más atómica posible — una sola responsabilidad.
- Al iniciar una tarea: cambiar estado a `en ejecución`. Al completarla: `implementada`.
- Nuevas tareas se agregan con ID correlativo (el último usado es **T-182**).
- El detalle histórico de cualquier tarea ya implementada del 010 está en `progress/history/tasks_harness010.md`.

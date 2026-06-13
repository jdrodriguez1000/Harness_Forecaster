# Estado del Proyecto — FARO (Harness Forecaster)

## Última actualización
2026-06-13 (sesión 39)

---

## LEER PRIMERO — estado en una frase

**El harness 010 Discovery está TERMINADO. La CONSTRUCCIÓN del harness 015 Intake (T-070) está EN CURSO siguiendo `plan/015_intake.md` (16 pasos). Ya están hechos el PASO 1 (andamiaje de carpetas en el repo fuente), el PASO 2 (absorbido en la skill `intake-state-schema`) y el PASO 3 (los 5 contratos: schemas + skills). El SIGUIENTE PASO es el PASO 4 — empezar los módulos del pipeline con TDD real (`source_adapter`, luego `format_detector`…). El detalle paso a paso y su estado vive en `tasks.md` (bloque "Construcción del 015 — desglose por PASO").**

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

**Hecho hasta ahora (sesión 39):**
- **PASO 1 ✅** — Andamiaje en el **repo fuente** (no carpetas runtime): `scripts/015_intake/{pipeline,tests/fixtures}/` (con `README.md` y `pipeline/__init__.py`) y `templates/015_intake/schemas/`. Entorno verificado: Python 3.12.10 + pandas/openpyxl/chardet/pytest; `xlrd` instalado (2.0.2, solo `.xls`).
- **PASO 2 ✅ (absorbido)** — Los archivos de estado son **runtime** (los crea E10-A en la terminal de prueba); su estructura quedó documentada en la skill `intake-state-schema`, no como archivos en el repo fuente.
- **PASO 3 ✅** — Los **5 contratos de referencia**: 3 JSON-schema en `templates/015_intake/schemas/` (`intake_report_schema.json`, `manifest_schema.json`, `intake_log_schema.json`) + 5 skills en `.claude/skills/` (`intake-report-schema`, `intake-manifest-schema`, `intake-log-schema`, `intake-rubric`, `intake-state-schema`).

**SIGUIENTE PASO → PASO 4** — Empezar los **módulos del pipeline con TDD real** (RED→GREEN→REFACTOR), en orden: `source_adapter` (P1) → `format_detector` (P1, el del encoding/delimitador — "canario" de los acentos cp1252) → `schema_validator` (P2, veto D2) → `type_validator`+`range_evaluator` (P3/P5) → `deduplicator` (P4) → `bronze_writer` (P6, veto D5) → `report_builder` (P7) → `pipeline.py` (orquestación P1→P8 + evento). Todos en `scripts/015_intake/pipeline/`, tests en `scripts/015_intake/tests/`. Ver PASOS 4–11 del plan.

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
- **Dónde está cada cosa:** decisiones formales en `progress/decisions.md` (última: DEC-055); lecciones en `progress/lessons.md`; registro atómico de tareas en `progress/tasks.md`.
- **Historial completo del harness 010** (todo el detalle de las sesiones 1–37, hallazgos y fixes) archivado en **`progress/history/`** (`progress_harness010.md`, `tasks_harness010.md`, `refactor_conductor_T166.md`). Consultar ahí si se necesita el porqué de algún fix del 010.
- **Repositorio GitHub:** `https://github.com/jdrodriguez1000/Harness_Forecaster.git` (rama `main`).

---

## Instrucciones para agentes (resumen de CLAUDE.md)

1. Leer **`CLAUDE.md`** (reglas de negocio) y este `progress.md` al inicio.
2. Consultar `progress/decisions.md` antes de proponer arquitecturas — puede haber una decisión ya tomada.
3. Consultar `progress/lessons.md` antes de implementar para no repetir errores.
4. Registrar toda tarea nueva en `progress/tasks.md` y mantener su estado actualizado.
5. Actualizar este `progress.md` al cerrar una sesión de trabajo significativa.

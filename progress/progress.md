# Estado del Proyecto — FARO (Harness Forecaster)

## Última actualización
2026-06-13 (sesión 38)

---

## LEER PRIMERO — estado en una frase

**El harness 010 Discovery está TERMINADO. El brief del 015 Intake (`brief/015_intake.md`, T-060) ya está REDACTADO tras una sesión de entendimiento que cerró 10 decisiones de diseño (DEC-057). El siguiente paso es CONSTRUIR el harness 015 (tarea T-070).**

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

## SIGUIENTE PASO — Construir el harness 015 Intake (T-070)

**El brief ya está escrito** (`brief/015_intake.md`, T-060 implementada). El siguiente paso es **construir** el harness siguiendo ese plan: agentes `intake-governor` / `intake-orchestrator` / `intake-processor` / `intake-evaluator`, skills/schemas (`intake-report-schema`, `intake-manifest-schema`, `intake-log-schema`, `intake-rubric`, `intake-state-schema`) y los módulos de código del pipeline P1→P8 con **TDD real** + ~20 fixtures de archivos rotos (E9).

**Qué hace el 015:** consume el handoff del 010 (`onboarding_config.json`/`client_config` + evento `onboarding_discovery_complete`) e ingiere los datos históricos del cliente para montar la capa **Bronce** (copia exacta intocable), emitiendo `intake_complete` que dispara 020 ‖ 025 en paralelo.

**Las 10 decisiones de diseño que rigen la construcción** están en **DEC-057** y desarrolladas en `brief/015_intake.md`. Lo esencial: pipeline determinístico (workers livianos), un único worker secuencial, fuente agnóstica con costura de adaptador (Fase 1 = manual/operador), Bronce write-once + SHA-256, Incremental = un archivo por entrega + manifest, Excel con huella de formato persistida en `client_config`, persistencia = rebanada del intake sin cobro (T-030/T-031 NO bloquean), handoff atómico (evento = último paso).

**Insumos disponibles:**
- Brief de construcción: `brief/015_intake.md` (recién escrito).
- Documentación funcional: `harnesses/015_intake.md`.
- Guía de persistencia: `documents/supabase_persistence_guide.md` (§6 Capa 1, §8 medallón, §10 conmutación).
- Brief de referencia (patrón): `brief/010_discovery.md`.

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

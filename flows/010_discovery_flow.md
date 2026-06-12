# Flujo del Harness 010 — Discovery
# FARO · Sabbia Solutions & Software

---

## Qué hace este harness y cuándo corre

El harness 010 es el primer proceso del sistema FARO. Se ejecuta **una sola vez por cliente nuevo**, justo después de que ese cliente firmó el contrato y pasó al estado *Onboarding*. Su objetivo es capturar todo el contexto operativo del cliente y dejar el sistema listo para recibir sus datos.

Es el único harness donde un **operador de Triple S** tiene un rol activo: conduce una sesión de preguntas con el cliente. Todos los harnesses posteriores son automáticos.

Al terminar, el sistema conoce quién es el cliente, cuánto cuesta su servicio, qué datos enviará y cómo procesarlos.

---

## Los actores

| Instancia | Nombre | Tipo | Responsabilidad única |
|-----------|--------|------|-----------------------|
| — | Operador Triple S | Humano | Facilita el acceso a stakeholders, aprueba borradores, toma decisiones estratégicas |
| — | Conductor | Sesión principal (comando `/faro-*`) | **Único que spawnea agentes.** Ejecuta el bucle conductor: spawnea al governor y a cada worker/orchestrator que el governor solicita, gestiona los gates con el operador y re-invoca al governor con el `[MODO: <then>]` indicado |
| A | discovery-governor | Agente de control | Controla el flujo completo, registra el estado global, decide qué se necesita a continuación (emite señales `dispatch`), pero **no spawnea a nadie** |
| B | discovery-orchestrator | Agente de estado | Registra checkpoints en `execution-state.json`, determina el punto de reanudación |
| W1 | discovery-interviewer | Worker interactivo | Conduce sesiones de entrevista con cada stakeholder del cliente, produce `session_notes.json` y `stakeholder_map.json` |
| W2 | discovery-synthesizer | Worker automático | Cross-referencia todas las entrevistas, detecta contradicciones, consolida `session_data.json`, clasifica brechas |
| W3 | discovery-analyst | Worker automático | Calcula el ITO, confirma la categoría M/L/XL, asigna el nivel cold start |
| W4 | discovery-configurator | Worker automático (2 modos) | DRAFT: genera borradores para revisión / COMMIT: escribe en BD, Storage y envía guía |
| C | discovery-evaluator | Auditor independiente | Evalúa los artefactos finales con rúbrica de 7 dimensiones, emite APPROVED o REJECTED |

**Regla de escritor único:** cada agente solo puede escribir en su propio archivo de salida. El governor nunca toca los archivos de los workers, y viceversa.

---

## El modelo conductor — cómo se despachan los agentes

Un subagente de Claude Code **no puede spawnear otros subagentes**. El governor y el orchestrator son subagentes, así que **ninguno spawnea**: solo la **sesión principal** (el comando `/faro-*` en ejecución, llamada aquí el **conductor**) puede hacerlo. Todo el harness gira en torno a este **handshake de despacho**:

1. El **conductor** spawnea al **governor** en un modo (`INIT`, `EXECUTE`, `POST_CP03`, `POST_CP04`, …).
2. El governor re-deriva su posición leyendo los archivos de estado del disco y retorna **un solo** `GOVERNOR_RESULT`. Cuando hace falta ejecutar un worker o el orchestrator, ese resultado es `WORKER_REQUIRED` u `ORCHESTRATOR_REQUIRED` con un bloque **`dispatch`**: `{ agent, prompt (literal), then }`.
3. El **conductor** lee el `dispatch`, **spawnea** al agente nombrado (vía la herramienta `Agent`, con `subagent_type = dispatch.agent`) pasándole `dispatch.prompt`, espera a que termine y verifica sus artefactos en disco.
4. El conductor **re-invoca al governor** con `[MODO: dispatch.then]`. El governor vuelve a re-derivar del disco y emite la siguiente señal. El ciclo se repite hasta un estado terminal.

**Excepción — el interviewer (W1):** es interactivo. El governor retorna `INTERVIEWER_REQUIRED` y el conductor lo ejecuta **inline en la sesión principal** (no como subagente aislado), porque necesita el diálogo en vivo con los stakeholders.

**Si un artefacto esperado no existe** tras un despacho, el conductor trata el caso como `EXECUTION_FAILED` (worker que no produjo salida) — nunca queda en espera infinita. Esto reemplaza al patrón anterior, en el que el governor abría sub-instancias `claude --print` en background y hacía polling (causa del cuelgue del synthesizer, T-166 / LEC-059). Decisión: **DEC-051**.

---

## Los archivos de estado y los artefactos

```
{proyecto_cliente}/
│
├── 800_inputs/                          ← archivos de entrada preparados por el operador
│   └── brief.md                     ← contexto del cliente y stakeholders iniciales
│
├── 010_discovery/                   ← artefactos de trabajo del harness
│   ├── stakeholder_map.json         ← escrito por W1 (interviewer) — mapa de stakeholders y estados
│   ├── session_notes.json           ← escrito por W1 (interviewer) — notas de cada sesión
│   ├── synthesis_report.json        ← escrito por W2 (synthesizer) — campos consolidados y contradicciones
│   ├── open_questions.json          ← escrito por W2 (synthesizer) — brechas clasificadas por severidad
│   ├── session_data.json            ← escrito por W2 (synthesizer) — datos consolidados para el analyst
│   ├── analysis_report.json         ← escrito por W3 (analyst)
│   ├── client_profile.json          ← escrito por W4 (configurator)
│   ├── onboarding_config.json       ← escrito por W4 (configurator)
│   ├── data_intake_guide.md/pdf     ← escrito por W4 (configurator)
│   ├── templates/                   ← guías de preguntas por rol (solo lectura)
│   └── schemas/                     ← schemas JSON de referencia (solo lectura)
│
├── 600_persistence/                 ← archivos de estado del harness
│   ├── harness-state.json           ← exclusivo de A (governor)
│   ├── execution-state.json         ← exclusivo de B (orchestrator)
│   ├── claude-progress.txt          ← bitácora de eventos (A escribe, todos leen)
│   └── events/                      ← evento de completitud (W4 en Fase 1)
│
├── 605_eval/                        ← exclusivo de C (evaluator)
│   ├── verdict.json
│   └── metrics_summary.json
│
└── 610_knowledge/                   ← base de conocimiento acumulada
    ├── decisions_library.md         ← A escribe al cierre
    └── lessons_learned.md           ← A y C escriben al cierre o tras rechazos
```

---

## El flujo completo — paso a paso

> **Cómo leer el diagrama:** la columna **OPERADOR** representa la terminal de la sesión principal, donde corre el **conductor**. Cada flecha `gov→WORKER_REQUIRED ──► CONDUCTOR spawnea` significa que el governor retornó una señal `dispatch` y fue el conductor —no el governor— quien spawneó al worker (ver "El modelo conductor"). Los `[MODO: …]` entre GOVERNOR y ORCHESTRATOR también los despacha el conductor vía `ORCHESTRATOR_REQUIRED`.

```
OPERADOR / CONDUCTOR        GOVERNOR (A)              ORCHESTRATOR (B)         WORKERS / EVALUATOR
   │                            │                            │                        │
   │  /faro-init o              │                            │                        │
   │  /faro-discovery ─────────►│                            │                        │
   │                            │                            │                        │
   │                        [MODO: INIT]                     │                        │
   │                        E10-A ritual:                    │                        │
   │                        · Crea carpetas                  │                        │
   │                        · git init                       │                        │
   │                        · Inicializa state files         │                        │
   │                        · Inicializa decisions_library   │                        │
   │                            │                            │                        │
   │◄── Sprint Contract ────────│                            │                        │
   │    (para revisión)         │                            │                        │
   │                            │                            │                        │
   │─── Aprueba ───────────────►│                            │                        │
   │                            │                            │                        │
   │                        [MODO: EXECUTE]                  │                        │
   │                            │────── [MODO: PLAN] ───────►│                        │
   │                            │◄───── PLAN_RESULT ─────────│                        │
   │                            │    (starting_point)        │                        │
   │                            │                            │                        │
   │◄── INTERVIEWER_REQUIRED ───│                            │                        │
   │    (con lista de           │                            │                        │
   │     stakeholders del brief)│                            │                        │
   │                            │                            │                        │
   │   ┌─── SESIÓN 1 ──────────────────────────────────────────────────────────────┐ │
   │◄─►│         discovery-interviewer (W1) — Stakeholder 1                        │ │
   │   │  · Entrevista adaptada al rol (negocio / técnico / usuario)               │ │
   │   │  · Guardado incremental por bloque al terminar cada sección               │ │
   │   │  · Cierre snowball → descubre nuevos stakeholders                         │ │
   │   │  → Actualiza 010_discovery/support/session_notes.json                             │ │
   │   │  → Actualiza 010_discovery/support/stakeholder_map.json                           │ │
   │   └───────────────────────────────────────────────────────────────────────────┘ │
   │                            │                            │                        │
   │   ┌─── SESIÓN N ──────────────────────────────────────────────────────────────┐ │
   │◄─►│         discovery-interviewer (W1) — Stakeholder N                        │ │
   │   │  (se repite por cada stakeholder en el mapa con estado "pendiente")       │ │
   │   │  → Actualiza session_notes.json y stakeholder_map.json                    │ │
   │   └───────────────────────────────────────────────────────────────────────────┘ │
   │                            │                            │                        │
   │─── interviewer_complete ──►│                            │                        │
   │    (todos los stakeholders │── [MODO: INTERVIEWER_DONE] ►│                        │
   │     con estado completada) │   marca interviewer_       │                        │
   │                            │◄── INTERVIEWER_MARK_OK ─────│  completed_at en        │
   │                            │   (no avanza last_checkpoint) execution-state.json    │
   │                            │                            │                        │
   │              gov→WORKER_REQUIRED ──► CONDUCTOR spawnea al worker ───────────────►│
   │                            │                    discovery-synthesizer (W2)        │
   │                            │                    · Lee session_notes.json          │
   │                            │                    · Lee stakeholder_map.json        │
   │                            │                    · Cross-referencia perspectivas   │
   │                            │                    · Detecta contradicciones         │
   │                            │                    · Clasifica brechas (bloqueante/  │
   │                            │                      importante/registrable)         │
   │                            │                    · Consolida session_data.json     │
   │                            │◄─── SYNTHESIZER_RESULT ────────────────────────────│
   │                            │                            │                        │
   │                      [Gate automático]                  │                        │
   │                      ¿hay campos bloqueantes?           │                        │
   │                            │                            │                        │
   │           ┌────────────────┴──────────────────┐         │                        │
   │  SEGUNDA_RONDA_REQUERIDA              COMPLETE │         │                        │
   │           │                                   │         │                        │
   │◄── INTERVIEWER_REQUIRED ──┘                   │         │                        │
   │    (modo COMPLEMENTARIO,                      │         │                        │
   │     lista de campos bloqueantes)              │         │                        │
   │                                               │         │                        │
   │   ┌─── SESIÓN COMPLEMENTARIA ─────────────────│──────────────────────────────┐  │
   │◄─►│    discovery-interviewer (W1) — modo COMPLEMENTARIO                       │  │
   │   │    Solo los stakeholders y campos que el synthesizer marcó como bloqueante │  │
   │   │    → Actualiza session_notes.json con subnodo complemento_<timestamp>      │  │
   │   └──────────────────────────────────────────────────────────────────────────-┘  │
   │                            │                            │                        │
   │─── interviewer_complete ──►│ (segunda ronda)            │                        │
   │                            │                            │                        │
   │       gov→WORKER_REQUIRED ──► CONDUCTOR re-spawnea synthesizer ─────────────────►│
   │                            │◄─── SYNTHESIZER_RESULT (COMPLETE) ─────────────────│
   │                            │                            │                        │
   │                            │── [MODO: CHECKPOINT-01] ──►│                        │
   │                            │◄── CHECKPOINT_OK: CP-01 ───│                        │
   │                            │                            │                        │
   │              gov→WORKER_REQUIRED ──► CONDUCTOR spawnea al worker ───────────────►│
   │                            │                      discovery-analyst (W3)          │
   │                            │                      · Lee session_data.json         │
   │                            │                      · Calcula ITO normalizado       │
   │                            │                      · Confirma categoría M/L/XL    │
   │                            │                      · Asigna nivel cold start       │
   │                            │◄─── ANALYST_RESULT ────────────────────────────────│
   │                            │                            │                        │
   │                      [Gate automático]                  │                        │
   │                      ¿discrepancia > 1 nivel?           │                        │
   │                      ¿historial < 3 meses?              │                        │
   │◄── ESCALATION_REQUIRED ────│  (si hay problema grave)   │                        │
   │   (operador debe decidir)  │                            │                        │
   │                            │                            │                        │
   │                            │── [MODO: CHECKPOINT-02] ──►│                        │
   │                            │◄── CHECKPOINT_OK: CP-02 ───│                        │
   │                            │                            │                        │
   │              gov→WORKER_REQUIRED ──► CONDUCTOR spawnea al worker ───────────────►│
   │                            │                    discovery-configurator (W4-DRAFT) │
   │                            │                    · Lee session_data.json           │
   │                            │                    · Lee analysis_report.json        │
   │                            │                    · Genera client_profile.json      │
   │                            │                    · Genera onboarding_config.json   │
   │                            │                    · NO escribe en BD ni Storage aún │
   │                            │◄─── CONFIGURATOR_RESULT ───────────────────────────│
   │                            │                            │                        │
   │                            │── [MODO: CHECKPOINT-03] ──►│                        │
   │                            │◄── CHECKPOINT_OK: CP-03 ───│                        │
   │                            │                            │                        │
   │◄── Borradores para ────────│                            │                        │
   │    revisión (CP-03)        │                            │                        │
   │    · client_profile.json   │                            │                        │
   │    · onboarding_config.json│                            │                        │
   │                            │                            │                        │
   │─── ¿Aprueba? ─────────────►│                            │                        │
   │    · Sí → continúa         │  [POST_CP03]               │                        │
   │    · No → pide cambios ────►  Configurator re-genera    │                        │
   │                            │  los borradores con los    │                        │
   │◄── Borradores nuevos ──────│  cambios y vuelve a        │                        │
   │    (rework)                │  presentar CP-03           │                        │
   │                            │                            │                        │
   │─── Aprueba finalmente ────►│                            │                        │
   │                            │                            │                        │
   │                        [MODO: POST_CP04]                │                        │
   │                            │── [MODO: CHECKPOINT-04] ──►│                        │
   │                            │◄── CHECKPOINT_OK: CP-04 ───│                        │
   │                            │                            │                        │
   │              gov→WORKER_REQUIRED ──► CONDUCTOR spawnea al worker ───────────────►│
   │                            │                   discovery-configurator (W4-COMMIT) │
   │                            │                   · Registros en BD (o JSON local)   │
   │                            │                   · Crea carpeta Storage del tenant  │
   │                            │                   · Genera data_intake_guide.md/pdf  │
   │                            │                   · Envía correo al contacto (o      │
   │                            │                     guarda pendiente en Fase 1)       │
   │                            │                   · Emite evento                     │
   │                            │                     onboarding_discovery_complete     │
   │                            │◄─── CONFIGURATOR_RESULT ───────────────────────────│
   │                            │                            │                        │
   │                            │── [MODO: CHECKPOINT-05] ──►│                        │
   │                            │◄── CHECKPOINT_OK: CP-05 ───│                        │
   │                            │                            │                        │
   │              gov→WORKER_REQUIRED ──► CONDUCTOR spawnea al worker ───────────────►│
   │                            │                      discovery-evaluator (C)         │
   │                            │                      · Lee todos los artefactos      │
   │                            │                      · Aplica rúbrica 7 dimensiones  │
   │                            │                      · Score global ≥ 0.80 = PASS    │
   │                            │                      · Escribe verdict.json          │
   │                            │◄─── APPROVED o REJECTED ───────────────────────────│
   │                            │                            │                        │
   │                      ┌─────┴──────┐                     │                        │
   │               APPROVED│          │REJECTED               │                        │
   │                        │          └── protocolo de       │                        │
   │                        │              rechazo:           │                        │
   │                        │              re-ejecutar        │                        │
   │                        │              workers fallidos   │                        │
   │                        │              → vuelve a C       │                        │
   │                        │                            │                        │
   │                    [MODO: CLOSE]                        │                        │
   │                    · Actualiza lessons_learned.md   │                        │
   │                    · Actualiza decisions_library.md │                        │
   │                    · git commit final               │                        │
   │                        │                            │                        │
   │◄── CLOSE_READY ────────│                            │                        │
   │    + pregunta si deployar│                           │                        │
   │      harness 015 Intake  │                           │                        │
   │                          │                           │                        │
   │─── Sí/No ───────────────►│                           │                        │
   │                          │ (si sí: deploy-harness    │                        │
   │                          │  -Harness 015)            │                        │
   │                                                       │                        │
  FIN — sistema listo para recibir datos del cliente
```

---

## Detalle de cada etapa

### INIT — Arranque o reanudación

El governor detecta si es la primera vez o si hay un harness en curso:

- **Primera vez (E10-A):** crea todas las carpetas, inicializa `harness-state.json` y `execution-state.json` vacíos, hace `git init`, crea la `decisions_library.md` con las 7 decisiones de configuración del sistema (escala ITO, pesos, cold start, etc.). El estado inicial es `PENDING_CONTRACT`.

- **Reanudación (E10-B):** lee `harness-state.json` y `execution-state.json`, determina en qué checkpoint se quedó y retorna la instrucción correcta al operador (por ejemplo, "los borradores estaban listos, retomamos en CP-03").

Al final del INIT, el governor presenta el **Sprint Contract**: un resumen del trabajo que se va a hacer, los workers que se activarán, los artefactos que se producirán y los criterios de éxito. El operador lo lee y aprueba antes de continuar.

---

### EXECUTE — Los cuatro workers en cadena

**¿Por qué la cadena es en ese orden?**
Cada worker necesita el output del anterior:
- El synthesizer necesita `session_notes.json` (del interviewer) para consolidar perspectivas.
- El analyst necesita `session_data.json` (del synthesizer) para calcular el ITO.
- El configurator necesita `analysis_report.json` (del analyst) para saber qué categoría y nivel cold start registrar.

#### W1 — discovery-interviewer (interactivo, multi-sesión)

Es el único worker que no puede lanzarse automáticamente: necesita a stakeholders del cliente respondiendo en tiempo real. El governor retorna `INTERVIEWER_REQUIRED` y el operador conduce las sesiones directamente.

| Qué necesita | Qué hace | Qué produce |
|---|---|---|
| `800_inputs/brief.md` + guías de preguntas por rol en `010_discovery/templates/` | Conduce una sesión por stakeholder adaptada a su rol (negocio / técnico / usuario). Aplica mecanismo snowball para descubrir nuevos interesados. Guarda incrementalmente después de cada bloque temático. | `010_discovery/support/session_notes.json` (notas por stakeholder) + `010_discovery/support/stakeholder_map.json` (estados del proceso) |

El interviewer puede correr N veces — una por cada stakeholder en el mapa con `estado: "pendiente"`. Incluye un modo COMPLEMENTARIO para segunda ronda acotada a campos bloqueantes específicos.

**Gate después de W1:** el governor verifica que haya cobertura mínima de roles (al menos un stakeholder técnico con valores ITO). Si falta, retorna `INTERVIEWER_REQUIRED` nuevamente antes de pasar al synthesizer.

---

#### W2 — discovery-synthesizer (automático)

El conductor lo spawnea cuando el governor retorna `WORKER_REQUIRED` (synthesizer), después de que el operador reporta `interviewer_complete`.

| Qué necesita | Qué hace | Qué produce |
|---|---|---|
| `010_discovery/support/session_notes.json` + `010_discovery/support/stakeholder_map.json` | 1. Cross-referencia perspectivas de todos los stakeholders. 2. Detecta contradicciones entre roles. 3. Consolida los valores de cada campo (elige la fuente más confiable). 4. Clasifica brechas: bloqueante (impide continuar) / importante (degradan calidad) / registrable (solo para seguimiento). 5. Genera `session_data.json` como fuente canónica para el analyst. | `010_discovery/support/synthesis_report.json` + `010_discovery/support/open_questions.json` + `010_discovery/session_data.json` |

**Gate después de W2:** si hay campos bloqueantes, el governor retorna `INTERVIEWER_REQUIRED` con modo COMPLEMENTARIO y la lista exacta de campos a resolver. El interviewer corre una segunda ronda acotada y el synthesizer vuelve a ejecutarse. Si no hay bloqueantes, el flujo avanza.

**CP-01 se registra aquí:** después de que el synthesizer retorna `COMPLETE` (sin bloqueantes pendientes), el governor registra CP-01. Este checkpoint significa "session_data.json consolidado y listo para el analyst".

---

#### W3 — discovery-analyst (automático)

El conductor lo spawnea cuando el governor retorna `WORKER_REQUIRED` (analyst). No necesita al operador.

| Qué necesita | Qué hace | Qué produce |
|---|---|---|
| `010_discovery/session_data.json` | 1. Lee SKUs, clientes XYZ y pedidos por mes. 2. Normaliza cada valor a escala 0–100 usando los máximos de referencia provisionales. 3. Aplica pesos (w1=0.40, w2=0.35, w3=0.25) → ITO = valor entre 0 y 100. 4. Clasifica: ITO ≤ 33 → M, ITO ≤ 66 → L, ITO > 66 → XL. 5. Compara con la categoría que se usó en la venta. 6. Asigna nivel cold start según los años de historial. | `010_discovery/analysis_report.json` |

**La categoría confirmada:** si la categoría que salió del ITO y la que se usó en la venta coinciden (o difieren solo 1 nivel), se confirma la calculada. Si difieren 2 niveles (ej: ITO dice XL pero se vendió como M), se escala al operador — es probable que hubo un error comercial grave.

**El nivel cold start:**

| Historial declarado | Nivel | Lo que implica |
|---------------------|-------|----------------|
| ≥ 3 años | Alta (CS-ALTA) | Pronóstico con máxima confianza desde el mes 3 |
| 2–3 años | Estándar (CS-ESTANDAR) | Pronóstico con confianza estándar |
| 1–2 años | Reducida (CS-REDUCIDA) | Pronóstico posible pero con intervalos más amplios |
| < 1 año | Experimental (CS-EXPERIMENTAL) | Se activa la cascada cold start; en Fase 1, siempre paso 3 (acumular 3 meses antes del primer pronóstico) |
| < 3 meses | Inviable | El governor escala — no hay base mínima para operar |

---

#### W4 — discovery-configurator en modo DRAFT (automático)

El conductor lo spawnea cuando el governor retorna `WORKER_REQUIRED` (configurator DRAFT). No escribe nada en BD ni en Storage.

| Qué necesita | Qué hace | Qué produce |
|---|---|---|
| `session_data.json` + `analysis_report.json` | Construye los dos artefactos de configuración con toda la información recolectada y analizada | `010_discovery/client_profile.json` (identidad, categoría, precio, cold start) + `010_discovery/onboarding_config.json` (modo ingesta, horizonte, jerarquías, esquemas activos) |

**¿Por qué primero un borrador y después el commit?** Porque antes de crear registros en la base de datos y enviar correos, el operador debe poder revisar y corregir cualquier dato. Una vez que el configurator hace el COMMIT, los efectos son reales e inmediatos. El borrador es la única oportunidad de corrección sin consecuencias.

---

### Gate CP-03 — Revisión del operador

El operador recibe los dos borradores y los revisa. Puede:

- **Aprobar:** se pasa al COMMIT. El sistema procede.
- **Pedir cambios:** se describe qué cambiar, el configurator regenera los borradores y se vuelve a presentar CP-03. No hay límite de iteraciones, pero cada ciclo se registra en el `harness-state.json`.

---

#### W4 — discovery-configurator en modo COMMIT (automático)

Con los borradores aprobados, el configurator ejecuta todas las escrituras reales, en este orden:

| Paso | Qué hace | En Fase 1 (sin infraestructura) |
|------|----------|----------------------------------|
| 1 | Registros en BD: `clients`, `contacts`, `client_config`, `subscriptions` | Escribe archivos JSON locales en `010_discovery/db_records/` |
| 2 | Crea carpeta del tenant en Storage: `tenants/{id}/{bronze,silver,gold,models,forecasts,exports}/` | Crea carpetas locales en el proyecto |
| 3 | Genera `data_intake_guide.md/pdf` — instrucciones personalizadas para el cliente | Genera `.md` en vez de PDF |
| 4 | Envía la guía al contacto principal por correo | Guarda `correo_pendiente.json` para envío manual |
| 5 | Emite el evento `onboarding_discovery_complete` con tenant_id, timestamp y next_harness: 015_intake | Guarda `evento_pendiente.json` |

**El evento es crítico:** es la señal que activa el harness 015 Intake. Mientras no se emita, el sistema considera que el cliente no está listo para recibir datos.

---

### Auditoría — discovery-evaluator (C)

Después del COMMIT, el governor retorna `WORKER_REQUIRED` (evaluator) y el conductor lo spawnea como auditor independiente. C arranca sin contexto de lo que ocurrió durante el harness — solo lee los archivos del filesystem.

Evalúa 7 dimensiones con un score de 0.0, 0.5 o 1.0 cada una:

| Dimensión | Qué verifica |
|-----------|-------------|
| D1 — Completitud de sesión | `session_data.json` tiene todos los campos obligatorios sin MISSING |
| D2 — Consistencia ITO-Categoría | La categoría confirmada es coherente con el ITO calculado |
| D3 — Cold start documentado | El nivel y cascada están correctamente registrados en `analysis_report.json` |
| D4 — BD completa | Los registros en BD (o archivos locales) existen y tienen todos los campos |
| D5 — Storage creado | La estructura de carpetas del tenant existe |
| D6 — Guía de datos generada | `data_intake_guide.md/pdf` existe y tiene contenido personalizado |
| D7 — Evento emitido | El evento `onboarding_discovery_complete` fue emitido o está pendiente de envío manual |

**Reglas de veto:** D4, D5 y D7 tienen veto automático — si cualquiera de ellas es 0.0, el veredicto es REJECTED sin importar el score promedio. Sin registro en BD no hay cliente. Sin carpeta en Storage no hay dónde guardar datos. Sin evento el 015 Intake nunca arranca.

**Gate de aprobación:** score promedio ≥ 0.80.

---

### Si hay un REJECTED

El governor activa el protocolo de rechazo según qué dimensión falló:

| Dimensión fallida | Acción |
|-------------------|--------|
| D1 (sesión incompleta) | Retorna `INTERVIEWER_REQUIRED` modo COMPLEMENTARIO → el operador coordina segunda ronda acotada → re-ejecuta synthesizer → ciclo desde CP-01 |
| D2 o D3 (análisis incorrecto) | El governor retorna `WORKER_REQUIRED` (analyst) → el conductor lo re-spawnea → ciclo desde CP-02 |
| D4, D5 o D7 (BD, Storage o evento) | El governor retorna `WORKER_REQUIRED` (configurator COMMIT de reparación) → el conductor lo re-spawnea → máximo 2 reintentos, luego escala al operador |

Tras cada re-ejecución, el evaluator vuelve a auditar desde cero.

---

### CLOSE — Cierre y traspaso

Si el veredicto es APPROVED:

1. El governor marca `harness-state.json` como `PHASE_COMPLETE`.
2. Actualiza `610_knowledge/lessons_learned.md` con lo que funcionó, lo que no y cuántas iteraciones tomó el ciclo.
3. Actualiza `610_knowledge/decisions_library.md` con las decisiones específicas del tenant (categoría confirmada, nivel cold start, parámetros de configuración).
4. Hace el commit final: `feat(010-discovery): onboarding complete — {tenant_id}`.
5. Pregunta al operador si despliega el harness 015 Intake en el mismo directorio.

---

## Los checkpoints — qué significan y para qué sirven

Los checkpoints son registros en `execution-state.json` que indican hasta dónde llegó el harness. Sirven para **reanudar sin repetir trabajo** si la sesión se interrumpe.

| Checkpoint | Significado | Estado del sistema en ese momento |
|------------|-------------|----------------------------------|
| CP-01 | `session_data.json` consolidado por el synthesizer, sin campos bloqueantes pendientes | El synthesizer completó, el analyst aún no corre |
| CP-02 | `analysis_report.json` existe y es consistente | El analyst terminó, el configurator DRAFT aún no corre |
| CP-03 | Borradores `client_profile.json` y `onboarding_config.json` existen | El configurator DRAFT terminó, pendiente aprobación del operador |
| CP-04 | El operador aprobó los borradores | La aprobación está registrada, el COMMIT aún no corre |
| CP-05 | El COMMIT completó: BD + Storage + guía + evento | Listo para auditoría |

Si el operador cierra la sesión entre CP-01 y CP-02, al reanudar el governor sabe que debe retomar justo antes de invocar el analyst — no necesita repetir las entrevistas ni la síntesis.

**Marcador del tramo interactivo (no es un checkpoint):** el interviewer (W1) es interactivo y no tiene checkpoint propio — CP-01 lo registra el synthesizer. Para que `execution-state.json` no quede congelado en `last_checkpoint: null` entre el fin de las entrevistas y la corrida del synthesizer, el governor retorna `ORCHESTRATOR_REQUIRED` y el conductor spawnea al orchestrator en `[MODO: INTERVIEWER_DONE]`, que escribe `interviewer_completed_at` (y los paths de `session_notes.json` + `stakeholder_map.json`) **sin avanzar `last_checkpoint`**. Es un marcador de progreso, no un gate de reanudación.

---

## Escalaciones — cuándo el flujo se detiene y espera al operador

Hay cuatro situaciones que bloquean el flujo automático y requieren acción del operador:

| Situación | Quién la detecta | Qué pasa |
|-----------|-----------------|----------|
| No hay cobertura técnica mínima al terminar las entrevistas | Governor (verifica post-W1) | Sin al menos un stakeholder técnico con valores ITO, el synthesizer no puede consolidar. El operador consigue acceso al equipo técnico del cliente. |
| Campos bloqueantes detectados por el synthesizer en `open_questions.json` | Governor (verifica post-W2) | El synthesizer no puede producir `session_data.json` completo. El governor retorna `INTERVIEWER_REQUIRED` con modo COMPLEMENTARIO y la lista de campos a resolver. El operador coordina una segunda ronda de entrevistas acotada. |
| Discrepancia de categoría > 1 nivel (ej: ITO→XL pero vendido como M) | Governor (verifica post-W3) | El precio que se le prometió al cliente puede ser incorrecto. Requiere revisión comercial antes de continuar. |
| Historial declarado < 3 meses | Governor (verifica post-W3) | El sistema puede operar con < 1 año (cascada cold start), pero con menos de 3 meses no hay base mínima. Requiere evaluación de viabilidad. |

---

## El resultado final — qué existe cuando el harness cierra

Cuando el evaluator aprueba y el governor cierra, el sistema tiene:

| Artefacto | Dónde vive | Para qué sirve |
|-----------|------------|----------------|
| `client_profile.json` | `010_discovery/` + BD | Identidad del cliente: razón social, categoría, precio, contactos, cold start |
| `onboarding_config.json` | `010_discovery/` + BD | Parámetros operativos: modo ingesta, horizonte, jerarquías, esquemas activos |
| `data_intake_guide.md/pdf` | `010_discovery/` + enviado al cliente | Instrucciones personalizadas para que el cliente sepa qué archivos enviar y cómo |
| Registros BD | `clients`, `contacts`, `client_config`, `subscriptions` | Base para que el harness 050 Lifecycle gestione cobros desde el mes 2 |
| Carpeta del tenant en Storage | `tenants/{id}/bronze/silver/gold/models/forecasts/exports/` | Contenedor aislado donde todos los harnesses posteriores depositarán sus artefactos |
| Evento `onboarding_discovery_complete` | `600_persistence/events/` | Señal que activa el harness 015 Intake y da inicio al flujo de datos |
| `decisions_library.md` actualizado | `610_knowledge/` | Registro de las decisiones específicas del tenant para que futuros agentes las consulten |

---

## Resumen visual del flujo

```
/faro-init
    │
    ▼
INIT ──► Sprint Contract ──► Operador aprueba
    │
    ▼
EXECUTE
    ├─► PLAN (orchestrator determina starting_point)
    │
    ├─► [W1] interviewer ──────────────► session_notes.json + stakeholder_map.json
    │         (interactivo, N sesiones)         │
    │         una por stakeholder               │
    │         ↺ /faro-save disponible           │
    │                                    [Gate: cobertura técnica mínima?]
    │                                           │
    ├─► [W2] synthesizer (automático) ──► synthesis_report.json
    │                                     open_questions.json
    │                                     session_data.json
    │                                           │
    │                                    [Gate: ¿campos bloqueantes?]
    │                                           │
    │         ┌─────────────── SÍ ─────────────┘
    │         │  INTERVIEWER_REQUIRED (COMPLEMENTARIO)
    │         │  operador coordina segunda ronda acotada
    │         └──► [W1] → [W2] nuevamente
    │                                           │ NO (COMPLETE)
    │                                      [CP-01]
    │                                           │
    ├─► [W3] analyst (automático) ─────────► analysis_report.json
    │                                    [Gate: categoría ok? cold start viable?]
    │                                      [CP-02]
    │                                           │
    └─► [W4] configurator DRAFT ───────► client_profile.json + onboarding_config.json
                                          [CP-03]
                                                │
                                         [Gate CP-03: operador revisa]
                                                │
                                         (aprueba / pide cambios)
                                                │
POST_CP04
    │
    └─► [W4] configurator COMMIT ──────► BD + Storage + guía + correo + evento
                                          [CP-05]
                                                │
                                         [Auditoría - evaluator C]
                                          7 dimensiones, score ≥ 0.80
                                          veto en D4, D5, D7
                                                │
                                    ┌───────────┴──────────┐
                                 APPROVED               REJECTED
                                    │                       │
                                 CLOSE                  protocolo
                                    │                   de rework
                                    │                       │
                                    └───────────┬───────────┘
                                                │
                                   lessons_learned + decisions_library
                                   git commit final
                                   ¿deployar 015 Intake?
                                                │
                                              FIN
```

---

## Lo que este harness NO hace

El harness 010 termina cuando el cliente está configurado y listo para enviar datos. Todo lo demás es responsabilidad de harnesses posteriores:

- Recibir y validar los archivos de datos del cliente → **015 Intake**
- Calcular el ISD (Índice de Salud de Datos) → **020 Diagnosis**
- Limpiar y normalizar los datos → **025 Refinery**
- Entrenar los modelos → **030 Trainer**
- Generar pronósticos → **035 Predictor**
- Publicar resultados en el dashboard → **040 Publisher**
- Gestionar cobros y ciclo de vida → **050 Lifecycle**

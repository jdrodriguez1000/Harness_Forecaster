# Plan de Refactor T-166 — Modelo Conductor del Harness 010 Discovery

> **Para el agente que retome esto en una sesión nueva:** este documento es autocontenido.
> Léelo completo antes de tocar código. Implementa en el orden de la Sección 8. Al terminar
> cada subtarea, actualiza su estado en `tasks.md` (T-166a … T-166e). El objetivo es eliminar
> el cuelgue del hallazgo T-166 (ver `lessons.md` LEC-059) cambiando **cómo se invocan los
> agentes del harness**, sin cambiar el formato de los archivos de estado.

---

## 0. Contexto — por qué este refactor

En la sesión 30, al reanudar Test_004A, el `discovery-governor` avanzó al `discovery-synthesizer`
invocándolo como **sub-instancia `claude --print` anidada en background** y quedó colgado ~19 min
sin producir ningún artefacto (4 archivos de salida CLI en 0 bytes; cero `session_data.json` /
`synthesis_report.json` / `open_questions.json`). Ver `progress.md` (sesión 30), `tasks.md` (T-166)
y `lessons.md` (LEC-059).

**Causa raíz confirmada con la documentación oficial de Claude Code**
(https://code.claude.com/docs/en/sub-agents):

> "This prevents infinite nesting **(subagents cannot spawn other subagents)** while still
> gathering necessary context."

**Un subagente NO puede spawnear otros subagentes.** El governor es un subagente (Instancia A, lo
spawnea la sesión principal vía `/faro-discovery`). Por eso intentaba invocar a los workers por la
única vía que le queda a un subagente — abrir un proceso `claude` nuevo por shell — y esa vía es
**poco confiable** (sin streaming, propensa a timeout del Bash tool a 120s, el padre no distingue
"trabajando" de "muerto").

**Conclusión:** el fix NO es "usar la herramienta `Agent` dentro del governor" (no funcionaría: el
governor es subagente). El fix es **mover toda la invocación a la sesión principal**, que es el único
nivel que SÍ puede spawnear subagentes de forma confiable.

El harness ya hace esto para el `discovery-interviewer` (governor retorna `INTERVIEWER_REQUIRED` →
la sesión principal lo corre → re-invoca al governor con `interviewer_complete: true`). Este plan
**generaliza ese patrón a todos los agentes**.

---

## 1. Principio rector

- **A (governor), B (orchestrator), C (evaluator) y los workers** pasan a ser **subagentes
  hermanos** colgando de la sesión principal. **Ninguno invoca a otro.** Cada uno hace una cosa y
  retorna una señal estructurada.
- **La sesión principal (los comandos `/faro-*`) es el CONDUCTOR**: el único que spawnea. Un bucle
  genérico: spawnea lo que el governor pida → re-invoca al governor.
- **El governor sigue siendo el cerebro** (decide secuencia y gates) pero **deja de ejecutar pasos**.
  En cada invocación hace **un solo paso de decisión** y retorna una señal de *despacho* que nombra
  qué subagente spawnear y con qué prompt.
- El governor es **stateless entre invocaciones**: re-deriva todo del disco (`harness-state.json`,
  `execution-state.json`, y la existencia de artefactos en `010_discovery/`). No necesita el stdout
  de los workers — lee sus artefactos en el siguiente turno. Esa verificación-en-disco es, además,
  la robustez que T-166 pedía.

---

## 2. El modelo nuevo (bucle conductor)

```
SESIÓN PRINCIPAL (/faro-discovery, /faro-restart, /faro-continue) = CONDUCTOR
   │
   │  bucle:
   │  1. result = spawn(discovery-governor, prompt)
   │  2. mientras result.status ∈ {WORKER_REQUIRED, ORCHESTRATOR_REQUIRED}:
   │        out    = spawn(result.dispatch.agent, result.dispatch.prompt)   ← solo la sesión principal puede
   │        result = spawn(discovery-governor, "MODO: <result.dispatch.then>")
   │  3. si result.status == INTERVIEWER_REQUIRED → correr interviewer inline → re-invocar governor
   │  4. si result.status es gate de operador (SPRINT_CONTRACT_READY, EXECUTION_COMPLETE,
   │        CP04_READY, CLOSURE_READY, …) → AskUserQuestion → re-invocar governor con la respuesta
   │  5. si result.status es terminal (CLOSE_READY, HANDOFF_READY, SUSPENDED, *_FAILED) → fin
   ▼
 governor   orchestrator   synthesizer   analyst   configurator   evaluator
 (decide)   (estado)       (trabaja)     (trabaja) (trabaja)       (audita)
        cada uno retorna una señal; NINGUNO invoca a otro
```

El governor nunca corre dos pasos en un turno. Hace uno, retorna, el conductor lo re-invoca, y el
governor re-lee disco para saber dónde quedó.

---

## 3. Nuevo contrato de señales

Se **agregan** dos status de despacho a `GOVERNOR_RESULT`. **Todos los status existentes se
conservan** (ver inventario en Sección 3.1).

```
GOVERNOR_RESULT:
  mode: EXECUTE | POST_CP03 | POST_CP04
  status: WORKER_REQUIRED            # o ORCHESTRATOR_REQUIRED
  dispatch:
    agent: discovery-synthesizer     # qué subagente spawnear
    prompt: |                        # el prompt EXACTO que el conductor pasa al subagente (literal)
      Eres discovery-synthesizer. Directorio de trabajo: <ruta absoluta>
      session_notes_path: 010_discovery/support/session_notes.json
      stakeholder_map_path: 010_discovery/support/stakeholder_map.json
      Cross-referencía las entrevistas, consolidá los campos obligatorios, detectá contradicciones
      y producí 010_discovery/support/synthesis_report.json, open_questions.json y session_data.json.
    then: EXECUTE                    # con qué MODO re-invocar al governor después de que el subagente corra
  context: <1 línea legible para el operador>
```

- `ORCHESTRATOR_REQUIRED` es idéntico pero con `agent: discovery-orchestrator` (para PLAN,
  INTERVIEWER_DONE y los CHECKPOINT-0X). Su `prompt` es el bloque `[MODO: …]` que el governor ya
  construía.
- El conductor **no interpreta** `dispatch.prompt` — lo pasa literal al subagente. Toda la
  inteligencia queda en el governor.
- `then` indica el MODO con que el conductor re-invoca al governor (casi siempre el mismo modo en
  curso: `EXECUTE`, `POST_CP03` o `POST_CP04`).

### 3.1 Inventario de status existentes (NO romper — el conductor debe manejarlos todos)

- **INIT:** `INIT_FAILED`, `SUSPEND_DETECTED`, `RESUME_AT_EXECUTE`, `RESUME_AFTER_ESCALATION`,
  `RESUME_AT_CP03`, `RESUME_AT_CP04`, `SPRINT_CONTRACT_READY`
- **EXECUTE:** `INTERVIEWER_REQUIRED` (+ variante `interviewer_mode: COMPLEMENTARIO`),
  `EXECUTION_FAILED`, `ESCALATION_REQUIRED`, `EXECUTION_COMPLETE`
- **POST_CP03:** `CP04_READY`, `REWORK_COMPLETE`, `STRATEGIC_REJECTION`
- **POST_CP04:** `CP04_DECLINED`, `AUDIT_FAILED`, `CLOSURE_READY`, `REWORK_AFTER_REJECTION`
- **CLOSE:** `CLOSE_BLOCKED`, `CLOSE_READY`, `HANDOFF_READY`, `PHASE_COMPLETE_NO_HANDOFF`
- **SUSPEND:** `SUSPENDED`
- **NUEVOS:** `WORKER_REQUIRED`, `ORCHESTRATOR_REQUIRED`

---

## 4. Cambios archivo por archivo

Rutas relativas a `Harness_Forecaster/`.

### 4.1 `.claude/agents/discovery-governor.md` (el grueso del trabajo)

**A. Sección "Mecanismo de invocación de workers y orchestrator" (≈ líneas 47–61):** reescribir.
- Hoy dice "Todos los agentes se invocan vía CLI … `$prompt | claude --agent … --print …`".
- Nuevo: el governor **no invoca a nadie**. Emite `WORKER_REQUIRED` / `ORCHESTRATOR_REQUIRED` con el
  bloque `dispatch`. El conductor (sesión principal) es el único que spawnea, vía la herramienta
  `Agent`. Conservar la nota del interviewer (ya delegado) como caso de referencia.

**B. Modo EXECUTE — convertir de secuencia monolítica a DESPACHADOR DE UN PASO.** Hoy EXECUTE corre
PLAN → interviewer → synthesizer → analyst → configurator DRAFT con CLI intercalado (≈ líneas
628–878). Reemplazar por una tabla de decisión que, leyendo disco, determina el ÚNICO próximo paso:

| Estado en disco | Retorno del governor |
|---|---|
| sin `orchestration_plan` en execution-state | `ORCHESTRATOR_REQUIRED` (PLAN), then EXECUTE |
| `starting_point=null` y sin `010_discovery/support/session_notes.json` | `INTERVIEWER_REQUIRED` *(igual que hoy)* |
| `session_notes.json` existe, `interviewer_completed_at=null` | `ORCHESTRATOR_REQUIRED` (INTERVIEWER_DONE), then EXECUTE |
| interviewer marcado, sin `support/synthesis_report.json` | `WORKER_REQUIRED` (synthesizer), then EXECUTE |
| `synthesis_report.json` con `synthesis_decision=SEGUNDA_RONDA_REQUERIDA` | `INTERVIEWER_REQUIRED` + `interviewer_mode: COMPLEMENTARIO` *(igual que hoy)* |
| synthesis COMPLETE y `last_checkpoint` < CP-01 | `ORCHESTRATOR_REQUIRED` (CHECKPOINT-01), then EXECUTE |
| `CP-01` y sin `support/analysis_report.json` | `WORKER_REQUIRED` (analyst), then EXECUTE |
| analyst con discrepancia de categoría > 1 nivel o historial < 3 meses | `ESCALATION_REQUIRED` *(igual que hoy)* |
| `analysis_report.json` ok y `last_checkpoint` < CP-02 | `ORCHESTRATOR_REQUIRED` (CHECKPOINT-02), then EXECUTE |
| `CP-02` y sin `deliverables/client_profile.json`+`onboarding_config.json` | `WORKER_REQUIRED` (configurator DRAFT), then EXECUTE |
| drafts existen y `last_checkpoint` < CP-03 | `ORCHESTRATOR_REQUIRED` (CHECKPOINT-03), then EXECUTE |
| `CP-03` | `EXECUTION_COMPLETE` *(gate de operador, igual que hoy)* |

Cada fila = un retorno. El governor **verifica artefactos en disco** como mecanismo de detección de
éxito/fallo del paso previo; si el artefacto esperado falta → `EXECUTION_FAILED` y (en el siguiente
turno, o vía un `ORCHESTRATOR_REQUIRED` WORKER_FAILED) registrar el fallo. **Nunca esperar en bucle.**

**C. Modo POST_CP04 — misma descomposición** (hoy ≈ líneas 953–1112). Secuencia actual
(CHECKPOINT-04 → COMMIT → CHECKPOINT-05 → pre-registro de campos MISSING → evaluator → leer verdict):

| Estado | Retorno |
|---|---|
| aprobado y `last_checkpoint` < CP-04 | `ORCHESTRATOR_REQUIRED` (CHECKPOINT-04), then POST_CP04 |
| `CP-04` y sin `deliverables/data_intake_guide.*` | `WORKER_REQUIRED` (configurator COMMIT), then POST_CP04 |
| COMMIT ok y `last_checkpoint` < CP-05 | `ORCHESTRATOR_REQUIRED` (CHECKPOINT-05), then POST_CP04 |
| `CP-05` y sin `605_eval/verdict.json` | el governor pre-registra campos MISSING él mismo (no spawnea) → `WORKER_REQUIRED` (evaluator), then POST_CP04 |
| `verdict.json` existe | leer y decidir `CLOSURE_READY` / rechazo *(igual que hoy)* |

> El **pre-registro de campos MISSING** (Paso 6 actual, ≈ líneas 1040–1061) lo hace el governor
> directamente con Read/Edit sobre `harness-state.json` — NO requiere spawnear. Se mantiene como
> paso interno antes de emitir `WORKER_REQUIRED` (evaluator).

**D. Modo POST_CP03 rework** (≈ líneas 910–949): el re-DRAFT pasa a `WORKER_REQUIRED`
(configurator DRAFT con los cambios solicitados en el `dispatch.prompt`), then POST_CP03.

**E. Protocolo de Rechazo** (≈ líneas 1242–1259): las acciones "Re-invocar `discovery-analyst`
vía CLI" / "Re-invocar `discovery-configurator` COMMIT" pasan a retornos `WORKER_REQUIRED` con el
`then` que devuelve al gate correspondiente (CP-02 / COMMIT). El caso "D1 < 0.80" ya retorna
`INTERVIEWER_REQUIRED` — se conserva.

**F. Eliminar los ~9 bloques ` ```powershell … claude --print … ``` `** repartidos por el archivo y
reemplazarlos por la construcción del `dispatch.prompt` correspondiente (es el MISMO texto de prompt
que hoy se ejecuta; ahora se emite dentro de la señal `dispatch` en vez de correrse).

**G. Frontmatter:** el bloque `agents:` y `tools: [Agent]` pueden quedarse como documentación de qué
subagentes participan, pero agregar una nota en el cuerpo: "el governor NO spawnea estos agentes — los
nombra en `dispatch` para que el conductor los spawnee". (Opcional: quitar `Agent` de `tools` para
evitar confusión, ya que el governor no lo usará.)

### 4.2 `commands/faro-discovery.md` — de 1 línea a CONDUCTOR

Hoy solo invoca `discovery-governor` en `MODO: INIT`. Reescribir como el bucle de la Sección 2:
1. Invoca governor `MODO: INIT`.
2. Bucle de despacho: mientras el status sea `WORKER_REQUIRED`/`ORCHESTRATOR_REQUIRED`, spawnea
   `dispatch.agent` con `dispatch.prompt` (herramienta `Agent`) y re-invoca al governor con
   `MODO: <dispatch.then>`.
3. `INTERVIEWER_REQUIRED` → correr el `discovery-interviewer` inline (es interactivo, usa
   AskUserQuestion con el operador) → re-invocar governor con `interviewer_complete: true`
   (+ `interviewer_mode: COMPLEMENTARIO` y `campos_bloqueantes` si venían en la señal).
4. Gates de operador (`SPRINT_CONTRACT_READY`, `EXECUTION_COMPLETE`, `CP04_READY`, `CLOSURE_READY`,
   etc.) → presentar al operador con AskUserQuestion → re-invocar governor con la respuesta
   (`MODO: POST_CP03 / POST_CP04 / CLOSE`, con `cp03_decision` / `cp04_approved` / `handoff_decision`).
5. Terminales (`CLOSE_READY`, `HANDOFF_READY`, `PHASE_COMPLETE_NO_HANDOFF`, `SUSPENDED`, `*_FAILED`)
   → informar al operador y terminar.
6. Incluir una tabla explícita que mapee CADA status del inventario (3.1) a la acción del conductor.

### 4.3 `commands/faro-restart.md` y `commands/faro-continue.md`

**Primer paso de implementación: leer ambos archivos** (no inventariados aún). Aplican el mismo bucle
conductor, arrancando al governor en `MODO: INIT` (el ritual E10-B detecta el punto de reanudación y
retorna `RESUME_AT_*`). Para no triplicar el bucle: extraerlo a un workflow común en
`.claude/workflows/` (p. ej. `conductor_loop.md`) y que los tres comandos lo referencien, o duplicar
con cuidado si el harness no soporta include de workflows.

### 4.4 `orchestrator`, `workers`, `evaluator` — cambios MÍNIMOS (solo descripción)

No cambia su lógica, sus prompts de entrada ni sus retornos. Solo corregir las líneas de descripción
que afirman que "el governor spawea los workers":
- `.claude/agents/discovery-orchestrator.md`: frontmatter `description` (≈ líneas 6–7) y cuerpo
  (≈ líneas 21–22): "El governor es quien spawea los workers" → "El conductor (sesión principal) es
  quien spawnea a todos los agentes; el orchestrator solo gestiona el estado".
- Revisar `discovery-synthesizer.md`, `discovery-analyst.md`, `discovery-configurator.md`,
  `discovery-evaluator.md` por frases equivalentes y corregirlas.

### 4.5 `flows/010_discovery_flow.md`

Actualizar diagrama y narrativa: el conductor es la sesión principal; A/B/C/workers son hermanos.
Reflejar el handshake de despacho (governor decide → conductor spawnea → re-invoca governor).

### 4.6 `.claude/skills/discovery-state-schema/SKILL.md`

Sin cambios estructurales (los archivos de estado NO cambian de formato). Opcional: una nota de que
el avance entre pasos lo orquesta el conductor, no el governor.

---

## 5. Compatibilidad y migración

- **Los archivos de estado en disco NO cambian de formato.** Una prueba suspendida (Test_004A) se
  reanuda con el governor refactorizado SIN migración.
- El governor sigue siendo idempotente y resumible por checkpoint → el bucle conductor puede arrancar
  en cualquier punto.
- La regla single-writer se conserva intacta (governor → `harness-state.json`; orchestrator →
  `execution-state.json`; workers → artefactos en `010_discovery/`; evaluator → `605_eval/verdict.json`).

---

## 6. Plan de prueba (validación del refactor)

1. **Reanudar Test_004A** (`C:\Users\USUARIO\Documents\Triple S\Test_Forecaster\Test_004A`) con el
   governor refactorizado. Antes, **sincronizar** los archivos editados del repo fuente a la carpeta
   de prueba `.claude/` (ver método en `progress.md` sesión 30: copiar agents/skills/commands sin
   tocar artefactos ni `600_persistence/`).
2. El conductor debe despachar: synthesizer → CP-01 → analyst → CP-02 → configurator DRAFT → CP-03 →
   gate de operador, **sin colgarse**, cada subagente spawneado por la sesión principal.
3. Verificar que cada artefacto aparece en disco entre dispatches (`support/synthesis_report.json`,
   `support/session_data.json`, `support/analysis_report.json`, `deliverables/*.json`). Revisar de
   paso **T-165**: cómo queda `responsable_pagos` en `session_data.json` (resuelto vs. MISSING).
4. Continuar el gate CP-03/CP-04 con AskUserQuestion → COMMIT → auditoría hasta APPROVED.
5. **Caso de fallo:** forzar un worker sin output (o artefacto ausente) → el governor debe detectar el
   artefacto faltante y emitir `EXECUTION_FAILED`, NO esperar indefinidamente.

---

## 7. Riesgos y mitigaciones

- **Más turnos = más contexto en la sesión principal.** Mitigado: cada turno agrega solo bloques
  pequeños (señal + resumen breve del worker); el trabajo pesado queda en el contexto de cada subagente.
- **Duplicación del bucle conductor** en 3 comandos. Mitigado: extraer a workflow común (4.3).
- **El governor debe ser un despachador de un paso impecable.** Es el cambio más delicado. Su lógica
  de "dónde estoy" YA existe (`starting_point` del PLAN + verificación de artefactos); solo se
  reorganiza de secuencia monolítica a tabla de decisión por estado.

---

## 8. Orden de implementación

1. **Leer** `commands/faro-restart.md` y `commands/faro-continue.md` (cerrar inventario de conductores).
2. **Refactor `discovery-governor.md`** (T-166a): EXECUTE → despachador (B), POST_CP04 (C),
   POST_CP03 rework (D), rechazo (E), eliminar bloques CLI (F), reescribir mecanismo (A), nota
   frontmatter (G).
3. **Reescribir `faro-discovery.md`** como conductor; replicar/compartir en `faro-restart.md` y
   `faro-continue.md` (T-166b).
4. **Corregir descripciones** en orchestrator/workers/evaluator (T-166c).
5. **Actualizar** `flows/010_discovery_flow.md` y la nota del schema (T-166d).
6. **Registrar DEC-051** (modelo conductor) en `decisions.md`; actualizar `progress.md`.
7. **Prueba** de reanudación en Test_004A (T-166e). Si pasa → marcar T-166 `implementada`.

---

## 9. Subtareas (registradas en tasks.md bajo T-166)

- **T-166a** — governor → despachador de un paso (EXECUTE / POST_CP03 / POST_CP04 / rechazo); eliminar bloques `claude --print`.
- **T-166b** — conductor en `faro-discovery.md` (+ restart/continue, idealmente vía workflow común).
- **T-166c** — correcciones de descripción en orchestrator / workers / evaluator.
- **T-166d** — actualizar `flows/010_discovery_flow.md` + nota en `discovery-state-schema` + DEC-051.
- **T-166e** — prueba de reanudación en Test_004A con el refactor; validar que no se cuelga y revisar T-165.

---

## 10. Referencias

- Hallazgo y causa: `tasks.md` (T-166), `lessons.md` (LEC-059), `progress.md` (sesión 30).
- Doc oficial Claude Code (regla de anidamiento): https://code.claude.com/docs/en/sub-agents
  ("subagents cannot spawn other subagents").
- Patrón de referencia ya existente: delegación del `discovery-interviewer`
  (`INTERVIEWER_REQUIRED` → sesión principal lo corre → re-invoca governor con `interviewer_complete: true`).
- Archivos a tocar: `.claude/agents/discovery-governor.md`, `commands/faro-discovery.md`,
  `commands/faro-restart.md`, `commands/faro-continue.md`, `.claude/agents/discovery-orchestrator.md`
  (+ synthesizer/analyst/configurator/evaluator: solo descripción), `flows/010_discovery_flow.md`,
  `.claude/skills/discovery-state-schema/SKILL.md`.

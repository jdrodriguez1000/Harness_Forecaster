# Bucle Conductor — Harness 010 Discovery de FARO

> **Quién ejecuta esto:** la **sesión principal** de Claude Code (el conductor), al correr
> `/faro-discovery`, `/faro-restart` o `/faro-continue`. Este archivo es la lógica común que
> los tres comandos comparten para conducir el harness 010.

## Por qué existe este bucle

El `discovery-governor` es el **cerebro** del harness pero es un **subagente**, y un subagente
no puede spawnear otros subagentes (doc oficial de Claude Code). Por eso el governor **no
invoca a nadie**: en cada turno hace un solo paso de decisión y retorna un bloque
`GOVERNOR_RESULT`. La **sesión principal es la única que puede spawnear** subagentes (vía la
herramienta `Agent`), así que actúa como **conductor**: spawnea lo que el governor pida y lo
re-invoca, hasta llegar a un estado terminal o a un gate del operador.

Esto reemplaza el patrón roto en el que el governor encadenaba workers con `claude --print` en
background y se colgaba (T-166 / LEC-059).

## Cómo spawnear

- **Agentes (governor, orchestrator, synthesizer, analyst, configurator, evaluator):** usar la
  herramienta `Agent` con `subagent_type` = nombre del agente y `prompt` = el texto indicado.
  El mensaje final del subagente vuelve al conductor como resultado de la herramienta — de ahí
  se extrae el bloque de resultado (`GOVERNOR_RESULT`, `PLAN_RESULT`, `CHECKPOINT_OK`, etc.).
- **discovery-interviewer:** es la **excepción** — es interactivo (conversa con el operador vía
  AskUserQuestion). **NO se spawnea** con la herramienta `Agent`. Se ejecuta **inline en esta
  sesión**: el conductor lee `.claude/agents/discovery-interviewer.md` y conduce las entrevistas
  él mismo siguiendo esas instrucciones.

---

## El bucle

```
1. resultado = spawn(discovery-governor, prompt_inicial)     # prompt_inicial lo define cada comando
2. repetir:
     parsear GOVERNOR_RESULT de `resultado`  (campos: mode, status, dispatch?, context, …)
     actuar según `status` (ver tabla abajo)
     - si la acción produce una re-invocación → resultado = spawn(discovery-governor, nuevo_prompt); continuar
     - si la acción es TERMINAL → salir del bucle
```

El governor es **stateless**: cada `spawn(discovery-governor, …)` es una instancia fresca que
re-deriva su posición leyendo el disco. El conductor nunca le pasa el stdout de los workers.

---

## Tabla de acciones por `status`

### Despacho automático (sin operador)

| status | Acción del conductor |
|---|---|
| `ORCHESTRATOR_REQUIRED` | `spawn(dispatch.agent, dispatch.prompt)` (es `discovery-orchestrator`). Luego `spawn(discovery-governor, "MODO: " + dispatch.then)`. |
| `WORKER_REQUIRED` | `spawn(dispatch.agent, dispatch.prompt)` (synthesizer / analyst / configurator / evaluator). Luego `spawn(discovery-governor, "MODO: " + dispatch.then)`. |

> El conductor pasa `dispatch.prompt` **literal**. No lo edita ni lo interpreta. Tras correr el
> subagente despachado, **no** verifica su salida: re-invoca al governor, que verificará los
> artefactos en disco en el turno siguiente (esa es la robustez del modelo). Si el subagente
> despachado dejó un resultado de error evidente, igual re-invocar al governor — él decidirá
> `EXECUTION_FAILED`/`WORKER_FAILED`.

### Interviewer (inline)

| status | Acción del conductor |
|---|---|
| `INTERVIEWER_REQUIRED` (sin `interviewer_mode`) | Conducir la **primera ronda** de entrevistas inline (leer `.claude/agents/discovery-interviewer.md` y seguirlo; usa `inputs` I1/I2/I3 como contexto). Al terminar: `spawn(discovery-governor, "MODO: EXECUTE\ninterviewer_complete: true")`. |
| `INTERVIEWER_REQUIRED` con `interviewer_mode: COMPLEMENTARIO` | Conducir una **segunda ronda acotada** inline, preguntando solo los `campos_bloqueantes` (ver `open_questions_path`). Al terminar: `spawn(discovery-governor, "MODO: EXECUTE\ninterviewer_complete: true")`. |

### Gates del operador (vía AskUserQuestion)

| status | Gate y re-invocación |
|---|---|
| `SPRINT_CONTRACT_READY` | Mostrar el `sprint_contract` al operador y preguntar **aprobar / rechazar**. Si aprueba → `spawn(discovery-governor, "MODO: EXECUTE\nsprint_contract_approved: true")`. Si rechaza → informar y terminar (el operador ajusta el brief y reinicia). |
| `EXECUTION_COMPLETE` | Gate **CP-03**: mostrar los borradores (`client_profile.json`, `onboarding_config.json`) y preguntar **aprobar / pedir cambios**. Aprobar → `spawn(discovery-governor, "MODO: POST_CP03\ncp03_decision: approved")`. Cambios → recoger la descripción y `spawn(discovery-governor, "MODO: POST_CP03\ncp03_decision: rework\nchanges: <texto>")`. |
| `REWORK_COMPLETE` | Re-presentar el gate **CP-03** (mismo manejo que `EXECUTION_COMPLETE`). |
| `CP04_READY` | Gate **CP-04**: confirmar al operador que se proceda al COMMIT (BD/Storage/guía/evento). Aprobar → `spawn(discovery-governor, "MODO: POST_CP04\ncp04_approved: true")`. Declinar → `spawn(discovery-governor, "MODO: POST_CP04\ncp04_approved: false")`. |
| `ESCALATION_REQUIRED` | Presentar `escalation_reason` + `next_action` al operador y obtener su decisión. Según la decisión, re-invocar el governor en el modo que corresponda o terminar pausando. **No** continuar en automático sin respuesta del operador. |

### Cierre

| status | Acción |
|---|---|
| `CLOSURE_READY` | La auditoría aprobó. Ejecutar el cierre técnico: `spawn(discovery-governor, "MODO: CLOSE")` (sin `handoff_decision`). |
| `CLOSE_READY` | Cierre técnico hecho. Preguntar al operador si desea **continuar al 015 Intake ahora**. Sí → `spawn(discovery-governor, "MODO: CLOSE\nhandoff_decision: yes")`. No → `spawn(discovery-governor, "MODO: CLOSE\nhandoff_decision: no")`. |

### Reanudación (provienen del Modo INIT / E10-B)

| status | Acción |
|---|---|
| `RESUME_AT_EXECUTE` | `spawn(discovery-governor, "MODO: EXECUTE")` y continuar el bucle. |
| `RESUME_AFTER_ESCALATION` | Conducir el interviewer **COMPLEMENTARIO** inline con los campos de `escalations`; al terminar `spawn(discovery-governor, "MODO: EXECUTE\ninterviewer_complete: true")`. |
| `RESUME_AT_CP03` | Presentar el gate **CP-03** al operador (como `EXECUTION_COMPLETE`). |
| `RESUME_AT_CP04` | `spawn(discovery-governor, "MODO: POST_CP04\ncp04_approved: true")` (CP-03 ya estaba aprobado; el operador confirma el COMMIT si se desea un gate explícito). |

### Estados terminales (salir del bucle e informar al operador)

| status | Mensaje |
|---|---|
| `HANDOFF_READY` | Mostrar `message` (deploy del 015 hecho — reiniciar sesión y `/faro-restart`). Terminar. |
| `PHASE_COMPLETE_NO_HANDOFF` | Mostrar `message` (010 completo, 015 diferido). Terminar. |
| `SUSPEND_DETECTED` | Informar que el harness está suspendido — usar `/faro-continue`. Terminar. |
| `SUSPENDED` | Confirmar la suspensión y terminar. |
| `INIT_FAILED` | Mostrar `error` al operador (brief incompleto, etc.) y terminar. |
| `EXECUTION_FAILED` | Mostrar `error` (worker afectado / checkpoint). Terminar y sugerir revisar `600_persistence/claude-progress.txt`. |
| `AUDIT_FAILED` | Mostrar `error` (evaluator no escribió verdict). Terminar. |
| `CLOSE_BLOCKED` | Mostrar `error` (precondición de cierre no cumplida). Terminar. |
| `CP04_DECLINED` | Informar que el operador no aprobó el COMMIT. Terminar (los borradores quedan para revisión). |
| `STRATEGIC_REJECTION` | Informar el rechazo estratégico de los borradores. Terminar. |
| `REWORK_AFTER_REJECTION` | Informativo: hubo rechazo técnico y el worker fue re-despachado. El governor ya re-encamina a auditoría — **continuar el bucle** re-invocando con el `dispatch` que acompañe (si lo trae) o `MODO: POST_CP04`. |

---

## Reglas del conductor

1. **Un spawn de governor por turno de decisión.** Nunca correr dos pasos del governor sin
   pasar por el conductor.
2. **No editar `dispatch.prompt`.** Pasarlo literal al `subagent_type` indicado en `dispatch.agent`.
3. **El interviewer va inline**, nunca vía `Agent`.
4. **Salvaguarda anti-bucle infinito:** si el governor retorna el **mismo** `WORKER_REQUIRED`/
   `ORCHESTRATOR_REQUIRED` dos veces seguidas para el mismo agente sin que cambie el estado en
   disco, detener e informar al operador (probable worker que no produce artefacto). No re-spawnear
   indefinidamente.
5. **Los gates SIEMPRE pasan por el operador** con AskUserQuestion — el conductor nunca los
   auto-aprueba.
6. **Verificar disponibilidad del agente** antes del primer spawn del governor: si
   `.claude/agents/discovery-governor.md` no existe, informar y detener.

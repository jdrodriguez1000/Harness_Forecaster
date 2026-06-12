---
name: discovery-state-schema
description: Schemas y reglas de escritura de los tres archivos de persistencia del harness
  010 Discovery de FARO — harness-state.json (governor), execution-state.json (orchestrator)
  y claude-progress.txt (governor). Define la Single Writer Rule y las reglas de lectura
  para cada agente. Usar cuando discovery-orchestrator escribe execution-state.json o
  cuando discovery-governor lee o escribe harness-state.json.
user-invocable: false
---

Los tres archivos de persistencia viven en `600_persistence/` del directorio de trabajo
del proyecto. Crearlos si no existen.

---

## Archivo 1 — 600_persistence/harness-state.json

**Escritor único:** discovery-governor. Ningún otro agente escribe este archivo.
**Lectores:** discovery-orchestrator (lee Sprint Contract al iniciar en Modo PLAN).

```json
{
  "phase": "010_discovery",
  "mode": "INICIO | CONTINUACIÓN",
  "governor_mode": "INIT | EXECUTE | POST_CP03 | POST_CP04 | CLOSE | SUSPEND",
  "tenant_id": null,
  "sprint_contract": {
    "objective": "Capturar el contexto completo del cliente y configurar el sistema para iniciar el onboarding",
    "client": {
      "razon_social": "",
      "categoria_comercial": "M | L | XL",
      "fecha_firma": ""
    },
    "inputs": {
      "I1": "<path al contrato firmado o null>",
      "I2": "<path a datos comerciales del cliente o null>",
      "I3": "<lista de restricciones conocidas o null>"
    },
    "workers": [
      "discovery-interviewer",
      "discovery-analyst",
      "discovery-configurator"
    ],
    "checkpoints": ["CP-01", "CP-02", "CP-03", "CP-04", "CP-05"],
    "done_criteria": [
      "todos los campos obligatorios registrados en BD",
      "ITO calculado y categoría M/L/XL confirmada",
      "nivel cold start documentado",
      "guía de datos enviada al contacto principal",
      "carpeta Storage del tenant creada con 6 subcarpetas",
      "registros BD creados con estado onboarding",
      "evento onboarding_discovery_complete emitido"
    ]
  },
  "status": "PENDING_CONTRACT | ACTIVE | PENDING_OPERATOR_APPROVAL | IN_REWORK | HOLD | AUDIT_PENDING | PHASE_COMPLETE | SUSPENDED",
  "operator_approvals": [],
  "escalations": [],
  "change_requests": [],
  "last_updated": "<timestamp ISO 8601>",
  "suspension": null
}
```

**Diferencia entre `mode` y `governor_mode`:**

- `mode` — origen del ciclo: `INICIO` (harness nuevo) o `CONTINUACIÓN` (reanudación). Lo lee el orchestrator en Modo PLAN. No cambia durante la ejecución.
- `governor_mode` — modo de ejecución vivo del governor. El governor lo actualiza al entrar a cada modo (`INIT` → `EXECUTE` → `POST_CP03` → `POST_CP04` → `CLOSE`, y `SUSPEND` si se suspende). Sirve para diagnóstico y reanudación: refleja en todo momento dónde está el governor. Inicializado en `INIT` en E10-A.3. **No confundir** con `suspension.governor_mode`, que registra el modo al que se debe reanudar, no el modo vivo.

**Campo `tenant_id`:**

- Identificador único del cliente. **Fuente única de verdad = governor** (DEC-047): lo genera en E10-A (Paso C de la Construcción del Sprint Contract) a partir de la razón social del brief (slug en minúsculas + sufijo numérico de 4 dígitos, p. ej. `prolimex-s-a-de-c-v-4528`) y lo persiste aquí **antes** de despachar cualquier worker.
- El `analyst` y el `configurator` **leen** este campo — nunca lo generan. Si está `null` o vacío cuando lo necesitan, retornan `BLOCKED`.
- Idempotente en reanudación: si ya tiene valor, el governor lo reutiliza (no regenera).

**Valores de `status`:**

| Valor | Momento |
|-------|---------|
| `PENDING_CONTRACT` | Harness inicializado, Sprint Contract aún no aprobado |
| `ACTIVE` | Sprint Contract aprobado, ejecución en curso |
| `PENDING_OPERATOR_APPROVAL` | CP-03 alcanzado, draft presentado al operador |
| `IN_REWORK` | C emitió REJECTED — governor re-ejecuta workers afectados |
| `HOLD` | Rechazo estratégico — requiere nueva aprobación humana |
| `AUDIT_PENDING` | CP-05 completo, governor solicita C (el conductor lo spawnea) |
| `PHASE_COMPLETE` | C emitió APPROVED — fase cerrada |
| `SUSPENDED` | `/faro-suspend` invocado — esperando `/faro-continue` |

**Estructura de `operator_approvals`** (escrita por governor en CP-04):
```json
[
  {
    "checkpoint": "CP-04",
    "timestamp": "<ISO 8601>",
    "approved_by": "operador Triple S",
    "nota": "<nota libre del operador si aplica>"
  }
]
```

**Estructura de `escalations`** (escrita por governor ante bloqueos):
```json
[
  {
    "id": "ESC-001",
    "timestamp": "<ISO 8601>",
    "campo": "<campo o situación que generó el escalamiento>",
    "razon": "<por qué se escaló>",
    "estado": "OPEN | RESOLVED",
    "resolucion": null
  }
]
```

**Estructura de `suspension`** (escrita por governor al recibir /faro-suspend):
```json
{
  "timestamp": "<ISO 8601>",
  "harness": "010_discovery",
  "governor_mode": "INIT | EXECUTE | POST_CP03 | POST_CP04 | CLOSE",
  "last_checkpoint": "null | CP-01 | CP-02 | CP-03 | CP-04 | CP-05",
  "context_note": "<descripción del estado al suspender>",
  "resume_instruction": "<qué hacer al reanudar>"
}
```

---

## Archivo 2 — 600_persistence/execution-state.json

**Escritor único:** discovery-orchestrator. Ningún otro agente escribe este archivo.
**Lectores:** discovery-governor (lee checkpoints y artifacts para decidir gates).

```json
{
  "orchestration_plan": {
    "phase": "010_discovery",
    "sequence": ["discovery-interviewer", "discovery-analyst", "discovery-configurator"],
    "parallelization": false,
    "nota_e7": "Dependencia secuencial estricta — E7 no aplica en este harness",
    "checkpoints": {
      "CP-01": "discovery-interviewer completo — session_data.json",
      "CP-02": "discovery-analyst completo — analysis_report.json",
      "CP-03": "discovery-configurator DRAFT — client_profile.json + onboarding_config.json — GATE: aprobación operador",
      "CP-04": "Operador aprobó — discovery-configurator COMMIT ejecutado",
      "CP-05": "BD + Storage + guía + evento confirmados — EXECUTION_COMPLETE"
    }
  },
  "last_checkpoint": null,
  "status": "PENDING | IN_PROGRESS | PENDING_OPERATOR_APPROVAL | EXECUTION_COMPLETE | WORKER_FAILED",
  "interviewer_completed_at": null,
  "interviewer_artifacts": {
    "session_notes": null,
    "stakeholder_map": null
  },
  "session_data_path": null,
  "analysis_report_path": null,
  "artifacts": {
    "client_profile": null,
    "onboarding_config": null,
    "data_intake_guide": null,
    "db_records": null,
    "storage_tenant": null,
    "evento": null
  },
  "worker_errors": [],
  "last_updated": "<timestamp ISO 8601>"
}
```

**Marcador del tramo interactivo (`interviewer_completed_at` / `interviewer_artifacts`):**

El discovery-interviewer es interactivo y **no tiene checkpoint propio** — CP-01 lo registra el
synthesizer. Sin un marcador, `execution-state.json` quedaría congelado en `last_checkpoint: null`
entre el fin de las entrevistas y la corrida del synthesizer, sin evidencia de que el tramo
interactivo ocurrió. El governor, tras verificar `session_notes.json` + `stakeholder_map.json`,
invoca al orchestrator en `[MODO: INTERVIEWER_DONE]`, que puebla estos campos **sin avanzar
`last_checkpoint`**. Es idempotente (una segunda ronda sobrescribe el timestamp).

**Valores de `last_checkpoint`:**

| Valor | Significa |
|-------|-----------|
| `null` | orchestration_plan persistido, ningún worker ha terminado |
| `"CP-01"` | discovery-interviewer completó; `session_data_path` tiene el path |
| `"CP-02"` | discovery-analyst completó; `analysis_report_path` tiene el path |
| `"CP-03"` | discovery-configurator DRAFT completó; `artifacts.client_profile` y `artifacts.onboarding_config` tienen paths; `status: PENDING_OPERATOR_APPROVAL` |
| `"CP-04"` | Operador aprobó; discovery-configurator COMMIT en curso |
| `"CP-05"` | Todas las escrituras confirmadas; `status: EXECUTION_COMPLETE`; `artifacts` completo |

**Estructura de `worker_errors`** (cuando `status: WORKER_FAILED`):
```json
[
  {
    "worker": "discovery-interviewer | discovery-analyst | discovery-configurator",
    "checkpoint_at_failure": "null | CP-01 | CP-02 | CP-03 | CP-04",
    "error": "<descripción del error>",
    "timestamp": "<ISO 8601>"
  }
]
```

**Creación inicial** (responsabilidad del governor en E10-A):
El governor crea el archivo con estructura mínima — `orchestration_plan: null`,
`last_checkpoint: null`, `status: "PENDING"`. El orchestrator escribe el `orchestration_plan`
y los checkpoints sobre ese archivo ya existente. Si el orchestrator llega y no existe,
lo crea como fallback antes de escribir.

---

## Archivo 3 — 600_persistence/claude-progress.txt

**Escritor único:** discovery-governor. Ningún otro agente escribe este archivo.
**Lectores:** discovery-governor (E10-B Paso 3 — orientación al reanudar).

**Formato de línea:**
```
[TIPO_EVENTO] [timestamp ISO 8601] — <descripción del evento>
```

**Tipos de evento válidos:**

| Tipo | Momento |
|------|---------|
| `INICIO` | governor arranca en modo INICIO (E10-A) |
| `E10-A COMPLETO` | Carpetas, archivos y git listos |
| `CONTINUACIÓN` | governor arranca en modo CONTINUACIÓN (E10-B) |
| `SPRINT_CONTRACT_DRAFT` | Sprint Contract construido, pendiente aprobación |
| `SPRINT_CONTRACT_APROBADO` | Operador aprobó el Sprint Contract |
| `DIALOGUER_REQUIRED` | Se requiere sesión interactiva con el cliente |
| `CP-01` | discovery-interviewer completó — session_data.json |
| `CP-02` | discovery-analyst completó — analysis_report.json |
| `CP-03` | discovery-configurator DRAFT completó — pendiente aprobación operador |
| `CP-04` | Operador aprobó artefactos draft — COMMIT iniciado |
| `CP-05` | Escrituras completas — EXECUTION_COMPLETE |
| `AUDIT_PENDING` | governor solicita discovery-evaluator (el conductor lo spawnea) |
| `RECHAZO_TECNICO` | C emitió REJECTED por razones técnicas |
| `RECHAZO_ESTRATEGICO` | Rechazo estratégico — fase en HOLD |
| `SUSPENSIÓN` | /faro-suspend invocado |
| `CIERRE` | Fase PHASE_COMPLETE — listo para 015 Intake |

**Reglas:**
- Append-only — nunca modificar ni eliminar entradas anteriores.
- Una línea por evento.
- No usar para logs de depuración ni mensajes intermedios de workers.

---

## Single Writer Rule

| Archivo | Escritor | Lectores |
|---------|----------|----------|
| `600_persistence/harness-state.json` | discovery-governor | discovery-orchestrator |
| `600_persistence/execution-state.json` | discovery-orchestrator | discovery-governor |
| `600_persistence/claude-progress.txt` | discovery-governor | discovery-governor |

Ningún worker (discovery-interviewer, discovery-analyst, discovery-configurator,
discovery-evaluator) escribe ninguno de estos archivos. Los workers solo reportan
paths a quien los spawnea.

> **Modelo conductor (DEC-051):** ni el governor ni el orchestrator spawnean agentes — un
> subagente de Claude Code no puede spawnear otros subagentes. El **único que spawnea** es el
> **conductor** (la sesión principal del comando `/faro-*`). El governor retorna señales
> `WORKER_REQUIRED` / `ORCHESTRATOR_REQUIRED` con un bloque `dispatch` (`agent`, `prompt`,
> `then`); el conductor spawnea al agente nombrado y re-invoca al governor con `[MODO: then]`.
> Por eso, donde este documento dice "governor spawnea X", léase "governor solicita X y el
> conductor lo spawnea". La Single Writer Rule sobre los archivos de estado no cambia.

---

## Reglas de escritura para discovery-orchestrator

1. **Persistir orchestration_plan completo antes de que el conductor spawnee cualquier worker** (E12). Si falla la escritura, retornar `PLAN_ERROR` inmediatamente.
2. **Actualizar `last_checkpoint` inmediatamente** al registrar un checkpoint. No acumular actualizaciones.
3. **Nunca reescribir campos ya completados.** Al reanudar, conservar `session_data_path` y `analysis_report_path` ya registrados — solo completar los campos faltantes.
4. **Actualizar `last_updated`** en cada escritura con timestamp ISO 8601 real.
5. **Verificar la escritura** leyendo el archivo después de escribirlo. Si el campo esperado no tiene el valor correcto, retornar `CHECKPOINT_FAILED`.

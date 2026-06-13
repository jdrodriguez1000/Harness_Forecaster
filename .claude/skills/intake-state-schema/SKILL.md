---
name: intake-state-schema
description: Schemas y reglas de escritura de los tres archivos de persistencia del harness
  015 Intake de FARO — harness-state.json (intake-governor), execution-state.json
  (intake-orchestrator) y claude-progress.txt (intake-governor). Define la Single Writer Rule,
  los checkpoints CP-01..CP-05 del pipeline P1→P8, los estados del flujo (incluido el rechazo
  de estructura) y las estructuras iniciales que crea el ritual E10-A. Bronce es write-once,
  solo del Worker. Usar cuando intake-orchestrator escribe execution-state.json o cuando
  intake-governor lee o escribe harness-state.json.
user-invocable: false
---

Los tres archivos de persistencia viven en `600_persistence/` del directorio de trabajo del
proyecto (lo crea el ritual E10-A; **no** existen en el repo fuente). Crearlos si no existen.

> **Nota de fase:** El 015 es un **pipeline determinístico** con un **único Worker**
> (`intake-processor`) que ejecuta P1→P8. No hay tramo interactivo (a diferencia del
> interviewer del 010). El único punto de input humano durante la ejecución es la confirmación
> de hoja/cabecera de Excel ambiguo en la 1ª entrega (estado `PENDING_OPERATOR_INPUT`).

---

## Archivo 1 — 600_persistence/harness-state.json

**Escritor único:** intake-governor. Ningún otro agente escribe este archivo.
**Lectores:** intake-orchestrator (lee Sprint Contract al iniciar en Modo PLAN).

```json
{
  "phase": "015_intake",
  "mode": "INICIO | CONTINUACIÓN",
  "governor_mode": "INIT | EXECUTE | POST_EXECUTION | POST_AUDIT | CLOSE | SUSPEND",
  "tenant_id": null,
  "delivery_id": null,
  "ingest_mode": "batch | incremental | null",
  "sprint_contract": {
    "objective": "Recibir los datos del cliente, validarlos y crear la copia Bronce exacta e inmutable; emitir intake_complete hacia 020 ‖ 025",
    "client": { "razon_social": "", "tenant_id": "" },
    "inputs": {
      "evento_010": "<path a onboarding_discovery_complete | AUSENTE>",
      "client_config": "<path o referencia>",
      "bronze_dir": "<path a 005_bronze/>",
      "snapshot_esquema1": "<path al archivo del cliente | PENDIENTE>",
      "snapshot_esquema2": "<path | N/A>",
      "huella_formato": "<presente | a determinar>"
    },
    "worker": "intake-processor",
    "checkpoints": ["CP-01", "CP-02", "CP-03", "CP-04", "CP-05"],
    "done_criteria": [
      "estructura validada o rechazada con intake_rejection.json",
      "tipos validados (conteos registrados)",
      "duplicados detectados según modo",
      "Bronce bit-exacto e inmutable con SHA-256 persistido",
      "_manifest.json e intake_report.json existen",
      "intake_log creado y tenants.last_intake_at actualizado",
      "evento intake_complete emitido como último paso"
    ]
  },
  "status": "PENDING_CONTRACT | ACTIVE | PENDING_OPERATOR_INPUT | REJECTED_STRUCTURE | AUDIT_PENDING | IN_REWORK | HOLD | PHASE_COMPLETE | SUSPENDED",
  "operator_approvals": [],
  "escalations": [],
  "change_requests": [],
  "last_updated": "<timestamp ISO 8601>",
  "suspension": null
}
```

**`mode` vs `governor_mode`:**
- `mode` — origen del ciclo: `INICIO` (harness nuevo) o `CONTINUACIÓN` (reanudación). Lo lee
  el orchestrator en Modo PLAN. No cambia durante la ejecución.
- `governor_mode` — modo vivo del governor: `INIT` → `EXECUTE` → `POST_EXECUTION` (gate
  intermedio 12.3 paso 1: verifica `EXECUTION_COMPLETE`, decide si fue rechazo de estructura o
  solicita auditoría) → `POST_AUDIT` (lee `verdict.json`, decide APPROVED/REJECTED) → `CLOSE`.
  `SUSPEND` si se suspende.

**`tenant_id`** — el slug generado por el **010** (fuente única DEC-047). El governor del 015 lo
**lee** del evento `onboarding_discovery_complete` / `client_config`; **nunca lo regenera**. Si
está `null` cuando un módulo lo necesita → `BLOCKED`.

**`delivery_id`** — `YYYYMMDD` de esta entrega; lo fija el governor en E10-A y lo usan el Bronce,
el manifest, el reporte y el evento.

**Valores de `status`:**

| Valor | Momento |
|-------|---------|
| `PENDING_CONTRACT` | Harness inicializado, Sprint Contract aún no aprobado |
| `ACTIVE` | Sprint Contract aprobado, pipeline en curso |
| `PENDING_OPERATOR_INPUT` | Excel ambiguo (1ª entrega): el Worker propone hoja/cabecera y espera confirmación del operador |
| `REJECTED_STRUCTURE` | P2 rechazó: falta ≥ 1 campo mínimo → `intake_rejection.json`, sin Bronce ni evento (flujo normal de entrada, no de calidad) |
| `AUDIT_PENDING` | CP-05 completo, governor solicita C (el conductor lo spawnea) |
| `IN_REWORK` | C emitió REJECTED — governor re-ejecuta los pasos fallidos |
| `HOLD` | Rechazo estratégico/de entrada (archivo no entregado, formato no aceptado) — requiere acción del operador/cliente |
| `PHASE_COMPLETE` | C emitió APPROVED — fase cerrada, 020 ‖ 025 listos para dispararse |
| `SUSPENDED` | `/faro-suspend` invocado |

**Estructura de `operator_approvals`** (Sprint Contract y, si aplica, confirmación de Excel):
```json
[
  { "tipo": "sprint_contract | excel_huella", "timestamp": "<ISO 8601>", "approved_by": "operador Triple S", "nota": "" }
]
```

**Estructura de `escalations`** (bloqueos §2.4: encoding irresoluble, Excel ambiguo, Esquema 2
esperado y no recibido, fallo de Storage):
```json
[
  { "id": "ESC-001", "timestamp": "<ISO 8601>", "tipo": "encoding | excel | esquema2_ausente | storage | estructura", "campo": "", "razon": "", "estado": "OPEN | RESOLVED", "resolucion": null }
]
```

**Estructura de `suspension`:**
```json
{
  "timestamp": "<ISO 8601>",
  "harness": "015_intake",
  "governor_mode": "INIT | EXECUTE | POST_EXECUTION | POST_AUDIT | CLOSE",
  "last_checkpoint": "null | CP-01 | CP-02 | CP-03 | CP-04 | CP-05",
  "context_note": "<estado al suspender>",
  "resume_instruction": "<qué hacer al reanudar>"
}
```

---

## Archivo 2 — 600_persistence/execution-state.json

**Escritor único:** intake-orchestrator. Ningún otro agente escribe este archivo.
**Lectores:** intake-governor (lee checkpoints y artifacts para decidir gates).

```json
{
  "orchestration_plan": {
    "phase": "015_intake",
    "sequence": ["intake-processor"],
    "parallelization": false,
    "nota_e7": "Cadena secuencial determinística P1→P8 — E7 no aplica DENTRO del 015 (el paralelo es DESPUÉS: 020 ‖ 025)",
    "checkpoints": {
      "CP-01": "P1–P2 — formato/encoding/delimitador detectados + gate de estructura (aprobado o REJECTED_STRUCTURE)",
      "CP-02": "P3–P5 — conteos de errores de tipo, duplicados, rango temporal + warnings",
      "CP-03": "P6 — Bronce escrito + SHA-256 + _manifest.json actualizado",
      "CP-04": "P7 — intake_report.json + intake_log + tenants.last_intake_at",
      "CP-05": "P8 — evento intake_complete emitido (último paso) — EXECUTION_COMPLETE"
    }
  },
  "last_checkpoint": null,
  "status": "PENDING | IN_PROGRESS | PENDING_OPERATOR_INPUT | REJECTED_STRUCTURE | EXECUTION_COMPLETE | WORKER_FAILED",
  "early_eval": null,
  "cp01": { "gate": null, "format": null },
  "cp02": { "errores_tipo": null, "duplicados": null, "rango": null, "warnings": [] },
  "artifact_paths": {
    "bronze_schema1": null,
    "bronze_schema2": null,
    "manifest": null,
    "intake_report": null,
    "intake_log": null,
    "intake_rejection": null,
    "event": null
  },
  "bronze_hashes": { "schema1": null, "schema2": null },
  "worker_errors": [],
  "last_updated": "<timestamp ISO 8601>"
}
```

**`early_eval`** (E9, §2.7 del brief) — registro de la evaluación temprana de ~20 fixtures por C
al completar el primer módulo funcional (`schema_validator` + `bronze_writer`):
```json
{ "timestamp": "<ISO 8601>", "fixtures_evaluados": 0, "score": 0.0, "decision": "CONTINUAR | AJUSTAR_SPEC", "nota": "" }
```
Score ≥ 0.7 → `CONTINUAR`. Score < 0.7 → `AJUSTAR_SPEC` antes de seguir.

**Valores de `last_checkpoint`:**

| Valor | Significa |
|-------|-----------|
| `null` | orchestration_plan persistido, Worker no ha terminado P2 |
| `"CP-01"` | P1–P2 completos. Si rechazo: `status: REJECTED_STRUCTURE`, `artifact_paths.intake_rejection` poblado, sin avanzar |
| `"CP-02"` | P3–P5 completos; `cp02` poblado |
| `"CP-03"` | P6 completo; `artifact_paths.bronze_*` y `manifest` poblados; `bronze_hashes` poblado |
| `"CP-04"` | P7 completo; `artifact_paths.intake_report` e `intake_log` poblados |
| `"CP-05"` | P8 completo; `artifact_paths.event` poblado; `status: EXECUTION_COMPLETE` |

**Estructura de `worker_errors`** (cuando `status: WORKER_FAILED`):
```json
[
  { "worker": "intake-processor", "checkpoint_at_failure": "null | CP-01 | ... | CP-04", "paso": "P1..P8", "error": "", "timestamp": "<ISO 8601>" }
]
```

**Creación inicial** (E10-A, responsabilidad del governor): crear con `orchestration_plan: null`,
`last_checkpoint: null`, `status: "PENDING"`. El orchestrator escribe el `orchestration_plan`
sobre ese archivo. Si llega y no existe, lo crea como fallback.

---

## Archivo 3 — 600_persistence/claude-progress.txt

**Escritor único:** intake-governor. **Lectores:** intake-governor (E10-B — orientación al reanudar).
> Excepción del 010 replicada: el orquestador activo (A, B o C) puede añadir su línea de
> progreso; en la práctica A consolida. El append-only se respeta siempre.

**Formato de línea:**
```
[TIPO_EVENTO] [timestamp ISO 8601] — <descripción>
```

**Tipos de evento válidos:**

| Tipo | Momento |
|------|---------|
| `INICIO` | governor arranca en modo INICIO (E10-A) |
| `E10-A COMPLETO` | Carpetas, archivos y git listos; precondición del 010 verificada |
| `CONTINUACIÓN` | governor arranca en modo CONTINUACIÓN (E10-B) |
| `SPRINT_CONTRACT_DRAFT` | Sprint Contract construido, pendiente aprobación |
| `SPRINT_CONTRACT_APROBADO` | Operador aprobó el Sprint Contract |
| `OPERATOR_INPUT_REQUIRED` | Excel ambiguo — se requiere confirmación de hoja/cabecera |
| `CP-01` | P1–P2 completos (formato + gate de estructura) |
| `RECHAZO_ESTRUCTURA` | P2 rechazó — intake_rejection.json, sin Bronce ni evento |
| `CP-02` | P3–P5 completos (tipos, duplicados, rango) |
| `CP-03` | P6 completo — Bronce + SHA-256 + manifest |
| `CP-04` | P7 completo — reportes + intake_log |
| `CP-05` | P8 completo — evento emitido — EXECUTION_COMPLETE |
| `AUDIT_PENDING` | governor solicita intake-evaluator (el conductor lo spawnea) |
| `RECHAZO_TECNICO` | C emitió REJECTED por razones técnicas |
| `RECHAZO_ESTRATEGICO` | Rechazo de entrada (archivo/formato) — fase en HOLD |
| `SUSPENSIÓN` | /faro-suspend invocado |
| `CIERRE` | Fase PHASE_COMPLETE — 020 ‖ 025 listos para dispararse |

**Reglas:** append-only; una línea por evento; no usar para logs de depuración.

---

## Single Writer Rule

| Archivo | Escritor | Lectores |
|---------|----------|----------|
| `600_persistence/harness-state.json` | intake-governor | intake-orchestrator |
| `600_persistence/execution-state.json` | intake-orchestrator | intake-governor |
| `600_persistence/claude-progress.txt` | intake-governor (orquestador activo) | intake-governor |
| **`005_bronze/` (Bronce + manifest + report)** | **intake-processor (Worker), write-once** | 020, 025, intake-evaluator (solo lectura) |

Ni el governor ni el orchestrator escriben en `005_bronze/`. **Ningún harness posterior (020,
025, …) escribe jamás en Bronce** — es la base del invariante del medallón (DEC-024). El
intake-evaluator (C) **solo lee y recalcula hashes**; nunca escribe en `harness-state.json`.

> **Modelo conductor (DEC-051):** ni el governor ni el orchestrator spawnean agentes. El
> **único que spawnea** es el **conductor** (la sesión principal del comando `/faro-*`). El
> governor retorna señales `WORKER_REQUIRED` / `ORCHESTRATOR_REQUIRED` con un bloque `dispatch`
> (`agent`, `prompt`, `then`); el conductor spawnea y re-invoca al governor con `[MODO: then]`.
> Donde se diga "governor spawnea X", léase "governor solicita X y el conductor lo spawnea".

---

## Reglas de escritura para intake-orchestrator

1. **Persistir `orchestration_plan` completo antes de que el conductor spawnee el Worker** (E12).
   Si falla la escritura, retornar `PLAN_ERROR`.
2. **Actualizar `last_checkpoint` inmediatamente** al registrar cada checkpoint. No acumular.
3. **Nunca reescribir campos ya completados.** Al reanudar, conservar paths y hashes ya
   registrados — solo completar los faltantes (la idempotencia del Bronce por SHA-256 hace la
   reanudación segura: si el archivo ya existe con el hash esperado, no se reescribe).
4. **Registrar el `early_eval`** cuando C complete la evaluación temprana (E9).
5. **Actualizar `last_updated`** en cada escritura con timestamp ISO 8601 real.
6. **Verificar la escritura** releyendo el archivo. Si el campo esperado no quedó, retornar
   `CHECKPOINT_FAILED`.

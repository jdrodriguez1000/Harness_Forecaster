# Ciclo 010 — Discovery

**Propósito:** Capturar el contexto del cliente, calcular el ITO, confirmar la categoría M/L/XL y
generar la configuración inicial del tenant (client_profile, onboarding_config, guía de datos).

**Agente responsable:** `discovery-governor`
**Duración típica:** 1–2 sesiones de trabajo con el operador Triple S.

---

## Cómo invocar

Todo el ciclo se conduce a través del agente `discovery-governor`. No ejecutar acciones técnicas
directamente. El governor retorna siempre un bloque `GOVERNOR_RESULT` — leerlo para determinar la
siguiente acción.

```powershell
$prompt = @"
[MODO: <MODO>]
<campos adicionales según modo>
"@
$result = $prompt | claude --agent discovery-governor --print --dangerously-skip-permissions
```

---

## Tabla de estados → modos → acciones

### INIT — al arrancar o reanudar

Invocar con `[MODO: INIT]`. Detecta si es inicio o continuación.

| GOVERNOR_RESULT status   | Acción                                                                                      |
|--------------------------|---------------------------------------------------------------------------------------------|
| `SPRINT_CONTRACT_READY`  | Presentar Sprint Contract al operador. Si aprueba → EXECUTE con `sprint_contract_approved: true` |
| `RESUME_AT_EXECUTE`      | Invocar EXECUTE directamente (Sprint Contract ya aprobado)                                  |
| `RESUME_AT_CP03`         | Presentar borradores al operador → invocar POST_CP03                                        |
| `RESUME_AT_CP04`         | Invocar POST_CP04 con `cp04_approved: true`                                                 |
| `SUSPEND_DETECTED`       | Mostrar `context_note` y `resume_instruction` al operador. Esperar instrucción              |
| `INIT_FAILED`            | Mostrar error al operador. No continuar                                                     |

### EXECUTE — ejecución de workers

Invocar con `[MODO: EXECUTE]` + `sprint_contract_approved: true` (o `interviewer_complete: true` en reanudación).

| GOVERNOR_RESULT status   | Acción                                                                                      |
|--------------------------|---------------------------------------------------------------------------------------------|
| `INTERVIEWER_REQUIRED`   | Invocar `discovery-interviewer` directamente en la sesión (es interactivo). Cuando termine, reinvocar EXECUTE con `interviewer_complete: true` |
| `ESCALATION_REQUIRED`    | Presentar `escalation_reason` al operador. Reinvocar según `next_action`                    |
| `EXECUTION_COMPLETE`     | Presentar borradores de `010_discovery/client_profile.json` y `onboarding_config.json` → invocar POST_CP03 |
| `EXECUTION_FAILED`       | Mostrar error al operador. Escalar si persiste                                              |

### POST_CP03 — revisión de borradores por el operador

Presentar artefactos al operador. Invocar con `[MODO: POST_CP03]` + `cp03_decision: approved|rework`.

| GOVERNOR_RESULT status   | Acción                                                                                      |
|--------------------------|---------------------------------------------------------------------------------------------|
| `CP04_READY`             | Invocar POST_CP04 con `cp04_approved: true`                                                 |
| `REWORK_COMPLETE`        | Presentar borradores actualizados al operador. Reinvocar POST_CP03                          |
| `STRATEGIC_REJECTION`    | Escalar al operador para redefinir alcance                                                  |

### POST_CP04 — COMMIT y auditoría

Invocar con `[MODO: POST_CP04]` + `cp04_approved: true`.

| GOVERNOR_RESULT status   | Acción                                                                                      |
|--------------------------|---------------------------------------------------------------------------------------------|
| `CLOSURE_READY`          | Invocar CLOSE (sin `handoff_decision`)                                                      |
| `AUDIT_FAILED`           | Mostrar error. Escalar                                                                      |
| `REWORK_AFTER_REJECTION` | Reinvocar POST_CP04 tras corrección automática                                              |

### CLOSE — cierre técnico y handoff

**Fase 1** — invocar con `[MODO: CLOSE]` sin `handoff_decision`.

| GOVERNOR_RESULT status      | Acción                                                                                   |
|-----------------------------|------------------------------------------------------------------------------------------|
| `CLOSE_READY`               | Preguntar al operador: "¿Continuar con el 015 Intake ahora?" → invocar CLOSE Fase 2     |
| `CLOSE_BLOCKED`             | Mostrar error. Ejecutar auditoría (POST_CP04) primero                                    |

**Fase 2** — invocar con `[MODO: CLOSE]` + `handoff_decision: yes|no`.

| GOVERNOR_RESULT status         | Acción                                                                                |
|--------------------------------|---------------------------------------------------------------------------------------|
| `HANDOFF_READY`                | Notificar: "Deploy del 015 completado. Reiniciar sesión y ejecutar /faro-restart"     |
| `PHASE_COMPLETE_NO_HANDOFF`    | Notificar: "Ciclo 010 completo. Cuando quieras continuar, ejecuta /faro-restart"      |

---

## Condición de completitud

```
600_persistence/harness-state.json["status"] == "PHASE_COMPLETE"
  Y  harness-state["handoff_015"] registrado
```

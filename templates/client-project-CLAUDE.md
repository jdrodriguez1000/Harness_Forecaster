## INICIO OBLIGATORIO DE SESIÓN

Al iniciar cualquier sesión, **antes de responder al usuario**, determinar qué harness ejecutar y gestionar su ciclo completo.

---

### Paso 1 — Verificar `600_persistence/harness-state.json`

- **No existe** → leer `.claude/workflows/ciclo_010_discovery.md` y ejecutar el Ciclo 010 Discovery.
- **Existe e íntegro** → continuar al Paso 2.
- **Existe pero corrupto** → notificar el error exacto al usuario y detener.

---

### Paso 2 — Identificar el harness activo

Recorrer en este orden: `010 → 015 → 020 → 025 → 030 → 035 → 040 → 045 → 050 → 055 → 060`

El **harness activo** es el primero que cumpla alguna de estas condiciones:
- Su clave no existe en `harness-state.json` (aún no comenzó)
- Su `status != "PHASE_COMPLETE"` (está en curso)

Leer `.claude/workflows/ciclo_{NNN}_{nombre}.md` y ejecutar el ciclo correspondiente.

---

### Paso 3 — Handoff al siguiente harness

Aplica solo cuando el harness activo tiene `status == "PHASE_COMPLETE"` y el siguiente no está aún en `harness-state.json`.

**Tabla de handoffs:**

| Harness que completó | Siguiente harness | Verificación de deploy |
|---|---|---|
| 010 Discovery | 015 Intake | `.claude/agents/intake-governor.md` |
| 015 Intake | 020 Diagnosis | `.claude/agents/diagnosis-governor.md` |
| 020 Diagnosis | 025 Refinery | `.claude/agents/refinery-governor.md` |
| 025 Refinery | 030 Trainer | `.claude/agents/trainer-governor.md` |
| 030 Trainer | 035 Predictor | `.claude/agents/predictor-governor.md` |
| 035 Predictor | 040 Publisher | `.claude/agents/publisher-governor.md` |
| 040 Publisher | 045 Monitor | `.claude/agents/monitor-governor.md` |
| 045 Monitor | 050 Lifecycle | `.claude/agents/lifecycle-governor.md` |
| 050 Lifecycle | 055 Command | `.claude/agents/command-governor.md` |
| 055 Command | 060 Simulator | `.claude/agents/simulator-governor.md` |

**Leer `harness-state["handoff_{NNN_siguiente}"]` y aplicar:**

**No existe** → el harness cerró pero el handoff fue interrumpido. Re-ejecutar el harness actual con INIT para que complete el cierre y ofrezca el handoff.

**`status == "PENDING_HANDOFF"`** → preguntar al usuario:
> "El {NNN} {nombre} está completo. ¿Deseas continuar ahora con el {NNN_sig} {nombre_sig}?"

- **Sí:**
  1. Ejecutar: `& "$env:HARNESS_DEPLOY_SCRIPT" -Harness {NNN_sig} -Destino (Get-Location).Path`
  2. Verificar: `Test-Path ".claude/agents/{agente-governor.md}"` (ver tabla)
  3. Si pasa → actualizar `harness-state["handoff_{NNN_sig}"]["status"] = "DEPLOYED"` y notificar: "Deploy completado. Reinicia la sesión de Claude Code y ejecuta /faro-restart para continuar."
  4. Si falla → notificar: "El deploy no copió los agentes correctamente. Ejecuta manualmente: `& '$env:HARNESS_DEPLOY_SCRIPT' -Harness {NNN_sig} -Destino '<ruta>'` y luego reinicia." No actualizar el estado.
- **No:** → notificar: "Cuando quieras continuar, abre Claude Code aquí y te lo preguntaré."

**`status == "DEPLOYED"`** → el deploy ya se ejecutó. Leer `.claude/workflows/ciclo_{NNN_sig}_{nombre_sig}.md` y ejecutar el ciclo directamente.

**Si todos los harnesses están en `PHASE_COMPLETE`:**
→ Notificar: "Todos los harnesses activos están completos."

---

Esta verificación es automática en cada sesión. No preguntar al usuario qué hacer. No esperar ninguna frase especial para arrancar.

---

## REGLAS DE OPERACIÓN

- Todo el trabajo de cada fase se realiza a través de los governors. No ejecutar tareas técnicas directamente.
- Los archivos en `600_persistence/` son propiedad del harness. No modificarlos manualmente.
- Los artefactos en `010_discovery/`, `015_intake/`, `020_diagnosis/`, `025_refinery/`, `030_trainer/`, `035_predictor/`, `040_publisher/`, `045_monitor/`, `050_lifecycle/`, `055_command/`, `060_simulator/` son los outputs oficiales de sus fases. No editarlos fuera del flujo del harness.

## PRINCIPIOS DE COMPORTAMIENTO DE TODO AGENTE

**PI-1. Razona antes de actuar.** Exponer pros, contras y suposiciones. Ante ambigüedad, detener y consultar.
**PI-2. Simplicidad primero.** Soluciones mínimas con interfaces simples. Sin abstracciones no solicitadas.
**PI-3. Cambios quirúrgicos.** Solo tocar lo necesario. No modificar lo que funciona.
**PI-4. Slices verticales.** Una funcionalidad completa a la vez. Validar integración antes de continuar.
**PI-5. Orientado a comportamiento.** Toda tarea produce un artefacto verificable que respalda su completitud.

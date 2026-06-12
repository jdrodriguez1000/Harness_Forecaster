Retoma el harness activo del proyecto actual tras un reinicio de sesión de Claude Code.

## Cuándo ejecutar

Cuando el usuario escribe `/faro-restart` después de reiniciar Claude Code en un directorio de proyecto FARO — ya sea tras el deploy de un nuevo harness o al retomar un harness en progreso.

## Pasos

### 1. Verificar directorio de proyecto

Leer `600_persistence/harness-state.json`.

- Si no existe: informar "No hay harness activo en este directorio. Verifica que estás en la carpeta correcta del proyecto." y detener.
- Si no es parseable: informar "600_persistence/harness-state.json está corrupto. Intervención manual requerida." y detener.

### 2. Determinar qué harness ejecutar

Evaluar el estado en este orden de prioridad:

**Prioridad 1a — Harness nuevo desplegado (post-transición):**

| Condición | Harness a iniciar |
|---|---|
| `handoff_015.status == "DEPLOYED"` Y `015_intake` no existe en el JSON | 015 Intake |
| `handoff_020.status == "DEPLOYED"` Y `020_diagnosis` no existe en el JSON | 020 Diagnosis |
| `handoff_025.status == "DEPLOYED"` Y `025_refinery` no existe en el JSON | 025 Refinery |
| `handoff_030.status == "DEPLOYED"` Y `030_trainer` no existe en el JSON | 030 Trainer |
| `handoff_035.status == "DEPLOYED"` Y `035_predictor` no existe en el JSON | 035 Predictor |
| `handoff_040.status == "DEPLOYED"` Y `040_publisher` no existe en el JSON | 040 Publisher |
| `handoff_045.status == "DEPLOYED"` Y `045_monitor` no existe en el JSON | 045 Monitor |
| `handoff_050.status == "DEPLOYED"` Y `050_lifecycle` no existe en el JSON | 050 Lifecycle |
| `handoff_055.status == "DEPLOYED"` Y `055_command` no existe en el JSON | 055 Command |
| `handoff_060.status == "DEPLOYED"` Y `060_simulator` no existe en el JSON | 060 Simulator |

**Prioridad 1b — Harness siguiente pendiente de deploy (PENDING_HANDOFF):**

Si ninguna condición de Prioridad 1a aplica, buscar el primer `handoff_0XX.status == "PENDING_HANDOFF"` en orden descendente (060 → 055 → ... → 015).

Si se encuentra un `PENDING_HANDOFF`:

1. Preguntar al usuario: "El harness anterior está completo pero el siguiente aún no fue desplegado. ¿Deseas desplegarlo ahora y continuar?"
2. Si sí:
   - Ejecutar: `& "$env:HARNESS_DEPLOY_SCRIPT" -Harness <NNN> -Destino (Get-Location).Path`
   - Verificar que el deploy tuvo éxito: `Test-Path ".claude/agents/<governor>.md"`
   - Si la verificación pasa:
     - Actualizar `handoff_0NNN.status = "DEPLOYED"` en `600_persistence/harness-state.json`
     - Notificar: "Deploy completado. Reinicia la sesión de Claude Code en este directorio y ejecuta /faro-restart para continuar."
     - Detener.
   - Si la verificación falla:
     - Notificar: "El agente <governor>.md no se copió correctamente. Estado NO actualizado. Ejecuta manualmente el deploy y luego /faro-restart."
     - Detener.
3. Si no: notificar "Cuando quieras continuar, ejecuta /faro-restart." y detener.

**Prioridad 2 — Harness activo en progreso:**

Buscar el primer harness con `status != "PHASE_COMPLETE"` en orden descendente:
`060_simulator` → `055_command` → `050_lifecycle` → `045_monitor` → `040_publisher` → `035_predictor` → `030_trainer` → `025_refinery` → `020_diagnosis` → `015_intake` → `010_discovery`

**Sin caso aplicable:**
- Todos en `PHASE_COMPLETE`: informar "Todos los harnesses activos están completos. No hay nada que reanudar." y detener.

### 3. Mapear harness a governor

| Harness | Governor |
|---|---|
| `010_discovery` | `discovery-governor` |
| `015_intake` | `intake-governor` |
| `020_diagnosis` | `diagnosis-governor` |
| `025_refinery` | `refinery-governor` |
| `030_trainer` | `trainer-governor` |
| `035_predictor` | `predictor-governor` |
| `040_publisher` | `publisher-governor` |
| `045_monitor` | `monitor-governor` |
| `050_lifecycle` | `lifecycle-governor` |
| `055_command` | `command-governor` |
| `060_simulator` | `simulator-governor` |

### 4. Verificar disponibilidad del governor

Verificar que `.claude/agents/<governor>.md` existe en el directorio de trabajo.

Si no existe: detener con mensaje exacto:
```
FARO: El agente <governor>.md no está disponible en .claude/agents/.
El deploy del harness <NNN> puede no haberse completado.
Ejecuta: & "$env:HARNESS_DEPLOY_SCRIPT" -Harness <NNN> -Destino "<ruta>" y luego /faro-restart.
```

### 5. Confirmar y conducir

Mostrar mensaje exacto:
```
FARO: Reanudando sesión.

  Harness : <harness detectado>
  Estado  : <"Iniciando nuevo harness" o "Continuando harness en progreso">
```

**Esta sesión actúa como CONDUCTOR.** El governor es un subagente y no puede spawnear otros
subagentes: decide el próximo paso y retorna `GOVERNOR_RESULT`. La sesión principal es la única
que spawnea (vía la herramienta `Agent`).

1. Si el harness es `010_discovery`: leer `.claude/workflows/conductor_loop.md` y seguir ese
   bucle. (Los harnesses 015–060 tendrán su propio bucle conductor cuando se construyan; por
   ahora solo el 010 está implementado.)
2. Spawnear el governor correspondiente (`subagent_type: <governor>`) con el prompt:
   ```
   MODO: INIT
   ```
3. Extraer el `GOVERNOR_RESULT` y entrar al bucle conductor. El governor ejecutará E10-A (inicio
   limpio para harness nuevo) o E10-B (continuación) según el estado en
   `600_persistence/harness-state.json`, y retornará un `SPRINT_CONTRACT_READY` o un `RESUME_AT_*`
   que el bucle maneja.

## Notas

- Si el harness está `SUSPENDED`: usar `/faro-continue` en su lugar.
- No invocar el governor antes de mostrar el mensaje de confirmación.

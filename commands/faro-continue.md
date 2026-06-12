Reanuda el harness suspendido del proyecto actual desde el punto exacto de interrupción.

## Cuándo ejecutar

Cuando el usuario escribe `/faro-continue` para retomar un harness previamente suspendido con `/faro-suspend`.

## Pasos

### 1. Obtener timestamp real

```powershell
(Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
```

### 2. Verificar que existe una suspensión activa

Leer `600_persistence/harness-state.json`.

- Si no existe o no es parseable: informar "No hay harness activo en este directorio. Verifica que estás en la carpeta correcta del proyecto." y detener.
- Buscar el harness con `status == "SUSPENDED"` en orden descendente: 060 → 055 → 050 → 045 → 040 → 035 → 030 → 025 → 020 → 015 → 010.
- Si ninguno tiene `status == "SUSPENDED"`: informar "No hay harness suspendido en este proyecto. Usa /faro-discovery para iniciar o /faro-restart para continuar normalmente." y detener.
- Si `suspension == null` pero `status == "SUSPENDED"`: informar "El harness está marcado como suspendido pero no tiene datos de reanudación. Usa /faro-restart." y detener.

Extraer del bloque `suspension`:
- `harness` → qué harness reanudar
- `governor_mode` → con qué modo invocar el governor
- `context_note` → resumen del contexto
- `resume_instruction` → instrucción precisa de reanudación

### 3. Registrar evento de reanudación en 600_persistence/claude-progress.txt

```powershell
Add-Content -Path "600_persistence/claude-progress.txt" -Value "[REANUDACIÓN] <timestamp> — Harness <harness> reanudado en modo <governor_mode>. Contexto: <context_note>" -Encoding utf8
```

Si el archivo no existe, crearlo primero.

### 4. Limpiar bloque de suspensión y restaurar status

Leer `600_persistence/harness-state.json` completo. Aplicar al harness activo:

- `suspension` → `null`
- `status` → restaurar según `governor_mode`:

| governor_mode | status a restaurar |
|---|---|
| `INIT` | `PENDING_CONTRACT` |
| `EXECUTE` | `ACTIVE` |
| `POST_CP03` | `ACTIVE` |
| `POST_CP04` | `ACTIVE` |
| `CLOSE` | `ACTIVE` |

**Regla crítica:** Escribir el archivo completo con TODOS los campos previos intactos.

### 5. Mapear harness a governor

| harness | governor |
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

### 6. Confirmar y conducir

Mostrar este mensaje exacto:

```
FARO: Reanudando harness suspendido.

  Harness     : <harness>
  Modo        : <governor_mode>
  Contexto    : <context_note>

Instrucción  : <resume_instruction>
```

**Esta sesión actúa como CONDUCTOR.** El governor es un subagente y no puede spawnear otros
subagentes: decide el próximo paso y retorna `GOVERNOR_RESULT`. La sesión principal es la única
que spawnea (vía la herramienta `Agent`).

1. Si el harness es `010_discovery`: leer `.claude/workflows/conductor_loop.md` y seguir ese bucle.
2. Spawnear el governor correspondiente (`subagent_type: <governor>`) con el prompt:
   ```
   MODO: <governor_mode>
   ```
3. Extraer el `GOVERNOR_RESULT` y entrar al bucle conductor, manejando cada `status` según la tabla
   del bucle (despachos automáticos de workers/orchestrator, gates del operador, reanudaciones y
   estados terminales). El governor reanuda desde el punto exacto re-derivando del disco.

## Notas

- El governor invocado, al reanudar en un modo de ejecución, opera como despachador de un solo
  paso: re-deriva su posición leyendo `600_persistence/harness-state.json`,
  `600_persistence/execution-state.json` y los artefactos en `010_discovery/`.
- El campo `suspension` limpiado en el Paso 4 garantiza que E10-B no retorne `SUSPEND_DETECTED`.

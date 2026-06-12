Suspende el harness activo de forma ordenada, persiste el estado de reanudación en 600_persistence/harness-state.json y confirma al usuario.

## Cuándo ejecutar

Cuando el usuario necesita interrumpir el trabajo en curso en un proyecto FARO. El comando persiste el estado exacto para que /faro-continue pueda retomar sin pérdida de contexto.

## Pasos

### 1. Obtener timestamp real

```powershell
(Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
```

### 2. Verificar que existe un harness activo

Leer `600_persistence/harness-state.json`.

- Si no existe o no es parseable: informar "No hay harness activo en este directorio. Verifica que estás en la carpeta correcta del proyecto." y detener.
- Si ya hay un harness en estado `"SUSPENDED"`: mostrar el contexto existente y preguntar si desea sobreescribir.

### 3. Identificar el harness activo

Recorrer en orden descendente para encontrar el harness más reciente que no está `PHASE_COMPLETE`:

**Prioridad (de más reciente a más antiguo):**
060_simulator → 055_command → 050_lifecycle → 045_monitor → 040_publisher → 035_predictor → 030_trainer → 025_refinery → 020_diagnosis → 015_intake → 010_discovery

Si ningún harness está activo: informar "Todos los harnesses del proyecto están completos. No hay estado que suspender." y detener.

### 4. Leer estado de ejecución

Leer `600_persistence/execution-state.json`.
Extraer: `last_checkpoint`, `status`.

Si no existe: asumir `last_checkpoint: null` y `status: "PENDING"`.

### 5. Inferir governor_mode y construir contexto

Usar la combinación de `status` del harness activo y `last_checkpoint`:

| harness.status | last_checkpoint | governor_mode | context_note | resume_instruction |
|---|---|---|---|---|
| `PENDING_CONTRACT` | — | `INIT` | Sprint Contract pendiente de aprobación del operador | Invocar governor con [MODO: INIT] para presentar Sprint Contract |
| `ACTIVE` | `null` | `EXECUTE` | Ejecución iniciada, primer worker no completado | Invocar governor con [MODO: EXECUTE] para continuar desde el inicio |
| `ACTIVE` | `CP-01` o `CP-02` | `EXECUTE` | Workers parciales completos | Invocar governor con [MODO: EXECUTE]; el orchestrator detectará el starting_point |
| `ACTIVE` | `CP-03` o posterior | `POST_CP03` | Workers completados, pendiente revisión del operador | Invocar governor con [MODO: POST_CP03] |
| `IN_REWORK` | — | `POST_CP03` | Rework en progreso tras rechazo | Invocar governor con [MODO: POST_CP03] para continuar rework |

Si la combinación no coincide: construir `context_note` descriptivo y `resume_instruction` genérica con [MODO: INIT].

**Override obligatorio — CP-03 ya aprobado:**
Si `operator_approvals` del harness activo contiene una aprobación de CP-03 → sobreescribir con `governor_mode: POST_CP04`.

### 6. Construir y escribir bloque de suspensión

Leer `600_persistence/harness-state.json` completo.

Construir bloque:
```json
"suspension": {
  "timestamp": "<timestamp del Paso 1>",
  "harness": "<phase_id del harness activo>",
  "governor_mode": "<governor_mode inferido>",
  "last_checkpoint": "<valor de execution-state.last_checkpoint, o null>",
  "context_note": "<context_note construido>",
  "resume_instruction": "<resume_instruction construida>"
}
```

Actualizar `status` del harness activo a `"SUSPENDED"` y agregar/reemplazar el campo `suspension`.

**Regla crítica:** Escribir el archivo completo con TODOS los campos previos intactos.

### 7. Registrar evento en 600_persistence/claude-progress.txt

```powershell
Add-Content -Path "600_persistence/claude-progress.txt" -Value "[SUSPENSIÓN] <timestamp> — Harness <phase_id> suspendido en modo <governor_mode>. Contexto: <context_note>" -Encoding utf8
```

Si el archivo no existe, crearlo primero.

### 8. Confirmar al usuario

```
FARO: Harness suspendido correctamente.

  Harness     : <phase_id>
  Checkpoint  : <last_checkpoint o "antes del primer checkpoint">
  Modo activo : <governor_mode>
  Contexto    : <context_note>

Para reanudar en la próxima sesión, escribe /faro-continue.
```

## Notas

- No invocar ningún governor ni agente — este comando opera directamente sobre los archivos de estado.
- El estado en los archivos de artefactos queda intacto; solo cambia `600_persistence/`.

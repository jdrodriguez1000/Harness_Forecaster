Registra una restricción vinculante del operador e inyecta un override en el harness activo de FARO.

## Cuándo ejecutar

Cuando el usuario escribe `/faro-override "texto"` para corregir una decisión del harness con una restricción propia que debe respetarse como fuente de verdad — típicamente durante la revisión del Sprint Contract o la revisión de artefactos draft en CP-03.

## Pasos

### 1. Extraer el texto del override

El texto es el argumento escrito después de `/faro-override`.

- Si no hay argumento o está vacío: informar 'Uso: /faro-override "descripción de la restricción"' y detener.

### 2. Obtener timestamp real

```powershell
(Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
```

### 3. Verificar harness activo

Leer `600_persistence/harness-state.json`.

- Si no existe: informar "No hay harness activo en este directorio." y detener.
- Identificar el harness activo en orden descendente: 060 → 055 → 050 → 045 → 040 → 035 → 030 → 025 → 020 → 015 → 010.
- Si todos están en `PHASE_COMPLETE`: informar "Todos los harnesses están completos. No hay nada que overridear." y detener.

Extraer: `phase_id` y `status` del harness activo.

### 4. Generar ID del override

Leer el campo `"overrides"` del harness activo.

- Si no existe o está vacío → ID: `OV-001`
- Si tiene N elementos → ID: `OV-<N+1 con padding de 3 dígitos>`

### 5. Registrar en 600_persistence/harness-state.json

Construir objeto override:
```json
{
  "id": "<ID generado>",
  "timestamp": "<timestamp>",
  "harness": "<phase_id>",
  "texto": "<texto del override>",
  "status": "ACTIVE"
}
```

Agregar al array `"overrides"` del harness activo. Actualizar `"last_updated"`.

**Regla crítica:** Escribir el archivo completo con TODOS los campos previos intactos.

### 6. Registrar en 600_persistence/overrides.md

Si no existe, crear con cabecera:
```markdown
# Overrides del Proyecto FARO

Restricciones vinculantes registradas por el operador Triple S durante la ejecución de los harnesses.
Los harnesses futuros leen este archivo en su inicialización (E10-A) para respetar estas restricciones.

---
```

Agregar al final:
```markdown
## <ID> — <timestamp>

**Harness:** <phase_id>
**Restricción:** <texto del override>
**Status:** ACTIVE

---
```

### 7. Registrar evento en 600_persistence/claude-progress.txt

```powershell
Add-Content -Path "600_persistence/claude-progress.txt" -Value "[OVERRIDE] <timestamp> — <ID> registrado en <phase_id>. Restricción: `"<texto>`"" -Encoding utf8
```

Si el archivo no existe, crearlo primero.

### 8. Confirmar y retornar resultado

Mostrar este mensaje exacto:

```
FARO: Override registrado.

  ID          : <ID>
  Harness     : <phase_id>
  Restricción : <texto del override>

Esta restricción es ahora vinculante para el harness activo y quedará disponible
para harnesses futuros en 600_persistence/overrides.md.
```

Retornar el siguiente bloque para que el ciclo activo lo lea:

```
FARO_OVERRIDE_RESULT:
  id: <ID>
  texto: <texto del override>
  constraint_str: "[OVERRIDE VINCULANTE — <ID>] <texto del override>"
```

## Comportamiento del ciclo tras el FARO_OVERRIDE_RESULT

**En revisión de Sprint Contract:**
→ Governor re-genera el Sprint Contract con la restricción como constraint duro.

**En revisión de artefactos draft (CP-03):**
→ Governor re-ejecuta el worker afectado. La restricción no es negociable.

## Notas

- No invocar ningún governor directamente — el ciclo activo lee el `FARO_OVERRIDE_RESULT`.
- Múltiples overrides son acumulativos: el ciclo concatena todos los `constraint_str` ACTIVE.
- Los overrides registrados en `600_persistence/overrides.md` son leídos por todos los governors futuros en su E10-A.

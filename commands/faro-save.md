Fuerza un guardado inmediato del estado parcial de la entrevista en curso. Escribe en
`010_discovery/support/session_notes.json` todo lo capturado hasta este momento como una entrada
con `estado: "parcial"`, protegiendo el trabajo ante una interrupción inesperada.

## Cuándo ejecutar

Durante una sesión activa del `discovery-interviewer`, cuando el operador quiere asegurarse
de que el progreso de la entrevista queda persistido antes de una pausa forzada, un cierre
de sesión o cualquier otra interrupción no planificada.

No sustituye el guardado incremental automático por bloque — es una medida de emergencia
para guardar lo capturado a mitad de un bloque temático.

## Pasos

### 1. Verificar contexto activo

Verificar que hay una sesión de entrevista en curso revisando `010_discovery/support/stakeholder_map.json`.

- Si el archivo no existe: informar "No hay un harness 010 Discovery activo en este
  directorio. Verifica que estás en la carpeta correcta del proyecto." y detener.
- Si existe pero todos los stakeholders están en `estado: "completada"`: informar "Todas
  las sesiones de entrevista ya están completadas. No hay nada pendiente que guardar."
  y detener.

### 2. Obtener timestamp real

```powershell
(Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
```

### 3. Identificar el stakeholder en curso

Leer `010_discovery/support/stakeholder_map.json` y buscar el primer stakeholder con
`estado: "pendiente"` — ese es el que está siendo entrevistado ahora mismo.

Si no hay ningún stakeholder `"pendiente"`: el proceso está entre stakeholders (no en mitad
de una sesión). Informar "No hay una sesión en curso. El guardado incremental automático
ya protege el progreso entre bloques." y detener.

### 4. Reunir lo capturado hasta ahora

Revisar la conversación activa para extraer todo lo que se haya discutido sobre el
stakeholder en curso, incluyendo:

- Respuestas a preguntas de cualquier bloque (negocio, técnico, usuario)
- Notas de estado emocional observadas
- Nombres de nuevos contactos mencionados (aunque no se haya hecho el cierre snowball formal)
- Cualquier observación libre relevante

Incluir **solo lo que el stakeholder haya expresado explícitamente** — no inferir ni completar
campos que no fueron abordados. Los campos no capturados se omiten o quedan como
`"MISSING — sesión parcial"`.

### 5. Leer session_notes.json

Intentar leer `010_discovery/support/session_notes.json`.

- Si no existe → crearlo con array vacío.
- Si existe → cargarlo. Buscar si ya existe una entrada para este `stakeholder_id`.

### 6. Escribir la entrada parcial

**Si no existe entrada previa** para este stakeholder → agregar nueva entrada.

**Si ya existe una entrada** (guardado incremental previo) → actualizar: sobrescribir los
bloques capturados hasta ahora y actualizar `fecha_ultima_actualizacion` y `bloques_guardados`.

En ambos casos, marcar con:

```json
{
  "estado": "parcial",
  "guardado_por": "faro-save",
  "fecha_ultima_actualizacion": "<timestamp del Paso 2>"
}
```

Escribir el archivo completo con el array actualizado.

### 7. Confirmar al operador

```
FARO: Guardado parcial completado.

  Stakeholder : [Nombre] — [Cargo]
  Bloques     : [lista de bloques con información capturada]
  Archivo     : 010_discovery/support/session_notes.json
  Timestamp   : [timestamp]

La entrevista puede continuar o reanudar desde aquí.
Para retomar, el interviewer leerá este estado al iniciar.
```

## Notas

- Este comando opera directamente sobre `session_notes.json` — no invoca ningún agente.
- El campo `estado: "parcial"` distingue este guardado del guardado incremental automático
  (`estado: "en_curso"`) y del guardado de cierre (`estado: "completada"`).
- El interviewer, al reanudar, detecta entradas con `estado: "parcial"` o `"en_curso"` y
  las retoma desde donde quedaron sin repetir preguntas ya respondidas.

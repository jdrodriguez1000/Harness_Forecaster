---
name: discovery-session-schema
description: Schema y reglas de escritura de session_data.json — derivado por
  discovery-synthesizer desde session_notes.json y synthesis_report.json. Define los
  campos obligatorios, opcionales y condicionales, cómo marcar campos faltantes con
  MISSING, y las reglas de validación de consistencia. Usar cuando discovery-synthesizer
  deriva 010_discovery/session_data.json para que el analyst lo consuma.
user-invocable: false
---

## Archivo — 010_discovery/session_data.json

**Path:** `010_discovery/session_data.json`
**Escritor único:** discovery-synthesizer (derivado desde session_notes.json + synthesis_report.json).
**Lectores:** discovery-analyst (lee para calcular ITO y cold start).

> **Nota arquitectónica:** Este archivo ya no es producido directamente por el interviewer.
> El interviewer produce `session_notes.json` (notas brutas por stakeholder) y
> `stakeholder_map.json`. El synthesizer consolida esas notas, resuelve contradicciones
> y deriva este archivo para mantener la interfaz del analyst sin cambios.

---

## Schema completo

```json
{
  "razon_social": "",
  "sector": "",
  "contacto_principal": {
    "nombre": "",
    "correo": "",
    "telefono": ""
  },
  "responsable_pagos": {
    "nombre": "",
    "correo": ""
  },
  "skus_activos": null,
  "clientes_xyz": null,
  "pedidos_por_mes": null,
  "anios_historial": null,
  "modo_ingesta": "",
  "frecuencia_incremental": null,
  "horizonte_pronostico": "",
  "jerarquia_producto": [],
  "jerarquia_geografica": [],
  "tiene_esquema2": null,
  "minimos_contractuales": null,
  "plan_suscripcion": "",
  "criterios_exito": [],
  "campos_missing": [],
  "inconsistencias_detectadas": [],
  "timestamp_sesion": ""
}
```

---

## Clasificación de campos

### Obligatorios — bloquean el flujo si están ausentes

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `razon_social` | string | Nombre legal de la empresa ABC |
| `sector` | string | Industria del cliente (alimentos, químicos, textil, etc.) |
| `contacto_principal.nombre` | string | Nombre del planificador de demanda |
| `contacto_principal.correo` | string | Correo del contacto principal |
| `contacto_principal.telefono` | string | Teléfono del contacto principal |
| `responsable_pagos.nombre` | string | Nombre del responsable de pagos |
| `responsable_pagos.correo` | string | Correo del responsable de pagos |
| `skus_activos` | integer | Cantidad aproximada de SKUs activos |
| `clientes_xyz` | integer | Cantidad aproximada de clientes XYZ atendidos |
| `pedidos_por_mes` | integer | Volumen aproximado de pedidos por mes |
| `anios_historial` | float | Años de historial de pedidos disponible |
| `modo_ingesta` | string | `"Batch"` o `"Incremental"` |
| `horizonte_pronostico` | string | `"días"`, `"semanas"`, `"meses"` o `"múltiples meses"` |
| `jerarquia_producto` | array | Niveles disponibles (ej: `["Categoría", "Subcategoría", "SKU"]`) |
| `jerarquia_geografica` | array | Niveles disponibles (ej: `["País", "Ciudad", "Sede"]`) |
| `tiene_esquema2` | boolean | Si tiene datos de producción e inventario |
| `plan_suscripcion` | string | `"Mensual"`, `"Trimestral"` o `"Anual"` |
| `criterios_exito` | array | Al menos uno de: `"reducir sobre-inventario"`, `"reducir quiebres"` |

### Condicionales — obligatorios solo si aplica

| Campo | Condición | Tipo |
|-------|-----------|------|
| `frecuencia_incremental` | Obligatorio si `modo_ingesta == "Incremental"` | string: `"Diaria"` o `"Semanal"` |

### Opcionales — se capturan si el cliente los tiene

| Campo | Tipo |
|-------|------|
| `minimos_contractuales` | string o null — si existen mínimos contractuales con clientes XYZ |

---

## Regla de campos MISSING

Si un campo obligatorio no puede obtenerse durante la sesión, registrarlo así:

```json
"campos_missing": [
  {
    "campo": "responsable_pagos.correo",
    "razon": "El cliente no tiene definido el responsable de pagos aún",
    "bloqueante": true
  }
]
```

**Campos bloqueantes** — impiden continuar al analyst:
- Cualquiera de los campos ITO: `skus_activos`, `clientes_xyz`, `pedidos_por_mes`
- `anios_historial`
- `modo_ingesta`

**Campos no bloqueantes** — el flujo continúa pero quedan pendientes:
- `responsable_pagos` (se puede agregar después)
- `frecuencia_incremental` si modo es Batch
- `minimos_contractuales`

---

## Reglas de consistencia entre campos

Al completar la sesión, verificar estas consistencias antes de escribir el archivo:

| Regla | Condición | Inconsistencia a registrar |
|-------|-----------|---------------------------|
| C-01 | `modo_ingesta == "Incremental"` y `frecuencia_incremental` es null | "Modo Incremental sin frecuencia definida" |
| C-02 | `anios_historial < 0.25` | "Historial menor a 3 meses — cold start inviable" |
| C-03 | `skus_activos <= 0` o `clientes_xyz <= 0` | "Valores ITO inválidos — deben ser > 0" |
| C-04 | `criterios_exito` es array vacío | "Sin criterios de éxito definidos" |
| C-05 | `jerarquia_producto` es array vacío | "Sin jerarquía de producto — no se puede construir pronóstico agregado" |

Registrar en `inconsistencias_detectadas`:
```json
"inconsistencias_detectadas": [
  {
    "codigo": "C-01",
    "descripcion": "Modo Incremental sin frecuencia definida",
    "campos_afectados": ["modo_ingesta", "frecuencia_incremental"],
    "bloqueante": false
  }
]
```

---

## Valores válidos por campo

| Campo | Valores permitidos |
|-------|-------------------|
| `modo_ingesta` | `"Batch"` \| `"Incremental"` |
| `frecuencia_incremental` | `"Diaria"` \| `"Semanal"` \| `null` |
| `horizonte_pronostico` | `"días"` \| `"semanas"` \| `"meses"` \| `"múltiples meses"` |
| `plan_suscripcion` | `"Mensual"` \| `"Trimestral"` \| `"Anual"` |
| `tiene_esquema2` | `true` \| `false` |
| `criterios_exito` | array con uno o más de: `"reducir sobre-inventario"` \| `"reducir quiebres"` |

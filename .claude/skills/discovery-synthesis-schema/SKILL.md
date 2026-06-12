---
name: discovery-synthesis-schema
description: Schema y reglas de escritura de synthesis_report.json — el artefacto de
  salida del worker discovery-synthesizer. Define la estructura del reporte de síntesis
  con campos consolidados de todas las entrevistas, contradicciones detectadas entre
  stakeholders, decisión de segunda ronda y los campos que alimentan session_data.json.
  Usar cuando discovery-synthesizer escribe 010_discovery/support/synthesis_report.json.
user-invocable: false
---

## Archivo — 010_discovery/support/synthesis_report.json

**Path:** `010_discovery/support/synthesis_report.json`
**Escritor único:** discovery-synthesizer.
**Lectores:** discovery-governor (para decidir si hay segunda ronda), discovery-analyst
(para leer los campos consolidados que antes estaban en session_data.json),
discovery-evaluator (para auditar cobertura y coherencia de la síntesis).

---

## Schema completo

> **`tenant_id`**: el synthesizer lo **lee** de `600_persistence/harness-state.json` (fuente única de verdad, DEC-047) y lo copia sin modificar. Es el slug generado por el governor (p. ej. `flexempaque-del-bajio-s-a-de-c-v-0949`), **nunca** la razón social. El mismo valor debe aparecer idéntico en `open_questions.json` y `session_data.json`.

```json
{
  "tenant_id": "",
  "timestamp_sintesis": "",
  "sesiones_analizadas": 0,
  "stakeholders_analizados": [
    {
      "id": "",
      "nombre": "",
      "roles": [],
      "estado": "completada | parcial"
    }
  ],
  "cobertura_roles": {
    "negocio": "cubierta | ausente",
    "tecnico": "cubierta | ausente",
    "usuario": "cubierta | ausente"
  },
  "campos_consolidados": {
    "razon_social": { "valor": null, "fuente_id": null, "confianza": null, "nota": null },
    "sector": { "valor": null, "fuente_id": null, "confianza": null, "nota": null },
    "skus_activos": { "valor": null, "fuente_id": null, "confianza": null, "nota": null },
    "clientes_xyz": { "valor": null, "fuente_id": null, "confianza": null, "nota": null },
    "pedidos_por_mes": { "valor": null, "fuente_id": null, "confianza": null, "nota": null },
    "anios_historial": { "valor": null, "fuente_id": null, "confianza": null, "nota": null },
    "modo_ingesta": { "valor": null, "fuente_id": null, "confianza": null, "nota": null },
    "frecuencia_incremental": { "valor": null, "fuente_id": null, "confianza": null, "nota": null },
    "horizonte_pronostico": { "valor": null, "fuente_id": null, "confianza": null, "nota": null },
    "jerarquia_producto": { "valor": null, "fuente_id": null, "confianza": null, "nota": null },
    "jerarquia_geografica": { "valor": null, "fuente_id": null, "confianza": null, "nota": null },
    "esquema2_disponible": { "valor": null, "fuente_id": null, "confianza": null, "nota": null },
    "minimos_contractuales": { "valor": null, "fuente_id": null, "confianza": null, "nota": null },
    "plan_suscripcion": { "valor": null, "fuente_id": null, "confianza": null, "nota": null },
    "criterios_exito": { "valor": null, "fuente_id": null, "confianza": null, "nota": null },
    "contacto_principal": { "valor": null, "fuente_id": null, "confianza": null, "nota": null },
    "responsable_pagos": { "valor": null, "fuente_id": null, "confianza": null, "nota": null }
  },
  "contradicciones": [],
  "contexto_cualitativo": {
    "urgencia_general": "alta | media | baja | mixta",
    "estado_emocional_predominante": "",
    "senales_de_riesgo": [],
    "oportunidades_detectadas": []
  },
  "decision_segunda_ronda": "requerida | no_requerida",
  "segunda_ronda_detalle": {
    "stakeholders": [],
    "campos_objetivo": []
  },
  "warnings": []
}
```

---

## Descripción de campos

### Bloque `stakeholders_analizados`

Lista de todos los stakeholders cuyas notas fueron procesadas. Un stakeholder con
`estado: "parcial"` significa que la sesión fue iniciada pero incompleta según el
`stakeholder_map.json`.

### Bloque `cobertura_roles`

| Valor | Significado |
|-------|-------------|
| `"cubierta"` | Al menos un stakeholder con ese rol tiene sesión completada |
| `"ausente"` | Ningún stakeholder cubrió ese rol — puede ser un gap bloqueante |

### Bloque `campos_consolidados`

Cada campo tiene cuatro subatributos:

| Subatributo | Tipo | Descripción |
|-------------|------|-------------|
| `valor` | any | El valor consolidado. Puede ser string, número, array, o `"MISSING"` |
| `fuente_id` | string \| null | ID del stakeholder de quien proviene el valor (ej: `"S001"`) |
| `confianza` | string \| null | `"alta"`, `"media"`, `"baja"` o null si valor es MISSING |
| `nota` | string \| null | Contexto relevante: si es estimado, si hubo contradicción resuelta, etc. |

**Reglas de consolidación cuando hay múltiples fuentes:**
- Si todos los stakeholders que mencionaron el campo dieron el mismo valor → `confianza: "alta"`
- Si los valores son consistentes pero con rangos (ej: "entre 100 y 150 SKUs") → usar punto medio, `confianza: "media"`, `nota: "rango estimado"`
- Si hay contradicción sin resolver → `valor: "MISSING"`, `nota: "contradicción sin resolver — ver contradicciones[id]"`
- Si ningún stakeholder mencionó el campo → `valor: "MISSING"`, `fuente_id: null`

**Valores de `jerarquia_producto` y `jerarquia_geografica`:**
Arrays de strings con los niveles disponibles declarados por el stakeholder técnico.
Ejemplos: `["sku", "subcategoria", "categoria"]`, `["sede", "ciudad"]`, `["no_aplica"]`

**Valores de `criterios_exito`:**
Array de strings. Valores posibles: `"reducir_sobre_inventario"`, `"reducir_quiebres"`,
`"ambos"`. Si no se capturó: `"MISSING"`.

**Valores de `contacto_principal` y `responsable_pagos`:**
Objetos con `nombre`, `correo`, `telefono`. Si no se capturó: `"MISSING"`.

### Bloque `contradicciones`

Array de objetos, uno por cada contradicción detectada entre stakeholders:

```json
{
  "id": "C001",
  "campo": "<nombre del campo en campos_consolidados>",
  "descripcion": "<qué dijo cada stakeholder>",
  "stakeholder_a": {
    "id": "S001",
    "nombre": "...",
    "valor_declarado": "<en sus palabras>"
  },
  "stakeholder_b": {
    "id": "S002",
    "nombre": "...",
    "valor_declarado": "<en sus palabras>"
  },
  "impacto": "bloqueante | importante | registrable",
  "resolucion": "pendiente | resuelta",
  "valor_resuelto": null,
  "accion": "<qué debe hacer el governor o el operador para resolver esto>"
}
```

**Impacto de contradicción:**
- `"bloqueante"` — los dos valores son incompatibles y afectan un campo sin el que el analyst no puede operar (ej: campo ITO, años de historial)
- `"importante"` — la contradicción afecta la calidad del pronóstico pero no impide continuar
- `"registrable"` — contexto cualitativo divergente sin impacto directo en campos estructurados

### Bloque `contexto_cualitativo`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `urgencia_general` | string | Percepción consolidada de urgencia del cliente |
| `estado_emocional_predominante` | string | Descripción libre del tono general de las sesiones |
| `senales_de_riesgo` | array | Señales que el synthesizer identificó como riesgos de adopción o de proyecto |
| `oportunidades_detectadas` | array | Contexto positivo que puede usarse para fortalecer la relación o el SLA |

### Bloque `decision_segunda_ronda`

| Valor | Condición para asignarlo |
|-------|--------------------------|
| `"requerida"` | Hay al menos una pregunta de categoría `bloqueante` en `open_questions.json` |
| `"no_requerida"` | No hay preguntas bloqueantes — el analyst puede operar con los campos consolidados |

### Bloque `segunda_ronda_detalle`

Solo se completa si `decision_segunda_ronda == "requerida"`:

```json
{
  "stakeholders": [
    { "id": "S002", "nombre": "...", "razon": "<por qué este stakeholder>" }
  ],
  "campos_objetivo": ["pedidos_por_mes", "anios_historial"]
}
```

---

## Reglas de escritura

1. **Incluir todos los campos del schema** — nunca omitir bloques aunque sean null o vacíos.
2. **`campos_consolidados` siempre completo** — los 17 campos deben estar presentes, aunque
   muchos tengan `valor: "MISSING"`.
3. **`contradicciones` vacío es válido** — si no hay contradicciones, dejar array vacío `[]`.
4. **`decision_segunda_ronda` se determina leyendo `open_questions.json`** que el synthesizer
   produce en el mismo ciclo de trabajo. Si hay al menos 1 pregunta bloqueante → `"requerida"`.
5. **No fabricar valores** — si un campo no aparece en ninguna sesión, marcar como MISSING.
6. **`fuente_id` siempre referencia un ID válido** del bloque `stakeholders_analizados`.

---

## Ejemplo completo — síntesis con una contradicción importante

```json
{
  "tenant_id": "alimentos-prueba-001",
  "timestamp_sintesis": "2026-06-09T10:15:00Z",
  "sesiones_analizadas": 2,
  "stakeholders_analizados": [
    { "id": "S001", "nombre": "María López", "roles": ["negocio"], "estado": "completada" },
    { "id": "S002", "nombre": "Carlos Ruiz", "roles": ["tecnico", "usuario"], "estado": "completada" }
  ],
  "cobertura_roles": {
    "negocio": "cubierta",
    "tecnico": "cubierta",
    "usuario": "cubierta"
  },
  "campos_consolidados": {
    "razon_social": { "valor": "Alimentos Prueba S.A.", "fuente_id": "S001", "confianza": "alta", "nota": null },
    "sector": { "valor": "alimentos y bebidas", "fuente_id": "S001", "confianza": "alta", "nota": null },
    "skus_activos": { "valor": 120, "fuente_id": "S001", "confianza": "media", "nota": "estimado del stakeholder de negocio" },
    "clientes_xyz": { "valor": 18, "fuente_id": "S001", "confianza": "media", "nota": "estimado" },
    "pedidos_por_mes": { "valor": 380, "fuente_id": "S001", "confianza": "media", "nota": "estimado" },
    "anios_historial": { "valor": "MISSING", "fuente_id": null, "confianza": null, "nota": "contradicción sin resolver — ver C001" },
    "modo_ingesta": { "valor": "incremental", "fuente_id": "S002", "confianza": "alta", "nota": null },
    "frecuencia_incremental": { "valor": "semanal", "fuente_id": "S002", "confianza": "alta", "nota": null },
    "horizonte_pronostico": { "valor": "meses", "fuente_id": "S002", "confianza": "alta", "nota": null },
    "jerarquia_producto": { "valor": ["sku", "subcategoria", "categoria"], "fuente_id": "S002", "confianza": "alta", "nota": null },
    "jerarquia_geografica": { "valor": ["no_aplica"], "fuente_id": "S002", "confianza": "alta", "nota": "operación en una sola sede" },
    "esquema2_disponible": { "valor": "no", "fuente_id": "S002", "confianza": "alta", "nota": null },
    "minimos_contractuales": { "valor": "no aplica", "fuente_id": "S001", "confianza": "alta", "nota": null },
    "plan_suscripcion": { "valor": "trimestral", "fuente_id": "S001", "confianza": "alta", "nota": null },
    "criterios_exito": { "valor": ["reducir_quiebres"], "fuente_id": "S001", "confianza": "alta", "nota": null },
    "contacto_principal": { "valor": { "nombre": "Carlos Ruiz", "correo": "cruiz@alimentos.com", "telefono": "+57 300 000 0001" }, "fuente_id": "S002", "confianza": "alta", "nota": null },
    "responsable_pagos": { "valor": { "nombre": "Ana García", "correo": "pagos@alimentos.com", "telefono": null }, "fuente_id": "S001", "confianza": "alta", "nota": null }
  },
  "contradicciones": [
    {
      "id": "C001",
      "campo": "anios_historial",
      "descripcion": "El stakeholder de negocio dice que tienen 3 años de datos. El técnico dice que el ERP actual lleva solo 8 meses y el sistema anterior nunca se migró.",
      "stakeholder_a": { "id": "S001", "nombre": "María López", "valor_declarado": "3 años" },
      "stakeholder_b": { "id": "S002", "nombre": "Carlos Ruiz", "valor_declarado": "8 meses en el ERP actual, sin migración del sistema anterior" },
      "impacto": "importante",
      "resolucion": "pendiente",
      "valor_resuelto": null,
      "accion": "Preguntar al técnico si existe forma de exportar datos del sistema anterior, o confirmar que el historial real disponible es 8 meses"
    }
  ],
  "contexto_cualitativo": {
    "urgencia_general": "media",
    "estado_emocional_predominante": "Receptivos pero cautelosos. El técnico tiene dudas sobre la calidad de los datos.",
    "senales_de_riesgo": [
      "El técnico mencionó que los datos tienen muchos registros duplicados — el ISD inicial puede ser bajo",
      "No hay respaldo del sistema anterior — el historial real puede ser 8 meses"
    ],
    "oportunidades_detectadas": [
      "El stakeholder de negocio tiene un caso concreto de pérdida de cliente por quiebre de stock — excelente anclaje para demostrar valor"
    ]
  },
  "decision_segunda_ronda": "requerida",
  "segunda_ronda_detalle": {
    "stakeholders": [
      { "id": "S002", "nombre": "Carlos Ruiz", "razon": "Confirmar si el historial del sistema anterior es recuperable" }
    ],
    "campos_objetivo": ["anios_historial"]
  },
  "warnings": [
    "La contradicción C001 (años de historial) es importante — impacta el nivel cold start y las expectativas de MAPE"
  ]
}
```

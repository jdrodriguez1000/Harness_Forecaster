---
name: discovery-open-questions
description: Schema y reglas de escritura de open_questions.json — el artefacto de
  preguntas pendientes producido por discovery-synthesizer. Clasifica los vacíos y
  contradicciones en tres niveles de impacto (bloqueante, importante, registrable),
  especifica qué stakeholder debe responder cada pregunta y qué campo afecta. El
  governor lee este archivo para decidir si se requiere una segunda ronda de entrevistas.
  Usar cuando discovery-synthesizer escribe 010_discovery/support/open_questions.json.
user-invocable: false
---

## Archivo — 010_discovery/support/open_questions.json

**Path:** `010_discovery/support/open_questions.json`
**Escritor único:** discovery-synthesizer.
**Lectores:** discovery-governor (para decidir si lanza segunda ronda o continúa hacia el
analyst), discovery-interviewer en modo COMPLEMENTARIO (para saber qué preguntar en la
segunda ronda), discovery-evaluator (para auditar que las preguntas bloqueantes fueron
resueltas antes del cierre).

---

## Schema completo

```json
{
  "tenant_id": "",
  "timestamp_generacion": "",
  "ciclo": 1,
  "resumen": {
    "total": 0,
    "bloqueantes": 0,
    "importantes": 0,
    "registrables": 0
  },
  "preguntas": []
}
```

### Estructura de cada pregunta

```json
{
  "id": "OQ-001",
  "ciclo_detectado": 1,
  "categoria": "bloqueante | importante | registrable",
  "tipo": "campo_faltante | contradiccion | aclaracion",
  "campo_afectado": "",
  "descripcion": "",
  "stakeholder_sugerido": {
    "id": "",
    "nombre": "",
    "rol": ""
  },
  "pregunta_segunda_ronda": "",
  "impacto_si_no_se_resuelve": "",
  "estado": "pendiente | resuelta",
  "resolucion": null
}
```

---

## Descripción de campos

### Bloque raíz

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `tenant_id` | string | Identificador (slug) del cliente. El synthesizer lo **lee** de `600_persistence/harness-state.json` (fuente única, DEC-047) y lo copia sin modificar — **nunca** la razón social. Debe ser idéntico al de `synthesis_report.json` y `session_data.json` |
| `timestamp_generacion` | string | Timestamp ISO 8601 de cuándo se generó este archivo |
| `ciclo` | integer | Número de ciclo del synthesizer. Empieza en 1, incrementa en cada segunda ronda |
| `resumen.total` | integer | Conteo total de preguntas en el array `preguntas` |
| `resumen.bloqueantes` | integer | Cuántas preguntas tienen `categoria: "bloqueante"` |
| `resumen.importantes` | integer | Cuántas preguntas tienen `categoria: "importante"` |
| `resumen.registrables` | integer | Cuántas preguntas tienen `categoria: "registrable"` |

### Campos de cada pregunta

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | string | Identificador correlativo: `"OQ-001"`, `"OQ-002"`, etc. |
| `ciclo_detectado` | integer | En qué ciclo del synthesizer se detectó esta pregunta |
| `categoria` | string | Nivel de impacto — ver tabla abajo |
| `tipo` | string | Naturaleza del problema — ver tabla abajo |
| `campo_afectado` | string | Nombre del campo en `campos_consolidados` de `synthesis_report.json` |
| `descripcion` | string | Descripción clara del vacío o contradicción en lenguaje de negocio |
| `stakeholder_sugerido.id` | string | ID del stakeholder más adecuado para responder |
| `stakeholder_sugerido.nombre` | string | Nombre del stakeholder |
| `stakeholder_sugerido.rol` | string | Rol FARO del stakeholder: `"negocio"`, `"tecnico"` o `"usuario"` |
| `pregunta_segunda_ronda` | string | La pregunta exacta que el interviewer debe hacer en la segunda ronda |
| `impacto_si_no_se_resuelve` | string | Qué pasa si esta pregunta queda sin respuesta al cierre |
| `estado` | string | `"pendiente"` al crearse; `"resuelta"` cuando la segunda ronda la cierra |
| `resolucion` | string \| null | Cómo se resolvió; null mientras `estado == "pendiente"` |

---

## Categorías de pregunta

| Categoría | Criterio | Efecto en el flujo |
|-----------|----------|-------------------|
| `"bloqueante"` | Sin esta respuesta el analyst no puede calcular ITO, cold start o categoría. Afecta campos: `skus_activos`, `clientes_xyz`, `pedidos_por_mes`, `anios_historial`, `modo_ingesta`, `criterios_exito`, `plan_suscripcion`, `contacto_principal` | El governor NO avanza al analyst — lanza segunda ronda obligatoria |
| `"importante"` | Afecta la calidad del pronóstico pero no impide configurar. Afecta campos: `horizonte_pronostico`, `jerarquia_producto`, `jerarquia_geografica`, `esquema2_disponible`, `frecuencia_incremental` (si modo Incremental), contradicciones de historial | El governor puede avanzar al analyst con advertencia; segunda ronda recomendada |
| `"registrable"` | Contexto cualitativo útil pero no crítico. Incluye señales de riesgo no resueltas, oportunidades de venta, preferencias del usuario, mínimos contractuales | No bloquea ni advierte — se registra para el configurator y la guía de datos |

---

## Tipos de pregunta

| Tipo | Cuándo usarlo |
|------|--------------|
| `"campo_faltante"` | Ningún stakeholder respondió este campo — falta información |
| `"contradiccion"` | Dos o más stakeholders dieron valores incompatibles para el mismo campo |
| `"aclaracion"` | Un stakeholder respondió pero la respuesta es demasiado vaga para ser útil |

---

## Reglas de escritura

1. **Una pregunta por campo bloqueante faltante** — si `skus_activos` y `clientes_xyz`
   están ambos como MISSING, son dos preguntas separadas (OQ-001 y OQ-002).
2. **Una pregunta por contradicción de impacto bloqueante o importante** — mapear al
   `id` de la contradicción en `synthesis_report.json` (ej: contradicción C001 → pregunta OQ-003).
3. **Las preguntas registrables son opcionales** — incluirlas si aportan contexto relevante
   para el configurator o la guía de datos; omitirlas si no hay nada concreto que preguntar.
4. **`pregunta_segunda_ronda` debe ser formulada en lenguaje de negocio** — el interviewer
   la usará directamente en la conversación sin reescribirla.
5. **`resumen` siempre consistente** — `total` debe ser igual a la suma de los tres conteos.
6. **Al ejecutar segunda ronda**, el synthesizer reescribe el archivo completo actualizando:
   - `ciclo` incrementado en 1
   - `estado` de las preguntas resueltas a `"resuelta"` con su `resolucion`
   - Nuevas preguntas si la segunda ronda revela nuevos vacíos
   - `resumen` recalculado contando solo preguntas con `estado: "pendiente"`

---

## Ejemplo completo

```json
{
  "tenant_id": "alimentos-prueba-001",
  "timestamp_generacion": "2026-06-09T10:15:30Z",
  "ciclo": 1,
  "resumen": {
    "total": 4,
    "bloqueantes": 1,
    "importantes": 2,
    "registrables": 1
  },
  "preguntas": [
    {
      "id": "OQ-001",
      "ciclo_detectado": 1,
      "categoria": "bloqueante",
      "tipo": "campo_faltante",
      "campo_afectado": "pedidos_por_mes",
      "descripcion": "Ningún stakeholder proporcionó el volumen de pedidos mensual. Es necesario para calcular el ITO y clasificar al cliente.",
      "stakeholder_sugerido": {
        "id": "S001",
        "nombre": "María López",
        "rol": "negocio"
      },
      "pregunta_segunda_ronda": "¿Cuántos pedidos u órdenes de compra reciben de sus clientes al mes? Un estimado está bien.",
      "impacto_si_no_se_resuelve": "El analyst no puede calcular el ITO — la clasificación M/L/XL queda bloqueada.",
      "estado": "pendiente",
      "resolucion": null
    },
    {
      "id": "OQ-002",
      "ciclo_detectado": 1,
      "categoria": "importante",
      "tipo": "contradiccion",
      "campo_afectado": "anios_historial",
      "descripcion": "Contradicción C001: el stakeholder de negocio dice 3 años de historial; el técnico dice que el ERP lleva solo 8 meses y el sistema anterior no fue migrado.",
      "stakeholder_sugerido": {
        "id": "S002",
        "nombre": "Carlos Ruiz",
        "rol": "tecnico"
      },
      "pregunta_segunda_ronda": "¿Existe alguna forma de exportar el historial del sistema anterior, aunque sea en Excel? ¿O el historial disponible de forma práctica son estos 8 meses del ERP actual?",
      "impacto_si_no_se_resuelve": "El nivel cold start puede ser Experimental en vez de Estándar — impacta las expectativas de MAPE y el período antes del primer pronóstico.",
      "estado": "pendiente",
      "resolucion": null
    },
    {
      "id": "OQ-003",
      "ciclo_detectado": 1,
      "categoria": "importante",
      "tipo": "aclaracion",
      "campo_afectado": "horizonte_pronostico",
      "descripcion": "El stakeholder técnico dijo que necesitan el pronóstico 'para el siguiente período' pero no especificó si es semanas o meses. El modo de ingesta es semanal, lo que sugiere horizonte de semanas, pero necesita confirmación.",
      "stakeholder_sugerido": {
        "id": "S002",
        "nombre": "Carlos Ruiz",
        "rol": "usuario"
      },
      "pregunta_segunda_ronda": "Cuando dices que necesitas saber lo del 'siguiente período', ¿estás pensando en la próxima semana, el próximo mes, o varios meses adelante?",
      "impacto_si_no_se_resuelve": "El horizonte de pronóstico es un parámetro de configuración obligatorio — si se deja sin confirmar, el configurator usará el valor por defecto 'meses'.",
      "estado": "pendiente",
      "resolucion": null
    },
    {
      "id": "OQ-004",
      "ciclo_detectado": 1,
      "categoria": "registrable",
      "tipo": "campo_faltante",
      "campo_afectado": "minimos_contractuales",
      "descripcion": "No se exploró si los clientes de Alimentos Prueba tienen mínimos de compra contractuales. Es información útil para el análisis de demanda.",
      "stakeholder_sugerido": {
        "id": "S001",
        "nombre": "María López",
        "rol": "negocio"
      },
      "pregunta_segunda_ronda": "¿Sus clientes tienen cantidades mínimas de compra comprometidas en contrato? ¿Se cumplen habitualmente?",
      "impacto_si_no_se_resuelve": "No impacta la configuración — el sistema opera igual. Es contexto adicional para el pronóstico.",
      "estado": "pendiente",
      "resolucion": null
    }
  ]
}
```

## Ejemplo — después de segunda ronda (ciclo 2)

```json
{
  "tenant_id": "alimentos-prueba-001",
  "timestamp_generacion": "2026-06-09T11:45:00Z",
  "ciclo": 2,
  "resumen": {
    "total": 4,
    "bloqueantes": 0,
    "importantes": 0,
    "registrables": 1
  },
  "preguntas": [
    {
      "id": "OQ-001",
      "ciclo_detectado": 1,
      "categoria": "bloqueante",
      "tipo": "campo_faltante",
      "campo_afectado": "pedidos_por_mes",
      "descripcion": "Ningún stakeholder proporcionó el volumen de pedidos mensual.",
      "stakeholder_sugerido": { "id": "S001", "nombre": "María López", "rol": "negocio" },
      "pregunta_segunda_ronda": "¿Cuántos pedidos u órdenes de compra reciben de sus clientes al mes?",
      "impacto_si_no_se_resuelve": "El analyst no puede calcular el ITO.",
      "estado": "resuelta",
      "resolucion": "María confirmó: aproximadamente 400 pedidos por mes en temporada normal."
    },
    {
      "id": "OQ-002",
      "ciclo_detectado": 1,
      "categoria": "importante",
      "tipo": "contradiccion",
      "campo_afectado": "anios_historial",
      "descripcion": "Contradicción C001: negocio dice 3 años, técnico dice 8 meses en ERP actual.",
      "stakeholder_sugerido": { "id": "S002", "nombre": "Carlos Ruiz", "rol": "tecnico" },
      "pregunta_segunda_ronda": "¿Existe forma de exportar el historial del sistema anterior?",
      "impacto_si_no_se_resuelve": "Nivel cold start puede ser Experimental.",
      "estado": "resuelta",
      "resolucion": "Carlos confirmó que el sistema anterior (Excel) tiene registros de 2018 a 2025. Puede exportar aproximadamente 6 años de historial en CSV."
    },
    {
      "id": "OQ-003",
      "ciclo_detectado": 1,
      "categoria": "importante",
      "tipo": "aclaracion",
      "campo_afectado": "horizonte_pronostico",
      "descripcion": "Horizonte no especificado — semanas o meses.",
      "stakeholder_sugerido": { "id": "S002", "nombre": "Carlos Ruiz", "rol": "usuario" },
      "pregunta_segunda_ronda": "¿Siguiente período significa semanas o meses?",
      "impacto_si_no_se_resuelve": "Parámetro obligatorio de configuración.",
      "estado": "resuelta",
      "resolucion": "Carlos confirmó: necesitan el pronóstico para el próximo mes y los dos siguientes (3 meses de horizonte)."
    },
    {
      "id": "OQ-004",
      "ciclo_detectado": 1,
      "categoria": "registrable",
      "tipo": "campo_faltante",
      "campo_afectado": "minimos_contractuales",
      "descripcion": "No se exploró si los clientes tienen mínimos contractuales.",
      "stakeholder_sugerido": { "id": "S001", "nombre": "María López", "rol": "negocio" },
      "pregunta_segunda_ronda": "¿Sus clientes tienen cantidades mínimas comprometidas en contrato?",
      "impacto_si_no_se_resuelve": "No impacta la configuración.",
      "estado": "pendiente",
      "resolucion": null
    }
  ]
}
```

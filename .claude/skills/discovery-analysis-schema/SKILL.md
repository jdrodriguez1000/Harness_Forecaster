---
name: discovery-analysis-schema
description: Schema y reglas de escritura de analysis_report.json — el artefacto de salida
  del worker discovery-analyst. Define la estructura del reporte con ITO calculado,
  categoría confirmada, nivel de confianza cold start y flags de escalamiento. Usar cuando
  discovery-analyst escribe 010_discovery/analysis_report.json.
user-invocable: false
---

## Archivo — 010_discovery/analysis_report.json

**Path:** `010_discovery/analysis_report.json`
**Escritor único:** discovery-analyst.
**Lectores:** discovery-configurator (para generar artefactos finales), discovery-evaluator
(para auditar dimensiones D2 y D3 de la rúbrica).

---

## Schema completo

```json
{
  "tenant_id": "",
  "timestamp_analisis": "",
  "session_data_path": "",
  "ito": {
    "provisional": true,
    "valores_base": {
      "skus_activos": null,
      "clientes_xyz": null,
      "pedidos_por_mes": null
    },
    "normalizados": {
      "norm_skus": null,
      "norm_clientes": null,
      "norm_pedidos": null
    },
    "pesos": {
      "w1_skus": 0.40,
      "w2_clientes": 0.35,
      "w3_pedidos": 0.25
    },
    "referencias_max": {
      "skus_max": 500,
      "clientes_max": 100,
      "pedidos_max": 2000
    },
    "ito_calculado": null
  },
  "categoria": {
    "calculada": "",
    "comercial": "",
    "confirmada": "",
    "discrepancia": "",
    "discrepancia_critica": false,
    "nota_discrepancia": null
  },
  "cold_start": {
    "anios_historial": null,
    "nivel": "",
    "codigo": "",
    "inviable": false,
    "cascada_paso": null,
    "cascada_descripcion": null
  },
  "escalamiento": {
    "requerido": false,
    "razones": []
  },
  "warnings": []
}
```

---

## Descripción de campos

### Bloque `ito`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `provisional` | boolean | Siempre `true` hasta que T-030 calibre los valores definitivos |
| `valores_base.skus_activos` | integer | Valor directo de session_data.json |
| `valores_base.clientes_xyz` | integer | Valor directo de session_data.json |
| `valores_base.pedidos_por_mes` | integer | Valor directo de session_data.json |
| `normalizados.norm_skus` | float | `min(skus / 500, 1.0) × 100` — redondeado a 2 decimales |
| `normalizados.norm_clientes` | float | `min(clientes / 100, 1.0) × 100` — redondeado a 2 decimales |
| `normalizados.norm_pedidos` | float | `min(pedidos / 2000, 1.0) × 100` — redondeado a 2 decimales |
| `pesos.w1_skus` | float | 0.40 (provisional) |
| `pesos.w2_clientes` | float | 0.35 (provisional) |
| `pesos.w3_pedidos` | float | 0.25 (provisional) |
| `referencias_max.*` | integer | Máximos de referencia para normalización (provisionales) |
| `ito_calculado` | float | `w1×norm_skus + w2×norm_clientes + w3×norm_pedidos` — 2 decimales |

### Bloque `categoria`

| Campo | Tipo | Valores posibles | Descripción |
|-------|------|-----------------|-------------|
| `calculada` | string | `"M"`, `"L"`, `"XL"` | Resultado del ITO (ITO ≤ 33 → M, 33 < ITO ≤ 66 → L, ITO > 66 → XL) |
| `comercial` | string | `"M"`, `"L"`, `"XL"` | Asignada durante el proceso comercial |
| `confirmada` | string | `"M"`, `"L"`, `"XL"` | La que usará el sistema — ver regla abajo |
| `discrepancia` | string | `"ninguna"`, `"advertencia"`, `"critica"` | Diferencia entre calculada y comercial |
| `discrepancia_critica` | boolean | `true` si M↔XL (2 niveles de diferencia) |
| `nota_discrepancia` | string \| null | Explicación y acción recomendada — null si no hay discrepancia |

**Regla de `confirmada`:**
- Sin discrepancia o discrepancia de advertencia → `confirmada = calculada`
- Discrepancia crítica → `confirmada = comercial` (bloqueado hasta resolución del operador)

### Bloque `cold_start`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `anios_historial` | float | Valor directo de session_data.json |
| `nivel` | string | `"Alta"`, `"Estándar"`, `"Reducida"` o `"Experimental"` |
| `codigo` | string | `"CS-ALTA"`, `"CS-ESTANDAR"`, `"CS-REDUCIDA"` o `"CS-EXPERIMENTAL"` |
| `inviable` | boolean | `true` si `anios_historial < 0.25` — escalamiento obligatorio |
| `cascada_paso` | integer \| null | 1, 2 o 3 — solo si `codigo == "CS-EXPERIMENTAL"`, null en los demás casos |
| `cascada_descripcion` | string \| null | Descripción del paso activo — null si no es CS-EXPERIMENTAL |

**Tabla de clasificación cold start:**

| Historial | Nivel | Código |
|-----------|-------|--------|
| ≥ 3 años | Alta | CS-ALTA |
| 2–3 años | Estándar | CS-ESTANDAR |
| 1–2 años | Reducida | CS-REDUCIDA |
| < 1 año | Experimental | CS-EXPERIMENTAL |

**Texto de `cascada_descripcion` por paso:**
- Paso 1: `"Analogía por categoría de producto — usar patrones de sector como proxy (requiere datos de otros tenants, disponible en Fase 3)"`
- Paso 2: `"Analogía por cliente XYZ — usar pedidos del mismo cliente a otros ABC (requiere datos de otros tenants, disponible en Fase 3)"`
- Paso 3: `"Acumulación — esperar 3 meses de datos reales antes del primer pronóstico (fallback garantizado en Fase 1)"`

En Fase 1, registrar siempre `cascada_paso: 3`.

### Bloque `escalamiento`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `requerido` | boolean | `true` si hay discrepancia crítica o cold start inviable |
| `razones` | array de strings | Una entrada por cada razón de escalamiento |

**Valores de `razones`:**
- `"Discrepancia crítica de categoría: ITO calcula {calculada} pero se vendió como {comercial}"`
- `"Cold start inviable: historial de {N} meses es menor al mínimo de 3 meses"`

### Campo `warnings`

Array de strings para advertencias no bloqueantes:
- `"ITO provisional — pesos y umbrales pendientes de calibración (T-030)"`
- `"Discrepancia de categoría de 1 nivel: calculada={X}, comercial={Y} — governor decide si escalar"`
- `"Historial en rango Experimental ({N} años) — cascada cold start activa, paso 3 en Fase 1"`

---

## Reglas de escritura

1. **Incluir todos los campos del schema** — nunca omitir bloques aunque sean null.
2. **`provisional: true` es obligatorio** hasta que T-030 calibre los valores definitivos.
3. **`ito_calculado` con exactamente 2 decimales** — redondeo estándar, no truncar.
4. **`cascada_paso` y `cascada_descripcion`** — obligatorios si `codigo == "CS-EXPERIMENTAL"`, null en todos los demás casos.
5. **`nota_discrepancia`** — obligatorio si `discrepancia != "ninguna"`, null si no hay discrepancia.
6. **`warnings` siempre incluye** el aviso ITO provisional mientras T-030 no esté cerrada.

---

## Ejemplo completo — cliente M con historial estándar (sin discrepancia)

```json
{
  "tenant_id": "alimentos-prueba-001",
  "timestamp_analisis": "2026-06-08T14:32:07Z",
  "session_data_path": "010_discovery/session_data.json",
  "ito": {
    "provisional": true,
    "valores_base": {
      "skus_activos": 120,
      "clientes_xyz": 18,
      "pedidos_por_mes": 380
    },
    "normalizados": {
      "norm_skus": 24.00,
      "norm_clientes": 18.00,
      "norm_pedidos": 19.00
    },
    "pesos": {
      "w1_skus": 0.40,
      "w2_clientes": 0.35,
      "w3_pedidos": 0.25
    },
    "referencias_max": {
      "skus_max": 500,
      "clientes_max": 100,
      "pedidos_max": 2000
    },
    "ito_calculado": 21.95
  },
  "categoria": {
    "calculada": "M",
    "comercial": "M",
    "confirmada": "M",
    "discrepancia": "ninguna",
    "discrepancia_critica": false,
    "nota_discrepancia": null
  },
  "cold_start": {
    "anios_historial": 2.5,
    "nivel": "Estándar",
    "codigo": "CS-ESTANDAR",
    "inviable": false,
    "cascada_paso": null,
    "cascada_descripcion": null
  },
  "escalamiento": {
    "requerido": false,
    "razones": []
  },
  "warnings": [
    "ITO provisional — pesos y umbrales pendientes de calibración (T-030)"
  ]
}
```

## Ejemplo — cliente XL vendido como M (discrepancia crítica)

```json
{
  "tenant_id": "manufactura-grande-002",
  "timestamp_analisis": "2026-06-08T15:10:22Z",
  "session_data_path": "010_discovery/session_data.json",
  "ito": {
    "provisional": true,
    "valores_base": {
      "skus_activos": 850,
      "clientes_xyz": 95,
      "pedidos_por_mes": 3200
    },
    "normalizados": {
      "norm_skus": 100.00,
      "norm_clientes": 95.00,
      "norm_pedidos": 100.00
    },
    "pesos": {
      "w1_skus": 0.40,
      "w2_clientes": 0.35,
      "w3_pedidos": 0.25
    },
    "referencias_max": {
      "skus_max": 500,
      "clientes_max": 100,
      "pedidos_max": 2000
    },
    "ito_calculado": 98.25
  },
  "categoria": {
    "calculada": "XL",
    "comercial": "M",
    "confirmada": "M",
    "discrepancia": "critica",
    "discrepancia_critica": true,
    "nota_discrepancia": "El ITO calculado (98.25) ubica al cliente en categoría XL, pero fue vendido como M. Diferencia de 2 niveles — requiere revisión comercial antes de continuar."
  },
  "cold_start": {
    "anios_historial": 4.0,
    "nivel": "Alta",
    "codigo": "CS-ALTA",
    "inviable": false,
    "cascada_paso": null,
    "cascada_descripcion": null
  },
  "escalamiento": {
    "requerido": true,
    "razones": [
      "Discrepancia crítica de categoría: ITO calcula XL pero se vendió como M"
    ]
  },
  "warnings": [
    "ITO provisional — pesos y umbrales pendientes de calibración (T-030)"
  ]
}
```

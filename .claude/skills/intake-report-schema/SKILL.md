---
name: intake-report-schema
description: Schema y reglas de escritura de intake_report.json — el reporte cuantificado de
  la entrega producido por el intake-processor en P7 del harness 015 Intake de FARO. Define
  los conteos obligatorios (formato/encoding/delimitador, filas, errores de tipo, duplicados,
  rango temporal, campos ideales faltantes, warnings) y cómo registrar el warning de rango.
  Es el primer documento de la cadena de evidencia del ISD que leerá el 020. Usar cuando el
  intake-processor escribe 005_bronze/intake_report.json.
user-invocable: false
---

## Propósito

`intake_report.json` es el **reporte cuantificado** de una entrega de datos. No corrige ni
transforma nada (eso es el 025); solo **cuenta y registra** lo observado al ingerir el
archivo. Es el primer eslabón de la cadena de evidencia que el **020 Diagnosis** usa para
calcular el ISD (Índice de Salud de Datos). Vive junto al Bronce en
`…/tenants/{id}/1000_data/005_bronze/intake_report.json`.

**Escritor único:** `intake-processor` (Worker), en P7. **Lectores:** 020 Diagnosis, 025
Refinery (referencia), `intake-evaluator` (Instancia C, dimensión D6).

Schema de referencia: `templates/015_intake/schemas/intake_report_schema.json`.

---

## Estructura

```json
{
  "tenant_id": "",
  "delivery_id": "",
  "mode": "batch | incremental",
  "timestamp": "",
  "format": {
    "tipo": "csv | xlsx | xls",
    "delimitador": null,
    "encoding": "",
    "hoja": null,
    "fila_cabecera": null,
    "huella_reutilizada": false
  },
  "schema1": {
    "rows": 0,
    "campos_minimos_presentes": [],
    "campos_minimos_faltantes": [],
    "campos_ideales_presentes": [],
    "campos_ideales_faltantes": [],
    "errores_tipo": { "fecha_pedido": 0, "id_cliente": 0, "id_producto": 0, "cantidad_solicitada": 0 },
    "duplicados": { "internos": 0, "vs_bronce_previo": 0 },
    "rango_temporal": { "fecha_min": "", "fecha_max": "", "dias_cubiertos": 0 }
  },
  "schema2": {
    "status": "CREATED | NOT_EXPECTED | EXPECTED_NOT_RECEIVED",
    "rows": 0,
    "campos_minimos_faltantes": [],
    "errores_tipo": {}
  },
  "rango_declarado_vs_real": {
    "declarado_anios": null, "real_anios": null, "discrepancia_pct": null, "warning": false
  },
  "warnings": []
}
```

---

## Reglas por campo

**`tenant_id`** — el slug generado por el 010 (fuente única DEC-047). El processor lo **lee**
de `client_config` / `harness-state.json`; nunca lo regenera. Debe coincidir carácter por
carácter con el del evento `intake_complete` y el `_manifest.json`.

**`delivery_id`** — `YYYYMMDD` de la entrega. Igual al usado en el nombre del archivo Bronce.

**`mode`** — `batch` o `incremental`, tomado de `client_config.modo_ingesta`.

**`format`** — lo que detectó P1 (`format_detector`):
- `delimitador` solo para CSV (`,` `;` `|`); `null` para Excel.
- `encoding` el realmente usado para decodificar (`utf-8`, `utf-8-sig`, `cp1252`, `latin-1`).
- `hoja` / `fila_cabecera` solo para Excel; `null` para CSV.
- `huella_reutilizada: true` si se aplicó una huella previa de `client_config` sin re-detectar.

**`schema1.errores_tipo`** — conteo exacto por campo mínimo (P3). **Cuenta, no elimina.**
Un valor 0 significa "verificado, sin errores", no "no verificado".

**`schema1.duplicados`** — `internos`: duplicados dentro del archivo de esta entrega (clave
`(fecha_pedido, id_cliente, id_producto)`). `vs_bronce_previo`: solo en modo incremental,
registros ya existentes en el Bronce acumulado (que se excluyeron de la persistencia).

**`schema1.campos_ideales_faltantes`** — de los hasta 17 campos ideales (DEC-014) que no
llegaron. No bloquean; alimentan el ISD del 020.

**`schema2.status`:**
- `NOT_EXPECTED` — `client_config.tiene_esquema2 == false`.
- `EXPECTED_NOT_RECEIVED` — `tiene_esquema2 == true` pero el archivo no llegó. **No bloquea**
  el Bronce del Esquema 1 (decisión d, DEC-057).
- `CREATED` — Esquema 2 recibido y persistido en Bronce.

**`rango_declarado_vs_real`** (P5) — comparación del rango real contra el historial declarado
en el 010. Si `discrepancia_pct > 20` → `warning: true` **y** se añade una entrada legible a
`warnings`. **Olvidar este warning cuando aplica es el defecto del ancla 0.8 de la rúbrica**
(no invalida el Bronce, pero el 020 pierde una señal). Si no hay dato declarado, dejar
`declarado_anios: null` y `warning: false`.

**`warnings`** — lista de strings legibles (rango, encoding ambiguo resuelto, Esquema 2 no
recibido, etc.). Vacía si no hubo ninguno.

---

## Reglas de escritura

1. Escribir **solo en P7**, después de que el Bronce existe y su SHA-256 está en el manifest.
   Nunca antes de P6.
2. Todos los conteos provienen de la ejecución real de los módulos (P3/P4/P5), nunca estimados.
3. El JSON producido debe validar contra `intake_report_schema.json`.
4. En caso de rework de reportes con Bronce intacto (rechazo D6), se **regenera** este archivo;
   el Bronce y su hash no se tocan.
5. No incluir datos de negocio fila a fila — solo agregados y metadatos (E6, referencias ligeras).

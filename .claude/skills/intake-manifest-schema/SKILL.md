---
name: intake-manifest-schema
description: Schema y reglas de escritura de _manifest.json — el registro autoritativo de
  entregas Bronce del harness 015 Intake de FARO. Fuente única de verdad del histórico (unión
  lógica de los archivos inmutables), con SHA-256 por archivo. Define cómo añadir una entrada
  por entrega sin reescribir las previas y cómo lo usan el deduplicador incremental y los
  consumidores 020/025 para verificar fidelidad. Usar cuando el intake-processor escribe o
  lee 005_bronze/_manifest.json.
user-invocable: false
---

## Propósito

`_manifest.json` es el **registro autoritativo** de todo lo que existe en el Bronce de un
tenant. El Bronce es un conjunto de archivos inmutables (uno por entrega); el manifest es su
índice y su prueba de integridad. Tres usos:

1. **Inmutabilidad verificable (D5):** guarda el SHA-256 de cada archivo. "No lo toqué" se
   convierte en prueba criptográfica.
2. **Unión lógica del histórico (incremental):** el `deduplicator` lee el manifest para saber
   qué archivos Bronce previos componen el acumulado y excluir registros ya existentes.
3. **Verificación aguas abajo:** 020 y 025 recalculan el hash de cada archivo Bronce contra el
   manifest **antes** de procesar. Si no coincide → Bronce alterado → se detienen.

Vive en `…/tenants/{id}/1000_data/005_bronze/_manifest.json`.

**Escritor único:** `intake-processor` (Worker), en P6. **Lectores:** el propio processor
(deduplicador incremental), 020, 025, `intake-evaluator` (D5).

Schema de referencia: `templates/015_intake/schemas/manifest_schema.json`.

---

## Estructura

```json
{
  "tenant_id": "",
  "entregas": [
    {
      "delivery_id": "YYYYMMDD",
      "mode": "batch | incremental",
      "timestamp": "",
      "archivo": "orders_batch_YYYYMMDD.csv",
      "esquema": 1,
      "sha256": "",
      "rows": 0,
      "rango": { "fecha_min": "", "fecha_max": "" }
    }
  ]
}
```

---

## Reglas por campo

**`tenant_id`** — el slug del 010 (DEC-047). Coincide con el del Bronce, el reporte y el evento.

**`entregas`** — array ordenado cronológicamente. **Una entrada por archivo Bronce escrito.**
- Un Esquema 1 + un Esquema 2 en la misma entrega = **dos** entradas (`esquema: 1` y `esquema: 2`).
- `archivo` — nombre del archivo Bronce (no path absoluto): `orders_{mode}_{YYYYMMDD}.csv`,
  `inventory_{mode}_{YYYYMMDD}.csv`.
- `sha256` — hash hex del archivo **tal como se escribió** (bit-exacto a la entrada).
- `rows` — filas de datos del archivo.
- `rango` — `fecha_min`/`fecha_max` de ese archivo (solo Esquema 1; Esquema 2 puede dejarlo vacío).

---

## Reglas de escritura — APPEND-ONLY

1. **Nunca reescribir ni eliminar entradas previas.** Cada entrega exitosa **añade** entradas
   al array `entregas`. Esto es el corazón de la decisión f (DEC-057): el "Bronce acumulado"
   es la unión de archivos, no un archivo que se reescribe.
2. **Batch** sobre un tenant sin entregas previas: añade la(s) entrada(s) de esta entrega.
   Un segundo batch es excepcional (re-ingesta) y se trata como nueva entrega, no como reemplazo.
3. **Incremental:** cada entrega añade exactamente las entradas de sus archivos nuevos.
4. Si el manifest no existe (primera entrega del tenant), crearlo con `tenant_id` y la primera
   entrada.
5. **Idempotencia (recuperación CP-03↔CP-05):** si ya existe una entrada con el mismo
   `delivery_id` + `archivo` + `sha256`, **no** duplicarla (el paso ya se completó antes del
   fallo). Si existe el mismo `archivo` con `sha256` distinto → error: no se sobrescribe Bronce
   salvo excepción controlada de rework D5 registrada por A.
6. El JSON debe validar contra `manifest_schema.json` tras cada escritura.

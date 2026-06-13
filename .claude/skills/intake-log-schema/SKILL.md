---
name: intake-log-schema
description: Schema y reglas de escritura de la fila intake_log — los metadatos consultables
  de una entrega del harness 015 Intake de FARO. Una fila por entrega con files JSONB (path +
  sha256 + rows + date_range por archivo). En Fase 1 es un JSON local con _pendiente_supabase:
  true; en Fase 3 una fila de la tabla Supabase intake_log. El _manifest.json es la fuente
  autoritativa; esta fila la indexa. Usar cuando el intake-processor escribe la fila intake_log.
user-invocable: false
---

## Propósito

`intake_log` es la **vista consultable** de una entrega: metadatos indexables para que la
operación (y futuras consultas SQL en Fase 3) sepan qué se ingirió, cuándo y con qué hashes,
sin tener que abrir el `_manifest.json`. El manifest sigue siendo la **fuente autoritativa**;
esta fila lo refleja.

**Fase 1 (actual):** un archivo JSON local (p. ej. junto a la persistencia del tenant) con
`_pendiente_supabase: true`, idéntico patrón al fallback del 010. **Fase 3:** una fila de la
tabla Supabase `intake_log` con `files` como columna JSONB.

> **Reconciliación de nombre (DEC-047):** la tabla de clientes es **`tenants`**, no `clients`.
> `tenants.last_intake_at` se actualiza junto con esta fila.

**Escritor único:** `intake-processor` (Worker), en P7. **Lectores:** operación / consultas
de Fase 3, `intake-evaluator` (D6).

Schema de referencia: `templates/015_intake/schemas/intake_log_schema.json`.

---

## Estructura

```json
{
  "_pendiente_supabase": true,
  "tenant_id": "",
  "delivery_id": "",
  "mode": "batch | incremental",
  "created_at": "",
  "files": [
    { "path": "", "esquema": 1, "sha256": "", "rows": 0, "date_range": { "min": "", "max": "" } }
  ],
  "report_path": "",
  "event_emitted": false
}
```

---

## Reglas por campo

**`_pendiente_supabase`** — `true` en Fase 1 (fallback local). En Fase 3, la escritura va a la
tabla y este flag desaparece o queda `false`.

**`tenant_id` / `delivery_id` / `mode`** — coinciden con el reporte, el manifest y el evento.

**`created_at`** — timestamp ISO 8601 **real** (reloj de ejecución, no narrado — LEC del 010
sobre timestamps).

**`files`** (JSONB) — una entrada **por archivo Bronce** de esta entrega:
- `path` — path al archivo Bronce (relativo al Storage del tenant).
- `esquema` — 1 o 2.
- `sha256` — el mismo hash que está en el manifest para ese archivo.
- `rows` — filas de datos.
- `date_range` — `min`/`max` (solo Esquema 1).

**`report_path`** — path a `intake_report.json` de esta entrega.

**`event_emitted`** — `false` cuando se escribe la fila en P7; pasa a `true` solo después de
que P8 emitió `intake_complete`. Permite saber si una entrega quedó a medias entre CP-04 y CP-05.

---

## Reglas de escritura

1. **Una fila por entrega.** Nunca acumular varias entregas en una fila ni reescribir filas
   previas (cada entrega incremental genera su propia fila).
2. Los `sha256` de `files` deben ser **idénticos** a los del `_manifest.json` (consistencia
   manifest↔log). Si difieren, es un defecto de D6.
3. Escribir en P7, después del reporte. Actualizar `event_emitted: true` en P8 tras el evento.
4. Actualizar `tenants.last_intake_at` con `created_at` (Fase 1: en el JSON de fallback del
   tenant; Fase 3: la columna real).
5. El JSON debe validar contra `intake_log_schema.json`.

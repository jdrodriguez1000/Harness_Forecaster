# Decisions Library — 015 Intake
# Harness FARO — Sabbia Solutions & Software
# Escritor de la Parte B: Governor (Instancia A) · Lector obligatorio: Orchestrator (Instancia B) en Modo PLAN (§12.2 paso 2)

> Este archivo tiene **dos partes**:
> - **Parte A — Fundamentos de diseño del sistema** (curada, fija): las decisiones de
>   arquitectura que el 015 debe respetar SIEMPRE, en todo tenant. Es de solo lectura para B;
>   no se edita ciclo a ciclo. Es el equivalente operativo de `progress/decisions.md`, resumido
>   para que B no tenga que leer el repo fuente en runtime.
> - **Parte B — Decisiones operativas por tenant** (append-only): los overrides y resoluciones
>   especiales que A registra al cierre de cada ciclo para un tenant concreto. Sigue el patrón de
>   la skill `discovery-knowledge-schema`. Comienza vacía.

---

# PARTE A — Fundamentos de diseño del sistema (curada, solo lectura)

Estas son las decisiones del proyecto que gobiernan el comportamiento del 015. B las da por
sentadas antes de spawnear al Worker. La fuente canónica es `progress/decisions.md` del repo
fuente; aquí va el resumen ejecutivo accionable.

## DEC-012 — Dos modos de ingesta: Batch e Incremental
**Qué:** El cliente entrega datos en uno de dos modos. **Batch:** un archivo histórico completo,
una sola vez. **Incremental:** entregas periódicas (diario/semanal) de las que el sistema
incorpora **solo los registros nuevos**, con deduplicación por la clave
`(fecha_pedido, id_cliente, id_producto)`. No se acepta correo electrónico como fuente.
**Impacto en el 015:** el pipeline detecta el `mode` desde el `client_config` (lo fija el 010).
En Incremental, el `deduplicator` (P4) compara contra la **unión lógica del Bronce previo** vía
`_manifest.json` para el **conteo** `vs_bronce_previo`; la bit-exactitud de Bronce (DEC-057.6)
manda sobre cualquier reescritura. El pronóstico se entrega mensual en ambos modos.

## DEC-014 — Dos esquemas complementarios e independientes
**Qué:** **Esquema 1 (obligatorio):** historial de pedidos — 4 campos mínimos
(`fecha_pedido`, `id_cliente`, `id_producto`, `cantidad_solicitada`) y hasta 17 campos ideales.
**Esquema 2 (opcional):** producción e inventario de ABC — 6 campos mínimos
(`fecha`, `id_producto`, `cantidad_producida`, `stock_disponible`, `costo_unitario`,
`stock_minimo`).
**Impacto en el 015:** el GATE de estructura (P2, `schema_validator`) rechaza ⟺ falta un campo
**mínimo** del esquema activo; los ideales faltantes son déficit que **no** rechaza (alimentan el
ISD del 020). El matching de cabeceras es **canónico** (trim/acentos/sinónimos), nunca por
substring (veto D2: FP = FN = 0). Esquema 2 ausente NO bloquea (ver DEC-057.5).

## DEC-024 — El 020 corre EN PARALELO con el 025, ambos leen Bronce
**Qué:** Cadena del pipeline principal: `015 → { 020 ∥ 025 } → 030 → 035 → 040`. El 020 Diagnosis
(ISD) y el 025 Refinery (Bronce→Plata→Oro) leen **ambos** desde Bronce y corren en paralelo —
diagnosticar sobre datos ya limpios invalidaría la medición real de la salud.
**Impacto en el 015:** el evento `intake_complete` (P8) declara `next_harnesses:
[020_diagnosis, 025_refinery]` y debe dejar Bronce en estado **solo-lectura verificable**
(SHA-256) para los dos consumidores. El fan-out lo dispara el conductor/operador (DEC-051) en
Fase 1.

## DEC-044 — Convención de carpetas de datos del proyecto cliente
**Qué:** Las capas medallón viven bajo `1000_data/`: Bronce en `1000_data/005_bronze/`, Plata en
`1000_data/007_silver/`, Oro en `1000_data/009_gold/`.
**Impacto en el 015:** el `bronze_writer` (P6) escribe en
`1000_storage_local/tenants/{tenant_id}/1000_data/005_bronze/` (Storage local, fallback Fase 1).
Toda ruta de lectura/escritura de datos usa esta convención numerada.

## DEC-047 — `tenant_id` único, generado por el governor
**Qué:** El `tenant_id` se genera una sola vez (en el governor del 010 al construir el Sprint
Contract) y se persiste en `harness-state.json`. Todos los agentes downstream lo **leen**, nunca
lo generan ni infieren. La tabla operacional se llama **`tenants`** (no `clients`).
**Impacto en el 015:** el `intake-governor` toma el `tenant_id` del handoff del 010
(`onboarding_discovery_complete` + `client_config`) y lo propaga; el Worker y el evaluator lo
**leen** de `harness-state.json`. Divergencia de `tenant_id` entre artefactos es un defecto grave
(causó hallazgos GLOBAL en el 010).

## DEC-057 — Las 10 decisiones de diseño del 015 Intake
1. **Formatos:** CSV con detección de delimitador (`,` `;` `|`) + Excel `.xlsx`/`.xls`. Nada más.
2. **Fuente agnóstica:** el 015 recibe siempre un **snapshot tabular** vía `source_adapter`. Fase 1
   solo implementa el adaptador manual/operador. Una fuente viva (ERP/BD) se materializa como
   snapshot **antes** de tocar el 015 (lo obliga el invariante Bronce).
3. **Peso agéntico invertido:** A/B/C completos pero **workers livianos** — el grueso es código con
   **TDD real** + ~20 fixtures (E9). El LLM solo interviene en puntos de juicio
   (encoding/delimitador/Excel ambiguo). C usa rúbrica de **integridad/fidelidad**.
4. **Worker único:** un solo `intake-processor` ejecuta la cadena secuencial P1→P8 (`run_intake`).
   No se paraleliza dentro del 015; el paralelismo es **después** (020 ∥ 025).
5. **Esquemas independientes:** Esquema 2 ausente NO bloquea el Bronce del Esquema 1; se registra
   como `EXPECTED_NOT_RECEIVED`.
6. **Inmutabilidad (veto D5):** Bronce **write-once + SHA-256** verificable. Se escriben los
   **bytes del snapshot** (bit-exacto), nunca una re-serialización del DataFrame.
7. **Incremental:** un archivo Bronce inmutable **por entrega** + `_manifest.json` (unión lógica
   del histórico). **Nunca** reescritura ni concatenación de un archivo acumulado.
8. **Excel con memoria:** heurística + confirmación del operador en la 1ª entrega → **huella de
   formato** (hoja/cabecera/delimitador/encoding) persistida en `client_config` y reutilizada
   después. No toca el schema del 010.
9. **Persistencia = rebanada del intake:** Storage de Bronce + `intake_log` (una fila por entrega,
   `files` JSONB con path+sha256+rows+date_range) + evento. Fallback JSON Fase 1 con
   `_pendiente_supabase: true`. **No** se diseña cobro (T-030/T-031 no bloquean el 015).
10. **Handoff atómico:** el evento `intake_complete` es el **último** artefacto (si algo falla
    antes, no hay evento). Payload por referencia (E6) + hashes; Bronce solo-lectura para 020/025;
    1 evento por entrega.

---

# PARTE B — Decisiones operativas por tenant (append-only)

> A agrega un bloque al cierre de cada ciclo (12.5). Si el ciclo transcurrió sin decisiones
> especiales, escribe el encabezado del ciclo con la nota `"Sin decisiones especiales en este
> ciclo"`. **Nunca** se borra ni edita una entrada anterior; una decisión revertida se anula con
> una entrada nueva. IDs secuenciales por harness (`DEC-001`, `DEC-002`, …), sin reiniciar entre
> tenants ni ciclos.

### Formato de cada entrada

```markdown
## Ciclo {N} — {tenant_id} — {fecha YYYY-MM-DD} — entrega {delivery_id}

### DEC-{NNN} — {Título breve de la decisión}
**Fecha:** {YYYY-MM-DD}
**Tenant:** {tenant_id}
**Categoría:** {comercial | técnica | operativa}
**Decisión:** {Qué se decidió, en una o dos oraciones}
**Razón:** {El contexto que llevó a esta decisión}
**Impacto en futuras ejecuciones:** {Qué debe saber B la próxima vez que ingiera para este tenant}
```

Casos típicos del 015 que ameritan una entrada: huella de formato confirmada por el operador para
un Excel atípico (hoja/fila de cabecera no estándar); aceptación de un override de write-once
(rework D5 controlado y registrado); resolución de un encoding/delimitador ambiguo escalado;
cambio de modo Batch↔Incremental acordado con el cliente.

---

_(Sin ciclos registrados aún — la Parte B se completa al cierre del primer ciclo de ejecución.)_

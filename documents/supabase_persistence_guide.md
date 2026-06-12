# Guía Base de Persistencia con Supabase — FARO

> **Estado:** documento base / guía de diseño. Recoge las **definiciones principales** que
> desarrollaremos en el futuro para la persistencia de FARO en Supabase. **No es un schema
> final ni una instrucción de construcción** — es el mapa que orienta cuándo y cómo construir
> cada capa. Las definiciones SQL son bocetos provisionales; el DDL definitivo se diseñará por
> capa cuando llegue su momento.
>
> **Creado:** sesión 33 (2026-06-11). **Origen:** análisis de `modelo.md` (schema de knowledge
> base heredado de otro harness) aplicado al dominio real de FARO.

---

## 1. Propósito y alcance

FARO es un sistema **Service as a Software**: Triple S opera todo y entrega pronósticos de
demanda como servicio a empresas manufactureras. Eso implica persistir **estado operacional
real** (clientes, suscripciones, cobros, estado de los harnesses, datos del cliente), no solo
documentación.

Hoy (Fase 1) el harness 010 escribe sus salidas como **archivos JSON locales** marcados con el
flag `"_pendiente_supabase": true`. Ese flag **es el plan**: persistir local primero, conmutar
a Supabase después sin reescribir la lógica de los agentes. Este documento define el destino de
esa conmutación.

**Este documento define:**
- Las capas de persistencia de FARO y su orden de construcción.
- Qué se reutiliza de `modelo.md` (patrones) y qué no (sus tablas).
- El esquema **operacional** (la primera capa a construir) a nivel conceptual.
- La estrategia de conmutación fallback JSON → Supabase.
- Las decisiones fundacionales y las que quedan abiertas.

**Este documento NO define (todavía):**
- DDL final de ninguna tabla.
- El esquema de los datos de negocio (medallón) — llega con los harnesses 015–040.
- El esquema de knowledge base — capa de menor urgencia.

---

## 2. Principios de persistencia FARO

1. **`tenant_id` es ciudadano de primera clase.** Cada cliente es un tenant. Toda tabla
   operacional y de negocio lleva `tenant_id`. La fuente única del `tenant_id` es el governor
   del harness 010 en E10-A (DEC-047). Esto distingue a FARO de `modelo.md`, donde la
   multi-tenancy es opcional (`organization_id` con default).
2. **Los datos originales del cliente son intocables (arquitectura medallón).** Bronce = copia
   exacta, Plata = limpieza, Oro = listo para modelos. Triple S nunca modifica el origen. Los
   datos de negocio NO viven en tablas relacionales pesadas — viven en **Storage** por tenant
   (`1000_storage_local/tenants/{tenant_id}/...`, futuro Supabase Storage / bucket). La BD
   relacional guarda **metadatos y punteros**, no los datasets crudos.
3. **Fallback-first.** Toda escritura tiene un modo Fase 1 (JSON local) y un modo Fase 3
   (Supabase). El agente decide por disponibilidad del servicio, no por código distinto. El
   JSON local sigue siendo el respaldo aun con Supabase activo.
4. **Los agentes leen lo mínimo.** Una query devuelve las filas y columnas exactas que el
   agente necesita — nunca volcados completos ni contexto innecesario. (Principio heredado de
   `modelo.md`, válido para FARO.)
5. **Trazabilidad y auditoría.** Toda fila apunta a su tenant y lleva timestamps. El estado de
   cada harness queda registrado para reanudación y diagnóstico.
6. **Single source of truth por dato.** Ningún dato se genera en dos lugares. (Es justo la
   lección de la divergencia de `tenant_id`: T-167/T-168.)

---

## 3. Las cuatro capas de persistencia

FARO no necesita "una base de datos". Necesita cuatro capas con urgencias distintas:

| # | Capa | Qué persiste | Estado hoy | Urgencia | Dónde |
|---|------|--------------|------------|----------|-------|
| 1 | **Operacional (tenants)** | `clients`, `contacts`, `client_config`, `subscriptions`, `events` | Ya diseñada como `db_records` JSON (`_pendiente_supabase: true`) | **Alta** | Tablas Postgres |
| 2 | **Estado de runtime** | `harness-state`, `execution-state`, checkpoints, escalaciones | Archivos JSON por proyecto | Media | Tablas Postgres (o híbrido) |
| 3 | **Datos de negocio (medallón)** | Bronce/Plata/Oro, forecasts, exports, salud de datos | No existe (llega con 015–040) | Alta pero **futura** | **Storage** + metadatos en tablas |
| 4 | **Knowledge base** | `decisions_library`, `lessons_learned` por harness | Markdown, volumen trivial | **Baja** | Tablas Postgres (FTS + pgvector) |

**Orden de construcción recomendado:** Capa 1 → Capa 2 → Capa 3 (incremental con cada harness)
→ Capa 4 (cuando el volumen lo justifique). La Capa 4 es lo que cubre `modelo.md`; es la
**última**, no la primera.

---

## 4. Qué se reutiliza de `modelo.md` (y qué no)

`modelo.md` es un schema de **knowledge base** diseñado para **otro harness** (generación de
documentos BRD/BDD/SAD). Su **dominio no aplica** a FARO, pero sus **patrones sí**.

**Se reutiliza (patrones):**
- Stack: PostgreSQL gestionado vía **Supabase** (pgvector nativo, PostgREST, pgBouncer, RLS).
- **FTS en español con `unaccent`** (`spanish_unaccent`) para búsquedas de texto.
- **pgvector + HNSW** para búsqueda semántica (relevante solo para la Capa 4).
- **Columnas generadas** (`tsvector` STORED) para FTS sin mantenimiento manual.
- **Estrategia de migración** local → cloud por `DATABASE_URL` (sin reescritura de queries).
- Consideración de **RLS** y connection pooling.

**No se reutiliza (tablas):**
- `documents (BRD/BDD/SAD)`, `sad_writer`, `project_metrics` de pipeline documental — no existen
  en FARO.
- La capa de knowledge de `modelo.md` (`decisions`, `lessons`) se **adaptará al dominio FARO**
  cuando se construya la Capa 4, no se copia tal cual.

---

## 5. Decisiones fundacionales

| ID | Decisión | Razón |
|----|----------|-------|
| P-01 | **Proveedor: Supabase** | pgvector nativo, PostgREST (queries HTTP sin driver), Storage para medallón, RLS, plan gratuito generoso. El schema es Postgres estándar → portable a Neon/Railway si hiciera falta. |
| P-02 | **`tenant_id` central en todas las tablas** | Multi-tenancy es el núcleo del negocio, no un add-on. Aislamiento por RLS por tenant. |
| P-03 | **Datos de negocio (medallón) en Storage, no en tablas** | Volumen alto, datos intocables, copia exacta. La BD guarda punteros/metadatos. |
| P-04 | **Fallback JSON ↔ Supabase como adaptador** | Conmutar de Fase 1 a Fase 3 es cambiar el destino de escritura, no la lógica del agente. |
| P-05 | **Construir por capas, no de golpe** | La Capa 1 desbloquea operación real; la 4 espera volumen. Evita sobre-ingeniería. |
| P-06 | **Single writer por dato** | Cada dato tiene un único generador (p. ej. `tenant_id` = governor). Réplica de DEC-047. |

> Estas decisiones se trasladarán a `progress/decisions.md` como DEC formales cuando se apruebe
> el documento.

---

## 6. Esquema operacional (Capa 1) — definición conceptual

Derivado de los 4 `db_records` que el configurator del harness 010 ya produce, más los eventos
y las reglas de negocio de `CLAUDE.md` (precios M/L/XL, ciclo de cobro, retención). **Bocetos
provisionales** — el DDL final se cierra al construir la capa.

### 6.1 `tenants` (raíz)
Identidad del cliente. La PK es el `tenant_id` generado por el governor (DEC-047).
- `tenant_id` (PK, TEXT — slug DEC-047, p. ej. `prolimex-s-a-de-c-v-4528`)
- `razon_social`, `sector`
- `estado` (`onboarding` | `activo` | `suspendido` | `cancelado`)
- `categoria` (`M` | `L` | `XL`) — del ITO
- `ito_calculado` (NUMERIC), `cold_start_nivel`
- `created_at`, `updated_at`

### 6.2 `contacts`
Contactos del tenant. Hoy: principal + pagos (T-165/DEC-052).
- `id` (PK UUID), `tenant_id` (FK)
- `tipo` (`principal` | `pagos` | …)
- `nombre`, `correo`, `telefono`
- Distingue explícitamente **responsable de pagos** (recibe avisos de cobro) de contacto
  principal y de aprobador/firmante (DEC-052).

### 6.3 `client_config`
Configuración técnica de ingesta y pronóstico (entrada del harness 015).
- `tenant_id` (FK, UNIQUE)
- `modo_ingesta`, `frecuencia_incremental`, `anios_historial_disponible`
- `horizonte_pronostico`, `jerarquia_producto`, `jerarquia_geografica`
- `minimos_contractuales`, `nivel_cold_start`, `tiene_esquema2`, `sistema_erp`
- `onboarding_config_path` (puntero al deliverable)

### 6.4 `subscriptions`
Suscripción y cobro. Núcleo del ciclo de pagos de `CLAUDE.md`.
- `id` (PK), `tenant_id` (FK)
- `plan` (`Mensual` | `Trimestral` | `Anual`), `descuento_porcentaje`
- `monto_mensual_base_usd`, `monto_mensual_efectivo_usd`
- `fecha_inicio`, `fecha_primer_cobro`, `fecha_vencimiento_actual`
- `estado` (`onboarding_gratuito` | `activa` | `en_gracia` | `suspendida` | `cancelada`)
- Soporta la lógica de días 2-9 (alertas/gracia/suspensión) y la regla de renovación de fecha
  (atraso ≤2 días conserva fecha / ≥3 días = pago + 30 días).

### 6.5 `events` (bus de eventos)
Eventos entre harnesses (p. ej. `onboarding_discovery_complete`).
- `id` (PK), `tenant_id` (FK)
- `tipo`, `payload` (JSONB), `harness_origen`
- `estado` (`pendiente` | `procesado`), `created_at`, `processed_at`
- Hoy en `600_persistence/events/`; futura tabla + (opcional) Realtime de Supabase.

### 6.6 Tablas de soporte previstas (no en 010, llegan después)
- `data_health` — diagnóstico mensual de salud de datos (objetivo ≥95%), desde capa Bronce.
- `forecasts` / `forecast_runs` — metadatos de cada pronóstico entregado (SLA: primeros 5 días
  hábiles, MAPE por nivel de salud).
- `billing_cycles` / `payments` — histórico de cobros, integración con pasarela de pagos (por
  definir — T-031).
- `export_requests` — solicitudes de exportación al cancelar (retención 6 meses, bloqueo de
  borrado con exportación pendiente).

---

## 7. Capa 2 — Estado de runtime (resumen)

`harness-state.json` y `execution-state.json` son hoy archivos por proyecto. Al migrar:
- Opción A (recomendada a evaluar): tablas `harness_state` / `harness_checkpoints` /
  `escalations` por `(tenant_id, harness)`, con el JSON como columna `JSONB` para el detalle
  + columnas indexadas para los campos consultables (`status`, `governor_mode`, `last_checkpoint`).
- Mantener el archivo local como respaldo/caché de la sesión activa (el conductor re-deriva del
  disco — ver DEC-051; conviene no romper esa lectura local).
- Respetar la **Single Writer Rule** existente (governor escribe harness-state, orchestrator
  escribe execution-state) también contra la BD.

> Decisión abierta: ¿el estado vivo de runtime vale la pena en BD, o basta archivo local +
> snapshot en BD al cerrar cada fase? Depende de si el dashboard/monitoreo necesita leer estado
> en vivo cross-tenant.

---

## 8. Capa 3 — Datos de negocio / medallón (resumen)

- **Datasets crudos y transformados → Supabase Storage** (buckets por tenant), NO tablas.
  Estructura ya definida en local: `1000_storage_local/tenants/{tenant_id}/1000_data/005_bronze/`,
  `007_silver/`, `009_gold/`, `1010_models/`, `1020_forecasts/`, `1030_exports/` (DEC-044).
- **Metadatos en tablas:** qué dataset, qué versión, qué salud, qué corrida de pronóstico lo usó.
- Se construye **incrementalmente** con cada harness (015 Intake, 020 Diagnosis, 025–040).
- Los agentes operan únicamente sobre la capa **Oro** (regla de negocio).

---

## 9. Capa 4 — Knowledge base (resumen)

Última capa, cuando el volumen de decisiones/lecciones haga ineficiente leer Markdown.
- Adaptar las tablas `decisions` y `lessons` (por harness FARO, no por BRD/BDD/SAD) al dominio.
- FTS español + pgvector/HNSW para búsqueda semántica entre clientes/dominios distintos.
- Migración con script Python que genera embeddings una vez.

Los **bocetos SQL concretos reutilizables** para esta capa (config FTS español, DDL pgvector +
HNSW, columnas generadas, patrón de migración y notas por proveedor) están en el **Apéndice A**
de este documento. Provienen del schema heredado `modelo.md`, ya absorbido aquí — `modelo.md`
puede archivarse/eliminarse sin pérdida de información.

---

## 10. Estrategia de conmutación Fase 1 → Fase 3

1. **Hoy (Fase 1):** agentes escriben JSON local con `"_pendiente_supabase": true`.
2. **Construir Capa 1 en Supabase:** crear schema operacional + extensiones.
3. **Adaptador de escritura:** un único punto (helper / tool) que, si `DATABASE_URL` está
   configurada y el servicio responde, hace UPSERT a Supabase **y** deja el JSON como respaldo;
   si no, solo JSON (comportamiento actual). Los agentes no cambian su lógica.
4. **Backfill:** cargar a Supabase los `db_records` JSON de tenants ya procesados.
5. **Verificación:** queries cross-tenant (lo que el JSON por proyecto no permite) — p. ej.
   "todos los tenants con vencimiento en 3 días".
6. **Solo cambia `DATABASE_URL`** entre entornos (local/Supabase) — sin reescritura de queries
   (ver Apéndice A.5 "Migración local → cloud").

---

## 11. Decisiones abiertas (por definir antes/durante la construcción)

- **D-A — ¿Cuándo construir la Capa 1?** Recomendación: **después** de validar el harness 010
  e2e con los fixes de la sesión 33, y antes/junto con el diseño del harness 015 (que consume
  `client_config`). No ahora mismo.
- **D-B — Pasarela de pagos (T-031).** El esquema `subscriptions`/`payments` depende de cuál se
  elija. Bloquea el detalle de la Capa 1 de cobro.
- **D-C — Estado de runtime en BD: ¿vale la pena?** (ver §7). Depende del dashboard/monitoreo.
- **D-D — RLS: ¿por tenant desde el día 1?** Probable sí, dado que el negocio es multi-tenant.
- **D-E — ¿PostgREST (HTTP) o driver SQL para los agentes?** PostgREST simplifica el tooling en
  Claude Code (sin driver), pero ata a la API de Supabase. Evaluar al construir el adaptador.
- **D-F — Pesos/umbrales del ITO (T-030).** Afectan `tenants.categoria`/`ito_calculado`.

---

## 12. Referencias

- `CLAUDE.md` — reglas de negocio (precios M/L/XL, ciclo de cobro, medallón, retención, SLAs).
- `.claude/agents/discovery-configurator.md` — origen de los 4 `db_records` (Capa 1).
- `progress/decisions.md` — DEC-044 (estructura storage), DEC-047 (tenant_id), DEC-052
  (responsable_pagos).
- `progress/tasks.md` — T-030 (ITO), T-031 (pasarela de pagos), T-170 (esta guía), T-171
  (construir Capa 1).
- **Apéndice A** — bocetos SQL heredados de `modelo.md` (ya absorbidos; el archivo original
  puede eliminarse).

---

## Apéndice A — Bocetos SQL heredados para la Capa 4 (knowledge base)

> Piezas concretas reutilizables absorbidas desde `modelo.md` (schema de knowledge base de otro
> harness). Se conservan aquí como **punto de partida** para construir la Capa 4 de FARO. **Son
> bocetos de referencia, no DDL final** — las tablas `decisions`/`lessons` deben adaptarse al
> dominio FARO (por harness, no por BRD/BDD/SAD) cuando llegue su momento. Con esto absorbido,
> `modelo.md` ya no contiene información única.

### A.1 Extensiones y configuración FTS en español

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";   -- UUIDs
CREATE EXTENSION IF NOT EXISTS "vector";       -- pgvector: búsqueda semántica
CREATE EXTENSION IF NOT EXISTS "unaccent";     -- FTS sin tildes (español)

-- Configuración FTS en español con unaccent
CREATE TEXT SEARCH CONFIGURATION spanish_unaccent (COPY = spanish);
ALTER TEXT SEARCH CONFIGURATION spanish_unaccent
  ALTER MAPPING FOR hword, hword_part, word WITH unaccent, spanish_stem;
```

> En Supabase, `pgvector` viene instalado por defecto (igual conviene el `CREATE EXTENSION`
> idempotente).

### A.2 Patrón de columna generada para FTS (tsvector STORED)

```sql
-- FTS generado automáticamente sobre los campos de búsqueda (cero mantenimiento manual)
search_tsv  TSVECTOR GENERATED ALWAYS AS (
    to_tsvector('spanish_unaccent',
        title || ' ' || decision || ' ' || reason || ' ' ||
        COALESCE(when_to_reuse, '') || ' ' || COALESCE(motivation, '')
    )
) STORED
-- Índice: CREATE INDEX idx_xxx_fts ON tabla USING GIN(search_tsv);
```

### A.3 Patrón de embedding semántico (pgvector + HNSW)

```sql
-- Columna de embedding (dimensión 1536 para text-embedding-3-small)
embedding   VECTOR(1536)

-- Índice HNSW para búsqueda semántica aproximada (mejor que IVFFlat para < 1M filas)
CREATE INDEX idx_xxx_embedding ON tabla
    USING HNSW (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
```

Filtrado exacto por tags (la capa más rápida, microsegundos):

```sql
CREATE INDEX idx_xxx_tags ON tabla USING GIN(tags);  -- WHERE tags @> ARRAY['nextjs']
```

**Tres capas de búsqueda** por entidad consultable: (1) tags exactos (GIN), (2) FTS
(`tsvector` + GIN), (3) semántica (vector + HNSW). El agente combina según necesidad —
tags como pre-filtro, FTS o vector como ranking.

### A.4 Esqueleto de tabla de conocimiento (a adaptar al dominio FARO)

```sql
-- Plantilla orientativa. En FARO: una entrada por decisión/lección de cada harness,
-- con harness_id en vez de project_id/document_type de BRD/BDD/SAD.
CREATE TABLE decisions (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    harness_id    TEXT NOT NULL,                 -- p. ej. '010_discovery' (adaptación FARO)
    dec_id        TEXT NOT NULL,                 -- 'DEC-047'
    title         TEXT NOT NULL,
    decision      TEXT NOT NULL,
    reason        TEXT NOT NULL,
    when_to_reuse TEXT,
    reusability   TEXT NOT NULL CHECK (reusability IN ('Alta','Media','Baja')),
    tags          TEXT[] NOT NULL DEFAULT '{}',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    search_tsv    TSVECTOR GENERATED ALWAYS AS (
        to_tsvector('spanish_unaccent', title || ' ' || decision || ' ' || reason)
    ) STORED,
    embedding     VECTOR(1536)
);
-- + índices GIN(tags), GIN(search_tsv), HNSW(embedding) de A.2/A.3.
-- Tabla 'lessons' análoga (rejection_cause, rule_for_future, etc.).
```

### A.5 Migración local → cloud (Supabase / cualquier Postgres gestionado)

El schema es **PostgreSQL estándar** → portable sin cambios a Supabase/Neon/Railway/Render.
Solo cambia `DATABASE_URL`; no hay conversión de tipos ni reescritura de queries.

```bash
# 1. Dump desde local
pg_dump --no-owner --no-acl --format=plain -f knowledge_dump.sql \
  postgresql://localhost:5432/faro_knowledge

# 2. Restaurar en el proveedor cloud
psql "postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres" -f knowledge_dump.sql
```

Patrón de migración de datos (Python): parsear los `decisions_library.md` / `lessons_learned.md`
de cada harness, insertar filas y **generar el embedding una sola vez** por fila
(`text-embedding-3-small`, dimensión 1536). A partir de ahí, el embedding se genera al archivar
cada nueva entrada.

### A.6 Notas operacionales por proveedor (resumen)

- **Supabase:** pgvector preinstalado; PostgREST da API HTTP sobre cada tabla (los agentes
  podrían consultar sin driver SQL — ver decisión abierta D-E); RLS activado por defecto (para
  uso interno: `CREATE POLICY "allow all" ... USING (true)`, o por tenant si multi-tenancy);
  pgBouncer incluido; plan gratuito 500 MB (~80.000 filas con `vector(1536)` ≈ 6 KB/fila).
- **Neon:** branching de BD nativo (útil para testear migraciones); serverless con cold start
  ~500 ms (irrelevante para agentes).
- **Railway / Render:** Postgres estándar; `pgvector` puede requerir paso manual según imagen.
- **Multi-tenant:** en FARO el aislamiento es por `tenant_id` (no `organization_id` opcional como
  en el schema heredado). RLS por tenant: `CREATE POLICY "tenant_isolation" ON tabla USING
  (tenant_id = current_setting('app.tenant_id'))`.

---

*Guía base v1.0 — Persistencia Supabase — FARO / Sabbia Solutions & Software (Triple S)*

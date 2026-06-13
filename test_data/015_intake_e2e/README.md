# Corrida e2e — Cadena 010 Discovery → 015 Intake

Material de prueba para validar **end-to-end** la cadena de los dos primeros harnesses
de FARO con un cliente ficticio consistente: **Conservas del Pacífico S.A.S.** (Cali,
Colombia) — fabricante B2B de conservas y alimentos procesados, escala mediana (M/L).

Esta carpeta es **repo fuente / staging**. La corrida real se ejecuta en una carpeta de
prueba dedicada (`Test_Forecaster/Test_NNN/`, arquitectura de dos terminales, LEC-053).

---

## Contenido de esta carpeta

| Archivo | Qué es | En qué paso se usa |
|---|---|---|
| `brief.md` | Brief de contexto del cliente (input del Discovery) | **010** — va a `800_inputs/brief.md` |
| `orders.csv` | Histórico de pedidos — Esquema 1 (entrega principal) | **015** — va a `800_inputs/orders.csv` |
| `orders_sin_cantidad.csv` | Pedidos SIN columna de cantidad (mini-corrida de rechazo) | **015** — opcional, para probar el veto D2 |
| `_build_dataset.py` | Generador reproducible de los dos CSV (semilla fija) | — (regenera los CSV byte-idénticos) |

Los CSV se generan con `python test_data/015_intake_e2e/_build_dataset.py`.

---

## Convención de carpetas en la corrida (Fase 1)

> **Convención del proyecto (Fase 1):** el operador deja **todos** los archivos de entrada
> del cliente en `800_inputs/`. Es el único "buzón de entrada" del proyecto, tanto para el
> brief del 010 como para los datos del 015. (El `brief/015_intake.md:56` dice "el operador
> deja el archivo en la carpeta del tenant"; aquí lo precisamos como `800_inputs/`.)

```
Test_NNN/
├── 800_inputs/
│   ├── brief.md      ← lo lee el 010 (Discovery)
│   ├── orders.csv    ← lo lee el 015 (Intake) — Esquema 1
│   └── inventory.csv ← (opcional) Esquema 2, si el cliente lo entrega
├── 010_discovery/    ← lo crea el 010 (deliverables, client_config, evento)
├── 600_persistence/  ← estado + eventos
└── 1000_storage_local/tenants/{tenant_id}/1000_data/005_bronze/
                       ← el 015 ESCRIBE aquí el Bronce (copia bit-exacta, intocable)
```

⚠️ **Nunca** pegar `orders.csv` directamente en `005_bronze/`. Esa carpeta es el Bronce y la
**escribe el 015** copiando el archivo de `800_inputs/` (bit-exacto, write-once + SHA-256).
Ponerlo a mano rompe el modelo medallón.

---

## Receta de la corrida

### Paso 1 — Harness 010 Discovery
1. Desplegar el 010 en `Test_NNN/` y copiar `brief.md` → `Test_NNN/800_inputs/brief.md`.
2. Correr el Discovery (`/faro-run` o el comando equivalente).
3. Resultado esperado: el 010 produce `client_config` (≈ 3 años de historial declarado,
   ~350 SKUs, ~45 clientes → categoría M/L), los deliverables de onboarding y emite el
   evento `onboarding_discovery_complete`. El evaluador C aprueba.

### Paso 2 — Harness 015 Intake (entrega principal)
1. Desplegar el 015 (modelo "switch": instala el 015, poda el 010 — su handoff ya está en disco).
2. Copiar `orders.csv` → `Test_NNN/800_inputs/orders.csv`.
3. Correr el Intake. El governor arma el Sprint Contract con
   `snapshot_esquema1: 800_inputs/orders.csv`; aprobar el contrato.
4. Resultado esperado (verificado contra los módulos del pipeline — ver tabla abajo):
   `EXECUTION_COMPLETE`, Bronce bit-exacto + SHA-256 en manifest, evento `intake_complete`
   como último artefacto (dispara 020 ‖ 025), C aprueba ≥ 0.80.

### Paso 3 — (opcional) Mini-corrida de rechazo
1. Copiar `orders_sin_cantidad.csv` → `800_inputs/` y correr el Intake apuntando a él.
2. Resultado esperado: `REJECTED_STRUCTURE` (falta `cantidad_solicitada`), `intake_rejection.json`,
   **sin Bronce ni evento** (veto D2). El cliente "re-entrega".

---

## Resultados esperados (medidos con los módulos reales del pipeline)

Validación ejecutada el 2026-06-13 sobre los CSV de esta carpeta:

### `orders.csv` (Esquema 1 — entrega principal)
| Dimensión | Valor medido |
|---|---|
| Formato | `csv` · encoding `cp1252` · delimitador `;` · no corrupto · no ambiguo |
| Tamaño | 4.050 filas × 10 columnas · 406.890 bytes |
| Canario de acentos | sobrevive (`Categoría`, `Atún`, `Champiñones`, `Bogotá`…) |
| Estructura (GATE) | **aprobado** — 4 mínimos presentes |
| Ideales | 9 presentes / 8 faltantes (déficit que alimenta el ISD del 020) |
| Errores de tipo | `cantidad_solicitada = 40` (cantidades negativas sembradas) |
| Duplicados internos | **50** (clave `fecha_pedido + id_cliente + id_producto`) |
| Rango | real **2,20 años** (2024-01-08 → 2026-03-20) vs **3 declarados** → discrepancia 26,8% → **warning** |

> Las 40 negativas, los 50 duplicados y el warning de rango **se cuentan pero NO detienen**
> el pipeline (P3/P4/P5 alimentan el ISD; no son vetos). Bronce se escribe igual y el evento
> se emite. Es el comportamiento de diseño.

### `orders_sin_cantidad.csv` (mini-corrida de rechazo)
| Dimensión | Valor medido |
|---|---|
| Estructura (GATE) | **rechazado** — falta el mínimo `cantidad_solicitada` |
| Efecto esperado en el 015 | `REJECTED_STRUCTURE`, sin Bronce ni evento (veto D2) |

---

## ¿Y si el cliente entrega dos o más archivos? (Esquema 1 + Esquema 2)

El 015 soporta **exactamente dos esquemas independientes** por entrega:

| | **Esquema 1 — Pedidos** | **Esquema 2 — Producción / Inventario** |
|---|---|---|
| ¿Obligatorio? | **Sí** | **No** (opcional) |
| Mínimos | `fecha_pedido, id_cliente, id_producto, cantidad_solicitada` | `fecha, id_producto, cantidad_producida, stock_disponible, costo_unitario, stock_minimo` |
| Archivo típico | `orders.csv` | `inventory.csv` |
| Si falta un mínimo | **rechazo de TODA la entrega** (`REJECTED_STRUCTURE`, sin Bronce ni evento — veto D2) | **NO bloquea** — se omite, el Esquema 1 sigue su curso |
| Bronce | `orders_{mode}_{delivery_id}.{ext}` | `inventory_{mode}_{delivery_id}.{ext}` |

**Claves del modelo (DEC-057):**
- Cada archivo es un **snapshot independiente** → su **propio** archivo Bronce, su **propio**
  SHA-256 en `_manifest.json`. No se mezclan ni se cruzan en la ingesta (eso ocurre aguas abajo).
- El Esquema 2 **nunca** tumba la entrega. El pipeline registra su estado:
  - `NOT_EXPECTED` — `client_config.tiene_esquema2 = false` (el cliente no lo entrega).
  - `EXPECTED_NOT_RECEIVED` — se esperaba pero falta / está vacío / corrupto / ambiguo.
  - `ESTRUCTURA_INVALIDA` — llegó pero le falta un mínimo (se omite, sin Bronce, no bloquea).
  - `CREATED` — ingerido, Bronce escrito.
- **Asimetría central:** un mínimo faltante en Pedidos = freno duro; en Inventario = se salta y sigue.

**¿Y si entrega MÁS de dos archivos** (p. ej. dos archivos de pedidos, o un tercer tipo)**?**
El 015 procesa **un snapshot por esquema y por entrega**. Varios archivos del mismo tipo se
resuelven *aguas arriba* (el adaptador de fuente los consolida en un único snapshot antes de
tocar el 015) o como **entregas incrementales** separadas (cada una añade su propio Bronce +
manifest, con deduplicación lógica del histórico). Un tercer tipo de archivo que no sea Pedidos
ni Inventario **no tiene esquema en el 015** y no se ingiere.

**En esta prueba:** el cliente entrega **solo Pedidos** (`tiene_esquema2 = false` → `NOT_EXPECTED`).
Si más adelante quisiéramos ejercitar el Esquema 2, se añade un `inventory.csv` consistente y se
marca `tiene_esquema2 = true` en el `client_config` — fuera del alcance actual.

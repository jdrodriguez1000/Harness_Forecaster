# Fixtures del Harness 015 Intake — PASO 12 (E9)

Batería de archivos de prueba que ejercita el pipeline P1→P8 contra los casos
reales que rompen una ingesta. Es la mayor palanca de calidad del 015 (DEC-057,
decisión 3): cada fixture tiene una **expectativa documentada** que el test
`tests/test_fixtures.py` verifica de punta a punta.

Los archivos se generan de forma reproducible con `python tests/fixtures/_build_fixtures.py`
(los binarios `.xlsx` usan openpyxl; el `.xls` usa xlwt solo en build-time — el
runtime lee `.xls` con xlrd). **No editar los binarios a mano.**

## Expectativas por categoría

### Estructura (GATE P2 — veto D2)

| Fixture | Esperado |
|---|---|
| `missing_id_producto.csv` | **REJECTED_STRUCTURE**: falta `id_producto`; `intake_rejection.json`, sin Bronce ni evento |
| `extra_columns.csv` | Aprobado; 4 mínimos + 3 ideales presentes (`fecha_entrega_solicitada`, `estado_pedido`, `ciudad`) registrados; columna no-ideal ignorada |
| `header_row_3.xlsx` | Aprobado; cabecera detectada en **fila 3** (dos filas vacías arriba) |

### Formato (P1 — detección)

| Fixture | Esperado |
|---|---|
| `orders_comma_utf8.csv` | tipo `csv`, delimitador `,`, encoding `utf-8` |
| `orders_semicolon.csv` | delimitador `;` |
| `orders_pipe.csv` | delimitador `\|` |
| `orders_utf8sig_bom.csv` | encoding `utf-8-sig` (BOM) |
| `cp1252_acentos.csv` | encoding `cp1252`; **acentos intactos byte-a-byte** (el canario: `Pingüino`, `Camión`, `Categoría`, `Limón`) |
| `header_row_1.xlsx` | tipo `xlsx`, hoja `Datos`, cabecera fila 1 |
| `legacy.xls` | tipo `xls` (OLE2), hoja `Datos`, cabecera fila 1, ingiere por el pipeline |
| `multi_sheet.xlsx` | **PENDING_OPERATOR_INPUT**: multi-hoja sin huella → escalamiento, sin Bronce |

### Tipos (P3 — cuenta, NUNCA detiene — D3)

| Fixture | Esperado |
|---|---|
| `cantidad_negativa.csv` | 5 errores en `cantidad_solicitada` (3 negativas + 2 no-numéricas); 6 filas conservadas |
| `fechas_3_formatos.csv` | 0 errores de fecha (`YYYY-MM-DD`, `DD/MM/YYYY`, `DD-MM-YYYY` parseables) |
| `id_cliente_vacio.csv` | 2 errores en `id_cliente` (vacío + solo-espacios) |

### Duplicados (P4 — D4)

| Fixture | Esperado |
|---|---|
| `dup_internos_batch.csv` | 6 claves únicas + 4 duplicadas = 10 filas; 4 duplicados internos contados; **no elimina filas** (batch) |
| `incremental_repetidos.csv` | 6 claves; con Bronce previo de C1..C3 → 3 nuevas, 3 excluidas (incremental) |

### Rango (P5)

| Fixture | Esperado |
|---|---|
| `historial_34_anios.csv` | rango real ≈ 3.4 años; declarado 2 → `warning=True`, también en `warnings` |

### Bronce (P6 — bit-exacto + idempotencia — veto D5)

| Fixture | Esperado |
|---|---|
| `bronce_bitexacto.csv` | Bronce byte-idéntico a la entrada; re-correr no reescribe (`rewritten=False`) |

### Corrupto / vacío (P1 — rechazo inmediato)

| Fixture | Esperado |
|---|---|
| `vacio.csv` | 0 bytes → **WORKER_FAILED**, sin Bronce ni evento |
| `binario_corrupto.bin` | bytes nulos → `corrupto` → **WORKER_FAILED**, sin Bronce ni evento |

**Total: 20 fixtures.**

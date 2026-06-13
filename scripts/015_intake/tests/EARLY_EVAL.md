# Evaluación Temprana (E9) — Harness 015 Intake — PASO 15

**Fecha:** 2026-06-13 (sesión 42)
**Evaluador:** Instancia C aplicando `intake-rubric` (7 dimensiones, gate de construcción ≥ 0.7)
**Gate de construcción:** ≥ 0.7 para continuar · **Gate operacional** (corrida real): ≥ 0.80
**Veredicto:** **APPROVED** — score global **1.00**, sin vetos.

> Este es el equivalente en el **repo fuente** del campo `execution-state.json.early_eval` que
> B persiste en runtime (terminal de prueba, LEC-053). Documenta que la batería de fixtures (E9,
> PASO 12) y los módulos críticos (`schema_validator` PASO 6, `bronze_writer` PASO 9) satisfacen
> la rúbrica de fidelidad **antes** de la corrida e2e (PASO 16).

## Cómo se ejecutó

1. `python -m pytest -q` desde `scripts/015_intake/` → **85 tests verdes** (incluye las 20
   expectativas de fixtures de `test_fixtures.py`).
2. Camino feliz sobre el canario `cp1252_acentos.csv` ejecutado por `run_intake`, con
   verificación **independiente** de la evidencia que exige la rúbrica (recálculo de SHA-256,
   comparación byte-a-byte contra el snapshot, inspección de reporte y evento).

## Scoring por dimensión

| Dim | Dimensión | Evidencia (fixture / verificación independiente) | Score |
|----|-----------|--------------------------------------------------|:----:|
| D1 | Detección de formato | `cp1252_acentos.csv`: tipo `csv`, delimitador `;`, encoding `cp1252`; acentos (`Pingüino`/`Camión`) **intactos byte-a-byte** en Bronce | 1.0 |
| D2 ⚠️ | Estructura (GATE) | `missing_id_producto.csv` → `REJECTED_STRUCTURE`, `intake_rejection.json`, **sin Bronce**; `extra_columns.csv` aceptado con ideales registrados; matching canónico sin substring (FP=FN=0) | 1.0 |
| D3 | Tipos y conteos | `cantidad_negativa.csv`: 5 errores, 6 filas **conservadas**; `id_cliente_vacio.csv`: 2 errores; `fechas_3_formatos.csv`: 0 errores. Nunca detiene ni elimina filas | 1.0 |
| D4 | Duplicados | `dup_internos_batch.csv`: 4 duplicados contados, **no eliminados** (batch); `incremental_repetidos.csv`: 3 nuevas / 3 excluidas (incremental) | 1.0 |
| D5 ⚠️ | Fidelidad/inmutabilidad Bronce | Bronce **byte-idéntico** a la entrada; SHA-256 recalculado por C `76556b88…928d` == manifest; re-corrida `rewritten=False` (write-once) | 1.0 |
| D6 | Completitud de reportes | `intake_report` con `format`/`schema1`/`warnings`; warning de rango en `historial_34_anios.csv`; `files` JSONB con hash por archivo | 1.0 |
| D7 ⚠️ | Evento emitido | `intake_complete` como **último** artefacto; `next_harnesses:[020_diagnosis,025_refinery]`; `tenant_id` coincide; `event_path` existe | 1.0 |

**Fórmula:** (1+1+1+1+1+1+1)/7 = **1.00**. Ningún veto (D2/D5/D7) activo.

## Hallazgo de higiene detectado y corregido en este paso

- **`test_existen_20_fixtures` contaba 21 archivos** porque el `.gitattributes` del directorio de
  fixtures (intencional — protege los fixtures byte-sensibles de la normalización de Git, crítico
  para el canario cp1252 y la bit-exactitud) no estaba excluido del conteo. Corregido el test para
  excluir dotfiles. No es un defecto del pipeline ni afecta la fidelidad; es higiene de test.

## Conclusión

El score (1.00) supera el gate de construcción (≥ 0.7) con holgura. **Se continúa al PASO 16**
(corrida e2e en `Test_Forecaster/Test_NNN/`). El ajuste menor diferido **T-184** (`type_validator`
no cuenta celdas numéricas vacías como error) sigue abierto y **no** afecta este veredicto (no
toca Bronce ni vetos; a lo sumo subestima levemente un conteo de D3, que se mantuvo en 1.0 porque
los fixtures evaluados no ejercitan ese caso).

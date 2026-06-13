# Código del Harness 015 Intake — Pipeline de Ingesta

Módulos de código del pipeline determinístico P1→P8 del harness 015 Intake, construidos con **TDD real** (RED → GREEN → REFACTOR). Ver el plan de construcción en `plan/015_intake.md` y el diseño en `brief/015_intake.md`.

> **Arquitectura de dos terminales (LEC-053).** Este código y sus tests se **construyen y verifican aquí** (repo fuente `Harness_Forecaster`). Las carpetas de estado runtime (`600_persistence/`, `605_eval/`, `610_knowledge/`, `615_changes/`) y el working dir `015_intake/` NO viven en el repo fuente — las crea el ritual E10-A durante la corrida e2e en la terminal de prueba (`Test_Forecaster/Test_NNN/`).

## Estructura

```
scripts/015_intake/
  pipeline/              ← módulos del pipeline (un módulo por responsabilidad)
    source_adapter.py    ← P1 recepción (Fase 1: adaptador manual/operador)
    format_detector.py   ← P1 detección de formato (CSV delim/encoding, Excel hoja/cabecera)
    schema_validator.py  ← P2 GATE de estructura (campos mínimos Esquema 1 / 2)
    type_validator.py    ← P3 validación de tipos (cuenta, no detiene)
    range_evaluator.py   ← P5 rango temporal vs historial declarado
    deduplicator.py      ← P4 duplicados por clave compuesta (batch/incremental)
    bronze_writer.py     ← P6 Bronce write-once + SHA-256 + manifest (veto D5)
    report_builder.py    ← P7 intake_report.json + intake_log
    pipeline.py          ← orquestación P1→P8 + P8 emisión del evento (el intake-processor)
  tests/                 ← tests unitarios (pytest) — uno por módulo + test_pipeline.py
    fixtures/            ← ~20 archivos rotos/válidos (E9) + README con expectativas
```

Las plantillas y schemas JSON de referencia viven en `templates/015_intake/`.

## Cómo correr los tests

```bash
pip install pandas openpyxl xlrd chardet pytest
cd scripts/015_intake
pytest -q
```

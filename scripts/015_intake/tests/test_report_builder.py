"""Tests del PASO 10 — report_builder.py (P7).

Contrato (plan/015_intake.md, PASO 10):
  build_report(...) -> dict (intake_report.json)
  build_intake_log(...) -> dict (fila intake_log, _pendiente_supabase: true)

Consolida P1–P6: formato/encoding/delimitador, conteos de filas, campos ideales
faltantes, errores de tipo, duplicados, rango temporal, warnings, y el `files`
JSONB. Conforme a templates/015_intake/schemas/*.json. El warning de rango NUNCA
se omite si P5 lo detectó (ancla 0.8 del brief).
"""

import json
from pathlib import Path

import pandas as pd

from pipeline.bronze_writer import write_bronze
from pipeline.format_detector import FormatSpec
from pipeline.range_evaluator import evaluate_range
from pipeline.report_builder import build_intake_log, build_report
from pipeline.schema_validator import validate_structure
from pipeline.type_validator import validate_types

_SCHEMAS = Path(__file__).resolve().parents[3] / "templates" / "015_intake" / "schemas"


def _df():
    return pd.DataFrame({
        "fecha_pedido": ["2021-01-01", "2022-07-15", "2024-06-01"],  # ~3.4 años
        "id_cliente": ["C1", "C2", ""],                              # 1 vacío
        "id_producto": ["P1", "P2", "P3"],
        "cantidad_solicitada": [5, -2, 3],                           # 1 negativo
    })


def _report(**over):
    df = _df()
    args = dict(
        tenant_id="t1", delivery_id="20260101", mode="batch",
        format_spec=FormatSpec(tipo="csv", delimitador=";", encoding="cp1252"),
        struct_result=validate_structure(df, 1),
        type_result=validate_types(df, 1),
        range_result=evaluate_range(df, anios_declarados=2),
        dup_internos=3, dup_vs_bronce=0,
    )
    args.update(over)
    return build_report(**args)


def _conforma(template, produced):
    """Toda clave del template (salvo '_description') existe en lo producido."""
    for k, v in template.items():
        if k == "_description":
            continue
        assert k in produced, f"falta clave: {k}"
        if isinstance(v, dict):
            _conforma(v, produced[k])
    return True


# --- intake_report ---

def test_report_consolida_conteos():
    rep = _report()
    assert rep["tenant_id"] == "t1"
    assert rep["format"]["encoding"] == "cp1252"
    assert rep["format"]["delimitador"] == ";"
    assert rep["schema1"]["rows"] == 3
    assert rep["schema1"]["errores_tipo"]["id_cliente"] == 1
    assert rep["schema1"]["errores_tipo"]["cantidad_solicitada"] == 1
    assert rep["schema1"]["duplicados"]["internos"] == 3
    assert rep["schema1"]["rango_temporal"]["fecha_min"] == "2021-01-01"


def test_report_warning_de_rango_no_se_omite():
    rep = _report()
    assert rep["rango_declarado_vs_real"]["warning"] is True
    assert rep["rango_declarado_vs_real"]["real_anios"] is not None
    # el warning aparece también en la lista de warnings legible
    assert any("rango" in w.lower() for w in rep["warnings"])


def test_report_huella_reutilizada():
    rep = _report(format_spec=FormatSpec(tipo="csv", delimitador=";", encoding="cp1252", fuente="huella"))
    assert rep["format"]["huella_reutilizada"] is True


def test_schema2_expected_not_received_no_bloquea():
    rep = _report(schema2={"status": "EXPECTED_NOT_RECEIVED", "rows": 0,
                           "campos_minimos_faltantes": [], "errores_tipo": {}})
    assert rep["schema2"]["status"] == "EXPECTED_NOT_RECEIVED"


def test_report_conforma_al_schema():
    rep = _report()
    template = json.loads((_SCHEMAS / "intake_report_schema.json").read_text(encoding="utf-8"))
    assert _conforma(template, rep)


# --- intake_log ---

def test_intake_log_files_uno_por_archivo(tmp_path):
    bf1 = write_bronze(b"a;b\n1;2\n", str(tmp_path), mode="batch", delivery_id="20260101",
                       esquema=1, tenant_id="t1", rows=1,
                       rango={"fecha_min": "2026-01-01", "fecha_max": "2026-01-02"})
    bf2 = write_bronze(b"c;d\n3;4\n", str(tmp_path), mode="batch", delivery_id="20260101",
                       esquema=2, tenant_id="t1", rows=1)
    log = build_intake_log(tenant_id="t1", delivery_id="20260101", mode="batch",
                           bronze_files=[bf1, bf2], report_path=str(tmp_path / "intake_report.json"))
    assert log["_pendiente_supabase"] is True
    assert len(log["files"]) == 2
    paths = {f["path"] for f in log["files"]}
    assert bf1.path in paths and bf2.path in paths
    f1 = next(f for f in log["files"] if f["path"] == bf1.path)
    assert f1["sha256"] == bf1.sha256
    assert f1["date_range"]["min"] == "2026-01-01"


def test_intake_log_conforma_al_schema(tmp_path):
    bf = write_bronze(b"a;b\n1;2\n", str(tmp_path), mode="batch", delivery_id="20260101",
                      esquema=1, tenant_id="t1", rows=1)
    log = build_intake_log(tenant_id="t1", delivery_id="20260101", mode="batch",
                           bronze_files=[bf], report_path="r.json")
    template = json.loads((_SCHEMAS / "intake_log_schema.json").read_text(encoding="utf-8"))
    # files es una lista de objetos; comprobar el primer elemento contra el template
    for k, v in template.items():
        if k in ("_description", "files"):
            continue
        assert k in log
    assert isinstance(log["files"], list) and log["files"]
    for k in template["files"][0]:
        assert k in log["files"][0]

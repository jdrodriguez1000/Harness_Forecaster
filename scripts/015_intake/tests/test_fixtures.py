"""Tests del PASO 12 — batería de fixtures (E9).

Ejercita los 20 fixtures de tests/fixtures/ contra el pipeline, verificando la
expectativa documentada en tests/fixtures/README.md. Es la mayor palanca de
calidad del 015 (DEC-057, decisión 3): casos reales que rompen una ingesta.
"""

import io
import json
import os

import pandas as pd
import pytest

from pipeline.deduplicator import (
    count_internal_duplicates,
    diff_against_bronze,
)
from pipeline.format_detector import detect_format
from pipeline.pipeline import Persistence, run_intake
from pipeline.range_evaluator import evaluate_range
from pipeline.schema_validator import validate_structure
from pipeline.type_validator import validate_types

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def _bytes(nombre):
    with open(os.path.join(FIXTURES, nombre), "rb") as fh:
        return fh.read()


def _spec(nombre):
    return detect_format(_bytes(nombre), nombre)


def _df_csv(nombre, sep, encoding="utf-8"):
    return pd.read_csv(io.StringIO(_bytes(nombre).decode(encoding)), sep=sep, dtype=str)


def _pers(tmp_path):
    return Persistence(bronze_dir=str(tmp_path / "005_bronze"), events_dir=str(tmp_path / "events"))


def _cfg(**kw):
    base = {"tenant_id": "t1", "mode": "batch", "tiene_esquema2": False,
            "historial_declarado_anios": 1, "delivery_id": "20240101"}
    base.update(kw)
    return base


# --- los 20 fixtures existen ---

def test_existen_20_fixtures():
    # Excluir auxiliares: prefijo "_" (generador), README y dotfiles como .gitattributes
    # (este último protege los fixtures byte-sensibles de la normalización de Git).
    archivos = [f for f in os.listdir(FIXTURES)
                if not f.startswith("_") and not f.startswith(".") and f != "README.md"]
    assert len(archivos) == 20


# --- Estructura ---

def test_missing_id_producto_rechazo(tmp_path):
    res = run_intake(_cfg(), os.path.join(FIXTURES, "missing_id_producto.csv"), _pers(tmp_path))
    assert res.estado == "REJECTED_STRUCTURE"
    assert "id_producto" in json.loads(open(res.rejection_path, encoding="utf-8").read())["campos_minimos_faltantes"]
    assert res.bronze_files == []
    assert res.event_path is None


def test_extra_columns_aprobado_con_ideales():
    df = _df_csv("extra_columns.csv", ";", "cp1252")
    r = validate_structure(df, 1)
    assert r.aprobado is True
    assert "ciudad" in r.campos_ideales_presentes
    assert "estado_pedido" in r.campos_ideales_presentes
    assert "fecha_entrega_solicitada" in r.campos_ideales_presentes


def test_header_row_3_cabecera_fila_3():
    spec = _spec("header_row_3.xlsx")
    assert spec.tipo == "xlsx"
    assert spec.fila_cabecera == 3


# --- Formato ---

def test_delimitadores_y_encodings():
    assert _spec("orders_comma_utf8.csv").delimitador == ","
    assert _spec("orders_comma_utf8.csv").encoding == "utf-8"
    assert _spec("orders_semicolon.csv").delimitador == ";"
    assert _spec("orders_pipe.csv").delimitador == "|"
    assert _spec("orders_utf8sig_bom.csv").encoding == "utf-8-sig"


def test_cp1252_acentos_intactos():
    spec = _spec("cp1252_acentos.csv")
    assert spec.encoding == "cp1252"
    texto = _bytes("cp1252_acentos.csv").decode("cp1252")
    for token in ("Pingüino", "Camión", "Categoría", "Limón"):
        assert token in texto


def test_header_row_1_xlsx():
    spec = _spec("header_row_1.xlsx")
    assert spec.tipo == "xlsx"
    assert spec.hoja == "Datos"
    assert spec.fila_cabecera == 1


def test_legacy_xls_ingiere(tmp_path):
    spec = _spec("legacy.xls")
    assert spec.tipo == "xls"
    assert spec.ambiguo is False
    res = run_intake(_cfg(), os.path.join(FIXTURES, "legacy.xls"), _pers(tmp_path))
    assert res.estado == "EXECUTION_COMPLETE"
    assert res.report["format"]["tipo"] == "xls"


def test_multi_sheet_escala(tmp_path):
    res = run_intake(_cfg(), os.path.join(FIXTURES, "multi_sheet.xlsx"), _pers(tmp_path))
    assert res.estado == "PENDING_OPERATOR_INPUT"
    assert res.escalation["tipo"] == "excel"
    assert res.bronze_files == []


# --- Tipos (cuenta, no detiene) ---

def test_cantidad_negativa_cuenta_5_no_elimina():
    df = _df_csv("cantidad_negativa.csv", ";")
    r = validate_types(df, 1)
    assert r.errores["cantidad_solicitada"] == 5  # 3 negativas + 2 no-numéricas
    assert r.filas_evaluadas == 6  # ninguna fila eliminada (5 con error + 1 válida)


def test_fechas_3_formatos_cero_errores():
    df = _df_csv("fechas_3_formatos.csv", ";")
    assert validate_types(df, 1).errores["fecha_pedido"] == 0


def test_id_cliente_vacio_cuenta_2():
    df = _df_csv("id_cliente_vacio.csv", ";")
    assert validate_types(df, 1).errores["id_cliente"] == 2


# --- Duplicados ---

def test_dup_internos_batch_cuenta_4_no_elimina():
    df = _df_csv("dup_internos_batch.csv", ";")
    assert count_internal_duplicates(df) == 4
    assert len(df) == 10  # 6 claves únicas + 4 duplicadas, ninguna eliminada


def test_incremental_excluye_existentes(tmp_path):
    # Bronce previo con C1..C3 (releído por el deduplicador)
    bronze_dir = tmp_path / "005_bronze"
    bronze_dir.mkdir()
    prev = "fecha_pedido;id_cliente;id_producto\n2024-01-01;C1;P1\n2024-01-01;C2;P1\n2024-01-01;C3;P1\n"
    (bronze_dir / "orders_incremental_20240101.csv").write_bytes(prev.encode("utf-8"))
    manifest = {"tenant_id": "t1", "entregas": [{
        "delivery_id": "20240101", "mode": "incremental",
        "archivo": "orders_incremental_20240101.csv", "esquema": 1, "sha256": "x", "rows": 3,
    }]}
    manifest_path = bronze_dir / "_manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    df = _df_csv("incremental_repetidos.csv", ";")
    df_nuevos, n_excluidos = diff_against_bronze(df, str(manifest_path))
    assert n_excluidos == 3
    assert len(df_nuevos) == 3


# --- Rango ---

def test_historial_34_anios_warning():
    df = _df_csv("historial_34_anios.csv", ";")
    r = evaluate_range(df, anios_declarados=2)
    assert r.warning is True
    assert r.anios_real > 3.0


# --- Bronce: bit-exacto + idempotencia ---

def test_bronce_bitexacto_e_idempotente(tmp_path):
    snap = os.path.join(FIXTURES, "bronce_bitexacto.csv")
    pers = _pers(tmp_path)
    r1 = run_intake(_cfg(), snap, pers)
    assert open(r1.bronze_files[0].path, "rb").read() == _bytes("bronce_bitexacto.csv")
    assert r1.bronze_files[0].rewritten is True
    r2 = run_intake(_cfg(), snap, pers)
    assert r2.bronze_files[0].rewritten is False  # no reescribe


# --- Corrupto / vacío ---

def test_vacio_falla(tmp_path):
    res = run_intake(_cfg(), os.path.join(FIXTURES, "vacio.csv"), _pers(tmp_path))
    assert res.estado == "WORKER_FAILED"
    assert res.bronze_files == []
    assert res.event_path is None


def test_binario_corrupto_falla(tmp_path):
    res = run_intake(_cfg(), os.path.join(FIXTURES, "binario_corrupto.bin"), _pers(tmp_path))
    assert res.estado == "WORKER_FAILED"
    assert res.bronze_files == []
    assert res.event_path is None

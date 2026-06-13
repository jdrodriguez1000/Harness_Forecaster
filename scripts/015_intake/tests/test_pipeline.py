"""Tests del PASO 11 — pipeline.py (orquestación P1→P8) — TDD de integración.

Contrato (plan/015_intake.md, PASO 11):
  run_intake(client_config, snapshot_path, persistence) -> IntakeResult

Encadena los módulos en orden estricto y respeta los gates:
  - P1 (recepción + formato): vacío/corrupto -> WORKER_FAILED; ambiguo -> PENDING_OPERATOR_INPUT.
  - P2 GATE: falta un mínimo -> REJECTED_STRUCTURE + intake_rejection.json, SIN Bronce ni evento.
  - P3/P4/P5: cuentan, no detienen.
  - P6 Bronce bit-exacto + SHA-256 + manifest.
  - P7 intake_report.json + intake_log.
  - P8 evento intake_complete como ÚLTIMO artefacto; si algo falla antes -> sin evento.
"""

import io
import json
import os

import pandas as pd
import pytest
from openpyxl import Workbook

from pipeline.pipeline import Persistence, run_intake


# --- Helpers de fixtures sintéticos ---

def _orders_csv_bytes():
    """CSV ';' cp1252 con acentos (canario), 1 cantidad negativa -> 1 error de tipo."""
    filas = [
        "fecha_pedido;id_cliente;id_producto;cantidad_solicitada",
        "2024-01-01;Pingüino;Camión;5",
        "2024-06-01;C2;P2;3",
        "2025-01-01;C3;P3;-2",
    ]
    return ("\n".join(filas) + "\n").encode("cp1252")


def _orders_sin_cantidad_bytes():
    filas = [
        "fecha_pedido;id_cliente;id_producto",
        "2024-01-01;C1;P1",
    ]
    return ("\n".join(filas) + "\n").encode("cp1252")


def _multi_sheet_xlsx_bytes():
    wb = Workbook()
    wb.active.title = "S1"
    wb.active.append(["fecha_pedido", "id_cliente", "id_producto", "cantidad_solicitada"])
    wb.active.append(["2024-01-01", "C1", "P1", "5"])
    wb.create_sheet("S2")
    bio = io.BytesIO()
    wb.save(bio)
    return bio.getvalue()


def _escribir(tmp_path, nombre, data: bytes):
    p = tmp_path / nombre
    p.write_bytes(data)
    return str(p)


def _persistence(tmp_path):
    return Persistence(
        bronze_dir=str(tmp_path / "005_bronze"),
        events_dir=str(tmp_path / "events"),
    )


def _config(**overrides):
    base = {
        "tenant_id": "t1",
        "mode": "batch",
        "tiene_esquema2": False,
        "historial_declarado_anios": 1,
        "delivery_id": "20240101",
    }
    base.update(overrides)
    return base


# --- Camino feliz ---

def test_camino_feliz_emite_evento_como_ultimo_artefacto(tmp_path):
    snap = _escribir(tmp_path, "orders.csv", _orders_csv_bytes())
    pers = _persistence(tmp_path)
    res = run_intake(_config(), snap, pers)

    assert res.estado == "EXECUTION_COMPLETE"
    # Bronce bit-exacto a la entrada
    bf = res.bronze_files[0]
    assert os.path.basename(bf.path) == "orders_batch_20240101.csv"
    assert open(bf.path, "rb").read() == _orders_csv_bytes()
    # manifest, report, intake_log, evento existen
    assert os.path.isfile(res.manifest_path)
    assert os.path.isfile(res.report_path)
    assert os.path.isfile(res.intake_log_path)
    assert os.path.isfile(res.event_path)
    # evento con payload completo
    evento = json.loads(open(res.event_path, encoding="utf-8").read())
    assert evento["event"] == "intake_complete"
    assert evento["estado"] == "pendiente"
    assert evento["next_harnesses"] == ["020_diagnosis", "025_refinery"]
    assert evento["bronze_path"] == pers.bronze_dir
    assert evento["manifest_path"] == res.manifest_path
    assert evento["intake_report_path"] == res.report_path


def test_canario_acento_sobrevive_y_cuenta_tipos(tmp_path):
    snap = _escribir(tmp_path, "orders.csv", _orders_csv_bytes())
    res = run_intake(_config(), snap, _persistence(tmp_path))
    # acento intacto en Bronce
    assert "Pingüino" in open(res.bronze_files[0].path, "rb").read().decode("cp1252")
    # encoding/delimitador registrados
    assert res.report["format"]["encoding"] == "cp1252"
    assert res.report["format"]["delimitador"] == ";"
    # 1 cantidad negativa contada, sin detener
    assert res.report["schema1"]["errores_tipo"]["cantidad_solicitada"] == 1
    assert res.report["schema1"]["rows"] == 3


# --- Rechazo de estructura (GATE P2) ---

def test_falta_minimo_rechazo_estructura_sin_bronce_ni_evento(tmp_path):
    snap = _escribir(tmp_path, "orders.csv", _orders_sin_cantidad_bytes())
    pers = _persistence(tmp_path)
    res = run_intake(_config(), snap, pers)

    assert res.estado == "REJECTED_STRUCTURE"
    assert os.path.isfile(res.rejection_path)
    rej = json.loads(open(res.rejection_path, encoding="utf-8").read())
    assert "cantidad_solicitada" in rej["campos_minimos_faltantes"]
    # ni Bronce ni evento
    assert res.bronze_files == []
    assert res.event_path is None
    assert not os.path.isdir(pers.bronze_dir) or not any(
        f.startswith("orders_") for f in os.listdir(pers.bronze_dir)
    )


# --- Escalamiento (Excel multi-hoja sin huella) ---

def test_excel_multihoja_sin_huella_escala_sin_bronce(tmp_path):
    snap = _escribir(tmp_path, "orders.xlsx", _multi_sheet_xlsx_bytes())
    pers = _persistence(tmp_path)
    res = run_intake(_config(), snap, pers)

    assert res.estado == "PENDING_OPERATOR_INPUT"
    assert res.escalation is not None
    assert res.escalation["tipo"] == "excel"
    assert res.bronze_files == []
    assert res.event_path is None


# --- Esquema 2 esperado pero no recibido ---

def test_esquema2_esperado_no_recibido_no_bloquea(tmp_path):
    snap = _escribir(tmp_path, "orders.csv", _orders_csv_bytes())
    res = run_intake(_config(tiene_esquema2=True), snap, _persistence(tmp_path))

    assert res.estado == "EXECUTION_COMPLETE"
    assert res.report["schema2"]["status"] == "EXPECTED_NOT_RECEIVED"
    assert os.path.isfile(res.event_path)  # evento sí se emite


# --- Atomicidad: si el report falla, no hay evento ---

def test_sin_evento_si_falla_el_report(tmp_path, monkeypatch):
    import pipeline.pipeline as pipe

    def _boom(*a, **k):
        raise RuntimeError("fallo simulado en build_report")

    monkeypatch.setattr(pipe, "build_report", _boom)
    snap = _escribir(tmp_path, "orders.csv", _orders_csv_bytes())
    pers = _persistence(tmp_path)
    with pytest.raises(RuntimeError):
        run_intake(_config(), snap, pers)
    # Bronce pudo escribirse, pero el evento NO existe (atomicidad del handoff)
    assert not os.path.isfile(os.path.join(pers.events_dir, "intake_complete_20240101.json"))


# --- Recuperación: re-correr no reescribe Bronce, completa report+evento ---

def test_recuperacion_no_reescribe_bronce(tmp_path):
    snap = _escribir(tmp_path, "orders.csv", _orders_csv_bytes())
    pers = _persistence(tmp_path)
    r1 = run_intake(_config(), snap, pers)
    assert r1.bronze_files[0].rewritten is True
    r2 = run_intake(_config(), snap, pers)
    assert r2.bronze_files[0].rewritten is False  # idempotente
    assert r2.estado == "EXECUTION_COMPLETE"
    assert os.path.isfile(r2.event_path)
    # un único archivo Bronce, una sola entrada en el manifest
    man = json.loads(open(r2.manifest_path, encoding="utf-8").read())
    assert len(man["entregas"]) == 1


# --- Archivo vacío / corrupto -> fallo de recepción ---

def test_archivo_vacio_falla_sin_bronce(tmp_path):
    snap = _escribir(tmp_path, "orders.csv", b"")
    pers = _persistence(tmp_path)
    res = run_intake(_config(), snap, pers)
    assert res.estado == "WORKER_FAILED"
    assert res.bronze_files == []
    assert res.event_path is None


def test_archivo_corrupto_falla_sin_bronce(tmp_path):
    snap = _escribir(tmp_path, "orders.csv", b"\x00\x01\x02binario\x00basura")
    res = run_intake(_config(), snap, _persistence(tmp_path))
    assert res.estado == "WORKER_FAILED"
    assert res.bronze_files == []
    assert res.event_path is None

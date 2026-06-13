"""Tests del PASO 9 — bronze_writer.py (P6) — MÓDULO CRÍTICO (veto D5).

Contrato (plan/015_intake.md, PASO 9):
  write_bronze(raw_bytes, bronze_dir, mode, delivery_id, esquema, ...) -> BronzeFile

Materializa el invariante del medallón:
  - Bronce BIT-EXACTO a la entrada (los bytes del snapshot, no re-serializa).
  - SHA-256 calculado y persistido en _manifest.json.
  - Write-once: mismo contenido → no reescribe (idempotente); mismo nombre con
    contenido distinto → error.
  - Incremental = un archivo inmutable por entrega + append a 'entregas'.
"""

import hashlib
import json
import time

import pytest

from pipeline.bronze_writer import (
    BronzeFile,
    BronzeImmutabilityError,
    write_bronze,
)

_CONTENIDO = "fecha_pedido;id_cliente;id_producto;cantidad_solicitada\n2026-01-01;Pingüino;Camión;5\n".encode("cp1252")


def _manifest(bronze_dir):
    return json.loads((bronze_dir / "_manifest.json").read_text(encoding="utf-8"))


# --- Bit-exactitud + hash ---

def test_bronce_byte_identico_a_la_entrada(tmp_path):
    res = write_bronze(_CONTENIDO, str(tmp_path), mode="batch", delivery_id="20260101", esquema=1)
    assert isinstance(res, BronzeFile)
    escrito = (tmp_path / res.archivo).read_bytes()
    assert escrito == _CONTENIDO
    assert hashlib.sha256(escrito).hexdigest() == hashlib.sha256(_CONTENIDO).hexdigest()


def test_nombre_orders_para_esquema1(tmp_path):
    res = write_bronze(_CONTENIDO, str(tmp_path), mode="batch", delivery_id="20260101", esquema=1)
    assert res.archivo == "orders_batch_20260101.csv"


def test_nombre_inventory_para_esquema2(tmp_path):
    res = write_bronze(b"fecha;id_producto\n2026-01-01;P1\n", str(tmp_path),
                       mode="batch", delivery_id="20260101", esquema=2)
    assert res.archivo == "inventory_batch_20260101.csv"


def test_sha256_persistido_en_manifest(tmp_path):
    res = write_bronze(_CONTENIDO, str(tmp_path), mode="batch", delivery_id="20260101",
                       esquema=1, tenant_id="t1", rows=1,
                       rango={"fecha_min": "2026-01-01", "fecha_max": "2026-01-01"})
    man = _manifest(tmp_path)
    assert man["tenant_id"] == "t1"
    assert len(man["entregas"]) == 1
    entrada = man["entregas"][0]
    assert entrada["sha256"] == hashlib.sha256(_CONTENIDO).hexdigest()
    assert entrada["archivo"] == "orders_batch_20260101.csv"
    assert entrada["rows"] == 1
    assert entrada["rango"]["fecha_min"] == "2026-01-01"


def test_acento_cp1252_sobrevive_byte_a_byte(tmp_path):
    res = write_bronze(_CONTENIDO, str(tmp_path), mode="batch", delivery_id="20260101", esquema=1)
    escrito = (tmp_path / res.archivo).read_bytes()
    # los acentos se reproducen al decodificar con cp1252 (no hubo recodificación)
    assert "Pingüino" in escrito.decode("cp1252")
    assert "Camión" in escrito.decode("cp1252")


# --- Write-once / idempotencia ---

def test_idempotente_mismo_contenido_no_reescribe(tmp_path):
    r1 = write_bronze(_CONTENIDO, str(tmp_path), mode="batch", delivery_id="20260101", esquema=1)
    assert r1.rewritten is True
    mtime1 = (tmp_path / r1.archivo).stat().st_mtime_ns
    time.sleep(0.01)
    r2 = write_bronze(_CONTENIDO, str(tmp_path), mode="batch", delivery_id="20260101", esquema=1)
    assert r2.rewritten is False  # idempotente: no reescribió
    mtime2 = (tmp_path / r2.archivo).stat().st_mtime_ns
    assert mtime1 == mtime2
    # el manifest no se duplica
    assert len(_manifest(tmp_path)["entregas"]) == 1


def test_mismo_nombre_distinto_contenido_es_error(tmp_path):
    write_bronze(_CONTENIDO, str(tmp_path), mode="batch", delivery_id="20260101", esquema=1)
    otro = _CONTENIDO + b"2026-01-02;C2;P2;9\n"
    with pytest.raises(BronzeImmutabilityError):
        write_bronze(otro, str(tmp_path), mode="batch", delivery_id="20260101", esquema=1)


# --- Incremental: un archivo por entrega ---

def test_incremental_dos_entregas_dos_archivos(tmp_path):
    write_bronze(b"a;b\n1;2\n", str(tmp_path), mode="incremental", delivery_id="20260101", esquema=1)
    write_bronze(b"a;b\n3;4\n", str(tmp_path), mode="incremental", delivery_id="20260102", esquema=1)
    man = _manifest(tmp_path)
    archivos = {e["archivo"] for e in man["entregas"]}
    assert archivos == {"orders_incremental_20260101.csv", "orders_incremental_20260102.csv"}
    assert (tmp_path / "orders_incremental_20260101.csv").exists()
    assert (tmp_path / "orders_incremental_20260102.csv").exists()
    assert len(man["entregas"]) == 2

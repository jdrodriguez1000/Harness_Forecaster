"""Tests del PASO 4 — source_adapter.py (P1 recepción).

Contrato (plan/015_intake.md, PASO 4):
  read_snapshot(path) -> (raw_bytes, formato_declarado, source_metadata)

En Fase 1 solo existe ManualOperatorAdapter: lee un archivo del filesystem
que el operador dejó en la carpeta del tenant. NO decodifica ni interpreta:
entrega bytes crudos + metadata de fuente. Nunca modifica el archivo origen.
"""

import hashlib

import pytest

from pipeline.source_adapter import (
    ManualOperatorAdapter,
    Snapshot,
    SourceNotFound,
)


# --- Caso 1: archivo existente → bytes byte-idénticos al archivo en disco ---

def test_lee_bytes_identicos(tmp_path):
    contenido = "fecha_pedido;id_cliente;id_producto;cantidad_solicitada\n".encode("cp1252")
    archivo = tmp_path / "orders.csv"
    archivo.write_bytes(contenido)

    snap = ManualOperatorAdapter().read_snapshot(str(archivo))

    assert isinstance(snap, Snapshot)
    assert snap.raw_bytes == contenido
    # invariante Bronce: lo que entra es exactamente lo que se entrega
    assert hashlib.sha256(snap.raw_bytes).hexdigest() == hashlib.sha256(contenido).hexdigest()
    assert snap.vacio is False


def test_formato_declarado_por_extension(tmp_path):
    archivo = tmp_path / "orders.CSV"
    archivo.write_bytes(b"a,b,c\n1,2,3\n")

    snap = ManualOperatorAdapter().read_snapshot(str(archivo))

    # formato_declarado es la extensión normalizada (sin punto, minúsculas) — NO detección real
    assert snap.formato_declarado == "csv"


def test_metadata_de_fuente(tmp_path):
    contenido = b"hola mundo\n"
    archivo = tmp_path / "data.xlsx"
    archivo.write_bytes(contenido)

    snap = ManualOperatorAdapter().read_snapshot(str(archivo))

    assert snap.source_metadata["path"] == str(archivo)
    assert snap.source_metadata["size_bytes"] == len(contenido)
    assert "mtime" in snap.source_metadata
    assert snap.formato_declarado == "xlsx"


# --- Caso 2: archivo inexistente → excepción clara SourceNotFound ---

def test_archivo_inexistente(tmp_path):
    inexistente = tmp_path / "no_existe.csv"
    with pytest.raises(SourceNotFound):
        ManualOperatorAdapter().read_snapshot(str(inexistente))


def test_ruta_es_directorio(tmp_path):
    # una carpeta no es un snapshot tabular → SourceNotFound
    with pytest.raises(SourceNotFound):
        ManualOperatorAdapter().read_snapshot(str(tmp_path))


# --- Caso 3: archivo vacío (0 bytes) → bandera vacio=True ---

def test_archivo_vacio(tmp_path):
    archivo = tmp_path / "vacio.csv"
    archivo.write_bytes(b"")

    snap = ManualOperatorAdapter().read_snapshot(str(archivo))

    assert snap.vacio is True
    assert snap.raw_bytes == b""
    assert snap.source_metadata["size_bytes"] == 0


# --- Invariante: el adaptador nunca modifica el archivo origen ---

def test_no_modifica_origen(tmp_path):
    contenido = b"fecha;cliente\n2026-01-01;C1\n"
    archivo = tmp_path / "orders.csv"
    archivo.write_bytes(contenido)
    hash_antes = hashlib.sha256(archivo.read_bytes()).hexdigest()

    ManualOperatorAdapter().read_snapshot(str(archivo))

    hash_despues = hashlib.sha256(archivo.read_bytes()).hexdigest()
    assert hash_antes == hash_despues

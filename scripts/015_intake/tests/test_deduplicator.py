"""Tests del PASO 8 — deduplicator.py (P4).

Contrato (plan/015_intake.md, PASO 8). Clave compuesta (fecha_pedido, id_cliente, id_producto):
  - Batch:        count_internal_duplicates(df) -> int
                  (registra como anomalía, NO elimina filas; el 020 los cuenta)
  - Incremental:  diff_against_bronze(df, manifest_path) -> (df_nuevos, n_excluidos)
                  (excluye lo ya presente en la unión lógica del Bronce acumulado;
                   solo lo nuevo se persiste)
"""

import json

import pandas as pd

from pipeline.deduplicator import (
    count_internal_duplicates,
    diff_against_bronze,
    keys_from_df,
)


# --- Batch: cuenta, no elimina ---

def test_batch_cuenta_34_no_elimina():
    filas = [
        {"fecha_pedido": "2026-01-01", "id_cliente": f"C{i}", "id_producto": "P1", "cantidad_solicitada": 1}
        for i in range(20)
    ]
    filas += [
        {"fecha_pedido": "2026-01-01", "id_cliente": "C0", "id_producto": "P1", "cantidad_solicitada": 1}
        for _ in range(34)
    ]
    df = pd.DataFrame(filas)
    n = count_internal_duplicates(df)
    assert n == 34
    assert len(df) == 54  # el deduplicador NO elimina nada


def test_clave_compuesta_distinto_producto_no_es_duplicado():
    df = pd.DataFrame({
        "fecha_pedido": ["2026-01-01", "2026-01-01"],
        "id_cliente": ["C1", "C1"],
        "id_producto": ["P1", "P2"],
        "cantidad_solicitada": [1, 2],
    })
    assert count_internal_duplicates(df) == 0


def test_keys_normaliza_a_string():
    df = pd.DataFrame({
        "fecha_pedido": ["2026-01-01"],
        "id_cliente": [" C1 "],
        "id_producto": ["P1"],
    })
    assert keys_from_df(df) == [("2026-01-01", "C1", "P1")]


# --- Incremental: excluye lo ya presente en Bronce previo ---

def _escribir_bronce_previo(tmp_path, n_claves):
    bronze_dir = tmp_path / "005_bronze"
    bronze_dir.mkdir()
    # CSV ; cp1252 (ejercita la detección de formato al releer el Bronce previo)
    contenido = "fecha_pedido;id_cliente;id_producto\n"
    for i in range(n_claves):
        contenido += f"2026-01-01;C{i};P1\n"
    (bronze_dir / "orders_incremental_20260101.csv").write_bytes(contenido.encode("cp1252"))
    manifest = {
        "tenant_id": "t1",
        "entregas": [{
            "delivery_id": "20260101", "mode": "incremental",
            "archivo": "orders_incremental_20260101.csv", "esquema": 1,
            "sha256": "x", "rows": n_claves,
        }],
    }
    manifest_path = bronze_dir / "_manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return str(manifest_path)


def test_incremental_excluye_existentes(tmp_path):
    manifest_path = _escribir_bronce_previo(tmp_path, n_claves=30)
    # 100 filas: C0..C29 ya existen, C30..C99 son nuevas (70)
    df = pd.DataFrame([
        {"fecha_pedido": "2026-01-01", "id_cliente": f"C{i}", "id_producto": "P1", "cantidad_solicitada": 1}
        for i in range(100)
    ])
    df_nuevos, n_excluidos = diff_against_bronze(df, manifest_path)
    assert n_excluidos == 30
    assert len(df_nuevos) == 70
    # solo deben quedar C30..C99
    assert set(df_nuevos["id_cliente"]) == {f"C{i}" for i in range(30, 100)}


def test_incremental_sin_manifest_previo_todo_nuevo(tmp_path):
    manifest_path = str(tmp_path / "005_bronze" / "_manifest.json")  # no existe
    df = pd.DataFrame([
        {"fecha_pedido": "2026-01-01", "id_cliente": f"C{i}", "id_producto": "P1"}
        for i in range(5)
    ])
    df_nuevos, n_excluidos = diff_against_bronze(df, manifest_path)
    assert n_excluidos == 0
    assert len(df_nuevos) == 5

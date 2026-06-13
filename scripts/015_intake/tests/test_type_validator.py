"""Tests del PASO 7 — type_validator.py (P3).

Contrato (plan/015_intake.md, PASO 7):
  validate_types(df, esquema) -> TypeResult

Por cada campo mínimo CUENTA errores (no detiene, no filtra filas):
  - fecha_pedido parseable (varios formatos: DD/MM/YYYY, YYYY-MM-DD, ...)
  - id_cliente / id_producto texto no vacío
  - cantidad_solicitada numérico ≥ 0
Devuelve conteo de errores por campo → alimenta el ISD del 020. NUNCA lanza.
"""

import pandas as pd

from pipeline.type_validator import TypeResult, parse_fecha, validate_types


# --- parse_fecha (función pura) ---

def test_parse_fecha_varios_formatos():
    assert parse_fecha("2026-01-15") is not None
    assert parse_fecha("15/01/2026") is not None
    assert parse_fecha("15-01-2026") is not None
    assert parse_fecha("no es fecha") is None
    assert parse_fecha("") is None


# --- conteos por campo, sin eliminar filas ---

def test_cantidad_negativas_y_no_numericas_cuenta_no_elimina():
    df = pd.DataFrame({
        "fecha_pedido": ["2026-01-01"] * 7,
        "id_cliente": ["C1"] * 7,
        "id_producto": ["P1"] * 7,
        "cantidad_solicitada": [10, -5, -1, -10, "abc", "", 3],  # 3 negativas + 2 no-numéricas
    })
    res = validate_types(df, esquema=1)
    assert isinstance(res, TypeResult)
    assert res.errores["cantidad_solicitada"] == 5
    assert res.filas_evaluadas == 7  # no se eliminó ninguna fila


def test_fecha_tres_formatos_cero_errores():
    df = pd.DataFrame({
        "fecha_pedido": ["2026-01-15", "15/01/2026", "15-01-2026"],
        "id_cliente": ["C1", "C2", "C3"],
        "id_producto": ["P1", "P2", "P3"],
        "cantidad_solicitada": [1, 2, 3],
    })
    res = validate_types(df, esquema=1)
    assert res.errores["fecha_pedido"] == 0


def test_id_cliente_vacios_cuenta():
    df = pd.DataFrame({
        "fecha_pedido": ["2026-01-01"] * 4,
        "id_cliente": ["C1", "", "  ", "C4"],  # 2 vacíos (vacío y solo-espacios)
        "id_producto": ["P1", "P2", "P3", "P4"],
        "cantidad_solicitada": [1, 2, 3, 4],
    })
    res = validate_types(df, esquema=1)
    assert res.errores["id_cliente"] == 2


def test_fecha_no_parseable_cuenta():
    df = pd.DataFrame({
        "fecha_pedido": ["2026-01-01", "32/13/2026", "ayer"],
        "id_cliente": ["C1", "C2", "C3"],
        "id_producto": ["P1", "P2", "P3"],
        "cantidad_solicitada": [1, 2, 3],
    })
    res = validate_types(df, esquema=1)
    assert res.errores["fecha_pedido"] == 2


def test_cabeceras_no_canonicas_se_resuelven():
    # type_validator resuelve nombres por canónico, igual que schema_validator
    df = pd.DataFrame({
        "Fecha Pedido": ["2026-01-01", "2026-01-02"],
        "cliente": ["C1", ""],          # sinónimo de id_cliente; 1 vacío
        "producto": ["P1", "P2"],
        "cantidad": [5, -2],            # sinónimo de cantidad_solicitada; 1 negativo
    })
    res = validate_types(df, esquema=1)
    assert res.errores["id_cliente"] == 1
    assert res.errores["cantidad_solicitada"] == 1

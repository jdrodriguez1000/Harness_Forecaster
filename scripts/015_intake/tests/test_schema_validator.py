"""Tests del PASO 6 — schema_validator.py (P2 GATE de estructura, veto D2).

Contrato (plan/015_intake.md, PASO 6):
  validate_structure(df, esquema:int) -> StructureResult

Verifica los campos mínimos del esquema. Falta ≥ 1 mínimo → aprobado=False +
lista de faltantes (el processor genera intake_rejection.json, NO crea Bronce).
Todos presentes → aprobado=True; registra ideales presentes/faltantes (no rechazan).
El matching es LÓGICO (normaliza cabeceras: trim/minúsculas/acentos/sinónimos)
sin alterar el archivo. Regla innegociable del veto D2: falso positivo = falso
negativo = 0 — rechaza si y solo si falta un mínimo.

Campos: Esquema 1 → 4 mínimos / 17 ideales (DEC-014, problem_statement.md).
        Esquema 2 → 6 mínimos.
"""

import pandas as pd

from pipeline.schema_validator import (
    IDEALES_ESQUEMA1,
    MINIMOS_ESQUEMA1,
    MINIMOS_ESQUEMA2,
    StructureResult,
    validate_structure,
)


def _df(cols):
    """DataFrame de una fila con las columnas dadas (solo importan las cabeceras)."""
    return pd.DataFrame([{c: "x" for c in cols}])


# --- Esquema 1: aprobación con los 4 mínimos ---

def test_esquema1_minimos_completos_aprobado():
    df = _df(MINIMOS_ESQUEMA1)
    res = validate_structure(df, esquema=1)
    assert isinstance(res, StructureResult)
    assert res.aprobado is True
    assert res.campos_minimos_faltantes == []
    assert set(res.campos_minimos_presentes) == set(MINIMOS_ESQUEMA1)


def test_esquema1_falta_id_producto_rechazado():
    df = _df(["fecha_pedido", "id_cliente", "cantidad_solicitada"])
    res = validate_structure(df, esquema=1)
    assert res.aprobado is False
    assert res.campos_minimos_faltantes == ["id_producto"]


def test_esquema1_minimos_mas_ideales_registra_ambos():
    cols = MINIMOS_ESQUEMA1 + [
        "fecha_entrega_real", "estado_pedido", "cantidad_entregada",
        "id_sede", "categoria", "region",
    ]
    df = _df(cols)
    res = validate_structure(df, esquema=1)
    assert res.aprobado is True
    # los 4 mínimos también cuentan como ideales presentes
    assert "categoria" in res.campos_ideales_presentes
    assert "fecha_pedido" in res.campos_ideales_presentes
    # los ideales no provistos quedan registrados como faltantes (déficit, no rechazo)
    assert "unidad_medida" in res.campos_ideales_faltantes
    assert "pais" in res.campos_ideales_faltantes
    # cobertura: presentes + faltantes = universo ideal completo
    assert set(res.campos_ideales_presentes) | set(res.campos_ideales_faltantes) == set(IDEALES_ESQUEMA1)


# --- Esquema 2 ---

def test_esquema2_minimos_completos_aprobado():
    df = _df(MINIMOS_ESQUEMA2)
    res = validate_structure(df, esquema=2)
    assert res.aprobado is True
    assert res.campos_minimos_faltantes == []


def test_esquema2_falta_costo_unitario_rechazado():
    cols = [c for c in MINIMOS_ESQUEMA2 if c != "costo_unitario"]
    res = validate_structure(_df(cols), esquema=2)
    assert res.aprobado is False
    assert "costo_unitario" in res.campos_minimos_faltantes


# --- Matching normalizado: espacios, mayúsculas, acentos, sinónimos ---

def test_cabeceras_con_espacios_y_mayusculas_reconocidas():
    df = _df(["Fecha Pedido", "ID  CLIENTE ", "Id_Producto", "CANTIDAD SOLICITADA"])
    res = validate_structure(df, esquema=1)
    assert res.aprobado is True
    assert res.campos_minimos_faltantes == []


def test_sinonimo_comun_reconocido():
    # 'cliente' y 'producto' y 'cantidad' son sinónimos curados de los mínimos
    df = _df(["fecha_pedido", "cliente", "producto", "cantidad"])
    res = validate_structure(df, esquema=1)
    assert res.aprobado is True


# --- Veto D2: cero falsos positivos / cero falsos negativos ---

def test_no_falso_positivo_por_substring():
    # 'cantidad_solicitada_total' NO es 'cantidad_solicitada' → debe faltar el mínimo
    df = _df(["fecha_pedido", "id_cliente", "id_producto", "cantidad_solicitada_total"])
    res = validate_structure(df, esquema=1)
    assert res.aprobado is False
    assert "cantidad_solicitada" in res.campos_minimos_faltantes


def test_no_falso_negativo_con_columnas_extra():
    # mínimos exactos + ruido irrelevante → aprobado (no rechaza por columnas de más)
    df = _df(MINIMOS_ESQUEMA1 + ["columna_irrelevante", "notas", "x9"])
    res = validate_structure(df, esquema=1)
    assert res.aprobado is True
    assert res.campos_minimos_faltantes == []

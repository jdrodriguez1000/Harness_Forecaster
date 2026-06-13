"""Tests del PASO 7 (anexo) — range_evaluator.py (P5).

Contrato (plan/015_intake.md, PASO 7):
  evaluate_range(df, anios_declarados) -> RangeResult

Calcula fecha_min/max, dias_cubiertos, anios_real; compara con lo declarado
en el 010; discrepancia > 20% → warning=True. No detiene el flujo.
"""

import pandas as pd

from pipeline.range_evaluator import RangeResult, evaluate_range


def test_historial_mas_largo_que_declarado_warning():
    # ~3.4 años reales vs 2 declarados → discrepancia ≈ 70% → warning
    df = pd.DataFrame({"fecha_pedido": ["2021-01-01", "2022-07-15", "2024-06-01"]})
    res = evaluate_range(df, anios_declarados=2)
    assert isinstance(res, RangeResult)
    assert res.fecha_min == "2021-01-01"
    assert res.fecha_max == "2024-06-01"
    assert res.warning is True
    assert 60 <= res.discrepancia_pct <= 80
    assert round(res.anios_real, 1) == 3.4


def test_historial_cercano_a_declarado_sin_warning():
    # ~2.1 años reales vs 2 declarados → discrepancia ≈ 5% → sin warning
    df = pd.DataFrame({"fecha_pedido": ["2022-01-01", "2024-02-06"]})
    res = evaluate_range(df, anios_declarados=2)
    assert res.warning is False
    assert res.discrepancia_pct < 20


def test_fechas_no_parseables_se_ignoran():
    df = pd.DataFrame({"fecha_pedido": ["2022-01-01", "basura", "2024-02-06", ""]})
    res = evaluate_range(df, anios_declarados=2)
    assert res.fecha_min == "2022-01-01"
    assert res.fecha_max == "2024-02-06"
    assert res.dias_cubiertos == 766  # 2022-01-01 → 2024-02-06


def test_sin_declarado_no_warning():
    df = pd.DataFrame({"fecha_pedido": ["2022-01-01", "2024-02-06"]})
    res = evaluate_range(df, anios_declarados=None)
    assert res.warning is False
    assert res.discrepancia_pct is None
    assert res.anios_declarados is None


def test_esquema2_usa_campo_fecha():
    df = pd.DataFrame({"fecha": ["2023-01-01", "2024-01-01"]})
    res = evaluate_range(df, anios_declarados=1, campo_fecha="fecha")
    assert res.fecha_min == "2023-01-01"
    assert res.fecha_max == "2024-01-01"

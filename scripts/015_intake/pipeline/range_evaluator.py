"""P5 — Evaluación de rango temporal. range_evaluator.py

evaluate_range(df, anios_declarados, campo_fecha="fecha_pedido") -> RangeResult

Calcula el rango real (fecha_min/max, días cubiertos, años reales) y lo compara
con el historial declarado por el cliente en el 010. Discrepancia > 20% →
warning=True. No detiene el flujo (el warning va al intake_report; el 020 decide).

Las fechas no parseables se ignoran para el cálculo del rango (el conteo de
errores de fecha lo lleva type_validator, P3).

Ver plan/015_intake.md (PASO 7 anexo) y brief/015_intake.md (P5).
"""

from __future__ import annotations

from dataclasses import dataclass

from pipeline.type_validator import _resolver_columna, parse_fecha

_DIAS_POR_ANIO = 365.25
_UMBRAL_DISCREPANCIA_PCT = 20.0


@dataclass
class RangeResult:
    """Rango temporal real y su comparación con lo declarado."""

    fecha_min: str | None = None
    fecha_max: str | None = None
    dias_cubiertos: int = 0
    anios_real: float | None = None
    anios_declarados: float | None = None
    discrepancia_pct: float | None = None
    warning: bool = False


def evaluate_range(df, anios_declarados, campo_fecha: str = "fecha_pedido") -> RangeResult:
    col = _resolver_columna(df, campo_fecha)
    if col is None:
        return RangeResult(anios_declarados=anios_declarados)

    fechas = [d for d in (parse_fecha(v) for v in df[col]) if d is not None]
    if not fechas:
        return RangeResult(anios_declarados=anios_declarados)

    fmin, fmax = min(fechas), max(fechas)
    dias = (fmax - fmin).days
    anios_real = dias / _DIAS_POR_ANIO

    discrepancia_pct = None
    warning = False
    if anios_declarados not in (None, 0):
        discrepancia_pct = abs(anios_real - anios_declarados) / anios_declarados * 100
        warning = discrepancia_pct > _UMBRAL_DISCREPANCIA_PCT

    return RangeResult(
        fecha_min=fmin.strftime("%Y-%m-%d"),
        fecha_max=fmax.strftime("%Y-%m-%d"),
        dias_cubiertos=dias,
        anios_real=anios_real,
        anios_declarados=anios_declarados,
        discrepancia_pct=discrepancia_pct,
        warning=warning,
    )

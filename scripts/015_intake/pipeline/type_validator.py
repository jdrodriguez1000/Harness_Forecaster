"""P3 — Validación de tipos. type_validator.py

validate_types(df, esquema) -> TypeResult

Por cada campo mínimo CUENTA errores; NUNCA detiene el flujo ni filtra filas
(D3). Los conteos alimentan el ISD del 020 (que decide qué hacer con ellos).

Reglas por campo:
  - fecha:   parseable en algún formato común (DD/MM/YYYY, YYYY-MM-DD, ...).
  - texto:   no vacío (None/NaN/'' / solo espacios → error).
  - num≥0:   convertible a número y ≥ 0 (no numérico o negativo → error).

Las cabeceras se resuelven por nombre canónico (mismo criterio que el GATE P2),
para tolerar mayúsculas/acentos/sinónimos sin tocar el archivo.

Ver plan/015_intake.md (PASO 7) y brief/015_intake.md (P3).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from pipeline.schema_validator import _canonico

# Formatos de fecha aceptados (explícitos para evitar ambigüedad día/mes).
_FORMATOS_FECHA = (
    "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d",
    "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M",
)

# Tipo esperado por campo mínimo, por esquema. "date" | "text" | "num_nonneg".
_REGLAS = {
    1: {
        "fecha_pedido": "date",
        "id_cliente": "text",
        "id_producto": "text",
        "cantidad_solicitada": "num_nonneg",
    },
    2: {
        "fecha": "date",
        "id_producto": "text",
        "cantidad_producida": "num_nonneg",
        "stock_disponible": "num_nonneg",
        "costo_unitario": "num_nonneg",
        "stock_minimo": "num_nonneg",
    },
}


@dataclass
class TypeResult:
    """Conteo de errores de tipo por campo. No modifica el DataFrame."""

    esquema: int
    errores: dict = field(default_factory=dict)
    filas_evaluadas: int = 0


def parse_fecha(value):
    """Devuelve un datetime si `value` es una fecha parseable, o None."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    s = str(value).strip()
    if s == "" or s.lower() in ("nan", "nat", "none"):
        return None
    for fmt in _FORMATOS_FECHA:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def _es_vacio(value) -> bool:
    if value is None:
        return True
    s = str(value).strip()
    return s == "" or s.lower() in ("nan", "none")


def _a_numero(value):
    """Convierte a float (admite coma decimal), o None si no es numérico."""
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if s == "":
        return None
    for candidato in (s, s.replace(",", ".")):
        try:
            return float(candidato)
        except ValueError:
            continue
    return None


def _resolver_columna(df, campo: str):
    """Columna del df cuyo nombre canónico coincide con `campo`, o None."""
    for col in df.columns:
        if _canonico(col) == campo:
            return col
    return None


def validate_types(df, esquema: int) -> TypeResult:
    reglas = _REGLAS.get(esquema, {})
    errores: dict = {}

    for campo, tipo in reglas.items():
        col = _resolver_columna(df, campo)
        if col is None:
            # campo ausente: lo gobierna el GATE P2, no se cuenta aquí
            continue
        serie = df[col]
        if tipo == "date":
            n = sum(1 for v in serie if parse_fecha(v) is None)
        elif tipo == "text":
            n = sum(1 for v in serie if _es_vacio(v))
        else:  # num_nonneg
            n = 0
            for v in serie:
                num = _a_numero(v)
                if num is None or num < 0:
                    n += 1
        errores[campo] = n

    return TypeResult(esquema=esquema, errores=errores, filas_evaluadas=len(df))

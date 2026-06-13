"""P2 — Validación de estructura (GATE). schema_validator.py

validate_structure(df, esquema:int) -> StructureResult

Es el GATE del pipeline y un VETO DURO (D2): si falta ≥ 1 campo mínimo, la
entrega se rechaza y NO se crea Bronce. Si todos los mínimos están presentes,
continúa y registra qué campos ideales hay y cuáles faltan (déficit que alimenta
el ISD del 020 — NO rechazan).

El matching es LÓGICO, no físico: las cabeceras se normalizan (trim, minúsculas,
acentos, espacios/guiones → '_') y se consultan sinónimos curados. El archivo
Bronce se copia tal cual — aquí solo se decide presencia/ausencia.

Regla innegociable del veto D2: falso positivo = falso negativo = 0. El matching
es por igualdad de nombre normalizado o sinónimo exacto, NUNCA por substring
(p. ej. 'cantidad_solicitada_total' ≠ 'cantidad_solicitada').

Campos (DEC-014 / problem_statement.md §esquemas).

Ver plan/015_intake.md (PASO 6) y brief/015_intake.md (P2).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

# --- Esquema 1: Historial de Pedidos (obligatorio) ---
MINIMOS_ESQUEMA1 = ["fecha_pedido", "id_cliente", "id_producto", "cantidad_solicitada"]

IDEALES_ESQUEMA1 = [
    "fecha_pedido", "fecha_entrega_solicitada", "fecha_entrega_real", "estado_pedido",
    "cantidad_solicitada", "cantidad_entregada", "cantidad_cancelada",
    "id_cliente", "id_sede", "id_producto", "subcategoria", "categoria",
    "ciudad", "pais", "region", "unidad_medida", "tipo_pedido",
]  # 17 campos (DEC-014)

# --- Esquema 2: Producción e Inventario (opcional) ---
MINIMOS_ESQUEMA2 = [
    "fecha", "id_producto", "cantidad_producida",
    "stock_disponible", "costo_unitario", "stock_minimo",
]

# Sinónimos curados (nombre normalizado de la cabecera → campo canónico).
# Conservador a propósito: solo equivalencias inequívocas, para no introducir
# falsos positivos en el GATE.
SINONIMOS = {
    "fecha_de_pedido": "fecha_pedido",
    "fecha_orden": "fecha_pedido",
    "fecha_del_pedido": "fecha_pedido",
    "cliente": "id_cliente",
    "codigo_cliente": "id_cliente",
    "id_del_cliente": "id_cliente",
    "producto": "id_producto",
    "codigo_producto": "id_producto",
    "sku": "id_producto",
    "id_del_producto": "id_producto",
    "cantidad": "cantidad_solicitada",
    "cantidad_pedida": "cantidad_solicitada",
    "cantidad_solicitada_unidades": "cantidad_solicitada",
}


@dataclass
class StructureResult:
    """Veredicto del GATE de estructura.

    esquema                   1 | 2
    aprobado                  False si falta ≥ 1 mínimo (rechazo, sin Bronce)
    campos_minimos_presentes  mínimos hallados (por nombre canónico)
    campos_minimos_faltantes  mínimos ausentes (motivo del rechazo)
    campos_ideales_presentes  ideales hallados (solo Esquema 1)
    campos_ideales_faltantes  ideales ausentes — déficit, NO rechaza
    mapeo                     cabecera original → campo canónico (trazabilidad)
    """

    esquema: int
    aprobado: bool
    campos_minimos_presentes: list = field(default_factory=list)
    campos_minimos_faltantes: list = field(default_factory=list)
    campos_ideales_presentes: list = field(default_factory=list)
    campos_ideales_faltantes: list = field(default_factory=list)
    mapeo: dict = field(default_factory=dict)


def _normalize(header: str) -> str:
    """trim → sin acentos → minúsculas → espacios/guiones a '_' → colapsa '_'."""
    s = str(header).strip()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))  # quita acentos
    s = s.lower()
    s = re.sub(r"[\s\-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def _canonico(header: str) -> str:
    """Nombre canónico de una cabecera: ella misma normalizada, o su sinónimo."""
    norm = _normalize(header)
    return SINONIMOS.get(norm, norm)


def validate_structure(df, esquema: int) -> StructureResult:
    minimos = MINIMOS_ESQUEMA1 if esquema == 1 else MINIMOS_ESQUEMA2

    # cabecera original → canónico (último gana si hay choque, irrelevante para presencia)
    mapeo = {col: _canonico(col) for col in df.columns}
    presentes = set(mapeo.values())

    min_presentes = [c for c in minimos if c in presentes]
    min_faltantes = [c for c in minimos if c not in presentes]

    ideales_presentes: list = []
    ideales_faltantes: list = []
    if esquema == 1:
        ideales_presentes = [c for c in IDEALES_ESQUEMA1 if c in presentes]
        ideales_faltantes = [c for c in IDEALES_ESQUEMA1 if c not in presentes]

    return StructureResult(
        esquema=esquema,
        aprobado=(len(min_faltantes) == 0),
        campos_minimos_presentes=min_presentes,
        campos_minimos_faltantes=min_faltantes,
        campos_ideales_presentes=ideales_presentes,
        campos_ideales_faltantes=ideales_faltantes,
        mapeo=mapeo,
    )

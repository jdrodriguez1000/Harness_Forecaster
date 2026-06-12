"""
ito_calculator.py — Cálculo del Índice de Tamaño Operativo (ITO)
Harness 010 Discovery — FARO / Sabbia Solutions & Software

Fórmula (escala normalizada 0–100):
    norm_x = min(x / x_max, 1.0) * 100
    ITO    = w1 * norm_skus + w2 * norm_clientes + w3 * norm_pedidos

Categorías:
    M  : ITO ≤ 33  → USD 200/mes
    L  : ITO ≤ 66  → USD 350/mes
    XL : ITO > 66  → USD 500/mes

IMPORTANTE: Pesos, referencias máximas y umbrales son PROVISIONALES.
Serán calibrados con datos piloto reales (T-030).
"""

# ── Pesos (provisionales — T-030) ──────────────────────────────────────────
W1_SKUS      = 0.40
W2_CLIENTES  = 0.35
W3_PEDIDOS   = 0.25

# ── Referencias máximas para normalización (provisionales — T-030) ─────────
SKUS_MAX     = 500
CLIENTES_MAX = 100
PEDIDOS_MAX  = 2000

# ── Umbrales de categoría en escala normalizada 0–100 ──────────────────────
UMBRAL_M = 33.0   # ITO ≤ 33  → M
UMBRAL_L = 66.0   # ITO ≤ 66  → L  |  ITO > 66 → XL

# ── Precios base por categoría (USD/mes) ───────────────────────────────────
PRECIO = {"M": 200, "L": 350, "XL": 500}


def calcular_ito(skus_activos: int, clientes_xyz: int, pedidos_por_mes: int) -> dict:
    """
    Calcula el ITO normalizado y determina la categoría M/L/XL.

    Parámetros
    ----------
    skus_activos    : cantidad aproximada de SKUs activos del cliente
    clientes_xyz    : cantidad aproximada de clientes XYZ atendidos
    pedidos_por_mes : volumen aproximado de pedidos por mes

    Retorna
    -------
    dict con la estructura completa del bloque `ito` + `categoria`
    de analysis_report.json (ver discovery-analysis-schema).
    """
    # Normalización (capped a 100)
    norm_skus     = round(min(skus_activos    / SKUS_MAX,     1.0) * 100, 2)
    norm_clientes = round(min(clientes_xyz    / CLIENTES_MAX, 1.0) * 100, 2)
    norm_pedidos  = round(min(pedidos_por_mes / PEDIDOS_MAX,  1.0) * 100, 2)

    ito = round(W1_SKUS * norm_skus + W2_CLIENTES * norm_clientes + W3_PEDIDOS * norm_pedidos, 2)

    # Clasificación
    if ito <= UMBRAL_M:
        categoria = "M"
    elif ito <= UMBRAL_L:
        categoria = "L"
    else:
        categoria = "XL"

    return {
        "provisional": True,
        "valores_base": {
            "skus_activos":    skus_activos,
            "clientes_xyz":    clientes_xyz,
            "pedidos_por_mes": pedidos_por_mes,
        },
        "normalizados": {
            "norm_skus":      norm_skus,
            "norm_clientes":  norm_clientes,
            "norm_pedidos":   norm_pedidos,
        },
        "pesos": {
            "w1_skus":      W1_SKUS,
            "w2_clientes":  W2_CLIENTES,
            "w3_pedidos":   W3_PEDIDOS,
        },
        "referencias_max": {
            "skus_max":     SKUS_MAX,
            "clientes_max": CLIENTES_MAX,
            "pedidos_max":  PEDIDOS_MAX,
        },
        "ito_calculado": ito,
        "categoria_calculada": categoria,
        "precio_base_usd": PRECIO[categoria],
    }


def evaluar_discrepancia(categoria_calculada: str, categoria_comercial: str) -> dict:
    """
    Compara la categoría calculada con la asignada comercialmente.

    Retorna el bloque `categoria` de analysis_report.json.
    """
    niveles = {"M": 0, "L": 1, "XL": 2}
    diff = abs(niveles[categoria_calculada] - niveles[categoria_comercial])

    if diff == 0:
        discrepancia      = "ninguna"
        critica           = False
        nota              = None
        confirmada        = categoria_calculada
    elif diff == 1:
        discrepancia      = "advertencia"
        critica           = False
        nota              = (
            f"El ITO calcula categoría {categoria_calculada} pero se vendió como "
            f"{categoria_comercial}. Diferencia de 1 nivel — el governor decide si escalar."
        )
        confirmada        = categoria_calculada
    else:
        discrepancia      = "critica"
        critica           = True
        nota              = (
            f"El ITO calcula categoría {categoria_calculada} pero se vendió como "
            f"{categoria_comercial}. Diferencia de 2 niveles — requiere revisión comercial "
            f"antes de continuar."
        )
        confirmada        = categoria_comercial  # bloqueado hasta resolución

    return {
        "calculada":           categoria_calculada,
        "comercial":           categoria_comercial,
        "confirmada":          confirmada,
        "discrepancia":        discrepancia,
        "discrepancia_critica": critica,
        "nota_discrepancia":   nota,
    }


# ── CLI ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse, json

    parser = argparse.ArgumentParser(
        description="Calcula el ITO y la categoría M/L/XL de un cliente."
    )
    parser.add_argument("--skus",     type=int, required=True, help="SKUs activos aprox.")
    parser.add_argument("--clientes", type=int, required=True, help="Clientes XYZ atendidos aprox.")
    parser.add_argument("--pedidos",  type=int, required=True, help="Volumen de pedidos por mes aprox.")
    parser.add_argument("--comercial", type=str, default=None,
                        choices=["M", "L", "XL"],
                        help="Categoría asignada comercialmente (para evaluar discrepancia).")
    args = parser.parse_args()

    resultado = calcular_ito(args.skus, args.clientes, args.pedidos)

    if args.comercial:
        resultado["categoria"] = evaluar_discrepancia(
            resultado["categoria_calculada"], args.comercial
        )

    print(json.dumps(resultado, ensure_ascii=False, indent=2))

"""
cold_start_evaluator.py — Evaluación del nivel de confianza Cold Start
Harness 010 Discovery — FARO / Sabbia Solutions & Software

Clasifica el historial disponible del cliente en cuatro niveles y determina
el paso de cascada aplicable cuando el historial es insuficiente.

Clasificación (DEC-013):
    ≥ 3 años  → Alta        (CS-ALTA)
    2–3 años  → Estándar    (CS-ESTANDAR)
    1–2 años  → Reducida    (CS-REDUCIDA)
    < 1 año   → Experimental (CS-EXPERIMENTAL) — cascada activa
    < 3 meses → Inviable    — escalar al operador obligatoriamente

Cascada cold start (3 pasos):
    Paso 1 — Analogía por categoría de producto  (Fase 3)
    Paso 2 — Analogía por cliente XYZ            (Fase 3)
    Paso 3 — Acumulación mínima 3 meses          (Fase 1 — fallback garantizado)

En Fase 1 siempre se registra cascada_paso = 3.
"""

# ── Umbrales en años ───────────────────────────────────────────────────────
UMBRAL_ALTA      = 3.0    # ≥ 3 años
UMBRAL_ESTANDAR  = 2.0    # ≥ 2 años
UMBRAL_REDUCIDA  = 1.0    # ≥ 1 año
UMBRAL_MINIMO    = 0.25   # ≥ 3 meses (~0.25 años) — mínimo viable

# ── Textos de cascada ──────────────────────────────────────────────────────
CASCADA = {
    1: "Analogía por categoría de producto — usar patrones de sector como proxy "
       "(requiere datos de otros tenants, disponible en Fase 3)",
    2: "Analogía por cliente XYZ — usar pedidos del mismo cliente a otros ABC "
       "(requiere datos de otros tenants, disponible en Fase 3)",
    3: "Acumulación — esperar 3 meses de datos reales antes del primer pronóstico "
       "(fallback garantizado en Fase 1)",
}


def evaluar_cold_start(anios_historial: float) -> dict:
    """
    Evalúa el nivel de confianza cold start según el historial declarado.

    Parámetros
    ----------
    anios_historial : años de historial de pedidos disponible (float)
                      Ejemplos: 2.5 = dos años y medio, 0.5 = seis meses

    Retorna
    -------
    dict con la estructura completa del bloque `cold_start` de analysis_report.json
    (ver discovery-analysis-schema) más campos auxiliares para el governor.
    """
    anios = round(float(anios_historial), 4)

    if anios >= UMBRAL_ALTA:
        nivel            = "Alta"
        codigo           = "CS-ALTA"
        inviable         = False
        cascada_paso     = None
        cascada_desc     = None

    elif anios >= UMBRAL_ESTANDAR:
        nivel            = "Estándar"
        codigo           = "CS-ESTANDAR"
        inviable         = False
        cascada_paso     = None
        cascada_desc     = None

    elif anios >= UMBRAL_REDUCIDA:
        nivel            = "Reducida"
        codigo           = "CS-REDUCIDA"
        inviable         = False
        cascada_paso     = None
        cascada_desc     = None

    elif anios >= UMBRAL_MINIMO:
        nivel            = "Experimental"
        codigo           = "CS-EXPERIMENTAL"
        inviable         = False
        cascada_paso     = 3        # Fase 1 — siempre paso 3
        cascada_desc     = CASCADA[3]

    else:
        nivel            = "Inviable"
        codigo           = "CS-INVIABLE"
        inviable         = True
        cascada_paso     = None
        cascada_desc     = None

    resultado = {
        "anios_historial":      anios,
        "nivel":                nivel,
        "codigo":               codigo,
        "inviable":             inviable,
        "cascada_paso":         cascada_paso,
        "cascada_descripcion":  cascada_desc,
    }

    # Campo auxiliar para el governor (no va en analysis_report.json)
    if inviable:
        resultado["_accion_governor"] = (
            f"ESCALAMIENTO OBLIGATORIO — historial de "
            f"{round(anios * 12)} meses es menor al mínimo de 3 meses."
        )
    elif codigo == "CS-EXPERIMENTAL":
        resultado["_accion_governor"] = (
            "ADVERTENCIA — historial en rango Experimental. "
            "Cascada cold start activa (paso 3 en Fase 1)."
        )
    else:
        resultado["_accion_governor"] = None

    return resultado


# ── CLI ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse, json

    parser = argparse.ArgumentParser(
        description="Evalúa el nivel de confianza cold start según el historial disponible."
    )
    parser.add_argument(
        "--anios",
        type=float,
        required=True,
        help="Años de historial de pedidos disponible (ej: 2.5 = dos años y medio, 0.5 = seis meses).",
    )
    args = parser.parse_args()

    resultado = evaluar_cold_start(args.anios)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))

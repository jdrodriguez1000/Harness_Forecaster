"""Generador reproducible del dataset e2e del harness 015 Intake.

Cliente ficticio: Conservas del Pacífico S.A.S. (Cali, Colombia) — fabricante B2B
de conservas y alimentos procesados, escala mediana (categoría M/L). Vende a
cadenas de supermercados, distribuidores mayoristas y tiendas (clientes XYZ).

Produce DOS archivos en `test_data/015_intake_e2e/`:

  1. orders.csv               → entrega principal (camino feliz + anomalías sembradas)
  2. orders_sin_cantidad.csv  → entrega de rechazo (sin la columna de cantidad)

Características de orders.csv (consistente con el brief.md de este mismo cliente):
  - Formato:    CSV ';' (export típico de Excel en locale español)
  - Encoding:   cp1252 (acentos y ñ → el CANARIO que debe sobrevivir byte-a-byte
                de P1 a Bronce; si se corrompe, el dedupe miente)
  - Esquema 1:  4 campos mínimos (fecha_pedido, id_cliente, id_producto,
                cantidad_solicitada) vía sinónimos + 5 ideales presentes
                (categoria, ciudad, cantidad_entregada, estado_pedido, unidad_medida)
  - Escala:     ~45 clientes XYZ × ~350 SKUs, ~4.000 filas de pedidos
  - Rango real: ~2,2 años (2024-01 → 2026-03). El brief declara "unos 3 años"
                → discrepancia > 20% → range_evaluator emite WARNING (no bloquea)
  - Anomalías sembradas (P3/P4 cuentan, NO detienen el pipeline):
      * ~40 filas con cantidad_solicitada NEGATIVA  → errores de tipo (P3)
      * ~50 filas duplicado interno exacto (misma clave fecha+cliente+producto) → P4

Resultado esperado del 015 sobre orders.csv:
  estado = EXECUTION_COMPLETE · Bronce bit-exacto + SHA-256 en manifest ·
  evento intake_complete como último artefacto · C aprueba (≥ 0.80) ·
  intake_report con: errores_tipo{cantidad_negativa: ~40}, duplicados_internos: ~50,
  warning de rango (declarado 3 vs real ~2,2), ideales faltantes (déficit ISD).

Resultado esperado del 015 sobre orders_sin_cantidad.csv:
  estado = REJECTED_STRUCTURE · intake_rejection.json · SIN Bronce NI evento (veto D2).

Reproducible: semilla fija. Re-ejecutar regenera byte-idénticos los CSV.

Uso:  python test_data/015_intake_e2e/_build_dataset.py
"""

from __future__ import annotations

import csv
import io
import os
import random
from datetime import date, timedelta

AQUI = os.path.dirname(os.path.abspath(__file__))
SEMILLA = 20260613

# --- Catálogos del cliente (con acentos / ñ a propósito: prueban el canario cp1252) ---

CIUDADES = ["Bogotá", "Medellín", "Cali", "Barranquilla", "Bucaramanga", "Pereira"]

CATEGORIAS = {
    "PES": ("Conservas de pescado", ["Atún en aceite 170g", "Atún en agua 170g",
                                      "Sardinas en salsa de tomate", "Atún lomitos 80g"]),
    "VEG": ("Vegetales enlatados", ["Maíz dulce 300g", "Arvejas verdes 300g",
                                     "Fríjol cargamanto 400g", "Champiñones rebanados"]),
    "SAL": ("Salsas y aderezos", ["Salsa de tomate 200g", "Mayonesa 380g",
                                   "Mostaza 250g", "Ají picante 150g"]),
    "GRA": ("Granos y cereales", ["Lenteja 500g", "Garbanzo 500g", "Avena en hojuelas"]),
    "DUL": ("Dulces y mermeladas", ["Mermelada de mora 300g", "Arequipe 250g",
                                     "Bocadillo veleño 400g"]),
}
UNIDADES = ["Caja x 24", "Caja x 12", "Unidad", "Display x 6"]
ESTADOS = ["Entregado", "Entregado", "Entregado", "Pendiente", "Cancelado"]

# Cabeceras estilo export colombiano — mapean al Esquema 1 vía sinónimos/normalización.
CABECERAS = [
    "Fecha del pedido",   # → fecha_pedido (mínimo)
    "Código cliente",     # → id_cliente   (mínimo)
    "Código producto",    # → id_producto  (mínimo)
    "Cantidad pedida",    # → cantidad_solicitada (mínimo)
    "Nombre producto",    # extra (no ideal)
    "Categoría",          # → categoria        (ideal)
    "Ciudad",             # → ciudad           (ideal)
    "Cantidad entregada", # → cantidad_entregada (ideal)
    "Estado pedido",      # → estado_pedido    (ideal)
    "Unidad medida",      # → unidad_medida    (ideal)
]


def _catalogo_productos(rng: random.Random):
    """~350 SKUs repartidos en las categorías, cada uno con nombre/categoría/unidad."""
    productos = []
    n_por_prefijo = 70
    for prefijo, (categoria, nombres) in CATEGORIAS.items():
        for i in range(1, n_por_prefijo + 1):
            sku = f"{prefijo}-{i:03d}"
            nombre = rng.choice(nombres)
            unidad = rng.choice(UNIDADES)
            productos.append((sku, nombre, categoria, unidad))
    return productos


def _generar_filas(rng: random.Random):
    """Lista de filas (dict por CABECERAS) del histórico de pedidos."""
    clientes = [f"CLI-{i:03d}" for i in range(1, 46)]          # 45 clientes XYZ
    productos = _catalogo_productos(rng)                       # ~350 SKUs
    ciudad_de = {c: rng.choice(CIUDADES) for c in clientes}    # cada cliente, una ciudad

    inicio = date(2024, 1, 8)
    fin = date(2026, 3, 20)                                    # ~2,2 años de rango real
    span_dias = (fin - inicio).days

    filas = []
    n_base = 4000
    for _ in range(n_base):
        cli = rng.choice(clientes)
        sku, nombre, categoria, unidad = rng.choice(productos)
        f = inicio + timedelta(days=rng.randint(0, span_dias))
        cant = rng.choice([6, 12, 12, 24, 24, 48, 60, 120, 240])
        # cantidad entregada: usualmente == pedida, a veces un poco menos
        entregada = cant if rng.random() < 0.8 else max(0, cant - rng.choice([6, 12, 24]))
        filas.append({
            "Fecha del pedido": f.isoformat(),
            "Código cliente": cli,
            "Código producto": sku,
            "Cantidad pedida": cant,
            "Nombre producto": nombre,
            "Categoría": categoria,
            "Ciudad": ciudad_de[cli],
            "Cantidad entregada": entregada,
            "Estado pedido": rng.choice(ESTADOS),
            "Unidad medida": unidad,
        })

    # --- Anomalía 1: ~40 cantidades NEGATIVAS (errores de tipo P3) ---
    for idx in rng.sample(range(len(filas)), 40):
        filas[idx]["Cantidad pedida"] = -abs(filas[idx]["Cantidad pedida"])

    # --- Anomalía 2: ~50 DUPLICADOS internos exactos (misma clave P4) ---
    for idx in rng.sample(range(len(filas)), 50):
        filas.append(dict(filas[idx]))

    rng.shuffle(filas)
    return filas


def _escribir_csv(path: str, filas, cabeceras):
    """Escribe ';' cp1252 sin BOM, fin de línea \\r\\n (estilo Excel Windows)."""
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cabeceras, delimiter=";",
                       lineterminator="\r\n", extrasaction="ignore")
    w.writeheader()
    for fila in filas:
        w.writerow(fila)
    datos = buf.getvalue().encode("cp1252")
    with open(path, "wb") as fh:
        fh.write(datos)
    return len(filas), len(datos)


def main():
    rng = random.Random(SEMILLA)
    filas = _generar_filas(rng)

    # 1) Entrega principal — camino feliz + anomalías
    p1 = os.path.join(AQUI, "orders.csv")
    n1, b1 = _escribir_csv(p1, filas, CABECERAS)

    # 2) Entrega de rechazo — sin la columna de cantidad (sin 'Cantidad pedida' NI sinónimo)
    cabeceras_sin_cant = [c for c in CABECERAS if c != "Cantidad pedida"]
    p2 = os.path.join(AQUI, "orders_sin_cantidad.csv")
    # reusar un subconjunto de filas (las primeras 200 bastan para el rechazo)
    n2, b2 = _escribir_csv(p2, filas[:200], cabeceras_sin_cant)

    negativas = sum(1 for f in filas if f["Cantidad pedida"] < 0)
    print(f"[OK] orders.csv               {n1} filas · {b1} bytes · cp1252 · ';'")
    print(f"      - cantidades negativas (P3): {negativas}")
    print(f"      - duplicados internos (P4):  ~50 (clave fecha+cliente+producto)")
    print(f"      - rango real: 2024-01-08 a 2026-03-20 (~2,2 anios)")
    print(f"[OK] orders_sin_cantidad.csv  {n2} filas · {b2} bytes · (sin columna de cantidad)")


if __name__ == "__main__":
    main()

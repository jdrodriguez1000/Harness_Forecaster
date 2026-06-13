"""Tests del PASO 5 — format_detector.py (P1 detección de formato).

Contrato (plan/015_intake.md, PASO 5):
  detect_format(raw_bytes, filename, huella=None) -> FormatSpec

Detecta tipo (csv/xlsx/xls), encoding (cascada utf-8 → utf-8-sig → cp1252/latin-1),
delimitador (, ; |), hoja y fila de cabecera en Excel. Marca ambiguo=True cuando
la heurística no resuelve con confianza (el processor escala al operador) y
corrupto=True para binarios no tabulares. Si `huella` existe, la respeta sin
re-detectar.

EL CANARIO: los acentos cp1252 deben sobrevivir intactos (D1/D5). Si se corrompen
aquí, id_cliente/id_producto cambian y el dedupe miente.
"""

import io

from openpyxl import Workbook

from pipeline.format_detector import FormatSpec, detect_format


def _xlsx_bytes(filas_por_hoja):
    """Construye un .xlsx en memoria. filas_por_hoja: {hoja: [fila, ...]}."""
    wb = Workbook()
    wb.remove(wb.active)
    for nombre, filas in filas_por_hoja.items():
        ws = wb.create_sheet(title=nombre)
        for fila in filas:
            ws.append(fila)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# --- CSV: delimitador + encoding ---

def test_csv_coma_utf8():
    raw = "fecha_pedido,id_cliente,id_producto,cantidad_solicitada\n2026-01-01,C1,P1,5\n".encode("utf-8")
    spec = detect_format(raw, "orders.csv")
    assert spec.tipo == "csv"
    assert spec.delimitador == ","
    assert spec.encoding == "utf-8"
    assert spec.corrupto is False
    assert spec.ambiguo is False


def test_csv_punto_y_coma_cp1252_acentos_intactos():
    # EL CANARIO: 'Categoría' con í (0xED en cp1252). utf-8 estricto falla → cp1252.
    texto = "fecha_pedido;id_cliente;Categoría\n2026-01-01;Pingüino;Camión\n"
    raw = texto.encode("cp1252")
    spec = detect_format(raw, "orders.csv")
    assert spec.tipo == "csv"
    assert spec.delimitador == ";"
    assert spec.encoding == "cp1252"
    # los acentos sobreviven: decodificar con el encoding detectado reproduce el original
    assert raw.decode(spec.encoding) == texto
    assert "Categoría" in raw.decode(spec.encoding)
    assert "Categorâ" not in raw.decode(spec.encoding)  # no mojibake


def test_csv_pipe():
    raw = "a|b|c\n1|2|3\n4|5|6\n".encode("utf-8")
    spec = detect_format(raw, "orders.csv")
    assert spec.tipo == "csv"
    assert spec.delimitador == "|"


def test_csv_utf8_con_bom():
    raw = "﻿fecha,cliente\n2026-01-01,C1\n".encode("utf-8-sig")
    spec = detect_format(raw, "orders.csv")
    assert spec.tipo == "csv"
    assert spec.encoding == "utf-8-sig"
    assert spec.delimitador == ","


# --- Excel: hoja y fila de cabecera ---

def test_xlsx_cabecera_fila_1():
    raw = _xlsx_bytes({"Datos": [
        ["fecha_pedido", "id_cliente", "id_producto", "cantidad_solicitada"],
        ["2026-01-01", "C1", "P1", 5],
    ]})
    spec = detect_format(raw, "orders.xlsx")
    assert spec.tipo == "xlsx"
    assert spec.hoja == "Datos"
    assert spec.fila_cabecera == 1
    assert spec.ambiguo is False


def test_xlsx_cabecera_fila_3():
    raw = _xlsx_bytes({"Hoja1": [
        [None, None, None],
        [None, None, None],
        ["fecha_pedido", "id_cliente", "cantidad_solicitada"],
        ["2026-01-01", "C1", 5],
    ]})
    spec = detect_format(raw, "orders.xlsx")
    assert spec.tipo == "xlsx"
    assert spec.fila_cabecera == 3


def test_xlsx_multi_hoja_es_ambiguo():
    raw = _xlsx_bytes({
        "Ventas": [["fecha", "x"], ["2026-01-01", 1]],
        "Resumen": [["total"], [10]],
    })
    spec = detect_format(raw, "orders.xlsx")
    assert spec.tipo == "xlsx"
    assert spec.ambiguo is True  # requiere confirmación del operador
    assert set(spec.hojas_disponibles) == {"Ventas", "Resumen"}


def test_xls_legacy_detecta_tipo():
    # firma OLE2 (Compound File) — basta para declarar tipo 'xls'
    raw = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"\x00" * 512
    spec = detect_format(raw, "legacy.xls")
    assert spec.tipo == "xls"


# --- Corrupto / no tabular ---

def test_binario_corrupto():
    raw = bytes([0x00, 0xFF, 0x13, 0x37, 0x00, 0x90, 0x8D]) * 20
    spec = detect_format(raw, "binario_corrupto.bin")
    assert spec.corrupto is True


# --- Huella provista: la respeta sin re-detectar ---

def test_huella_respetada_sin_redetectar():
    # raw_bytes deliberadamente vacío/basura: si respeta la huella, ni lo mira
    huella = {"tipo": "csv", "encoding": "cp1252", "delimitador": ";"}
    spec = detect_format(b"", "orders.csv", huella=huella)
    assert spec.tipo == "csv"
    assert spec.encoding == "cp1252"
    assert spec.delimitador == ";"
    assert spec.fuente == "huella"


def test_huella_excel_respetada():
    huella = {"tipo": "xlsx", "hoja": "Datos", "fila_cabecera": 3}
    spec = detect_format(b"", "orders.xlsx", huella=huella)
    assert spec.tipo == "xlsx"
    assert spec.hoja == "Datos"
    assert spec.fila_cabecera == 3
    assert spec.fuente == "huella"
    assert isinstance(spec, FormatSpec)

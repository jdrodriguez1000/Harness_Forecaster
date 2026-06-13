"""P4 — Detección de duplicados. deduplicator.py

Clave compuesta: (fecha_pedido, id_cliente, id_producto), normalizada a string.

Dos comportamientos según el modo (D4):
  - Batch:       count_internal_duplicates(df) -> int
                 Cuenta los duplicados internos como ANOMALÍA pero NO elimina
                 filas: se copian a Bronce y el 020 los contabiliza en Unicidad.
  - Incremental: diff_against_bronze(df, manifest_path) -> (df_nuevos, n_excluidos)
                 Compara contra la unión lógica del Bronce acumulado (vía
                 _manifest.json → archivos previos) y devuelve SOLO los registros
                 nuevos; los ya existentes se excluyen (no se re-persisten).

Ver plan/015_intake.md (PASO 8) y brief/015_intake.md (P4).
"""

from __future__ import annotations

import io
import json
import os

import pandas as pd

from pipeline.format_detector import detect_format
from pipeline.source_adapter import ManualOperatorAdapter
from pipeline.type_validator import _resolver_columna

_CAMPOS_CLAVE = ("fecha_pedido", "id_cliente", "id_producto")


def keys_from_df(df) -> list:
    """Lista de claves compuestas (tuplas de string normalizado) del DataFrame.

    Resuelve las columnas por nombre canónico (tolera mayúsculas/acentos/sinónimos).
    Una columna clave ausente se trata como cadena vacía en esa posición.
    """
    cols = {campo: _resolver_columna(df, campo) for campo in _CAMPOS_CLAVE}
    claves = []
    for _, fila in df.iterrows():
        clave = tuple(
            str(fila[cols[campo]]).strip() if cols[campo] is not None else ""
            for campo in _CAMPOS_CLAVE
        )
        claves.append(clave)
    return claves


def count_internal_duplicates(df) -> int:
    """Nº de filas duplicadas internas = total - claves únicas. No elimina nada."""
    claves = keys_from_df(df)
    return len(claves) - len(set(claves))


def _read_bronze_file(path: str):
    """Relee un archivo Bronce CSV previo como DataFrame de strings.

    Usa el mismo adaptador + detector de formato del pipeline, de modo que un
    Bronce en cp1252 con acentos se relee fielmente (encadena con el canario P5).
    """
    snap = ManualOperatorAdapter().read_snapshot(path)
    spec = detect_format(snap.raw_bytes, path)
    texto = snap.raw_bytes.decode(spec.encoding)
    return pd.read_csv(io.StringIO(texto), sep=spec.delimitador, dtype=str)


def load_bronze_keys(manifest_path: str) -> set:
    """Unión lógica de claves del Bronce acumulado declarado en el manifest.

    Si el manifest no existe (primera entrega incremental) → conjunto vacío.
    """
    if not os.path.isfile(manifest_path):
        return set()

    bronze_dir = os.path.dirname(manifest_path)
    with open(manifest_path, "r", encoding="utf-8") as fh:
        manifest = json.load(fh)

    claves: set = set()
    for entrega in manifest.get("entregas", []):
        archivo = entrega.get("archivo")
        if not archivo:
            continue
        path = os.path.join(bronze_dir, archivo)
        if os.path.isfile(path):
            claves.update(keys_from_df(_read_bronze_file(path)))
    return claves


def diff_against_bronze(df, manifest_path: str):
    """Devuelve (df_nuevos, n_excluidos) tras excluir claves ya en Bronce previo."""
    previas = load_bronze_keys(manifest_path)
    claves = keys_from_df(df)
    mask = [clave not in previas for clave in claves]
    df_nuevos = df[pd.Series(mask, index=df.index)].copy()
    n_excluidos = len(df) - len(df_nuevos)
    return df_nuevos, n_excluidos

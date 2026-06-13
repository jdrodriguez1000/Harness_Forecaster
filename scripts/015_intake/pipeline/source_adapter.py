"""P1 — Recepción. source_adapter.py

Devuelve siempre un snapshot tabular CRUDO: bytes + formato declarado por
extensión + metadata de fuente. NO decodifica, NO interpreta, NO detecta el
formato real (eso es P1/format_detector). Es la frontera de entrada del 015.

Fase 1 (DEC-057, decisión 2): solo existe `ManualOperatorAdapter`, que lee un
archivo que el operador dejó en la carpeta del tenant. La interfaz `SourceAdapter`
documenta —sin construir— conectores futuros (SFTP/ERP/BD): cualquier conector
debe MATERIALIZAR un snapshot en disco antes de tocar el 015, porque el invariante
Bronce exige una copia bit-exacta del origen.

Ver plan/015_intake.md (PASO 4) y brief/015_intake.md (P1).
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


class SourceNotFound(Exception):
    """La ruta no apunta a un archivo legible (inexistente o no es un archivo)."""


@dataclass(frozen=True)
class Snapshot:
    """Snapshot tabular crudo entregado por un adaptador de fuente.

    raw_bytes        bytes exactos del archivo origen (sin decodificar).
    formato_declarado extensión normalizada (sin punto, minúsculas): 'csv'|'xlsx'|'xls'|...
                     Es lo DECLARADO por el nombre, no el formato verificado.
    source_metadata  procedencia: path, size_bytes, mtime.
    vacio            True si el archivo tiene 0 bytes (P1 lo rechaza después).
    """

    raw_bytes: bytes
    formato_declarado: str
    source_metadata: dict = field(default_factory=dict)
    vacio: bool = False


class SourceAdapter(ABC):
    """Interfaz de costura de fuentes. Fase 1 solo implementa el manual.

    Conectores futuros (SFTP/ERP/BD) implementan esta misma firma y deben
    materializar un archivo antes de devolver el snapshot — el 015 nunca
    ingiere un stream que no tenga respaldo bit-exacto en disco.
    """

    @abstractmethod
    def read_snapshot(self, path: str) -> Snapshot:  # pragma: no cover - contrato
        ...


class ManualOperatorAdapter(SourceAdapter):
    """Lee un archivo del filesystem dejado por el operador Triple S.

    No modifica el archivo origen (abre en modo binario de solo lectura).
    """

    def read_snapshot(self, path: str) -> Snapshot:
        if not os.path.isfile(path):
            raise SourceNotFound(f"No es un archivo legible: {path}")

        stat = os.stat(path)
        with open(path, "rb") as fh:
            raw_bytes = fh.read()

        formato_declarado = os.path.splitext(path)[1].lstrip(".").lower()

        source_metadata = {
            "path": path,
            "size_bytes": stat.st_size,
            "mtime": stat.st_mtime,
        }

        return Snapshot(
            raw_bytes=raw_bytes,
            formato_declarado=formato_declarado,
            source_metadata=source_metadata,
            vacio=(stat.st_size == 0),
        )

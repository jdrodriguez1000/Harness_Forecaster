"""P6 — Escritura de la capa Bronce. bronze_writer.py — MÓDULO CRÍTICO (veto D5).

write_bronze(raw_bytes, bronze_dir, mode, delivery_id, esquema, ...) -> BronzeFile

Materializa el invariante del medallón (CLAUDE.md): el Bronce es una copia
INTOCABLE y BIT-EXACTA del origen. Por eso escribe los MISMOS bytes del snapshot
(NO re-serializa desde el DataFrame — eso cambiaría comillas, decimales y orden y
rompería D5). El DataFrame solo sirvió para validar y contar.

Garantías:
  - SHA-256 del archivo escrito, persistido en _manifest.json.
  - Write-once: si ya existe con el hash esperado → NO reescribe (idempotencia
    para recuperación CP-03↔CP-05). Si existe con hash distinto → error duro
    (BronzeImmutabilityError) — Bronce nunca se sobrescribe salvo rework D5
    controlado y registrado fuera de este módulo.
  - Incremental = un archivo inmutable por entrega + append a 'entregas' del
    manifest. NUNCA concatena ni reescribe un archivo acumulado.

Ver plan/015_intake.md (PASO 9) y brief/015_intake.md (P6).
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone

_PREFIJO = {1: "orders", 2: "inventory"}


class BronzeImmutabilityError(Exception):
    """Intento de sobrescribir un archivo Bronce existente con contenido distinto."""


@dataclass
class BronzeFile:
    """Resultado de la escritura Bronce de una entrega.

    rewritten=True  → el archivo se escribió en esta llamada.
    rewritten=False → ya existía bit-idéntico; no se tocó (idempotencia).
    """

    path: str
    archivo: str
    sha256: str
    rewritten: bool
    manifest_entry: dict = field(default_factory=dict)


def _nombre_archivo(esquema: int, mode: str, delivery_id: str, extension: str) -> str:
    prefijo = _PREFIJO.get(esquema, "data")
    return f"{prefijo}_{mode}_{delivery_id}.{extension}"


def _sha256(raw_bytes: bytes) -> str:
    return hashlib.sha256(raw_bytes).hexdigest()


def write_bronze(
    raw_bytes: bytes,
    bronze_dir: str,
    mode: str,
    delivery_id: str,
    esquema: int,
    *,
    tenant_id: str = "",
    extension: str = "csv",
    rows: int | None = None,
    rango: dict | None = None,
    timestamp: str | None = None,
) -> BronzeFile:
    os.makedirs(bronze_dir, exist_ok=True)
    archivo = _nombre_archivo(esquema, mode, delivery_id, extension)
    path = os.path.join(bronze_dir, archivo)
    nuevo_hash = _sha256(raw_bytes)

    # Write-once: respeta un Bronce preexistente.
    if os.path.isfile(path):
        existente_hash = _sha256(open(path, "rb").read())
        if existente_hash != nuevo_hash:
            raise BronzeImmutabilityError(
                f"Bronce inmutable: {archivo} ya existe con hash distinto "
                f"({existente_hash[:12]}… ≠ {nuevo_hash[:12]}…)."
            )
        rewritten = False
    else:
        with open(path, "wb") as fh:
            fh.write(raw_bytes)
        rewritten = True

    entry = _actualizar_manifest(
        bronze_dir, tenant_id, delivery_id, mode, archivo, esquema,
        nuevo_hash, rows, rango, timestamp,
    )

    return BronzeFile(path=path, archivo=archivo, sha256=nuevo_hash,
                      rewritten=rewritten, manifest_entry=entry)


def _actualizar_manifest(
    bronze_dir, tenant_id, delivery_id, mode, archivo, esquema,
    sha256, rows, rango, timestamp,
) -> dict:
    manifest_path = os.path.join(bronze_dir, "_manifest.json")
    if os.path.isfile(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as fh:
            manifest = json.load(fh)
    else:
        manifest = {"tenant_id": tenant_id, "entregas": []}

    if tenant_id and not manifest.get("tenant_id"):
        manifest["tenant_id"] = tenant_id

    entry = {
        "delivery_id": delivery_id,
        "mode": mode,
        "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
        "archivo": archivo,
        "esquema": esquema,
        "sha256": sha256,
        "rows": rows,
        "rango": rango or {"fecha_min": None, "fecha_max": None},
    }

    # Idempotencia del manifest: no duplicar una entrada ya registrada (mismo archivo+hash).
    for existente in manifest["entregas"]:
        if existente.get("archivo") == archivo and existente.get("sha256") == sha256:
            return existente

    manifest["entregas"].append(entry)
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    return entry

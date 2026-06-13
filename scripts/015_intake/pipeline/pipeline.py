"""P1→P8 — Orquestación del intake. pipeline.py (el intake-processor).

run_intake(client_config, snapshot_path, persistence) -> IntakeResult

Encadena los módulos de los PASOS 4–10 en el orden estricto del brief y respeta
los gates. Es el único punto donde se materializan artefactos en disco.

Orden y garantías (brief §2.5, garantía de atomicidad del handoff):
  P1  recepción + detección de formato
        · vacío/corrupto      → WORKER_FAILED   (intake_rejection.json, sin Bronce ni evento)
        · ambiguo (Excel/enc) → PENDING_OPERATOR_INPUT (escalamiento, sin Bronce ni evento)
  P2  GATE de estructura (veto D2)
        · falta un mínimo     → REJECTED_STRUCTURE (intake_rejection.json, SIN Bronce ni evento)
  P3  tipos  · P4 duplicados · P5 rango   (cuentan, NUNCA detienen — D3)
  P6  Bronce bit-exacto + SHA-256 + manifest (veto D5)
  P7  intake_report.json + intake_log (fallback JSON, _pendiente_supabase)
  P8  evento intake_complete — ÚLTIMO artefacto. Si algo falla antes → SIN evento.

Invariantes (progress.md, "Invariantes que el PASO 11 debe respetar"):
  - Bronce = los BYTES del snapshot, nunca re-serializando el DataFrame (D5).
    El DataFrame solo valida y cuenta. En incremental, diff_against_bronze aporta
    el conteo `vs_bronce_previo` para el reporte; NO altera los bytes que se copian
    (la unión lógica del histórico vive en el manifest).
  - El canario cp1252 sobrevive byte-a-byte de P1 a Bronce.
  - El evento es siempre el último artefacto; el rechazo de estructura nunca crea Bronce.
  - Write-once idempotente: re-correr no reescribe Bronce → soporta recuperación CP-03↔CP-05.

Ver plan/015_intake.md (PASO 11) y brief/015_intake.md (P1→P8).
"""

from __future__ import annotations

import io
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone

import pandas as pd

from pipeline.bronze_writer import write_bronze
from pipeline.deduplicator import count_internal_duplicates, diff_against_bronze
from pipeline.format_detector import detect_format
from pipeline.range_evaluator import evaluate_range
from pipeline.report_builder import build_intake_log, build_report
from pipeline.schema_validator import validate_structure
from pipeline.source_adapter import ManualOperatorAdapter
from pipeline.type_validator import validate_types

_NEXT_HARNESSES = ["020_diagnosis", "025_refinery"]


@dataclass
class Persistence:
    """Rutas de salida. En Fase 1 todo es filesystem local (DEC-044).

    bronze_dir   carpeta 005_bronze del tenant: Bronce + _manifest.json + intake_report.json.
    events_dir   carpeta de eventos/coordinación: intake_complete / rejection / intake_log.
    """

    bronze_dir: str
    events_dir: str


@dataclass
class IntakeResult:
    """Resultado de una corrida del pipeline (lo que el Worker reporta a B).

    estado: EXECUTION_COMPLETE | REJECTED_STRUCTURE | PENDING_OPERATOR_INPUT | WORKER_FAILED.
    """

    estado: str
    tenant_id: str
    delivery_id: str
    mode: str
    bronze_files: list = field(default_factory=list)
    report: dict | None = None
    report_path: str | None = None
    manifest_path: str | None = None
    intake_log: dict | None = None
    intake_log_path: str | None = None
    event: dict | None = None
    event_path: str | None = None
    rejection: dict | None = None
    rejection_path: str | None = None
    escalation: dict | None = None


# --- helpers ---

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def _parse_dataframe(raw_bytes: bytes, spec):
    """DataFrame de strings para validar/contar (NUNCA para reescribir Bronce)."""
    if spec.tipo == "csv":
        text = raw_bytes.decode(spec.encoding)
        return pd.read_csv(io.StringIO(text), sep=spec.delimitador, dtype=str)
    engine = "openpyxl" if spec.tipo == "xlsx" else "xlrd"
    header = (spec.fila_cabecera - 1) if spec.fila_cabecera else 0
    return pd.read_excel(
        io.BytesIO(raw_bytes), sheet_name=spec.hoja, header=header, dtype=str, engine=engine
    )


def _rechazo(estado, cfg, ts, pers, *, motivo, detalle, faltantes=None):
    rej = {
        "_schema_version": 1,
        "tenant_id": cfg["tenant_id"],
        "delivery_id": cfg["delivery_id"],
        "mode": cfg["mode"],
        "timestamp": ts,
        "motivo": motivo,
        "detalle": detalle,
        "campos_minimos_faltantes": faltantes or [],
        "bronce_creado": False,
        "evento_emitido": False,
    }
    rej_path = os.path.join(pers.events_dir, f"intake_rejection_{cfg['delivery_id']}.json")
    _write_json(rej_path, rej)
    return IntakeResult(
        estado=estado, tenant_id=cfg["tenant_id"], delivery_id=cfg["delivery_id"],
        mode=cfg["mode"], rejection=rej, rejection_path=rej_path,
    )


def _procesar_esquema2(cfg, ts, pers):
    """Devuelve (schema2_dict, bronze_file|None). Esquema 2 NUNCA bloquea (brief §2.4.4)."""
    if not cfg.get("tiene_esquema2"):
        return {"status": "NOT_EXPECTED", "rows": 0, "errores_tipo": {}}, None

    path = cfg.get("esquema2_path")
    if not path or not os.path.isfile(path):
        return {"status": "EXPECTED_NOT_RECEIVED", "rows": 0, "errores_tipo": {}}, None

    snap = ManualOperatorAdapter().read_snapshot(path)
    spec = detect_format(snap.raw_bytes, path, huella=cfg.get("huella_esquema2"))
    if snap.vacio or spec.corrupto or spec.ambiguo:
        return {"status": "EXPECTED_NOT_RECEIVED", "rows": 0, "errores_tipo": {}}, None

    df = _parse_dataframe(snap.raw_bytes, spec)
    struct = validate_structure(df, 2)
    if not struct.aprobado:
        return {
            "status": "ESTRUCTURA_INVALIDA", "rows": len(df), "errores_tipo": {},
            "campos_minimos_faltantes": struct.campos_minimos_faltantes,
        }, None

    types = validate_types(df, 2)
    rng = evaluate_range(df, cfg.get("historial_declarado_anios"), campo_fecha="fecha")
    bf = write_bronze(
        snap.raw_bytes, pers.bronze_dir, cfg["mode"], cfg["delivery_id"], esquema=2,
        tenant_id=cfg["tenant_id"], extension=spec.tipo, rows=len(df),
        rango={"fecha_min": rng.fecha_min, "fecha_max": rng.fecha_max}, timestamp=ts,
    )
    schema2 = {
        "status": "CREATED", "rows": len(df), "errores_tipo": dict(types.errores),
    }
    return schema2, bf


def run_intake(client_config: dict, snapshot_path: str, persistence: Persistence) -> IntakeResult:
    cfg = dict(client_config)
    cfg.setdefault("delivery_id", datetime.now().strftime("%Y%m%d"))
    cfg.setdefault("mode", "batch")
    cfg.setdefault("tenant_id", "")
    ts = cfg.get("timestamp") or _now()
    pers = persistence

    # --- P1: recepción ---
    snap = ManualOperatorAdapter().read_snapshot(snapshot_path)
    if snap.vacio:
        return _rechazo("WORKER_FAILED", cfg, ts, pers,
                        motivo="FORMATO_VACIO", detalle="El archivo entregado tiene 0 bytes.")

    # --- P1: detección de formato ---
    spec = detect_format(snap.raw_bytes, snapshot_path, huella=cfg.get("huella"))
    if spec.corrupto:
        return _rechazo("WORKER_FAILED", cfg, ts, pers,
                        motivo="FORMATO_CORRUPTO",
                        detalle="Binario no tabular o encoding irresoluble.")
    if spec.ambiguo:
        esc = {
            "tipo": "excel" if spec.tipo in ("xlsx", "xls") else "encoding",
            "razon": "La heurística no resolvió el formato con confianza; requiere "
                     "confirmación del operador.",
            "propuesta": {
                "tipo": spec.tipo, "encoding": spec.encoding, "delimitador": spec.delimitador,
                "hoja": spec.hoja, "fila_cabecera": spec.fila_cabecera,
                "hojas_disponibles": spec.hojas_disponibles,
            },
        }
        return IntakeResult(
            estado="PENDING_OPERATOR_INPUT", tenant_id=cfg["tenant_id"],
            delivery_id=cfg["delivery_id"], mode=cfg["mode"], escalation=esc,
        )

    df = _parse_dataframe(snap.raw_bytes, spec)

    # --- P2: GATE de estructura (veto D2) ---
    struct = validate_structure(df, 1)
    if not struct.aprobado:
        return _rechazo("REJECTED_STRUCTURE", cfg, ts, pers,
                        motivo="ESTRUCTURA",
                        detalle="Falta al menos un campo mínimo del Esquema 1.",
                        faltantes=struct.campos_minimos_faltantes)

    # --- P3 tipos · P4 duplicados · P5 rango (cuentan, no detienen) ---
    types = validate_types(df, 1)
    rng = evaluate_range(df, cfg.get("historial_declarado_anios"))

    manifest_path = os.path.join(pers.bronze_dir, "_manifest.json")
    dup_internos = count_internal_duplicates(df)
    dup_vs_bronce = 0
    if cfg["mode"] == "incremental":
        _, dup_vs_bronce = diff_against_bronze(df, manifest_path)

    # --- P6: Bronce bit-exacto desde los BYTES del snapshot (veto D5) ---
    bf = write_bronze(
        snap.raw_bytes, pers.bronze_dir, cfg["mode"], cfg["delivery_id"], esquema=1,
        tenant_id=cfg["tenant_id"], extension=spec.tipo, rows=len(df),
        rango={"fecha_min": rng.fecha_min, "fecha_max": rng.fecha_max}, timestamp=ts,
    )
    bronze_files = [bf]

    schema2, bf2 = _procesar_esquema2(cfg, ts, pers)
    if bf2 is not None:
        bronze_files.append(bf2)

    # --- P7: reportes ---
    report = build_report(
        tenant_id=cfg["tenant_id"], delivery_id=cfg["delivery_id"], mode=cfg["mode"],
        format_spec=spec, struct_result=struct, type_result=types, range_result=rng,
        dup_internos=dup_internos, dup_vs_bronce=dup_vs_bronce, schema2=schema2,
        timestamp=ts,
    )
    report_path = os.path.join(pers.bronze_dir, "intake_report.json")
    _write_json(report_path, report)

    intake_log = build_intake_log(
        tenant_id=cfg["tenant_id"], delivery_id=cfg["delivery_id"], mode=cfg["mode"],
        bronze_files=bronze_files, report_path=report_path, event_emitted=False,
        created_at=ts,
    )
    intake_log_path = os.path.join(pers.events_dir, f"intake_log_{cfg['delivery_id']}.json")
    _write_json(intake_log_path, intake_log)

    # --- P8: evento intake_complete — ÚLTIMO artefacto ---
    event = {
        "event": "intake_complete",
        "estado": "pendiente",
        "tenant_id": cfg["tenant_id"],
        "delivery_id": cfg["delivery_id"],
        "mode": cfg["mode"],
        "timestamp": ts,
        "bronze_path": pers.bronze_dir,
        "manifest_path": manifest_path,
        "intake_report_path": report_path,
        "next_harnesses": list(_NEXT_HARNESSES),
    }
    event_path = os.path.join(pers.events_dir, f"intake_complete_{cfg['delivery_id']}.json")
    _write_json(event_path, event)

    # intake_log refleja que el evento ya se emitió
    intake_log["event_emitted"] = True
    _write_json(intake_log_path, intake_log)

    return IntakeResult(
        estado="EXECUTION_COMPLETE", tenant_id=cfg["tenant_id"], delivery_id=cfg["delivery_id"],
        mode=cfg["mode"], bronze_files=bronze_files, report=report, report_path=report_path,
        manifest_path=manifest_path, intake_log=intake_log, intake_log_path=intake_log_path,
        event=event, event_path=event_path,
    )

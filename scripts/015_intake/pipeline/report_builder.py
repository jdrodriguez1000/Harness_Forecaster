"""P7 — Generación de reportes. report_builder.py

build_report(...) -> dict       (intake_report.json)
build_intake_log(...) -> dict   (fila intake_log; _pendiente_supabase en Fase 1)

Consolida los resultados de P1–P6 en los dos artefactos de la cadena de evidencia
del ISD que leerá el 020. Conforme a templates/015_intake/schemas/*.json.

Regla del brief (ancla 0.8): si P5 detectó discrepancia de rango, el warning va
SIEMPRE tanto en `rango_declarado_vs_real` como en la lista legible `warnings`.

Ver plan/015_intake.md (PASO 10) y brief/015_intake.md (P7).
"""

from __future__ import annotations

from datetime import datetime, timezone

_SCHEMA2_DEFAULT = {
    "status": "NOT_EXPECTED",
    "rows": 0,
    "campos_minimos_faltantes": [],
    "errores_tipo": {},
}


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_report(
    *,
    tenant_id: str,
    delivery_id: str,
    mode: str,
    format_spec,
    struct_result,
    type_result,
    range_result,
    dup_internos: int = 0,
    dup_vs_bronce: int = 0,
    schema2: dict | None = None,
    extra_warnings: list | None = None,
    timestamp: str | None = None,
) -> dict:
    warnings = list(extra_warnings or [])

    rango = {
        "declarado_anios": range_result.anios_declarados,
        "real_anios": range_result.anios_real,
        "discrepancia_pct": range_result.discrepancia_pct,
        "warning": range_result.warning,
    }
    if range_result.warning:
        warnings.append(
            f"Rango temporal real ({range_result.anios_real:.1f} años) difiere "
            f"{range_result.discrepancia_pct:.0f}% del historial declarado "
            f"({range_result.anios_declarados} años)."
        )

    return {
        "_schema_version": 1,
        "tenant_id": tenant_id,
        "delivery_id": delivery_id,
        "mode": mode,
        "timestamp": timestamp or _ahora(),
        "format": {
            "tipo": format_spec.tipo,
            "delimitador": format_spec.delimitador,
            "encoding": format_spec.encoding,
            "hoja": format_spec.hoja,
            "fila_cabecera": format_spec.fila_cabecera,
            "huella_reutilizada": format_spec.fuente == "huella",
        },
        "schema1": {
            "rows": type_result.filas_evaluadas,
            "campos_minimos_presentes": struct_result.campos_minimos_presentes,
            "campos_minimos_faltantes": struct_result.campos_minimos_faltantes,
            "campos_ideales_presentes": struct_result.campos_ideales_presentes,
            "campos_ideales_faltantes": struct_result.campos_ideales_faltantes,
            "errores_tipo": dict(type_result.errores),
            "duplicados": {
                "internos": dup_internos,
                "vs_bronce_previo": dup_vs_bronce,
            },
            "rango_temporal": {
                "fecha_min": range_result.fecha_min,
                "fecha_max": range_result.fecha_max,
                "dias_cubiertos": range_result.dias_cubiertos,
            },
        },
        "schema2": dict(schema2) if schema2 is not None else dict(_SCHEMA2_DEFAULT),
        "rango_declarado_vs_real": rango,
        "warnings": warnings,
    }


def _file_entry(bronze_file) -> dict:
    """Entrada `files` (JSONB) a partir de un BronzeFile."""
    meta = getattr(bronze_file, "manifest_entry", {}) or {}
    rango = meta.get("rango") or {}
    return {
        "path": bronze_file.path,
        "esquema": meta.get("esquema"),
        "sha256": bronze_file.sha256,
        "rows": meta.get("rows"),
        "date_range": {
            "min": rango.get("fecha_min"),
            "max": rango.get("fecha_max"),
        },
    }


def build_intake_log(
    *,
    tenant_id: str,
    delivery_id: str,
    mode: str,
    bronze_files: list,
    report_path: str,
    event_emitted: bool = False,
    created_at: str | None = None,
) -> dict:
    return {
        "_schema_version": 1,
        "_pendiente_supabase": True,
        "tenant_id": tenant_id,
        "delivery_id": delivery_id,
        "mode": mode,
        "created_at": created_at or _ahora(),
        "files": [_file_entry(bf) for bf in bronze_files],
        "report_path": report_path,
        "event_emitted": event_emitted,
    }

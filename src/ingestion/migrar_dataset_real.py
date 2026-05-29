"""Migracion del dataset real del reto a CSVs y Supabase.

Uso:
  python src/ingestion/migrar_dataset_real.py
  python src/ingestion/migrar_dataset_real.py --upload
  python src/ingestion/migrar_dataset_real.py --source data/raw
  python src/ingestion/migrar_dataset_real.py --excel data/raw/dataset.xlsx
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import unicodedata
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data" / "processed" / "real"
DEFAULT_LIMIT = 500

TABLE_ORDER = ["asegurados", "proveedores", "polizas", "siniestros", "documentos", "indice_documentos", "vehiculos"]

SUPABASE_COLUMNS = {
    "siniestros": [
        "id_siniestro",
        "id_poliza",
        "id_asegurado",
        "ramo",
        "placa_vehiculo",
        "cobertura",
        "fecha_ocurrencia",
        "fecha_reporte",
        "dias_entre_ocurrencia_reporte",
        "monto_reclamado",
        "monto_estimado",
        "monto_pagado",
        "estado",
        "sucursal",
        "id_proveedor",
        "descripcion",
        "documentos_completos",
        "proveedor_restrictivo",
        "dias_desde_inicio_poliza",
        "dias_desde_fin_poliza",
        "historial_siniestros_asegurado",
        "suma_asegurada",
        "similitud_narrativa",
        "numero_parte_policial",
        "beneficiario",
        "ciudad",
    ],
    "polizas": [
        "id_poliza",
        "id_asegurado",
        "ramo",
        "fecha_inicio",
        "fecha_fin",
        "suma_asegurada",
        "prima",
        "canal_venta",
        "estado_poliza",
    ],
    "asegurados": [
        "id_asegurado",
        "nombre_asegurado",
        "segmento",
        "ciudad",
        "antiguedad",
        "numero_polizas",
        "reclamos_ultimos_12_meses",
        "reclamos_historico_total",
        "reclamos_rc_sin_tercero",
        "perfil_riesgo",
    ],
    "proveedores": [
        "id_proveedor",
        "nombre",
        "tipo",
        "ciudad",
        "reclamos_asociados",
        "restrictivo",
        "motivo_restriccion",
        "monto_promedio_reclamado",
    ],
    "documentos": [
        "id_documento",
        "id_siniestro",
        "tipo_documento",
        "nombre_pdf",
    ],
    "indice_documentos": [
        "id_documento",
        "id_siniestro",
        "tipo_documento",
        "nombre_pdf",
    ],
    "vehiculos": [
        "id_vehiculo",
        "id_siniestro",
        "placa",
        "chasis",
        "motor",
        "marca",
        "modelo",
        "anio",
    ],
}

SOURCE_ALIASES = {
    "siniestros": ["1_siniestros.csv", "1_siniestros.xlsx", "siniestros.csv", "siniestros.xlsx"],
    "polizas": ["2_polizas.csv", "2_polizas.xlsx", "polizas.csv", "polizas.xlsx"],
    "asegurados": ["3_asegurados.csv", "3_asegurados.xlsx", "asegurados.csv", "asegurados.xlsx"],
    "proveedores": ["4_proveedores.csv", "4_proveedores.xlsx", "proveedores.csv", "proveedores.xlsx"],
    "documentos": ["5_documentos.csv", "5_documentos.xlsx", "documentos.csv", "documentos.xlsx"],
    "indice_documentos": ["6_indice_documentos.csv", "6_indice_documentos.xlsx", "indice_documentos.csv", "indice_documentos.xlsx"],
}

HEADER_MAPS = {
    "siniestros": {
        "id_siniestro": ["id siniestro", "id_siniestro"],
        "id_poliza": ["id poliza", "id_póliza", "id_poliza"],
        "id_asegurado": ["id asegurado", "id_asegurado"],
        "ramo": ["ramo"],
        "placa_vehiculo": ["placa vehiculo asegurado", "placa vehiculo", "placa_vehiculo"],
        "cobertura": ["cobertura"],
        "fecha_ocurrencia": ["fecha ocurrencia", "fecha_ocurrencia"],
        "fecha_reporte": ["fecha reporte", "fecha_reporte"],
        "dias_entre_ocurrencia_reporte": ["dias ocurr reporte", "dias entre ocurrencia reporte", "dias_entre_ocurrencia_reporte"],
        "monto_reclamado": ["monto reclamado $", "monto reclamado", "monto_reclamado"],
        "monto_estimado": ["monto estimado $", "monto estimado", "monto_estimado"],
        "monto_pagado": ["monto pagado $", "monto pagado", "monto_pagado"],
        "estado": ["estado"],
        "sucursal": ["sucursal"],
        "id_proveedor": ["id proveedor", "id_proveedor"],
        "descripcion": ["descripcion del evento", "descripcion", "descripcion_evento"],
        "documentos_completos": ["docs completos", "documentos completos", "documentos_completos"],
        "proveedor_restrictivo": ["prov lista restrictiva", "proveedor restrictivo", "proveedor_restrictivo"],
        "dias_desde_inicio_poliza": ["dias desde inicio poliza", "dias desde inicio de poliza", "dias_desde_inicio_poliza"],
        "dias_desde_fin_poliza": ["dias hasta fin poliza", "dias desde fin poliza", "dias_desde_fin_poliza"],
        "historial_siniestros_asegurado": ["n reclamos previos asegurado", "historial siniestros asegurado", "historial_siniestros_asegurado"],
        "suma_asegurada": ["suma asegurada $", "suma asegurada", "suma_asegurada"],
        "similitud_narrativa": ["similitud narrativa max", "similitud_narrativa"],
        "numero_parte_policial": ["numero parte policial", "numero_parte_policial"],
    },
    "polizas": {
        "id_poliza": ["id poliza", "id_poliza"],
        "id_asegurado": ["id asegurado", "id_asegurado"],
        "ramo": ["ramo"],
        "fecha_inicio": ["fecha inicio", "fecha_inicio"],
        "fecha_fin": ["fecha fin", "fecha_fin"],
        "suma_asegurada": ["suma asegurada $", "suma asegurada", "suma_asegurada"],
        "prima": ["prima anual $", "prima"],
        "canal_venta": ["canal venta", "canal_venta"],
        "estado_poliza": ["estado poliza", "estado_poliza"],
    },
    "asegurados": {
        "id_asegurado": ["id asegurado", "id_asegurado"],
        "nombre_asegurado": ["nombres asegurado", "nombre asegurado", "nombre_asegurado"],
        "segmento": ["segmento"],
        "ciudad": ["ciudad"],
        "antiguedad": ["antiguedad", "antiguedad años"],
        "numero_polizas": ["n polizas activas", "numero polizas", "numero_polizas"],
        "reclamos_ultimos_12_meses": ["n reclamos ultimos 12 meses", "reclamos ultimos 12 meses", "reclamos_ultimos_12_meses"],
        "reclamos_historico_total": ["n reclamos historico total", "reclamos historico total", "reclamos_historico_total"],
        "reclamos_rc_sin_tercero": ["reclamos rc sin tercero", "reclamos_rc_sin_tercero"],
        "perfil_riesgo": ["perfil riesgo historico", "perfil_riesgo"],
    },
    "proveedores": {
        "id_proveedor": ["id proveedor", "id_proveedor"],
        "nombre": ["nombre proveedor", "nombre", "proveedor"],
        "tipo": ["tipo"],
        "ciudad": ["ciudad"],
        "reclamos_asociados": ["n siniestros asociados", "reclamos asociados", "reclamos_asociados"],
        "restrictivo": ["en lista restrictiva", "restrictivo"],
        "motivo_restriccion": ["motivo restriccion", "motivo_restriccion"],
        "monto_promedio_reclamado": ["promedio monto $", "monto promedio", "monto_promedio_reclamado"],
    },
    "documentos": {
        "id_documento": ["id documento", "id_documento"],
        "id_siniestro": ["id siniestro", "id_siniestro"],
        "tipo_documento": ["tipo documento", "tipo_documento"],
        "nombre_pdf": ["nombre archivo pdf", "nombre pdf", "nombre_pdf"],
    },
    "indice_documentos": {
        "id_documento": ["doc id", "id documento", "id_documento"],
        "id_siniestro": ["siniestro vinculado", "id siniestro", "id_siniestro"],
        "tipo_documento": ["tipo", "tipo documento", "tipo_documento"],
        "nombre_pdf": ["nombre pdf", "nombre archivo pdf", "nombre_pdf"],
    },
}


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    return re.sub(r"\s+", " ", text)


def _to_bool(value) -> bool:
    if pd.isna(value):
        return False
    normalized = _norm(value)
    return normalized in {"si", "s", "yes", "true", "1", "verdadero", "y"}


def _to_float(value, default=0.0) -> float:
    if pd.isna(value):
        return default
    text = str(value).strip()
    if not text:
        return default
    text = text.replace("$", "").replace(" ", "")
    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    else:
        text = text.replace(",", ".")
    try:
        return float(text)
    except (TypeError, ValueError):
        return default


def _to_int(value, default=0) -> int:
    if pd.isna(value):
        return default
    text = str(value).strip()
    if not text:
        return default
    try:
        return int(round(float(text.replace("$", "").replace(",", "."))))
    except (TypeError, ValueError):
        return default


def _to_date(value):
    if pd.isna(value) or value == "":
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.strftime("%Y-%m-%d")


def _first_present(df: pd.DataFrame, names: list[str]) -> str | None:
    normalized = {_norm(col): col for col in df.columns}
    for name in names:
        key = _norm(name)
        if key in normalized:
            return normalized[key]
    return None


def _rename_known_columns(df: pd.DataFrame, mapping: dict[str, list[str]]) -> pd.DataFrame:
    rename = {}
    for target, aliases in mapping.items():
        source = _first_present(df, aliases)
        if source and source != target:
            rename[source] = target
    return df.rename(columns=rename).copy()


def _find_source_file(base_dir: Path, candidates: list[str]) -> Path | None:
    if not base_dir.exists():
        return None
    normalized_candidates = {_norm(name) for name in candidates}
    for path in sorted(base_dir.rglob("*")):
        if not path.is_file():
            continue
        if _norm(path.name) in normalized_candidates or _norm(path.stem) in normalized_candidates:
            return path
    return None


def _load_csv_or_excel(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    for encoding in ("utf-8-sig", "utf-8", "latin1"):
        try:
            return pd.read_csv(path, encoding=encoding, low_memory=False)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(path, low_memory=False)


def _read_excel_tables(excel_path: Path) -> dict[str, pd.DataFrame]:
    workbook = pd.ExcelFile(excel_path)
    tables: dict[str, pd.DataFrame] = {}
    for table_name in SOURCE_ALIASES:
        expected = {_norm(alias) for alias in [table_name, *SOURCE_ALIASES[table_name]]}
        for sheet_name in workbook.sheet_names:
            if _norm(sheet_name) in expected:
                tables[table_name] = pd.read_excel(excel_path, sheet_name=sheet_name)
                break
    return tables


def _read_source_tables(source_dir: Path | None = None, excel_path: Path | None = None) -> dict[str, pd.DataFrame]:
    base_dir = source_dir if source_dir and source_dir.is_dir() else RAW_DIR
    tables: dict[str, pd.DataFrame] = {}

    if excel_path and excel_path.is_file():
        tables.update(_read_excel_tables(excel_path))
        if tables:
            return tables

    for table_name, candidates in SOURCE_ALIASES.items():
        source = _find_source_file(base_dir, candidates)
        if source is not None:
            tables[table_name] = _load_csv_or_excel(source)
    return tables


def _apply_schema_types(df: pd.DataFrame, bool_cols: list[str] | None = None, int_cols: list[str] | None = None, float_cols: list[str] | None = None, date_cols: list[str] | None = None) -> pd.DataFrame:
    df = df.copy()
    bool_cols = bool_cols or []
    int_cols = int_cols or []
    float_cols = float_cols or []
    date_cols = date_cols or []

    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].map(_to_bool)

    for col in int_cols:
        if col in df.columns:
            df[col] = df[col].map(_to_int)

    for col in float_cols:
        if col in df.columns:
            df[col] = df[col].map(_to_float)

    for col in date_cols:
        if col in df.columns:
            df[col] = df[col].map(_to_date)

    return df


def transform_asegurados(df: pd.DataFrame) -> pd.DataFrame:
    df = _rename_known_columns(df, HEADER_MAPS["asegurados"])
    df = _apply_schema_types(
        df,
        int_cols=["antiguedad", "numero_polizas", "reclamos_ultimos_12_meses", "reclamos_historico_total", "reclamos_rc_sin_tercero"],
    )
    if "perfil_riesgo" not in df.columns:
        df["perfil_riesgo"] = None
    return df


def transform_proveedores(df: pd.DataFrame) -> pd.DataFrame:
    df = _rename_known_columns(df, HEADER_MAPS["proveedores"])
    df = _apply_schema_types(
        df,
        bool_cols=["restrictivo"],
        int_cols=["reclamos_asociados"],
        float_cols=["monto_promedio_reclamado"],
    )
    if "motivo_restriccion" not in df.columns:
        df["motivo_restriccion"] = None
    return df


def transform_polizas(df: pd.DataFrame) -> pd.DataFrame:
    df = _rename_known_columns(df, HEADER_MAPS["polizas"])
    df = _apply_schema_types(
        df,
        float_cols=["suma_asegurada", "prima"],
        date_cols=["fecha_inicio", "fecha_fin"],
    )
    if "estado_poliza" not in df.columns:
        df["estado_poliza"] = None
    return df


def transform_documentos(df: pd.DataFrame) -> pd.DataFrame:
    df = _rename_known_columns(df, HEADER_MAPS["documentos"])
    if "nombre_pdf" not in df.columns:
        df["nombre_pdf"] = None
    return df


def transform_indice_documentos(df: pd.DataFrame) -> pd.DataFrame:
    df = _rename_known_columns(df, HEADER_MAPS["indice_documentos"])
    if "nombre_pdf" not in df.columns:
        df["nombre_pdf"] = None
    return df


def _parse_pdf_text(pdf_path: Path) -> str:
    for module_name, reader_name in (("pypdf", "PdfReader"), ("PyPDF2", "PdfReader")):
        if importlib.util.find_spec(module_name) is None:
            continue
        module = __import__(module_name, fromlist=[reader_name])
        reader = getattr(module, reader_name)
        try:
            with pdf_path.open("rb") as handle:
                pdf = reader(handle)
                pages = []
                for page in getattr(pdf, "pages", []):
                    try:
                        pages.append(page.extract_text() or "")
                    except Exception:
                        continue
                return "\n".join(pages)
        except Exception:
            return ""
    return ""


def _extract_pdf_fields(text: str, source_name: str) -> dict[str, object]:
    normalized = text.replace("\r", "\n")
    combined = f"{source_name}\n{normalized}"

    def find(pattern: str, flags: int = re.IGNORECASE) -> str | None:
        match = re.search(pattern, combined, flags)
        if match:
            value = match.group(1).strip()
            return value or None
        return None

    plate = find(r"(?:placa|plate)\s*[:\-]?\s*([A-Z0-9\-]{5,12})")
    marca = find(r"marca\s*[:\-]?\s*([A-ZÁÉÍÓÚÑa-záéíóúñ0-9 ._-]{2,40})")
    modelo = find(r"modelo\s*[:\-]?\s*([A-ZÁÉÍÓÚÑa-záéíóúñ0-9 ._-]{2,40})")
    anio = find(r"(?:anio|año|year)\s*[:\-]?\s*(\d{4})")
    motor = find(r"motor\s*[:\-]?\s*([A-Z0-9\-]{4,30})")
    chasis = find(r"chasis\s*[:\-]?\s*([A-Z0-9\-]{6,40})")
    numero_parte = find(r"(?:n(?:u|ú)mero\s+)?parte\s*(?:policial)?\s*[:\-]?\s*([A-Z0-9\-/.]{4,40})")

    return {
        "placa": plate.upper() if plate else None,
        "marca": marca.title() if marca else None,
        "modelo": modelo.title() if modelo else None,
        "anio": _to_int(anio) if anio else None,
        "motor": motor.upper() if motor else None,
        "chasis": chasis.upper() if chasis else None,
        "numero_parte_policial": numero_parte,
    }


def _pdf_directories(source_dir: Path | None = None) -> list[Path]:
    base = source_dir if source_dir and source_dir.is_dir() else RAW_DIR
    if not base.is_dir():
        return []
    dirs: list[Path] = []
    for path in base.iterdir():
        if not path.is_dir():
            continue
        normalized = _norm(path.name)
        if any(token in normalized for token in ("factura", "parte policial", "parte_policial", "declaracion de accidente", "declaracion", "accidente")):
            dirs.append(path)
    return dirs


def _scan_pdf_metadata(source_dir: Path | None = None) -> tuple[dict[str, dict[str, object]], dict[str, dict[str, object]]]:
    by_plate: dict[str, dict[str, object]] = {}
    by_siniestro: dict[str, dict[str, object]] = {}

    for pdf_dir in _pdf_directories(source_dir):
        for pdf_path in pdf_dir.rglob("*.pdf"):
            text = _parse_pdf_text(pdf_path)
            fields = _extract_pdf_fields(text, pdf_path.stem)

            name_norm = _norm(pdf_path.stem)
            sin_match = re.search(r"(SIN[-_ ]?\d{3,6})", pdf_path.stem.upper())
            if sin_match:
                by_siniestro[sin_match.group(1).replace("_", "-").replace(" ", "-")] = fields

            plate = fields.get("placa")
            if plate:
                current = by_plate.setdefault(str(plate).upper(), {})
                for key, value in fields.items():
                    if value not in (None, "", 0) and current.get(key) in (None, "", 0):
                        current[key] = value

            if not plate and re.fullmatch(r"[A-Z0-9\-]{5,12}", pdf_path.stem.upper()):
                by_plate.setdefault(pdf_path.stem.upper(), {}).update(fields)

            if name_norm.startswith("sin-") or name_norm.startswith("siniestro-"):
                by_siniestro.setdefault(pdf_path.stem.upper(), {}).update(fields)

    return by_plate, by_siniestro


def _fill_missing_vehicle_fields(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "placa_vehiculo" in df.columns:
        df["placa_vehiculo"] = df["placa_vehiculo"].replace({"N/A": None, "NA": None, "na": None, "": None})
    else:
        df["placa_vehiculo"] = None

    if "numero_parte_policial" not in df.columns:
        df["numero_parte_policial"] = None

    return df


def _compute_historial_siniestros(df: pd.DataFrame) -> pd.Series:
    if "id_asegurado" not in df.columns:
        return pd.Series([0] * len(df), index=df.index)
    ordered = df.copy()
    ordered["_fecha_tmp"] = pd.to_datetime(ordered.get("fecha_ocurrencia"), errors="coerce")
    ordered = ordered.sort_values(["id_asegurado", "_fecha_tmp", "id_siniestro"], na_position="last")
    counts = ordered.groupby("id_asegurado").cumcount()
    return counts.reindex(df.index).fillna(0).astype(int)


def _merge_provider_reference(siniestros: pd.DataFrame, proveedores: pd.DataFrame | None) -> pd.DataFrame:
    if proveedores is None or proveedores.empty or "id_proveedor" not in siniestros.columns:
        if "beneficiario" not in siniestros.columns:
            siniestros["beneficiario"] = siniestros.get("id_proveedor")
        return siniestros

    providers = proveedores.copy()
    if "restrictivo" in providers.columns:
        providers["restrictivo"] = providers["restrictivo"].map(_to_bool)
    provider_name = providers.set_index("id_proveedor")["nombre"].to_dict() if "nombre" in providers.columns else {}
    provider_flag = providers.set_index("id_proveedor")["restrictivo"].to_dict() if "restrictivo" in providers.columns else {}

    if "beneficiario" not in siniestros.columns:
        siniestros["beneficiario"] = siniestros["id_proveedor"].map(provider_name)
    else:
        siniestros["beneficiario"] = siniestros["beneficiario"].fillna(siniestros["id_proveedor"].map(provider_name))

    if "proveedor_restrictivo" not in siniestros.columns:
        siniestros["proveedor_restrictivo"] = False
    siniestros["proveedor_restrictivo"] = siniestros["proveedor_restrictivo"].map(_to_bool)
    siniestros["proveedor_restrictivo"] = siniestros["proveedor_restrictivo"].fillna(siniestros["id_proveedor"].map(provider_flag)).fillna(False)
    return siniestros


def transform_siniestros(
    df: pd.DataFrame,
    polizas: pd.DataFrame | None = None,
    asegurados: pd.DataFrame | None = None,
    proveedores: pd.DataFrame | None = None,
    documentos: pd.DataFrame | None = None,
    indice_documentos: pd.DataFrame | None = None,
) -> pd.DataFrame:
    df = _rename_known_columns(df, HEADER_MAPS["siniestros"])
    df = _fill_missing_vehicle_fields(df)

    if polizas is not None and not polizas.empty:
        join_cols = [col for col in ["id_poliza", "id_asegurado", "ramo", "suma_asegurada", "fecha_inicio", "fecha_fin"] if col in polizas.columns]
        if join_cols and "id_poliza" in df.columns:
            policy_cols = polizas[[col for col in ["id_poliza", *[c for c in join_cols if c != "id_poliza"]] if col in polizas.columns]].copy()
            policy_cols = policy_cols.drop_duplicates(subset=["id_poliza"])
            df = df.merge(policy_cols, on="id_poliza", how="left", suffixes=("", "_poliza"))

    if asegurados is not None and not asegurados.empty and "id_asegurado" in df.columns:
        insurance_cols = [col for col in ["id_asegurado", "ciudad", "perfil_riesgo"] if col in asegurados.columns]
        if insurance_cols:
            insured = asegurados[insurance_cols].drop_duplicates(subset=["id_asegurado"])
            df = df.merge(insured, on="id_asegurado", how="left", suffixes=("", "_asegurado"))

    df = _merge_provider_reference(df, proveedores)

    if documentos is not None and not documentos.empty and "id_siniestro" in df.columns:
        docs_subset = documentos[[col for col in ["id_siniestro", "tipo_documento", "nombre_pdf"] if col in documentos.columns]].copy()
        if not docs_subset.empty:
            parte_docs = docs_subset[docs_subset["tipo_documento"].astype(str).str.contains("parte pol|denuncia pol", case=False, na=False)] if "tipo_documento" in docs_subset.columns else pd.DataFrame()
            if not parte_docs.empty:
                parte_doc = parte_docs.groupby("id_siniestro")["nombre_pdf"].first().to_dict() if "nombre_pdf" in parte_docs.columns else {}
                if "numero_parte_policial" not in df.columns:
                    df["numero_parte_policial"] = None
                df["numero_parte_policial"] = df["numero_parte_policial"].fillna(df["id_siniestro"].map(parte_doc))

    if indice_documentos is not None and not indice_documentos.empty and "id_siniestro" in df.columns:
        idx_subset = indice_documentos[[col for col in ["id_siniestro", "tipo_documento", "nombre_pdf"] if col in indice_documentos.columns]].copy()
        if not idx_subset.empty:
            parte_docs = idx_subset[idx_subset["tipo_documento"].astype(str).str.contains("parte pol|denuncia pol", case=False, na=False)] if "tipo_documento" in idx_subset.columns else pd.DataFrame()
            if not parte_docs.empty:
                parte_doc = parte_docs.groupby("id_siniestro")["nombre_pdf"].first().to_dict() if "nombre_pdf" in parte_docs.columns else {}
                df["numero_parte_policial"] = df["numero_parte_policial"].fillna(df["id_siniestro"].map(parte_doc))

    if "dias_entre_ocurrencia_reporte" not in df.columns:
        if {"fecha_ocurrencia", "fecha_reporte"}.issubset(df.columns):
            delta = pd.to_datetime(df["fecha_reporte"], errors="coerce") - pd.to_datetime(df["fecha_ocurrencia"], errors="coerce")
            df["dias_entre_ocurrencia_reporte"] = delta.dt.days.fillna(0).astype(int)
        else:
            df["dias_entre_ocurrencia_reporte"] = 0

    if "dias_desde_inicio_poliza" not in df.columns or df["dias_desde_inicio_poliza"].isna().all():
        if {"fecha_ocurrencia", "fecha_inicio"}.issubset(df.columns):
            delta = pd.to_datetime(df["fecha_ocurrencia"], errors="coerce") - pd.to_datetime(df["fecha_inicio"], errors="coerce")
            df["dias_desde_inicio_poliza"] = delta.dt.days.fillna(0).astype(int)
        else:
            df["dias_desde_inicio_poliza"] = 0

    if "dias_desde_fin_poliza" not in df.columns or df["dias_desde_fin_poliza"].isna().all():
        if {"fecha_ocurrencia", "fecha_fin"}.issubset(df.columns):
            delta = pd.to_datetime(df["fecha_fin"], errors="coerce") - pd.to_datetime(df["fecha_ocurrencia"], errors="coerce")
            df["dias_desde_fin_poliza"] = delta.dt.days.fillna(0).astype(int)
        else:
            df["dias_desde_fin_poliza"] = 0

    if "historial_siniestros_asegurado" not in df.columns or df["historial_siniestros_asegurado"].isna().all():
        df["historial_siniestros_asegurado"] = _compute_historial_siniestros(df)
    else:
        df["historial_siniestros_asegurado"] = df["historial_siniestros_asegurado"].map(_to_int)

    if "similitud_narrativa" not in df.columns:
        df["similitud_narrativa"] = 0.0

    if "documentos_completos" not in df.columns:
        df["documentos_completos"] = True

    if "suma_asegurada" not in df.columns and "suma_asegurada_poliza" in df.columns:
        df["suma_asegurada"] = df["suma_asegurada_poliza"]

    if "ramo" not in df.columns and "ramo_poliza" in df.columns:
        df["ramo"] = df["ramo_poliza"]

    if "id_asegurado" not in df.columns and "id_asegurado_poliza" in df.columns:
        df["id_asegurado"] = df["id_asegurado_poliza"]

    if "ciudad" not in df.columns:
        df["ciudad"] = None

    if "fecha_ocurrencia" in df.columns:
        df["fecha_ocurrencia"] = df["fecha_ocurrencia"].map(_to_date)
    if "fecha_reporte" in df.columns:
        df["fecha_reporte"] = df["fecha_reporte"].map(_to_date)

    df = _apply_schema_types(
        df,
        bool_cols=["documentos_completos", "proveedor_restrictivo"],
        int_cols=["dias_entre_ocurrencia_reporte", "dias_desde_inicio_poliza", "dias_desde_fin_poliza", "historial_siniestros_asegurado"],
        float_cols=["monto_reclamado", "monto_estimado", "monto_pagado", "suma_asegurada", "similitud_narrativa"],
    )

    if "proveedor_restrictivo" in df.columns:
        df["proveedor_restrictivo"] = df["proveedor_restrictivo"].fillna(False).astype(bool)

    if "beneficiario" not in df.columns and "id_proveedor" in df.columns:
        df["beneficiario"] = None

    if "id_siniestro" in df.columns:
        df = df.drop_duplicates(subset=["id_siniestro"], keep="first")

    return df


def _infer_vehicle_row(row: pd.Series, pdf_by_plate: dict[str, dict[str, object]], pdf_by_siniestro: dict[str, dict[str, object]]) -> dict[str, object]:
    id_siniestro = str(row.get("id_siniestro", "")).strip()
    plate = row.get("placa_vehiculo")
    if pd.isna(plate) or not str(plate).strip():
        plate = None
    plate = str(plate).strip().upper() if plate else None

    metadata = {
        "id_vehiculo": f"VEH-{id_siniestro.replace('SIN-', '').replace('_', '-')}",
        "id_siniestro": id_siniestro,
        "placa": plate,
        "chasis": None,
        "motor": None,
        "marca": None,
        "modelo": None,
        "anio": None,
    }

    if id_siniestro in pdf_by_siniestro:
        for key, value in pdf_by_siniestro[id_siniestro].items():
            if key in metadata and value not in (None, "", 0):
                metadata[key] = value

    if plate and plate in pdf_by_plate:
        for key, value in pdf_by_plate[plate].items():
            if key in metadata and value not in (None, "", 0):
                metadata[key] = value

    if metadata["placa"] is None and plate:
        metadata["placa"] = plate

    return metadata


def build_vehiculos(siniestros: pd.DataFrame, source_dir: Path | None = None) -> pd.DataFrame:
    pdf_by_plate, pdf_by_siniestro = _scan_pdf_metadata(source_dir)
    rows = [_infer_vehicle_row(row, pdf_by_plate, pdf_by_siniestro) for _, row in siniestros.iterrows()]
    vehiculos = pd.DataFrame(rows)
    if vehiculos.empty:
        return vehiculos
    vehiculos["anio"] = vehiculos["anio"].map(lambda value: _to_int(value, default=None) if value not in (None, "") else None)
    vehiculos = vehiculos.drop_duplicates(subset=["id_siniestro"], keep="first")
    return vehiculos


def _clean_records(df: pd.DataFrame) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    normalized = df.where(pd.notnull(df), None)
    for record in normalized.to_dict(orient="records"):
        cleaned: dict[str, object] = {}
        for key, value in record.items():
            if isinstance(value, pd.Timestamp):
                cleaned[key] = value.strftime("%Y-%m-%d")
            elif hasattr(value, "item"):
                try:
                    cleaned[key] = value.item()
                except Exception:
                    cleaned[key] = str(value)
            elif isinstance(value, float) and pd.isna(value):
                cleaned[key] = None
            else:
                cleaned[key] = value
        records.append(cleaned)
    return records


def _filter_for_supabase(table_name: str, df: pd.DataFrame) -> pd.DataFrame:
    filtered = df.copy()
    return filtered[[column for column in filtered.columns]]


def _limit_related_rows(tables: dict[str, pd.DataFrame], limit: int, source_dir: Path | None = None) -> dict[str, pd.DataFrame]:
    siniestros = tables.get("siniestros")
    if siniestros is None or siniestros.empty:
        return tables

    siniestros = siniestros.copy()
    if "fecha_ocurrencia" in siniestros.columns:
        siniestros["_sort_fecha"] = pd.to_datetime(siniestros["fecha_ocurrencia"], errors="coerce")
        siniestros = siniestros.sort_values(["_sort_fecha", "id_siniestro"], na_position="last")
        siniestros = siniestros.drop(columns=["_sort_fecha"])
    elif "id_siniestro" in siniestros.columns:
        siniestros = siniestros.sort_values(["id_siniestro"])

    siniestros = siniestros.drop_duplicates(subset=["id_siniestro"], keep="first").head(limit)
    tables["siniestros"] = siniestros.reset_index(drop=True)

    id_siniestros = set(siniestros.get("id_siniestro", pd.Series(dtype=str)).astype(str))
    id_polizas = set(siniestros.get("id_poliza", pd.Series(dtype=str)).dropna().astype(str))
    id_asegurados = set(siniestros.get("id_asegurado", pd.Series(dtype=str)).dropna().astype(str))
    id_proveedores = set(siniestros.get("id_proveedor", pd.Series(dtype=str)).dropna().astype(str))

    if "polizas" in tables and not tables["polizas"].empty:
        polizas = tables["polizas"].copy()
        if "id_poliza" in polizas.columns:
            polizas = polizas[polizas["id_poliza"].astype(str).isin(id_polizas | set(siniestros.get("id_poliza", pd.Series(dtype=str)).dropna().astype(str)))]
        tables["polizas"] = polizas.reset_index(drop=True)

    if "asegurados" in tables and not tables["asegurados"].empty:
        asegurados = tables["asegurados"].copy()
        if "id_asegurado" in asegurados.columns:
            asegurados = asegurados[asegurados["id_asegurado"].astype(str).isin(id_asegurados | set(tables.get("polizas", pd.DataFrame()).get("id_asegurado", pd.Series(dtype=str)).dropna().astype(str)))]
        tables["asegurados"] = asegurados.reset_index(drop=True)

    if "proveedores" in tables and not tables["proveedores"].empty:
        proveedores = tables["proveedores"].copy()
        if "id_proveedor" in proveedores.columns:
            proveedores = proveedores[proveedores["id_proveedor"].astype(str).isin(id_proveedores)]
        tables["proveedores"] = proveedores.reset_index(drop=True)

    for key in ("documentos", "indice_documentos"):
        if key in tables and not tables[key].empty:
            docs = tables[key].copy()
            if "id_siniestro" in docs.columns:
                docs = docs[docs["id_siniestro"].astype(str).isin(id_siniestros)]
            tables[key] = docs.reset_index(drop=True)

    tables["vehiculos"] = build_vehiculos(tables["siniestros"], source_dir=source_dir)
    return tables


def _ensure_output_tables(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    for table_name in TABLE_ORDER:
        tables.setdefault(table_name, pd.DataFrame(columns=SUPABASE_COLUMNS.get(table_name, [])))
    return tables


def _save_tables(tables: dict[str, pd.DataFrame]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table_name in TABLE_ORDER:
        if table_name not in tables:
            continue
        output_path = OUT_DIR / f"{table_name}.csv"
        tables[table_name].to_csv(output_path, index=False)
        print(f"Guardado: {output_path} ({len(tables[table_name])} filas)")


def _clear_supabase_table(supabase, table_name: str, pk: str) -> None:
    try:
        supabase.table(table_name).delete().neq(pk, "").execute()
    except Exception as exc:
        print(f"  Aviso limpiando {table_name}: {exc}")


def _upload_table(supabase, table_name: str, df: pd.DataFrame, pk: str) -> None:
    if df is None or df.empty:
        print(f"  {table_name}: sin datos, omitido")
        return
    df = _filter_for_supabase(table_name, df)
    records = _clean_records(df)
    batch_size = 100
    try:
        for start in range(0, len(records), batch_size):
            try:
                supabase.table(table_name).insert(records[start : start + batch_size]).execute()
                print(f"  {table_name}: {min(start + batch_size, len(records))}/{len(records)}")
            except Exception as batch_error:
                if "Could not find the" in str(batch_error) and "column" in str(batch_error):
                    print(f"  {table_name}: Columnas incompatibles, intentando sin algunas...")
                    for record in records[start : start + batch_size]:
                        try:
                            supabase.table(table_name).insert(record).execute()
                        except Exception:
                            pass
                else:
                    raise
    except Exception as exc:
        if "Could not find the table" in str(exc):
            print(f"  {table_name}: Tabla no existe en Supabase (create en panel SQL)")
        else:
            print(f"  {table_name}: {str(exc)[:80]}")


def _prepare_tables(source_dir: Path | None = None, excel_path: Path | None = None, limit: int = DEFAULT_LIMIT) -> dict[str, pd.DataFrame]:
    raw_tables = _read_source_tables(source_dir=source_dir, excel_path=excel_path)
    if "siniestros" not in raw_tables:
        raise FileNotFoundError("No se encontro el archivo de siniestros en data/raw o en --source/--excel.")

    asegurados = transform_asegurados(raw_tables["asegurados"]) if "asegurados" in raw_tables else None
    proveedores = transform_proveedores(raw_tables["proveedores"]) if "proveedores" in raw_tables else None
    polizas = transform_polizas(raw_tables["polizas"]) if "polizas" in raw_tables else None
    documentos = transform_documentos(raw_tables["documentos"]) if "documentos" in raw_tables else None
    indice_documentos = transform_indice_documentos(raw_tables["indice_documentos"]) if "indice_documentos" in raw_tables else None

    siniestros = transform_siniestros(
        raw_tables["siniestros"],
        polizas=polizas,
        asegurados=asegurados,
        proveedores=proveedores,
        documentos=documentos,
        indice_documentos=indice_documentos,
    )

    tables: dict[str, pd.DataFrame] = {"siniestros": siniestros}
    if polizas is not None:
        tables["polizas"] = polizas
    if asegurados is not None:
        tables["asegurados"] = asegurados
    if proveedores is not None:
        tables["proveedores"] = proveedores
    if documentos is not None:
        tables["documentos"] = documentos
    if indice_documentos is not None:
        tables["indice_documentos"] = indice_documentos

    tables = _limit_related_rows(tables, limit=limit, source_dir=source_dir)
    tables = _ensure_output_tables(tables)
    return tables


def migrate(
    excel_path: Path | None = None,
    source_dir: Path | None = None,
    upload: bool = False,
    limit: int = DEFAULT_LIMIT,
) -> dict[str, pd.DataFrame]:
    load_dotenv(ROOT / ".env")

    if source_dir is not None:
        print(f"Fuente: {source_dir}")
    if excel_path is not None:
        print(f"Excel: {excel_path}")

    tables = _prepare_tables(source_dir=source_dir, excel_path=excel_path, limit=limit)
    _save_tables(tables)
    print(f"\nMigracion completada -> {OUT_DIR}")

    if upload:
        from supabase import create_client

        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise RuntimeError("Faltan SUPABASE_URL y SUPABASE_KEY en .env")

        client = create_client(url, key)
        print("\nLimpiando Supabase...")
        for table_name, pk in [
            ("documentos", "id_documento"),
            ("indice_documentos", "id_documento"),
            ("vehiculos", "id_vehiculo"),
            ("siniestros", "id_siniestro"),
            ("proveedores", "id_proveedor"),
            ("polizas", "id_poliza"),
            ("asegurados", "id_asegurado"),
        ]:
            _clear_supabase_table(client, table_name, pk)

        print("\nSubiendo a Supabase...")
        for table_name, pk in [
            ("asegurados", "id_asegurado"),
            ("proveedores", "id_proveedor"),
            ("polizas", "id_poliza"),
            ("siniestros", "id_siniestro"),
            ("documentos", "id_documento"),
            ("indice_documentos", "id_documento"),
            ("vehiculos", "id_vehiculo"),
        ]:
            _upload_table(client, table_name, tables.get(table_name, pd.DataFrame()), pk)

        print("\nSupabase actualizado con dataset real.")

    return tables


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrar el dataset real a CSVs y Supabase")
    parser.add_argument("--source", type=str, help="Carpeta con los CSV/PDF del evento")
    parser.add_argument("--excel", type=str, help="Ruta al Excel del dataset real")
    parser.add_argument("--upload", action="store_true", help="Subir los datos a Supabase")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Maximo de siniestros a migrar")
    args = parser.parse_args()

    source_dir = Path(args.source) if args.source else None
    excel_path = Path(args.excel) if args.excel else None
    migrate(excel_path=excel_path, source_dir=source_dir, upload=args.upload, limit=args.limit)


if __name__ == "__main__":
    main()

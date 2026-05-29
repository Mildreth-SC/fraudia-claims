"""Analisis de CSV subido: mapeo, reglas, graficos y consultas tipo SQL."""

import math
import os
import re
import pandas as pd
import numpy as np

from app.data_pipeline import (
    enriquecer_dataframe,
    aplicar_reglas_y_ml,
    cargar_auxiliares_local,
    resolver_vehiculos_para_df,
)
from explainability.explain_score import generar_reporte_ejecutivo

_uploaded_df: pd.DataFrame | None = None
_last_output_dir: str | None = None


def get_uploaded_df() -> pd.DataFrame | None:
    return _uploaded_df


def _json_safe(obj):
    """Convierte NaN/Inf y tipos numpy a valores compatibles con JSON."""
    if obj is None:
        return None
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return _json_safe(obj.tolist())
    if isinstance(obj, np.generic):
        return _json_safe(obj.item())
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, (int, bool, str)):
        return obj
    try:
        if pd.isna(obj):
            return None
    except (TypeError, ValueError):
        pass
    return str(obj)


def json_response_payload(data: dict) -> dict:
    """Limpia NaN/Inf y valida serializacion JSON estricta."""
    import json

    cleaned = _json_safe(data)
    # Round-trip: garantiza tipos nativos sin NaN
    return json.loads(json.dumps(cleaned, allow_nan=False))


def json_response_bytes(data: dict) -> bytes:
    """Body listo para FastAPI Response (evita re-serializacion con NaN)."""
    import json

    payload = json_response_payload(data)
    return json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")


def _detect_col(columns: list[str], patterns: list[str]) -> str | None:
    for pat in patterns:
        for col in columns:
            if re.search(pat, col.lower()):
                return col
    return None


def mapear_csv(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    cols = list(df.columns)
    mapping = {
        "id_siniestro": _detect_col(cols, [r"id.*sin", r"claim", r"codigo", r"^id$", r"case"]),
        "monto_reclamado": _detect_col(cols, [r"monto", r"amount", r"valor", r"reclamado"]),
        "dias_desde_inicio_poliza": _detect_col(cols, [r"dias.*poliza", r"policy", r"vigencia"]),
        "dias_entre_ocurrencia_reporte": _detect_col(cols, [r"dias.*report", r"demora", r"delay"]),
        "historial_siniestros_asegurado": _detect_col(cols, [r"historial", r"history", r"prev"]),
        "documentos_completos": _detect_col(cols, [r"document", r"completo"]),
        "id_proveedor": _detect_col(cols, [r"proveedor", r"provider", r"vendor"]),
        "suma_asegurada": _detect_col(cols, [r"suma.*aseg", r"coverage", r"insured"]),
        "cobertura": _detect_col(cols, [r"cobertura", r"coverage"]),
        "ciudad": _detect_col(cols, [r"ciudad", r"city"]),
        "ramo": _detect_col(cols, [r"ramo", r"branch", r"linea"]),
        "beneficiario": _detect_col(cols, [r"beneficiario", r"proveedor", r"taller"]),
        "descripcion": _detect_col(cols, [r"descripcion", r"narrativa", r"texto"]),
        "placa": _detect_col(cols, [r"placa", r"plate", r"matricula", r"patente"]),
        "id_asegurado": _detect_col(cols, [r"asegurado", r"insured", r"policyholder"]),
    }

    out = pd.DataFrame()
    report_lines = [f"Filas leidas: {len(df)}", f"Columnas detectadas: {len(cols)}", ""]

    for target, source in mapping.items():
        if source and source in df.columns:
            out[target] = df[source]
            report_lines.append(f"  {target} <- {source}")
        else:
            report_lines.append(f"  {target} <- (valor por defecto)")

    n = len(df)
    if "id_siniestro" not in out.columns or out["id_siniestro"].isna().all():
        out["id_siniestro"] = [f"UP-{i+1:05d}" for i in range(n)]

    defaults = {
        "monto_reclamado": 5000.0,
        "dias_desde_inicio_poliza": 60,
        "dias_entre_ocurrencia_reporte": 2,
        "historial_siniestros_asegurado": 0,
        "documentos_completos": True,
        "id_proveedor": "P000",
        "suma_asegurada": 20000.0,
        "cobertura": "Choque",
        "ciudad": "Quito",
        "ramo": "Generales",
        "beneficiario": "Proveedor generico",
        "descripcion": "Sin descripcion",
    }
    for col, val in defaults.items():
        if col not in out.columns:
            out[col] = val
        out[col] = out[col].fillna(val)

    if out["documentos_completos"].dtype == object:
        out["documentos_completos"] = (
            out["documentos_completos"]
            .astype(str)
            .str.lower()
            .isin(["true", "1", "si", "sí", "yes"])
        )

    for col in ["monto_reclamado", "dias_desde_inicio_poliza", "dias_entre_ocurrencia_reporte",
                "historial_siniestros_asegurado", "suma_asegurada"]:
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(defaults[col])

    return out, "\n".join(report_lines)


def _generar_graficos(df: pd.DataFrame, output_dir: str) -> dict[str, str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    graf_dir = os.path.join(output_dir, "graficos")
    os.makedirs(graf_dir, exist_ok=True)
    paths = {}

    # 1. Distribucion riesgo
    counts = df["nivel_riesgo"].value_counts()
    colors = {"ROJO": "#E24B4A", "AMARILLO": "#EF9F27", "VERDE": "#4CAF50"}
    fig, ax = plt.subplots(figsize=(5, 4))
    labels = list(counts.index)
    ax.pie(
        counts.values,
        labels=labels,
        colors=[colors.get(l, "#999") for l in labels],
        autopct="%1.1f%%",
    )
    ax.set_title("Distribucion de riesgo")
    p1 = os.path.join(graf_dir, "distribucion_riesgo.png")
    fig.savefig(p1, dpi=100, bbox_inches="tight")
    plt.close(fig)
    paths["distribucion_riesgo"] = "/graficos/distribucion_riesgo.png"

    # 2. Score por ramo
    if "ramo" in df.columns:
        ramo_scores = df.groupby("ramo")["score"].mean().sort_values(ascending=False).head(8)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.barh(ramo_scores.index.astype(str), ramo_scores.values, color="#1B3A6B")
        ax.set_xlabel("Score promedio")
        ax.set_title("Score por ramo")
        p2 = os.path.join(graf_dir, "score_por_ramo.png")
        fig.savefig(p2, dpi=100, bbox_inches="tight")
        plt.close(fig)
        paths["score_por_ramo"] = "/graficos/score_por_ramo.png"

    # 3. Top proveedores
    if "beneficiario" in df.columns:
        top = (
            df[df["nivel_riesgo"].isin(["ROJO", "AMARILLO"])]
            .groupby("beneficiario")
            .size()
            .sort_values(ascending=False)
            .head(5)
        )
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.barh(top.index.astype(str), top.values, color="#E24B4A")
        ax.set_xlabel("Alertas")
        ax.set_title("Top proveedores")
        p3 = os.path.join(graf_dir, "top_proveedores.png")
        fig.savefig(p3, dpi=100, bbox_inches="tight")
        plt.close(fig)
        paths["top_proveedores"] = "/graficos/top_proveedores.png"

    # 4. Alertas por ciudad
    if "ciudad" in df.columns:
        city = (
            df[df["nivel_riesgo"].isin(["ROJO", "AMARILLO"])]
            .groupby("ciudad")
            .size()
            .sort_values(ascending=False)
            .head(8)
        )
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(city.index.astype(str), city.values, color="#EF9F27")
        ax.set_ylabel("Alertas")
        ax.set_title("Alertas por ciudad")
        plt.xticks(rotation=45, ha="right")
        p4 = os.path.join(graf_dir, "alertas_ciudad.png")
        fig.savefig(p4, dpi=100, bbox_inches="tight")
        plt.close(fig)
        paths["alertas_ciudad"] = "/graficos/alertas_ciudad.png"

    return paths


def _leer_archivo_subido(file_path: str) -> pd.DataFrame:
    path = file_path.lower()
    if path.endswith((".xlsx", ".xls")):
        xl = pd.ExcelFile(file_path)
        for name in xl.sheet_names:
            if "siniestro" in name.lower():
                return pd.read_excel(file_path, sheet_name=name)
        for name in xl.sheet_names:
            if name.upper() != "README":
                return pd.read_excel(file_path, sheet_name=name)
        return pd.read_excel(file_path, sheet_name=0)
    return pd.read_csv(file_path, encoding="utf-8", low_memory=False)


def analizar_archivo_csv(file_path: str, output_dir: str, root: str | None = None) -> dict:
    global _uploaded_df, _last_output_dir

    raw = _leer_archivo_subido(file_path)
    mapped, report_map = mapear_csv(raw)
    veh, docs = (None, None)
    if root:
        veh = resolver_vehiculos_para_df(root, mapped)
        _, docs_full = cargar_auxiliares_local(root)
        if docs_full is not None and not docs_full.empty:
            ids = set(mapped["id_siniestro"].astype(str))
            docs = docs_full[docs_full["id_siniestro"].isin(ids)]
            if docs.empty:
                docs = None
        if veh is not None and not veh.empty:
            report_map += f"\n\nVehiculos enlazados: {len(veh)} registro(s) (local o columna placa)."
    df = enriquecer_dataframe(mapped, veh=veh, docs=docs)
    df = aplicar_reglas_y_ml(df)
    df = df.replace([np.inf, -np.inf], np.nan)
    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].fillna(0)

    os.makedirs(output_dir, exist_ok=True)
    cleaned_path = os.path.join(output_dir, "cleaned_data.csv")
    df.to_csv(cleaned_path, index=False)

    alertas_path = os.path.join(output_dir, "alertas_detalle.txt")
    with open(alertas_path, "w", encoding="utf-8") as f:
        f.write(generar_reporte_ejecutivo(df))

    cleaning_path = os.path.join(output_dir, "cleaning_report.txt")
    with open(cleaning_path, "w", encoding="utf-8") as f:
        f.write(report_map)
        f.write("\n\nReglas RF aplicadas (Python).\n")
        f.write("Graficos generados con matplotlib desde el dataset subido.\n")

    graficos = _generar_graficos(df, output_dir)

    _uploaded_df = df
    _last_output_dir = output_dir

    casos_df = df.nlargest(50, "score")[
        ["id_siniestro", "nivel_riesgo", "score", "alertas"]
    ].copy()
    casos_df["alertas"] = casos_df["alertas"].astype(str)
    casos_df["score"] = pd.to_numeric(casos_df["score"], errors="coerce").fillna(0).astype(int)
    casos = casos_df.where(pd.notnull(casos_df), None).to_dict(orient="records")

    mean_score = df["score"].mean()
    score_prom = round(float(mean_score), 1) if pd.notna(mean_score) else 0.0

    payload = {
        "status": "success",
        "resumen": {
            "total_casos": int(len(df)),
            "rojos": int((df["nivel_riesgo"] == "ROJO").sum()),
            "amarillos": int((df["nivel_riesgo"] == "AMARILLO").sum()),
            "verdes": int((df["nivel_riesgo"] == "VERDE").sum()),
            "score_promedio": score_prom,
        },
        "reporte_limpieza": report_map,
        "reporte_alertas": generar_reporte_ejecutivo(df),
        "casos": casos,
        "graficos": graficos,
        "columnas_disponibles": [str(c) for c in df.columns],
    }
    return json_response_payload(payload)


def ejecutar_consulta_sql(sql: str, limit: int = 100) -> dict:
    global _uploaded_df

    if _uploaded_df is None:
        return {"error": "Primero analice un dataset CSV en la pestana Analizar Dataset."}

    sql_clean = sql.strip().rstrip(";")
    if not re.match(r"^select\s", sql_clean, re.IGNORECASE):
        return {"error": "Solo se permiten consultas SELECT."}

    forbidden = ["insert", "update", "delete", "drop", "alter", "create", "attach", "detach"]
    if any(re.search(rf"\b{kw}\b", sql_clean, re.IGNORECASE) for kw in forbidden):
        return {"error": "Consulta no permitida por seguridad."}

    try:
        import duckdb

        con = duckdb.connect(":memory:")
        con.register("siniestros", _uploaded_df)
        if "limit" not in sql_clean.lower():
            sql_exec = f"{sql_clean} LIMIT {limit}"
        else:
            sql_exec = sql_clean
        result = con.execute(sql_exec).fetchdf()
        con.close()
        filas = result.head(limit).where(pd.notnull(result), None).to_dict(orient="records")
        return json_response_payload({
            "columnas": list(result.columns),
            "filas": filas,
            "total_filas": len(result),
        })
    except Exception as e:
        return {"error": str(e)}

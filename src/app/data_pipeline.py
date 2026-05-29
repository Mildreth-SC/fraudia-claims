"""Pipeline compartido: enriquecimiento, reglas, ML."""

import os
import pandas as pd
import numpy as np

from rules.fraud_rules import calcular_score
from models.fraud_model import entrenar_modelo


def _enriquecer_placa_desde_siniestro(df: pd.DataFrame) -> pd.DataFrame:
    """Usa placa_vehiculo del dataset real si no hay join con tabla vehiculos."""
    if "placa_vehiculo" not in df.columns:
        return df
    if "placa" not in df.columns:
        df["placa"] = df["placa_vehiculo"]
    else:
        df["placa"] = df["placa"].fillna(df["placa_vehiculo"])
    mask = df["placa"].notna()
    if mask.any():
        freq = df.groupby("placa")["id_siniestro"].transform("nunique")
        df["frecuencia_placa"] = freq.where(mask, 0)
    return df


def _enriquecer_vehiculos(df: pd.DataFrame, veh: pd.DataFrame) -> pd.DataFrame:
    if veh is None or veh.empty:
        df["placa"] = None
        df["frecuencia_placa"] = 0
        df["frecuencia_conductor_veh"] = 0
        df["marca_vehiculo"] = None
        df["modelo_vehiculo"] = None
        df["anio_vehiculo"] = None
        return _enriquecer_placa_desde_siniestro(df)
    placa_map = veh.set_index("id_siniestro")["placa"].to_dict()
    freq = veh.groupby("placa")["id_siniestro"].nunique().to_dict()
    df["placa"] = df["id_siniestro"].map(placa_map)
    df["frecuencia_placa"] = df["placa"].map(lambda p: freq.get(p, 0) if pd.notna(p) else 0)
    for col_src, col_dst in [
        ("marca", "marca_vehiculo"),
        ("modelo", "modelo_vehiculo"),
        ("anio", "anio_vehiculo"),
    ]:
        if col_src in veh.columns:
            df[col_dst] = df["id_siniestro"].map(veh.set_index("id_siniestro")[col_src].to_dict())
        else:
            df[col_dst] = None
    if "id_conductor" in veh.columns:
        cond_map = veh.set_index("id_siniestro")["id_conductor"].to_dict()
        freq_cond = veh.groupby("id_conductor")["id_siniestro"].nunique().to_dict()
        df["id_conductor"] = df["id_siniestro"].map(cond_map)
        df["frecuencia_conductor_veh"] = df["id_conductor"].map(
            lambda c: freq_cond.get(c, 0) if pd.notna(c) else 0
        )
    else:
        df["frecuencia_conductor_veh"] = 0
    df = _enriquecer_placa_desde_siniestro(df)
    return df


def _enriquecer_conductor_asegurado(df: pd.DataFrame) -> pd.DataFrame:
    """Alta frecuencia conductor (PDF): proxy por asegurado en ramo Vehiculos."""
    df["frecuencia_conductor"] = 0
    if "id_asegurado" not in df.columns or "ramo" not in df.columns:
        return df
    mask = df["ramo"].astype(str).str.contains("Vehic", case=False, na=False)
    if not mask.any():
        return df
    freq = df[mask].groupby("id_asegurado")["id_siniestro"].transform("nunique")
    df.loc[mask, "frecuencia_conductor"] = freq
    if "frecuencia_conductor_veh" in df.columns:
        df.loc[mask, "frecuencia_conductor"] = df.loc[mask, [
            "frecuencia_conductor", "frecuencia_conductor_veh"
        ]].max(axis=1)
    return df


def _enriquecer_documentos(df: pd.DataFrame, docs: pd.DataFrame) -> pd.DataFrame:
    if docs is None or docs.empty:
        df["doc_inconsistente"] = False
        return df
    agg = docs.groupby("id_siniestro")["inconsistencia_detectada"].max().to_dict()
    df["doc_inconsistente"] = df["id_siniestro"].map(lambda x: bool(agg.get(x, False)))
    return df


def _enriquecer_proveedor(df: pd.DataFrame) -> pd.DataFrame:
    freq = df.groupby("beneficiario")["id_siniestro"].transform("count")
    df["frecuencia_beneficiario"] = freq
    return df


def _enriquecer_narrativas(df: pd.DataFrame) -> pd.DataFrame:
    if "similitud_narrativa" in df.columns:
        existing = pd.to_numeric(df["similitud_narrativa"], errors="coerce")
        if existing.notna().any() and (existing > 0).any():
            df["similitud_narrativa"] = existing.fillna(0.0)
            return df

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError:
        df["similitud_narrativa"] = 0.0
        return df

    texts = df["descripcion"].fillna("").astype(str)
    if len(texts) < 2:
        df["similitud_narrativa"] = 0.0
        return df

    vec = TfidfVectorizer(max_features=800, ngram_range=(1, 2))
    matrix = vec.fit_transform(texts)
    sim = cosine_similarity(matrix)
    np.fill_diagonal(sim, 0.0)
    df["similitud_narrativa"] = sim.max(axis=1)
    return df


def enriquecer_dataframe(
    df: pd.DataFrame,
    veh: pd.DataFrame | None = None,
    docs: pd.DataFrame | None = None,
) -> pd.DataFrame:
    df = df.copy()
    df = _enriquecer_vehiculos(df, veh)
    df = _enriquecer_conductor_asegurado(df)
    df = _enriquecer_documentos(df, docs)
    df = _enriquecer_proveedor(df)
    df = _enriquecer_narrativas(df)
    return df


def cargar_auxiliares_local(root: str) -> tuple[pd.DataFrame | None, pd.DataFrame | None]:
    veh_path = os.path.join(root, "data", "synthetic", "vehiculos.csv")
    docs_path = os.path.join(root, "data", "synthetic", "documentos.csv")
    veh = pd.read_csv(veh_path) if os.path.isfile(veh_path) else None
    docs = pd.read_csv(docs_path) if os.path.isfile(docs_path) else None
    return veh, docs


def vehiculo_por_siniestro(root: str, id_siniestro: str) -> dict | None:
    candidates = [
        os.path.join(root, "data", "processed", "real", "vehiculos.csv"),
        os.path.join(root, "data", "synthetic", "vehiculos.csv"),
    ]
    for veh_path in candidates:
        if not os.path.isfile(veh_path):
            continue
        veh = pd.read_csv(veh_path)
        row = veh[veh["id_siniestro"] == id_siniestro]
        if row.empty:
            continue
        rec = row.iloc[0].to_dict()
        for k, v in list(rec.items()):
            if hasattr(v, "item"):
                try:
                    rec[k] = v.item()
                except Exception:
                    rec[k] = str(v)
        return rec
    return None


def calcular_resumen_negocio(df: pd.DataFrame) -> dict:
    rojos = df[df["nivel_riesgo"] == "ROJO"]
    monto_rojos = float(rojos["monto_reclamado"].sum()) if "monto_reclamado" in df.columns else 0.0
    pendientes = int(df["nivel_riesgo"].isin(["ROJO", "AMARILLO"]).sum())
    revisados = int((df["nivel_riesgo"] == "VERDE").sum())
    return {
        "total_siniestros": int(len(df)),
        "rojos": int((df["nivel_riesgo"] == "ROJO").sum()),
        "amarillos": int((df["nivel_riesgo"] == "AMARILLO").sum()),
        "verdes": int((df["nivel_riesgo"] == "VERDE").sum()),
        "score_promedio": round(float(df["score"].mean()), 1),
        "anomalias_ml": int(df["es_anomalia"].sum()) if "es_anomalia" in df.columns else 0,
        "monto_total_rojos": round(monto_rojos, 2),
        "ahorro_potencial_30pct": round(monto_rojos * 0.30, 2),
        "casos_pendientes_revision": pendientes,
        "casos_bajo_riesgo": revisados,
    }


def resolver_vehiculos_para_df(root: str, df: pd.DataFrame) -> pd.DataFrame | None:
    """Une vehiculos locales o placa del CSV subido para activar RF-08."""
    veh_local, _ = cargar_auxiliares_local(root)
    ids = set(df["id_siniestro"].astype(str))
    partes = []
    if veh_local is not None and not veh_local.empty:
        match = veh_local[veh_local["id_siniestro"].isin(ids)]
        if not match.empty:
            partes.append(match)
    if "placa" in df.columns:
        placas = df[["id_siniestro", "placa"]].dropna(subset=["placa"])
        if not placas.empty:
            partes.append(placas)
    if not partes:
        return None
    veh = pd.concat(partes, ignore_index=True).drop_duplicates(subset=["id_siniestro"], keep="first")
    return veh if not veh.empty else None


def aplicar_reglas_y_ml(df: pd.DataFrame) -> pd.DataFrame:
    resultados = df.apply(calcular_score, axis=1)
    df = pd.concat([df, resultados], axis=1)
    df, _, _ = entrenar_modelo(df)
    return df


def _data_paths(root: str) -> tuple[str, str | None, str | None]:
    """Prioriza dataset real migrado sobre sintetico."""
    real = os.path.join(root, "data", "processed", "real")
    if os.path.isfile(os.path.join(real, "siniestros.csv")):
        return (
            os.path.join(real, "siniestros.csv"),
            os.path.join(real, "vehiculos.csv") if os.path.isfile(os.path.join(real, "vehiculos.csv")) else None,
            os.path.join(real, "documentos.csv") if os.path.isfile(os.path.join(real, "documentos.csv")) else None,
        )
    return (
        os.path.join(root, "data", "synthetic", "siniestros.csv"),
        os.path.join(root, "data", "synthetic", "vehiculos.csv"),
        os.path.join(root, "data", "synthetic", "documentos.csv"),
    )


def cargar_desde_csv_local(root: str, usar_scored_cache: bool = False) -> pd.DataFrame:
    scored = os.path.join(root, "data", "processed", "siniestros_scored.csv")
    synth, veh_path, docs_path = _data_paths(root)

    if usar_scored_cache and os.path.isfile(scored):
        return pd.read_csv(scored)

    if not os.path.isfile(synth):
        raise FileNotFoundError(
            "Falta dataset. Ejecute load_data.py o migrar_dataset_real.py"
        )

    df = pd.read_csv(synth)
    veh = pd.read_csv(veh_path) if veh_path and os.path.isfile(veh_path) else None
    docs = pd.read_csv(docs_path) if docs_path and os.path.isfile(docs_path) else None

    df = enriquecer_dataframe(df, veh, docs)
    return aplicar_reglas_y_ml(df)


def cargar_desde_csv_real(root: str = None) -> pd.DataFrame:
    """Carga datos reales desde CSVs locales (data/processed/real/)"""
    if root is None:
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    csv_dir = os.path.join(root, "data", "processed", "real")
    if not os.path.exists(csv_dir):
        return pd.DataFrame()

    try:
        df = pd.read_csv(os.path.join(csv_dir, "siniestros.csv"))

        veh = pd.DataFrame()
        veh_path = os.path.join(csv_dir, "vehiculos.csv")
        if os.path.exists(veh_path):
            veh = pd.read_csv(veh_path)

        docs = pd.DataFrame()
        docs_path = os.path.join(csv_dir, "documentos.csv")
        if os.path.exists(docs_path):
            docs = pd.read_csv(docs_path)

        df = enriquecer_dataframe(df, veh, docs)
        return aplicar_reglas_y_ml(df)
    except Exception as e:
        print(f"Error cargando CSVs reales: {e}")
        return pd.DataFrame()


def cargar_desde_supabase(supabase) -> pd.DataFrame:
    response = supabase.table("siniestros").select("*").execute()
    df = pd.DataFrame(response.data)

    # Si Supabase está vacío, intentar cargar desde CSVs locales
    if df.empty:
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return cargar_desde_csv_real(root)

    veh = pd.DataFrame()
    try:
        veh_resp = supabase.table("vehiculos").select("id_siniestro,placa").execute()
        veh = pd.DataFrame(veh_resp.data)
    except Exception:
        pass

    docs = pd.DataFrame()
    try:
        doc_resp = supabase.table("documentos").select(
            "id_siniestro,inconsistencia_detectada"
        ).execute()
        docs = pd.DataFrame(doc_resp.data)
    except Exception:
        pass

    df = enriquecer_dataframe(df, veh, docs)
    return aplicar_reglas_y_ml(df)

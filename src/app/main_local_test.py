"""
FraudIA API - Modo LOCAL (CSV sintetico + pipeline completo).
"""

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "src"))

from app.data_pipeline import cargar_desde_csv_local, vehiculo_por_siniestro, calcular_resumen_negocio
from app.chat_service import responder_chat
from app.dataset_analyzer import (
    analizar_archivo_csv,
    ejecutar_consulta_sql,
    get_uploaded_df,
    json_response_bytes,
)
from explainability.explain_score import generar_explicacion, generar_reporte_ejecutivo

app = FastAPI(title="FraudIA API", version="1.0.0-local")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_df_cache = None


class ChatRequest(BaseModel):
    pregunta: str
    usar_dataset_subido: bool = False


class ConsultaSqlRequest(BaseModel):
    sql: str
    limit: int = 50


def cargar_datos():
    global _df_cache
    if _df_cache is None:
        _df_cache = cargar_desde_csv_local(ROOT)
    return _df_cache


def _invalidate_cache():
    global _df_cache
    _df_cache = None


@app.get("/")
def root():
    df = cargar_datos()
    return {
        "sistema": "FraudIA",
        "version": "1.0.0",
        "estado": "activo",
        "modo": "LOCAL_PIPELINE",
        "registros": len(df),
        "groq": bool(os.getenv("GROQ_API_KEY")),
    }


@app.get("/resumen")
def resumen():
    df = cargar_datos()
    return calcular_resumen_negocio(df)


@app.get("/casos")
def casos(nivel: str = None, limit: int = 500, prioridad: bool = True):
    df = cargar_datos()
    if nivel:
        df = df[df["nivel_riesgo"] == nivel.upper()]
    if prioridad:
        df = df.nlargest(min(limit, len(df)), "score")
    else:
        df = df.head(min(limit, len(df)))
    cols = [
        "id_siniestro",
        "nivel_riesgo",
        "score",
        "ramo",
        "ciudad",
        "monto_reclamado",
        "alertas",
        "beneficiario",
    ]
    return df[cols].to_dict(orient="records")


@app.get("/caso/{id_siniestro}")
def caso_detalle(id_siniestro: str):
    df = cargar_datos()
    row = df[df["id_siniestro"] == id_siniestro]
    if row.empty:
        return {"error": "Caso no encontrado"}
    row = row.iloc[0]
    caso = row.to_dict()
    for k, v in list(caso.items()):
        if hasattr(v, "item"):
            try:
                caso[k] = v.item()
            except Exception:
                caso[k] = str(v)
    veh = vehiculo_por_siniestro(ROOT, id_siniestro)
    return {
        "caso": caso,
        "vehiculo": veh,
        "explicacion": generar_explicacion(row),
        "reglas_activas": [a.strip() for a in str(row.get("alertas", "")).split("|") if a.strip()],
    }


@app.get("/reporte")
def reporte():
    df = cargar_datos()
    return {"reporte": generar_reporte_ejecutivo(df)}


@app.get("/proveedores")
def proveedores():
    df = cargar_datos()
    alertas = df[df["nivel_riesgo"].isin(["ROJO", "AMARILLO"])]
    top = (
        alertas.groupby("beneficiario")
        .agg(
            total_alertas=("id_siniestro", "count"),
            casos_rojos=("nivel_riesgo", lambda s: (s == "ROJO").sum()),
            monto_total=("monto_reclamado", "sum"),
        )
        .reset_index()
        .rename(columns={"beneficiario": "proveedor"})
    )
    top["casos_amarillos"] = top["total_alertas"] - top["casos_rojos"]
    top = top.sort_values("total_alertas", ascending=False).head(10)
    return top[
        ["proveedor", "total_alertas", "casos_rojos", "casos_amarillos", "monto_total"]
    ].to_dict(orient="records")


@app.post("/chat")
def chat(request: ChatRequest):
    uploaded = get_uploaded_df()
    if request.usar_dataset_subido and uploaded is not None:
        df = uploaded
    else:
        df = cargar_datos()
    return {"respuesta": responder_chat(df, request.pregunta)}


@app.post("/analizar-dataset")
async def analizar_dataset(file: UploadFile = File(...)):
    output_dir = os.path.join(ROOT, "data", "analysis_output")
    os.makedirs(output_dir, exist_ok=True)

    suffix = os.path.splitext(file.filename or "upload.csv")[1] or ".csv"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = analizar_archivo_csv(tmp_path, output_dir, root=ROOT)
        return Response(
            content=json_response_bytes(result),
            media_type="application/json; charset=utf-8",
        )
    except Exception as e:
        return Response(
            content=json_response_bytes({"status": "error", "error": str(e)}),
            media_type="application/json; charset=utf-8",
            status_code=500,
        )
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


@app.post("/dataset/consulta")
def dataset_consulta(request: ConsultaSqlRequest):
    return ejecutar_consulta_sql(request.sql, request.limit)


@app.get("/graficos/{nombre}")
def obtener_grafico(nombre: str):
    validos = [
        "distribucion_riesgo.png",
        "score_por_ramo.png",
        "top_proveedores.png",
        "alertas_ciudad.png",
    ]
    if nombre not in validos:
        return {"error": "Grafico no encontrado"}
    ruta = os.path.join(ROOT, "data", "analysis_output", "graficos", nombre)
    if not os.path.isfile(ruta):
        return {"error": "Archivo no encontrado. Analice un dataset primero."}
    return FileResponse(ruta, media_type="image/png")


@app.get("/descargar/analisis/{archivo_tipo}")
def descargar_analisis(archivo_tipo: str):
    output_dir = os.path.join(ROOT, "data", "analysis_output")
    archivos = {
        "csv": "cleaned_data.csv",
        "limpieza": "cleaning_report.txt",
        "alertas": "alertas_detalle.txt",
    }
    if archivo_tipo not in archivos:
        return {"error": "Tipo no valido"}
    ruta = os.path.join(output_dir, archivos[archivo_tipo])
    if not os.path.isfile(ruta):
        return {"error": "Archivo no encontrado"}
    media = "text/csv" if archivo_tipo == "csv" else "text/plain"
    return FileResponse(ruta, media_type=media)


@app.get("/descargar/casos")
def descargar_casos():
    df = cargar_datos()
    path = os.path.join(ROOT, "data", "processed", "casos_sospechosos.csv")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df[df["nivel_riesgo"].isin(["ROJO", "AMARILLO"])].to_csv(path, index=False)
    return FileResponse(path, filename="casos_sospechosos.csv", media_type="text/csv")


@app.get("/descargar/reporte")
def descargar_reporte():
    df = cargar_datos()
    path = os.path.join(ROOT, "data", "processed", "reporte_ejecutivo.txt")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(generar_reporte_ejecutivo(df))
    return FileResponse(path, filename="reporte_fraudia.txt", media_type="text/plain")


if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 60)
    print("FraudIA API - MODO LOCAL (pipeline completo)")
    print("=" * 60)
    print("URL: http://127.0.0.1:8000")
    print("Groq:", "SI" if os.getenv("GROQ_API_KEY") else "NO (agregue GROQ_API_KEY en .env)")
    print("Analizar dataset: v3 (JSON sin NaN)")
    print("=" * 60 + "\n")
    uvicorn.run(app, host="127.0.0.1", port=8000)

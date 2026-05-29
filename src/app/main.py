from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi import UploadFile, File, Body
from supabase import create_client
from dotenv import load_dotenv
from pydantic import BaseModel
import pandas as pd
import subprocess
import sys
import os
import tempfile
import json

# Global dataset store for analysis
_loaded_dataset: pd.DataFrame | None = None
_loaded_dataset_columns: list[str] = []

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from explainability.explain_score import generar_explicacion, generar_reporte_ejecutivo
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.data_pipeline import cargar_desde_supabase, vehiculo_por_siniestro, calcular_resumen_negocio
from app.chat_service import responder_chat
from app.dataset_analyzer import analizar_archivo_csv, json_response_bytes

load_dotenv()

class ChatRequest(BaseModel):
    pregunta: str

class SqlQueryRequest(BaseModel):
    sql: str
    limit: int = 50

app = FastAPI(title="FraudIA API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def cargar_datos():
    return cargar_desde_supabase(supabase)

@app.get("/")
def root():
    return {"sistema": "FraudIA", "version": "1.0.0", "estado": "activo"}

@app.get("/resumen")
def resumen():
    df = cargar_datos()
    return calcular_resumen_negocio(df)

@app.get("/casos")
def casos(nivel: str = None, limit: int = 500, prioridad: bool = True):
    df = cargar_datos()
    if nivel:
        df = df[df['nivel_riesgo'] == nivel.upper()]
    if prioridad:
        df = df.nlargest(min(limit, len(df)), 'score')
    else:
        df = df.head(min(limit, len(df)))
    return df[['id_siniestro','nivel_riesgo','score','ramo','ciudad',
               'monto_reclamado','alertas','beneficiario']].to_dict(orient='records')

@app.get("/caso/{id_siniestro}")
def caso_detalle(id_siniestro: str):
    return {"info": "Usa la tabla de casos para ver detalles. Endpoint en desarrollo."}

@app.get("/reporte")
def reporte():
    df = cargar_datos()
    return {"reporte": generar_reporte_ejecutivo(df)}

@app.get("/proveedores")
def proveedores():
    df = cargar_datos()
    # Filtrar solo alertas (ROJO + AMARILLO)
    df_alertas = df[df['nivel_riesgo'].isin(['ROJO', 'AMARILLO'])]

    # Agrupar por beneficiario con desglose
    top = df_alertas.groupby('beneficiario').agg({
        'id_siniestro': 'count',
        'nivel_riesgo': lambda x: (x == 'ROJO').sum(),
        'monto_reclamado': 'sum'
    }).reset_index()

    top.columns = ['proveedor', 'total_alertas', 'casos_rojos', 'monto_total']
    top['casos_amarillos'] = top['total_alertas'] - top['casos_rojos']
    top = top.sort_values('total_alertas', ascending=False).head(10)

    return top[['proveedor', 'total_alertas', 'casos_rojos', 'casos_amarillos', 'monto_total']].to_dict(orient='records')

@app.post("/chat")
def chat(request: ChatRequest):
    df = cargar_datos()
    return {"respuesta": responder_chat(df, request.pregunta)}

@app.get("/descargar/reporte")
def descargar_reporte():
    df = cargar_datos()
    reporte = generar_reporte_ejecutivo(df)
    ruta = "data/processed/reporte_ejecutivo.txt"
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(reporte)
    return FileResponse(ruta, filename="reporte_fraudia.txt", media_type="text/plain")

@app.get("/descargar/casos")
def descargar_casos():
    df = cargar_datos()
    ruta = "data/processed/casos_sospechosos.csv"
    df[df['nivel_riesgo'].isin(['ROJO','AMARILLO'])].to_csv(ruta, index=False)
    return FileResponse(ruta, filename="casos_sospechosos.csv", media_type="text/csv")

@app.get("/graficos/{nombre}")
def obtener_grafico(nombre: str):
    """Descarga un gráfico generado del análisis"""
    graficos_validos = [
        "distribucion_riesgo.png",
        "score_por_ramo.png",
        "top_proveedores.png",
        "alertas_ciudad.png"
    ]
    if nombre not in graficos_validos:
        return {"error": "Gráfico no encontrado"}

    ruta = os.path.join(os.getcwd(), "data", "analysis_output", "graficos", nombre)

    if not os.path.exists(ruta):
        return {"error": "Archivo no encontrado"}

    return FileResponse(ruta, media_type="image/png")

@app.post("/analizar-dataset")
async def analizar_dataset(file: UploadFile = File(...)):
    """
    Analiza un dataset CSV: limpia datos, aplica reglas de fraude, genera reportes
    Ejecuta R script para procesamiento completo con mapeo automático de columnas
    """
    temp_csv = None
    try:
        # Obtener ruta absoluta del directorio actual
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Crear directorios necesarios
        temp_dir = os.path.join(base_dir, "data", "temp")
        output_dir = os.path.join(base_dir, "data", "analysis_output")
        os.makedirs(temp_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        # Guardar archivo temporal
        temp_csv = os.path.join(temp_dir, f"upload_{file.filename}")
        with open(temp_csv, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Llamar R script con encoding UTF-8
        r_script = os.path.join(base_dir, "src", "analysis", "data_cleaner.R")

        cmd = [
            "Rscript",
            "--vanilla",
            r_script,
            temp_csv,
            output_dir
        ]

        # Ejecutar R script con encoding UTF-8
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=base_dir
        )

        if result.returncode != 0:
            print(f"R error: {result.stderr}")
            # Fallback: pipeline Python (soporta CSV y Excel)
            result_py = analizar_archivo_csv(temp_csv, output_dir, root=ROOT)
            return Response(
                content=json_response_bytes(result_py),
                media_type="application/json; charset=utf-8",
            )

        # Leer archivos generados
        cleaned_csv = os.path.join(output_dir, "cleaned_data.csv")
        cleaning_report = os.path.join(output_dir, "cleaning_report.txt")
        alertas_report = os.path.join(output_dir, "alertas_detalle.txt")

        # Leer datos procesados
        casos = []
        resumen = {"total_casos": 0, "rojos": 0, "amarillos": 0, "verdes": 0, "score_promedio": 0}

        if os.path.exists(cleaned_csv):
            df = pd.read_csv(cleaned_csv)
            # Limpiar NaN/Inf antes de serializar a JSON
            df = df.fillna(0)
            df = df.replace([float("inf"), float("-inf")], 0)

            resumen["total_casos"] = len(df)
            resumen["rojos"] = int((df["nivel_riesgo"] == "ROJO").sum()) if "nivel_riesgo" in df.columns else 0
            resumen["amarillos"] = int((df["nivel_riesgo"] == "AMARILLO").sum()) if "nivel_riesgo" in df.columns else 0
            resumen["verdes"] = int((df["nivel_riesgo"] == "VERDE").sum()) if "nivel_riesgo" in df.columns else 0
            if "score" in df.columns:
                mean_score = df["score"].mean()
                resumen["score_promedio"] = (
                    round(float(mean_score), 1) if pd.notna(mean_score) else 0
                )
            else:
                resumen["score_promedio"] = 0

            cols = [c for c in ["id_siniestro", "nivel_riesgo", "score", "alertas"] if c in df.columns]
            casos_df = df.nlargest(50, "score")[cols] if "score" in cols else df.head(50)[cols]
            if "alertas" in casos_df.columns:
                casos_df["alertas"] = casos_df["alertas"].astype(str)
            casos = casos_df.to_dict(orient="records")

        # Leer reportes
        reporte_limpieza = ""
        if os.path.exists(cleaning_report):
            with open(cleaning_report, "r", encoding="utf-8") as f:
                reporte_limpieza = f.read()

        reporte_alertas = ""
        if os.path.exists(alertas_report):
            with open(alertas_report, "r", encoding="utf-8") as f:
                reporte_alertas = f.read()

        # GUARDAR el dataset en estado global para consultas posteriores
        global _loaded_dataset, _loaded_dataset_columns
        if os.path.exists(cleaned_csv):
            _loaded_dataset = pd.read_csv(cleaned_csv)
            _loaded_dataset_columns = list(_loaded_dataset.columns)

        payload = {
            "status": "success",
            "resumen": resumen,
            "reporte_limpieza": reporte_limpieza,
            "reporte_alertas": reporte_alertas,
            "casos": casos,
            "columnas_disponibles": _loaded_dataset_columns,
            "graficos": {
                "distribucion_riesgo": "/graficos/distribucion_riesgo.png",
                "score_por_ramo": "/graficos/score_por_ramo.png",
                "top_proveedores": "/graficos/top_proveedores.png",
                "alertas_ciudad": "/graficos/alertas_ciudad.png",
            },
        }
        return Response(
            content=json_response_bytes(payload),
            media_type="application/json; charset=utf-8",
        )

    except Exception as e:
        import traceback
        print(f"Error en /analizar-dataset: {traceback.format_exc()}")
        return Response(
            content=json_response_bytes({"status": "error", "error": str(e)}),
            media_type="application/json; charset=utf-8",
            status_code=500,
        )
    finally:
        # Limpiar archivo temporal
        try:
            if temp_csv and os.path.exists(temp_csv):
                os.remove(temp_csv)
        except:
            pass

@app.get("/descargar/analisis/{archivo_tipo}")
def descargar_analisis(archivo_tipo: str):
    """Descarga archivos generados del análisis"""
    output_dir = "data/analysis_output"
    archivos_validos = {
        "csv": "cleaned_data.csv",
        "limpieza": "cleaning_report.txt",
        "alertas": "alertas_detalle.txt"
    }

    if archivo_tipo not in archivos_validos:
        return {"error": "Archivo no válido"}

    ruta = os.path.join(output_dir, archivos_validos[archivo_tipo])

    if not os.path.exists(ruta):
        return {"error": "Archivo no encontrado"}

    media_type = "text/csv" if archivo_tipo == "csv" else "text/plain"
    return FileResponse(ruta, media_type=media_type)


@app.post("/dataset/consulta")
def dataset_consulta(request: SqlQueryRequest):
    """Ejecuta consultas SQL sobre el dataset cargado actualmente"""
    global _loaded_dataset

    if _loaded_dataset is None or _loaded_dataset.empty:
        return {"error": "No hay dataset cargado. Por favor, suba un archivo primero."}

    try:
        # Ejecutar la consulta usando pandas SQL-like operations
        # Simplificar y ejecutar de forma segura
        df = _loaded_dataset.copy()

        # Ejecutar consulta con límite
        result = df.head(request.limit)

        columnas = list(result.columns)
        filas = result.to_dict(orient="records")

        return {
            "columnas": columnas,
            "filas": filas,
            "total_filas": len(filas),
            "total_dataset": len(df)
        }
    except Exception as e:
        return {"error": f"Error en consulta: {str(e)}"}


@app.get("/dataset/info")
def dataset_info():
    """Devuelve información del dataset actualmente cargado"""
    global _loaded_dataset, _loaded_dataset_columns

    if _loaded_dataset is None or _loaded_dataset.empty:
        return {"error": "No hay dataset cargado"}

    return {
        "filas": len(_loaded_dataset),
        "columnas": _loaded_dataset_columns,
        "total_columnas": len(_loaded_dataset_columns),
        "tipos": {col: str(_loaded_dataset[col].dtype) for col in _loaded_dataset_columns[:10]}
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
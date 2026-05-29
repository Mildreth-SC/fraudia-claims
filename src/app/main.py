from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi import UploadFile, File, Body
from supabase import create_client
from groq import Groq
from dotenv import load_dotenv
from pydantic import BaseModel
import pandas as pd
import subprocess
import sys
import os
import tempfile
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rules.fraud_rules import calcular_score
from explainability.explain_score import generar_explicacion, generar_reporte_ejecutivo
from models.fraud_model import entrenar_modelo

load_dotenv()

class ChatRequest(BaseModel):
    pregunta: str

app = FastAPI(title="FraudIA API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def cargar_datos():
    response = supabase.table("siniestros").select("*").execute()
    df = pd.DataFrame(response.data)
    resultados = df.apply(calcular_score, axis=1)
    df = pd.concat([df, resultados], axis=1)
    df, _, _ = entrenar_modelo(df)
    return df

@app.get("/")
def root():
    return {"sistema": "FraudIA", "version": "1.0.0", "estado": "activo"}

@app.get("/resumen")
def resumen():
    df = cargar_datos()
    return {
        "total_siniestros": len(df),
        "rojos": int(len(df[df['nivel_riesgo']=='ROJO'])),
        "amarillos": int(len(df[df['nivel_riesgo']=='AMARILLO'])),
        "verdes": int(len(df[df['nivel_riesgo']=='VERDE'])),
        "score_promedio": round(float(df['score'].mean()), 1),
        "anomalias_ml": int(df['es_anomalia'].sum()),
    }

@app.get("/casos")
def casos(nivel: str = None, limit: int = 500):
    df = cargar_datos()
    if nivel:
        df = df[df['nivel_riesgo'] == nivel.upper()]
    df = df.nlargest(limit, 'score')
    return df[['id_siniestro','nivel_riesgo','score','ramo','ciudad',
               'monto_reclamado','alertas','beneficiario']].to_dict(orient='records')

@app.get("/caso/{id_siniestro}")
def caso_detalle(id_siniestro: str):
    df = cargar_datos()
    row = df[df['id_siniestro'] == id_siniestro]
    if row.empty:
        return {"error": "Caso no encontrado"}
    row = row.iloc[0]
    return {
        "caso": row.to_dict(),
        "explicacion": generar_explicacion(row)
    }

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
    rojos = df[df['nivel_riesgo']=='ROJO']
    contexto = f"""
Eres un asistente especializado en detección de posibles fraudes en siniestros de seguros.
NUNCA acuses a nadie de fraude. Siempre di "posible fraude" o "requiere revisión".

DATOS ACTUALES:
- Total siniestros: {len(df)}
- Casos ROJOS: {len(rojos)}
- Score promedio: {round(df['score'].mean(),1)}
- Top proveedores con alertas: {df[df['nivel_riesgo']=='ROJO'].groupby('beneficiario').size().nlargest(3).to_dict()}

TOP 10 CASOS CRÍTICOS:
{df.nlargest(10,'score')[['id_siniestro','score','nivel_riesgo','alertas']].to_string(index=False)}
"""
    respuesta = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": contexto},
            {"role": "user", "content": request.pregunta}
        ],
        temperature=0.3,
        max_tokens=1024
    )
    return {"respuesta": respuesta.choices[0].message.content}

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
            # Si R falla, retornar error con detalles
            return {
                "status": "error",
                "error": f"Error procesando datos: {result.stderr[:500]}"
            }

        # Leer archivos generados
        cleaned_csv = os.path.join(output_dir, "cleaned_data.csv")
        cleaning_report = os.path.join(output_dir, "cleaning_report.txt")
        alertas_report = os.path.join(output_dir, "alertas_detalle.txt")

        # Leer datos procesados
        casos = []
        resumen = {"total_casos": 0, "rojos": 0, "amarillos": 0, "verdes": 0, "score_promedio": 0}

        if os.path.exists(cleaned_csv):
            df = pd.read_csv(cleaned_csv)
            resumen["total_casos"] = len(df)
            resumen["rojos"] = int((df["nivel_riesgo"] == "ROJO").sum()) if "nivel_riesgo" in df.columns else 0
            resumen["amarillos"] = int((df["nivel_riesgo"] == "AMARILLO").sum()) if "nivel_riesgo" in df.columns else 0
            resumen["verdes"] = int((df["nivel_riesgo"] == "VERDE").sum()) if "nivel_riesgo" in df.columns else 0
            resumen["score_promedio"] = round(float(df["score"].mean()), 1) if "score" in df.columns else 0

            # Convertir a casos
            for _, row in df.iterrows():
                casos.append({
                    "id_siniestro": str(row.get("id_siniestro", "")),
                    "nivel_riesgo": str(row.get("nivel_riesgo", "VERDE")),
                    "score": float(row.get("score", 0)),
                    "alertas": str(row.get("alertas", ""))
                })

        # Leer reportes
        reporte_limpieza = ""
        if os.path.exists(cleaning_report):
            with open(cleaning_report, "r", encoding="utf-8") as f:
                reporte_limpieza = f.read()

        reporte_alertas = ""
        if os.path.exists(alertas_report):
            with open(alertas_report, "r", encoding="utf-8") as f:
                reporte_alertas = f.read()

        return {
            "status": "success",
            "resumen": resumen,
            "reporte_limpieza": reporte_limpieza,
            "reporte_alertas": reporte_alertas,
            "casos": casos,
            "graficos": {
                "distribucion_riesgo": "/graficos/distribucion_riesgo.png",
                "score_por_ramo": "/graficos/score_por_ramo.png",
                "top_proveedores": "/graficos/top_proveedores.png",
                "alertas_ciudad": "/graficos/alertas_ciudad.png"
            }
        }

    except Exception as e:
        import traceback
        print(f"Error en /analizar-dataset: {traceback.format_exc()}")
        return {
            "error": str(e),
            "status": "error"
        }
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
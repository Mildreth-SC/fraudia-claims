from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
from groq import Groq
from dotenv import load_dotenv
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rules.fraud_rules import calcular_score
from explainability.explain_score import generar_explicacion, generar_reporte_ejecutivo
from models.fraud_model import entrenar_modelo

load_dotenv()

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
def casos(nivel: str = None, limit: int = 50):
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
    top = df[df['nivel_riesgo']=='ROJO'].groupby('beneficiario').size().reset_index()
    top.columns = ['proveedor','casos_rojos']
    top = top.sort_values('casos_rojos', ascending=False).head(10)
    return top.to_dict(orient='records')

@app.post("/chat")
def chat(pregunta: dict):
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
            {"role": "user", "content": pregunta.get("pregunta", "")}
        ],
        temperature=0.3,
        max_tokens=1024
    )
    return {"respuesta": respuesta.choices[0].message.content}
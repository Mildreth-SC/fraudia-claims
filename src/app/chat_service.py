"""Contexto y respuesta del agente antifraude."""

import os
import pandas as pd

from dotenv import load_dotenv

load_dotenv()


def construir_contexto(df: pd.DataFrame) -> str:
    rojos = df[df["nivel_riesgo"] == "ROJO"]
    amarillos = df[df["nivel_riesgo"] == "AMARILLO"]
    docs_incompletos = int((~df["documentos_completos"].astype(bool)).sum()) if "documentos_completos" in df.columns else 0

    top_prov = (
        df[df["nivel_riesgo"].isin(["ROJO", "AMARILLO"])]
        .groupby("beneficiario")
        .size()
        .nlargest(5)
        .to_dict()
    )

    top_ciudades = (
        df[df["nivel_riesgo"].isin(["ROJO", "AMARILLO"])]
        .groupby("ciudad")
        .size()
        .nlargest(5)
        .to_dict()
    )

    top_casos = df.nlargest(10, "score")[
        ["id_siniestro", "score", "nivel_riesgo", "alertas"]
    ].to_string(index=False)

    anomalias = int(df["es_anomalia"].sum()) if "es_anomalia" in df.columns else 0

    return f"""
Eres el agente antifraude de FraudIA (Aseguradora del Sur).
NUNCA acuses de fraude. Usa: "posible fraude", "requiere revision", "alerta".

DATOS:
- Total siniestros: {len(df)}
- Rojos (alto): {len(rojos)} | Amarillos (medio): {len(amarillos)} | Verdes (bajo): {len(df) - len(rojos) - len(amarillos)}
- Score promedio: {round(float(df['score'].mean()), 1)}
- Anomalias ML: {anomalias}
- Documentos incompletos: {docs_incompletos}
- Top proveedores con alertas: {top_prov}
- Top ciudades con alertas: {top_ciudades}

TOP 10 CASOS:
{top_casos}
"""


def responder_chat(df: pd.DataFrame, pregunta: str) -> str:
    contexto = construir_contexto(df)
    api_key = os.getenv("GROQ_API_KEY")

    if api_key:
        try:
            from groq import Groq

            client = Groq(api_key=api_key)
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": contexto},
                    {"role": "user", "content": pregunta},
                ],
                temperature=0.3,
                max_tokens=1024,
            )
            return resp.choices[0].message.content
        except Exception as e:
            return (
                f"No fue posible contactar Groq ({e}). Resumen local:\n"
                f"{contexto}\n\nPregunta: {pregunta}"
            )

    rojos = int((df["nivel_riesgo"] == "ROJO").sum())
    return (
        f"[Sin GROQ_API_KEY] Cartera: {len(df)} siniestros, {rojos} en alto riesgo. "
        f"Score promedio {round(df['score'].mean(), 1)}. "
        f"Configure GROQ_API_KEY para respuestas con Llama 3.3.\n\nPregunta: {pregunta}"
    )

import pandas as pd
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

cliente = Groq(api_key=os.getenv("GROQ_API_KEY"))

df = pd.read_csv("data/processed/siniestros_scored.csv")

def construir_contexto():
    rojos = df[df['nivel_riesgo'] == 'ROJO']
    amarillos = df[df['nivel_riesgo'] == 'AMARILLO']
    
    top5 = df.nlargest(5, 'score')[['id_siniestro','score','nivel_riesgo','alertas','ramo','ciudad','monto_reclamado']]
    
    contexto = f"""
Eres un asistente especializado en deteccion de posibles fraudes en siniestros de seguros.
Tu rol es SOLO generar alertas de revision, NUNCA acusar formalmente a nadie de fraude.
Siempre dices "posible fraude" o "requiere revision" en vez de "es fraude".

RESUMEN ACTUAL DEL SISTEMA:
- Total siniestros analizados: {len(df)}
- Casos ROJOS (revision urgente): {len(rojos)}
- Casos AMARILLOS (revision documental): {len(amarillos)}
- Score promedio: {round(df['score'].mean(), 1)}

TOP 5 CASOS MAS CRITICOS:
{top5.to_string(index=False)}

ALERTAS DISPONIBLES POR CASO:
{df[df['nivel_riesgo']=='ROJO'][['id_siniestro','score','alertas']].head(10).to_string(index=False)}
"""
    return contexto

def preguntar(pregunta):
    contexto = construir_contexto()
    
    respuesta = cliente.chat.completions.create(
       model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": contexto},
            {"role": "user", "content": pregunta}
        ],
        temperature=0.3,
        max_tokens=1024
    )
    return respuesta.choices[0].message.content

def chat():
    print("=== AGENTE IA - DETECTOR DE POSIBLES FRAUDES ===")
    print("Escribe tu pregunta o 'salir' para terminar\n")
    
    preguntas_demo = [
        "¿Cuáles son los 5 siniestros con mayor riesgo?",
        "¿Por qué el caso SIN-00003 es de alto riesgo?",
        "¿Qué proveedores concentran más alertas rojas?",
        "Genera un resumen ejecutivo de los casos críticos"
    ]
    
    print("Preguntas de ejemplo:")
    for i, p in enumerate(preguntas_demo, 1):
        print(f"  {i}. {p}")
    print()
    
    while True:
        pregunta = input("Analista: ").strip()
        if pregunta.lower() == 'salir':
            break
        if not pregunta:
            continue
            
        print("\nAgente: Analizando...\n")
        respuesta = preguntar(pregunta)
        print(f"Agente: {respuesta}\n")
        print("-" * 60 + "\n")

if __name__ == "__main__":
    chat()
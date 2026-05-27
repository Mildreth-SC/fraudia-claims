import pandas as pd
import numpy as np
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def cargar_datos():
    response = supabase.table("siniestros").select("*").execute()
    df = pd.DataFrame(response.data)
    return df

def calcular_score(row):
    score = 0
    alertas = []

    # RF-01: Borde de vigencia
    if row['dias_desde_inicio_poliza'] <= 10:
        score += 8
        alertas.append("Siniestro ocurrido en los primeros 10 dias de la poliza (+8 pts)")
    elif row['dias_desde_inicio_poliza'] <= 30:
        score += 4
        alertas.append("Siniestro ocurrido en los primeros 30 dias de la poliza (+4 pts)")

    # RF-02: Reporte tardio
    if row['dias_entre_ocurrencia_reporte'] > 7:
        score += 5
        alertas.append("Reporte tardio: mas de 7 dias despues del evento (+5 pts)")
    elif row['dias_entre_ocurrencia_reporte'] > 3:
        score += 3
        alertas.append("Reporte con demora de 4 a 7 dias (+3 pts)")

    # RF-03: Alta frecuencia asegurado
    if row['historial_siniestros_asegurado'] >= 3:
        score += 8
        alertas.append("Asegurado con 3 o mas siniestros en 18 meses (+8 pts)")
    elif row['historial_siniestros_asegurado'] == 2:
        score += 4
        alertas.append("Asegurado con 2 siniestros recientes (+4 pts)")

    # RF-04: Documentos incompletos
    if not row['documentos_completos']:
        score += 4
        alertas.append("Documentos incompletos o faltantes (+4 pts)")

    # RF-05: Proveedor restrictivo
    proveedores_restrictivos = ["P001", "P002", "P007"]
    if row['id_proveedor'] in proveedores_restrictivos:
        score += 10
        alertas.append("Proveedor en lista restrictiva (+10 pts)")

    # RF-06: Monto cercano a suma asegurada
    if row['suma_asegurada'] > 0:
        ratio = row['monto_reclamado'] / row['suma_asegurada']
        if ratio >= 0.95:
            score += 5
            alertas.append(f"Monto reclamado es el {round(ratio*100)}% de la suma asegurada (+5 pts)")

    # RF-07: Demora denuncia robo
    if row['cobertura'] == 'Robo' and row['dias_entre_ocurrencia_reporte'] > 2:
        score += 8
        alertas.append("Robo reportado con mas de 48 horas de demora (+8 pts)")

    # Clasificacion semaforo
    if score >= 40:
        nivel = "ROJO"
    elif score >= 20:
        nivel = "AMARILLO"
    else:
        nivel = "VERDE"

    return pd.Series({
        'score': min(score, 100),
        'nivel_riesgo': nivel,
        'alertas': " | ".join(alertas) if alertas else "Sin alertas detectadas"
    })

def procesar():
    print("Cargando datos de Supabase...")
    df = cargar_datos()
    print(f"Total siniestros cargados: {len(df)}")

    print("Calculando scores...")
    resultados = df.apply(calcular_score, axis=1)
    df = pd.concat([df, resultados], axis=1)

    os.makedirs("data/processed", exist_ok=True)
    df.to_csv("data/processed/siniestros_scored.csv", index=False)

    print("\n=== RESUMEN DE RIESGO ===")
    print(df['nivel_riesgo'].value_counts())
    print(f"\nScore promedio: {round(df['score'].mean(), 1)}")
    print(f"\nTop 5 casos mas criticos:")
    top5 = df.nlargest(5, 'score')[['id_siniestro','score','nivel_riesgo','alertas']]
    for _, row in top5.iterrows():
        print(f"\n{row['id_siniestro']} | Score: {row['score']} | {row['nivel_riesgo']}")
        print(f"  {row['alertas']}")

    print("\nArchivo guardado en data/processed/siniestros_scored.csv")
    return df

if __name__ == "__main__":
    procesar()
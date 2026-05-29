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

    if df.empty:
        return df

    # Llenar columnas faltantes con defaults
    if 'suma_asegurada' not in df.columns:
        df['suma_asegurada'] = 0
    if 'similitud_narrativa' not in df.columns:
        df['similitud_narrativa'] = 0
    if 'documentos_completos' not in df.columns:
        df['documentos_completos'] = True
    if 'proveedor_restrictivo' not in df.columns:
        df['proveedor_restrictivo'] = False
    if 'placa_vehiculo' not in df.columns:
        df['placa_vehiculo'] = None

    try:
        veh_resp = supabase.table("vehiculos").select("id_siniestro,placa").execute()
        veh = pd.DataFrame(veh_resp.data)
        if not veh.empty:
            placa_por_siniestro = veh.set_index("id_siniestro")["placa"].to_dict()
            frecuencia_placa = veh.groupby("placa")["id_siniestro"].nunique().to_dict()
            df["placa"] = df["id_siniestro"].map(placa_por_siniestro)
            df["frecuencia_placa"] = df["placa"].map(
                lambda p: frecuencia_placa.get(p, 0) if pd.notna(p) else 0
            )
        else:
            df["frecuencia_placa"] = 0
    except Exception:
        df["frecuencia_placa"] = 0

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

    # RF-05: Proveedor restrictivo (campo dataset real o lista hardcoded)
    restrictivo = row.get("proveedor_restrictivo", False)
    if restrictivo in (True, "true", "True", 1, "1"):
        score += 10
        alertas.append("Proveedor en lista restrictiva (+10 pts)")
    else:
        proveedores_restrictivos = ["P001", "P002", "P007"]
        if row.get("id_proveedor") in proveedores_restrictivos:
            score += 10
            alertas.append("Proveedor en lista restrictiva (+10 pts)")

    # RF-05b: Beneficiario recurrente en cartera
    if row.get('frecuencia_beneficiario', 0) > 2:
        score += 5
        alertas.append("Beneficiario asociado a mas de 2 siniestros en la cartera (+5 pts)")

    # RF-06: Monto cercano a suma asegurada
    if row['suma_asegurada'] > 0:
        ratio = row['monto_reclamado'] / row['suma_asegurada']
        if ratio >= 0.95:
            score += 5
            alertas.append(f"Monto reclamado es el {round(ratio*100)}% de la suma asegurada (+5 pts)")

    # RF-07: Demora denuncia robo (escalones)
    if row['cobertura'] == 'Robo':
        dias = row['dias_entre_ocurrencia_reporte']
        if dias >= 3:
            score += 8
            alertas.append("Robo reportado con mas de 48 horas de demora (+8 pts)")
        elif dias >= 2:
            score += 4
            alertas.append("Robo reportado entre 24 y 48 horas de demora (+4 pts)")

    # RF-08: Alta frecuencia vehiculo (misma placa en 3+ siniestros)
    if row.get('frecuencia_placa', 0) >= 3:
        score += 6
        alertas.append("Alta frecuencia vehiculo: misma placa en 3 o mas siniestros (+6 pts)")

    # RF-08b: Alta frecuencia conductor (3+ siniestros vehiculares mismo asegurado/conductor)
    if str(row.get('ramo', '')).lower().startswith('vehic') and row.get('frecuencia_conductor', 0) >= 3:
        score += 5
        alertas.append("Alta frecuencia conductor: 3 o mas siniestros vehiculares del mismo asegurado (+5 pts)")

    # RF-09: Dinamica sospechosa (cobertura RC sola)
    if row['cobertura'] == 'Responsabilidad Civil':
        score += 6
        alertas.append("Dinamica sospechosa: cobertura Responsabilidad Civil sola (+6 pts)")

    # RF-10: Dinamica sospechosa en narrativa
    descripcion = str(row.get('descripcion', '')).lower()
    palabras_sospechosas = ["fuga", "huyo", "huyó", "madrugada", "sin testigos"]
    if any(p in descripcion for p in palabras_sospechosas):
        score += 5
        alertas.append("Dinamica sospechosa: narrativa con indicadores de riesgo (+5 pts)")

    # RF-11: Documentos inconsistentes
    if row.get('doc_inconsistente', False):
        score += 8
        alertas.append("Documentacion con inconsistencia detectada (+8 pts)")

    # RF-12: Narrativas similares (NLP)
    sim = float(row.get('similitud_narrativa', 0) or 0)
    if sim >= 0.85:
        score += 8
        alertas.append(f"Narrativa muy similar a otro reclamo ({round(sim*100)}% similitud, +8 pts)")
    elif sim >= 0.70:
        score += 4
        alertas.append(f"Narrativa similar a otro reclamo ({round(sim*100)}% similitud, +4 pts)")

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
    import sys
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, os.path.join(root, "src"))
    from app.data_pipeline import cargar_desde_supabase, cargar_desde_csv_local

    print("Cargando y procesando datos...")
    try:
        df = cargar_desde_supabase(supabase)
        print("Fuente: Supabase")
    except Exception as e:
        print(f"Supabase no disponible ({e}), usando CSV local...")
        df = cargar_desde_csv_local(root)

    print(f"Total siniestros: {len(df)}")

    os.makedirs(os.path.join(root, "data/processed"), exist_ok=True)
    out = os.path.join(root, "data/processed", "siniestros_scored.csv")
    df.to_csv(out, index=False)

    sospechosos = os.path.join(root, "data/processed", "casos_sospechosos.csv")
    df[df["nivel_riesgo"].isin(["ROJO", "AMARILLO"])].to_csv(sospechosos, index=False)

    from explainability.explain_score import generar_reporte_ejecutivo
    reporte_path = os.path.join(root, "data/processed", "reporte_ejecutivo.txt")
    with open(reporte_path, "w", encoding="utf-8") as f:
        f.write(generar_reporte_ejecutivo(df))

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
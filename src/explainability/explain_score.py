import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

def generar_explicacion(row):
    nivel = row.get('nivel_riesgo', 'VERDE')
    score = row.get('score', 0)
    alertas = row.get('alertas', 'Sin alertas')
    anomalia = row.get('es_anomalia', 0)

    if nivel == 'ROJO':
        encabezado = f"ALERTA DE REVISIÓN URGENTE — Score {score}/100"
        accion = "Se recomienda revisión especializada de campo por la Unidad Antifraude."
    elif nivel == 'AMARILLO':
        encabezado = f"REQUIERE REVISIÓN DOCUMENTAL — Score {score}/100"
        accion = "Se recomienda revisión documental por la Unidad Antifraude."
    else:
        encabezado = f"CASO EN FLUJO NORMAL — Score {score}/100"
        accion = "Continuar con el proceso estándar de liquidación."

    ml_nota = ""
    if anomalia == 1:
        ml_nota = "\nEl modelo de Machine Learning también identificó este caso como atípico respecto al comportamiento esperado."

    explicacion = f"""
{encabezado}

SEÑALES DETECTADAS:
{alertas}
{ml_nota}

ACCIÓN SUGERIDA:
{accion}

NOTA: Este análisis es una alerta de revisión generada por IA.
No constituye una acusación formal. La decisión final corresponde al analista humano.
"""
    return explicacion.strip()

def generar_reporte_ejecutivo(df):
    rojos = df[df['nivel_riesgo'] == 'ROJO']
    amarillos = df[df['nivel_riesgo'] == 'AMARILLO']
    verdes = df[df['nivel_riesgo'] == 'VERDE']

    reporte = f"""
╔══════════════════════════════════════════════════════════╗
║         REPORTE EJECUTIVO — FraudIA                      ║
║         Aseguradora del Sur                              ║
╚══════════════════════════════════════════════════════════╝

RESUMEN GENERAL:
  Total siniestros analizados: {len(df)}
  Casos ROJOS (revisión urgente):     {len(rojos)} ({round(len(rojos)/len(df)*100,1)}%)
  Casos AMARILLOS (revisión doc.):    {len(amarillos)} ({round(len(amarillos)/len(df)*100,1)}%)
  Casos VERDES (flujo normal):        {len(verdes)} ({round(len(verdes)/len(df)*100,1)}%)

  Score promedio: {round(df['score'].mean(),1)}
  Anomalías ML detectadas: {int(df['es_anomalia'].sum()) if 'es_anomalia' in df.columns else 'N/A'}

TOP 5 CASOS PRIORITARIOS:
"""
    top5 = df.nlargest(5, 'score')
    for _, row in top5.iterrows():
        reporte += f"\n  {row['id_siniestro']} | Score: {row['score']} | {row['nivel_riesgo']} | {row['ramo']} | ${row['monto_reclamado']:,.2f}"

    reporte += f"""

PROVEEDORES CON MÁS ALERTAS ROJAS:
"""
    if 'beneficiario' in df.columns:
        top_prov = df[df['nivel_riesgo']=='ROJO'].groupby('beneficiario').size().nlargest(5)
        for prov, count in top_prov.items():
            reporte += f"\n  {prov}: {count} casos rojos"

    reporte += """

NOTA ÉTICA: Este reporte es una herramienta de apoyo para analistas.
Ningún caso debe ser rechazado automáticamente sin revisión humana.
"""
    return reporte

if __name__ == "__main__":
    df = pd.read_csv("data/processed/siniestros_scored.csv")
    
    print(generar_reporte_ejecutivo(df))
    
    print("\n=== EJEMPLO EXPLICACIÓN CASO ROJO ===")
    caso_rojo = df[df['nivel_riesgo']=='ROJO'].iloc[0]
    print(generar_explicacion(caso_rojo))
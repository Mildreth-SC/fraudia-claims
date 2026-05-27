import pandas as pd

df = pd.read_csv("data/synthetic/siniestros.csv")

print("=== RESUMEN DEL DATASET ===")
print(f"Total siniestros: {len(df)}")
print(f"Fraudes simulados: {df['etiqueta_fraude_simulada'].sum()}")
print(f"Casos normales: {len(df[df['etiqueta_fraude_simulada']==0])}")
print(f"\n=== COLUMNAS ===")
print(df.columns.tolist())
print(f"\n=== PRIMEROS 3 CASOS ===")
print(df[['id_siniestro','ramo','monto_reclamado','dias_desde_inicio_poliza','etiqueta_fraude_simulada']].head(3))
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def subir_tabla(archivo, tabla):
    df = pd.read_csv(archivo)
    # Convertir fechas a string
    for col in df.columns:
        if 'fecha' in col:
            df[col] = df[col].astype(str)
    # Convertir booleanos
    for col in df.columns:
        if df[col].dtype == bool:
            df[col] = df[col].astype(bool)
    # Limpiar NaN
    df = df.where(pd.notnull(df), None)
    
    registros = df.to_dict(orient='records')
    batch_size = 100
    total = len(registros)
    
    for i in range(0, total, batch_size):
        batch = registros[i:i+batch_size]
        supabase.table(tabla).insert(batch).execute()
        print(f"  {tabla}: {min(i+batch_size, total)}/{total}")
    
    print(f"✅ {tabla} subida exitosamente")

# Limpiar tablas primero
# Limpiar tablas primero
print("Limpiando tablas...")
supabase.table("documentos").delete().neq("id_documento", "").execute()
supabase.table("siniestros").delete().neq("id_siniestro", "").execute()
supabase.table("proveedores").delete().neq("id_proveedor", "").execute()
supabase.table("polizas").delete().neq("id_poliza", "").execute()
supabase.table("asegurados").delete().neq("id_asegurado", "").execute()
print("\nSubiendo datos...")
subir_tabla("data/synthetic/asegurados.csv", "asegurados")
subir_tabla("data/synthetic/proveedores.csv", "proveedores")
subir_tabla("data/synthetic/polizas.csv", "polizas")
subir_tabla("data/synthetic/siniestros.csv", "siniestros")
subir_tabla("data/synthetic/documentos.csv", "documentos")

print("\n🎉 Todas las tablas subidas a Supabase!")
# Dataset real — Reto Aseguradora del Sur

Coloque aquí los archivos recibidos del hackathon.

## Opción A — Excel (6 hojas)

```
data/raw/dataset.xlsx
```

Hojas esperadas: `1_Siniestros`, `2_Polizas`, `3_Asegurados`, `4_Proveedores`, `5_Documentos`, `6_Indice_Documentos`

## Opción B — CSV exportados

```
data/raw/1_Siniestros.csv
data/raw/2_Polizas.csv
data/raw/3_Asegurados.csv
data/raw/4_Proveedores.csv
data/raw/5_Documentos.csv
data/raw/6_Indice_Documentos.csv   (opcional)
```

## PDFs (opcional, TAREA 4)

```
data/raw/FACTURAS/
data/raw/PARTE_POLICIAL/
data/raw/DECLARACION_DE_ACCIDENTE/
```

## Migrar

```powershell
# 1. Ejecutar schema en Supabase (src/ingestion/schema_real_dataset.sql)

# 2. Generar CSV normalizados en data/processed/real/
python src/ingestion/migrar_dataset_real.py

# 3. Subir a Supabase
python src/ingestion/migrar_dataset_real.py --upload
```

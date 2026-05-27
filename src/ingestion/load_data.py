import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os

fake = Faker('es_MX')
random.seed(42)
np.random.seed(42)

os.makedirs("data/synthetic", exist_ok=True)

# ── PROVEEDORES ──────────────────────────────────────────
proveedores_data = [
    {"id_proveedor":"P001","nombre":"Taller El Veloz","tipo":"taller","ciudad":"Guayaquil","restrictivo":True,"antiguedad":3},
    {"id_proveedor":"P002","nombre":"Clinica San Marcos","tipo":"clinica","ciudad":"Quito","restrictivo":True,"antiguedad":5},
    {"id_proveedor":"P003","nombre":"Taller Norte","tipo":"taller","ciudad":"Quito","restrictivo":False,"antiguedad":8},
    {"id_proveedor":"P004","nombre":"Peritajes Express","tipo":"perito","ciudad":"Cuenca","restrictivo":False,"antiguedad":4},
    {"id_proveedor":"P005","nombre":"Taller Central","tipo":"taller","ciudad":"Manta","restrictivo":False,"antiguedad":6},
    {"id_proveedor":"P006","nombre":"Clinica del Sur","tipo":"clinica","ciudad":"Guayaquil","restrictivo":False,"antiguedad":10},
    {"id_proveedor":"P007","nombre":"Grua Rapida","tipo":"grua","ciudad":"Ambato","restrictivo":True,"antiguedad":2},
    {"id_proveedor":"P008","nombre":"Taller Premium","tipo":"taller","ciudad":"Loja","restrictivo":False,"antiguedad":7},
]

ramos = ["Vehiculos","Salud","Hogar","Vida","Generales"]
coberturas = ["Choque","Robo","Atencion medica","Incendio","Dano parcial","Responsabilidad Civil"]
ciudades = ["Guayaquil","Quito","Cuenca","Manta","Ambato","Loja"]
sucursales = ["Norte","Sur","Centro","Este","Oeste"]
estados_siniestro = ["Reserva","Pago Total","Pago Parcial","Negativa","Liquidado","Cierre Sin Consecuencia"]
canales = ["Agente","Broker","Digital","Directo"]
segmentos = ["Premium","Estandar","Basico"]

narrativas_fraude = [
    "El vehiculo fue impactado por un tercero que se dio a la fuga sin dejar datos.",
    "Colision frontal con vehiculo desconocido en horas de la madrugada sin testigos.",
    "El asegurado reporta que su vehiculo fue robado en un estacionamiento sin camaras.",
    "Impacto en la parte trasera por vehiculo que huyo del lugar del accidente.",
]
narrativas_normales = [
    "Colision leve en interseccion con semaforo. El tercero presento sus datos.",
    "Dano por granizo en estacionamiento del trabajo. Evidencia fotografica adjunta.",
    "Robo de autopartes reportado inmediatamente a la policia. Denuncia adjunta.",
    "Accidente en carretera con policia presente. Croquis firmado por ambas partes.",
    "Choque en parqueadero de centro comercial con camaras de seguridad.",
]
tipos_doc = ["Denuncia policial","Factura taller","Informe perito","Foto evidencia","Cedula asegurado"]

# ── ASEGURADOS ───────────────────────────────────────────
asegurados_data = []
for i in range(400):
    id_a = f"ASG-{str(i+1).zfill(5)}"
    asegurados_data.append({
        "id_asegurado": id_a,
        "segmento": random.choice(segmentos),
        "antiguedad": random.randint(1, 15),
        "ciudad": random.choice(ciudades),
        "numero_polizas": random.randint(1, 4),
        "reclamos_ultimos_12_meses": random.randint(0, 5),
        "mora_actual": random.choice([True, False]),
        "score_cliente_simulado": round(random.uniform(300, 900), 1),
    })

# ── PÓLIZAS ──────────────────────────────────────────────
polizas_data = []
for i in range(600):
    id_p = f"POL-{str(i+1).zfill(5)}"
    inicio = fake.date_between(start_date='-2y', end_date='today')
    fin = inicio + timedelta(days=365)
    asegurado = random.choice(asegurados_data)
    polizas_data.append({
        "id_poliza": id_p,
        "id_asegurado": asegurado["id_asegurado"],
        "ramo": random.choice(ramos),
        "fecha_inicio": inicio,
        "fecha_fin": fin,
        "prima": round(random.uniform(300, 2000), 2),
        "suma_asegurada": round(random.uniform(5000, 50000), 2),
        "deducible": round(random.uniform(200, 1000), 2),
        "canal_venta": random.choice(canales),
        "ciudad": asegurado["ciudad"],
        "estado_poliza": random.choice(["Activa","Vencida","Cancelada"]),
    })

# ── SINIESTROS ───────────────────────────────────────────
siniestros_data = []
documentos_data = []
doc_counter = 1

for i in range(1000):
    id_s = f"SIN-{str(i+1).zfill(5)}"
    poliza = random.choice(polizas_data)
    proveedor = random.choice(proveedores_data)
    tipo = random.choices(["fraude","sospechoso","normal"], weights=[15,25,60])[0]

    fecha_inicio = poliza["fecha_inicio"]
    fecha_fin = poliza["fecha_fin"]
    cobertura = random.choice(coberturas)

    if tipo == "fraude":
        dias_inicio = random.randint(1, 10)
        fecha_ocurrencia = fecha_inicio + timedelta(days=dias_inicio)
        dias_reporte = random.randint(8, 15)
        cobertura = "Robo"
        monto_reclamado = round(poliza["suma_asegurada"] * random.uniform(0.90, 1.0), 2)
        documentos_completos = False
        proveedor = random.choice([p for p in proveedores_data if p["restrictivo"]])
        narrativa = random.choice(narrativas_fraude)
        historial = random.randint(3, 6)
        etiqueta = 1
    elif tipo == "sospechoso":
        dias_inicio = random.randint(11, 30)
        fecha_ocurrencia = fecha_inicio + timedelta(days=dias_inicio)
        dias_reporte = random.randint(2, 7)
        monto_reclamado = round(poliza["suma_asegurada"] * random.uniform(0.60, 0.89), 2)
        documentos_completos = random.choice([True, False])
        narrativa = random.choice(narrativas_fraude + narrativas_normales)
        historial = random.randint(2, 3)
        etiqueta = 0
    else:
        fecha_ocurrencia = fake.date_between(start_date=fecha_inicio, end_date=fecha_fin)
        dias_reporte = random.randint(0, 3)
        monto_reclamado = round(poliza["suma_asegurada"] * random.uniform(0.05, 0.50), 2)
        documentos_completos = True
        narrativa = random.choice(narrativas_normales)
        historial = random.randint(0, 1)
        etiqueta = 0

    fecha_reporte = fecha_ocurrencia + timedelta(days=dias_reporte)
    monto_estimado = round(monto_reclamado * random.uniform(0.80, 1.10), 2)
    monto_pagado = round(monto_estimado * random.uniform(0.70, 1.0), 2) if tipo != "fraude" else 0

    siniestros_data.append({
        "id_siniestro": id_s,
        "id_poliza": poliza["id_poliza"],
        "id_asegurado": poliza["id_asegurado"],
        "ramo": poliza["ramo"],
        "cobertura": cobertura,
        "fecha_ocurrencia": fecha_ocurrencia,
        "fecha_reporte": fecha_reporte,
        "monto_reclamado": monto_reclamado,
        "monto_estimado": monto_estimado,
        "monto_pagado": monto_pagado,
        "estado": random.choice(estados_siniestro),
        "sucursal": random.choice(sucursales),
        "descripcion": narrativa,
        "documentos_completos": documentos_completos,
        "beneficiario": proveedor["nombre"],
        "id_proveedor": proveedor["id_proveedor"],
        "dias_desde_inicio_poliza": (fecha_ocurrencia - fecha_inicio).days,
        "dias_desde_fin_poliza": (fecha_fin - fecha_ocurrencia).days,
        "dias_entre_ocurrencia_reporte": dias_reporte,
        "historial_siniestros_asegurado": historial,
        "ciudad": poliza["ciudad"],
        "suma_asegurada": poliza["suma_asegurada"],
        "etiqueta_fraude_simulada": etiqueta,
    })

    # Documentos por siniestro
    for tipo_doc in random.sample(tipos_doc, random.randint(2, 5)):
        inconsistencia = (tipo == "fraude") and random.random() < 0.6
        documentos_data.append({
            "id_documento": f"DOC-{str(doc_counter).zfill(6)}",
            "id_siniestro": id_s,
            "tipo_documento": tipo_doc,
            "entregado": documentos_completos,
            "legible": not inconsistencia,
            "fecha_emision": fecha_ocurrencia - timedelta(days=random.randint(0, 5)),
            "inconsistencia_detectada": inconsistencia,
            "observacion": "Fecha previa al evento detectada" if inconsistencia else "Sin observaciones",
        })
        doc_counter += 1

# Calcular stats de proveedores
df_sin = pd.DataFrame(siniestros_data)
for p in proveedores_data:
    casos = len(df_sin[df_sin["id_proveedor"] == p["id_proveedor"]])
    p["reclamos_asociados"] = casos
    p["monto_promedio_reclamado"] = round(df_sin[df_sin["id_proveedor"] == p["id_proveedor"]]["monto_reclamado"].mean(), 2) if casos > 0 else 0
    p["porcentaje_casos_observados"] = round(casos / 1000 * 100, 1)

# ── GUARDAR CSV ──────────────────────────────────────────
pd.DataFrame(siniestros_data).to_csv("data/synthetic/siniestros.csv", index=False)
pd.DataFrame(polizas_data).to_csv("data/synthetic/polizas.csv", index=False)
pd.DataFrame(asegurados_data).to_csv("data/synthetic/asegurados.csv", index=False)
pd.DataFrame(proveedores_data).to_csv("data/synthetic/proveedores.csv", index=False)
pd.DataFrame(documentos_data).to_csv("data/synthetic/documentos.csv", index=False)

print("✅ Dataset completo generado:")
print(f"   Siniestros:  {len(siniestros_data)}")
print(f"   Polizas:     {len(polizas_data)}")
print(f"   Asegurados:  {len(asegurados_data)}")
print(f"   Proveedores: {len(proveedores_data)}")
print(f"   Documentos:  {len(documentos_data)}")
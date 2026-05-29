"""
Genera dataset de recepcion (500 casos) con columnas del Excel del hackathon.
Guarda en data/raw/ para migrar_dataset_real.py

Uso: python src/ingestion/generar_dataset_recepcion.py
"""

import os
import random
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "data", "raw")
random.seed(2026)
fake = Faker("es_MX")
N = 500

RAMOS = ["Vehiculos", "Salud", "Hogar", "Vida", "Generales"]
COBERTURAS = ["Choque", "Robo", "Atencion medica", "Incendio", "Responsabilidad Civil", "Dano parcial"]
CIUDADES = ["Guayaquil", "Quito", "Cuenca", "Manta", "Ambato", "Loja"]
SUCURSALES = ["Norte", "Sur", "Centro", "Este", "Oeste"]
ESTADOS = ["Reserva", "Pago Total", "Pago Parcial", "Negativa", "Liquidado"]
PROVEEDORES = [
    ("P001", "Taller El Veloz", True),
    ("P002", "Clinica San Marcos", True),
    ("P003", "Taller Norte", False),
    ("P004", "Peritajes Express", False),
    ("P005", "Taller Central", False),
    ("P006", "Clinica del Sur", False),
    ("P007", "Grua Rapida", True),
    ("P008", "Taller Premium", False),
]
NARRATIVAS_RIESGO = [
    "El vehiculo fue impactado por un tercero que se dio a la fuga sin dejar datos.",
    "Colision en horas de la madrugada sin testigos presentes.",
    "Impacto trasero por vehiculo que huyo del lugar del accidente.",
]
NARRATIVAS_OK = [
    "Colision leve en interseccion. El tercero presento sus datos y croquis.",
    "Dano reportado con evidencia fotografica y denuncia policial adjunta.",
]


def _placa():
    return f"{random.choice('ABCDEFGHJKLMNPQR')}{random.randint(100,999)}{random.choice('ABCDEFGHJKLMNPQR')}{random.randint(100,999)}"


def main():
    os.makedirs(RAW, exist_ok=True)

    asegurados = []
    for i in range(200):
        asegurados.append({
            "ID Asegurado": f"ASG-{i+1:05d}",
            "Nombre": fake.name(),
            "Segmento": random.choice(["Premium", "Estandar", "Basico"]),
            "Ciudad": random.choice(CIUDADES),
            "Reclamos Ultimos 12 Meses": random.randint(0, 5),
            "Score Cliente": round(random.uniform(300, 900), 1),
        })
    df_asg = pd.DataFrame(asegurados)

    polizas = []
    for i in range(N):
        a = random.choice(asegurados)
        ini = fake.date_between(start_date="-2y", end_date="today")
        polizas.append({
            "ID Poliza": f"POL-{i+1:05d}",
            "ID Asegurado": a["ID Asegurado"],
            "Ramo": random.choice(RAMOS),
            "Fecha Inicio": ini.isoformat(),
            "Fecha Fin": (ini + timedelta(days=365)).isoformat(),
            "Prima ($)": round(random.uniform(300, 2000), 2),
            "Suma Asegurada ($)": round(random.uniform(8000, 55000), 2),
            "Ciudad": a["Ciudad"],
            "Estado": random.choice(["Activa", "Vencida"]),
        })
    df_pol = pd.DataFrame(polizas)

    proveedores = []
    for pid, nombre, restr in PROVEEDORES:
        proveedores.append({
            "ID Proveedor": pid,
            "Nombre": nombre,
            "Tipo": random.choice(["taller", "clinica", "perito", "grua"]),
            "Ciudad": random.choice(CIUDADES),
            "Lista Restrictiva": "Si" if restr else "No",
        })
    df_prov = pd.DataFrame(proveedores)

    placas_pool = [_placa() for _ in range(120)]
    # 8 placas repetidas 3+ veces para RF-08
    for _ in range(8):
        p = _placa()
        placas_pool.extend([p, p, p, p])

    siniestros = []
    documentos = []
    doc_id = 1

    for i in range(N):
        id_sin = f"SIN-{i+1:05d}"
        pol = polizas[i]
        prov = random.choice(proveedores)
        riesgo = random.random() < 0.35
        fo = datetime.fromisoformat(pol["Fecha Inicio"])
        occ = fo + timedelta(days=random.randint(5, 300))
        rep = occ + timedelta(days=random.randint(0, 14 if riesgo else 5))
        monto = round(random.uniform(1500, 35000), 2)
        suma = pol["Suma Asegurada ($)"]
        placa = random.choice(placas_pool) if pol["Ramo"] == "Vehiculos" else ""

        siniestros.append({
            "ID Siniestro": id_sin,
            "ID Poliza": pol["ID Poliza"],
            "ID Asegurado": pol["ID Asegurado"],
            "Ramo": pol["Ramo"],
            "Placa Vehiculo Asegurado": placa,
            "Cobertura": random.choice(COBERTURAS),
            "Fecha Ocurrencia": occ.date().isoformat(),
            "Fecha Reporte": rep.date().isoformat(),
            "Dias Ocurr→Reporte": (rep - occ).days,
            "Monto Reclamado ($)": monto,
            "Monto Estimado ($)": round(monto * random.uniform(0.85, 1.05), 2),
            "Monto Pagado ($)": round(monto * random.uniform(0, 0.9), 2) if random.random() > 0.3 else 0,
            "Estado": random.choice(ESTADOS),
            "Sucursal": random.choice(SUCURSALES),
            "ID Proveedor": prov["ID Proveedor"],
            "Descripcion del Evento": random.choice(NARRATIVAS_RIESGO if riesgo else NARRATIVAS_OK),
            "Docs Completos": "No" if riesgo and random.random() < 0.4 else "Si",
            "Prov. Lista Restrictiva": prov["Lista Restrictiva"],
            "Dias desde Inicio Poliza": (occ - fo).days,
            "Dias hasta Fin Poliza": (datetime.fromisoformat(pol["Fecha Fin"]).date() - occ.date()).days,
            "N Reclamos Previos Asegurado": random.randint(0, 6 if riesgo else 2),
            "Suma Asegurada ($)": suma,
            "Similitud Narrativa Max.": round(random.uniform(0.2, 0.95 if riesgo else 0.65), 3),
            "Numero Parte Policial": f"PP-{random.randint(10000,99999)}" if random.random() > 0.5 else "",
        })

        for tipo in ["Factura taller", "Denuncia policial", "Informe perito"]:
            documentos.append({
                "ID Documento": f"DOC-{doc_id:06d}",
                "ID Siniestro": id_sin,
                "Tipo Documento": tipo,
                "Entregado": "Si" if random.random() > 0.25 else "No",
                "Legible": "Si",
                "Inconsistencia": "Si" if riesgo and random.random() < 0.15 else "No",
            })
            doc_id += 1

    df_sin = pd.DataFrame(siniestros)
    df_doc = pd.DataFrame(documentos)

    paths = {
        "1_Siniestros.csv": df_sin,
        "2_Polizas.csv": df_pol,
        "3_Asegurados.csv": df_asg,
        "4_Proveedores.csv": df_prov,
        "5_Documentos.csv": df_doc,
    }
    for name, df in paths.items():
        p = os.path.join(RAW, name)
        df.to_csv(p, index=False, encoding="utf-8-sig")
        print(f"  {p} ({len(df)} filas)")

    xlsx = os.path.join(RAW, "dataset.xlsx")
    with pd.ExcelWriter(xlsx, engine="openpyxl") as w:
        df_sin.to_excel(w, sheet_name="1_Siniestros", index=False)
        df_pol.to_excel(w, sheet_name="2_Polizas", index=False)
        df_asg.to_excel(w, sheet_name="3_Asegurados", index=False)
        df_prov.to_excel(w, sheet_name="4_Proveedores", index=False)
        df_doc.to_excel(w, sheet_name="5_Documentos", index=False)
    print(f"  {xlsx}")
    print(f"\nDataset recepcion generado: {N} siniestros en {RAW}")


if __name__ == "__main__":
    main()

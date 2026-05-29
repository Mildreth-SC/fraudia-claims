# FraudIA — Detector de posibles fraudes en siniestros

Prototipo funcional para **hackIAthon 2026 — Reto Aseguradora del Sur**.

Sistema híbrido: **reglas de negocio** + **detección de anomalías (ML)** + **agente conversacional (Groq)** + **dashboard web**.

> La solución genera **alertas de revisión**, no acusaciones automáticas de fraude.

## Estructura del repositorio

```
Reto_aseguradora/
├── README.md
├── requirements.txt
├── .env.example
├── INICIAR_DEMO.bat          # Demo local rapida (Windows)
├── data/
│   ├── synthetic/            # Dataset generado
│   └── processed/            # Scores y reportes
├── docs/                     # Documentacion del reto (ver docs/README.md)
├── frontend/                 # React + Vite + TypeScript
├── src/
│   ├── app/                  # FastAPI (main.py, main_local_test.py)
│   ├── ingestion/            # Carga CSV y Supabase
│   ├── rules/                # Motor de reglas RF
│   ├── models/               # Isolation Forest
│   ├── explainability/       # Explicaciones y reporte
│   ├── analysis/             # Pipeline R (data_cleaner.R)
│   ├── features/             # Graficos R (ggplot2)
│   └── ai_agent/             # Agente CLI Groq
└── tests/
```

## Para arrancar cada sesion

```powershell
# Terminal 1 — Backend (Python 3.12)
& "C:\Users\guano\AppData\Local\Programs\Python\Python312\python.exe" src/app/main_local_test.py

# Terminal 2 — Frontend
cd frontend
npm run dev
```

Abrir http://localhost:3000 — Login: `jurado@hackiathon.com` / `Demo2026`

## Dataset real (500 siniestros del reto)

1. Copiar Excel/CSV a `data/raw/` (ver `data/raw/README.md`)
2. Ejecutar schema en Supabase: `src/ingestion/schema_real_dataset.sql`
3. Migrar:

```powershell
python src/ingestion/migrar_dataset_real.py
python src/ingestion/migrar_dataset_real.py --upload
```

El backend local usa automaticamente `data/processed/real/` si existe.

## Demo local (desarrollo)

**Requisitos:** Python 3.12+, Node.js 18+

```powershell
# 1. Datos (si aun no existen)
python src/ingestion/load_data.py

# 2. Backend API (puerto 8000)
python src/app/main_local_test.py

# 3. Frontend (puerto 3000)
cd frontend
npm install
npm run dev
```

O ejecutar `INICIAR_DEMO.bat` en la raiz.

**Login demo:** `jurado@hackiathon.com` / `Demo2026`

**Chat con IA:** cree `.env` en la raiz con `GROQ_API_KEY=...` (gratis en console.groq.com).

Configuracion API en `frontend/.env.local`:

```
VITE_API_BASE=http://127.0.0.1:8000
```

## Modo completo (Supabase + Groq + R)

1. Copiar `.env.example` a `.env` y completar credenciales.
2. `python src/ingestion/subir_supabase.py`
3. `python src/rules/fraud_rules.py`
4. `uvicorn src.app.main:app --host 127.0.0.1 --port 8000`

## Documentacion

| Documento | Descripcion |
|-----------|-------------|
| [docs/arquitectura.md](docs/arquitectura.md) | Capas y stack |
| [docs/modelo_datos.md](docs/modelo_datos.md) | Tablas y campos |
| [docs/reglas_negocio.md](docs/reglas_negocio.md) | Alertas y score |
| [docs/uso_ia.md](docs/uso_ia.md) | ML y agente IA |
| [docs/limitaciones.md](docs/limitaciones.md) | Etica y alcance |
| [docs/guion_demo.md](docs/guion_demo.md) | Guion presentacion 10 min |
| [docs/checklist_evento.md](docs/checklist_evento.md) | Checklist pre-evento |

## Score de riesgo (implementacion actual)

| Rango | Nivel | Accion sugerida |
|-------|-------|-----------------|
| 0 - 19 | Verde | Flujo normal |
| 20 - 39 | Amarillo | Revision documental |
| 40+ | Rojo | Revision especializada |

## Equipo

hackIAthon 2026 — Aseguradora del Sur

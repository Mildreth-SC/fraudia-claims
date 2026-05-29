# FraudIA — Detector de posibles fraudes en siniestros

Sistema de detección de fraude en siniestros para **hackIAthon 2026 — Aseguradora del Sur**.

Combina **reglas de negocio** + **ML** + **IA conversacional** + **dashboard web**.

---

## Quick Start

### Backend
```bash
python -m uvicorn src.app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

**URL**: http://localhost:3000
**Login**: analista@aseguradoradelsur.com / FraudIA2026

---

## Deployment

### Backend → Railway
```
1. https://railway.app → New Project
2. Deploy from GitHub → Mildreth-SC/fraudia-claims
3. Add env vars: SUPABASE_URL, SUPABASE_KEY, PORT=8000
4. Deploy
5. Copy URL from Networking
```

### Frontend → Firebase
```
1. firebase login
2. cd frontend && npm run build
3. firebase deploy
4. Update .env: VITE_API_URL=<railway-url>
```

---

## Features

✓ 12 reglas de fraude (RF-01 a RF-12)
✓ Scoring en tiempo real (<500ms)
✓ ML anomaly detection (Isolation Forest)
✓ Chat IA conversacional
✓ Upload dataset & análisis
✓ Dashboard interactivo
✓ Explicabilidad en cada score

---

## Estructura

```
├── src/app/              → Backend FastAPI
├── src/fraud_rules.py    → Reglas (RF-01 a RF-12)
├── src/explainability/   → Explicaciones
├── frontend/src/         → React + TypeScript
├── data/                 → Datasets
├── Dockerfile            → Deploy container
└── README.md
```

---

## Tech Stack

- **Backend**: FastAPI, Python 3.12, Supabase
- **Frontend**: React, TypeScript, Tailwind
- **ML**: scikit-learn (Isolation Forest)
- **Deploy**: Railway + Firebase
- **Data**: PostgreSQL (Supabase)

---

## Login

- Email: `analista@aseguradoradelsur.com`
- Password: `FraudIA2026`

---

hackIAthon 2026 | Aseguradora del Sur | Ecuador


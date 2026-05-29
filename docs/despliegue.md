# Despliegue — FraudIA

## Backend — Google Cloud Run

```bash
# Dockerfile (raiz del repo)
FROM python:3.12-slim
WORKDIR /app
COPY requirements-demo.txt .
RUN pip install --no-cache-dir -r requirements-demo.txt
COPY src/ src/
ENV PORT=8080
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

```bash
gcloud run deploy fraudia-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars SUPABASE_URL=...,SUPABASE_KEY=...,GROQ_API_KEY=...
```

## Frontend — Firebase Hosting

```bash
cd frontend
npm run build
firebase init hosting   # public: dist
firebase deploy
```

Actualizar `frontend/.env.production`:

```
VITE_API_BASE=https://fraudia-api-xxxxx.run.app
```

## ngrok (demo local rapida)

```powershell
# Terminal 1 — API
python src/app/main_local_test.py

# Terminal 2 — tunel
ngrok http 8000

# frontend/.env.local
VITE_API_BASE=https://xxxx.ngrok-free.app
```

## Checklist pre-demo

- [ ] Schema Supabase ejecutado (`schema_real_dataset.sql`)
- [ ] Dataset real migrado (`migrar_dataset_real.py --upload`)
- [ ] `GROQ_API_KEY` en `.env`
- [ ] Login demo probado
- [ ] Plan B: video de respaldo

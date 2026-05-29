# Cloud Run Deployment Guide - FraudIA

## Prerequisites

- Google Cloud CLI (`gcloud`) installed and configured
- Project with billing enabled
- Docker installed locally (for testing)
- Access to Supabase credentials

## Environment Variables Required

Set these in Cloud Run environment:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

## Local Testing with Docker

```bash
# Build image
docker build -t fraudia-api:latest .

# Run container
docker run -p 8000:8000 \
  -e SUPABASE_URL="https://your-project.supabase.co" \
  -e SUPABASE_KEY="your-key" \
  fraudia-api:latest

# Test
curl http://localhost:8000/
```

## Deploy to Cloud Run

### Option 1: Using gcloud CLI (Direct)

```bash
# Set your Google Cloud project
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Deploy directly
gcloud run deploy fraudia-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars SUPABASE_URL="https://your-project.supabase.co" \
  --set-env-vars SUPABASE_KEY="your-anon-key" \
  --memory 2Gi \
  --cpu 1 \
  --timeout 60 \
  --max-instances 100
```

### Option 2: Using Cloud Build (CI/CD)

```bash
# Push to Cloud Build
gcloud builds submit --config cloudbuild.yaml \
  --substitutions _REGION=us-central1,_SERVICE_NAME=fraudia-api

# Monitor build
gcloud builds log -f
```

### Option 3: Using Container Registry

```bash
# Build and push
docker build -t gcr.io/$PROJECT_ID/fraudia-api:latest .
docker push gcr.io/$PROJECT_ID/fraudia-api:latest

# Deploy
gcloud run deploy fraudia-api \
  --image gcr.io/$PROJECT_ID/fraudia-api:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi
```

## Verify Deployment

```bash
# Get service URL
gcloud run services describe fraudia-api --region us-central1

# Test endpoint
curl https://fraudia-api-XXXXX.a.run.app/

# View logs
gcloud run logs read fraudia-api --region us-central1 --limit 50
```

## Frontend Configuration

Update frontend `.env` to point to deployed API:

```
VITE_API_URL=https://fraudia-api-XXXXX.a.run.app
```

## Performance Optimization

- **Memory**: 2Gi (2GB) recommended
- **CPU**: 2 CPUs for better performance
- **Instances**: 5-10 min, 50-100 max
- **Timeout**: 60 seconds
- **Concurrency**: Default (80)

## Monitoring

- Cloud Run Dashboard: https://console.cloud.google.com/run
- Logs: Cloud Logging
- Metrics: Cloud Monitoring
- Error rates: Real-time alerts

## Cost Optimization

- Use Cloud CDN for static assets
- Enable vertical Pod autoscaling
- Set appropriate max instances
- Use Cloud Armor for DDoS protection

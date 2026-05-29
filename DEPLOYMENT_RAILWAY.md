# Railway Deployment Guide - FraudIA

## Prerequisites

- GitHub account with code pushed
- Railway account (free at https://railway.app)
- Supabase credentials (URL and API key)

## Quick Deploy (Recommended)

### Step 1: Connect GitHub to Railway

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access your GitHub
5. Select `fraudia-claims` repository
6. Select branch `main`

### Step 2: Set Environment Variables

In Railway dashboard:

1. Go to "Variables" tab
2. Add these environment variables:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
PORT=8000
```

### Step 3: Configure Service

1. Click "Settings"
2. Set:
   - **Root Directory**: (leave empty)
   - **Build Command**: (leave empty - auto-detected)
   - **Start Command**: `uvicorn src.app.main:app --host 0.0.0.0 --port 8000`

### Step 4: Deploy

1. Click "Deploy" button
2. Wait for deployment to complete
3. View logs in "Deployment" tab
4. Get public URL from "Networking" tab

---

## Local Testing Before Deploy

```bash
# Build Docker image
docker build -t fraudia-api:latest .

# Test locally
docker run -p 8000:8000 \
  -e SUPABASE_URL="https://your-project.supabase.co" \
  -e SUPABASE_KEY="your-key" \
  fraudia-api:latest

# Test endpoint
curl http://localhost:8000/
```

---

## Verification

### Check Service Status

```bash
# From Railway dashboard
1. Go to Deployments
2. Click latest deployment
3. View logs for errors
4. Check Health indicator (green = good)
```

### Test API Endpoints

```bash
# Replace YOUR_URL with the public URL from Railway
curl https://YOUR_URL/

curl https://YOUR_URL/resumen

curl https://YOUR_URL/casos?nivel=ROJO&limit=5
```

### Monitor Logs

In Railway dashboard:
- Real-time logs in "Deployments" tab
- Filter by log level (info, error, warning)
- Search by keyword

---

## Update Frontend Configuration

Edit `frontend/.env`:

```
VITE_API_URL=https://YOUR_RAILWAY_URL
```

Then rebuild and redeploy frontend.

---

## Common Issues

### Build fails with "Module not found"

```
Solution:
1. Check requirements.txt is in root directory
2. Ensure all dependencies are listed
3. Check Python version matches (3.12)
```

### Deployment succeeds but API returns 500

```
Solution:
1. Check environment variables are set
2. Verify Supabase credentials are correct
3. Check logs for specific error messages
4. Test locally first with same env vars
```

### Cannot connect from frontend

```
Solution:
1. Verify CORS is enabled in main.py (it is by default)
2. Check frontend has correct API_BASE URL
3. Test API directly: curl https://YOUR_URL/
4. Check browser console for CORS errors
```

### Service goes to sleep (free tier)

```
Railway free tier may put inactive services to sleep.
Solution: Use a monitoring service to ping the API periodically
Example: Use UptimeRobot (free tier) to ping every 5 minutes
```

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | https://abc.supabase.co |
| `SUPABASE_KEY` | Supabase anonymous key | eyJ... |
| `PORT` | Server port (should be 8000) | 8000 |

---

## Performance Settings

Railway automatically scales based on usage:
- **Memory**: 512MB (free tier) - 8GB+ (paid)
- **CPU**: Shared (free) - Dedicated (paid)
- **Regions**: us-west, eu-west (free tier)

For production, consider upgrading to:
- Dedicated CPU
- More memory (2GB+)
- Auto-scaling

---

## Costs

- **Free tier**: Perfect for demo and hackathon
- **Pay-as-you-go**: $0.50/hour for running services
- **No cold start charges**: Unlike some platforms

---

## Redeploy Updates

When you push changes to GitHub:

1. Railway automatically detects new commits
2. Starts build process
3. Deploys new version automatically
4. Old version rolls back on failure

View deployments:
- Railway Dashboard → Deployments
- See all versions and rollback if needed

---

## Scale to Production

When ready to scale:

1. Upgrade Railway plan (paid)
2. Set environment: `ENVIRONMENT=production`
3. Enable auto-scaling:
   - Min instances: 2
   - Max instances: 10
4. Add database connection pooling
5. Enable monitoring and alerts

---

## Custom Domain (Optional)

1. In Railway: Settings → Networking
2. Add custom domain
3. Point DNS CNAME to Railway endpoint
4. SSL automatically configured

Example: api.fraudia.com → Your Railway service

---

## Monitoring & Alerts

Set up notifications:

1. Railway Dashboard → Alerts
2. Configure email alerts for:
   - Failed deployments
   - High CPU/Memory usage
   - Service crashes

---

## Support & Troubleshooting

- Railway Docs: https://docs.railway.app
- Discord Community: https://discord.gg/railway
- Status Page: https://status.railway.app

For this project:
- GitHub Issues: https://github.com/Mildreth-SC/fraudia-claims/issues

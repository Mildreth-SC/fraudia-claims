#!/bin/bash
# FraudIA Cloud Run Deployment Script
# Automates the deployment process to Google Cloud Run

set -e

echo "=================================="
echo "FraudIA Cloud Run Deployment"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "\n${YELLOW}Checking prerequisites...${NC}"

if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}ERROR: gcloud CLI not found. Install it from: https://cloud.google.com/sdk/docs/install${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}ERROR: Docker not found. Install it from: https://www.docker.com/products/docker-desktop${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites satisfied${NC}"

# Get project ID
read -p "Enter your Google Cloud Project ID: " PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}ERROR: Project ID cannot be empty${NC}"
    exit 1
fi

# Set gcloud configuration
echo -e "\n${YELLOW}Configuring gcloud...${NC}"
gcloud config set project $PROJECT_ID
gcloud auth application-default login

# Get Supabase credentials
echo -e "\n${YELLOW}Setting up environment variables...${NC}"
read -p "Enter Supabase URL (https://your-project.supabase.co): " SUPABASE_URL
read -sp "Enter Supabase API Key: " SUPABASE_KEY
echo

if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    echo -e "${YELLOW}Warning: Supabase credentials not provided. You can set them after deployment.${NC}"
fi

# Build Docker image locally (optional)
read -p "Build Docker image locally first? (y/n): " -n 1 -r BUILD_LOCAL
echo
if [[ $BUILD_LOCAL =~ ^[Yy]$ ]]; then
    echo -e "\n${YELLOW}Building Docker image...${NC}"
    docker build -t fraudia-api:latest .
    echo -e "${GREEN}✓ Docker image built${NC}"
fi

# Deploy to Cloud Run
echo -e "\n${YELLOW}Deploying to Cloud Run...${NC}"

SERVICE_NAME="fraudia-api"
REGION="us-central1"

DEPLOY_CMD="gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 60 \
  --max-instances 100"

if [ ! -z "$SUPABASE_URL" ] && [ ! -z "$SUPABASE_KEY" ]; then
    DEPLOY_CMD="$DEPLOY_CMD \
  --set-env-vars SUPABASE_URL=$SUPABASE_URL \
  --set-env-vars SUPABASE_KEY=$SUPABASE_KEY"
fi

eval $DEPLOY_CMD

echo -e "${GREEN}✓ Deployment initiated${NC}"

# Get service URL
echo -e "\n${YELLOW}Retrieving service URL...${NC}"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')

echo -e "\n${GREEN}=================================="
echo "Deployment Successful!"
echo "===================================${NC}"
echo -e "Service: ${GREEN}$SERVICE_NAME${NC}"
echo -e "Region: ${GREEN}$REGION${NC}"
echo -e "URL: ${GREEN}$SERVICE_URL${NC}"

# Test the endpoint
echo -e "\n${YELLOW}Testing endpoint...${NC}"
curl -s "$SERVICE_URL/" | head -1
echo

# Update frontend configuration
read -p "Update frontend .env with API URL? (y/n): " -n 1 -r UPDATE_FRONTEND
echo
if [[ $UPDATE_FRONTEND =~ ^[Yy]$ ]]; then
    if [ -f "frontend/.env" ]; then
        sed -i "s|VITE_API_URL=.*|VITE_API_URL=$SERVICE_URL|" frontend/.env
        echo -e "${GREEN}✓ Frontend .env updated${NC}"
    else
        echo "VITE_API_URL=$SERVICE_URL" > frontend/.env
        echo -e "${GREEN}✓ Created frontend/.env${NC}"
    fi
fi

# View logs
read -p "View deployment logs? (y/n): " -n 1 -r VIEW_LOGS
echo
if [[ $VIEW_LOGS =~ ^[Yy]$ ]]; then
    gcloud run logs read $SERVICE_NAME --region $REGION --limit 50
fi

echo -e "\n${GREEN}Deployment Complete!${NC}"
echo -e "Next steps:"
echo -e "1. Set environment variables if not done during deployment"
echo -e "2. Monitor logs: ${YELLOW}gcloud run logs read $SERVICE_NAME --region $REGION${NC}"
echo -e "3. Test the API: ${YELLOW}curl $SERVICE_URL/${NC}"
echo -e "4. Update frontend with API URL: ${YELLOW}$SERVICE_URL${NC}"

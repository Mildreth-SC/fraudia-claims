#!/bin/bash
# FraudIA Railway Deployment Script
# Automates the deployment to Railway platform

set -e

echo "=================================="
echo "FraudIA Railway Deployment"
echo "=================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check prerequisites
echo -e "\n${YELLOW}Checking prerequisites...${NC}"

if ! command -v git &> /dev/null; then
    echo -e "${RED}ERROR: Git not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Git found${NC}"

# Push to GitHub
echo -e "\n${YELLOW}Preparing repository...${NC}"
read -p "Have you created a GitHub repository? (y/n): " -n 1 -r GITHUB_READY
echo

if [[ ! $GITHUB_READY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Please create a GitHub repository first and push your code${NC}"
    echo "Then run this script again."
    exit 0
fi

read -p "Commit message (default: 'Deploy FraudIA to Railway'): " COMMIT_MSG
COMMIT_MSG=${COMMIT_MSG:-"Deploy FraudIA to Railway"}

git add -A
git commit -m "$COMMIT_MSG" || echo "No changes to commit"
git push origin main || git push origin master

echo -e "${GREEN}✓ Code pushed to GitHub${NC}"

# Get Supabase credentials
echo -e "\n${YELLOW}Setting up environment variables...${NC}"
read -p "Supabase URL (https://your-project.supabase.co): " SUPABASE_URL
read -sp "Supabase API Key: " SUPABASE_KEY
echo

if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    echo -e "${RED}ERROR: Supabase credentials required${NC}"
    exit 1
fi

# Instructions for Railway
echo -e "\n${GREEN}=================================="
echo "Railway Deployment Instructions"
echo "==================================${NC}"
echo
echo "1. Go to https://railway.app"
echo "2. Sign in with GitHub"
echo "3. Click 'New Project' → 'Deploy from GitHub repo'"
echo "4. Select your 'fraudia-claims' repository"
echo "5. Railway will auto-detect settings"
echo "6. Add these environment variables:"
echo -e "   ${YELLOW}SUPABASE_URL=$SUPABASE_URL${NC}"
echo -e "   ${YELLOW}SUPABASE_KEY=$SUPABASE_KEY${NC}"
echo "7. Click 'Deploy'"
echo "8. Wait for deployment to complete"
echo "9. Copy public URL from 'Networking' tab"
echo "10. Update frontend VITE_API_URL"
echo
echo -e "${GREEN}Note: Railway auto-redeploys on git push to main${NC}"
echo

read -p "Open Railway in browser? (y/n): " -n 1 -r OPEN_BROWSER
echo
if [[ $OPEN_BROWSER =~ ^[Yy]$ ]]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open https://railway.app/dashboard
    elif command -v open &> /dev/null; then
        open https://railway.app/dashboard
    else
        echo "Please visit: https://railway.app/dashboard"
    fi
fi

echo -e "\n${GREEN}Deployment setup complete!${NC}"

# Deployment Guide (No Docker)

## GitHub Actions + Railway Setup

### 1. Set up Railway
1. Go to [railway.app](https://railway.app) and sign up/login
2. Connect your GitHub repository
3. Create a new project from your repo
4. Add a new service → "Empty Service"
5. Configure the service:
   - **Build Command**: `cd api && pip install -r requirements.txt`
   - **Start Command**: `cd api && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.9

### 2. Configure Environment Variables
In Railway dashboard, add:
- `MODEL_RUN_PATH` = `captcha-solver/Results/202509041853`
- `PORT` = `8000` (Railway sets this automatically)

### 3. Set up GitHub Secrets
In your GitHub repo → Settings → Secrets and variables → Actions, add:
- `RAILWAY_TOKEN`: Get from Railway → Account Settings → Tokens
- `RAILWAY_SERVICE_ID`: Found in your Railway service settings

### 4. Push to Deploy
```bash
git add .
git commit -m "Add deployment workflow"
git push origin main
```

### 5. Get your API URL
After deployment, Railway gives you a URL like:
`https://your-project-production.up.railway.app`

### 6. Update Frontend
In your Vercel deployment, set:
- `NEXT_PUBLIC_API_BASE` = `https://your-railway-url.up.railway.app`

## Alternative: Render (Python)
1. Go to [render.com](https://render.com)
2. Create "Web Service" → "Build and deploy from a Git repository"
3. Connect your GitHub repo
4. Settings:
   - **Build Command**: `cd api && pip install -r requirements.txt`
   - **Start Command**: `cd api && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.9

## Alternative: Heroku
```bash
# Install Heroku CLI, then:
heroku create your-app-name
heroku config:set MODEL_RUN_PATH=captcha-solver/Results/202509041853
git push heroku main
```

## Testing
After deployment, test:
```bash
curl https://your-api-url.up.railway.app/health
curl -F "file=@test.png" https://your-api-url.up.railway.app/api/predict
```

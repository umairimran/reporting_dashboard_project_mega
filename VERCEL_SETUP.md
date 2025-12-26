# Frontend on Vercel + Backend on Docker

## 🎯 Setup Overview

Your setup:
- ✅ **Frontend**: Deployed on Vercel
- ✅ **Backend + Database**: Running in Docker (local)

## 🚀 Step 1: Start Backend (Docker)

Run Docker to start backend API and database:

```bash
start-docker.bat          # Windows
./start-docker.sh         # Mac/Linux
docker-compose up --build # Manual
```

This starts:
- PostgreSQL database on port 5432
- Backend API on http://localhost:8000

## 🔗 Step 2: Update Vercel Frontend

Your Vercel frontend needs to connect to your local backend.

### Option A: Expose Backend Publicly (Recommended for Production)

Use a service like:
- **ngrok**: https://ngrok.com/
- **Cloudflare Tunnel**: https://www.cloudflare.com/products/tunnel/
- **Deploy backend to a server** (Railway, Render, DigitalOcean, etc.)

Example with ngrok:
```bash
# Install ngrok
# Then expose your local backend:
ngrok http 8000
```

You'll get a URL like: `https://abc123.ngrok.io`

Update your Vercel environment variable:
```
NEXT_PUBLIC_API_URL=https://abc123.ngrok.io/api/v1
```

### Option B: Use for Local Development Only

If testing locally:
1. Run backend: `start-docker.bat`
2. Run frontend locally: `cd client && npm run dev`
3. Access at: http://localhost:3000

## 🔧 Step 3: Update CORS in docker-compose.yml

Open `docker-compose.yml` and update the CORS line with your Vercel URL:

```yaml
CORS_ORIGINS: '["http://localhost:3000","https://your-actual-vercel-url.vercel.app"]'
```

Replace `your-actual-vercel-url.vercel.app` with your real Vercel URL!

## 🔐 Step 4: Update Vercel Environment Variables

In your Vercel project dashboard:

1. Go to **Settings** → **Environment Variables**
2. Add/Update:

```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
# Or your ngrok/public URL:
# NEXT_PUBLIC_API_URL=https://your-backend-url.ngrok.io/api/v1
```

3. Redeploy your Vercel app

## ✅ Testing the Connection

1. Start backend: `start-docker.bat`
2. Check backend is running: http://localhost:8000/docs
3. Open Vercel frontend
4. Try to login with:
   - Email: admin@gmail.com
   - Password: admin123

## 🌐 Production Deployment Options

For production, deploy your backend to:

### Railway (Easiest)
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Render
1. Connect GitHub repo
2. Select "Web Service"
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### DigitalOcean App Platform
1. Connect GitHub repo
2. Auto-detect Dockerfile
3. Deploy!

### Fly.io
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy
```

## 📝 Environment Variables Needed on Backend Host

When deploying backend to production, set these:

```
DATABASE_URL=postgresql://user:pass@host:5432/db
SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-encryption-key
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
SMTP_HOST=smtp.gmail.com
SMTP_USERNAME=umairimran6277@gmail.com
SMTP_PASSWORD=jtawalawmbrppzss
```

## 🎉 Summary

**Current Setup:**
- Frontend: Vercel ✅
- Backend: Docker (local) ✅
- Database: Docker (local) ✅

**For Production:**
- Frontend: Vercel ✅
- Backend: Deploy to Railway/Render/DigitalOcean ⏳
- Database: Use managed PostgreSQL (Supabase/Railway/Neon) ⏳

**Quick Commands:**
- Start backend: `start-docker.bat`
- Stop backend: `stop-docker.bat`
- Backend API: http://localhost:8000
- Backend Docs: http://localhost:8000/docs




# Configuration Guide - Single Point URLs

## 🎯 All Configuration in ONE Place: `.env` File

### Location of .env Files:

```
server/.env          ← Backend configuration (MAIN FILE)
client/.env.local    ← Frontend configuration (for Vercel)
docker-compose.yml   ← Docker environment variables
```

---

## 📝 Backend Configuration (server/.env)

### Required Settings:

```bash
# =============================================================================
# SINGLE POINT CONFIGURATION - UPDATE THESE URLs
# =============================================================================

# Database
DATABASE_URL=postgresql://postgres:03025202775Abc$@localhost:5432/megaDB

# CORS - Frontend URLs that can access the backend
CORS_ORIGINS=["http://localhost:3000","https://your-vercel-app.vercel.app"]

# Security Keys
SECRET_KEY=your-secret-key-change-this-in-production-32-chars-minimum
ENCRYPTION_KEY=44p68_kzgH3OfCQsovZOFnk8PJGAuwS7V4kvkaCo7nY=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# AWS S3 (for Surfside)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-surfside-bucket

# Vibe API
VIBE_API_BASE_URL=https://clear-platform.vibe.co
VIBE_API_KEY=your_vibe_api_key_here
VIBE_RATE_LIMIT_PER_HOUR=15

# Email/SMTP (for alerts)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=umairimran6277@gmail.com
SMTP_PASSWORD=jtawalawmbrppzss
SMTP_FROM_EMAIL=umairimran6277@gmail.com
SMTP_FROM_NAME=Dashboard Alerts

# File Upload
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE=52428800

# Scheduler
SURFSIDE_CRON_HOUR=5
VIBE_CRON_HOUR=5
ENABLE_SCHEDULER=True

# Debug
DEBUG=False
```

---

## 🌐 Frontend Configuration (Vercel)

### Environment Variable in Vercel Dashboard:

```
Name:  NEXT_PUBLIC_API_URL
Value: http://YOUR_SERVER_IP:8000/api/v1
```

**Example:**
```
NEXT_PUBLIC_API_URL=http://54.123.45.67:8000/api/v1
```

Or for production with domain:
```
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1
```

---

## 🔧 How to Update URLs

### To Change Backend URL (for frontend to connect):

**Option 1: Vercel Dashboard**
1. Go to https://vercel.com/dashboard
2. Select your project
3. Settings → Environment Variables
4. Update `NEXT_PUBLIC_API_URL`
5. Redeploy

**Option 2: Local Development**
Create `client/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### To Change Allowed Frontend URLs (CORS):

**Edit `server/.env`:**
```bash
CORS_ORIGINS=["http://localhost:3000","https://your-new-frontend.vercel.app"]
```

**Or in `docker-compose.yml`:**
```yaml
environment:
  CORS_ORIGINS: '["http://localhost:3000","https://your-frontend.vercel.app"]'
```

---

## 📍 Configuration File Locations

### Backend:
- **Main config file:** `server/app/core/config.py`
  - Reads from: `server/.env`
  - All settings defined here

### Frontend:
- **Main API client:** `client/lib/api-client.ts`
  - Line 5: `const API_Base_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"`
  - Reads from: `NEXT_PUBLIC_API_URL` environment variable

### CORS:
- **Backend main:** `server/app/main.py`
  - Line 85-92: Uses `settings.cors_origins_list` from config
  - No hardcoded URLs anymore!

---

## ✅ Verification

### Check Backend is using .env:
```bash
# On server
cd ~/reporting_dashboard_project_mega/server
python -c "from app.core.config import settings; print('CORS:', settings.cors_origins_list)"
```

### Check Frontend is using env var:
```bash
# In Vercel deployment logs
# You should see: NEXT_PUBLIC_API_URL=your-backend-url
```

---

## 🚀 Quick Setup Steps

### For New Deployment:

1. **Update server/.env:**
   ```bash
   CORS_ORIGINS=["http://localhost:3000","https://your-vercel-app.vercel.app"]
   ```

2. **Update Vercel Environment Variable:**
   ```
   NEXT_PUBLIC_API_URL=http://your-server-ip:8000/api/v1
   ```

3. **Restart Backend:**
   ```bash
   docker compose down
   docker compose up -d
   ```

4. **Redeploy Frontend:**
   - Go to Vercel dashboard
   - Click "Redeploy"

---

## 🔒 Security Notes

1. **Never commit `.env` files to Git** (already in .gitignore)
2. **Change SECRET_KEY and ENCRYPTION_KEY in production**
3. **Use HTTPS in production** (https:// not http://)
4. **Restrict CORS_ORIGINS** to only your domains in production

---

## 📦 Summary

**Single Configuration Points:**

| What | Where to Change | File/Location |
|------|----------------|---------------|
| Backend URL | Vercel Environment Variables | `NEXT_PUBLIC_API_URL` |
| Frontend URLs (CORS) | `server/.env` | `CORS_ORIGINS` |
| Database URL | `server/.env` | `DATABASE_URL` |
| Email Settings | `server/.env` | `SMTP_*` |
| AWS Settings | `server/.env` | `AWS_*` |

**No more hardcoded URLs anywhere in the code!** ✅


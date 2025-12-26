# Environment Setup Guide

## ⚠️ IMPORTANT: No Default URLs!

**All URLs MUST be configured in environment files. The application will NOT start without proper configuration.**

---

## 🔧 Backend Setup (server/.env)

### 1. Copy the example file:
```bash
cd server
cp .env.example .env
```

### 2. Edit `.env` and update these REQUIRED fields:

```bash
# CORS - Frontend URLs (REQUIRED!)
CORS_ORIGINS=["https://your-actual-vercel-app.vercel.app","http://localhost:3000"]

# Database (REQUIRED!)
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/megaDB

# Security Keys (REQUIRED!)
SECRET_KEY=your-secret-key-32-chars-minimum
ENCRYPTION_KEY=your-encryption-key

# AWS (REQUIRED!)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret

# Email (REQUIRED!)
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

## 🌐 Frontend Setup (Vercel)

### For Vercel Deployment:

1. Go to Vercel Dashboard
2. Select your project
3. Settings → Environment Variables
4. Add this **REQUIRED** variable:

```
Name:  NEXT_PUBLIC_API_URL
Value: http://YOUR_SERVER_IP:8000/api/v1
```

**Example:**
```
NEXT_PUBLIC_API_URL=http://54.123.45.67:8000/api/v1
```

### For Local Development:

Create `client/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 🐳 Docker Setup (docker-compose.yml)

Update the `CORS_ORIGINS` in `docker-compose.yml`:

```yaml
environment:
  CORS_ORIGINS: '["https://your-vercel-app.vercel.app"]'
```

---

## ✅ Validation

### Backend will fail to start if:
- `CORS_ORIGINS` is not set in `.env`
- `CORS_ORIGINS` is invalid JSON
- Required AWS/SMTP credentials are missing

### Frontend will fail to build if:
- `NEXT_PUBLIC_API_URL` is not set

**This is intentional! No defaults = No accidents in production.**

---

## 🚀 Quick Start

### 1. Backend:
```bash
cd server
cp .env.example .env
# Edit .env with your values
python -m app.main
```

### 2. Frontend (Local):
```bash
cd client
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
npm run dev
```

### 3. Docker:
```bash
# Update docker-compose.yml CORS_ORIGINS first!
docker compose up --build
```

---

## 📝 Required Environment Variables Summary

### Backend (server/.env):
- ✅ `CORS_ORIGINS` - Frontend URLs
- ✅ `DATABASE_URL` - Database connection
- ✅ `SECRET_KEY` - JWT secret
- ✅ `ENCRYPTION_KEY` - Data encryption
- ✅ `AWS_*` - S3 credentials
- ✅ `SMTP_*` - Email credentials

### Frontend (Vercel / .env.local):
- ✅ `NEXT_PUBLIC_API_URL` - Backend API URL

### Docker (docker-compose.yml):
- ✅ `CORS_ORIGINS` - Frontend URLs
- ✅ All backend variables

---

## ❌ What Happens Without Configuration?

**Backend:**
```
ValueError: CORS_ORIGINS must be set in .env file as valid JSON array
```

**Frontend:**
```
Error: NEXT_PUBLIC_API_URL environment variable is required!
```

**This forces proper configuration and prevents accidental deployments!**


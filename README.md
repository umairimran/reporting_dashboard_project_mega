# Paid Media Reporting Dashboard

Complete dashboard for managing and analyzing paid media performance data from multiple sources (Surfside, Vibe, Facebook).

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed
- Git installed
- Vercel account (for frontend)

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd reporting_dashboard_project_mega
```

### 2. Configure Environment Variables

#### Backend Configuration (server/.env)
```bash
# Database
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/megaDB

# CORS - Frontend URLs (REQUIRED!)
CORS_ORIGINS=["https://your-vercel-app.vercel.app"]

# Security
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
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Dashboard Alerts

# File Upload
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE=52428800

# Scheduler
SURFSIDE_CRON_HOUR=5
VIBE_CRON_HOUR=5
ENABLE_SCHEDULER=True
```

#### Frontend Configuration (Vercel)
1. Go to Vercel Dashboard
2. Select your project
3. Settings → Environment Variables
4. Add:
```
NEXT_PUBLIC_API_URL=http://YOUR_SERVER_IP:8000/api/v1
```

#### Docker Configuration (docker-compose.yml)
Update line 66 with your Vercel URL:
```yaml
CORS_ORIGINS: '["https://your-vercel-app.vercel.app"]'
```

### 3. Start with Docker

#### Windows:
```bash
start-docker.bat
```

#### Mac/Linux:
```bash
chmod +x start-docker.sh
./start-docker.sh
```

#### Or manually:
```bash
docker compose up --build
```

### 4. Access the Application

- **Frontend**: https://your-vercel-app.vercel.app
- **Backend API**: http://YOUR_SERVER_IP:8000
- **API Docs**: http://YOUR_SERVER_IP:8000/docs

### 5. Login

Default admin credentials:
- **Email**: admin@gmail.com
- **Password**: admin123

---

## 📁 Project Structure

```
reporting_dashboard_project_mega/
├── client/                    # Next.js Frontend
│   ├── app/                   # App router pages
│   ├── components/            # React components
│   ├── lib/                   # API client & services
│   └── types/                 # TypeScript types
├── server/                    # FastAPI Backend
│   ├── app/                   # Application code
│   │   ├── auth/              # Authentication
│   │   ├── clients/           # Client management
│   │   ├── campaigns/         # Campaign hierarchy
│   │   ├── metrics/           # Metrics & aggregation
│   │   ├── dashboard/         # Dashboard endpoints
│   │   ├── exports/           # CSV/PDF exports
│   │   ├── facebook/          # Facebook integration
│   │   ├── surfside/          # Surfside S3 integration
│   │   ├── vibe/              # Vibe API integration
│   │   ├── etl/               # ETL pipeline
│   │   └── core/              # Configuration & database
│   ├── database_schema.sql    # Database schema
│   ├── Dockerfile             # Backend Docker config
│   └── requirements.txt       # Python dependencies
├── docker-compose.yml         # Docker orchestration
├── start-docker.bat           # Windows start script
├── start-docker.sh            # Linux/Mac start script
└── README.md                  # This file
```

---

## 🔧 Configuration Details

### Single Configuration Points

All URLs are configured in ONE place each:

| Setting | Location | Variable |
|---------|----------|----------|
| Backend URL | Vercel Environment Variables | `NEXT_PUBLIC_API_URL` |
| Frontend URLs (CORS) | `server/.env` or `docker-compose.yml` | `CORS_ORIGINS` |
| Database | `server/.env` | `DATABASE_URL` |
| AWS Credentials | `server/.env` | `AWS_*` |
| Email Settings | `server/.env` | `SMTP_*` |

### No Hardcoded URLs

The application will **fail to start** if environment variables are not set. This prevents accidental deployments with wrong configurations.

---

## 🐳 Docker Setup

### What Docker Does

1. Creates PostgreSQL database (megaDB)
2. Runs database_schema.sql (creates all tables)
3. Creates admin user (admin@gmail.com / admin123)
4. Starts Backend API on port 8000
5. All data persists in Docker volumes

### Docker Commands

```bash
# Start everything
docker compose up --build

# Start in background
docker compose up -d

# Stop everything
docker compose down

# Stop and remove all data
docker compose down -v

# View logs
docker compose logs -f

# Restart backend only
docker compose restart backend
```

### Docker Volumes

Data is stored in Docker volumes:
- `postgres_data` - Database data
- `backend_uploads` - Uploaded files

Data survives container restarts!

---

## 🌐 Deployment

### Backend Deployment (Ubuntu Server)

1. **Install Docker:**
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
```

2. **Clone and Configure:**
```bash
git clone <your-repo>
cd reporting_dashboard_project_mega
# Update docker-compose.yml with your Vercel URL
```

3. **Open Firewall Ports:**
```bash
sudo ufw allow 8000
sudo ufw allow 5432
```

4. **Start Docker:**
```bash
docker compose up -d
```

5. **Get Server IP:**
```bash
curl ifconfig.me
```

### Frontend Deployment (Vercel)

1. **Connect GitHub repo to Vercel**
2. **Set Environment Variable:**
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `http://YOUR_SERVER_IP:8000/api/v1`
3. **Deploy**

### AWS Security Group (if using EC2)

Add inbound rules:
- Port 8000 (Backend API) - Source: 0.0.0.0/0
- Port 5432 (PostgreSQL) - Source: Your VPC only

---

## 📊 Data Sources

### 1. Surfside (S3)
- Automated daily ingestion from S3 bucket
- Configure AWS credentials in `.env`
- Scheduled at 5:00 AM daily

### 2. Vibe (API)
- Direct API integration
- Configure API key in `.env`
- Rate limited to 15 requests/hour

### 3. Facebook (Upload)
- Manual CSV/Excel upload
- Upload via dashboard UI
- Supports ad-level data with regions

---

## 🔑 Admin User

### Default Credentials
- Email: admin@gmail.com
- Password: admin123

### Creating Additional Users
1. Login as admin
2. Go to Admin → Clients
3. Click "Add Client"
4. Fill in details (creates client + user)

### Changing Admin Password
```bash
# On server
docker exec -it reporting_backend python
>>> from app.auth.security import get_password_hash
>>> print(get_password_hash("new_password"))
>>> exit()

# Update in database
docker exec -it reporting_db psql -U postgres -d megaDB
UPDATE users SET password_hash='<hash_from_above>' WHERE email='admin@gmail.com';
\q
```

---

## 🛠️ Development

### Local Development (Without Docker)

#### Backend:
```bash
cd server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup database
psql -U postgres -d megaDB -f database_schema.sql

# Create .env file with local settings
# Start server
uvicorn app.main:app --reload
```

#### Frontend:
```bash
cd client
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

# Start dev server
npm run dev
```

---

## 📝 API Documentation

Once backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔍 Troubleshooting

### Backend won't start
```bash
# Check logs
docker compose logs backend

# Common issues:
# 1. Port 8000 already in use
sudo lsof -i :8000

# 2. Database not ready
docker compose restart db
docker compose restart backend

# 3. Environment variables not set
cat docker-compose.yml | grep CORS_ORIGINS
```

### Frontend can't connect to backend
```bash
# 1. Check backend is running
curl http://YOUR_SERVER_IP:8000/docs

# 2. Check CORS settings
# Backend .env should have your Vercel URL in CORS_ORIGINS

# 3. Check Vercel environment variable
# Should have NEXT_PUBLIC_API_URL set
```

### Database connection issues
```bash
# Check database is running
docker exec -it reporting_db pg_isready -U postgres

# Connect to database
docker exec -it reporting_db psql -U postgres -d megaDB

# Check tables exist
\dt
```

### Admin user creation failed
```bash
# Check error
docker compose logs backend | grep admin

# Common issue: Column name mismatch
# Make sure you have latest code:
git pull
docker compose down
docker compose up --build
```

---

## 🔧 Troubleshooting

### Backend Not Starting / "Failed to fetch /openapi.json"

If you see this error when accessing `http://YOUR_SERVER:8000/docs`:

**Symptoms:**
- FastAPI docs page shows "Failed to load API definition"
- "Failed to fetch /openapi.json" error
- Backend container starts but crashes silently

**Solution:**

1. **Check backend logs:**
   ```bash
   docker compose logs backend --tail 100
   ```

2. **Common causes:**
   - **CORS_ORIGINS not set**: Ensure `docker-compose.yml` line 66 has:
     ```yaml
     CORS_ORIGINS: '["https://your-vercel-app.vercel.app","http://localhost:3000"]'
     ```
   - **Invalid JSON format**: CORS_ORIGINS must be valid JSON array string
   - **Missing environment variables**: Check all required vars in `docker-compose.yml`

3. **Rebuild containers:**
   ```bash
   docker compose down
   docker compose up --build
   ```

### Port Already in Use (5432)

If you see "address already in use" for port 5432:

**Solution:**
```bash
# Stop system PostgreSQL
sudo systemctl stop postgresql
sudo systemctl disable postgresql  # Prevent auto-start

# Then restart Docker
docker compose up --build
```

### Admin User Creation Failed

If you see "column 'hashed_password' does not exist":

**Solution:**
- This has been fixed in `server/create_admin_docker.py`
- Pull latest code: `git pull`
- Rebuild: `docker compose up --build`

### Frontend Can't Connect to Backend

If Vercel frontend shows connection errors:

**Solution:**

1. **Check CORS in docker-compose.yml:**
   ```yaml
   CORS_ORIGINS: '["https://your-actual-vercel-url.vercel.app"]'
   ```

2. **Update Vercel environment variable:**
   - Go to Vercel → Project Settings → Environment Variables
   - Set `NEXT_PUBLIC_API_URL=http://YOUR_EC2_IP:8000/api/v1`
   - Redeploy frontend

3. **Check EC2 Security Group:**
   - Port 8000 must be open to 0.0.0.0/0 (or your IP)
   - AWS Console → EC2 → Security Groups → Inbound Rules

### Database Connection Failed

If you see database connection errors:

**Solution:**

1. **Check DATABASE_URL in docker-compose.yml:**
   ```yaml
   DATABASE_URL: postgresql://postgres:YOUR_PASSWORD@db:5432/megaDB
   ```

2. **Verify database is running:**
   ```bash
   docker compose ps  # db should show "Up"
   docker compose logs db --tail 50
   ```

3. **Reset database:**
   ```bash
   docker compose down -v  # WARNING: Deletes all data!
   docker compose up --build
   ```

---

## 📦 Tech Stack

### Frontend
- Next.js 16
- React 19
- TypeScript
- TailwindCSS
- Shadcn/ui
- React Query
- Recharts

### Backend
- Python 3.11
- FastAPI
- SQLAlchemy
- PostgreSQL 15
- Pandas
- ReportLab (PDF)
- APScheduler

### Infrastructure
- Docker & Docker Compose
- Vercel (Frontend)
- AWS S3 (Surfside data)

---

## 🔒 Security

- JWT authentication with HTTP-only cookies
- Password hashing with bcrypt
- Encrypted storage for sensitive data (API keys)
- CORS protection
- SQL injection prevention (SQLAlchemy ORM)
- Input validation (Pydantic)

---

## 📄 License

Proprietary - All rights reserved

---

## 👥 Support

For issues or questions, contact the development team.

---

## 🎯 Quick Reference

### Start Application
```bash
docker compose up -d
```

### Stop Application
```bash
docker compose down
```

### View Logs
```bash
docker compose logs -f
```

### Update Code
```bash
git pull
docker compose down
docker compose up --build
```

### Backup Database
```bash
docker exec reporting_db pg_dump -U postgres megaDB > backup.sql
```

### Restore Database
```bash
cat backup.sql | docker exec -i reporting_db psql -U postgres -d megaDB
```

---

**That's it! Your dashboard should now be running.** 🎉

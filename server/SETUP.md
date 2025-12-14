# Backend Setup Guide - FastAPI + PostgreSQL

This guide will help you set up the development environment for the Dashboard Application backend.

---

## Prerequisites

Ensure you have the following installed:

- **Python 3.10+** (Check: `python --version`)
- **PostgreSQL 14+** (Check: `psql --version`)
- **pgAdmin 4** (for database management)
- **Git** (for version control)
- **pip** (Python package manager)

---

## Step 1: PostgreSQL Database Setup

### 1.1 Create a New Server in pgAdmin 4

1. **Open pgAdmin 4**
2. **Right-click on "Servers"** → Select **"Register" → "Server..."**
3. **In the "General" tab:**
   - **Name:** `Dashboard_Dev_Server`
4. **In the "Connection" tab:**
   - **Host name/address:** `localhost`
   - **Port:** `5432` (default)
   - **Maintenance database:** `postgres`
   - **Username:** `postgres`
   - **Password:** `[your_postgres_password]`
   - ✅ Check **"Save password?"**
5. **Click "Save"**

### 1.2 Create Project Database

1. **Expand the "Dashboard_Dev_Server"** in pgAdmin
2. **Right-click on "Databases"** → Select **"Create" → "Database..."**
3. **Database configuration:**
   - **Database name:** `megaDB`
   - **Owner:** `postgres` (or your username)
   - **Encoding:** `UTF8`
   - **Template:** `template0`
4. **Click "Save"**

### 1.3 Create Database User (Optional but Recommended)

For better security, create a dedicated user for the application:

1. **Right-click on "Login/Group Roles"** → **"Create" → "Login/Group Role..."**
2. **In the "General" tab:**
   - **Name:** `megauser`
3. **In the "Definition" tab:**
   - **Password:** `dashboard_password_2025`
4. **In the "Privileges" tab:**
   - ✅ Check **"Can login?"**
5. **Click "Save"**

6. **Grant privileges to the new user:**
   - Right-click on `megaDB` → **"Query Tool"**
   - Run the following SQL:
   ```sql
    GRANT ALL PRIVILEGES ON DATABASE "megaDB" TO megauser;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO megauser;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO megauser;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO megauser;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO megauser;
   ```

### 1.4 Verify Database Connection

1. **Open Query Tool** for `dashboard_db`
2. **Run a test query:**
   ```sql
   SELECT version();
   ```
3. **Expected Result:** PostgreSQL version information displayed

---

## Step 2: Python Virtual Environment Setup

### 2.1 Navigate to Server Directory

```powershell
cd C:\Users\shame\Desktop\mega\server
```

### 2.2 Create Virtual Environment
using python 3.11
```powershell
python -m venv venv
```

### 2.3 Activate Virtual Environment

```powershell
# PowerShell
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

You should see `(venv)` in your terminal prompt.

### 2.4 Upgrade pip

```powershell
python -m pip install --upgrade pip
```

---

## Step 3: Install FastAPI Dependencies

### 3.1 Install Core Packages

```powershell
pip install fastapi[all]
pip install uvicorn[standard]
pip install sqlalchemy
pip install psycopg2-binary
pip install alembic
pip install python-dotenv
pip install pydantic[email]
pip install python-multipart
pip install bcrypt
pip install python-jose[cryptography]
pip install passlib[bcrypt]
```

### 3.2 Install Additional Dependencies

```powershell
# For data processing
pip install pandas
pip install openpyxl

# For AWS S3 integration
pip install boto3

# For API requests (Vibe API)
pip install httpx
pip install requests

# For testing
pip install pytest
pip install pytest-asyncio
pip install httpx

# For code quality
pip install black
pip install flake8
pip install pylint
```

### 3.3 Generate Requirements File

```powershell
pip freeze > requirements.txt
```

---

## Step 4: Project Structure Setup

### 4.1 Create Project Directory Structure

```powershell
# Create directories
New-Item -ItemType Directory -Path "app" -Force
New-Item -ItemType Directory -Path "app/api" -Force
New-Item -ItemType Directory -Path "app/api/v1" -Force
New-Item -ItemType Directory -Path "app/api/v1/endpoints" -Force
New-Item -ItemType Directory -Path "app/core" -Force
New-Item -ItemType Directory -Path "app/db" -Force
New-Item -ItemType Directory -Path "app/models" -Force
New-Item -ItemType Directory -Path "app/schemas" -Force
New-Item -ItemType Directory -Path "app/services" -Force
New-Item -ItemType Directory -Path "app/utils" -Force
New-Item -ItemType Directory -Path "tests" -Force
New-Item -ItemType Directory -Path "alembic" -Force

# Create __init__.py files
New-Item -ItemType File -Path "app/__init__.py" -Force
New-Item -ItemType File -Path "app/api/__init__.py" -Force
New-Item -ItemType File -Path "app/api/v1/__init__.py" -Force
New-Item -ItemType File -Path "app/api/v1/endpoints/__init__.py" -Force
New-Item -ItemType File -Path "app/core/__init__.py" -Force
New-Item -ItemType File -Path "app/db/__init__.py" -Force
New-Item -ItemType File -Path "app/models/__init__.py" -Force
New-Item -ItemType File -Path "app/schemas/__init__.py" -Force
New-Item -ItemType File -Path "app/services/__init__.py" -Force
New-Item -ItemType File -Path "app/utils/__init__.py" -Force
New-Item -ItemType File -Path "tests/__init__.py" -Force
```

**Expected Structure:**

```
server/
├── venv/                          # Virtual environment
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py             # API router
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── auth.py        # Authentication endpoints
│   │           ├── dashboard.py   # Dashboard endpoints
│   │           ├── campaigns.py   # Campaign endpoints
│   │           ├── sync.py        # Data sync endpoints
│   │           └── upload.py      # File upload endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration settings
│   │   └── security.py            # Security utilities
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py                # SQLAlchemy base
│   │   ├── session.py             # Database session
│   │   └── init_db.py             # Database initialization
│   ├── models/
│   │   ├── __init__.py
│   │   ├── campaign.py            # Campaign model
│   │   ├── metric.py              # Metrics model
│   │   ├── user.py                # User model
│   │   └── sync_log.py            # Sync log model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── campaign.py            # Campaign schemas
│   │   ├── metric.py              # Metric schemas
│   │   └── user.py                # User schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── surfside.py            # Surfside integration
│   │   ├── vibe.py                # Vibe API integration
│   │   └── facebook.py            # Facebook upload processing
│   └── utils/
│       ├── __init__.py
│       ├── s3.py                  # S3 utilities
│       └── validators.py          # Data validators
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── alembic/                       # Database migrations
├── .env                           # Environment variables
├── .env.example                   # Example environment variables
├── .gitignore
├── requirements.txt
└── SETUP.md                       # This file
```

---

## Step 5: Environment Configuration

### 5.1 Create `.env` File

Create a `.env` file in the `server` directory:

```powershell
New-Item -ItemType File -Path ".env" -Force
```

### 5.2 Add Environment Variables

Open `.env` and add the following:

```env
# Application Settings
APP_NAME=Dashboard Application
APP_VERSION=1.0.0
DEBUG=True
ENVIRONMENT=development

# Database Configuration
DATABASE_URL=postgresql://dashboard_user:dashboard_password_2025@localhost:5432/dashboard_db
# Alternative if using default postgres user:
# DATABASE_URL=postgresql://postgres:your_password@localhost:5432/dashboard_db

# Security
SECRET_KEY=your-secret-key-change-this-in-production-32-chars-minimum
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS S3 Configuration (for Surfside)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-surfside-bucket

# Vibe API Configuration
VIBE_API_BASE_URL=https://clear-platform.vibe.co/rest/reporting/v1
VIBE_API_KEY=your_vibe_api_key_here
VIBE_RATE_LIMIT_PER_HOUR=15

# File Upload Configuration
MAX_UPLOAD_SIZE_MB=50
ALLOWED_UPLOAD_EXTENSIONS=.csv
UPLOAD_TEMP_DIR=./uploads/temp

# CORS Settings
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### 5.3 Create `.env.example` File

```powershell
Copy-Item .env .env.example
```

Then remove sensitive values from `.env.example` for version control.

### 5.4 Update `.gitignore`

Create or update `.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# Environment variables
.env

# Database
*.db
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Uploads
uploads/

# Testing
.pytest_cache/
.coverage
htmlcov/

# Logs
*.log
```

---

## Step 6: Initialize Alembic for Database Migrations

### 6.1 Initialize Alembic

```powershell
alembic init alembic
```

### 6.2 Configure Alembic

1. **Edit `alembic/env.py`** - Update the SQLAlchemy URL section:

   ```python
   # Add at the top
   from app.core.config import settings
   from app.db.base import Base

   # Replace the sqlalchemy.url line in the config section
   config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
   ```

2. **Edit `alembic.ini`** - Comment out the sqlalchemy.url line:
   ```ini
   # sqlalchemy.url = driver://user:pass@localhost/dbname
   ```

---

## Step 7: Verify Setup

### 7.1 Test Database Connection

Create a test script `test_db.py` in the server directory:

```python
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()
        print("✅ Database connection successful!")
        print(f"PostgreSQL version: {version[0]}")
except Exception as e:
    print("❌ Database connection failed!")
    print(f"Error: {e}")
```

Run the test:

```powershell
python test_db.py
```

### 7.2 Create a Basic FastAPI App

Create `app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Dashboard Application API",
        "version": settings.APP_VERSION,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### 7.3 Run the Development Server

```powershell
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 7.4 Test the API

Open your browser and navigate to:

- **API:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

You should see the FastAPI welcome message and interactive documentation.

---

## Step 8: Database Schema Creation (Next Steps)

After verifying the setup, you'll create:

1. Database models in `app/models/`
2. Pydantic schemas in `app/schemas/`
3. Alembic migrations
4. CRUD operations
5. API endpoints

---

## Quick Reference Commands

### Activate Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

### Deactivate Virtual Environment

```powershell
deactivate
```

### Run Development Server

```powershell
cd app
uvicorn main:app --reload
```

### Create Database Migration

```powershell
alembic revision --autogenerate -m "migration message"
```

### Apply Migrations

```powershell
alembic upgrade head
```

### Rollback Migration

```powershell
alembic downgrade -1
```

### Install New Package

```powershell
pip install package-name
pip freeze > requirements.txt
```

### Run Tests

```powershell
pytest
```

---

## Troubleshooting

### Issue: PostgreSQL Connection Refused

**Solution:** Ensure PostgreSQL service is running

```powershell
# Check PostgreSQL service status in Services (services.msc)
# Or restart PostgreSQL service
```

### Issue: Port 8000 Already in Use

**Solution:** Use a different port

```powershell
uvicorn main:app --reload --port 8001
```

### Issue: Permission Error When Activating venv

**Solution:** Change PowerShell execution policy

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: psycopg2 Installation Error

**Solution:** Install binary version

```powershell
pip uninstall psycopg2
pip install psycopg2-binary
```

### Issue: Alembic Can't Find Models

**Solution:** Import all models in `app/db/base.py`

```python
from app.db.session import Base
from app.models.campaign import Campaign
from app.models.metric import Metric
# Import all models here
```

---

## Next Steps

Once setup is complete:

1. ✅ Create database models (`app/models/`)
2. ✅ Create Pydantic schemas (`app/schemas/`)
3. ✅ Set up database configuration (`app/core/config.py`)
4. ✅ Create initial migration
5. ✅ Build API endpoints
6. ✅ Implement data integration services
7. ✅ Write tests

---

## Resources

- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **SQLAlchemy Documentation:** https://docs.sqlalchemy.org/
- **Alembic Documentation:** https://alembic.sqlalchemy.org/
- **PostgreSQL Documentation:** https://www.postgresql.org/docs/
- **Pydantic Documentation:** https://docs.pydantic.dev/

---

**Setup completed!** 🎉

You're now ready to start building the Dashboard Application backend.

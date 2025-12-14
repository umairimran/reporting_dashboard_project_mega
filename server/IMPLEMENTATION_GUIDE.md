# **IMPLEMENTATION GUIDE - Dashboard Application Backend**

## **Project:** Paid Media Performance Dashboard (V1)

## **Tech Stack:** FastAPI + PostgreSQL + AWS S3 + Vibe API + Facebook Upload

## **Date:** December 13, 2025

---

# **TABLE OF CONTENTS**

1. [Project Overview](#1-project-overview)
2. [Three Primary Data Sources](#2-three-primary-data-sources)
3. [Modular Architecture](#3-modular-architecture)
4. [Development Roadmap](#4-development-roadmap)
5. [Module-by-Module Implementation](#5-module-by-module-implementation)
6. [Code Templates](#6-code-templates)
7. [Testing Strategy](#7-testing-strategy)
8. [Deployment Checklist](#8-deployment-checklist)

---

# **1. PROJECT OVERVIEW**

## **1.1 System Purpose**

Build a SaaS dashboard that:

- **Integrates THREE primary data sources** (Surfside, Vibe, Facebook)
- Processes and transforms data with client-specific CPM calculations
- Stores data in PostgreSQL with proper relationships
- Serves data via FastAPI REST endpoints
- Supports admin portal for client management
- Provides authentication and role-based access
- Handles async workflows (Vibe API) and file uploads (Facebook)

## **1.2 Database Schema**

**All database schemas, tables, indexes, and functions are now in:**

📄 **`server/database_schema.sql`**

This includes:

- 12 core tables (users, clients, campaigns, strategies, placements, creatives, metrics, etc.)
- Source-specific tables (vibe_credentials, vibe_report_requests, uploaded_files)
- Staging and ingestion tracking tables
- Indexes, triggers, and constraints

---

# **2. THREE PRIMARY DATA SOURCES**

All three data sources are **equally important** and will be implemented in **V1** with parallel development tracks.

## **2.1 Surfside (S3 Bucket)**

- **Type:** AWS S3 CSV/XLSX files
- **Access:** boto3 SDK
- **Frequency:** Daily automated ingestion
- **Delivery:** Daily at 3-4 AM EST
- **Location:** Stephen's S3 bucket
- **Processing:** ETL pipeline with CPM recalculation
- **Data Volume:** ~50k rows/day per client

**Key Columns Expected:**

```
Date, Campaign, Strategy, Placement, Creative, Impressions, Clicks,
Conversions, Conversion Revenue, CTR
```

## **2.2 Vibe (REST API)**

- **Type:** REST API with async report generation
- **Access:** HTTP requests with API key
- **Frequency:** Daily automated pull
- **Rate Limit:** 15 requests/hour
- **Async Flow:** Create report → Poll status → Download CSV
- **Processing:** ETL pipeline with CPM recalculation

**API Endpoints:**

```
POST /reporting/v1/std/reports  → Create report
GET  /reporting/v1/std/reports/{id} → Check status
GET  {download_url} → Download CSV
```

**Expected Response Fields:**

```
date, campaign_name, strategy_name, placement_name, creative_name,
impressions, clicks, conversions, revenue
```

## **2.3 Facebook (Manual Upload)**

- **Type:** User-uploaded CSV/XLSX files
- **Access:** File upload endpoint (multipart/form-data)
- **Frequency:** On-demand (manual)
- **Processing:** Validation → Staging → ETL with CPM recalculation
- **Storage:** Temporary local storage or S3 bucket

**Expected Columns:**

```
Date, Campaign Name, Ad Set Name, Ad Name, Impressions, Clicks,
Conversions, Revenue
```

**File Constraints:**

- Max size: 50MB
- Formats: `.csv`, `.xlsx`
- Date range validation
- Duplicate detection

---

# **3. MODULAR ARCHITECTURE**

We'll organize the backend into **10 focused modules**, each with clear responsibilities:

```
server/
├── database_schema.sql          # Complete DB schema
├── .env                         # Environment variables
├── requirements.txt             # Python dependencies
├── alembic/                     # Database migrations
│   ├── env.py
│   └── versions/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app entry point
│   │
│   ├── core/                    # MODULE 1: Core/Foundation
│   │   ├── config.py            # Settings, environment variables
│   │   ├── database.py          # DB connection, session management
│   │   ├── logging.py           # Logging configuration
│   │   └── exceptions.py        # Custom exceptions
│   │
│   ├── auth/                    # MODULE 2: Authentication & Authorization
│   │   ├── models.py            # User model
│   │   ├── schemas.py           # Login, register DTOs
│   │   ├── security.py          # JWT, password hashing
│   │   ├── dependencies.py      # get_current_user, require_admin
│   │   └── router.py            # /auth endpoints
│   │
│   ├── clients/                 # MODULE 3: Client Management
│   │   ├── models.py            # Client, ClientSettings models
│   │   ├── schemas.py           # Client DTOs
│   │   ├── service.py           # CRUD operations, CPM management
│   │   └── router.py            # /clients endpoints
│   │
│   ├── campaigns/               # MODULE 4: Campaign Hierarchy
│   │   ├── models.py            # Campaign, Strategy, Placement, Creative
│   │   ├── schemas.py           # Campaign DTOs
│   │   ├── service.py           # Hierarchy management
│   │   └── router.py            # /campaigns endpoints
│   │
│   ├── surfside/                # MODULE 5: Surfside Integration
│   │   ├── s3_service.py        # S3 file download (boto3)
│   │   ├── parser.py            # CSV/XLSX parsing
│   │   ├── etl.py               # Surfside-specific ETL
│   │   └── scheduler.py         # Daily cron job
│   │
│   ├── vibe/                    # MODULE 6: Vibe Integration
│   │   ├── api_client.py        # HTTP client for Vibe API
│   │   ├── models.py            # VibeCredentials, VibeReportRequest
│   │   ├── service.py           # Async report workflow
│   │   ├── parser.py            # Vibe CSV parsing
│   │   ├── etl.py               # Vibe-specific ETL
│   │   └── scheduler.py         # Daily API pull job
│   │
│   ├── facebook/                # MODULE 7: Facebook Integration
│   │   ├── upload_handler.py   # File upload processing
│   │   ├── validator.py         # File validation
│   │   ├── parser.py            # Facebook CSV/XLSX parsing
│   │   ├── etl.py               # Facebook-specific ETL
│   │   ├── models.py            # UploadedFiles model
│   │   └── router.py            # /facebook/upload endpoint
│   │
│   ├── metrics/                 # MODULE 8: Metrics & Aggregation
│   │   ├── models.py            # DailyMetrics, WeeklySummaries, MonthlySummaries
│   │   ├── schemas.py           # Metrics DTOs
│   │   ├── calculator.py        # CPM calculations, derived metrics
│   │   ├── aggregator.py        # Weekly/monthly rollup logic
│   │   └── router.py            # /metrics endpoints
│   │
│   ├── dashboard/               # MODULE 9: Dashboard API
│   │   ├── service.py           # Dashboard data queries
│   │   ├── schemas.py           # Dashboard response DTOs
│   │   └── router.py            # /dashboard endpoints
│   │
│   ├── etl/                     # MODULE 10: Shared ETL Components
│   │   ├── orchestrator.py      # Unified ingestion orchestrator
│   │   ├── staging.py           # Staging table operations
│   │   ├── transformer.py       # Common transformations
│   │   └── loader.py            # Load to final tables
│   │
│   ├── jobs/                    # Scheduled Jobs
│   │   ├── daily_ingestion.py   # Run all 3 sources daily
│   │   ├── summaries.py         # Weekly/monthly aggregations
│   │   └── scheduler.py         # APScheduler setup
│   │
│   └── api/
│       └── v1/
│           └── api.py           # API router aggregator
│
└── tests/
    ├── test_auth/
    ├── test_surfside/
    ├── test_vibe/
    ├── test_facebook/
    └── test_etl/
```

---

# **4. DEVELOPMENT ROADMAP**

## **4.1 Development Phases**

We'll develop in **3 parallel tracks** + **2 integration phases**:

### **Phase 1: Foundation (Week 1)**

Build core infrastructure that all modules depend on.

**Deliverables:**

- ✅ Database schema deployed (`database_schema.sql`)
- ✅ FastAPI app structure
- ✅ Authentication module (JWT, RBAC)
- ✅ Client management module (CRUD, CPM)
- ✅ Campaign hierarchy models
- ✅ Shared ETL utilities

**Dependencies:** None  
**Team Size:** 1-2 developers

---

### **Phase 2A: Surfside Track (Week 2-3)**

Parallel development of Surfside S3 integration.

**Deliverables:**

- ✅ S3 service (boto3 download)
- ✅ Surfside CSV parser
- ✅ Surfside ETL pipeline
- ✅ Daily scheduler (APScheduler)
- ✅ Ingestion logs
- ✅ Testing (unit + integration)

**Dependencies:** Phase 1  
**Team Size:** 1 developer

---

### **Phase 2B: Vibe Track (Week 2-3)**

Parallel development of Vibe API integration.

**Deliverables:**

- ✅ Vibe API client (async report workflow)
- ✅ Vibe credentials management
- ✅ Report request tracking
- ✅ Vibe CSV parser
- ✅ Vibe ETL pipeline
- ✅ Rate limiting (15/hour)
- ✅ Daily scheduler
- ✅ Testing (unit + integration + mock API)

**Dependencies:** Phase 1  
**Team Size:** 1 developer

---

### **Phase 2C: Facebook Track (Week 2-3)**

Parallel development of Facebook upload integration.

**Deliverables:**

- ✅ File upload endpoint (multipart/form-data)
- ✅ File validation (size, format, columns)
- ✅ Facebook CSV/XLSX parser
- ✅ Facebook ETL pipeline
- ✅ Uploaded files tracking
- ✅ Error handling and user feedback
- ✅ Testing (unit + integration)

**Dependencies:** Phase 1  
**Team Size:** 1 developer

---

### **Phase 3: Integration & Metrics (Week 4)**

Integrate all three sources and build metrics/dashboard APIs.

**Deliverables:**

- ✅ Unified ETL orchestrator (handles all 3 sources)
- ✅ Daily metrics calculation (CPM, CPC, CPA, ROAS, CTR)
- ✅ Weekly/monthly aggregation
- ✅ Dashboard API endpoints
- ✅ Export functionality (CSV/XLSX)
- ✅ Performance optimization
- ✅ End-to-end testing

**Dependencies:** Phase 2A, 2B, 2C  
**Team Size:** 2 developers

---

### **Phase 4: Admin Portal & Deployment (Week 5)**

Build admin features and deploy to production.

**Deliverables:**

- ✅ Admin portal endpoints
- ✅ Ingestion monitoring dashboard
- ✅ Error alerting
- ✅ Documentation (API docs, deployment guide)
- ✅ Production deployment
- ✅ Monitoring setup

**Dependencies:** Phase 3  
**Team Size:** 1-2 developers

---

## **4.2 Parallel Development Strategy**

**Week 1:** Foundation (all developers together)  
**Week 2-3:** Split team into 3 tracks

- Developer A: Surfside module
- Developer B: Vibe module
- Developer C: Facebook module

**Week 4:** Integration (all developers together)  
**Week 5:** Polish & deploy (all developers together)

**Total Timeline:** 5 weeks (or 3 weeks with 3 developers working in parallel)

---

# **5. MODULE-BY-MODULE IMPLEMENTATION**

## **Module 1: Core/Foundation**

### **5.1 Database Connection (`app/core/database.py`)**

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Database URL from environment
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### **5.2 Configuration (`app/core/config.py`)**

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Dashboard API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # AWS S3 (Surfside)
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str
    S3_PREFIX: str = "surfside/"

    # Vibe API
    VIBE_API_BASE_URL: str = "https://api.vibe.co"
    VIBE_API_KEY: str
    VIBE_ADVERTISER_ID: str
    VIBE_RATE_LIMIT: int = 15  # requests per hour

    # Facebook Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB

    # Email Alerts (SMTP)
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM: str
    ALERT_EMAIL: str  # Stephen's email for alerts

    # Scheduler
    SURFSIDE_CRON: str = "0 5 * * *"  # 5 AM daily
    VIBE_CRON: str = "0 6 * * *"      # 6 AM daily
    SUMMARY_CRON: str = "0 7 * * *"   # 7 AM daily

    class Config:
        env_file = ".env"@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
```

### **5.3 Logging (`app/core/logging.py`)**

```python
import logging
import sys
from app.core.config import settings

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG if settings.DEBUG else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log")
        ]
    )

    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
```

### **5.3.1 Email Notification Service (`app/core/email.py`)**

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from app.core.logging import logger
from typing import List, Optional

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM
        self.alert_email = settings.ALERT_EMAIL

    def send_email(self, to: str, subject: str, body: str, html: bool = False):
        """Send email via SMTP."""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to
            msg['Subject'] = subject

            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent to {to}: {subject}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise

    def send_ingestion_failure_alert(self, client_name: str, date: str, error: str):
        """Alert for ingestion failure."""
        subject = f"🚨 Data Ingestion Failed - {client_name} - {date}"
        body = f"""
        Data ingestion has failed for:

        Client: {client_name}
        Date: {date}
        Error: {error}

        Please investigate the issue in the admin portal.
        """
        self.send_email(self.alert_email, subject, body)

    def send_missing_file_alert(self, date: str, bucket: str, expected_path: str):
        """Alert for missing S3 file."""
        subject = f"⚠️ Missing Daily File - {date}"
        body = f"""
        Expected daily file not found in S3:

        Date: {date}
        Bucket: {bucket}
        Expected Path: {expected_path}

        Please check if the file was uploaded by the media partner.
        """
        self.send_email(self.alert_email, subject, body)

    def send_validation_error_alert(self, client_name: str, date: str, errors: List[str]):
        """Alert for data validation errors."""
        subject = f"⚠️ Data Validation Errors - {client_name} - {date}"
        error_list = "\n".join([f"- {e}" for e in errors])
        body = f"""
        Data validation failed for:

        Client: {client_name}
        Date: {date}

        Errors:
        {error_list}

        Please review the data quality.
        """
        self.send_email(self.alert_email, subject, body)

email_service = EmailService()
```

---

## **Module 2: Authentication**

### **5.4 Security Utilities (`app/auth/security.py`)**

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
```

### **5.5 Authentication Dependencies (`app/auth/dependencies.py`)**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.security import decode_access_token
from app.auth.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception

    return user

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
```

### **5.5.1 Password Reset (`app/auth/router.py` - additional endpoint)**

```python
from app.auth.security import hash_password
from app.auth.dependencies import require_admin

@router.post("/reset-password/{user_id}")
async def reset_user_password(
    user_id: str,
    new_password: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin-only: Reset a client's password."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == "admin" and user.id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Cannot reset another admin's password"
        )

    user.password_hash = hash_password(new_password)
    db.commit()

    # Optionally send email notification to user
    # email_service.send_password_reset_notification(user.email)

    return {"message": "Password reset successfully"}
```

---

## **Module 3: Client Management**

### **5.6 Client Service (`app/clients/service.py`)**

```python
from sqlalchemy.orm import Session
from app.clients.models import Client, ClientSettings
from app.clients.schemas import ClientCreate, ClientSettingsUpdate
from datetime import date

class ClientService:
    @staticmethod
    def create_client(db: Session, data: ClientCreate, user_id: str):
        client = Client(
            name=data.name,
            user_id=user_id,
            status="active"
        )
        db.add(client)
        db.commit()
        db.refresh(client)
        return client

    @staticmethod
    def get_client_by_id(db: Session, client_id: str):
        return db.query(Client).filter(Client.id == client_id).first()

    @staticmethod
    def update_cpm(db: Session, client_id: str, cpm: float, effective_date: date = None):
        settings = ClientSettings(
            client_id=client_id,
            cpm=cpm,
            effective_date=effective_date or date.today()
        )
        db.add(settings)
        db.commit()
        return settings

    @staticmethod
    def get_current_cpm(db: Session, client_id: str) -> float:
        settings = db.query(ClientSettings) \
            .filter(ClientSettings.client_id == client_id) \
            .order_by(ClientSettings.effective_date.desc()) \
            .first()
        return settings.cpm if settings else 15.0  # default CPM

    @staticmethod
    def toggle_client_status(db: Session, client_id: str, status: str):
        """Enable or disable client access."""
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")

        client.status = status

        # Also update associated user
        if client.user_id:
            user = db.query(User).filter(User.id == client.user_id).first()
            if user:
                user.is_active = (status == "active")

        db.commit()
        return client

    @staticmethod
    def get_all_active_clients(db: Session):
        """Get all active clients for scheduled jobs."""
        return db.query(Client).filter(Client.status == "active").all()
```

---

## **Module 5: Surfside Integration**

### **5.7 S3 Service (`app/surfside/s3_service.py`)**

```python
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings
from app.core.logging import logger
from datetime import datetime, timedelta
from typing import List

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket = settings.S3_BUCKET_NAME
        self.prefix = settings.S3_PREFIX

    def list_files_for_date(self, target_date: datetime) -> List[str]:
        """List all CSV/XLSX files for a specific date."""
        try:
            date_str = target_date.strftime("%Y-%m-%d")
            prefix = f"{self.prefix}{date_str}/"

            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix
            )

            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    key = obj['Key']
                    if key.endswith(('.csv', '.xlsx')):
                        files.append(key)

            logger.info(f"Found {len(files)} files in S3 for date {date_str}")
            return files

        except ClientError as e:
            logger.error(f"S3 list error: {e}")
            raise

    def download_file(self, s3_key: str, local_path: str):
        """Download a file from S3."""
        try:
            self.s3_client.download_file(self.bucket, s3_key, local_path)
            logger.info(f"Downloaded {s3_key} to {local_path}")
        except ClientError as e:
            logger.error(f"S3 download error: {e}")
            raise

    def get_latest_file(self) -> str:
        """Get the most recent file from S3."""
        yesterday = datetime.now() - timedelta(days=1)
        files = self.list_files_for_date(yesterday)
        return files[0] if files else None
```

### **5.8 Surfside Parser (`app/surfside/parser.py`)**

```python
import pandas as pd
from typing import List, Dict
from pathlib import Path

class SurfsideParser:
    REQUIRED_COLUMNS = [
        'Date', 'Campaign', 'Strategy', 'Placement', 'Creative',
        'Impressions', 'Clicks', 'Conversions', 'Conversion Revenue', 'CTR'
    ]

    @staticmethod
    def parse_file(file_path: str) -> List[Dict]:
        """Parse Surfside CSV/XLSX file."""
        path = Path(file_path)

        # Read file
        if path.suffix == '.csv':
            df = pd.read_csv(file_path)
        elif path.suffix == '.xlsx':
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

        # Validate columns
        missing = set(SurfsideParser.REQUIRED_COLUMNS) - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        # Clean data
        df['Date'] = pd.to_datetime(df['Date'])
        df['Impressions'] = df['Impressions'].fillna(0).astype(int)
        df['Clicks'] = df['Clicks'].fillna(0).astype(int)
        df['Conversions'] = df['Conversions'].fillna(0).astype(int)
        df['Conversion Revenue'] = df['Conversion Revenue'].fillna(0).astype(float)
        df['CTR'] = df['CTR'].fillna(0).astype(float)

        # Convert to dict records
        return df.to_dict('records')
```

### **5.9 Surfside ETL (`app/surfside/etl.py`)**

```python
from sqlalchemy.orm import Session
from app.surfside.s3_service import S3Service
from app.surfside.parser import SurfsideParser
from app.etl.staging import StagingService
from app.etl.transformer import TransformerService
from app.etl.loader import LoaderService
from app.core.logging import logger
import uuid
from datetime import datetime

class SurfsideETL:
    def __init__(self, db: Session):
        self.db = db
        self.s3_service = S3Service()
        self.parser = SurfsideParser()
        self.staging = StagingService(db)
        self.transformer = TransformerService(db)
        self.loader = LoaderService(db)

    def run_daily_ingestion(self, client_id: str, target_date: datetime):
        """Run complete Surfside ETL for a specific date."""
        ingestion_run_id = str(uuid.uuid4())
        logger.info(f"Starting Surfside ingestion for client {client_id}, date {target_date}")

        try:
            # 1. Extract: Download from S3
            files = self.s3_service.list_files_for_date(target_date)
            if not files:
                logger.warning(f"No Surfside files found for {target_date}")
                return

            for s3_key in files:
                local_path = f"/tmp/{s3_key.split('/')[-1]}"
                self.s3_service.download_file(s3_key, local_path)

                # 2. Parse file
                records = self.parser.parse_file(local_path)
                logger.info(f"Parsed {len(records)} records from {s3_key}")

                # 3. Load to staging
                self.staging.load_to_staging(
                    records=records,
                    client_id=client_id,
                    source="surfside",
                    ingestion_run_id=ingestion_run_id
                )

            # 4. Transform and load to final tables
            self.transformer.process_staging(ingestion_run_id, client_id)
            self.loader.load_daily_metrics(ingestion_run_id)

            logger.info(f"Surfside ingestion completed for {target_date}")

        except Exception as e:
            logger.error(f"Surfside ETL failed: {e}")
            raise

    def run_historical_backfill(self, client_id: str, start_date: datetime, end_date: datetime):
        """Backfill historical data for a date range."""
        logger.info(f"Starting historical backfill for client {client_id} from {start_date} to {end_date}")

        current_date = start_date
        successful_days = 0
        failed_days = 0

        while current_date <= end_date:
            try:
                logger.info(f"Processing historical data for {current_date}")
                self.run_daily_ingestion(client_id, current_date)
                successful_days += 1
            except Exception as e:
                logger.error(f"Failed to backfill data for {current_date}: {e}")
                failed_days += 1

            current_date += timedelta(days=1)

        logger.info(f"Backfill completed: {successful_days} successful, {failed_days} failed")
        return {"successful": successful_days, "failed": failed_days}
```

---

## **Module 6: Vibe Integration**

### **5.10 Vibe API Client (`app/vibe/api_client.py`)**

```python
import httpx
from app.core.config import settings
from app.core.logging import logger
from typing import Dict
import asyncio

class VibeAPIClient:
    def __init__(self, api_key: str = None, advertiser_id: str = None):
        self.base_url = settings.VIBE_API_BASE_URL
        self.api_key = api_key or settings.VIBE_API_KEY
        # Support per-client advertiser IDs for multi-client setups
        self.advertiser_id = advertiser_id or settings.VIBE_ADVERTISER_ID
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    async def create_report(self, start_date: str, end_date: str, advertiser_id: str) -> Dict:
        """Create async report request."""
        async with httpx.AsyncClient() as client:
            payload = {
                "advertiserId": advertiser_id,
                "startDate": start_date,
                "endDate": end_date,
                "metrics": ["impressions", "clicks", "conversions", "revenue"],
                "dimensions": ["date", "campaign", "strategy", "placement", "creative"]
            }

            response = await client.post(
                f"{self.base_url}/reporting/v1/std/reports",
                json=payload,
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def check_report_status(self, report_id: str) -> Dict:
        """Check report generation status."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/reporting/v1/std/reports/{report_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def download_report(self, download_url: str) -> bytes:
        """Download completed report CSV."""
        async with httpx.AsyncClient() as client:
            response = await client.get(download_url)
            response.raise_for_status()
            return response.content

    async def wait_for_report(self, report_id: str, max_attempts: int = 20) -> str:
        """Poll until report is ready, return download URL."""
        for attempt in range(max_attempts):
            status_data = await self.check_report_status(report_id)
            status = status_data.get("status")

            if status == "done":
                return status_data.get("downloadUrl")
            elif status == "error":
                raise Exception(f"Report generation failed: {status_data.get('error')}")

            logger.info(f"Report {report_id} status: {status}, attempt {attempt + 1}")
            await asyncio.sleep(30)  # Wait 30 seconds between checks

        raise TimeoutError(f"Report {report_id} not ready after {max_attempts} attempts")
```

### **5.10 Vibe Service (`app/vibe/service.py`)**

```python
from typing import Optional
from sqlalchemy.orm import Session
from app.vibe.api_client import VibeAPIClient
from app.models import VibeCredentials
from app.core.logging import logger

class VibeService:
    \"\"\"Service for managing Vibe API interactions with client-specific credentials\"\"\"

    def __init__(self, db: Session, client_id: Optional[str] = None):
        self.db = db
        # Support client-specific Vibe credentials for multi-client setups
        advertiser_id, api_key = self._get_client_credentials(client_id) if client_id else (None, None)
        self.client = VibeAPIClient(api_key=api_key, advertiser_id=advertiser_id)

    def _get_client_credentials(self, client_id: str) -> tuple[Optional[str], Optional[str]]:
        \"\"\"Fetch client-specific Vibe credentials from database\"\"\"
        creds = self.db.query(VibeCredentials).filter(
            VibeCredentials.client_id == client_id,
            VibeCredentials.is_active == True
        ).first()

        if creds:
            logger.info(f"Using client-specific Vibe credentials for client {client_id}")
            return (creds.advertiser_id, creds.api_key)
        else:
            logger.warning(f"No Vibe credentials found for client {client_id}, using defaults")
            return (None, None)

    async def request_report(self, start_date: str, end_date: str):
        \"\"\"Request report using client-specific or default credentials\"\"\"
        return await self.client.create_report(start_date, end_date, self.client.advertiser_id)
```

### **5.11 Vibe ETL (`app/vibe/etl.py`)**

```python
from sqlalchemy.orm import Session
from app.vibe.api_client import VibeAPIClient
from app.vibe.parser import VibeParser
from app.etl.staging import StagingService
from app.etl.transformer import TransformerService
from app.etl.loader import LoaderService
from app.core.logging import logger
from datetime import datetime
import uuid

class VibeETL:
    def __init__(self, db: Session):
        self.db = db
        self.api_client = VibeAPIClient()
        self.parser = VibeParser()
        self.staging = StagingService(db)
        self.transformer = TransformerService(db)
        self.loader = LoaderService(db)

    async def run_daily_ingestion(self, client_id: str, target_date: datetime, advertiser_id: str):
        """Run complete Vibe ETL for a specific date."""
        ingestion_run_id = str(uuid.uuid4())
        date_str = target_date.strftime("%Y-%m-%d")
        logger.info(f"Starting Vibe ingestion for client {client_id}, date {date_str}")

        try:
            # 1. Extract: Create report via API
            report_response = await self.api_client.create_report(
                start_date=date_str,
                end_date=date_str,
                advertiser_id=advertiser_id
            )
            report_id = report_response.get("reportId")
            logger.info(f"Created Vibe report {report_id}")

            # 2. Wait for report to complete
            download_url = await self.api_client.wait_for_report(report_id)
            logger.info(f"Vibe report ready: {download_url}")

            # 3. Download CSV
            csv_content = await self.api_client.download_report(download_url)
            local_path = f"/tmp/vibe_{date_str}.csv"
            with open(local_path, 'wb') as f:
                f.write(csv_content)

            # 4. Parse file
            records = self.parser.parse_file(local_path)
            logger.info(f"Parsed {len(records)} records from Vibe")

            # 5. Load to staging
            self.staging.load_to_staging(
                records=records,
                client_id=client_id,
                source="vibe",
                ingestion_run_id=ingestion_run_id
            )

            # 6. Transform and load to final tables
            self.transformer.process_staging(ingestion_run_id, client_id)
            self.loader.load_daily_metrics(ingestion_run_id)

            logger.info(f"Vibe ingestion completed for {date_str}")

        except Exception as e:
            logger.error(f"Vibe ETL failed: {e}")
            raise
```

---

## **Module 7: Facebook Integration**

### **5.12 Facebook Upload Handler (`app/facebook/upload_handler.py`)**

```python
from fastapi import UploadFile, HTTPException
from app.facebook.validator import FacebookValidator
from app.facebook.parser import FacebookParser
from app.etl.staging import StagingService
from app.etl.transformer import TransformerService
from app.etl.loader import LoaderService
from sqlalchemy.orm import Session
from app.core.logging import logger
import uuid
import shutil
from pathlib import Path

class FacebookUploadHandler:
    def __init__(self, db: Session):
        self.db = db
        self.validator = FacebookValidator()
        self.parser = FacebookParser()
        self.staging = StagingService(db)
        self.transformer = TransformerService(db)
        self.loader = LoaderService(db)

    async def process_upload(self, file: UploadFile, client_id: str, user_id: str):
        """Process uploaded Facebook CSV/XLSX file."""
        ingestion_run_id = str(uuid.uuid4())
        logger.info(f"Processing Facebook upload from user {user_id} for client {client_id}")

        try:
            # 1. Validate file
            self.validator.validate_file(file)

            # 2. Save file temporarily
            temp_path = f"/tmp/{file.filename}"
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # 3. Parse file
            records = self.parser.parse_file(temp_path)
            logger.info(f"Parsed {len(records)} records from Facebook upload")

            # 4. Validate data
            self.validator.validate_data(records)

            # 5. Load to staging
            self.staging.load_to_staging(
                records=records,
                client_id=client_id,
                source="facebook",
                ingestion_run_id=ingestion_run_id
            )

            # 6. Transform and load to final tables
            self.transformer.process_staging(ingestion_run_id, client_id)
            self.loader.load_daily_metrics(ingestion_run_id)

            logger.info(f"Facebook upload processing completed")
            return {
                "status": "success",
                "records_processed": len(records),
                "ingestion_run_id": ingestion_run_id
            }

        except Exception as e:
            logger.error(f"Facebook upload processing failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))
```

### **5.13 Facebook Validator (`app/facebook/validator.py`)**

```python
from fastapi import UploadFile, HTTPException
from app.core.config import settings
from typing import List, Dict

class FacebookValidator:
    ALLOWED_EXTENSIONS = ['.csv', '.xlsx']
    REQUIRED_COLUMNS = ['Date', 'Campaign Name', 'Ad Set Name', 'Ad Name',
                        'Impressions', 'Clicks', 'Conversions', 'Revenue']

    def validate_file(self, file: UploadFile):
        """Validate uploaded file."""
        # Check extension
        if not any(file.filename.endswith(ext) for ext in self.ALLOWED_EXTENSIONS):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {self.ALLOWED_EXTENSIONS}"
            )

        # Check size (in production, implement streaming validation)
        # For now, this is a placeholder

    def validate_data(self, records: List[Dict]):
        """Validate parsed data."""
        if not records:
            raise HTTPException(status_code=400, detail="File is empty")

        # Check required columns in first record
        first_record = records[0]
        missing = set(self.REQUIRED_COLUMNS) - set(first_record.keys())
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing columns: {missing}"
            )

    def check_duplicates(self, db: Session, records: List[Dict], client_id: str, source: str):
        """Check for duplicate records already in database."""
        duplicates = []

        for record in records:
            # Check if record already exists in daily_metrics
            existing = db.query(DailyMetrics).filter(
                DailyMetrics.client_id == client_id,
                DailyMetrics.date == record.get('Date'),
                DailyMetrics.source == source
            ).first()

            if existing:
                duplicates.append({
                    'date': record.get('Date'),
                    'campaign': record.get('Campaign Name'),
                    'source': source
                })

        if duplicates:
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "Duplicate records detected",
                    "duplicates": duplicates[:10]  # Show first 10
                }
            )
```

---

## **Module 7.5: Export Functionality**

### **5.13.1 CSV Export Service (`app/exports/csv_export.py`)**

```python
import csv
import io
from typing import List, Dict
from datetime import datetime
from fastapi.responses import StreamingResponse

class CSVExportService:
    @staticmethod
    def export_metrics_to_csv(metrics: List[Dict], filename: str = None) -> StreamingResponse:
        """Export metrics data to CSV file."""
        output = io.StringIO()

        if not metrics:
            return None

        # Get all unique keys from metrics
        fieldnames = list(metrics[0].keys())

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metrics)

        output.seek(0)

        filename = filename or f"metrics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
```

### **5.13.2 PDF Export Service (`app/exports/pdf_export.py`)**

```python
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from typing import List, Dict
from datetime import datetime
from fastapi.responses import StreamingResponse

class PDFExportService:
    @staticmethod
    def export_dashboard_to_pdf(
        summary_data: Dict,
        campaigns_data: List[Dict],
        client_name: str,
        date_range: str
    ) -> StreamingResponse:
        """Export dashboard data to formatted PDF."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        # Container for elements
        elements = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=30,
        )
        title = Paragraph(f"Performance Dashboard - {client_name}", title_style)
        elements.append(title)

        # Date range
        subtitle = Paragraph(f"Period: {date_range}", styles['Heading2'])
        elements.append(subtitle)
        elements.append(Spacer(1, 0.3*inch))

        # Summary Section
        summary_title = Paragraph("Summary Overview", styles['Heading2'])
        elements.append(summary_title)
        elements.append(Spacer(1, 0.2*inch))

        # Summary table
        summary_table_data = [
            ['Metric', 'Value'],
            ['Impressions', f"{summary_data.get('impressions', 0):,}"],
            ['Clicks', f"{summary_data.get('clicks', 0):,}"],
            ['CTR', f"{summary_data.get('ctr', 0):.2f}%"],
            ['Conversions', f"{summary_data.get('conversions', 0):,}"],
            ['Revenue', f"${summary_data.get('revenue', 0):,.2f}"],
            ['Spend', f"${summary_data.get('spend', 0):,.2f}"],
            ['CPC', f"${summary_data.get('cpc', 0):.2f}"],
            ['CPA', f"${summary_data.get('cpa', 0):.2f}"],
            ['ROAS', f"{summary_data.get('roas', 0):.2f}%"],
        ]

        summary_table = Table(summary_table_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.5*inch))

        # Campaign Performance
        campaign_title = Paragraph("Top Campaigns", styles['Heading2'])
        elements.append(campaign_title)
        elements.append(Spacer(1, 0.2*inch))

        campaign_table_data = [['Campaign', 'Impressions', 'Clicks', 'Conversions', 'Spend', 'ROAS']]
        for campaign in campaigns_data[:10]:  # Top 10
            campaign_table_data.append([
                campaign.get('name', 'N/A')[:30],
                f"{campaign.get('impressions', 0):,}",
                f"{campaign.get('clicks', 0):,}",
                f"{campaign.get('conversions', 0):,}",
                f"${campaign.get('spend', 0):,.2f}",
                f"{campaign.get('roas', 0):.1f}%"
            ])

        campaign_table = Table(campaign_table_data, colWidths=[2*inch, 1*inch, 0.8*inch, 1*inch, 1*inch, 0.8*inch])
        campaign_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        elements.append(campaign_table)

        # Build PDF
        doc.build(elements)
        buffer.seek(0)

        filename = f"dashboard_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
```

### **5.13.3 Export Router (`app/exports/router.py`)**

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.exports.csv_export import CSVExportService
from app.exports.pdf_export import PDFExportService
from datetime import date

router = APIRouter()

@router.get("/csv")
async def export_to_csv(
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export filtered metrics to CSV."""
    # Query metrics based on filters
    metrics = get_metrics_for_export(db, current_user.client_id, start_date, end_date)

    return CSVExportService.export_metrics_to_csv(metrics)

@router.get("/pdf")
async def export_to_pdf(
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export dashboard to formatted PDF."""
    # Get summary and campaign data
    summary_data = get_summary_data(db, current_user.client_id, start_date, end_date)
    campaigns_data = get_campaigns_data(db, current_user.client_id, start_date, end_date)

    client = db.query(Client).filter(Client.id == current_user.client_id).first()
    date_range = f"{start_date} to {end_date}"

    return PDFExportService.export_dashboard_to_pdf(
        summary_data,
        campaigns_data,
        client.name,
        date_range
    )
```

---

## **Module 8: Metrics & Calculation**

### **5.14 Aggregator Service (`app/metrics/aggregator.py`)**

```python
from sqlalchemy.orm import Session
from app.models import DailyMetrics, WeeklySummary, MonthlySummary, Campaign, Creative
from datetime import date, timedelta
from typing import List, Dict
import json

class AggregatorService:
    def __init__(self, db: Session):
        self.db = db

    def generate_weekly_summary(self, client_id: str, week_start: date):
        """Generate weekly summary with week-over-week deltas."""
        week_end = week_start + timedelta(days=6)

        # Get current week metrics
        current_week_metrics = self.db.query(DailyMetrics).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date >= week_start,
            DailyMetrics.date <= week_end
        ).all()

        # Aggregate current week
        total_impressions = sum(m.impressions for m in current_week_metrics)
        total_clicks = sum(m.clicks for m in current_week_metrics)
        total_conversions = sum(m.conversions for m in current_week_metrics)
        total_revenue = sum(m.conversion_revenue for m in current_week_metrics)
        total_spend = sum(m.spend for m in current_week_metrics)

        # Calculate derived metrics
        ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
        cpa = (total_spend / total_conversions) if total_conversions > 0 else 0
        roas = (total_revenue / total_spend * 100) if total_spend > 0 else 0

        # Get previous week for comparison
        prev_week_start = week_start - timedelta(days=7)
        prev_week_end = prev_week_start + timedelta(days=6)

        prev_week_summary = self.db.query(WeeklySummary).filter(
            WeeklySummary.client_id == client_id,
            WeeklySummary.week_start == prev_week_start
        ).first()

        # Calculate deltas (week-over-week)
        deltas = {}
        if prev_week_summary:
            deltas = {
                'impressions_delta': total_impressions - prev_week_summary.impressions,
                'impressions_delta_pct': ((total_impressions - prev_week_summary.impressions) / prev_week_summary.impressions * 100) if prev_week_summary.impressions > 0 else 0,
                'clicks_delta': total_clicks - prev_week_summary.clicks,
                'conversions_delta': total_conversions - prev_week_summary.conversions,
                'revenue_delta': total_revenue - prev_week_summary.revenue,
                'spend_delta': total_spend - prev_week_summary.spend,
                'roas_delta': roas - prev_week_summary.roas if prev_week_summary.roas else 0
            }

        # Identify top performers
        top_campaigns = self._get_top_campaigns(current_week_metrics)
        top_creatives = self._get_top_creatives(current_week_metrics)

        # Identify underperformers
        underperformers = self._get_underperformers(current_week_metrics)

        # Create summary record
        summary = WeeklySummary(
            client_id=client_id,
            week_start=week_start,
            week_end=week_end,
            impressions=total_impressions,
            clicks=total_clicks,
            conversions=total_conversions,
            revenue=total_revenue,
            spend=total_spend,
            ctr=ctr,
            cpc=cpc,
            cpa=cpa,
            roas=roas,
            top_campaigns=json.dumps({**top_campaigns, 'deltas': deltas, 'underperformers': underperformers}),
            top_creatives=json.dumps(top_creatives)
        )

        self.db.merge(summary)
        self.db.commit()
        return summary

    def generate_monthly_summary(self, client_id: str, month_start: date):
        """Generate monthly summary with month-over-month deltas."""
        # Calculate month_end
        if month_start.month == 12:
            month_end = date(month_start.year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(month_start.year, month_start.month + 1, 1) - timedelta(days=1)

        # Similar logic to weekly, but for monthly aggregation
        current_month_metrics = self.db.query(DailyMetrics).filter(
            DailyMetrics.client_id == client_id,
            DailyMetrics.date >= month_start,
            DailyMetrics.date <= month_end
        ).all()

        # Aggregate and calculate (similar to weekly)
        # ... (implementation similar to weekly summary)

        # Get previous month for comparison
        if month_start.month == 1:
            prev_month_start = date(month_start.year - 1, 12, 1)
        else:
            prev_month_start = date(month_start.year, month_start.month - 1, 1)

        prev_month_summary = self.db.query(MonthlySummary).filter(
            MonthlySummary.client_id == client_id,
            MonthlySummary.month_start == prev_month_start
        ).first()

        # Calculate month-over-month deltas (similar to week-over-week)
        # ...

    def _get_top_campaigns(self, metrics: List[DailyMetrics], limit: int = 5) -> Dict:
        """Get top campaigns by conversions and revenue."""
        campaign_totals = {}

        for m in metrics:
            if m.campaign_id not in campaign_totals:
                campaign_totals[m.campaign_id] = {
                    'campaign_id': str(m.campaign_id),
                    'campaign_name': m.campaign.name if m.campaign else 'Unknown',
                    'conversions': 0,
                    'revenue': 0,
                    'spend': 0
                }
            campaign_totals[m.campaign_id]['conversions'] += m.conversions
            campaign_totals[m.campaign_id]['revenue'] += float(m.conversion_revenue)
            campaign_totals[m.campaign_id]['spend'] += float(m.spend)

        # Sort by conversions
        top_by_conversions = sorted(
            campaign_totals.values(),
            key=lambda x: x['conversions'],
            reverse=True
        )[:limit]

        # Sort by revenue
        top_by_revenue = sorted(
            campaign_totals.values(),
            key=lambda x: x['revenue'],
            reverse=True
        )[:limit]

        return {
            'top_by_conversions': top_by_conversions,
            'top_by_revenue': top_by_revenue
        }

    def _get_top_creatives(self, metrics: List[DailyMetrics], limit: int = 5) -> Dict:
        """Get top creatives by performance."""
        creative_totals = {}

        for m in metrics:
            if m.creative_id not in creative_totals:
                creative_totals[m.creative_id] = {
                    'creative_id': str(m.creative_id),
                    'creative_name': m.creative.name if m.creative else 'Unknown',
                    'conversions': 0,
                    'ctr': 0,
                    'impressions': 0,
                    'clicks': 0
                }
            creative_totals[m.creative_id]['conversions'] += m.conversions
            creative_totals[m.creative_id]['impressions'] += m.impressions
            creative_totals[m.creative_id]['clicks'] += m.clicks

        # Calculate CTR for each
        for creative in creative_totals.values():
            if creative['impressions'] > 0:
                creative['ctr'] = (creative['clicks'] / creative['impressions']) * 100

        # Sort by conversions
        top_creatives = sorted(
            creative_totals.values(),
            key=lambda x: x['conversions'],
            reverse=True
        )[:limit]

        return {'top_creatives': top_creatives}

    def _get_underperformers(self, metrics: List[DailyMetrics], threshold_ctr: float = 0.5) -> List[Dict]:
        """Identify underperforming campaigns (low CTR, high spend, low conversions)."""
        campaign_performance = {}

        for m in metrics:
            if m.campaign_id not in campaign_performance:
                campaign_performance[m.campaign_id] = {
                    'campaign_id': str(m.campaign_id),
                    'campaign_name': m.campaign.name if m.campaign else 'Unknown',
                    'total_spend': 0,
                    'total_conversions': 0,
                    'total_impressions': 0,
                    'total_clicks': 0
                }
            campaign_performance[m.campaign_id]['total_spend'] += float(m.spend)
            campaign_performance[m.campaign_id]['total_conversions'] += m.conversions
            campaign_performance[m.campaign_id]['total_impressions'] += m.impressions
            campaign_performance[m.campaign_id]['total_clicks'] += m.clicks

        underperformers = []
        for campaign in campaign_performance.values():
            ctr = (campaign['total_clicks'] / campaign['total_impressions'] * 100) if campaign['total_impressions'] > 0 else 0

            # Criteria: CTR < threshold, spend > $100, conversions < 5
            if ctr < threshold_ctr and campaign['total_spend'] > 100 and campaign['total_conversions'] < 5:
                underperformers.append({
                    'campaign_name': campaign['campaign_name'],
                    'ctr': round(ctr, 2),
                    'spend': round(campaign['total_spend'], 2),
                    'conversions': campaign['total_conversions'],
                    'reason': 'Low CTR and conversions with significant spend'
                })

        return underperformers[:5]  # Top 5 underperformers
```

### **5.15 CPM Calculator (`app/metrics/calculator.py`)**

```python
from decimal import Decimal

class MetricsCalculator:
    @staticmethod
    def calculate_spend(impressions: int, cpm: Decimal) -> Decimal:
        """Calculate spend using CPM formula: (impressions / 1000) * CPM"""
        return (Decimal(impressions) / Decimal(1000)) * cpm

    @staticmethod
    def calculate_ctr(clicks: int, impressions: int) -> Decimal:
        """Calculate CTR: (clicks / impressions) * 100"""
        if impressions == 0:
            return Decimal(0)
        return (Decimal(clicks) / Decimal(impressions)) * Decimal(100)

    @staticmethod
    def calculate_cpc(spend: Decimal, clicks: int) -> Decimal:
        """Calculate CPC: spend / clicks"""
        if clicks == 0:
            return Decimal(0)
        return spend / Decimal(clicks)

    @staticmethod
    def calculate_cpa(spend: Decimal, conversions: int) -> Decimal:
        """Calculate CPA: spend / conversions"""
        if conversions == 0:
            return Decimal(0)
        return spend / Decimal(conversions)

    @staticmethod
    def calculate_roas(revenue: Decimal, spend: Decimal) -> Decimal:
        """Calculate ROAS: (revenue / spend) * 100"""
        if spend == 0:
            return Decimal(0)
        return (revenue / spend) * Decimal(100)
```

---

## **Module 10: ETL Shared Components**

### **5.15 Staging Service (`app/etl/staging.py`)**

```python
from sqlalchemy.orm import Session
from app.models import StagingMediaRaw
from typing import List, Dict
import json

class StagingService:
    def __init__(self, db: Session):
        self.db = db

    def load_to_staging(self, records: List[Dict], client_id: str, source: str, ingestion_run_id: str):
        """Load parsed records to staging table."""
        staging_records = []

        for record in records:
            staging_record = StagingMediaRaw(
                ingestion_run_id=ingestion_run_id,
                client_id=client_id,
                source=source,
                date=record.get('Date'),
                campaign_name=record.get('Campaign') or record.get('Campaign Name'),
                strategy_name=record.get('Strategy') or record.get('Ad Set Name'),
                placement_name=record.get('Placement') or record.get('Ad Name'),
                creative_name=record.get('Creative') or record.get('Ad Name'),
                impressions=record.get('Impressions', 0),
                clicks=record.get('Clicks', 0),
                ctr=record.get('CTR', 0),
                conversions=record.get('Conversions', 0),
                conversion_revenue=record.get('Conversion Revenue') or record.get('Revenue', 0),
                raw_data=json.dumps(record)
            )
            staging_records.append(staging_record)

        self.db.bulk_save_objects(staging_records)
        self.db.commit()
```

### **5.16 Transformer Service (`app/etl/transformer.py`)**

```python
from sqlalchemy.orm import Session
from app.models import StagingMediaRaw, Campaign, Strategy, Placement, Creative
from app.clients.service import ClientService

class TransformerService:
    def __init__(self, db: Session):
        self.db = db

    def process_staging(self, ingestion_run_id: str, client_id: str):
        """Transform staging data and create hierarchy entities."""
        staging_records = self.db.query(StagingMediaRaw) \
            .filter(StagingMediaRaw.ingestion_run_id == ingestion_run_id) \
            .all()

        for record in staging_records:
            # Get or create campaign
            campaign = self.db.query(Campaign).filter(
                Campaign.client_id == client_id,
                Campaign.name == record.campaign_name,
                Campaign.source == record.source
            ).first()

            if not campaign:
                campaign = Campaign(
                    client_id=client_id,
                    name=record.campaign_name,
                    source=record.source
                )
                self.db.add(campaign)
                self.db.flush()

            # Get or create strategy
            strategy = self.db.query(Strategy).filter(
                Strategy.campaign_id == campaign.id,
                Strategy.name == record.strategy_name
            ).first()

            if not strategy:
                strategy = Strategy(
                    campaign_id=campaign.id,
                    name=record.strategy_name
                )
                self.db.add(strategy)
                self.db.flush()

            # Get or create placement
            placement = self.db.query(Placement).filter(
                Placement.strategy_id == strategy.id,
                Placement.name == record.placement_name
            ).first()

            if not placement:
                placement = Placement(
                    strategy_id=strategy.id,
                    name=record.placement_name
                )
                self.db.add(placement)
                self.db.flush()

            # Get or create creative
            creative = self.db.query(Creative).filter(
                Creative.placement_id == placement.id,
                Creative.name == record.creative_name
            ).first()

            if not creative:
                creative = Creative(
                    placement_id=placement.id,
                    name=record.creative_name
                )
                self.db.add(creative)
                self.db.flush()

            # Update staging record with IDs
            record.campaign_id = campaign.id
            record.strategy_id = strategy.id
            record.placement_id = placement.id
            record.creative_id = creative.id

        self.db.commit()
```

### **5.17 Loader Service (`app/etl/loader.py`)**

```python
from sqlalchemy.orm import Session
from app.models import StagingMediaRaw, DailyMetrics
from app.metrics.calculator import MetricsCalculator
from app.clients.service import ClientService
from decimal import Decimal

class LoaderService:
    def __init__(self, db: Session):
        self.db = db
        self.calculator = MetricsCalculator()

    def load_daily_metrics(self, ingestion_run_id: str):
        """Load staging data to daily_metrics with CPM calculations."""
        staging_records = self.db.query(StagingMediaRaw) \
            .filter(StagingMediaRaw.ingestion_run_id == ingestion_run_id) \
            .all()

        for record in staging_records:
            # Get client CPM
            cpm = Decimal(ClientService.get_current_cpm(self.db, record.client_id))

            # Calculate metrics
            spend = self.calculator.calculate_spend(record.impressions, cpm)
            ctr = self.calculator.calculate_ctr(record.clicks, record.impressions)
            cpc = self.calculator.calculate_cpc(spend, record.clicks)
            cpa = self.calculator.calculate_cpa(spend, record.conversions)
            roas = self.calculator.calculate_roas(Decimal(record.conversion_revenue), spend)

            # Create or update daily metric
            metric = DailyMetrics(
                client_id=record.client_id,
                date=record.date,
                campaign_id=record.campaign_id,
                strategy_id=record.strategy_id,
                placement_id=record.placement_id,
                creative_id=record.creative_id,
                source=record.source,
                impressions=record.impressions,
                clicks=record.clicks,
                conversions=record.conversions,
                conversion_revenue=Decimal(record.conversion_revenue),
                spend=spend,
                ctr=ctr,
                cpc=cpc,
                cpa=cpa,
                roas=roas
            )

            self.db.merge(metric)  # Upsert

        self.db.commit()
```

---

# **6. CODE TEMPLATES**

## **6.1 Dashboard API Response Schemas**

### **Dashboard Overview Schema (`app/dashboard/schemas.py`)**

```python
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import date
from decimal import Decimal

class DashboardSummary(BaseModel):
    \"\"\"Summary metrics for dashboard overview.\"\"\"
    impressions: int
    clicks: int
    ctr: float
    conversions: int
    conversion_revenue: Decimal
    spend: Decimal
    cpc: Decimal
    cpa: Decimal
    roas: Decimal
    date_range: Dict[str, date]

    class Config:
        orm_mode = True

class CampaignPerformance(BaseModel):
    \"\"\"Campaign performance data.\"\"\"
    campaign_id: str
    campaign_name: str
    source: str
    impressions: int
    clicks: int
    conversions: int
    spend: Decimal
    revenue: Decimal
    ctr: float
    cpc: Decimal
    cpa: Decimal
    roas: Decimal

class StrategyPerformance(BaseModel):
    \"\"\"Strategy performance data.\"\"\"
    strategy_id: str
    strategy_name: str
    campaign_name: str
    impressions: int
    clicks: int
    conversions: int
    spend: Decimal
    ctr: float

class CreativePerformance(BaseModel):
    \"\"\"Creative performance data.\"\"\"
    creative_id: str
    creative_name: str
    preview_url: Optional[str]
    impressions: int
    clicks: int
    conversions: int
    ctr: float
    spend: Decimal

class WeeklySummaryResponse(BaseModel):
    \"\"\"Weekly summary with deltas.\"\"\"
    week_start: date
    week_end: date
    impressions: int
    clicks: int
    conversions: int
    revenue: Decimal
    spend: Decimal
    ctr: float
    cpc: Decimal
    cpa: Decimal
    roas: Decimal
    top_campaigns: List[Dict]
    top_creatives: List[Dict]
    underperformers: List[Dict]
    deltas: Optional[Dict]  # Week-over-week changes

    class Config:
        orm_mode = True

class DashboardResponse(BaseModel):
    \"\"\"Complete dashboard data structure.\"\"\"
    summary: DashboardSummary
    campaigns: List[CampaignPerformance]
    strategies: List[StrategyPerformance]
    placements: List[Dict]
    creatives: List[CreativePerformance]
    weekly_summary: Optional[WeeklySummaryResponse]
    monthly_summary: Optional[Dict]
```

---

## **6.2 FastAPI Main App (`app/main.py`)**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging import setup_logging
from app.core.config import settings
from app.api.v1.api import api_router
from app.jobs.scheduler import start_scheduler

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-source marketing dashboard API"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")

# Start scheduler on startup
@app.on_event("startup")
async def startup_event():
    start_scheduler()

@app.get("/")
async def root():
    return {"message": "Dashboard API is running", "version": settings.APP_VERSION}
```

## **6.2 API Router Aggregator (`app/api/v1/api.py`)**

```python
from fastapi import APIRouter
from app.auth.router import router as auth_router
from app.clients.router import router as clients_router
from app.campaigns.router import router as campaigns_router
from app.facebook.router import router as facebook_router
from app.metrics.router import router as metrics_router
from app.dashboard.router import router as dashboard_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(clients_router, prefix="/clients", tags=["Clients"])
api_router.include_router(campaigns_router, prefix="/campaigns", tags=["Campaigns"])
api_router.include_router(facebook_router, prefix="/facebook", tags=["Facebook"])
api_router.include_router(metrics_router, prefix="/metrics", tags=["Metrics"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
```

## **6.3 Scheduler Setup (`app/jobs/scheduler.py`)**

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.jobs.daily_ingestion import run_all_sources_ingestion
from app.jobs.summaries import run_weekly_summary, run_monthly_summary
from app.core.config import settings
from app.core.logging import logger

scheduler = AsyncIOScheduler()

def start_scheduler():
    # Surfside daily ingestion (5 AM)
    scheduler.add_job(
        run_all_sources_ingestion,
        'cron',
        hour=5,
        minute=0,
        id='daily_ingestion'
    )

    # Weekly summary (Sunday 7 AM)
    scheduler.add_job(
        run_weekly_summary,
        'cron',
        day_of_week='sun',
        hour=7,
        minute=0,
        id='weekly_summary'
    )

    # Monthly summary (1st of month, 8 AM)
    scheduler.add_job(
        run_monthly_summary,
        'cron',
        day=1,
        hour=8,
        minute=0,
        id='monthly_summary'
    )

    scheduler.start()
    logger.info("Scheduler started with all jobs")
```

## **6.4 Daily Ingestion Job (`app/jobs/daily_ingestion.py`)**

```python
import asyncio
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.surfside.etl import SurfsideETL
from app.vibe.etl import VibeETL
from app.clients.service import ClientService
from app.core.logging import logger
from datetime import datetime, timedelta

async def run_all_sources_ingestion():
    """Run ingestion for all 3 sources for all active clients."""
    db = SessionLocal()
    target_date = datetime.now() - timedelta(days=1)  # Yesterday's data

    try:
        # Get all active clients
        clients = ClientService.get_all_active_clients(db)
        logger.info(f"Running daily ingestion for {len(clients)} clients")

        for client in clients:
            logger.info(f"Processing client: {client.name}")

            # Run all 3 sources in parallel
            await asyncio.gather(
                run_surfside(db, client.id, target_date),
                run_vibe(db, client.id, target_date),
                # Facebook is manual upload only, no scheduled job
            )

        logger.info("Daily ingestion completed for all sources")

    except Exception as e:
        logger.error(f"Daily ingestion failed: {e}")
    finally:
        db.close()

async def run_surfside(db: Session, client_id: str, target_date: datetime):
    try:
        etl = SurfsideETL(db)
        etl.run_daily_ingestion(client_id, target_date)
        logger.info(f"Surfside ingestion completed for client {client_id}")
    except Exception as e:
        logger.error(f"Surfside ingestion failed for client {client_id}: {e}")

async def run_vibe(db: Session, client_id: str, target_date: datetime):
    try:
        etl = VibeETL(db)
        advertiser_id = get_vibe_advertiser_id(db, client_id)  # Implement this
        await etl.run_daily_ingestion(client_id, target_date, advertiser_id)
        logger.info(f"Vibe ingestion completed for client {client_id}")
    except Exception as e:
        logger.error(f"Vibe ingestion failed for client {client_id}: {e}")
```

---

# **7. TESTING STRATEGY**

## **7.1 Unit Tests**

Test each module independently with mocked dependencies:

```python
# tests/test_surfside/test_parser.py
import pytest
from app.surfside.parser import SurfsideParser

def test_parse_csv_file():
    parser = SurfsideParser()
    records = parser.parse_file("tests/fixtures/surfside_sample.csv")
    assert len(records) > 0
    assert 'Date' in records[0]
    assert 'Impressions' in records[0]

def test_parse_missing_columns():
    parser = SurfsideParser()
    with pytest.raises(ValueError, match="Missing columns"):
        parser.parse_file("tests/fixtures/invalid.csv")
```

## **7.2 Integration Tests**

Test ETL pipelines end-to-end with test database:

```python
# tests/test_etl/test_surfside_etl.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.surfside.etl import SurfsideETL
from app.core.database import Base

@pytest.fixture
def db_session():
    engine = create_engine("postgresql://test:test@localhost/test_db")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

@pytest.mark.asyncio
async def test_surfside_etl_full_pipeline(db_session):
    etl = SurfsideETL(db_session)
    # Mock S3 service to return test file
    # Run ingestion
    # Assert records in daily_metrics
    pass
```

## **7.3 API Tests**

Test API endpoints with `httpx.AsyncClient`:

```python
# tests/test_api/test_facebook_upload.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_upload_facebook_file():
    async with AsyncClient(app=app, base_url="http://test") as client:
        files = {"file": ("facebook.csv", open("tests/fixtures/facebook.csv", "rb"))}
        response = await client.post("/api/v1/facebook/upload", files=files)
        assert response.status_code == 200
        assert response.json()["status"] == "success"
```

---

# **8. DEPLOYMENT CHECKLIST**

## **8.1 Pre-Deployment**

- [ ] Run `database_schema.sql` on production PostgreSQL
- [ ] Configure environment variables in `.env` (AWS keys, DB URL, JWT secret)
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run migrations: `alembic upgrade head`
- [ ] Run test suite: `pytest`
- [ ] Configure CORS for production domains

## **8.2 Deployment**

- [ ] Deploy FastAPI app (Docker/Kubernetes/EC2)
- [ ] Setup reverse proxy (Nginx)
- [ ] Configure SSL certificates
- [ ] Start scheduler process
- [ ] Setup monitoring (Sentry, CloudWatch, etc.)

## **8.3 Post-Deployment**

- [ ] Create admin user
- [ ] Test authentication endpoints
- [ ] Verify S3 bucket access
- [ ] Test Vibe API connectivity
- [ ] Test Facebook file upload
- [ ] Monitor first scheduled ingestion
- [ ] Setup alerting for failed jobs
- [ ] Configure SMTP for email alerts
- [ ] Test email notifications
- [ ] Verify PDF/CSV exports
- [ ] Test historical backfill functionality

---

## **9. DEPENDENCIES AND REQUIREMENTS**

### **9.1 Python Dependencies (`requirements.txt`)**

```
# FastAPI and Server
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.1.1

# AWS S3
boto3==1.29.7
botocore==1.32.7

# HTTP Requests (Vibe API)
httpx==0.25.2
aiohttp==3.9.1

# Data Processing
pandas==2.1.3
openpyxl==3.1.2
python-dateutil==2.8.2

# Validation
pydantic==2.5.2
pydantic-settings==2.1.0
email-validator==2.1.0

# Scheduling
apscheduler==3.10.4

# Export Functionality
reportlab==4.0.7

# Email
aiosmtplib==3.0.1

# Utilities
python-dotenv==1.0.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2
faker==20.1.0

# Monitoring and Logging
sentry-sdk==1.38.0
```

### **9.2 Environment Variables (`.env.example`)**

```bash
# Application
APP_NAME="Dashboard API"
APP_VERSION="1.0.0"
DEBUG=False
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dashboard_db

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS S3 (Surfside)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
S3_PREFIX=surfside/

# Vibe API
VIBE_API_BASE_URL=https://api.vibe.co
VIBE_API_KEY=your-vibe-api-key
VIBE_ADVERTISER_ID=your-advertiser-id
VIBE_RATE_LIMIT=15

# Facebook Upload
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=52428800

# Email Alerts (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=alerts@yourdomain.com
ALERT_EMAIL=stephen@yourdomain.com

# Scheduler
SURFSIDE_CRON=0 5 * * *
VIBE_CRON=0 6 * * *
SUMMARY_CRON=0 7 * * *

# CORS
CORS_ORIGINS=["http://localhost:3000","https://yourdomain.com"]

# Monitoring (Optional)
SENTRY_DSN=your-sentry-dsn
```

---

## **10. ADDITIONAL IMPLEMENTATION NOTES**

### **10.1 Facebook Field Mapping**

Facebook CSV structure differs from Surfside/Vibe:

- `Campaign Name` → Campaign
- `Ad Set Name` → Strategy
- `Ad Name` → Both Placement AND Creative (use same value)

**Implementation in Facebook Parser:**

```python
def parse_facebook_record(record):
    return {
        'campaign_name': record['Campaign Name'],
        'strategy_name': record['Ad Set Name'],
        'placement_name': record['Ad Name'],  # Ad name as placement
        'creative_name': record['Ad Name'],   # Ad name as creative
        # ... other fields
    }
```

### **10.2 Data Validation Rules**

**Validation Logic in Parsers:**

```python
class DataValidator:
    @staticmethod
    def validate_metrics_record(record: Dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate a single metrics record. Returns (is_valid, errors)"""
        errors = []

        # Required fields check
        required_fields = ['campaign_name', 'date', 'impressions', 'clicks', 'spend']
        for field in required_fields:
            if not record.get(field):
                errors.append(f"Missing required field: {field}")

        # Numeric validation
        numeric_fields = ['impressions', 'clicks', 'spend', 'conversions', 'revenue']
        for field in numeric_fields:
            if field in record and record[field] is not None:
                try:
                    value = float(record[field])
                    if value < 0:
                        errors.append(f"{field} cannot be negative: {value}")
                except (ValueError, TypeError):
                    errors.append(f"{field} must be numeric: {record[field]}")

        # Date validation
        if 'date' in record:
            try:
                from datetime import datetime
                date_obj = datetime.strptime(str(record['date']), '%Y-%m-%d')
                # Check date is not in future
                if date_obj.date() > datetime.now().date():
                    errors.append(f"Date cannot be in future: {record['date']}")
            except ValueError:
                errors.append(f"Invalid date format: {record['date']}")

        # Business logic validation
        if record.get('clicks', 0) > record.get('impressions', 0):
            errors.append("Clicks cannot exceed impressions")

        if record.get('conversions', 0) > record.get('clicks', 0):
            errors.append("Conversions cannot exceed clicks")

        # String length limits
        if len(record.get('campaign_name', '')) > 255:
            errors.append("Campaign name exceeds 255 characters")

        return (len(errors) == 0, errors)

    @staticmethod
    def validate_batch(records: list[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate batch of records and return summary"""
        total = len(records)
        valid_records = []
        invalid_records = []

        for idx, record in enumerate(records):
            is_valid, errors = DataValidator.validate_metrics_record(record)
            if is_valid:
                valid_records.append(record)
            else:
                invalid_records.append({
                    'row': idx + 1,
                    'record': record,
                    'errors': errors
                })

        return {
            'total': total,
            'valid': len(valid_records),
            'invalid': len(invalid_records),
            'valid_records': valid_records,
            'invalid_records': invalid_records[:100],  # Limit for logging
            'validation_rate': len(valid_records) / total if total > 0 else 0
        }
```

### **10.3 Retry Mechanisms for API Failures**

**Exponential Backoff with Retry Decorator:**

```python
import asyncio
from functools import wraps
from typing import TypeVar, Callable, Any
import httpx

T = TypeVar('T')

def async_retry(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    exceptions: tuple = (httpx.HTTPError, asyncio.TimeoutError)
):
    """Decorator for retrying async functions with exponential backoff"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise

                    wait_time = backoff_factor ** attempt
                    logger.warning(
                        f"{func.__name__} attempt {attempt} failed: {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)

            raise last_exception

        return wrapper
    return decorator

# Usage in VibeAPIClient
class VibeAPIClient:
    @async_retry(max_attempts=3, backoff_factor=2.0)
    async def create_report(self, start_date: str, end_date: str, advertiser_id: str):
        """Create report with automatic retry on failure"""
        # ... implementation

    @async_retry(max_attempts=5, backoff_factor=1.5)
    async def check_report_status(self, report_id: str):
        """Check status with retry"""
        # ... implementation

# Usage in S3Service
class S3Service:
    @async_retry(max_attempts=3, backoff_factor=2.0, exceptions=(Exception,))
    async def download_file(self, key: str) -> bytes:
        """Download S3 file with retry"""
        # ... implementation
```

**Circuit Breaker Pattern (Advanced):**

```python
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Too many failures, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    async def call(self, func: Callable, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(f"Circuit breaker opened after {self.failure_count} failures")

# Usage
vibe_circuit = CircuitBreaker(failure_threshold=5, timeout=300)

async def fetch_vibe_data_with_circuit_breaker():
    return await vibe_circuit.call(vibe_client.create_report, start_date, end_date, advertiser_id)
```

### **10.4 Missing File Scenarios Handling**

**Strategy for handling missing Surfside files:**

```python
# In SurfsideETL
class SurfsideETL:
    async def run_daily_ingestion(self, target_date: date):
        try:
            file_data = await self.s3_service.get_file_for_date(target_date)
        except FileNotFoundError:
            logger.warning(f"Surfside file not found for {target_date}")

            # Log missing file
            log = IngestionLog(
                source='surfside',
                status='missing_file',
                start_time=datetime.now(),
                end_time=datetime.now(),
                error_message=f"File not found in S3 for date {target_date}"
            )
            self.db.add(log)
            self.db.commit()

            # Send alert email
            await self.email_service.send_missing_file_alert(
                source='Surfside',
                date=target_date,
                s3_bucket=settings.S3_BUCKET_NAME,
                s3_prefix=settings.S3_PREFIX
            )

            # Mark in dashboard as "No Data Available"
            return None

        # Continue with normal processing
        # ...

# In S3Service
class S3Service:
    async def get_file_for_date(self, target_date: date) -> bytes:
        """Get file for specific date, raise FileNotFoundError if missing"""
        key = self._build_key(target_date)

        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return response['Body'].read()
        except self.s3_client.exceptions.NoSuchKey:
            raise FileNotFoundError(f"S3 file not found: {key}")
        except Exception as e:
            logger.error(f"Error downloading S3 file {key}: {e}")
            raise
```

**Dashboard handling:**

```python
# Frontend should display gaps gracefully
# Example response for date range with missing data:
{
    "date_range": ["2024-01-01", "2024-01-07"],
    "data": [
        {"date": "2024-01-01", "metrics": {...}},
        {"date": "2024-01-02", "metrics": {...}},
        {"date": "2024-01-03", "status": "no_data", "reason": "File not found"},
        {"date": "2024-01-04", "metrics": {...}},
    ]
}
```

### **10.5 Audit Logging for User Actions**

**Database Schema Addition (add to database_schema.sql):**

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

COMMENT ON TABLE audit_logs IS 'Tracks all user actions for security and compliance';
```

**Audit Service Implementation:**

```python
# app/core/audit.py
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
from app.models import AuditLog, User
from fastapi import Request

class AuditService:
    def __init__(self, db: Session):
        self.db = db

    async def log_action(
        self,
        user_id: str,
        action: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None
    ):
        """Log user action to audit trail"""
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=request.client.host if request else None,
            user_agent=request.headers.get('user-agent') if request else None
        )
        self.db.add(audit_log)
        self.db.commit()

    def get_user_activity(self, user_id: str, limit: int = 100) -> list:
        """Get recent activity for a user"""
        return self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).order_by(
            AuditLog.created_at.desc()
        ).limit(limit).all()

    def get_entity_history(self, entity_type: str, entity_id: str) -> list:
        """Get all changes to a specific entity"""
        return self.db.query(AuditLog).filter(
            AuditLog.entity_type == entity_type,
            AuditLog.entity_id == entity_id
        ).order_by(
            AuditLog.created_at.desc()
        ).all()

# Usage in routers
from fastapi import Depends, Request
from app.core.audit import AuditService

@router.post("/clients")
async def create_client(
    client_data: ClientCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Create client
    client = ClientService(db).create_client(client_data)

    # Log action
    audit = AuditService(db)
    await audit.log_action(
        user_id=current_user.id,
        action="create_client",
        entity_type="client",
        entity_id=client.id,
        new_values=client_data.dict(),
        request=request
    )

    return client

@router.put("/clients/{client_id}")
async def update_client(
    client_id: str,
    client_data: ClientUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get old state
    old_client = db.query(Client).filter(Client.id == client_id).first()
    old_values = {'name': old_client.name, 'is_active': old_client.is_active}

    # Update client
    updated_client = ClientService(db).update_client(client_id, client_data)

    # Log action
    audit = AuditService(db)
    await audit.log_action(
        user_id=current_user.id,
        action="update_client",
        entity_type="client",
        entity_id=client_id,
        old_values=old_values,
        new_values=client_data.dict(exclude_unset=True),
        request=request
    )

    return updated_client

# Admin audit log viewer
@router.get("/admin/audit-logs")
async def get_audit_logs(
    user_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    query = db.query(AuditLog)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    return query.order_by(AuditLog.created_at.desc()).limit(limit).all()
```

### \*\*10.6 S3 File Pattern Configuration

        # String length limits
        if len(record.get('campaign_name', '')) > 255:
            errors.append("Campaign name exceeds 255 characters")

        return (len(errors) == 0, errors)

    @staticmethod
    def validate_batch(records: list[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate batch of records and return summary"""
        total = len(records)
        valid_records = []
        invalid_records = []

        for idx, record in enumerate(records):
            is_valid, errors = DataValidator.validate_metrics_record(record)
            if is_valid:
                valid_records.append(record)
            else:
                invalid_records.append({
                    'row': idx + 1,
                    'record': record,
                    'errors': errors
                })

        return {
            'total': total,
            'valid': len(valid_records),
            'invalid': len(invalid_records),
            'valid_records': valid_records,
            'invalid_records': invalid_records[:100],  # Limit for logging
            'validation_rate': len(valid_records) / total if total > 0 else 0
        }

````

### **10.3 S3 File Pattern Configuration**

Support flexible file naming patterns via configuration:

```python
# In config.py
S3_FILE_PATTERN: str = "media-report-{date}.csv"  # {date} = YYYY-MM-DD

# In S3Service
def get_file_for_date(self, target_date):
    pattern = settings.S3_FILE_PATTERN.replace('{date}', target_date.strftime('%Y-%m-%d'))
    # Or support regex patterns
    # pattern = r'.*' + target_date.strftime('%Y-%m-%d') + r'.*\.csv$'
````

### **10.3 Performance Optimization for 50k+ Rows**

**Batch Inserts:**

```python
# Use bulk operations
db.bulk_insert_mappings(DailyMetrics, records, batch_size=1000)
```

**Database Connection Pooling:**

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

**Indexing Strategy:**

- Composite index on (client_id, date) for dashboard queries
- Index on source column for filtering
- Partial indexes for active clients only

### **10.8 Data Retention Policy**

Consider implementing data archival:

- Keep last 13 months in hot storage (daily_metrics)
- Archive older data to cold storage (S3/data warehouse)
- Summaries retained indefinitely
- Audit logs: Retain 2 years, then archive to S3
- Ingestion logs: Retain 90 days for recent troubleshooting

---

## **END OF IMPLEMENTATION GUIDE**

## **1.3 Core Features**

✅ **Data Ingestion:**

- Daily automated S3 CSV ingestion
- Historical data backfill
- Data validation and error handling
- Staging and transformation pipeline

✅ **Data Processing:**

- Client-specific CPM calculation
- Derived metrics (CPC, CPA, ROAS, CTR)
- Weekly and monthly summaries
- Campaign hierarchy (Campaign → Strategy → Placement → Creative)

✅ **User Management:**

- Admin authentication
- Client authentication
- Role-based access control
- Password management

✅ **Admin Portal:**

- Client management (CRUD)
- CPM configuration
- Ingestion log viewing
- Error alert management

---

## **2.2 Entity Relationship Summary**

```
users (1) ─────────> (1) clients
                           │
                           ├─────> (1:N) client_settings
                           │
                           ├─────> (1:N) campaigns
                           │              │
                           │              └─────> (1:N) strategies
                           │                            │
                           │                            ├─────> (1:N) placements
                           │                            │              │
                           │                            │              └─────> (1:N) creatives
                           │                            │
                           │                            └─────> (1:N) daily_metrics
                           │
                           ├─────> (1:N) weekly_summaries
                           │
                           └─────> (1:N) monthly_summaries

Standalone Tables:
- staging_media_raw (temporary ingestion)
- ingestion_logs (audit trail)
```

---

# **3. ETL PIPELINE ARCHITECTURE**

## **3.1 ETL Overview**

```
┌─────────────────────────────────────────────────────────────────────┐
│                          ETL PIPELINE FLOW                           │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   S3 Bucket  │ (Stephen's bucket with daily CSV files)
└──────┬───────┘
       │
       │ ① EXTRACT
       ▼
┌──────────────────────┐
│  S3 Download Service │ - List files
│                      │ - Download latest file for date
│                      │ - Validate file exists
└──────┬───────────────┘
       │
       │ ② TRANSFORM
       ▼
┌──────────────────────┐
│   CSV Parser         │ - Parse CSV structure
│                      │ - Validate columns
│                      │ - Data type conversion
│                      │ - Handle nulls/errors
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Data Validator      │ - Check required fields
│                      │ - Validate data ranges
│                      │ - Detect duplicates
│                      │ - Business rules validation
└──────┬───────────────┘
       │
       │ ③ LOAD (Staging)
       ▼
┌──────────────────────┐
│  Staging Table       │ - Insert raw records
│  (staging_media_raw) │ - Tag with ingestion_run_id
└──────┬───────────────┘
       │
       │ ④ TRANSFORM (Normalization)
       ▼
┌──────────────────────┐
│  Entity Resolution   │ - Find/Create campaigns
│                      │ - Find/Create strategies
│                      │ - Find/Create placements
│                      │ - Find/Create creatives
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  CPM Calculation     │ - Fetch client CPM
│                      │ - Calculate spend
│                      │ - Calculate CPC, CPA, ROAS
│                      │ - Calculate CTR (if needed)
└──────┬───────────────┘
       │
       │ ⑤ LOAD (Production)
       ▼
┌──────────────────────┐
│  daily_metrics       │ - Insert/Update metrics
│                      │ - Atomic transaction
└──────┬───────────────┘
       │
       │ ⑥ CLEANUP & LOGGING
       ▼
┌──────────────────────┐
│  Post-Processing     │ - Archive staging data
│                      │ - Log success/failure
│                      │ - Send alerts if needed
│                      │ - Trigger summary jobs
└──────────────────────┘
```

## **3.2 Data Flow Specifications**

### **Extract Phase**

- **Input:** S3 bucket path, file naming pattern, target date
- **Process:**
  - Connect to S3 using boto3
  - List files matching pattern for target date
  - Download latest file
  - Verify file size > 0
- **Output:** Local CSV file or file stream
- **Error Handling:** File not found, connection issues, invalid file

### **Transform Phase**

- **Input:** CSV file
- **Process:**
  - Parse CSV headers
  - Validate expected columns exist
  - Row-by-row parsing
  - Data type conversion
  - Null handling
  - Calculate derived fields if needed
- **Output:** List of validated records
- **Error Handling:** Missing columns, invalid data types, malformed rows

### **Load Phase (Staging)**

- **Input:** Validated records
- **Process:**
  - Generate ingestion_run_id
  - Batch insert into staging_media_raw
  - Link to client_id
- **Output:** Staging records with IDs
- **Error Handling:** Database connection, constraint violations

### **Transform Phase (Normalization)**

- **Input:** Staging records
- **Process:**
  - For each record:
    - Find or create campaign by (client_id, campaign_name)
    - Find or create strategy by (campaign_id, strategy_name)
    - Find or create placement by (strategy_id, placement_name)
    - Find or create creative by (placement_id, creative_name)
  - Fetch client CPM from client_settings
  - Calculate metrics:
    - spend = (impressions / 1000) \* client_cpm
    - ctr = clicks / impressions (if impressions > 0)
    - cpc = spend / clicks (if clicks > 0)
    - cpa = spend / conversions (if conversions > 0)
    - roas = conversion_revenue / spend (if spend > 0)
- **Output:** Normalized records with all IDs and calculated metrics
- **Error Handling:** Missing client CPM, calculation errors

### **Load Phase (Production)**

- **Input:** Normalized records
- **Process:**
  - Upsert into daily_metrics (INSERT ... ON CONFLICT UPDATE)
  - Use unique constraint on (client_id, date, campaign_id, strategy_id, placement_id, creative_id)
- **Output:** Persisted metrics
- **Error Handling:** Constraint violations, transaction rollback

---

# **4. DATA SOURCE INTEGRATION DETAILS**

## **4.1 S3 Integration (Surfside - Primary V1)**

### **Configuration Required**

```python
# Environment Variables
AWS_ACCESS_KEY_ID=<provided_by_stephen>
AWS_SECRET_ACCESS_KEY=<provided_by_stephen>
AWS_REGION=us-east-1
S3_BUCKET_NAME=<stephen_bucket_name>
S3_FOLDER_PREFIX=media-reports/
```

### **File Naming Convention**

```
Expected formats:
- media-report-YYYY-MM-DD.csv
- client-media-YYYYMMDD.csv
- Or pattern provided by Stephen
```

### **CSV Structure (Expected)**

| Column Name        | Data Type | Required | Notes                                  |
| ------------------ | --------- | -------- | -------------------------------------- |
| date               | DATE      | Yes      | YYYY-MM-DD format                      |
| campaign_name      | VARCHAR   | Yes      | Campaign identifier                    |
| strategy_name      | VARCHAR   | Yes      | Strategy identifier                    |
| placement_name     | VARCHAR   | Yes      | Placement identifier                   |
| creative_name      | VARCHAR   | Yes      | Creative identifier                    |
| impressions        | BIGINT    | Yes      | Number of impressions                  |
| clicks             | BIGINT    | Yes      | Number of clicks                       |
| ctr                | DECIMAL   | No       | Click-through rate (can be calculated) |
| conversions        | BIGINT    | Yes      | Number of conversions                  |
| conversion_revenue | DECIMAL   | Yes      | Revenue from conversions               |

### **S3 Service Implementation Structure**

```
app/services/s3_service.py
│
├── S3Service class
│   ├── connect()
│   ├── list_files(prefix, date)
│   ├── download_file(file_key)
│   ├── get_latest_file(date)
│   └── upload_file() [for backups]
```

## **4.2 Vibe API Integration (Future Enhancement)**

### **API Configuration**

```python
VIBE_API_BASE_URL=https://clear-platform.vibe.co/rest/reporting/v1
VIBE_API_KEY=<test_key_provided>
VIBE_RATE_LIMIT=15  # requests per hour
```

### **Integration Flow**

1. Create async report via `/create_async_report`
2. Poll status via `/get_report_status` (every 10 seconds)
3. Download report when ready (CSV or JSON)
4. Parse and load into staging
5. Follow same normalization process

### **Service Structure**

```
app/services/vibe_service.py
│
├── VibeAPIClient class
│   ├── create_async_report()
│   ├── poll_report_status()
│   ├── download_report()
│   ├── parse_report()
│   └── handle_rate_limiting()
```

## **4.3 Facebook CSV Upload (Future Enhancement)**

### **Upload Flow**

1. User uploads CSV via admin/client portal
2. File validation (size, format, structure)
3. Parse CSV
4. Store in staging
5. Follow same normalization process

### **Service Structure**

```
app/services/facebook_service.py
│
├── FacebookUploadService class
│   ├── validate_file()
│   ├── parse_csv()
│   ├── save_to_staging()
│   └── trigger_processing()
```

---

# **5. CPM CALCULATION LOGIC**

## **5.1 Core Formula**

```python
# Primary Calculation
spend = (impressions / 1000) * client_cpm

# Derived Metrics
ctr = (clicks / impressions) if impressions > 0 else 0
cpc = (spend / clicks) if clicks > 0 else 0
cpa = (spend / conversions) if conversions > 0 else 0
roas = (conversion_revenue / spend) if spend > 0 else 0
```

## **5.2 Implementation Rules**

### **Division by Zero Handling**

```python
def safe_divide(numerator, denominator, default=0):
    """Safely divide two numbers, return default if denominator is zero."""
    if denominator == 0 or denominator is None:
        return default
    return numerator / denominator
```

### **Precision Rules**

- Store all decimals with high precision (DECIMAL(12,6))
- Round for display only (2 decimal places for currency, 3 for rates)
- Never round during calculations

### **CPM Lookup Logic**

```python
def get_client_cpm(client_id: UUID, effective_date: date = None) -> Decimal:
    """
    Fetch client CPM rate.
    If effective_date provided, get CPM active on that date.
    Otherwise, get latest CPM.
    """
    if effective_date:
        # Get CPM where effective_date <= target_date, order by effective_date DESC
        return query.filter(
            ClientSettings.client_id == client_id,
            ClientSettings.effective_date <= effective_date
        ).order_by(ClientSettings.effective_date.desc()).first().cpm
    else:
        # Get latest CPM
        return query.filter(
            ClientSettings.client_id == client_id
        ).order_by(ClientSettings.created_at.desc()).first().cpm
```

---

# **6. IMPLEMENTATION PHASES**

## **Phase 1: Foundation (Week 1)**

- ✅ Database schema creation
- ✅ Alembic migrations setup
- ✅ Core models (SQLAlchemy)
- ✅ Pydantic schemas
- ✅ Database connection and session management

## **Phase 2: Authentication & User Management (Week 1-2)**

- User authentication (JWT)
- Password hashing and validation
- Login/logout endpoints
- User CRUD operations
- Role-based access control

## **Phase 3: Client Management (Week 2)**

- Client CRUD endpoints
- Client settings management
- CPM configuration
- Admin portal backend

## **Phase 4: S3 Integration & ETL (Week 2-3)**

- S3 service implementation
- CSV parser
- Data validator
- Staging loader
- Entity resolution (campaigns, strategies, etc.)
- CPM calculation engine
- Daily metrics loader

## **Phase 5: Scheduled Jobs (Week 3)**

- Daily ingestion cron job
- Weekly summary generation
- Monthly summary generation
- Error notification system

## **Phase 6: API Endpoints (Week 3-4)**

- Dashboard data endpoints
- Campaign/strategy/placement/creative endpoints
- Metrics aggregation endpoints
- Export endpoints (CSV/PDF)
- Filter and sort logic

## **Phase 7: Testing (Week 4)**

- Unit tests for all services
- Integration tests for ETL pipeline
- API endpoint tests
- Data validation tests

## **Phase 8: Future Enhancements (Post-V1)**

- Vibe API integration
- Facebook upload functionality
- Advanced analytics
- Additional data sources

---

# **7. STEP-BY-STEP IMPLEMENTATION PLAN**

## **CHECKPOINT 1: Database Setup** ✅

### **Tasks:**

1. [ ] Review and understand complete schema
2. [ ] Create migration file with all tables
3. [ ] Run migration to create tables
4. [ ] Verify all tables created correctly
5. [ ] Test relationships and constraints
6. [ ] Create seed data for testing

**Files to Create:**

- `alembic/versions/001_initial_schema.py`
- `app/db/base.py` (import all models)
- `app/db/session.py` (database session factory)

**Verification:**

```sql
-- Check all tables exist
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';

-- Check relationships
SELECT * FROM information_schema.table_constraints
WHERE constraint_type = 'FOREIGN KEY';
```

---

## **CHECKPOINT 2: SQLAlchemy Models**

### **Tasks:**

1. [ ] Create User model
2. [ ] Create Client model
3. [ ] Create ClientSettings model
4. [ ] Create Campaign model
5. [ ] Create Strategy model
6. [ ] Create Placement model
7. [ ] Create Creative model
8. [ ] Create DailyMetrics model
9. [ ] Create WeeklySummary model
10. [ ] Create MonthlySummary model
11. [ ] Create StagingMediaRaw model
12. [ ] Create IngestionLog model

**Files to Create:**

- `app/models/user.py`
- `app/models/client.py`
- `app/models/client_settings.py`
- `app/models/campaign.py`
- `app/models/strategy.py`
- `app/models/placement.py`
- `app/models/creative.py`
- `app/models/daily_metrics.py`
- `app/models/weekly_summary.py`
- `app/models/monthly_summary.py`
- `app/models/staging.py`
- `app/models/ingestion_log.py`

**Model Template:**

```python
from sqlalchemy import Column, String, Integer, ForeignKey, DECIMAL, BigInteger, Date, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
import uuid

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    name = Column(String(255), nullable=False)
    # ... rest of columns

    # Relationships
    client = relationship("Client", back_populates="campaigns")
    strategies = relationship("Strategy", back_populates="campaign")
```

---

## **CHECKPOINT 3: Pydantic Schemas**

### **Tasks:**

1. [ ] Create request/response schemas for all models
2. [ ] Add validation rules
3. [ ] Create nested schemas for relationships

**Files to Create:**

- `app/schemas/user.py`
- `app/schemas/client.py`
- `app/schemas/campaign.py`
- `app/schemas/metrics.py`
- etc.

**Schema Template:**

```python
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal

class ClientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    status: str = Field(default="active", regex="^(active|disabled)$")

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = Field(None, regex="^(active|disabled)$")

class ClientResponse(ClientBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
```

---

## **CHECKPOINT 4: Core Configuration**

### **Tasks:**

1. [ ] Create settings configuration
2. [ ] Set up environment variables
3. [ ] Configure database connection
4. [ ] Set up logging

**Files to Create:**

- `app/core/config.py`
- `app/core/security.py`
- `app/core/logging.py`

**config.py Template:**

```python
from pydantic import BaseSettings, PostgresDsn, Field
from typing import List

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Dashboard Application"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: PostgresDsn

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # AWS S3
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str
    S3_FOLDER_PREFIX: str = "media-reports/"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

---

## **CHECKPOINT 5: Authentication System**

### **Tasks:**

1. [ ] Implement password hashing
2. [ ] Create JWT token generation
3. [ ] Create JWT token verification
4. [ ] Implement login endpoint
5. [ ] Implement logout endpoint
6. [ ] Create authentication dependency
7. [ ] Role-based access control

**Files to Create:**

- `app/core/security.py` (password hashing, JWT)
- `app/api/v1/endpoints/auth.py` (auth endpoints)
- `app/core/deps.py` (dependencies for auth)

**Key Functions:**

```python
# Password hashing
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# JWT tokens
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> dict:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    return payload

# Authentication dependency
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user
```

---

## **CHECKPOINT 6: Client Management API**

### **Tasks:**

1. [ ] Create client CRUD service
2. [ ] Create client endpoints
3. [ ] Create client settings endpoints
4. [ ] Add admin-only access control

**Files to Create:**

- `app/services/client_service.py`
- `app/api/v1/endpoints/clients.py`

**Endpoints:**

```
POST   /api/v1/clients              - Create client (admin only)
GET    /api/v1/clients              - List all clients (admin only)
GET    /api/v1/clients/{client_id}  - Get client details
PUT    /api/v1/clients/{client_id}  - Update client (admin only)
DELETE /api/v1/clients/{client_id}  - Delete client (admin only)
POST   /api/v1/clients/{client_id}/settings - Set CPM
GET    /api/v1/clients/{client_id}/settings - Get settings
```

---

## **CHECKPOINT 7: S3 Service Implementation**

### **Tasks:**

1. [ ] Create S3 connection service
2. [ ] Implement file listing
3. [ ] Implement file download
4. [ ] Add error handling
5. [ ] Test with sample files

**Files to Create:**

- `app/services/s3_service.py`
- `app/utils/s3_helpers.py`

**Service Template:**

```python
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings
from datetime import date
import logging

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME

    def list_files(self, prefix: str = None, target_date: date = None) -> list:
        """List files in S3 bucket with optional prefix and date filter."""
        try:
            prefix = prefix or settings.S3_FOLDER_PREFIX
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )

            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified']
                })

            return files
        except ClientError as e:
            logger.error(f"Error listing S3 files: {e}")
            raise

    def download_file(self, file_key: str, local_path: str = None) -> str:
        """Download file from S3 to local path or return content."""
        try:
            if local_path:
                self.s3_client.download_file(self.bucket_name, file_key, local_path)
                return local_path
            else:
                response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
                return response['Body'].read()
        except ClientError as e:
            logger.error(f"Error downloading file from S3: {e}")
            raise

    def get_latest_file_for_date(self, target_date: date) -> dict:
        """Find the latest file for a specific date."""
        date_str = target_date.strftime("%Y-%m-%d")
        files = self.list_files()

        # Filter files matching date pattern
        matching_files = [f for f in files if date_str in f['key']]

        if not matching_files:
            raise FileNotFoundError(f"No file found for date {date_str}")

        # Return latest by last_modified
        return max(matching_files, key=lambda x: x['last_modified'])
```

---

## **CHECKPOINT 8: CSV Parser Service**

### **Tasks:**

1. [ ] Create CSV parsing service
2. [ ] Add column validation
3. [ ] Add data type conversion
4. [ ] Add error handling
5. [ ] Test with sample CSV

**Files to Create:**

- `app/services/csv_parser.py`
- `app/utils/validators.py`

**Parser Template:**

```python
import csv
import pandas as pd
from datetime import datetime
from decimal import Decimal
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class CSVParser:
    REQUIRED_COLUMNS = [
        'date', 'campaign_name', 'strategy_name',
        'placement_name', 'creative_name', 'impressions',
        'clicks', 'conversions', 'conversion_revenue'
    ]

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate_structure(self, df: pd.DataFrame) -> bool:
        """Validate CSV has required columns."""
        missing_cols = set(self.REQUIRED_COLUMNS) - set(df.columns)
        if missing_cols:
            self.errors.append(f"Missing required columns: {missing_cols}")
            return False
        return True

    def parse_csv(self, file_path: str = None, file_content: bytes = None) -> List[Dict]:
        """Parse CSV file and return list of validated records."""
        try:
            # Read CSV
            if file_path:
                df = pd.read_csv(file_path)
            else:
                df = pd.read_csv(io.BytesIO(file_content))

            # Validate structure
            if not self.validate_structure(df):
                raise ValueError("CSV structure validation failed")

            # Data type conversions
            df['date'] = pd.to_datetime(df['date']).dt.date
            df['impressions'] = df['impressions'].fillna(0).astype(int)
            df['clicks'] = df['clicks'].fillna(0).astype(int)
            df['conversions'] = df['conversions'].fillna(0).astype(int)
            df['conversion_revenue'] = df['conversion_revenue'].fillna(0).astype(float)

            # Optional CTR
            if 'ctr' in df.columns:
                df['ctr'] = df['ctr'].fillna(0).astype(float)

            # Convert to list of dicts
            records = df.to_dict('records')

            logger.info(f"Parsed {len(records)} records from CSV")
            return records

        except Exception as e:
            logger.error(f"Error parsing CSV: {e}")
            raise
```

---

## **CHECKPOINT 9: ETL Pipeline Implementation**

### **Tasks:**

1. [ ] Create ingestion orchestrator
2. [ ] Implement staging loader
3. [ ] Implement entity resolver
4. [ ] Implement CPM calculator
5. [ ] Implement metrics loader
6. [ ] Add transaction management
7. [ ] Add error logging

**Files to Create:**

- `app/services/ingestion_service.py`
- `app/services/entity_resolver.py`
- `app/services/metrics_calculator.py`

**Orchestrator Template:**

```python
from sqlalchemy.orm import Session
from datetime import date, datetime
import uuid
import logging
from typing import Optional

from app.services.s3_service import S3Service
from app.services.csv_parser import CSVParser
from app.services.entity_resolver import EntityResolver
from app.services.metrics_calculator import MetricsCalculator
from app.models.staging import StagingMediaRaw
from app.models.ingestion_log import IngestionLog

logger = logging.getLogger(__name__)

class IngestionService:
    def __init__(self, db: Session):
        self.db = db
        self.s3_service = S3Service()
        self.csv_parser = CSVParser()
        self.entity_resolver = EntityResolver(db)
        self.metrics_calculator = MetricsCalculator(db)

    async def run_daily_ingestion(
        self,
        client_id: uuid.UUID,
        target_date: date = None
    ) -> IngestionLog:
        """
        Main orchestration function for daily ingestion.

        Steps:
        1. Download file from S3
        2. Parse and validate CSV
        3. Load into staging
        4. Resolve entities
        5. Calculate metrics
        6. Load into daily_metrics
        7. Log results
        """
        target_date = target_date or date.today()
        ingestion_run_id = uuid.uuid4()
        start_time = datetime.now()

        log = IngestionLog(
            id=ingestion_run_id,
            run_date=target_date,
            started_at=start_time,
            status='processing',
            source='s3',
            client_id=client_id
        )
        self.db.add(log)
        self.db.commit()

        try:
            # Step 1: Download from S3
            logger.info(f"Fetching file for date {target_date}")
            file_info = self.s3_service.get_latest_file_for_date(target_date)
            file_content = self.s3_service.download_file(file_info['key'])
            log.file_name = file_info['key']
            self.db.commit()

            # Step 2: Parse CSV
            logger.info("Parsing CSV")
            records = self.csv_parser.parse_csv(file_content=file_content)

            # Step 3: Load to staging
            logger.info(f"Loading {len(records)} records to staging")
            staging_records = []
            for record in records:
                staging_record = StagingMediaRaw(
                    ingestion_run_id=ingestion_run_id,
                    client_id=client_id,
                    **record
                )
                staging_records.append(staging_record)

            self.db.bulk_save_objects(staging_records)
            self.db.commit()

            # Step 4-6: Process staging records
            logger.info("Processing staging records")
            processed_count = await self._process_staging_records(
                ingestion_run_id,
                client_id
            )

            # Step 7: Update log
            log.status = 'success'
            log.records_loaded = processed_count
            log.records_failed = len(records) - processed_count
            log.finished_at = datetime.now()
            log.message = f"Successfully processed {processed_count} records"
            self.db.commit()

            logger.info(f"Ingestion completed successfully: {processed_count} records")
            return log

        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            log.status = 'failed'
            log.message = str(e)
            log.finished_at = datetime.now()
            self.db.commit()

            # Send alert (implement notification service)
            # await self.send_alert(log)

            raise
```

---

## **CHECKPOINT 10: Scheduled Jobs**

### **Tasks:**

1. [ ] Create daily ingestion job
2. [ ] Create weekly summary job
3. [ ] Create monthly summary job
4. [ ] Set up APScheduler or Celery
5. [ ] Add job monitoring

**Files to Create:**

- `app/jobs/scheduler.py`
- `app/jobs/daily_ingestion.py`
- `app/jobs/weekly_summary.py`
- `app/jobs/monthly_summary.py`

**Scheduler Template:**

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import logging

from app.jobs.daily_ingestion import run_daily_ingestion_job
from app.jobs.weekly_summary import run_weekly_summary_job
from app.jobs.monthly_summary import run_monthly_summary_job

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

def setup_jobs():
    """Configure all scheduled jobs."""

    # Daily ingestion at 3:30 AM EST
    scheduler.add_job(
        run_daily_ingestion_job,
        trigger=CronTrigger(hour=3, minute=30, timezone='America/New_York'),
        id='daily_ingestion',
        name='Daily S3 Data Ingestion',
        replace_existing=True
    )

    # Weekly summary on Monday at 5:00 AM
    scheduler.add_job(
        run_weekly_summary_job,
        trigger=CronTrigger(day_of_week='mon', hour=5, minute=0),
        id='weekly_summary',
        name='Weekly Summary Generation',
        replace_existing=True
    )

    # Monthly summary on 1st of month at 5:00 AM
    scheduler.add_job(
        run_monthly_summary_job,
        trigger=CronTrigger(day=1, hour=5, minute=0),
        id='monthly_summary',
        name='Monthly Summary Generation',
        replace_existing=True
    )

    logger.info("Scheduled jobs configured")

def start_scheduler():
    """Start the job scheduler."""
    setup_jobs()
    scheduler.start()
    logger.info("Job scheduler started")

def shutdown_scheduler():
    """Gracefully shutdown scheduler."""
    scheduler.shutdown()
    logger.info("Job scheduler shut down")
```

---

## **CHECKPOINT 11: API Endpoints**

### **Tasks:**

1. [ ] Dashboard overview endpoint
2. [ ] Campaign list and detail endpoints
3. [ ] Metrics aggregation endpoints
4. [ ] Filter and sort implementation
5. [ ] Export endpoints

**Files to Create:**

- `app/api/v1/endpoints/dashboard.py`
- `app/api/v1/endpoints/campaigns.py`
- `app/api/v1/endpoints/metrics.py`
- `app/api/v1/endpoints/exports.py`

**Endpoints to Implement:**

```
GET /api/v1/dashboard/overview
GET /api/v1/dashboard/summary?start_date=&end_date=&client_id=

GET /api/v1/campaigns?client_id=&start_date=&end_date=
GET /api/v1/campaigns/{campaign_id}
GET /api/v1/campaigns/{campaign_id}/metrics

GET /api/v1/strategies?campaign_id=
GET /api/v1/strategies/{strategy_id}/metrics

GET /api/v1/placements?strategy_id=
GET /api/v1/creatives?placement_id=

GET /api/v1/metrics/daily?filters=
GET /api/v1/metrics/weekly?client_id=
GET /api/v1/metrics/monthly?client_id=

POST /api/v1/exports/csv
POST /api/v1/exports/pdf

GET /api/v1/admin/ingestion-logs
POST /api/v1/admin/trigger-ingestion
POST /api/v1/admin/backfill-historical
PUT /api/v1/admin/clients/{client_id}/toggle-status
POST /api/v1/admin/ingestion-logs/{log_id}/resolve
```

### **6.5 Admin Backfill Endpoint (`app/api/v1/endpoints/admin.py`)**

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.dependencies import require_admin
from app.surfside.etl import SurfsideETL
from datetime import date

router = APIRouter()

@router.post("/backfill-historical")
async def backfill_historical_data(
    client_id: str,
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Trigger historical data backfill for a date range."""
    etl = SurfsideETL(db)
    result = etl.run_historical_backfill(client_id, start_date, end_date)
    return result

@router.put("/clients/{client_id}/toggle-status")
async def toggle_client_status(
    client_id: str,
    status: str = Query(..., regex="^(active|disabled)$"),
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Enable or disable client access."""
    from app.clients.service import ClientService
    client = ClientService.toggle_client_status(db, client_id, status)
    return {"message": f"Client status updated to {status}", "client": client}

@router.post("/ingestion-logs/{log_id}/resolve")
async def resolve_ingestion_error(
    log_id: str,
    resolution_notes: str,
    current_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Mark an ingestion error as resolved."""
    log = db.query(IngestionLog).filter(IngestionLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Ingestion log not found")

    log.resolution_status = "resolved"
    log.resolution_notes = resolution_notes
    log.resolved_at = datetime.now()
    log.resolved_by = current_user.id
    db.commit()

    return {"message": "Ingestion error marked as resolved"}
```

---

## **CHECKPOINT 12: Testing**

### **Tasks:**

1. [ ] Unit tests for models
2. [ ] Unit tests for services
3. [ ] Integration tests for ETL
4. [ ] API endpoint tests
5. [ ] Load testing for large datasets

**Files to Create:**

- `tests/test_models.py`
- `tests/test_services/test_s3_service.py`
- `tests/test_services/test_csv_parser.py`
- `tests/test_services/test_ingestion.py`
- `tests/test_api/test_auth.py`
- `tests/test_api/test_campaigns.py`

---

# **8. TESTING STRATEGY**

## **8.1 Unit Tests**

```python
# Example: Test CPM calculation
def test_cpm_calculation():
    impressions = 10000
    client_cpm = 15.00
    expected_spend = 150.00

    calculator = MetricsCalculator(db)
    spend = calculator.calculate_spend(impressions, client_cpm)

    assert spend == expected_spend

# Example: Test division by zero
def test_cpc_with_zero_clicks():
    spend = 100.00
    clicks = 0

    calculator = MetricsCalculator(db)
    cpc = calculator.calculate_cpc(spend, clicks)

    assert cpc == 0
```

## **8.2 Integration Tests**

```python
# Example: Test full ETL pipeline
async def test_full_etl_pipeline(db, sample_csv_file):
    service = IngestionService(db)
    result = await service.run_daily_ingestion(
        client_id=test_client_id,
        target_date=date(2024, 1, 1)
    )

    assert result.status == 'success'
    assert result.records_loaded > 0

    # Verify data in daily_metrics
    metrics = db.query(DailyMetrics).filter(
        DailyMetrics.client_id == test_client_id,
        DailyMetrics.date == date(2024, 1, 1)
    ).all()

    assert len(metrics) > 0
    assert all(m.spend > 0 for m in metrics)
```

---

# **9. DEPLOYMENT CHECKLIST**

## **Pre-Deployment**

- [ ] All tests passing
- [ ] Database migrations ready
- [ ] Environment variables configured
- [ ] S3 credentials verified
- [ ] Logging configured
- [ ] Error monitoring setup

## **Deployment Steps**

- [ ] Deploy database migrations
- [ ] Deploy application
- [ ] Start scheduler
- [ ] Verify cron jobs running
- [ ] Test API endpoints
- [ ] Monitor first ingestion run

## **Post-Deployment**

- [ ] Verify daily ingestion working
- [ ] Check logs for errors
- [ ] Verify data accuracy
- [ ] Test admin portal
- [ ] Load test with production data

---

# **IMPLEMENTATION ORDER SUMMARY**

```
Week 1:
✅ Database schema & migrations
✅ SQLAlchemy models
✅ Pydantic schemas
✅ Core configuration
✅ Authentication system

Week 2:
⏳ Client management API
⏳ S3 service
⏳ CSV parser
⏳ Entity resolver
⏳ Metrics calculator

Week 3:
⏳ ETL orchestration
⏳ Scheduled jobs
⏳ API endpoints
⏳ Admin endpoints

Week 4:
⏳ Testing
⏳ Bug fixes
⏳ Performance optimization
⏳ Documentation
⏳ Deployment
```

---

**END OF IMPLEMENTATION GUIDE**

This document provides the complete roadmap for building the V1 dashboard backend. Follow each checkpoint sequentially, and mark tasks complete as you progress.

# **SYSTEM ARCHITECTURE DOCUMENT**

## **Project:** Paid Media Performance Dashboard (V1)
## **Date:** December 13, 2025
## **Tech Stack:** FastAPI + PostgreSQL + AWS S3 + Vibe API + Facebook Upload

---

# **TABLE OF CONTENTS**

1. [High-Level Architecture](#1-high-level-architecture)
2. [System Components Overview](#2-system-components-overview)
3. [Data Flow Diagrams](#3-data-flow-diagrams)
4. [Low-Level Architecture - Module Details](#4-low-level-architecture---module-details)
5. [Database Architecture](#5-database-architecture)
6. [API Architecture](#6-api-architecture)
7. [Integration Patterns](#7-integration-patterns)
8. [Security Architecture](#8-security-architecture)
9. [Deployment Architecture](#9-deployment-architecture)

---

# **1. HIGH-LEVEL ARCHITECTURE**

## **1.1 System Overview**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DASHBOARD APPLICATION                            │
│                                                                           │
│  ┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐ │
│  │   Data Sources  │──────│   Backend API    │──────│  Frontend Web   │ │
│  │                 │      │   (FastAPI)      │      │   Dashboard     │ │
│  │  1. Surfside    │      │                  │      │                 │ │
│  │  2. Vibe API    │      │  ┌────────────┐  │      │  - Charts       │ │
│  │  3. Facebook    │      │  │ PostgreSQL │  │      │  - Tables       │ │
│  └─────────────────┘      │  └────────────┘  │      │  - Filters      │ │
│                            └──────────────────┘      └─────────────────┘ │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                        Scheduled Jobs Layer                          │ │
│  │  - Daily Surfside Ingestion (5 AM)                                  │ │
│  │  - Daily Vibe API Pull (6 AM)                                       │ │
│  │  - Weekly/Monthly Aggregations (7 AM)                               │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

## **1.2 Core Principles**

1. **Modular Design**: 10 independent modules with clear responsibilities
2. **Three Equal Sources**: Surfside, Vibe, and Facebook are all primary sources
3. **ETL Pipeline**: Extract → Transform → Load pattern for all data sources
4. **CPM-Based Calculations**: All spend calculations use client-specific CPM rates
5. **API-First**: RESTful API for all data access
6. **Scheduled Automation**: Daily ingestion and aggregation jobs
7. **Security**: JWT-based authentication with RBAC (admin/client roles)
8. **Scalability**: Batch processing, connection pooling, indexed queries

## **1.3 Technology Stack**

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend Framework** | FastAPI 0.104+ | REST API, async support, auto-documentation |
| **Database** | PostgreSQL 14+ | Relational data storage, JSONB support |
| **ORM** | SQLAlchemy 2.0+ | Database abstraction, migrations |
| **Authentication** | JWT + bcrypt | Secure token-based auth, password hashing |
| **Cloud Storage** | AWS S3 + boto3 | Surfside file storage |
| **External API** | httpx + aiohttp | Vibe API integration (async) |
| **Scheduling** | APScheduler | Cron-like job scheduling |
| **Data Processing** | pandas + openpyxl | CSV/XLSX parsing, transformations |
| **Export** | ReportLab + CSV | PDF and CSV export generation |
| **Email** | SMTP (aiosmtplib) | Alert notifications |
| **Testing** | pytest + httpx | Unit, integration, API tests |
| **Logging** | Python logging | Structured application logs |

---

# **2. SYSTEM COMPONENTS OVERVIEW**

## **2.1 Component Hierarchy**

```
Dashboard System
│
├── 1. Foundation Layer (Core Infrastructure)
│   ├── Database Connection Management
│   ├── Configuration & Settings
│   ├── Logging System
│   ├── Email Service
│   └── Custom Exceptions
│
├── 2. Security Layer (Authentication & Authorization)
│   ├── JWT Token Management
│   ├── Password Hashing
│   ├── User Authentication
│   ├── Role-Based Access Control (RBAC)
│   └── Password Reset
│
├── 3. Data Management Layer
│   ├── Client Management (CPM rates, settings)
│   ├── Campaign Hierarchy (campaigns → strategies → placements → creatives)
│   ├── Metrics Storage (daily, weekly, monthly)
│   └── Audit Logging
│
├── 4. Data Ingestion Layer (ETL)
│   ├── Surfside Integration (S3 → ETL → DB)
│   ├── Vibe Integration (API → ETL → DB)
│   ├── Facebook Integration (Upload → ETL → DB)
│   └── Shared ETL Components (staging, transformation, loading)
│
├── 5. Business Logic Layer
│   ├── Metrics Calculation (CPM, CPC, CPA, ROAS, CTR)
│   ├── Aggregation (weekly, monthly summaries)
│   ├── Top Performers Identification
│   └── Delta Calculations (WoW, MoM)
│
├── 6. API Layer (REST Endpoints)
│   ├── Authentication Endpoints
│   ├── Client Management Endpoints
│   ├── Campaign Management Endpoints
│   ├── Metrics Endpoints
│   ├── Dashboard Endpoints
│   ├── Export Endpoints
│   └── Admin Endpoints
│
├── 7. Scheduling Layer (Background Jobs)
│   ├── Daily Surfside Ingestion
│   ├── Daily Vibe API Pull
│   ├── Weekly Aggregation
│   └── Monthly Aggregation
│
└── 8. Integration Layer
    ├── AWS S3 Integration
    ├── Vibe API Integration
    └── SMTP Email Integration
```

## **2.2 Module Breakdown (10 Modules)**

| Module # | Module Name | Purpose | Key Files |
|----------|-------------|---------|-----------|
| **1** | Core/Foundation | Database, config, logging, email | config.py, database.py, logging.py, email.py, exceptions.py |
| **2** | Authentication | User auth, JWT, RBAC | models.py, schemas.py, security.py, dependencies.py, router.py |
| **3** | Client Management | Client CRUD, CPM management | models.py, schemas.py, service.py, router.py |
| **4** | Campaign Hierarchy | Campaign/Strategy/Placement/Creative | models.py, schemas.py, service.py, router.py |
| **5** | Surfside Integration | S3 download, parsing, ETL | s3_service.py, parser.py, etl.py, scheduler.py |
| **6** | Vibe Integration | API client, async reports, ETL | api_client.py, service.py, parser.py, etl.py, models.py, scheduler.py |
| **7** | Facebook Integration | File upload, validation, ETL | upload_handler.py, validator.py, parser.py, etl.py, models.py, router.py |
| **8** | Metrics & Aggregation | Calculations, summaries | models.py, schemas.py, calculator.py, aggregator.py, router.py |
| **9** | Dashboard API | Dashboard queries, responses | service.py, schemas.py, router.py |
| **10** | Shared ETL | Common ETL components | orchestrator.py, staging.py, transformer.py, loader.py |

---

# **3. DATA FLOW DIAGRAMS**

## **3.1 Surfside Data Flow (S3 → Database)**

```
┌──────────────┐
│   S3 Bucket  │ (Stephen's bucket: daily CSV/XLSX files)
└──────┬───────┘
       │
       │ [1] S3Service.download_file()
       ▼
┌──────────────────┐
│  Local File      │ (/tmp/surfside_2024-12-13.csv)
└──────┬───────────┘
       │
       │ [2] SurfsideParser.parse_file()
       ▼
┌──────────────────┐
│  Python List     │ (list of dict records)
└──────┬───────────┘
       │
       │ [3] DataValidator.validate_batch()
       ▼
┌──────────────────┐
│  Validated Data  │ (valid_records, invalid_records)
└──────┬───────────┘
       │
       │ [4] StagingService.load_to_staging()
       ▼
┌──────────────────────┐
│ staging_media_raw    │ (temporary storage with ingestion_run_id)
└──────┬───────────────┘
       │
       │ [5] TransformerService.process_staging()
       │     - Find/create campaigns
       │     - Find/create strategies
       │     - Find/create placements
       │     - Find/create creatives
       ▼
┌──────────────────────┐
│ campaigns, strategies│
│ placements, creatives│ (normalized entities with UUIDs)
└──────┬───────────────┘
       │
       │ [6] LoaderService.load_daily_metrics()
       │     - Fetch client CPM
       │     - Calculate spend = (impressions/1000) * cpm
       │     - Calculate CTR, CPC, CPA, ROAS
       ▼
┌──────────────────────┐
│   daily_metrics      │ (final metrics table)
└──────────────────────┘
```

## **3.2 Vibe API Data Flow (API → Database)**

```
┌──────────────┐
│  Vibe API    │ (https://api.vibe.co)
└──────┬───────┘
       │
       │ [1] VibeAPIClient.create_report()
       │     POST /reporting/v1/std/reports
       ▼
┌──────────────────────┐
│  Report Created      │ (report_id: "abc-123")
│  Status: "created"   │
└──────┬───────────────┘
       │
       │ [2] VibeAPIClient.wait_for_report()
       │     Poll GET /reports/{id} every 30 seconds
       ▼
┌──────────────────────┐
│  Report Ready        │ (status: "done", download_url: "https://...")
└──────┬───────────────┘
       │
       │ [3] VibeAPIClient.download_report()
       │     GET {download_url}
       ▼
┌──────────────────┐
│  CSV Content     │ (bytes)
└──────┬───────────┘
       │
       │ [4] VibeParser.parse_file()
       ▼
┌──────────────────┐
│  Python List     │ (list of dict records)
└──────┬───────────┘
       │
       │ [5-7] Same as Surfside flow
       │       - Validation
       │       - Staging
       │       - Transformation
       │       - Loading with CPM calculations
       ▼
┌──────────────────────┐
│   daily_metrics      │ (source='vibe')
└──────────────────────┘
```

## **3.3 Facebook Upload Data Flow (Upload → Database)**

```
┌──────────────┐
│  User Upload │ (Frontend form: multipart/form-data)
└──────┬───────┘
       │
       │ [1] POST /api/v1/facebook/upload
       ▼
┌──────────────────────┐
│ FacebookValidator    │ - Check file size (<50MB)
│                      │ - Check file extension (.csv, .xlsx)
│                      │ - Check columns match expected
└──────┬───────────────┘
       │
       │ [2] Save to uploaded_files table
       ▼
┌──────────────────────┐
│  uploaded_files      │ (status='pending', file_path='/uploads/...')
└──────┬───────────────┘
       │
       │ [3] FacebookParser.parse_file()
       ▼
┌──────────────────┐
│  Python List     │ (Facebook schema: Campaign Name, Ad Set Name, Ad Name)
└──────┬───────────┘
       │
       │ [4] Check duplicates
       │     FacebookValidator.check_duplicates()
       ▼
┌──────────────────────┐
│  Duplicate Check     │ (query daily_metrics for existing records)
└──────┬───────────────┘
       │
       │ [5-7] Same ETL flow
       │       - Staging
       │       - Transformation (Ad Name → Placement + Creative)
       │       - Loading
       ▼
┌──────────────────────┐
│   daily_metrics      │ (source='facebook')
└──────┬───────────────┘
       │
       │ [8] Update uploaded_files status
       ▼
┌──────────────────────┐
│  uploaded_files      │ (status='processed', processed_at=NOW())
└──────────────────────┘
```

## **3.4 Dashboard Query Flow (Client Request → Response)**

```
┌──────────────┐
│  Client      │ (React/Vue frontend)
└──────┬───────┘
       │
       │ GET /api/v1/dashboard?start_date=2024-12-01&end_date=2024-12-13
       │ Header: Authorization: Bearer <jwt_token>
       ▼
┌──────────────────────┐
│  Authentication      │ - Verify JWT token
│  Middleware          │ - Extract user_id
│                      │ - Check permissions
└──────┬───────────────┘
       │
       │ [Authorized]
       ▼
┌──────────────────────┐
│  DashboardService    │ - Parse query params
│                      │ - Get client_id from user
│                      │ - Build SQL queries
└──────┬───────────────┘
       │
       │ [Query 1] Summary metrics
       ▼
┌──────────────────────┐
│  daily_metrics       │ SELECT SUM(impressions), SUM(clicks), ...
│  WHERE client_id=X   │ WHERE date BETWEEN start AND end
│  AND date BETWEEN... │ GROUP BY client_id
└──────┬───────────────┘
       │
       │ [Query 2] Top campaigns
       ▼
┌──────────────────────┐
│  daily_metrics       │ SELECT campaign_id, SUM(conversions)
│  JOIN campaigns      │ ORDER BY conversions DESC LIMIT 5
└──────┬───────────────┘
       │
       │ [Query 3] Top creatives
       ▼
┌──────────────────────┐
│  daily_metrics       │ SELECT creative_id, SUM(revenue)
│  JOIN creatives      │ ORDER BY revenue DESC LIMIT 5
└──────┬───────────────┘
       │
       │ [Query 4] Week-over-week deltas
       ▼
┌──────────────────────┐
│  weekly_summaries    │ SELECT this_week.*, prev_week.*
│                      │ Calculate % change
└──────┬───────────────┘
       │
       │ [Aggregate results]
       ▼
┌──────────────────────┐
│  DashboardResponse   │ {
│  (Pydantic Schema)   │   summary: {...},
│                      │   campaigns: [...],
│                      │   creatives: [...],
│                      │   weekly_delta: {...}
│                      │ }
└──────┬───────────────┘
       │
       │ HTTP 200 OK (JSON)
       ▼
┌──────────────┐
│  Client      │ (Render charts and tables)
└──────────────┘
```

---

# **4. LOW-LEVEL ARCHITECTURE - MODULE DETAILS**

## **Module 1: Core/Foundation (`app/core/`)**

### **Purpose**
Provides foundational infrastructure used by all other modules: database connections, configuration management, logging, email notifications, and custom exceptions.

### **Files & Responsibilities**

#### **`config.py`**
- **Purpose**: Centralized configuration management using environment variables
- **Key Classes**:
  - `Settings(BaseSettings)`: Pydantic settings class
- **Responsibilities**:
  - Load `.env` file
  - Define all environment variables with types and defaults
  - Provide singleton `settings` instance
- **Environment Variables**:
  - `DATABASE_URL`: PostgreSQL connection string
  - `SECRET_KEY`: JWT signing key
  - `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`: S3 credentials
  - `VIBE_API_KEY`, `VIBE_ADVERTISER_ID`: Vibe API credentials
  - `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`: Email config
  - `UPLOAD_DIR`, `MAX_UPLOAD_SIZE`: File upload settings
- **Dependencies**: `pydantic-settings`, `python-dotenv`

#### **`database.py`**
- **Purpose**: Database connection and session management
- **Key Components**:
  - `engine`: SQLAlchemy engine with connection pooling
  - `SessionLocal`: Session factory for creating DB sessions
  - `Base`: Declarative base for ORM models
  - `get_db()`: FastAPI dependency for DB sessions
- **Responsibilities**:
  - Create SQLAlchemy engine with pool settings
  - Provide session management with auto-commit/rollback
  - Ensure sessions are closed after requests
- **Connection Pool Settings**:
  - `pool_size=20`: Max persistent connections
  - `max_overflow=20`: Additional connections when pool full
  - `pool_pre_ping=True`: Verify connection before use
  - `pool_recycle=3600`: Recycle connections after 1 hour
- **Dependencies**: `sqlalchemy`

#### **`logging.py`**
- **Purpose**: Structured logging configuration
- **Key Functions**:
  - `setup_logging()`: Initialize logging system
- **Responsibilities**:
  - Configure log format (timestamp, level, module, message)
  - Set log level based on DEBUG environment variable
  - Configure console and file handlers
  - Suppress noisy third-party logs (boto3, urllib3)
- **Log Levels**:
  - DEBUG mode: ALL logs
  - Production: INFO and above
- **Dependencies**: Python `logging` module

#### **`email.py`**
- **Purpose**: Email notification service for alerts
- **Key Classes**:
  - `EmailService`: SMTP email sender
- **Methods**:
  - `send_email(to, subject, body)`: Generic email sender
  - `send_ingestion_failure_alert(source, date, error)`: Alert on ETL failures
  - `send_missing_file_alert(source, date, bucket, path)`: Alert on missing S3 files
  - `send_validation_error_alert(client, date, errors)`: Alert on data validation issues
- **Responsibilities**:
  - Connect to SMTP server
  - Format email templates
  - Send notifications to admin email
  - Handle SMTP errors gracefully
- **Dependencies**: `smtplib`, `aiosmtplib` (for async)

#### **`exceptions.py`**
- **Purpose**: Custom exception classes for application-specific errors
- **Key Classes**:
  - `DatabaseError(Exception)`: Database operation failures
  - `ValidationError(Exception)`: Data validation failures
  - `S3Error(Exception)`: S3 download/upload errors
  - `VibeAPIError(Exception)`: Vibe API request failures
  - `AuthenticationError(Exception)`: Auth failures
  - `AuthorizationError(Exception)`: Permission denied errors
- **Responsibilities**:
  - Provide meaningful error messages
  - Enable specific error handling in try/except blocks
  - Support error logging and debugging

---

## **Module 2: Authentication (`app/auth/`)**

### **Purpose**
Handles user authentication, JWT token generation/validation, password management, and role-based access control.

### **Files & Responsibilities**

#### **`models.py`**
- **Purpose**: SQLAlchemy ORM model for users table
- **Key Classes**:
  - `User(Base)`: User entity
- **Fields**:
  - `id`: UUID primary key
  - `email`: Unique email address
  - `password_hash`: bcrypt hashed password
  - `role`: Enum ('admin', 'client')
  - `is_active`: Boolean flag
  - `created_at`, `updated_at`: Timestamps
- **Relationships**:
  - `clients`: One-to-many (User → Client)
  - `audit_logs`: One-to-many (User → AuditLog)
- **Methods**:
  - `verify_password(password)`: Check password against hash
  - `is_admin()`: Check if user is admin

#### **`schemas.py`**
- **Purpose**: Pydantic schemas for request/response validation
- **Key Classes**:
  - `UserLogin`: Login request (email, password)
  - `UserRegister`: Registration request (email, password, role)
  - `UserResponse`: User response (id, email, role, is_active)
  - `Token`: JWT token response (access_token, token_type)
  - `TokenData`: Decoded token data (user_id, email, role)
  - `PasswordReset`: Password reset request (new_password)
- **Validation Rules**:
  - Email format validation
  - Password minimum length (8 characters)
  - Role must be 'admin' or 'client'

#### **`security.py`**
- **Purpose**: JWT token management and password hashing
- **Key Functions**:
  - `hash_password(password)`: Hash password with bcrypt
  - `verify_password(plain, hashed)`: Verify password
  - `create_access_token(data, expires_delta)`: Generate JWT token
  - `decode_access_token(token)`: Decode and validate JWT
- **Responsibilities**:
  - Use bcrypt for secure password hashing
  - Generate JWT tokens with expiration
  - Validate JWT signatures
  - Handle token expiration
- **Security Settings**:
  - Algorithm: HS256
  - Token expiration: 30 minutes (configurable)
  - Bcrypt rounds: 12 (default)
- **Dependencies**: `python-jose[cryptography]`, `passlib[bcrypt]`

#### **`dependencies.py`**
- **Purpose**: FastAPI dependencies for authentication
- **Key Functions**:
  - `get_current_user(token)`: Extract user from JWT
  - `require_admin(current_user)`: Ensure user is admin
  - `get_current_client(current_user)`: Get client for client users
- **Responsibilities**:
  - Validate JWT token on each request
  - Query user from database
  - Enforce role-based access control
  - Raise HTTPException on auth failures
- **Usage**: FastAPI route dependencies

#### **`router.py`**
- **Purpose**: Authentication API endpoints
- **Endpoints**:
  - `POST /auth/login`: User login (returns JWT token)
  - `POST /auth/register`: User registration (admin only)
  - `GET /auth/me`: Get current user info
  - `POST /auth/reset-password/{user_id}`: Reset user password (admin only)
  - `PUT /auth/change-password`: Change own password
- **Responsibilities**:
  - Validate credentials
  - Generate tokens
  - Create new users
  - Update passwords
  - Return appropriate HTTP status codes

---

## **Module 3: Client Management (`app/clients/`)**

### **Purpose**
Manages client entities, client settings (CPM rates), and provides CRUD operations for client data.

### **Files & Responsibilities**

#### **`models.py`**
- **Purpose**: SQLAlchemy models for clients and client settings
- **Key Classes**:
  - `Client(Base)`: Client entity
  - `ClientSettings(Base)`: Client CPM and configuration
- **Client Fields**:
  - `id`: UUID primary key
  - `name`: Client name
  - `status`: Enum ('active', 'disabled')
  - `user_id`: FK to users table
  - `created_at`, `updated_at`: Timestamps
- **ClientSettings Fields**:
  - `id`: UUID primary key
  - `client_id`: FK to clients table
  - `cpm`: Decimal(10,4) - CPM rate
  - `currency`: VARCHAR(3) default 'USD'
  - `effective_date`: Date when CPM becomes active
  - `created_at`, `updated_at`: Timestamps
- **Relationships**:
  - Client → User (many-to-one)
  - Client → ClientSettings (one-to-many)
  - Client → Campaigns (one-to-many)

#### **`schemas.py`**
- **Purpose**: Pydantic schemas for client API
- **Key Classes**:
  - `ClientCreate`: Create client (name, user_id)
  - `ClientUpdate`: Update client (name, status)
  - `ClientResponse`: Client data response
  - `ClientSettingsCreate`: Create CPM setting (cpm, effective_date)
  - `ClientSettingsUpdate`: Update CPM setting
  - `ClientSettingsResponse`: Settings response
  - `ClientWithSettings`: Client + current CPM
- **Validation**:
  - CPM must be positive
  - Status must be 'active' or 'disabled'
  - Name must be non-empty

#### **`service.py`**
- **Purpose**: Business logic for client management
- **Key Classes**:
  - `ClientService`: Client CRUD operations
- **Methods**:
  - `create_client(data)`: Create new client
  - `get_client(id)`: Get client by ID
  - `get_all_clients()`: List all clients
  - `get_all_active_clients()`: List active clients only
  - `update_client(id, data)`: Update client
  - `delete_client(id)`: Soft delete (set status='disabled')
  - `toggle_client_status(id)`: Toggle active/disabled
  - `get_client_cpm(id, date)`: Get effective CPM for date
  - `set_client_cpm(id, cpm, effective_date)`: Create CPM setting
  - `get_cpm_history(id)`: List all CPM changes
- **Responsibilities**:
  - Validate business rules
  - Query database efficiently
  - Handle CPM effective date logic
  - Return appropriate errors

#### **`router.py`**
- **Purpose**: Client management API endpoints
- **Endpoints**:
  - `POST /clients`: Create client (admin only)
  - `GET /clients`: List all clients (admin only)
  - `GET /clients/active`: List active clients
  - `GET /clients/{id}`: Get client details
  - `PUT /clients/{id}`: Update client (admin only)
  - `DELETE /clients/{id}`: Delete client (admin only)
  - `POST /clients/{id}/toggle`: Toggle client status (admin only)
  - `POST /clients/{id}/cpm`: Set CPM rate (admin only)
  - `GET /clients/{id}/cpm/history`: Get CPM history
- **Responsibilities**:
  - Validate request data
  - Enforce authorization
  - Call service methods
  - Return JSON responses

---

## **Module 4: Campaign Hierarchy (`app/campaigns/`)**

### **Purpose**
Manages the 4-level campaign hierarchy: Campaign → Strategy → Placement → Creative. Provides CRUD operations and relationship management.

### **Files & Responsibilities**

#### **`models.py`**
- **Purpose**: SQLAlchemy models for campaign hierarchy
- **Key Classes**:
  - `Campaign(Base)`: Top-level campaign entity
  - `Strategy(Base)`: Second-level strategy entity
  - `Placement(Base)`: Third-level placement entity
  - `Creative(Base)`: Fourth-level creative entity
- **Campaign Fields**:
  - `id`: UUID primary key
  - `client_id`: FK to clients
  - `name`: Campaign name
  - `source`: Enum ('surfside', 'vibe', 'facebook')
  - `created_at`, `updated_at`: Timestamps
  - Unique constraint: (client_id, name, source)
- **Strategy Fields**:
  - `id`: UUID primary key
  - `campaign_id`: FK to campaigns
  - `name`: Strategy name
  - Unique constraint: (campaign_id, name)
- **Placement Fields**:
  - `id`: UUID primary key
  - `strategy_id`: FK to strategies
  - `name`: Placement name
  - Unique constraint: (strategy_id, name)
- **Creative Fields**:
  - `id`: UUID primary key
  - `placement_id`: FK to placements
  - `name`: Creative name
  - `preview_url`: Optional URL to creative preview
  - Unique constraint: (placement_id, name)
- **Relationships**:
  - Campaign → Strategies (one-to-many)
  - Strategy → Placements (one-to-many)
  - Placement → Creatives (one-to-many)
  - All cascade deletes enabled

#### **`schemas.py`**
- **Purpose**: Pydantic schemas for hierarchy API
- **Key Classes**:
  - `CampaignCreate`: Create campaign (name, source, client_id)
  - `CampaignUpdate`: Update campaign (name)
  - `CampaignResponse`: Campaign data with stats
  - `StrategyCreate`: Create strategy (name, campaign_id)
  - `StrategyUpdate`: Update strategy
  - `StrategyResponse`: Strategy with performance metrics
  - `PlacementCreate`: Create placement
  - `PlacementResponse`: Placement data
  - `CreativeCreate`: Create creative
  - `CreativeResponse`: Creative with preview
  - `HierarchyTree`: Nested hierarchy structure
- **Validation**:
  - Names must be non-empty
  - Source must be valid enum value
  - Foreign keys must exist

#### **`service.py`**
- **Purpose**: Business logic for hierarchy management
- **Key Classes**:
  - `CampaignService`: Hierarchy CRUD and queries
- **Methods**:
  - `find_or_create_campaign(client_id, name, source)`: Get existing or create new
  - `find_or_create_strategy(campaign_id, name)`: Get existing or create new
  - `find_or_create_placement(strategy_id, name)`: Get existing or create new
  - `find_or_create_creative(placement_id, name)`: Get existing or create new
  - `get_campaign_tree(campaign_id)`: Get full hierarchy tree
  - `get_client_campaigns(client_id, source)`: List campaigns with filters
  - `delete_campaign(id)`: Delete campaign and children
  - `get_campaign_performance(id, start_date, end_date)`: Aggregate metrics
- **Responsibilities**:
  - Ensure unique constraints
  - Handle cascade relationships
  - Optimize queries with joins
  - Support ETL lookups (find_or_create pattern)

#### **`router.py`**
- **Purpose**: Campaign hierarchy API endpoints
- **Endpoints**:
  - `GET /campaigns`: List campaigns with filters
  - `GET /campaigns/{id}`: Get campaign details
  - `GET /campaigns/{id}/tree`: Get full hierarchy
  - `GET /campaigns/{id}/performance`: Get performance metrics
  - `POST /campaigns`: Create campaign (admin only)
  - `PUT /campaigns/{id}`: Update campaign
  - `DELETE /campaigns/{id}`: Delete campaign
  - `GET /strategies`: List strategies
  - `POST /strategies`: Create strategy
  - `GET /placements`: List placements
  - `POST /placements`: Create placement
  - `GET /creatives`: List creatives
  - `POST /creatives`: Create creative
- **Responsibilities**:
  - Filter by client (auto-filter for client users)
  - Support pagination
  - Return nested data structures
  - Handle orphan cleanup

---

## **Module 5: Surfside Integration (`app/surfside/`)**

### **Purpose**
Handles Surfside data ingestion from AWS S3: download files, parse CSV/XLSX, validate data, and run ETL pipeline.

### **Files & Responsibilities**

#### **`s3_service.py`**
- **Purpose**: AWS S3 file operations using boto3
- **Key Classes**:
  - `S3Service`: S3 client wrapper
- **Methods**:
  - `__init__()`: Initialize boto3 S3 client with credentials
  - `list_files(prefix, date)`: List files in bucket matching pattern
  - `download_file(key)`: Download file as bytes
  - `get_file_for_date(target_date)`: Get specific date's file
  - `upload_file(key, data)`: Upload file (for backups)
  - `delete_file(key)`: Delete file
  - `file_exists(key)`: Check if file exists
- **Responsibilities**:
  - Connect to S3 using AWS credentials
  - Handle S3 exceptions (NoSuchKey, AccessDenied)
  - Support flexible file naming patterns
  - Implement retry logic for network issues
  - Log all S3 operations
- **Configuration**:
  - Bucket name from env: `S3_BUCKET_NAME`
  - Prefix from env: `S3_PREFIX`
  - File pattern: configurable (default: `media-report-{date}.csv`)
- **Error Handling**:
  - Raise `FileNotFoundError` if file missing
  - Raise `S3Error` on AWS errors
  - Log all errors with context

#### **`parser.py`**
- **Purpose**: Parse Surfside CSV/XLSX files into Python dictionaries
- **Key Classes**:
  - `SurfsideParser`: CSV/XLSX parser
- **Methods**:
  - `parse_file(file_path)`: Parse file and return list of records
  - `validate_columns(df)`: Check required columns exist
  - `clean_data(df)`: Handle nulls, strip whitespace
  - `convert_types(df)`: Convert string numbers to int/decimal
- **Responsibilities**:
  - Support both CSV and XLSX formats
  - Validate required columns exist
  - Handle missing/null values
  - Clean data (strip whitespace, lowercase keys)
  - Convert data types (string → int/decimal)
  - Return list of dictionaries
- **Required Columns**:
  - `Date`, `Campaign`, `Strategy`, `Placement`, `Creative`
  - `Impressions`, `Clicks`, `Conversions`, `Conversion Revenue`
  - `CTR` (optional, can be calculated)
- **Data Transformations**:
  - Date: string → date object
  - Metrics: string → int/decimal
  - Names: strip whitespace
- **Dependencies**: `pandas`, `openpyxl`

#### **`etl.py`**
- **Purpose**: Surfside-specific ETL pipeline orchestration
- **Key Classes**:
  - `SurfsideETL`: ETL coordinator
- **Methods**:
  - `__init__(db)`: Initialize with DB session
  - `run_daily_ingestion(target_date)`: Run full ETL for date
  - `run_historical_backfill(start_date, end_date)`: Backfill date range
  - `_extract(target_date)`: Download file from S3
  - `_transform(file_data)`: Parse and validate
  - `_load(records, client_id)`: Stage and load to DB
- **ETL Flow**:
  1. Extract: Download from S3
  2. Parse: CSV/XLSX → list of dicts
  3. Validate: Check data quality
  4. Stage: Insert to `staging_media_raw`
  5. Transform: Create/lookup entities
  6. Calculate: Apply CPM, derive metrics
  7. Load: Insert to `daily_metrics`
  8. Log: Record ingestion status
- **Responsibilities**:
  - Orchestrate full ETL pipeline
  - Handle errors at each stage
  - Log ingestion to `ingestion_logs`
  - Send email alerts on failures
  - Support historical backfill
  - Clean up staging data
- **Error Handling**:
  - Catch and log all exceptions
  - Update ingestion_logs with error details
  - Send email alert on failure
  - Continue processing valid records on partial failure

#### **`scheduler.py`**
- **Purpose**: Schedule daily Surfside ingestion job
- **Key Functions**:
  - `schedule_surfside_job()`: Register cron job
- **Responsibilities**:
  - Run at 5 AM daily (configurable via env)
  - Get yesterday's date (or configured offset)
  - Run ETL for all active clients
  - Handle timezone conversions
- **Configuration**:
  - Cron expression from env: `SURFSIDE_CRON` (default: `0 5 * * *`)
  - Timezone: UTC or configured
- **Dependencies**: `apscheduler`

---

## **Module 6: Vibe Integration (`app/vibe/`)**

### **Purpose**
Handles Vibe API integration: async report creation, status polling, report download, parsing, and ETL pipeline.

### **Files & Responsibilities**

#### **`api_client.py`**
- **Purpose**: HTTP client for Vibe API async report workflow
- **Key Classes**:
  - `VibeAPIClient`: Async HTTP client
- **Methods**:
  - `__init__(api_key, advertiser_id)`: Initialize with credentials
  - `create_report(start_date, end_date, advertiser_id)`: Create async report
  - `check_report_status(report_id)`: Poll report status
  - `download_report(download_url)`: Download CSV
  - `wait_for_report(report_id, max_attempts)`: Poll until ready
  - `_wait_for_rate_limit()`: Enforce 15/hour limit
- **Responsibilities**:
  - Make async HTTP requests to Vibe API
  - Handle authentication (Bearer token)
  - Enforce rate limiting (15 requests/hour)
  - Poll report status every 30 seconds
  - Handle API errors and retries
  - Support client-specific advertiser IDs
- **API Endpoints**:
  - `POST /reporting/v1/std/reports`: Create report
  - `GET /reporting/v1/std/reports/{id}`: Check status
  - `GET {download_url}`: Download CSV
- **Rate Limiting**:
  - Track request timestamps
  - Sleep if 15 requests in past hour
  - Log rate limit waits
- **Error Handling**:
  - Retry on 429 (rate limit)
  - Retry on 5xx (server errors)
  - Fail on 4xx (client errors)
  - Timeout after max polling attempts
- **Dependencies**: `httpx`, `aiohttp`

#### **`models.py`**
- **Purpose**: SQLAlchemy models for Vibe-specific tracking
- **Key Classes**:
  - `VibeCredentials(Base)`: Client-specific API credentials
  - `VibeReportRequest(Base)`: Track async report requests
- **VibeCredentials Fields**:
  - `id`: UUID
  - `client_id`: FK to clients
  - `api_key`: Encrypted API key
  - `advertiser_id`: Vibe advertiser ID
  - `is_active`: Boolean flag
- **VibeReportRequest Fields**:
  - `id`: UUID
  - `client_id`: FK to clients
  - `report_id`: Vibe report ID
  - `status`: Enum ('created', 'processing', 'done', 'error')
  - `request_params`: JSONB (dates, metrics)
  - `download_url`: Report URL
  - `url_expiration`: Timestamp
- **Responsibilities**:
  - Store per-client Vibe credentials
  - Track report requests for debugging
  - Enable report status monitoring

#### **`service.py`**
- **Purpose**: Vibe service layer with client credential management
- **Key Classes**:
  - `VibeService`: Vibe integration coordinator
- **Methods**:
  - `__init__(db, client_id)`: Initialize with client context
  - `_get_client_credentials(client_id)`: Fetch credentials from DB
  - `request_report(start_date, end_date)`: Create report with client creds
  - `get_report_data(report_id)`: Download and return data
- **Responsibilities**:
  - Support multi-client Vibe setups
  - Fetch client-specific credentials
  - Fall back to default credentials if needed
  - Coordinate API client operations
  - Log all Vibe interactions

#### **`parser.py`**
- **Purpose**: Parse Vibe CSV responses
- **Key Classes**:
  - `VibeParser`: CSV parser for Vibe format
- **Methods**:
  - `parse_file(file_path)`: Parse CSV to list of dicts
  - `validate_columns(df)`: Check expected columns
  - `transform_schema(df)`: Map Vibe columns to standard schema
- **Responsibilities**:
  - Parse Vibe CSV format
  - Map Vibe column names to standard schema
  - Handle Vibe-specific data quirks
  - Return standardized records
- **Column Mapping**:
  - Vibe `date` → `date`
  - Vibe `campaign_name` → `campaign_name`
  - Vibe `strategy_name` → `strategy_name`
  - Vibe `placement_name` → `placement_name`
  - Vibe `creative_name` → `creative_name`
  - Vibe metrics → standard metrics

#### **`etl.py`**
- **Purpose**: Vibe-specific ETL pipeline
- **Key Classes**:
  - `VibeETL`: ETL coordinator for Vibe
- **Methods**:
  - `run_daily_ingestion(client_id, target_date, advertiser_id)`: Full ETL
  - `_extract(date)`: Create and download report
  - `_transform(csv_data)`: Parse and validate
  - `_load(records, client_id)`: Stage and load
- **ETL Flow**:
  1. Create async report via API
  2. Poll status until done
  3. Download CSV
  4. Parse CSV
  5. Validate data
  6. Stage → Transform → Load (same as Surfside)
- **Responsibilities**:
  - Handle async report workflow
  - Manage Vibe report tracking
  - Support client-specific advertiser IDs
  - Log all operations
  - Send alerts on failures

#### **`scheduler.py`**
- **Purpose**: Schedule daily Vibe API pulls
- **Key Functions**:
  - `schedule_vibe_job()`: Register cron job
- **Responsibilities**:
  - Run at 6 AM daily
  - Get active clients with Vibe credentials
  - Run ETL for each client
  - Handle rate limiting across clients
- **Configuration**:
  - Cron: `VIBE_CRON` (default: `0 6 * * *`)

---

## **Module 7: Facebook Integration (`app/facebook/`)**

### **Purpose**
Handles Facebook data upload: file validation, parsing, duplicate detection, and ETL pipeline.

### **Files & Responsibilities**

#### **`upload_handler.py`**
- **Purpose**: Process uploaded Facebook CSV/XLSX files
- **Key Classes**:
  - `FacebookUploadHandler`: Upload coordinator
- **Methods**:
  - `__init__(db)`: Initialize with DB session
  - `handle_upload(file, client_id, uploaded_by)`: Process uploaded file
  - `_save_file(file)`: Save to disk/S3
  - `_track_upload(file_info, client_id, user_id)`: Insert to uploaded_files
  - `_process_file(file_path, upload_id)`: Parse and ETL
  - `_update_status(upload_id, status, error)`: Update upload record
- **Upload Flow**:
  1. Receive file from endpoint
  2. Validate file (size, extension, columns)
  3. Save to upload directory
  4. Create uploaded_files record
  5. Parse file
  6. Check for duplicates
  7. Run ETL
  8. Update upload status
  9. Return result to user
- **Responsibilities**:
  - Accept multipart/form-data uploads
  - Save files securely
  - Track upload metadata
  - Handle upload errors
  - Provide user feedback
  - Clean up temp files
- **Configuration**:
  - Upload dir: `UPLOAD_DIR` (default: `./uploads`)
  - Max size: `MAX_UPLOAD_SIZE` (default: 50MB)

#### **`validator.py`**
- **Purpose**: Validate Facebook upload files
- **Key Classes**:
  - `FacebookValidator`: File and data validator
- **Methods**:
  - `validate_file(file)`: Check size and extension
  - `validate_columns(df)`: Check required columns
  - `check_duplicates(records, client_id, db)`: Query for existing data
  - `validate_data_quality(records)`: Business rule validation
- **Validations**:
  - File size < 50MB
  - Extension in ['.csv', '.xlsx']
  - Required columns present
  - No duplicate records in DB
  - Date format valid
  - Metrics are positive numbers
- **Responsibilities**:
  - Reject invalid files immediately
  - Provide clear error messages
  - Prevent duplicate data loads
  - Enforce data quality rules
- **Error Messages**:
  - List specific issues (missing columns, invalid dates, etc.)
  - Return user-friendly error responses

#### **`parser.py`**
- **Purpose**: Parse Facebook CSV/XLSX files
- **Key Classes**:
  - `FacebookParser`: Parser for Facebook format
- **Methods**:
  - `parse_file(file_path)`: Parse to list of dicts
  - `transform_schema(df)`: Map Facebook columns to standard
  - `handle_facebook_quirks(df)`: Handle Facebook-specific formats
- **Column Mapping**:
  - `Campaign Name` → `campaign_name`
  - `Ad Set Name` → `strategy_name`
  - `Ad Name` → `placement_name` AND `creative_name` (same value)
  - Facebook metrics → standard metrics
- **Responsibilities**:
  - Parse Facebook export format
  - Handle Facebook column names
  - Map Ad Name to both Placement and Creative
  - Return standardized records

#### **`etl.py`**
- **Purpose**: Facebook-specific ETL pipeline
- **Key Classes**:
  - `FacebookETL`: ETL coordinator for Facebook
- **Methods**:
  - `run_upload_ingestion(file_path, client_id, upload_id)`: Full ETL
  - `_extract(file_path)`: Read file
  - `_transform(records)`: Validate and transform
  - `_load(records, client_id)`: Stage and load
- **Responsibilities**:
  - Same ETL flow as Surfside/Vibe
  - Handle Facebook schema mapping
  - Update uploaded_files status
  - Log ingestion results

#### **`models.py`**
- **Purpose**: SQLAlchemy model for upload tracking
- **Key Classes**:
  - `UploadedFile(Base)`: Upload metadata
- **Fields**:
  - `id`: UUID
  - `client_id`: FK to clients
  - `source`: Varchar ('facebook')
  - `original_filename`: User's filename
  - `file_size`: Bytes
  - `file_path`: Storage path
  - `uploaded_by`: FK to users
  - `upload_status`: Enum ('pending', 'processing', 'completed', 'failed')
  - `processed_at`: Timestamp
  - `error_message`: Error details if failed
- **Responsibilities**:
  - Track all file uploads
  - Enable upload history
  - Support error debugging

#### **`router.py`**
- **Purpose**: Facebook upload API endpoint
- **Endpoints**:
  - `POST /facebook/upload`: Upload file
  - `GET /facebook/uploads`: List upload history
  - `GET /facebook/uploads/{id}`: Get upload details
  - `DELETE /facebook/uploads/{id}`: Delete upload record
- **Responsibilities**:
  - Accept file uploads
  - Validate user permissions
  - Return upload status
  - Provide upload history

---

## **Module 8: Metrics & Aggregation (`app/metrics/`)**

### **Purpose**
Handles metrics storage, CPM calculations, derived metrics, and weekly/monthly aggregations.

### **Files & Responsibilities**

#### **`models.py`**
- **Purpose**: SQLAlchemy models for metrics tables
- **Key Classes**:
  - `DailyMetrics(Base)`: Daily performance data
  - `WeeklySummary(Base)`: Weekly aggregated data
  - `MonthlySummary(Base)`: Monthly aggregated data
- **DailyMetrics Fields**:
  - `id`: UUID
  - `client_id`, `date`, `campaign_id`, `strategy_id`, `placement_id`, `creative_id`: FKs
  - `source`: Enum ('surfside', 'vibe', 'facebook')
  - Raw metrics: `impressions`, `clicks`, `conversions`, `conversion_revenue`
  - Calculated: `ctr`, `spend`, `cpc`, `cpa`, `roas`
  - Unique: (client_id, date, campaign_id, strategy_id, placement_id, creative_id, source)
- **WeeklySummary Fields**:
  - `id`, `client_id`, `week_start`, `week_end`
  - Aggregated metrics: sums of impressions, clicks, conversions, revenue, spend
  - Calculated: `ctr`, `cpc`, `cpa`, `roas`
  - `top_campaigns`, `top_creatives`: JSONB
- **MonthlySummary Fields**:
  - Same as WeeklySummary but for months
- **Responsibilities**:
  - Store granular daily data
  - Store pre-aggregated summaries
  - Enable fast dashboard queries
  - Support trend analysis

#### **`schemas.py`**
- **Purpose**: Pydantic schemas for metrics API
- **Key Classes**:
  - `DailyMetricsResponse`: Daily metrics data
  - `WeeklySummaryResponse`: Weekly data with deltas
  - `MonthlySummaryResponse`: Monthly data with deltas
  - `MetricsFilter`: Query filters (date range, source, campaign)
  - `MetricsTrend`: Trend data (dates, values)
  - `TopPerformer`: Top campaign/creative data
- **Validation**:
  - Date ranges must be valid
  - Metrics must be non-negative
  - Decimals have proper precision

#### **`calculator.py`**
- **Purpose**: Calculate derived metrics from raw data
- **Key Classes**:
  - `MetricsCalculator`: Metrics calculation logic
- **Methods**:
  - `calculate_spend(impressions, cpm)`: (impressions/1000) * cpm
  - `calculate_ctr(clicks, impressions)`: (clicks/impressions) * 100
  - `calculate_cpc(spend, clicks)`: spend/clicks
  - `calculate_cpa(spend, conversions)`: spend/conversions
  - `calculate_roas(revenue, spend)`: (revenue/spend) * 100
  - `safe_divide(a, b, default)`: Division with zero handling
- **Responsibilities**:
  - Implement all metric formulas
  - Handle division by zero
  - Return precise decimal values
  - Ensure consistent rounding
- **Formulas**:
  - Spend = (Impressions / 1000) × CPM
  - CTR = (Clicks / Impressions) × 100
  - CPC = Spend / Clicks
  - CPA = Spend / Conversions
  - ROAS = (Revenue / Spend) × 100

#### **`aggregator.py`**
- **Purpose**: Generate weekly and monthly summary data
- **Key Classes**:
  - `AggregatorService`: Aggregation coordinator
- **Methods**:
  - `generate_weekly_summary(client_id, week_start)`: Aggregate week
  - `generate_monthly_summary(client_id, month_start)`: Aggregate month
  - `calculate_deltas(current, previous)`: Week/month-over-week deltas
  - `_get_top_campaigns(client_id, date_range, limit)`: Top by conversions/revenue
  - `_get_top_creatives(client_id, date_range, limit)`: Top creatives
  - `_get_underperformers(client_id, date_range)`: Low CTR + high spend
- **Aggregation Logic**:
  - Query daily_metrics for date range
  - SUM raw metrics (impressions, clicks, conversions, revenue, spend)
  - Calculate derived metrics (CTR, CPC, CPA, ROAS)
  - Identify top performers (ORDER BY conversions/revenue DESC)
  - Calculate deltas vs. previous period
  - Store in weekly_summaries or monthly_summaries
- **Responsibilities**:
  - Generate summary data nightly
  - Calculate period-over-period deltas
  - Identify top/underperformers
  - Store JSONB data for top lists
  - Enable fast dashboard loading

#### **`router.py`**
- **Purpose**: Metrics query API endpoints
- **Endpoints**:
  - `GET /metrics/daily`: Query daily metrics
  - `GET /metrics/weekly`: Query weekly summaries
  - `GET /metrics/monthly`: Query monthly summaries
  - `GET /metrics/trends`: Get trend data
  - `GET /metrics/top-campaigns`: Top performers
  - `GET /metrics/top-creatives`: Top creatives
  - `GET /metrics/underperformers`: Underperforming items
- **Responsibilities**:
  - Accept filter parameters
  - Query database efficiently
  - Return paginated results
  - Support multiple aggregation levels

---

## **Module 9: Dashboard API (`app/dashboard/`)**

### **Purpose**
Provides consolidated dashboard data: summary stats, charts, tables, top performers, trends.

### **Files & Responsibilities**

#### **`service.py`**
- **Purpose**: Dashboard data aggregation and queries
- **Key Classes**:
  - `DashboardService`: Dashboard query coordinator
- **Methods**:
  - `get_dashboard_data(client_id, start_date, end_date)`: Full dashboard
  - `get_summary_stats(client_id, date_range)`: Overview KPIs
  - `get_campaign_performance(client_id, date_range)`: Campaign table
  - `get_strategy_performance(client_id, date_range)`: Strategy table
  - `get_creative_performance(client_id, date_range)`: Creative table
  - `get_trend_data(client_id, metric, date_range)`: Time series
  - `get_source_breakdown(client_id, date_range)`: By source comparison
- **Responsibilities**:
  - Aggregate data from multiple tables
  - Join campaigns, strategies, placements, creatives
  - Calculate summary statistics
  - Format data for charts
  - Apply client filtering automatically
  - Optimize queries with indexes
- **Query Patterns**:
  - Use CTEs for complex aggregations
  - Join daily_metrics with hierarchy tables
  - Use window functions for trends
  - Leverage indexes on (client_id, date)

#### **`schemas.py`**
- **Purpose**: Pydantic response schemas for dashboard
- **Key Classes**:
  - `DashboardSummary`: Summary stats (total impressions, clicks, spend, etc.)
  - `CampaignPerformance`: Campaign row (name, metrics, deltas)
  - `StrategyPerformance`: Strategy row
  - `CreativePerformance`: Creative row
  - `TrendDataPoint`: (date, value) pair
  - `SourceBreakdown`: Metrics by source
  - `DashboardResponse`: Complete dashboard payload
- **Nested Structure**:
  ```
  DashboardResponse {
    summary: DashboardSummary
    campaigns: List[CampaignPerformance]
    strategies: List[StrategyPerformance]
    creatives: List[CreativePerformance]
    trends: Dict[str, List[TrendDataPoint]]
    source_breakdown: List[SourceBreakdown]
    weekly_summary: WeeklySummaryResponse
    monthly_summary: MonthlySummaryResponse
  }
  ```

#### **`router.py`**
- **Purpose**: Dashboard API endpoint
- **Endpoints**:
  - `GET /dashboard`: Full dashboard data
  - `GET /dashboard/summary`: Summary stats only
  - `GET /dashboard/campaigns`: Campaign performance
  - `GET /dashboard/trends`: Trend charts
  - `GET /dashboard/source-breakdown`: Source comparison
- **Query Parameters**:
  - `start_date`, `end_date`: Date range
  - `source`: Filter by source
  - `campaign_id`: Filter by campaign
  - `metric`: Metric for trends
- **Responsibilities**:
  - Auto-filter by client for client users
  - Validate date ranges
  - Call service methods
  - Return structured JSON
  - Cache responses (optional)

---

## **Module 10: Shared ETL Components (`app/etl/`)**

### **Purpose**
Provides shared ETL utilities used by all three data sources: staging, transformation, loading.

### **Files & Responsibilities**

#### **`orchestrator.py`**
- **Purpose**: Unified ingestion coordinator for all sources
- **Key Classes**:
  - `ETLOrchestrator`: Multi-source coordinator
- **Methods**:
  - `run_all_sources(client_id, target_date)`: Run all 3 sources
  - `run_source(source, client_id, target_date)`: Run specific source
  - `get_ingestion_status(run_id)`: Check status
- **Responsibilities**:
  - Coordinate Surfside, Vibe, Facebook ETLs
  - Run sources in parallel (optional)
  - Track overall ingestion status
  - Handle cross-source dependencies
  - Aggregate ingestion logs

#### **`staging.py`**
- **Purpose**: Staging table operations
- **Key Classes**:
  - `StagingService`: Staging CRUD
- **Methods**:
  - `load_to_staging(records, client_id, source, run_id)`: Insert records
  - `get_staging_records(run_id)`: Query staging by run
  - `clear_staging(run_id)`: Delete after processing
  - `get_failed_records(run_id)`: Query validation failures
- **Responsibilities**:
  - Insert raw data to staging_media_raw
  - Tag with ingestion_run_id for tracking
  - Store raw JSONB for debugging
  - Enable reprocessing
  - Clean up after successful load

#### **`transformer.py`**
- **Purpose**: Transform staging data to normalized entities
- **Key Classes**:
  - `TransformerService`: Entity normalization
- **Methods**:
  - `process_staging(run_id, client_id)`: Transform all staging records
  - `_resolve_campaign(client_id, name, source)`: Find/create campaign
  - `_resolve_strategy(campaign_id, name)`: Find/create strategy
  - `_resolve_placement(strategy_id, name)`: Find/create placement
  - `_resolve_creative(placement_id, name)`: Find/create creative
  - `_build_entity_map(run_id)`: Cache entity lookups
- **Responsibilities**:
  - Query staging records
  - Look up or create campaigns
  - Look up or create strategies
  - Look up or create placements
  - Look up or create creatives
  - Maintain entity cache for performance
  - Handle unique constraint violations
- **Optimization**:
  - Batch queries for entity lookup
  - Cache results within transaction
  - Use upsert patterns

#### **`loader.py`**
- **Purpose**: Load final metrics to daily_metrics table
- **Key Classes**:
  - `LoaderService`: Metrics loading
- **Methods**:
  - `load_daily_metrics(run_id)`: Load from staging
  - `_calculate_metrics(record, cpm)`: Apply calculations
  - `_upsert_metrics(metrics_record)`: Insert or update
  - `_mark_processed(run_id)`: Update staging status
- **Responsibilities**:
  - Fetch client CPM rate
  - Calculate spend = (impressions/1000) * cpm
  - Calculate derived metrics (CTR, CPC, CPA, ROAS)
  - Insert to daily_metrics (upsert on conflict)
  - Handle duplicates gracefully
  - Update staging records as processed
- **Transaction Management**:
  - Use database transactions
  - Rollback on errors
  - Ensure atomicity

---

# **5. DATABASE ARCHITECTURE**

## **5.1 Database Schema Overview**

**Reference**: See `database_schema.sql` for complete schema

**Total Tables**: 16
- Core tables: 12
- Source-specific: 3
- Audit: 1

## **5.2 Entity Relationship Diagram**

```
┌────────────┐
│   users    │──────┐
└────────────┘      │
                    │ user_id
                    ▼
              ┌────────────┐
              │  clients   │
              └──────┬─────┘
                     │
       ┌─────────────┼─────────────┬─────────────┬────────────┐
       │             │             │             │            │
       ▼             ▼             ▼             ▼            ▼
┌────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│  campaigns │ │client_   │ │ingestion_│ │uploaded_ │ │  vibe_   │
│            │ │settings  │ │  logs    │ │  files   │ │credentials│
└──────┬─────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘
       │
       │ campaign_id
       ▼
┌────────────┐
│ strategies │
└──────┬─────┘
       │
       │ strategy_id
       ▼
┌────────────┐
│ placements │
└──────┬─────┘
       │
       │ placement_id
       ▼
┌────────────┐
│ creatives  │
└──────┬─────┘
       │
       │ (all entity FKs)
       ▼
┌────────────┐
│daily_      │
│metrics     │
└────────────┘
```

## **5.3 Key Design Patterns**

### **Hierarchy Pattern**
- Campaign → Strategy → Placement → Creative
- Cascade deletes enabled
- Unique constraints at each level

### **Temporal Data Pattern**
- `created_at`, `updated_at` on all entities
- Triggers for auto-update
- Effective dates for CPM rates

### **Staging Pattern**
- `staging_media_raw` for temporary storage
- `ingestion_run_id` for tracking
- JSONB `raw_data` for debugging

### **Audit Pattern**
- `ingestion_logs` for ETL tracking
- `audit_logs` for user actions
- Resolution tracking for errors

### **Denormalization Pattern**
- `weekly_summaries`, `monthly_summaries` for performance
- JSONB for top performers
- Pre-calculated metrics

## **5.4 Indexing Strategy**

**Critical Indexes**:
- `daily_metrics(client_id, date DESC)`: Dashboard queries
- `daily_metrics(campaign_id, date DESC)`: Campaign drilldown
- `campaigns(client_id, name, source)`: Entity lookup
- `ingestion_logs(run_date DESC, status)`: Monitoring
- `audit_logs(created_at DESC)`: Audit queries

**Composite Indexes**:
- Support filter + sort patterns
- Enable index-only scans

## **5.5 Data Volume Estimates**

**Daily Metrics**:
- 50k rows/client/source/day
- 3 sources = 150k rows/client/day
- 10 clients = 1.5M rows/day
- 1 year = 547M rows

**Retention Strategy**:
- Daily metrics: 13 months (hot)
- Older: Archive to S3 (cold)
- Summaries: Keep forever
- Staging: Delete after load
- Logs: 90 days

---

# **6. API ARCHITECTURE**

## **6.1 API Structure**

**Base URL**: `/api/v1`

**Route Organization**:
```
/api/v1/
├── /auth
│   ├── POST /login
│   ├── POST /register
│   ├── GET /me
│   └── POST /reset-password/{id}
│
├── /clients
│   ├── GET /
│   ├── POST /
│   ├── GET /{id}
│   ├── PUT /{id}
│   ├── POST /{id}/toggle
│   └── POST /{id}/cpm
│
├── /campaigns
│   ├── GET /
│   ├── POST /
│   ├── GET /{id}
│   ├── GET /{id}/tree
│   └── GET /{id}/performance
│
├── /facebook
│   ├── POST /upload
│   └── GET /uploads
│
├── /metrics
│   ├── GET /daily
│   ├── GET /weekly
│   ├── GET /monthly
│   └── GET /trends
│
├── /dashboard
│   ├── GET /
│   ├── GET /summary
│   └── GET /trends
│
└── /exports
    ├── GET /csv
    └── GET /pdf
```

## **6.2 Authentication Flow**

```
1. Client sends credentials
   POST /auth/login
   { "email": "user@example.com", "password": "secret" }

2. Server validates and returns JWT
   { "access_token": "eyJ...", "token_type": "bearer" }

3. Client includes JWT in subsequent requests
   Authorization: Bearer eyJ...

4. Server validates JWT on each request
   - Decode token
   - Verify signature
   - Check expiration
   - Load user from DB
   - Inject user into route handler
```

## **6.3 Request/Response Patterns**

### **List Endpoints**
- Support pagination: `?page=1&page_size=50`
- Support filtering: `?status=active&source=surfside`
- Support sorting: `?sort_by=created_at&order=desc`
- Return metadata: `{ "total": 100, "page": 1, "data": [...] }`

### **Error Responses**
```json
{
  "detail": "Human-readable error message",
  "error_code": "VALIDATION_ERROR",
  "field_errors": {
    "email": ["Invalid email format"]
  }
}
```

### **Success Responses**
```json
{
  "id": "uuid",
  "created_at": "2024-12-13T10:00:00Z",
  ...data fields...
}
```

## **6.4 Rate Limiting**

**Vibe API**: 15 requests/hour (enforced in client)
**Dashboard API**: No limits in V1
**Future**: Implement per-user rate limiting

---

# **7. INTEGRATION PATTERNS**

## **7.1 S3 Integration Pattern**

```
Configuration:
- AWS credentials in environment
- Bucket name configurable
- File naming pattern configurable

Connection:
- Initialize boto3 client on service start
- Reuse client across requests
- Handle temporary credential expiration

Error Handling:
- Retry on network errors (3 attempts)
- Fail on missing files
- Log all S3 operations

Security:
- Use IAM roles (preferred) or access keys
- Principle of least privilege
- No public bucket access
```

## **7.2 Vibe API Integration Pattern**

```
Authentication:
- Bearer token authentication
- API key from environment or database

Rate Limiting:
- Track request timestamps
- Sleep when limit reached
- Distribute requests across hour

Async Pattern:
- Create report (get report_id)
- Poll status every 30 seconds
- Download when ready
- Timeout after 20 attempts (10 minutes)

Error Handling:
- Retry on 5xx errors
- Fail on 4xx errors
- Handle expired download URLs
```

## **7.3 Email Integration Pattern**

```
Configuration:
- SMTP server settings in environment
- Alert recipient configurable

Alert Types:
- Ingestion failures (with error details)
- Missing files (with expected path)
- Validation errors (with error list)

Email Format:
- Plain text body
- Clear subject lines
- Actionable information
- Timestamps

Error Handling:
- Log SMTP errors
- Don't block on email failures
- Queue for retry (future)
```

---

# **8. SECURITY ARCHITECTURE**

## **8.1 Authentication Security**

**JWT Tokens**:
- Algorithm: HS256
- Expiration: 30 minutes
- Payload: user_id, email, role
- Secret key: Strong random string (256 bits)

**Password Security**:
- Hashing: bcrypt (12 rounds)
- Minimum length: 8 characters
- Stored as hash only (never plaintext)
- Password reset: Admin-only in V1

## **8.2 Authorization (RBAC)**

**Roles**:
- Admin: Full access to all resources
- Client: Access to own client data only

**Access Control**:
- Admin can create/update/delete all entities
- Client can view own metrics only
- Client cannot access other clients' data
- Enforced at DB query level + API level

## **8.3 Data Security**

**Database**:
- Row-Level Security (RLS) enabled
- Client data isolation enforced
- Encrypted connections (SSL/TLS)
- Regular backups

**API**:
- HTTPS only in production
- CORS configured for frontend origin
- Input validation on all endpoints
- SQL injection prevention (parameterized queries)

**File Uploads**:
- File type validation
- Size limits enforced
- Virus scanning (future)
- Isolated storage

## **8.4 Audit Logging**

**Logged Actions**:
- User logins
- Client creation/updates
- CPM changes
- Data uploads
- Export downloads

**Audit Data**:
- User ID
- Action type
- Entity type and ID
- Old and new values (JSONB)
- IP address
- User agent
- Timestamp

**Retention**: 2 years, then archive

---

# **9. DEPLOYMENT ARCHITECTURE**

## **9.1 Infrastructure Components**

```
┌─────────────────────────────────────────────────────────┐
│                     Load Balancer                        │
│                     (Nginx/ALB)                          │
└────────────┬────────────────────────────────────────────┘
             │
             │ HTTPS
             ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Application                     │
│                  (Uvicorn workers)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Worker 1 │  │ Worker 2 │  │ Worker N │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└────────────┬──────────────┬─────────────────────────────┘
             │              │
             │              │
    ┌────────▼──────┐  ┌───▼────────┐
    │  PostgreSQL   │  │  APScheduler│
    │   Database    │  │  (Scheduler)│
    └───────────────┘  └────────────┘
```

## **9.2 Deployment Options**

### **Option 1: Docker + Docker Compose**
```yaml
services:
  api:
    image: dashboard-api:latest
    ports: ["8000:8000"]
    depends_on: [db]
    environment: [...]

  db:
    image: postgres:14
    volumes: [postgres_data:/var/lib/postgresql/data]

  scheduler:
    image: dashboard-api:latest
    command: python -m app.jobs.scheduler
    depends_on: [db]
```

### **Option 2: Kubernetes**
- Deployment for API (multiple replicas)
- StatefulSet for PostgreSQL
- CronJob for scheduled tasks
- Secrets for environment variables
- ConfigMaps for configuration

### **Option 3: Cloud Platform**
- AWS: ECS + RDS + S3
- GCP: Cloud Run + Cloud SQL + Cloud Storage
- Azure: App Service + Azure Database

## **9.3 Environment Configuration**

**Development**:
- Local PostgreSQL
- Debug logging enabled
- No HTTPS
- Disable email alerts

**Staging**:
- Cloud database
- Production-like setup
- Test data only
- Email to test address

**Production**:
- High-availability database
- Multiple API workers
- HTTPS enforced
- Real email alerts
- Monitoring enabled

## **9.4 Monitoring & Observability**

**Metrics**:
- API response times
- Request rate
- Error rate
- Database query performance
- ETL job success/failure rate

**Logging**:
- Structured JSON logs
- Centralized log aggregation (CloudWatch, Datadog, etc.)
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Correlation IDs for request tracing

**Alerting**:
- Failed ETL jobs
- High error rates
- Database connection issues
- Disk space low
- High response times

**Tools**:
- Sentry: Error tracking
- Prometheus + Grafana: Metrics
- CloudWatch/Datadog: Logs and metrics
- UptimeRobot: Uptime monitoring

---

# **10. FILE STRUCTURE COMPLETE REFERENCE**

```
server/
│
├── database_schema.sql              # PostgreSQL schema (16 tables)
├── .env                             # Environment variables (not in git)
├── .env.example                     # Environment template
├── requirements.txt                 # Python dependencies
├── README.md                        # Project documentation
├── Dockerfile                       # Docker image definition
├── docker-compose.yml               # Local development setup
│
├── alembic/                         # Database migrations
│   ├── env.py                       # Alembic configuration
│   ├── script.py.mako               # Migration template
│   ├── alembic.ini                  # Alembic settings
│   └── versions/                    # Migration files
│       └── 001_initial.py
│
├── app/
│   ├── __init__.py                  # App package init
│   ├── main.py                      # FastAPI app + startup logic
│   │
│   ├── core/                        # MODULE 1: Foundation
│   │   ├── __init__.py
│   │   ├── config.py                # Settings class, env vars
│   │   ├── database.py              # SQLAlchemy engine, session
│   │   ├── logging.py               # Logging setup
│   │   ├── email.py                 # Email service (SMTP)
│   │   └── exceptions.py            # Custom exceptions
│   │
│   ├── auth/                        # MODULE 2: Authentication
│   │   ├── __init__.py
│   │   ├── models.py                # User ORM model
│   │   ├── schemas.py               # Pydantic schemas (login, register, etc.)
│   │   ├── security.py              # JWT, password hashing
│   │   ├── dependencies.py          # get_current_user, require_admin
│   │   └── router.py                # /auth endpoints
│   │
│   ├── clients/                     # MODULE 3: Client Management
│   │   ├── __init__.py
│   │   ├── models.py                # Client, ClientSettings models
│   │   ├── schemas.py               # Client DTOs
│   │   ├── service.py               # Business logic (CRUD, CPM)
│   │   └── router.py                # /clients endpoints
│   │
│   ├── campaigns/                   # MODULE 4: Campaign Hierarchy
│   │   ├── __init__.py
│   │   ├── models.py                # Campaign, Strategy, Placement, Creative
│   │   ├── schemas.py               # Hierarchy DTOs
│   │   ├── service.py               # Hierarchy management
│   │   └── router.py                # /campaigns endpoints
│   │
│   ├── surfside/                    # MODULE 5: Surfside Integration
│   │   ├── __init__.py
│   │   ├── s3_service.py            # AWS S3 operations (boto3)
│   │   ├── parser.py                # CSV/XLSX parsing (pandas)
│   │   ├── etl.py                   # ETL pipeline coordinator
│   │   └── scheduler.py             # Daily cron job (APScheduler)
│   │
│   ├── vibe/                        # MODULE 6: Vibe Integration
│   │   ├── __init__.py
│   │   ├── api_client.py            # Async HTTP client (httpx)
│   │   ├── models.py                # VibeCredentials, VibeReportRequest
│   │   ├── service.py               # Vibe coordinator (multi-client)
│   │   ├── parser.py                # Vibe CSV parsing
│   │   ├── etl.py                   # Vibe ETL pipeline
│   │   └── scheduler.py             # Daily API pull job
│   │
│   ├── facebook/                    # MODULE 7: Facebook Integration
│   │   ├── __init__.py
│   │   ├── upload_handler.py        # File upload processing
│   │   ├── validator.py             # File & data validation
│   │   ├── parser.py                # Facebook CSV parsing
│   │   ├── etl.py                   # Facebook ETL pipeline
│   │   ├── models.py                # UploadedFile model
│   │   └── router.py                # /facebook/upload endpoint
│   │
│   ├── metrics/                     # MODULE 8: Metrics & Aggregation
│   │   ├── __init__.py
│   │   ├── models.py                # DailyMetrics, WeeklySummary, MonthlySummary
│   │   ├── schemas.py               # Metrics DTOs
│   │   ├── calculator.py            # CPM calculations, formulas
│   │   ├── aggregator.py            # Weekly/monthly rollups
│   │   └── router.py                # /metrics endpoints
│   │
│   ├── dashboard/                   # MODULE 9: Dashboard API
│   │   ├── __init__.py
│   │   ├── service.py               # Dashboard queries
│   │   ├── schemas.py               # Dashboard response DTOs
│   │   └── router.py                # /dashboard endpoint
│   │
│   ├── exports/                     # MODULE 9.5: Export Functionality
│   │   ├── __init__.py
│   │   ├── csv_export.py            # CSV generation
│   │   ├── pdf_export.py            # PDF generation (ReportLab)
│   │   └── router.py                # /exports endpoints
│   │
│   ├── etl/                         # MODULE 10: Shared ETL
│   │   ├── __init__.py
│   │   ├── orchestrator.py          # Multi-source coordinator
│   │   ├── staging.py               # Staging table operations
│   │   ├── transformer.py           # Entity normalization
│   │   └── loader.py                # Metrics loading
│   │
│   ├── jobs/                        # Scheduled Jobs
│   │   ├── __init__.py
│   │   ├── scheduler.py             # APScheduler setup
│   │   ├── daily_ingestion.py       # Daily ETL job (all sources)
│   │   └── summaries.py             # Weekly/monthly aggregation
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── api.py               # Router aggregator
│   │
│   └── models/                      # (Optional) Centralized models
│       └── __init__.py              # Import all models
│
├── tests/                           # Test suite
│   ├── __init__.py
│   ├── conftest.py                  # Pytest fixtures
│   ├── test_auth/
│   │   ├── test_security.py
│   │   └── test_endpoints.py
│   ├── test_clients/
│   │   ├── test_service.py
│   │   └── test_endpoints.py
│   ├── test_surfside/
│   │   ├── test_s3_service.py
│   │   ├── test_parser.py
│   │   └── test_etl.py
│   ├── test_vibe/
│   │   ├── test_api_client.py
│   │   └── test_etl.py
│   ├── test_facebook/
│   │   ├── test_validator.py
│   │   └── test_upload.py
│   ├── test_metrics/
│   │   ├── test_calculator.py
│   │   └── test_aggregator.py
│   └── test_etl/
│       ├── test_staging.py
│       ├── test_transformer.py
│       └── test_loader.py
│
├── uploads/                         # File upload storage (gitignored)
├── logs/                            # Application logs (gitignored)
└── scripts/                         # Utility scripts
    ├── create_admin.py              # Create initial admin user
    ├── seed_data.py                 # Load sample data
    └── run_backfill.py              # Manual backfill script
```

---

# **APPENDIX A: CRITICAL IMPLEMENTATION NOTES**

## **A.1 CPM Calculation Logic**

```
Spend Calculation:
  spend = (impressions / 1000) * client_cpm

Derived Metrics:
  CTR = (clicks / impressions) * 100
  CPC = spend / clicks
  CPA = spend / conversions
  ROAS = (conversion_revenue / spend) * 100

Division by Zero Handling:
  - All divisions check denominator != 0
  - Return 0 or None if division would fail
  - Use safe_divide() helper function

Decimal Precision:
  - CPM: 4 decimals (e.g., 15.0000)
  - Spend: 2 decimals (currency)
  - CTR: 6 decimals (percentage)
  - CPC/CPA: 4 decimals
  - ROAS: 4 decimals
```

## **A.2 Data Source Mapping**

### **Surfside Mapping**:
```
Date → date
Campaign → campaign_name
Strategy → strategy_name
Placement → placement_name
Creative → creative_name
Impressions → impressions
Clicks → clicks
Conversions → conversions
Conversion Revenue → conversion_revenue
CTR → ctr (or calculated)
```

### **Vibe Mapping**:
```
date → date
campaign_name → campaign_name
strategy_name → strategy_name
placement_name → placement_name
creative_name → creative_name
impressions → impressions
clicks → clicks
conversions → conversions
revenue → conversion_revenue
```

### **Facebook Mapping**:
```
Date → date
Campaign Name → campaign_name
Ad Set Name → strategy_name
Ad Name → placement_name AND creative_name (SAME VALUE)
Impressions → impressions
Clicks → clicks
Conversions → conversions
Revenue → conversion_revenue
```

## **A.3 Scheduled Job Timings**

```
5:00 AM - Surfside Ingestion
  - Download yesterday's S3 file
  - Parse and load
  - Duration: ~10-15 minutes

6:00 AM - Vibe API Pull
  - Create reports for all clients
  - Poll until ready
  - Download and load
  - Duration: ~20-30 minutes (due to async + rate limiting)

7:00 AM - Summary Aggregation
  - Generate weekly summaries (on Mondays)
  - Generate monthly summaries (on 1st of month)
  - Duration: ~5 minutes

All times in UTC
```

## **A.4 Error Handling Strategy**

```
ETL Errors:
  - Log to ingestion_logs table
  - Set status='failed'
  - Store error message and traceback
  - Send email alert to admin
  - Continue processing other clients

API Errors:
  - Return appropriate HTTP status codes
  - Provide user-friendly error messages
  - Log detailed error for debugging
  - Don't expose internal details

Database Errors:
  - Rollback transaction
  - Log error with query context
  - Retry once on deadlock
  - Fail gracefully

External Service Errors:
  - Retry with exponential backoff
  - Circuit breaker after 5 failures
  - Fallback to cached data (if applicable)
  - Alert on sustained failures
```

---

# **APPENDIX B: DEVELOPMENT WORKFLOW**

## **B.1 Setup Steps**

1. Clone repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and configure
6. Start PostgreSQL (Docker or local)
7. Run migrations: `alembic upgrade head`
8. Create admin user: `python scripts/create_admin.py`
9. Start server: `uvicorn app.main:app --reload`
10. Access docs: http://localhost:8000/docs

## **B.2 Testing Workflow**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific module
pytest tests/test_auth/

# Run with verbose output
pytest -v

# Run in parallel
pytest -n auto
```

## **B.3 Database Migration Workflow**

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Review migration file
# Edit if needed

# Apply migration
alembic upgrade head

# Rollback one version
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

---

# **CONCLUSION**

This architecture document provides complete specifications for implementing the Dashboard Application backend. Every module, file, class, method, and integration pattern is described in detail without code implementation.

**Next Steps**:
1. Review and validate architecture decisions
2. Set up development environment
3. Implement modules sequentially (start with Module 1)
4. Write tests alongside implementation
5. Deploy to staging environment
6. Load test with production-like data volumes
7. Deploy to production

**Success Criteria**:
- All 3 data sources ingesting successfully
- Dashboard loading in <2 seconds
- 99.9% uptime for API
- Zero data loss during ingestion
- Secure authentication and authorization
- Comprehensive error logging and alerting

---

**END OF SYSTEM ARCHITECTURE DOCUMENT**

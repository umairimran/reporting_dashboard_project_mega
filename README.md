# Dashboard Application - Comprehensive Project Guide

**Project Repository:** reporting_dashboard_project_mega  
**Owner:** umairimran  
**Last Updated:** December 13, 2025  
**Status:** In Development

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Glossary of Terms](#glossary-of-terms)
3. [Data Sources & Integration](#data-sources--integration)
4. [Technical Architecture](#technical-architecture)
5. [Functional Requirements](#functional-requirements)
6. [Technical Requirements](#technical-requirements)
7. [Deliverables](#deliverables)
8. [Development Roadmap](#development-roadmap)
9. [Implementation Checklist](#implementation-checklist)
10. [API Documentation](#api-documentation)
11. [Data Schema & Models](#data-schema--models)
12. [Security & Compliance](#security--compliance)
13. [Testing Strategy](#testing-strategy)
14. [Deployment Strategy](#deployment-strategy)
15. [Reference Documentation](#reference-documentation)

---

## Executive Summary

### Project Overview
This project involves developing a **comprehensive dashboard web application** that aggregates and visualizes advertising campaign data from three distinct data sources. The dashboard will provide unified reporting and analytics capabilities for marketing campaign performance tracking.

### Business Objectives
- **Centralized Data Visualization:** Consolidate data from Surfside, Vibe API, and Facebook into a single dashboard
- **Real-time Insights:** Provide up-to-date campaign performance metrics
- **Multi-Source Integration:** Handle diverse data ingestion methods (S3, API, Manual Upload)
- **User-Friendly Interface:** Enable non-technical users to analyze campaign data effectively

### Key Stakeholders
- **Client:** End-user requiring dashboard functionality
- **Development Team:** Responsible for implementation
- **Data Providers:** Surfside, Vibe, Facebook (Meta)

### Success Criteria
- Successfully integrate all three data sources
- Display accurate, synchronized data across all sources
- Provide intuitive UI/UX for data exploration
- Ensure data refresh mechanisms work correctly
- Meet performance benchmarks for data loading and visualization

---

## Glossary of Terms

### General Terms

**Dashboard**  
A visual interface displaying key metrics, KPIs, and data visualizations in a centralized location.

**ETL (Extract, Transform, Load)**  
Process of extracting data from sources, transforming it into usable format, and loading it into a destination system.

**API (Application Programming Interface)**  
A set of protocols and tools for building software applications and enabling communication between systems.

**CSV (Comma-Separated Values)**  
A file format that stores tabular data in plain text, with each line representing a row and commas separating columns.

**S3 (Amazon Simple Storage Service)**  
Cloud-based object storage service used for storing and retrieving data.

**Backend**  
Server-side application logic, database interactions, and API endpoints that power the frontend.

**Frontend**  
Client-side user interface that users interact with directly in their web browsers.

### Marketing & Advertising Terms

**CPM (Cost Per Mille/Thousand)**  
The cost an advertiser pays for one thousand advertisement impressions.

**Impressions**  
The number of times an advertisement is displayed, regardless of whether it was clicked.

**CTR (Click-Through Rate)**  
Percentage of users who click on an ad after seeing it (Clicks ÷ Impressions × 100).

**ROAS (Return on Ad Spend)**  
Revenue generated for every dollar spent on advertising.

**Campaign**  
A coordinated series of advertisements promoting a specific goal or product.

**Strategy**  
A specific approach or tactic within a campaign (e.g., retargeting, demographic targeting).

**Creative**  
The actual advertisement content (video, image, text) shown to users.

**Attribution Window**  
The time period during which a conversion can be credited to an ad interaction (e.g., 7 days, 30 days).

**Conversion**  
A desired action taken by a user (purchase, signup, download, etc.).

**Household**  
Unique residential unit reached by an advertisement (CTV metric).

**Frequency**  
Average number of times each household/user saw an advertisement.

### Data Source Specific Terms

**Surfside**  
A data provider whose data is stored in S3 and pulled into the application backend.

**Vibe (CTV Platform)**  
Connected TV advertising platform providing campaign performance data via API.

**CTV (Connected TV)**  
Television content accessed via internet-connected devices (smart TVs, streaming devices).

**DMA (Designated Market Area)**  
Geographic regions used for media market analysis.

**MMP (Mobile Measurement Partner)**  
Third-party attribution platform for tracking mobile app installs and events.

**Advertiser ID**  
Unique identifier for an advertising account in the Vibe platform.

**Strategy ID**  
Unique identifier for a specific advertising strategy within a campaign.

**Campaign ID**  
Unique identifier for an advertising campaign.

**App ID**  
Identifier for mobile applications (iOS or Android) where events are tracked.

**Purchase ID**  
Unique identifier for purchase events used for reconciliation.

### Technical Terms

**REST API**  
Representational State Transfer - architectural style for building web services.

**Async (Asynchronous)**  
Operations that don't block execution while waiting for completion.

**Report ID**  
Unique identifier assigned to a generated report in the Vibe API system.

**Rate Limiting**  
Restriction on the number of API requests allowed within a time period.

**Authentication**  
Process of verifying the identity of a user or system (e.g., API keys).

**Endpoint**  
A specific URL where an API can access resources.

**Payload**  
Data sent in an API request body.

**Dimensions**  
Categories by which data can be broken down (e.g., campaign name, date, geography).

**Metrics**  
Quantitative measurements (e.g., spend, impressions, conversions).

**Filters**  
Criteria used to narrow down data results.

**Granularity**  
Level of detail in time-based aggregation (hour, day, week, month).

**Timezone**  
Geographic time zone for interpreting date/time data.

---

## Data Sources & Integration

### Overview of Data Sources

The dashboard integrates data from **three distinct sources**, each with different integration methods:

| Data Source | Integration Method | Data Format | Update Frequency | Complexity |
|------------|-------------------|-------------|------------------|-----------|
| **Surfside** | S3 Bucket → Backend | CSV/Excel | Batch (Scheduled) | Medium |
| **Vibe** | REST API | JSON/CSV | On-Demand | High |
| **Facebook** | Manual Upload | CSV | Manual | Low |

---

### 1. Surfside Integration

#### Description
Surfside data is automatically pulled from their system into an **S3 bucket** managed by the backend infrastructure. The application retrieves this data from S3 for processing and display.

#### Data Flow
```
Surfside Platform → S3 Bucket (Backend) → Application Database → Dashboard UI
```

#### Integration Details

**Storage Location:** Amazon S3 Bucket (Backend-managed)  
**Data Format:** CSV/Excel files  
**Sample Data:** Available in `data/surfside.xlsx`  
**Update Mechanism:** Scheduled batch processing

#### Implementation Requirements

**Backend Tasks:**
- Configure S3 bucket access (AWS credentials, IAM roles)
- Implement S3 file watcher/listener for new data
- Create ETL pipeline to process Surfside CSV files
- Parse and validate CSV structure
- Transform data into application schema
- Load data into application database
- Implement error handling for malformed files
- Set up logging for data ingestion jobs

**Data Processing Steps:**
1. Monitor S3 bucket for new Surfside files
2. Download file when detected
3. Validate file structure and data integrity
4. Parse CSV and extract relevant fields
5. Transform data to match database schema
6. Perform data quality checks
7. Insert/update records in database
8. Archive processed file
9. Log success/failure status

**Technical Considerations:**
- Handle large file sizes efficiently (streaming)
- Implement incremental updates vs. full refresh
- Manage duplicate data handling
- Set up retry mechanism for failed uploads
- Configure data retention policies

#### Data Schema (Surfside)
*Based on surfside.xlsx sample file - exact fields to be confirmed after file analysis*

Expected fields may include:
- Campaign identifiers
- Impressions, clicks, conversions
- Cost metrics
- Date/time stamps
- Geographic data
- Demographic information

---

### 2. Vibe API Integration

#### Description
Vibe provides a comprehensive **REST API** for retrieving Connected TV (CTV) advertising campaign data. This is the most complex integration requiring API authentication, asynchronous report generation, and regular polling.

#### Data Flow
```
Dashboard → Vibe API (Create Report) → Poll Status → Download Report → Process Data → Database → UI
```

#### API Overview

**Base URL:** `https://clear-platform.vibe.co/rest/reporting/v1/`  
**Authentication:** API Key via `X-API-KEY` header  
**API Version:** v1  
**Documentation:** https://help.vibe.co/en/articles/8943325-vibe-api-reporting

#### Key Endpoints

| Endpoint | Method | Purpose | Rate Limit |
|----------|--------|---------|-----------|
| `/create_async_report` | POST | Generate report request | 15 requests/hour/tenant |
| `/get_report_status` | GET | Check report status & get download URL | Once per 10 seconds per report |
| `/get_advertiser_ids` | GET | List all advertiser IDs | No limit |
| `/get_app_ids` | GET | Get app IDs for advertiser | No limit |
| `/get_campaign_details` | GET | Get campaign/strategy IDs | No limit |
| `/get_purchase_ids` | POST | Get purchase event details | No limit |

#### Authentication Setup

**Obtaining API Key:**
1. Log into Vibe account
2. Navigate to: **Account Settings → Developer Tool → API Keys**
3. Click "Create API Key"
4. Enter a descriptive name
5. Copy and securely store the key (only shown once)
6. If lost, generate a new key

**Using API Key:**
```http
X-API-KEY: your_api_key_here
```

**Sample API Key Provided:** *(Client should provide actual key for testing)*

#### API Workflow

**Step 1: Create Async Report**

POST to `/create_async_report` with parameters:

**Required Parameters:**
- `advertiser_id`: Advertiser UUID(s)
- `start_date`: YYYY-MM-DD format
- `end_date`: YYYY-MM-DD format (exclusive)
- `metrics`: Array of metrics to retrieve
- `format`: "JSON" or "CSV"

**Optional Parameters:**
- `dimensions`: Array of dimensions for data breakdown
- `filters`: Array of filter objects
- `timezone`: Timezone identifier (default: UTC)
- `granularity`: "hour", "day", "week", "month"
- `attribution_window`: "1h", "6h", "12h", "24h", "48h", "72h", "7 days", "30 days"

**Response:**
```json
{
  "report_id": "946fcf93-0a58-4dee-9534-88ff133b8ec8"
}
```

**Step 2: Poll Report Status**

GET `/get_report_status?report_id={report_id}`

**Polling Strategy:**
- Wait 10 seconds between polls
- Set timeout after 30 minutes
- Check for status: "created", "processing", "done", "error"

**Response (When Ready):**
```json
{
  "status": "done",
  "report_id": "946fcf93-0a58-4dee-9534-88ff133b8ec8",
  "generated_url_time": "2024-01-01T08:26:18.457690+00:00",
  "url_expiration_time": "2024-01-30T08:26:18.457690+00:00",
  "download_url": "https://xxx.amazonaws.com/xxxxxxxxx"
}
```

**Step 3: Download & Process Report**

- Download file from `download_url` (valid for 24 hours)
- Parse JSON or CSV data
- Transform to application schema
- Load into database

#### Available Metrics

**Core Metrics:**
- `spend`: Ad spend in USD
- `impressions`: Number of ad impressions
- `households`: Unique households reached
- `frequency`: Average views per household
- `cpm`: Cost per thousand impressions
- `completed_views`: 100% completion rate views
- `cost_per_completed_view`: Cost per completed view
- `view_through_rate`: Completion rate percentage

**Conversion Metrics:**
- `installs`: App installs (MMP)
- `cost_per_install`: CPI in USD
- `number_of_purchases`: Purchase events
- `cost_per_purchase`: Cost per purchase
- `amount_of_purchases`: Purchase revenue in USD
- `number_of_signups`: Signup events
- `cost_per_signup`: Cost per signup
- `roas`: Return on ad spend (%)

**Web Pixel Metrics:**
- `number_of_page_views`: Page views
- `cost_per_page_view`: Cost per page view
- `number_of_sessions`: Web sessions
- `cost_per_session`: Cost per session
- `number_of_leads`: Lead events
- `cost_per_lead`: Cost per lead

**Custom Events:**
- `number_of_custom_1`, `cost_per_custom_1`
- `number_of_custom_2`, `cost_per_custom_2`
- `number_of_custom_3`, `cost_per_custom_3`

#### Available Dimensions

**Campaign Structure:**
- `advertiser_id`, `advertiser_name`
- `campaign_id`, `campaign_name`
- `strategy_id`, `strategy_name`
- `creative_id`, `creative_name`

**Technical:**
- `impression_date`: YYYY-MM-DD (always included)
- `app_id`: iOS/Android app identifier
- `os`: Operating system (Android, iOS, Web)
- `purchase_id`: Purchase event identifier
- `screen`: Device type (TV, Mobile, Tablet)
- `channel_name`: Content channel (Pluto, ESPN, Tubi, etc.)

**Geographic:**
- `geo_region`: US state
- `geo_metro`: DMA (Designated Market Area)
- `geo_city`: City
- `geo_zip`: ZIP code

**Audience Segments:**
- `segment_ages`: Age groups
- `segment_career`: Career categories
- `segment_education`: Education levels
- `segment_estimated_incomes`: Income ranges
- `segment_estimated_net_worth`: Net worth ranges
- `segment_ethnicity`: Ethnicity
- `segment_family_composition`: Family structure
- `segment_genders`: Gender
- `segment_interests`: Interest categories
- `segment_languages`: Languages
- `segment_political_status`: Political affiliation
- `segment_retargeting`: Retargeting audiences

#### Filters

Available filters (use in `filters` array):
- `app_id`: App identifier
- `campaign_id`: Campaign UUID
- `strategy_id`: Strategy UUID

**Filter Format:**
```json
{
  "filters": [
    {
      "dimension": "campaign_id",
      "values": ["2b54b588-19a9-4424-a368-b30df9fea6ae"]
    },
    {
      "dimension": "strategy_id",
      "values": ["763c5d2b-68eb-4ddd-9c34-ad6025c24ffb"]
    }
  ]
}
```

#### Rate Limits & Constraints

**Rate Limits:**
- 15 requests per hour for `/create_async_report`
- 1 request per 10 seconds per report for `/get_report_status`

**Response Headers:**
- `x-rate-limit`: Max requests in window
- `x-rate-limit-left`: Remaining requests
- `x-rate-limit-reset-at`: Unix timestamp of reset
- `x-rate-limit-retry-after`: Seconds until reset (when exceeded)

**Data Constraints:**
- Maximum 45 days per query
- Data updated hourly
- Data may be partial for 6-7 hours post-impression
- **Best Practice:** Always fetch at least 1 full day of past data
- **Best Practice:** Re-fetch last day's data to ensure completeness
- Report URLs expire after 24 hours
- Set 30-minute timeout for report generation

#### Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Continue |
| 400 | Bad request | Check parameters |
| 403 | Access denied | Verify API key and advertiser_id ownership |
| 404 | Not found | Verify advertiser exists |
| 422 | Invalid format | Check payload structure |
| 500 | Internal error | Retry request |

#### Implementation Requirements

**Backend Tasks:**
1. Store Vibe API key securely (environment variables)
2. Implement API client with authentication
3. Create async report generation workflow
4. Implement polling mechanism with backoff
5. Handle report download and parsing
6. Implement rate limit tracking and queuing
7. Set up error handling and retry logic
8. Create data transformation pipeline
9. Implement incremental data refresh strategy
10. Log all API interactions for debugging

**Frontend Tasks:**
1. Create UI for triggering data refresh
2. Display sync status and last update time
3. Show progress during async report generation
4. Handle and display error messages
5. Allow users to select date ranges
6. Provide filtering options (campaigns, strategies)

**Scheduled Jobs:**
- Daily automated data pull for previous day
- Hourly updates for current day (if needed)
- Re-fetch last day data to ensure completeness

#### Sample API Request (Python)

```python
import requests
import time

# Configuration
ADVERTISER_ID = "<ADVERTISER_ID>"
START_DATE = "2024-08-01"
END_DATE = "2024-08-02"
X_API_KEY = "<API_KEY>"

# Step 1: Create async report
payload = {
    "advertiser_id": ADVERTISER_ID,
    "metrics": [
        "spend",
        "impressions",
        "installs",
        "number_of_purchases",
        "amount_of_purchases"
    ],
    "dimensions": ["campaign_name", "strategy_name"],
    "start_date": START_DATE,
    "end_date": END_DATE,
    "timezone": "America/New_York",
    "format": "csv"
}

headers = {'X-API-KEY': X_API_KEY}

# Generate report
create_response = requests.post(
    "https://clear-platform.vibe.co/rest/reporting/v1/create_async_report",
    json=payload,
    headers=headers
)
report_id = create_response.json()["report_id"]

# Step 2: Poll for completion
while True:
    status_response = requests.get(
        f"https://clear-platform.vibe.co/rest/reporting/v1/get_report_status?report_id={report_id}",
        headers=headers
    ).json()
    
    if status_response["status"] in ["done", "error"]:
        break
    
    time.sleep(10)  # Wait 10 seconds

# Step 3: Download report
if status_response["status"] == "done":
    download_url = status_response["download_url"]
    # Download and process the report
```

---

### 3. Facebook (Meta) Integration

#### Description
Facebook data will be **manually uploaded** by users through a file upload interface. This provides flexibility for users to upload data exported from Facebook Ads Manager.

#### Data Flow
```
Facebook Ads Manager → User Export → Manual Upload → Validation → Database → Dashboard UI
```

#### Integration Details

**Data Format:** CSV  
**Upload Method:** Web-based file upload interface  
**Sample Data:** To be provided by client  
**Update Frequency:** Manual (user-initiated)

#### Implementation Requirements

**Frontend Tasks:**
1. Create file upload interface
   - Drag-and-drop support
   - File selection button
   - File size validation (max limit)
   - File type validation (.csv only)
   - Upload progress indicator
2. Display upload history
3. Show validation results
4. Provide download template feature
5. Allow data preview before final import

**Backend Tasks:**
1. Create file upload endpoint
2. Implement file validation
   - Check file format
   - Validate CSV structure
   - Check required columns
   - Validate data types
3. Parse CSV file
4. Transform data to application schema
5. Detect and handle duplicates
6. Batch insert data into database
7. Return validation errors to user
8. Log upload activities
9. Implement file size limits
10. Secure file storage (temporary)

**Security Considerations:**
- Scan uploaded files for malware
- Limit file size (e.g., 50MB max)
- Validate file content (no malicious code)
- Sanitize file names
- Implement user authentication for uploads
- Track who uploaded what and when

**Data Processing:**
1. User selects CSV file
2. Frontend validates file type/size
3. File uploaded to server
4. Backend validates CSV structure
5. Data parsed and validated
6. Preview shown to user (optional)
7. User confirms import
8. Data inserted into database
9. Success/error message displayed
10. File archived or deleted

#### Expected Data Schema (Facebook)
*To be confirmed based on actual sample CSV*

Typical Facebook Ads data includes:
- Campaign ID, Campaign Name
- Ad Set ID, Ad Set Name
- Ad ID, Ad Name
- Date (delivery date)
- Impressions
- Clicks
- Spend
- Conversions
- CTR (Click-through rate)
- CPC (Cost per click)
- CPM (Cost per thousand impressions)
- Reach
- Frequency

---

### Data Synchronization Strategy

#### Sync Frequency

| Source | Frequency | Trigger | Notes |
|--------|-----------|---------|-------|
| Surfside | Daily | Scheduled job | Process new S3 files |
| Vibe | Daily + On-demand | Scheduled + Manual | API rate limits apply |
| Facebook | Manual | User upload | User-initiated |

#### Data Consistency

**Challenges:**
- Different update frequencies across sources
- Potential data delays (Vibe: 6-7 hours)
- Manual upload timing variance

**Solutions:**
- Display last update timestamp for each source
- Implement "data freshness" indicators
- Allow users to manually trigger refreshes
- Cache data appropriately
- Handle missing data gracefully

#### Data Deduplication

**Strategy:**
- Use unique identifiers (campaign ID + date)
- Implement upsert logic (update if exists, insert if new)
- Track data source and version
- Maintain audit trail of data changes

---

## Technical Architecture

### System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Dashboard   │  │   Data       │  │   Upload     │          │
│  │  UI          │  │   Filters    │  │   Interface  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   API Gateway     │
                    └─────────┬─────────┘
                              │
┌─────────────────────────────┴───────────────────────────────────┐
│                       BACKEND LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  S3 Sync     │  │  Vibe API    │  │  Upload      │          │
│  │  Service     │  │  Client      │  │  Handler     │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                  │
│         └──────────────────┼──────────────────┘                  │
│                            │                                     │
│                   ┌────────┴────────┐                           │
│                   │  Data Processing │                           │
│                   │  & ETL Pipeline  │                           │
│                   └────────┬────────┘                           │
└────────────────────────────┼──────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │    DATABASE     │
                    │   (PostgreSQL/  │
                    │    MySQL)       │
                    └─────────────────┘
                             │
┌────────────────────────────┴──────────────────────────────────┐
│                     EXTERNAL SERVICES                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   AWS S3     │  │  Vibe API    │  │  Facebook    │        │
│  │  (Surfside)  │  │  Platform    │  │  (Manual)    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└───────────────────────────────────────────────────────────────┘
```

### Technology Stack Recommendations

#### Frontend
**Framework Options:**
- **React.js** (Recommended) - Component-based, large ecosystem
- **Vue.js** - Simpler learning curve, good performance
- **Next.js** - React with SSR, great for SEO

**UI Libraries:**
- **Material-UI (MUI)** or **Ant Design** - Comprehensive component library
- **Tailwind CSS** - Utility-first CSS framework
- **Chart.js** or **Recharts** or **ApexCharts** - Data visualization

**State Management:**
- **Redux Toolkit** or **Zustand** - Global state management
- **React Query** or **SWR** - Server state management & caching

#### Backend
**Framework Options:**
- **Node.js + Express** - JavaScript/TypeScript full-stack
- **Python + FastAPI** - Modern, fast, auto-documentation
- **Python + Django** - Batteries-included framework
- **NestJS** - TypeScript, enterprise-grade structure

**Recommended:** **Python + FastAPI** for:
- Excellent data processing capabilities
- Easy integration with pandas for data transformation
- Fast async support for API calls
- Auto-generated API documentation
- Strong typing with Pydantic

#### Database
**Primary Database:**
- **PostgreSQL** (Recommended) - Robust, supports complex queries, JSON data
- **MySQL** - Reliable, wide adoption
- **MongoDB** - If flexible schema needed

**Caching Layer:**
- **Redis** - Fast in-memory caching for API responses

#### Cloud Infrastructure
**AWS Services:**
- **S3** - File storage (Surfside data)
- **EC2** or **ECS/Fargate** - Application hosting
- **RDS** - Managed database
- **Lambda** - Serverless functions for data processing
- **CloudWatch** - Logging and monitoring
- **IAM** - Access management

**Alternative:**
- **Google Cloud Platform (GCP)**
- **Microsoft Azure**
- **Heroku** (simpler deployment)

#### DevOps & Tools
- **Docker** - Containerization
- **Git** - Version control
- **GitHub Actions** or **GitLab CI/CD** - Automation
- **Nginx** - Reverse proxy
- **Let's Encrypt** - SSL certificates

### Database Schema Design

#### Core Tables

**1. campaigns**
```sql
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source VARCHAR(50) NOT NULL,  -- 'surfside', 'vibe', 'facebook'
    external_campaign_id VARCHAR(255) NOT NULL,
    campaign_name VARCHAR(500),
    advertiser_id VARCHAR(255),
    advertiser_name VARCHAR(500),
    status VARCHAR(50),
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source, external_campaign_id)
);
```

**2. strategies** (Vibe-specific)
```sql
CREATE TABLE strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id),
    external_strategy_id VARCHAR(255) NOT NULL,
    strategy_name VARCHAR(500),
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(campaign_id, external_strategy_id)
);
```

**3. daily_metrics**
```sql
CREATE TABLE daily_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source VARCHAR(50) NOT NULL,
    campaign_id UUID REFERENCES campaigns(id),
    strategy_id UUID REFERENCES strategies(id),
    date DATE NOT NULL,
    
    -- Core metrics
    spend DECIMAL(12,2),
    impressions INTEGER,
    clicks INTEGER,
    conversions INTEGER,
    
    -- Calculated metrics
    cpm DECIMAL(10,4),
    cpc DECIMAL(10,4),
    ctr DECIMAL(8,4),
    
    -- Vibe-specific metrics
    households INTEGER,
    frequency DECIMAL(8,2),
    completed_views INTEGER,
    view_through_rate DECIMAL(8,4),
    installs INTEGER,
    purchases INTEGER,
    purchase_amount DECIMAL(12,2),
    roas DECIMAL(8,4),
    
    -- Dimensions
    geo_region VARCHAR(100),
    geo_metro VARCHAR(100),
    channel_name VARCHAR(255),
    device_type VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(source, campaign_id, date, strategy_id)
);
```

**4. data_sync_logs**
```sql
CREATE TABLE data_sync_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source VARCHAR(50) NOT NULL,
    sync_type VARCHAR(50),  -- 'scheduled', 'manual', 'upload'
    status VARCHAR(50),  -- 'success', 'error', 'partial'
    records_processed INTEGER,
    records_inserted INTEGER,
    records_updated INTEGER,
    errors TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_by VARCHAR(255)
);
```

**5. uploaded_files**
```sql
CREATE TABLE uploaded_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source VARCHAR(50) NOT NULL,
    original_filename VARCHAR(500),
    file_size INTEGER,
    file_path VARCHAR(1000),
    uploaded_by VARCHAR(255),
    upload_status VARCHAR(50),
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### API Endpoints Design

#### Backend API Endpoints

**Authentication**
```
POST   /api/auth/login
POST   /api/auth/logout
POST   /api/auth/refresh
GET    /api/auth/user
```

**Dashboard Data**
```
GET    /api/dashboard/overview
GET    /api/dashboard/metrics?source=&start_date=&end_date=
GET    /api/dashboard/campaigns?source=
GET    /api/dashboard/trends?metric=&granularity=
```

**Data Sync**
```
POST   /api/sync/surfside/trigger
POST   /api/sync/vibe/trigger
GET    /api/sync/status
GET    /api/sync/history
```

**File Upload (Facebook)**
```
POST   /api/upload/facebook
GET    /api/upload/history
GET    /api/upload/:id/status
DELETE /api/upload/:id
```

**Campaigns**
```
GET    /api/campaigns?source=&status=
GET    /api/campaigns/:id
GET    /api/campaigns/:id/metrics
```

**Vibe Specific**
```
GET    /api/vibe/advertisers
GET    /api/vibe/campaigns/:advertiser_id
GET    /api/vibe/strategies/:campaign_id
POST   /api/vibe/report/create
GET    /api/vibe/report/:report_id/status
```

**Reports**
```
GET    /api/reports/performance?start_date=&end_date=
GET    /api/reports/comparison?sources[]=
POST   /api/reports/export
```

---

## Functional Requirements

### Core Features

#### 1. Data Integration Module

**FR-1.1: Surfside Data Import**
- System shall automatically detect new files in S3 bucket
- System shall parse CSV/Excel files from Surfside
- System shall validate data integrity before import
- System shall handle import errors gracefully
- System shall log all import activities

**FR-1.2: Vibe API Integration**
- System shall authenticate with Vibe API using API key
- System shall create async report requests
- System shall poll report status with proper rate limiting
- System shall download completed reports
- System shall handle API errors and retry failed requests
- System shall respect rate limits (15 requests/hour)

**FR-1.3: Facebook Manual Upload**
- System shall provide file upload interface
- System shall validate CSV file format
- System shall preview data before final import
- System shall provide clear error messages
- System shall track upload history

#### 2. Dashboard Visualization Module

**FR-2.1: Main Dashboard**
- Display key metrics overview (spend, impressions, conversions)
- Show metrics by data source
- Provide date range selector
- Display data freshness indicators
- Show trend visualizations (line charts, bar charts)

**FR-2.2: Campaign Performance View**
- List all campaigns across sources
- Display campaign-level metrics
- Allow sorting and filtering
- Provide drill-down capability
- Show campaign status and dates

**FR-2.3: Comparison View**
- Compare metrics across data sources
- Compare performance across time periods
- Show side-by-side metrics
- Highlight variances and anomalies

**FR-2.4: Geographic Analysis** (if data available)
- Display metrics by region/state
- Show DMA-level performance
- Provide map visualization

#### 3. Filtering & Search Module

**FR-3.1: Date Range Filtering**
- Select custom date ranges
- Provide preset ranges (Last 7 days, Last 30 days, This month, etc.)
- Support date comparison

**FR-3.2: Campaign Filtering**
- Filter by campaign name
- Filter by advertiser
- Filter by status (active, paused, completed)
- Multi-select capability

**FR-3.3: Source Filtering**
- Filter by data source
- View combined or individual source data
- Toggle source visibility

#### 4. Data Management Module

**FR-4.1: Data Refresh**
- Manual refresh trigger for each source
- Display last sync timestamp
- Show sync progress
- Provide sync history

**FR-4.2: Data Quality**
- Validate data completeness
- Detect and flag anomalies
- Show data coverage metrics

#### 5. Export & Reporting Module

**FR-5.1: Data Export**
- Export dashboard data to CSV
- Export filtered datasets
- Include metadata (date range, filters applied)

**FR-5.2: Scheduled Reports** (Future Enhancement)
- Generate automated reports
- Email report delivery
- Customizable report templates

### User Roles & Permissions (Optional)

**Admin**
- Full access to all features
- Manage data sources
- Configure integrations
- View all campaigns

**Analyst**
- View dashboards
- Filter and analyze data
- Export reports
- Cannot modify integrations

**Viewer**
- Read-only dashboard access
- Limited filter options

---

## Technical Requirements

### Performance Requirements

**PERF-1: Page Load Time**
- Dashboard should load within 3 seconds
- API responses should return within 1 second (90th percentile)

**PERF-2: Data Processing**
- Process Surfside files within 5 minutes (for files up to 100MB)
- Handle Vibe API report download within 10 minutes
- Process Facebook uploads within 2 minutes (for files up to 50MB)

**PERF-3: Concurrent Users**
- Support at least 20 concurrent users
- Maintain performance under load

**PERF-4: Database**
- Query optimization for large datasets (millions of records)
- Implement proper indexing
- Use pagination for large result sets

### Scalability Requirements

**SCALE-1: Data Volume**
- Handle at least 1 million metric records
- Support growth to 10 million records within 2 years

**SCALE-2: Horizontal Scaling**
- Application should support horizontal scaling
- Database should support read replicas

### Security Requirements

**SEC-1: Authentication**
- Implement secure user authentication
- Use JWT tokens or session management
- Support password complexity requirements

**SEC-2: API Security**
- Store API keys in environment variables (never in code)
- Encrypt sensitive data at rest
- Use HTTPS for all communications

**SEC-3: File Upload Security**
- Scan uploaded files for malware
- Validate file types and sizes
- Sanitize file names
- Implement access controls

**SEC-4: Data Privacy**
- Comply with data protection regulations
- Implement audit logging
- Secure database access

### Reliability Requirements

**REL-1: Uptime**
- Target 99.5% uptime
- Implement health checks

**REL-2: Error Handling**
- Graceful degradation
- Meaningful error messages
- Automated error logging

**REL-3: Data Integrity**
- Implement transaction management
- Regular database backups
- Data validation at all entry points

### Compatibility Requirements

**COMPAT-1: Browser Support**
- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

**COMPAT-2: Mobile Responsiveness**
- Dashboard should be responsive
- Support tablet and mobile devices

**COMPAT-3: API Versioning**
- Maintain API version compatibility
- Provide migration path for breaking changes

---

## Deliverables

### Phase 1: Foundation & Setup (Weeks 1-2)

**D1.1: Project Setup**
- ✅ Repository initialized
- ✅ README documentation
- [ ] Development environment setup
- [ ] CI/CD pipeline configuration
- [ ] Database schema design document

**D1.2: Technical Stack Decision**
- [ ] Frontend framework selected
- [ ] Backend framework selected
- [ ] Database selected
- [ ] Cloud infrastructure planned
- [ ] Third-party services identified

**D1.3: Design Assets**
- [ ] Wireframes for all main views
- [ ] UI/UX mockups
- [ ] Design system/style guide
- [ ] Prototype approval (reference: https://ai.studio/apps/drive/1367lVE8aOj5P6QYO3T0Lpy5ElbWoB8Ub)

### Phase 2: Backend Development (Weeks 3-6)

**D2.1: Core Backend Infrastructure**
- [ ] Database setup and migration scripts
- [ ] API framework implementation
- [ ] Authentication system
- [ ] Error handling middleware
- [ ] Logging system

**D2.2: Surfside Integration**
- [ ] S3 bucket access configuration
- [ ] File watcher/listener implementation
- [ ] CSV parser implementation
- [ ] ETL pipeline for Surfside data
- [ ] Scheduled job for automatic sync
- [ ] Unit tests for Surfside integration

**D2.3: Vibe API Integration**
- [ ] API client implementation
- [ ] Authentication handler
- [ ] Async report creation endpoint
- [ ] Report polling mechanism
- [ ] Rate limit handler
- [ ] Data transformation pipeline
- [ ] Error handling and retry logic
- [ ] Unit tests for Vibe integration

**D2.4: Facebook Upload System**
- [ ] File upload endpoint
- [ ] CSV validation logic
- [ ] File parsing and transformation
- [ ] Duplicate detection
- [ ] Upload history tracking
- [ ] Unit tests for upload system

**D2.5: API Endpoints**
- [ ] Dashboard data endpoints
- [ ] Campaign management endpoints
- [ ] Sync trigger endpoints
- [ ] Report generation endpoints
- [ ] API documentation (Swagger/OpenAPI)

### Phase 3: Frontend Development (Weeks 5-8)

**D3.1: Core UI Components**
- [ ] Navigation and layout
- [ ] Authentication UI (login/logout)
- [ ] Dashboard layout
- [ ] Reusable components library
- [ ] Responsive design implementation

**D3.2: Dashboard Views**
- [ ] Main overview dashboard
- [ ] Campaign performance view
- [ ] Comparison view
- [ ] Trend analysis charts
- [ ] Metric cards and visualizations

**D3.3: Filtering & Interaction**
- [ ] Date range selector
- [ ] Campaign filters
- [ ] Source filters
- [ ] Search functionality
- [ ] Sort and pagination

**D3.4: Data Management UI**
- [ ] Facebook file upload interface
- [ ] Sync trigger buttons
- [ ] Sync status indicators
- [ ] Sync history view
- [ ] Error message displays

**D3.5: Export & Reporting**
- [ ] CSV export functionality
- [ ] Report customization UI
- [ ] Export history

### Phase 4: Integration & Testing (Weeks 9-10)

**D4.1: System Integration**
- [ ] End-to-end data flow testing
- [ ] Frontend-Backend integration
- [ ] All three data sources integrated
- [ ] Data consistency validation

**D4.2: Testing**
- [ ] Unit tests (80%+ coverage)
- [ ] Integration tests
- [ ] API endpoint tests
- [ ] UI component tests
- [ ] End-to-end tests
- [ ] Load testing
- [ ] Security testing

**D4.3: Bug Fixes & Optimization**
- [ ] Bug tracking and resolution
- [ ] Performance optimization
- [ ] Query optimization
- [ ] Caching implementation

### Phase 5: Deployment & Launch (Weeks 11-12)

**D5.1: Deployment**
- [ ] Production environment setup
- [ ] Database migration to production
- [ ] Application deployment
- [ ] SSL certificate configuration
- [ ] Domain configuration

**D5.2: Monitoring & Logging**
- [ ] Application monitoring setup
- [ ] Error tracking (Sentry/similar)
- [ ] Performance monitoring
- [ ] Uptime monitoring
- [ ] Log aggregation

**D5.3: Documentation**
- [ ] User manual
- [ ] API documentation
- [ ] Deployment guide
- [ ] Troubleshooting guide
- [ ] Maintenance procedures

**D5.4: Training & Handoff**
- [ ] User training session
- [ ] Admin training
- [ ] Documentation walkthrough
- [ ] Support handoff

---

## Development Roadmap

### Timeline Overview (12 Weeks)

```
Week 1-2:   Foundation & Setup
Week 3-4:   Backend Core + Surfside Integration
Week 5-6:   Vibe API Integration + Facebook Upload
Week 7-8:   Frontend Development
Week 9-10:  Integration & Testing
Week 11-12: Deployment & Launch
```

### Detailed Sprint Plan

#### Sprint 1 (Weeks 1-2): Foundation

**Goals:**
- Set up development environment
- Finalize technical decisions
- Complete database design
- Set up CI/CD

**Key Tasks:**
- [ ] Initialize repository with proper structure
- [ ] Set up development, staging, production environments
- [ ] Create database schema
- [ ] Design API contract
- [ ] Review and approve UI/UX designs
- [ ] Set up project management tools

**Deliverables:**
- Project repository
- Database schema document
- API specification
- Approved mockups

#### Sprint 2 (Weeks 3-4): Backend Core + Surfside

**Goals:**
- Implement core backend functionality
- Complete Surfside integration
- Set up authentication

**Key Tasks:**
- [ ] Implement database models
- [ ] Create authentication system
- [ ] Build S3 integration
- [ ] Implement Surfside CSV parser
- [ ] Create Surfside ETL pipeline
- [ ] Build basic API endpoints
- [ ] Write unit tests

**Deliverables:**
- Working authentication
- Surfside data import functional
- Core API endpoints

#### Sprint 3 (Weeks 5-6): Vibe API + Facebook Upload

**Goals:**
- Complete Vibe API integration
- Implement Facebook upload system
- Finalize all data ingestion

**Key Tasks:**
- [ ] Build Vibe API client
- [ ] Implement async report workflow
- [ ] Create rate limiting logic
- [ ] Build file upload system
- [ ] Implement file validation
- [ ] Create data transformation pipelines
- [ ] Write comprehensive tests

**Deliverables:**
- All three data sources integrated
- Data successfully flowing to database
- Upload interface working

#### Sprint 4 (Weeks 7-8): Frontend Development

**Goals:**
- Build complete frontend application
- Implement all dashboard views
- Connect to backend APIs

**Key Tasks:**
- [ ] Set up React/frontend framework
- [ ] Build component library
- [ ] Implement authentication UI
- [ ] Create dashboard views
- [ ] Build filtering system
- [ ] Implement data visualizations
- [ ] Add file upload UI
- [ ] Connect to all backend APIs
- [ ] Responsive design implementation

**Deliverables:**
- Complete frontend application
- All views functional
- Responsive design working

#### Sprint 5 (Weeks 9-10): Integration & Testing

**Goals:**
- Full system integration
- Comprehensive testing
- Bug fixes and optimization

**Key Tasks:**
- [ ] End-to-end integration testing
- [ ] Cross-browser testing
- [ ] Performance testing
- [ ] Security testing
- [ ] Bug fixing
- [ ] Code optimization
- [ ] Documentation updates

**Deliverables:**
- Fully tested application
- Bug-free (critical bugs resolved)
- Performance optimized

#### Sprint 6 (Weeks 11-12): Deployment

**Goals:**
- Deploy to production
- Complete documentation
- User training

**Key Tasks:**
- [ ] Set up production environment
- [ ] Deploy application
- [ ] Configure monitoring
- [ ] Final testing in production
- [ ] Create user documentation
- [ ] Conduct training sessions
- [ ] Handoff and support setup

**Deliverables:**
- Live production application
- Complete documentation
- Trained users

---

## Implementation Checklist

### Pre-Development

#### Requirements Gathering
- [ ] Review all client requirements
- [ ] Access to reference prototype
- [ ] Obtain Vibe API key for testing
- [ ] Obtain sample Surfside data file
- [ ] Obtain sample Facebook data file
- [ ] Clarify data field mappings
- [ ] Define success metrics

#### Resource Allocation
- [ ] Assign backend developer(s)
- [ ] Assign frontend developer(s)
- [ ] Assign DevOps engineer
- [ ] Assign QA tester
- [ ] Assign project manager
- [ ] Determine budget allocation

#### Environment Setup
- [ ] Set up AWS account (or chosen cloud provider)
- [ ] Create development database
- [ ] Create staging database
- [ ] Create production database
- [ ] Set up S3 buckets
- [ ] Configure IAM roles and permissions
- [ ] Set up Git repository
- [ ] Configure CI/CD pipeline

### Backend Development Checklist

#### Infrastructure
- [ ] Choose backend framework (FastAPI/Express/Django)
- [ ] Set up project structure
- [ ] Configure database connection
- [ ] Implement database migrations
- [ ] Set up environment variables
- [ ] Configure logging
- [ ] Set up error tracking

#### Authentication & Security
- [ ] Implement user authentication
- [ ] Create JWT/session management
- [ ] Set up password hashing
- [ ] Implement API key management
- [ ] Configure CORS
- [ ] Set up rate limiting
- [ ] Implement request validation

#### Surfside Integration
- [ ] Configure AWS SDK
- [ ] Set up S3 bucket access
- [ ] Create file monitoring service
- [ ] Implement CSV parser
- [ ] Build data transformation logic
- [ ] Create database insertion logic
- [ ] Implement error handling
- [ ] Add logging
- [ ] Create scheduled job
- [ ] Write unit tests

#### Vibe API Integration
- [ ] Study Vibe API documentation
- [ ] Create API client class
- [ ] Implement authentication
- [ ] Build async report creation
- [ ] Implement polling mechanism
- [ ] Add rate limit tracking
- [ ] Create report download logic
- [ ] Build data parser
- [ ] Implement retry logic
- [ ] Handle all error codes
- [ ] Create scheduled jobs
- [ ] Write unit tests
- [ ] Test with sample API key

#### Facebook Upload System
- [ ] Create upload endpoint
- [ ] Implement file validation
- [ ] Build CSV parser
- [ ] Create data transformation
- [ ] Implement duplicate checking
- [ ] Add batch insertion
- [ ] Create upload history tracking
- [ ] Implement file cleanup
- [ ] Add security scanning
- [ ] Write unit tests

#### API Development
- [ ] Create OpenAPI/Swagger spec
- [ ] Implement authentication endpoints
- [ ] Build dashboard data endpoints
- [ ] Create campaign endpoints
- [ ] Build sync trigger endpoints
- [ ] Implement filtering logic
- [ ] Add pagination
- [ ] Create export endpoints
- [ ] Add API documentation
- [ ] Test all endpoints

### Frontend Development Checklist

#### Setup
- [ ] Choose frontend framework (React/Vue/Next.js)
- [ ] Set up project structure
- [ ] Configure build tools
- [ ] Set up routing
- [ ] Configure state management
- [ ] Set up API client
- [ ] Configure environment variables

#### UI Components
- [ ] Create design system
- [ ] Build layout components
- [ ] Create navigation
- [ ] Build form components
- [ ] Create button components
- [ ] Build table components
- [ ] Create modal components
- [ ] Build card components
- [ ] Create loading states
- [ ] Build error components

#### Authentication UI
- [ ] Create login page
- [ ] Create logout functionality
- [ ] Implement protected routes
- [ ] Add session management
- [ ] Handle token refresh

#### Dashboard Views
- [ ] Build main dashboard
- [ ] Create metric cards
- [ ] Implement charts (line, bar, pie)
- [ ] Build campaign list view
- [ ] Create campaign detail view
- [ ] Implement comparison view
- [ ] Add geographic view (if applicable)
- [ ] Create trend analysis view

#### Filtering & Search
- [ ] Build date range picker
- [ ] Create campaign filter
- [ ] Implement source filter
- [ ] Add search functionality
- [ ] Create filter chips
- [ ] Implement filter persistence
- [ ] Add clear filters option

#### Data Management
- [ ] Create upload modal
- [ ] Build file drop zone
- [ ] Implement upload progress
- [ ] Create sync buttons
- [ ] Build sync status indicators
- [ ] Create sync history view
- [ ] Implement error displays

#### Export & Reports
- [ ] Build export modal
- [ ] Implement CSV export
- [ ] Create report preview
- [ ] Add export history

#### Responsive Design
- [ ] Mobile navigation
- [ ] Tablet layouts
- [ ] Mobile-friendly charts
- [ ] Touch interactions
- [ ] Responsive tables

### Testing Checklist

#### Unit Tests
- [ ] Backend model tests
- [ ] Service layer tests
- [ ] API endpoint tests
- [ ] Frontend component tests
- [ ] Utility function tests
- [ ] Achieve 80%+ code coverage

#### Integration Tests
- [ ] Database integration tests
- [ ] API integration tests
- [ ] S3 integration tests
- [ ] Vibe API integration tests
- [ ] Frontend-backend integration

#### End-to-End Tests
- [ ] User login flow
- [ ] Dashboard data loading
- [ ] Surfside sync flow
- [ ] Vibe sync flow
- [ ] Facebook upload flow
- [ ] Export functionality
- [ ] Filtering and search

#### Performance Tests
- [ ] API response times
- [ ] Database query performance
- [ ] Frontend load time
- [ ] Large file upload
- [ ] Concurrent user testing

#### Security Tests
- [ ] Authentication bypass attempts
- [ ] SQL injection tests
- [ ] XSS vulnerability tests
- [ ] File upload security
- [ ] API authorization tests

### Deployment Checklist

#### Pre-Deployment
- [ ] All tests passing
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Environment variables configured
- [ ] SSL certificates obtained
- [ ] Domain configured
- [ ] Backup strategy defined

#### Deployment
- [ ] Database migration to production
- [ ] Application deployment
- [ ] Static files deployment
- [ ] Verify all services running
- [ ] Test production endpoints
- [ ] Verify data connections
- [ ] Test authentication

#### Post-Deployment
- [ ] Monitor error logs
- [ ] Check performance metrics
- [ ] Verify scheduled jobs
- [ ] Test critical user flows
- [ ] Monitor resource usage
- [ ] Set up alerts

#### Monitoring & Maintenance
- [ ] Set up uptime monitoring
- [ ] Configure error tracking
- [ ] Set up performance monitoring
- [ ] Create backup schedule
- [ ] Define incident response plan
- [ ] Schedule regular updates

---

## API Documentation

### Vibe API Quick Reference

**Base URL:** `https://clear-platform.vibe.co/rest/reporting/v1/`

**Authentication Header:**
```
X-API-KEY: your_api_key_here
```

**Key Endpoints:**

1. **Create Async Report**
   - **URL:** `/create_async_report`
   - **Method:** POST
   - **Rate Limit:** 15 requests/hour/tenant
   - **Returns:** `{ "report_id": "uuid" }`

2. **Get Report Status**
   - **URL:** `/get_report_status?report_id={uuid}`
   - **Method:** GET
   - **Poll Interval:** 10 seconds minimum
   - **Timeout:** 30 minutes
   - **Returns:** Status and download URL when ready

3. **Get Advertiser IDs**
   - **URL:** `/get_advertiser_ids`
   - **Method:** GET
   - **Returns:** List of advertiser IDs and names

4. **Get Campaign Details**
   - **URL:** `/get_campaign_details?advertiser_id={uuid}`
   - **Method:** GET
   - **Returns:** Campaigns and strategies with date ranges

**Supported Timezones:**
- UTC (default)
- America/New_York
- America/Los_Angeles
- America/Phoenix
- America/Denver
- Europe/London
- Europe/Amsterdam
- Europe/Berlin
- Europe/Helsinki
- Europe/Stockholm
- Europe/Istanbul
- Asia/Shanghai
- Asia/Seoul
- Asia/Tel_Aviv

---

## Data Schema & Models

### Data Field Mapping

#### Common Fields Across All Sources

| Field | Surfside | Vibe | Facebook | Data Type | Description |
|-------|----------|------|----------|-----------|-------------|
| Date | ✅ | ✅ | ✅ | DATE | Campaign date |
| Campaign ID | ✅ | ✅ | ✅ | VARCHAR | Unique campaign identifier |
| Campaign Name | ✅ | ✅ | ✅ | VARCHAR | Campaign name |
| Impressions | ✅ | ✅ | ✅ | INTEGER | Ad impressions |
| Spend | ✅ | ✅ | ✅ | DECIMAL | Ad spend in USD |
| Clicks | ✅ | ⚠️ | ✅ | INTEGER | Click count |
| Conversions | ✅ | ✅ | ✅ | INTEGER | Conversion events |

✅ Available | ⚠️ Limited | ❌ Not Available

#### Vibe-Specific Fields

- `advertiser_id`, `advertiser_name`
- `strategy_id`, `strategy_name`
- `creative_id`, `creative_name`
- `households`, `frequency`
- `completed_views`, `view_through_rate`
- `app_id`, `os`
- `channel_name`, `screen`
- `geo_region`, `geo_metro`, `geo_city`, `geo_zip`
- Audience segments (age, gender, income, etc.)
- `installs`, `purchases`, `purchase_amount`, `roas`

#### Surfside-Specific Fields
*To be determined from actual data file*

#### Facebook-Specific Fields
*To be determined from actual data file*

### Data Transformation Rules

**Currency:**
- All spend amounts in USD
- Round to 2 decimal places

**Dates:**
- Store in UTC
- Display in user's timezone
- Format: YYYY-MM-DD

**Calculations:**
- CPM = (Spend / Impressions) × 1000
- CTR = (Clicks / Impressions) × 100
- CPC = Spend / Clicks
- ROAS = (Revenue / Spend) × 100

**Null Handling:**
- Store as NULL in database
- Display as "-" or "N/A" in UI
- Exclude from calculations

---

## Security & Compliance

### Security Best Practices

**1. API Key Management**
- Store in environment variables
- Never commit to version control
- Rotate keys regularly
- Use different keys for dev/staging/production

**2. Database Security**
- Use strong passwords
- Enable encryption at rest
- Use SSL/TLS for connections
- Implement principle of least privilege
- Regular security patches

**3. Application Security**
- Input validation on all endpoints
- Sanitize user inputs
- Implement CSRF protection
- Use parameterized queries (prevent SQL injection)
- Set secure HTTP headers

**4. File Upload Security**
- Validate file types
- Scan for malware
- Limit file sizes
- Sanitize filenames
- Store in secure location

**5. Authentication**
- Hash passwords (bcrypt/argon2)
- Implement rate limiting on login
- Use secure session management
- Implement password complexity rules
- Add multi-factor authentication (optional)

### Compliance Considerations

**Data Privacy:**
- Identify PII (Personally Identifiable Information)
- Implement data retention policies
- Provide data deletion mechanisms
- Log data access

**Audit Logging:**
- Log all data modifications
- Track user actions
- Monitor API usage
- Retain logs securely

---

## Testing Strategy

### Test Coverage Goals

- **Unit Tests:** 80%+ coverage
- **Integration Tests:** Critical paths covered
- **E2E Tests:** Main user flows covered

### Test Scenarios

**Surfside Integration:**
- New file detected and processed
- File with errors handled gracefully
- Large file processed successfully
- Duplicate data handled correctly

**Vibe API Integration:**
- Report created successfully
- Polling works correctly
- Rate limits respected
- API errors handled
- Report downloaded and parsed

**Facebook Upload:**
- Valid file uploaded successfully
- Invalid file rejected with clear message
- Large file uploaded
- Duplicate upload detected

**Dashboard:**
- Data displays correctly
- Filters work properly
- Date range selection works
- Export functions correctly
- Responsive on mobile

---

## Deployment Strategy

### Environment Strategy

**Development:**
- Local development environment
- Seed data for testing
- Debug mode enabled

**Staging:**
- Production-like environment
- Real data samples
- Testing before production deployment

**Production:**
- Live environment
- Real data
- Monitoring enabled
- Backups automated

### Deployment Process

1. **Code Review**
   - Peer review required
   - CI checks must pass
   - Security scan completed

2. **Testing**
   - All tests pass
   - Manual QA completed
   - Performance verified

3. **Staging Deployment**
   - Deploy to staging
   - Run smoke tests
   - Stakeholder approval

4. **Production Deployment**
   - Database migration (if needed)
   - Deploy application
   - Verify deployment
   - Monitor for errors

5. **Rollback Plan**
   - Keep previous version ready
   - Database rollback script
   - Quick rollback procedure

---

## Reference Documentation

### External Documentation Links

**Vibe API:**
- Main Documentation: https://help.vibe.co/en/articles/8943325-vibe-api-reporting
- Support: Contact Vibe support for API key

**AWS S3:**
- S3 Documentation: https://docs.aws.amazon.com/s3/
- SDK Documentation: https://aws.amazon.com/sdk-for-python/

**Surfside:**
- Documentation: *To be provided by client*
- Sample Data: `data/surfside.xlsx`

**Facebook Ads:**
- Ads Manager: https://www.facebook.com/business/tools/ads-manager
- Export Documentation: https://www.facebook.com/business/help/

**Project Prototype:**
- Reference: https://ai.studio/apps/drive/1367lVE8aOj5P6QYO3T0Lpy5ElbWoB8Ub

### Additional Resources

**Scope of Work:** https://docs.google.com/document/d/1GjHHOPg_Px2cUQFBtS7KO2_YNgOVudsEf6Vf8MSINok/edit?usp=sharing

**Tech Architecture:** https://docs.google.com/document/d/1Hh3D7nvo3WHzY5uq4vgMXIa20U4lH_cuzv3uQHRUeDo/edit?usp=sharing

**Data Ingestion & CPM Logic:** https://docs.google.com/document/d/1YgT_7Kg-4HzFQeQxGXzMmGhh6lQsn-SobUUFnpKuFsk/edit?usp=sharing

**Database Setup:** https://docs.google.com/document/d/12cgXSKcnkszZfjI1rTK8sZkqAb_vVgxhdIFHNOnAmWs/edit?usp=sharing

---

## Action Items & Next Steps

### Immediate Actions (This Week)

**Priority 1: Critical**
- [ ] Review and approve this README
- [ ] Obtain Vibe API key for testing
- [ ] Access sample Surfside data file (analyze structure)
- [ ] Obtain sample Facebook CSV file
- [ ] Confirm access to reference prototype
- [ ] Define project timeline and deadlines

**Priority 2: High**
- [ ] Decide on technology stack (Frontend/Backend/Database)
- [ ] Set up development environment
- [ ] Create database schema based on actual sample data
- [ ] Assign development team members
- [ ] Set up project management tools (Jira/Trello/GitHub Projects)

**Priority 3: Medium**
- [ ] Review and approve UI/UX prototype
- [ ] Set up AWS account and S3 bucket access
- [ ] Configure CI/CD pipeline
- [ ] Plan sprint schedule

### Short-term Goals (Next 2 Weeks)

- [ ] Complete Phase 1 deliverables
- [ ] Finalize all technical decisions
- [ ] Begin backend development
- [ ] Start Surfside integration
- [ ] Set up authentication system

### Medium-term Goals (Next Month)

- [ ] Complete all backend integrations
- [ ] Begin frontend development
- [ ] Achieve working data flow from all sources
- [ ] Complete authentication and basic dashboard

### Long-term Goals (3 Months)

- [ ] Complete all development
- [ ] Finish testing
- [ ] Deploy to production
- [ ] Complete user training
- [ ] Begin maintenance phase

---

## Support & Maintenance

### Support Channels

**Development Issues:**
- GitHub Issues
- Development team Slack/Email

**User Support:**
- Email support
- Documentation wiki
- Training materials

### Maintenance Schedule

**Regular Maintenance:**
- Weekly: Review error logs
- Monthly: Security updates
- Quarterly: Dependency updates
- Annually: Major version upgrades

**Monitoring:**
- 24/7 uptime monitoring
- Error tracking alerts
- Performance monitoring
- Resource usage tracking

---

## Appendix

### Acronyms & Abbreviations

- **API** - Application Programming Interface
- **AWS** - Amazon Web Services
- **CPM** - Cost Per Mille (thousand)
- **CPC** - Cost Per Click
- **CTR** - Click-Through Rate
- **CTV** - Connected TV
- **CSV** - Comma-Separated Values
- **DMA** - Designated Market Area
- **ETL** - Extract, Transform, Load
- **IAM** - Identity and Access Management
- **JWT** - JSON Web Token
- **MMP** - Mobile Measurement Partner
- **ROAS** - Return on Ad Spend
- **S3** - Simple Storage Service
- **SSL** - Secure Sockets Layer
- **TLS** - Transport Layer Security
- **UI/UX** - User Interface/User Experience
- **UUID** - Universally Unique Identifier

### Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | December 13, 2025 | Development Team | Initial comprehensive README |

---

## Contact Information

**Project Owner:** umairimran  
**Repository:** reporting_dashboard_project_mega  
**Last Updated:** December 13, 2025

---

**End of Document**


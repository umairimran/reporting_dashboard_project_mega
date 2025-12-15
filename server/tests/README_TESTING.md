# Automated Production Testing

## Quick Start

### 1. Install Test Dependencies

```powershell
pip install -r test_requirements.txt
```

### 2. Configure Database & Vibe API Credentials

Edit the configuration in `automated_production_test.py`:

**Database Configuration:**

```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'dashboard_db',
    'user': 'megauser',
    'password': 'mega321'  # Change this to your password
}
```

**Vibe API Configuration (Required for Phase 5):**

```python
VIBE_API_KEY = "sk_your_vibe_api_key_here"
VIBE_ADVERTISER_ID = "your-advertiser-id-here"
```

> **Note:** Update these values with your actual Vibe API credentials. If not configured, Phase 5 (Vibe testing) will be skipped.

### 3. Start the Server

In a separate terminal:

```powershell
cd c:\Users\shame\Desktop\mega\server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Wait until you see:

```
INFO:     Application startup complete.
```

### 4. Run the Test Script

```powershell
cd c:\Users\shame\Desktop\mega\server\tests
python automated_production_test.py
```

## What Gets Tested

The script automatically tests **complete ETL pipelines** for all three data sources:

✅ **Phase 0: Pre-flight Checks**

- Server connectivity
- Database connection
- Test data files availability

✅ **Phase 1: Authentication**

- Admin user creation (shameerbaba415@gmail.com)
- Admin login
- Token verification
- Invalid login rejection

✅ **Phase 2: Client Management**

- Create test client
- Set CPM settings ($5.50)
- Client login
- Access control enforcement

✅ **Phase 3: Surfside Module (Complete ETL)**

- File upload from `data/` folder
- Processing status monitoring
- Staging table verification
- Campaign/Strategy/Placement/Creative hierarchy creation
- Daily metrics loaded
- CPM calculation validation
- CTR calculation verification

✅ **Phase 4: Facebook Module (Complete ETL)**

- Facebook CSV upload
- Processing status monitoring
- Staging table verification
- Campaign hierarchy creation
- Daily metrics loaded
- CTR calculation verification

✅ **Phase 5: Vibe Module (Complete ETL)**

- API credentials storage
- Report creation via Vibe API
- Report status monitoring (created → processing → done)
- CSV download verification
- Staging table verification
- Campaign hierarchy creation
- Daily metrics loaded
- Column mapping verification (channel_name→placement_name, installs→clicks, etc.)
- CTR calculation verification

✅ **Phase 6: Metrics & Dashboard**

- Daily metrics endpoint
- Dashboard summary
- Campaign breakdown
- Top performers

✅ **Phase 7: Exports**

- CSV export functionality
- PDF report generation

✅ **Phase 8: Scheduler**

- Scheduler status check
- Job configuration verification

✅ **Phase 9: Error Handling**

- Invalid file format rejection
- Default CPM fallback ($17)

## Expected Output

The script provides:

1. **Real-time Progress**: Colored output showing each test's status
2. **Phase Summary**: Results grouped by testing phase
3. **Detailed Report**: Saved to `test_report_YYYYMMDD_HHMMSS.txt`
4. **Production Readiness Assessment**: Pass/Fail decision

### Sample Output

```
================================================================================
                   AUTOMATED PRODUCTION TESTING
================================================================================

Starting comprehensive backend testing...
Target: http://localhost:8000
Admin Email: shameerbaba415@gmail.com

================================================================================
                        PHASE 0: PRE-FLIGHT CHECKS
================================================================================

────────────────────────────────────────────────────────────────────────────────
Test 0.1: Server Connectivity
────────────────────────────────────────────────────────────────────────────────

✓ Server Running: Server is accessible
...

================================================================================
                   COMPREHENSIVE TEST REPORT
================================================================================

SUMMARY
────────────────────────────────────────────────────────────────────────────────

Total Tests: 35
Passed: 35
Failed: 0
Pass Rate: 100.0%

Phase Breakdown:

+----+----------+-------+--------+--------+-----------+
|    | Phase    | Total | Passed | Failed | Pass Rate |
+====+==========+=======+========+========+===========+
| ✓  | Phase 0  |   3   |   3    |   0    |   100.0%  |
+----+----------+-------+--------+--------+-----------+
| ✓  | Phase 1  |   4   |   4    |   0    |   100.0%  |
+----+----------+-------+--------+--------+-----------+
...

PRODUCTION READINESS
────────────────────────────────────────────────────────────────────────────────

✓ PRODUCTION READY
All critical systems operational. Backend is ready for production deployment.
```

## Test Data

The script automatically finds CSV files in `c:\Users\shame\Desktop\mega\data\`:

- **surfside.csv** - For Surfside module testing
- **facebook.csv** - For Facebook module testing

Make sure these files exist before running tests.

## Admin Credentials

The script creates an admin user:

- **Email**: `shameerbaba415@gmail.com`
- **Password**: `Admin@123456`

You can use these credentials to login after testing.

## Test Client

The script also creates a test client:5-10 minutes\*\* depending on:

- CSV file sizes
- Database performance
- Server processing speed
- **Vibe API report generation** (2-5 minutes for report creation)23456`
- **CPM**: $5.50

## Duration

Complete testing takes approximately **3-5 minutes** depending on:

- CSV file sizes
- Database performance
- Server processing speed

## Troubleshooting

### Server Not Running

```
✗ Server Running: Cannot connect to server
```

**Solution**: Start the server with `uvicorn app.main:app --reload`

### Database Connection Failed

```
✗ Database Connection: Cannot connect to database
```

**Solution**: Check PostgreSQL is running and credentials in `DB_CONFIG` are correct

### CSV Files Not Found

```
⚠ Surfside CSV not found in data folder
```

**Solution**: Ensure `surfside.csv` exists in `c:\Users\shame\Desktop\mega\data\`

### Vibe API Testing\*\*: Phase 5 tests complete Vibe integration including API report creation, CSV download, and full ETL pipeline

- **Complete ETL Verification**: All three sources (Surfside, Facebook, Vibe) test the entire pipeline: Parse → Transform → Stage → Load
- **Database State**: Tests create data but don't clean up automatically
- **Multiple Runs**: You can run the script multiple times; it handles existing data
- **Report Files**: Each run creates a timestamped report file
- **Vibe Report Time**: Vibe API reports can take 2-5 minutes to generate; the script will wait up to 5 minutes

````

**Solution**: Install dependencies with `pip install -r test_requirements.txt`

## Notes

- **S3 Tests Skipped**: Vibe module tests are excluded as S3 access is not configured yet
- **Database State**: Tests create data but don't clean up automatically
- **Multiple Runs**: You can run the script multiple times; it handles existing data
- **Report Files**: Each run creates a timestamped report file

## Clean Database (Optional)

To start fresh between test runs:

```sql
psql -U postgres -d dashboard_db

TRUNCATE TABLE
    audit_logs,
    uploaded_files,
    vibe_report_requests,
    vibe_credentials,
    ingestion_logs,
    staging_media_raw,
    monthly_summaries,
    weekly_summaries,
    daily_metrics,
    creatives,
    placements,
    strategies,
    campaigns,
    client_settings,
    clients,
    users
CASCADE;
````

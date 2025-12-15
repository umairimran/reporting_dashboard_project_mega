# Background Jobs & Scheduler Testing Guide

## **Module Overview**

The Jobs module (`app/jobs/`) handles automated background tasks for data ingestion and aggregation using APScheduler.

### **Purpose**

- Automatically ingest data from Surfside and Vibe daily
- Aggregate weekly performance summaries
- Aggregate monthly performance summaries
- Send alerts on failures
- Run tasks on schedule without manual intervention

### **Key Components**

- **Scheduler** (`scheduler.py`): APScheduler configuration and job registration
- **Daily Ingestion** (`daily_ingestion.py`): Automated Surfside + Vibe data pulls
- **Summaries** (`summaries.py`): Weekly and monthly aggregation jobs

---

## **Scheduled Jobs**

### **1. Daily Data Ingestion**

- **Schedule:** Every day at 5:00 AM (configurable)
- **Job ID:** `daily_data_ingestion`
- **Function:** `run_all_daily_ingestions()`
- **What it does:**
  1. Pulls yesterday's data from Surfside S3
  2. Pulls yesterday's data from Vibe API
  3. Processes and loads into database
  4. Sends email alerts on failures

### **2. Weekly Aggregation**

- **Schedule:** Every Sunday at 7:00 AM
- **Job ID:** `weekly_aggregation`
- **Function:** `run_weekly_aggregation()`
- **What it does:**
  1. Aggregates previous week's data (Monday-Sunday)
  2. Creates weekly_summaries table entries
  3. Calculates week-over-week comparisons

### **3. Monthly Aggregation**

- **Schedule:** 1st of each month at 8:00 AM
- **Job ID:** `monthly_aggregation`
- **Function:** `run_monthly_aggregation()`
- **What it does:**
  1. Aggregates previous month's data
  2. Creates monthly_summaries table entries
  3. Calculates month-over-month trends

---

## **Job Configuration**

### **Environment Variables (.env)**

```env
# Cron Schedule Settings
SURFSIDE_CRON_HOUR=5    # Hour to run daily ingestion (0-23)
SURFSIDE_CRON_MINUTE=0  # Minute to run (0-59)

# S3 Configuration (for Surfside)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
SURFSIDE_S3_BUCKET=your-bucket-name

# Vibe API Configuration
VIBE_API_BASE_URL=https://api.vibe.co
```

---

## **Testing Methods**

### **Method 1: Check Scheduler Status at Startup**

When you start the server, you should see:

```bash
uvicorn app.main:app --reload
```

**Expected Startup Logs:**

```
INFO:     Starting PAID MEDIA PERFORMANCE DASHBOARD API
INFO:     ✓ Database connection successful
INFO:     ✓ Background job scheduler started
INFO:     ✓ Daily data ingestion scheduled at 5:00
INFO:     ✓ Weekly aggregation scheduled for Sundays at 07:00
INFO:     ✓ Monthly aggregation scheduled for 1st of month at 08:00
INFO:     ==================================================
INFO:     ALL SCHEDULED JOBS CONFIGURED
INFO:     ==================================================
INFO:     APPLICATION STARTUP COMPLETE
```

---

### **Method 2: Manual Job Trigger via API**

#### **Step 1: Create Test Endpoint**

Add to `app/jobs/router.py` (create if doesn't exist):

```python
from fastapi import APIRouter, Depends, HTTPException
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.jobs.daily_ingestion import run_all_daily_ingestions
from app.jobs.summaries import run_weekly_aggregation, run_monthly_aggregation
from datetime import date

router = APIRouter(prefix="/jobs", tags=["Background Jobs"])

@router.post("/trigger/daily-ingestion")
async def trigger_daily_ingestion(
    current_user: User = Depends(get_current_user)
):
    """Manually trigger daily ingestion (admin only)."""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin only")

    await run_all_daily_ingestions()
    return {"status": "completed"}

@router.post("/trigger/weekly-aggregation")
async def trigger_weekly_aggregation(
    current_user: User = Depends(get_current_user)
):
    """Manually trigger weekly aggregation (admin only)."""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin only")

    await run_weekly_aggregation()
    return {"status": "completed"}

@router.post("/trigger/monthly-aggregation")
async def trigger_monthly_aggregation(
    current_user: User = Depends(get_current_user)
):
    """Manually trigger monthly aggregation (admin only)."""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin only")

    await run_monthly_aggregation()
    return {"status": "completed"}

@router.get("/status")
async def get_jobs_status(
    current_user: User = Depends(get_current_user)
):
    """Get status of all scheduled jobs."""
    from app.main import scheduler
    from app.jobs.scheduler import get_scheduler_status

    return get_scheduler_status(scheduler)
```

**Register router in `app/main.py`:**

```python
from app.jobs.router import router as jobs_router
app.include_router(jobs_router, prefix="/api/v1")
```

#### **Step 2: Test with Postman**

**Get Job Status:**

```
GET http://localhost:8000/api/v1/jobs/status
Authorization: Bearer <token>
```

**Expected Response:**

```json
{
  "running": true,
  "jobs_count": 3,
  "jobs": [
    {
      "id": "daily_data_ingestion",
      "name": "run_all_daily_ingestions",
      "next_run_time": "2025-12-16T05:00:00",
      "trigger": "cron[hour='5', minute='0']"
    },
    {
      "id": "weekly_aggregation",
      "name": "run_weekly_aggregation",
      "next_run_time": "2025-12-21T07:00:00",
      "trigger": "cron[day_of_week='sun', hour='7']"
    },
    {
      "id": "monthly_aggregation",
      "name": "run_monthly_aggregation",
      "next_run_time": "2026-01-01T08:00:00",
      "trigger": "cron[day='1', hour='8']"
    }
  ]
}
```

**Trigger Daily Ingestion:**

```
POST http://localhost:8000/api/v1/jobs/trigger/daily-ingestion
Authorization: Bearer <admin_token>
```

**Expected Response:**

```json
{
  "status": "completed"
}
```

---

### **Method 3: Directly Run Job Functions (Python)**

Create `test_jobs.py`:

```python
import asyncio
from app.core.database import SessionLocal
from app.jobs.daily_ingestion import run_all_daily_ingestions
from app.jobs.summaries import run_weekly_aggregation, run_monthly_aggregation

async def test_daily_ingestion():
    """Test daily ingestion job."""
    print("Testing daily ingestion...")
    await run_all_daily_ingestions()
    print("Daily ingestion completed!")

async def test_weekly_aggregation():
    """Test weekly aggregation job."""
    print("Testing weekly aggregation...")
    await run_weekly_aggregation()
    print("Weekly aggregation completed!")

async def test_monthly_aggregation():
    """Test monthly aggregation job."""
    print("Testing monthly aggregation...")
    await run_monthly_aggregation()
    print("Monthly aggregation completed!")

if __name__ == "__main__":
    # Test one at a time
    asyncio.run(test_daily_ingestion())
    # asyncio.run(test_weekly_aggregation())
    # asyncio.run(test_monthly_aggregation())
```

**Run:**

```powershell
cd c:\Users\shame\Desktop\mega\server
python test_jobs.py
```

---

### **Method 4: Change Schedule for Testing**

In `app/jobs/scheduler.py`, temporarily change schedule:

```python
# TEST: Run every 2 minutes instead of daily at 5 AM
scheduler.add_job(
    run_all_daily_ingestions,
    trigger='interval',
    minutes=2,  # Run every 2 minutes
    id='daily_data_ingestion',
    replace_existing=True,
    max_instances=1
)
```

**Watch logs to see job execute:**

```
INFO:     ======================================
INFO:     STARTING ALL DAILY DATA INGESTIONS
INFO:     ======================================
INFO:     Target date: 2025-12-14
...
```

---

## **Verification Checklist**

### **Scheduler Health**

- [ ] Scheduler starts successfully on app startup
- [ ] All 3 jobs registered (daily, weekly, monthly)
- [ ] Next run times calculated correctly
- [ ] Scheduler shows `running: true` status

### **Daily Ingestion Job**

- [ ] Runs at configured time (5 AM default)
- [ ] Processes all active Surfside clients
- [ ] Processes all active Vibe clients
- [ ] Creates ingestion_logs entries
- [ ] Sends email alerts on failures
- [ ] Logs show success/failure counts

### **Weekly Aggregation Job**

- [ ] Runs on Sundays at 7 AM
- [ ] Aggregates previous week (Monday-Sunday)
- [ ] Creates entries in weekly_summaries table
- [ ] Calculates metrics correctly

### **Monthly Aggregation Job**

- [ ] Runs on 1st of month at 8 AM
- [ ] Aggregates previous month
- [ ] Creates entries in monthly_summaries table
- [ ] Handles month-end edge cases

---

## **Database Verification**

### **Check Ingestion Logs:**

```sql
SELECT
    id,
    client_id,
    source,
    run_date,
    status,
    records_loaded,
    records_failed,
    started_at,
    finished_at,
    message
FROM ingestion_logs
ORDER BY started_at DESC
LIMIT 10;
```

**Expected Results:**

- New entries created daily at 5 AM
- `status` = 'success' or 'failed'
- `records_loaded` shows count of processed records

### **Check Weekly Summaries:**

```sql
SELECT
    id,
    client_id,
    week_start,
    week_end,
    total_impressions,
    total_spend,
    total_conversions,
    created_at
FROM weekly_summaries
ORDER BY week_start DESC
LIMIT 5;
```

**Expected Results:**

- New entries every Sunday
- Week spans Monday-Sunday
- Aggregated metrics match daily_metrics sum

### **Check Monthly Summaries:**

```sql
SELECT
    id,
    client_id,
    year,
    month,
    total_impressions,
    total_spend,
    total_conversions,
    created_at
FROM monthly_summaries
ORDER BY year DESC, month DESC
LIMIT 5;
```

**Expected Results:**

- New entries on 1st of each month
- Month/year correct
- Aggregated metrics match daily_metrics sum

---

## **Monitoring & Logs**

### **Real-time Log Monitoring:**

**PowerShell (watch logs):**

```powershell
Get-Content -Path "logs/app.log" -Wait -Tail 50
```

**Filter for job logs:**

```powershell
Get-Content logs/app.log | Select-String "INGESTION|AGGREGATION"
```

### **Key Log Messages:**

**Success:**

```
INFO: ✓ Surfside successful for Test Client
INFO: ✓ Vibe successful for Test Client
INFO: Weekly aggregation completed: 5 summaries created
INFO: Monthly aggregation completed: 5 summaries created
```

**Failures:**

```
ERROR: ✗ Surfside failed for Test Client: S3 file not found
ERROR: ✗ Vibe failed for Test Client: API authentication failed
```

---

## **Troubleshooting**

### **Issue: Jobs Not Running**

**Symptoms:** Scheduler says jobs are registered but never execute
**Diagnosis:**

```python
# Check scheduler state
from app.main import scheduler
print(scheduler.running)  # Should be True
print(scheduler.get_jobs())  # Should show 3 jobs
```

**Solutions:**

- Verify scheduler.start() called in lifespan
- Check for exceptions in job functions
- Ensure server stays running (not restarting)

### **Issue: Daily Ingestion Fails**

**Symptoms:** Job runs but all clients fail
**Diagnosis:** Check logs for error messages
**Common Causes:**

- S3 credentials invalid → Fix AWS_ACCESS_KEY_ID/SECRET
- Vibe API down → Check VIBE_API_BASE_URL
- No active clients → Verify clients.status = 'active'
- Database connection lost → Check DATABASE_URL

### **Issue: Wrong Schedule**

**Symptoms:** Jobs run at unexpected times
**Diagnosis:**

```python
job = scheduler.get_job('daily_data_ingestion')
print(job.next_run_time)  # Check next execution
```

**Solutions:**

- Verify SURFSIDE_CRON_HOUR environment variable
- Check server timezone vs expected timezone
- Adjust cron expression in scheduler.py

### **Issue: Duplicate Executions**

**Symptoms:** Same job runs multiple times simultaneously
**Diagnosis:** Check `max_instances` setting
**Solution:**

```python
scheduler.add_job(
    ...,
    max_instances=1  # Prevent concurrent runs
)
```

### **Issue: Aggregations Missing Data**

**Symptoms:** Weekly/monthly summaries have zero metrics
**Diagnosis:**

```sql
-- Check if daily_metrics exist for the period
SELECT COUNT(*) FROM daily_metrics
WHERE date BETWEEN '2025-12-08' AND '2025-12-14';
```

**Solution:**

- Ensure daily ingestion ran successfully first
- Manually run aggregation for specific period
- Check aggregation logic in summaries.py

---

## **Performance Considerations**

### **Daily Ingestion:**

- **Duration:** 2-10 minutes per client (depends on data volume)
- **Concurrency:** Processes clients sequentially (not parallel)
- **Memory:** ~100MB per client during processing
- **Recommendations:**
  - Schedule during off-peak hours (5 AM)
  - Monitor for clients taking > 15 minutes
  - Add timeout handling for stuck jobs

### **Aggregations:**

- **Weekly:** < 30 seconds per client
- **Monthly:** < 2 minutes per client
- **Database impact:** Read-heavy queries on daily_metrics
- **Recommendations:**
  - Ensure indexes on date, client_id columns
  - Run after daily ingestion completes
  - Cache results for dashboard queries

---

## **Production Deployment**

### **1. Job Monitoring**

```python
# Add Sentry/DataDog integration
from sentry_sdk import capture_exception

try:
    await run_all_daily_ingestions()
except Exception as e:
    capture_exception(e)
    # Send PagerDuty alert
```

### **2. Job Status Dashboard**

Create admin page showing:

- Last run time per job
- Success/failure status
- Average duration
- Next scheduled run

### **3. Retry Logic**

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def run_with_retry():
    await run_all_daily_ingestions()
```

### **4. Alerting**

- Slack webhook on job failures
- PagerDuty escalation if 3+ failures
- Email digest of daily job results

### **5. Scaling**

For many clients (> 50):

- Use Celery for distributed task processing
- Parallel client processing with asyncio.gather()
- Split jobs by client tier (premium clients first)

---

## **Expected Test Results**

### **Successful Daily Ingestion:**

```
==================================================
STARTING ALL DAILY DATA INGESTIONS
==================================================
Target date: 2025-12-14

==================================================
SURFSIDE DATA INGESTION
==================================================
Found 3 clients with Surfside enabled
Processing Surfside for: Client A
✓ Surfside successful for Client A
Processing Surfside for: Client B
✓ Surfside successful for Client B
Processing Surfside for: Client C
✓ Surfside successful for Client C
Surfside complete: 3 success, 0 failed

==================================================
VIBE DATA INGESTION
==================================================
Found 2 clients with Vibe enabled
Processing Vibe for: Client A
✓ Vibe successful for Client A
Processing Vibe for: Client B
✓ Vibe successful for Client B
Vibe complete: 2 success, 0 failed

==================================================
DAILY INGESTION SUMMARY
==================================================
Surfside: 3 success, 0 failed
Vibe: 2 success, 0 failed
Total: 5 success, 0 failed
==================================================
```

### **Successful Weekly Aggregation:**

```
==================================================
STARTING WEEKLY AGGREGATION
==================================================
Aggregating week starting: 2025-12-08
==================================================
Weekly aggregation completed: 5 summaries created
==================================================
```

### **Successful Monthly Aggregation:**

```
==================================================
STARTING MONTHLY AGGREGATION
==================================================
Aggregating month: 2025-11
==================================================
Monthly aggregation completed: 5 summaries created
==================================================
```

---

## **Manual Testing Scenarios**

### **Scenario 1: Test Daily Ingestion**

1. Configure Surfside S3 bucket with test file
2. Configure Vibe API credentials
3. Trigger job manually via API
4. Verify ingestion_logs created
5. Verify daily_metrics populated
6. Check email for success/failure alerts

### **Scenario 2: Test Weekly Aggregation**

1. Ensure daily_metrics exist for past week
2. Trigger weekly aggregation
3. Query weekly_summaries table
4. Verify metrics sum matches daily totals

### **Scenario 3: Test Monthly Aggregation**

1. Ensure daily_metrics exist for past month
2. Trigger monthly aggregation
3. Query monthly_summaries table
4. Verify metrics sum matches daily totals

### **Scenario 4: Test Failure Handling**

1. Temporarily break S3 credentials
2. Trigger daily ingestion
3. Verify email alert sent to admins
4. Check ingestion_logs shows 'failed' status
5. Fix credentials and re-run successfully

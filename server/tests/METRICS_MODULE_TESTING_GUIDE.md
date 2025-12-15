# Metrics Module Testing Guide

## **Module Overview**

The Metrics module (`app/metrics/`) provides API endpoints and services for querying and analyzing performance metrics across campaigns, dates, and data sources.

### **Purpose**
- Query daily metrics with filtering and pagination
- Access weekly and monthly aggregated summaries
- Calculate performance metrics (CTR, CPC, CPA, ROAS)
- Trigger manual aggregations for specific periods
- Support both admin and client user access controls

### **Key Components**
- **Router** (`router.py`): API endpoints for metrics queries
- **Models** (`models.py`): Database tables (daily_metrics, weekly_summaries, monthly_summaries)
- **Calculator** (`calculator.py`): Metrics calculation formulas
- **Aggregator** (`aggregator.py`): Weekly/monthly aggregation service
- **Schemas** (`schemas.py`): Pydantic response models

---

## **Available Endpoints**

### **1. Get Daily Metrics**
```
GET /api/v1/metrics/daily
```

**Query Parameters:**
- `start_date` (required): YYYY-MM-DD
- `end_date` (required): YYYY-MM-DD
- `client_id` (optional): Filter by client (admin only)
- `campaign_name` (optional): Filter by campaign name (partial match)
- `source` (optional): surfside/vibe/facebook
- `limit` (default: 100, max: 1000): Records per page
- `offset` (default: 0): Pagination offset

**Response:** Array of daily metric records

### **2. Get Weekly Summaries**
```
GET /api/v1/metrics/weekly
```

**Query Parameters:**
- `client_id` (optional): Filter by client
- `limit` (default: 52, max: 104): Number of weeks

**Response:** Array of weekly summary records

### **3. Get Monthly Summaries**
```
GET /api/v1/metrics/monthly
```

**Query Parameters:**
- `client_id` (optional): Filter by client
- `year` (optional): Filter by specific year
- `limit` (default: 12, max: 24): Number of months

**Response:** Array of monthly summary records

### **4. Get Metrics Summary**
```
GET /api/v1/metrics/summary
```

**Query Parameters:**
- `start_date` (required): Start date
- `end_date` (required): End date
- `client_id` (optional): Filter by client

**Response:** Aggregated totals and averages for date range

### **5. Trigger Weekly Aggregation**
```
POST /api/v1/metrics/aggregate/week
```

**Query Parameters:**
- `week_start` (required): Monday of the week (YYYY-MM-DD)
- `client_id` (optional): Specific client or all clients

**Auth:** Admin only

### **6. Trigger Monthly Aggregation**
```
POST /api/v1/metrics/aggregate/month
```

**Query Parameters:**
- `year` (required): Year
- `month` (required): Month (1-12)
- `client_id` (optional): Specific client or all clients

**Auth:** Admin only

---

## **Testing with Postman**

### **Prerequisites**

1. **Authenticate:**
   - POST `/api/v1/auth/login`
   - Get access_token
   - Store as Postman environment variable

2. **Get Client ID:**
   - GET `/api/v1/clients`
   - Copy your client UUID

3. **Ensure Data Exists:**
   - Upload Surfside/Facebook data first
   - Or use existing data from previous tests

---

### **Test 1: Query Daily Metrics**

**Request:**
```
GET http://localhost:8000/api/v1/metrics/daily?start_date=2025-11-01&end_date=2025-11-30&limit=50
```

**Headers:**
```
Authorization: Bearer <your_token>
```

**Expected Response (200 OK):**
```json
[
    {
        "id": "uuid-here",
        "client_id": "client-uuid",
        "client_name": "Test Client",
        "campaign_name": "Prospecting",
        "strategy_name": "Audience | Cannabis Consumers",
        "placement_name": "Ad Placement",
        "creative_name": "Creative 2",
        "date": "2025-11-04",
        "impressions": 8865,
        "clicks": 6,
        "conversions": 0,
        "conversion_revenue": 0.00,
        "ctr": 0.07,
        "spend": 110.81,
        "cpc": 18.47,
        "cpa": null,
        "roas": 0.00,
        "source": "surfside"
    },
    ...
]
```

**Verification:**
- Array of metric objects returned
- All fields populated correctly
- CTR calculated as (clicks/impressions) * 100
- Spend calculated as (impressions / 1000) * CPM
- Dates within requested range

---

### **Test 2: Filter by Campaign**

**Request:**
```
GET http://localhost:8000/api/v1/metrics/daily?start_date=2025-11-01&end_date=2025-11-30&campaign_name=Prospecting
```

**Expected Response:**
- Only metrics for campaigns containing "Prospecting"
- Case-insensitive partial match works

---

### **Test 3: Filter by Source**

**Request:**
```
GET http://localhost:8000/api/v1/metrics/daily?start_date=2025-11-01&end_date=2025-11-30&source=surfside
```

**Expected Response:**
- Only Surfside metrics returned
- No Vibe or Facebook data in results

---

### **Test 4: Pagination**

**Request:**
```
GET http://localhost:8000/api/v1/metrics/daily?start_date=2025-11-01&end_date=2025-11-30&limit=10&offset=0
```

**Expected Response:**
- Exactly 10 records returned (first page)

**Next Page:**
```
GET .../metrics/daily?...&limit=10&offset=10
```

**Expected Response:**
- Next 10 records (second page)

---

### **Test 5: Get Weekly Summaries**

**Request:**
```
GET http://localhost:8000/api/v1/metrics/weekly?limit=10
```

**Expected Response (200 OK):**
```json
[
    {
        "id": "uuid-here",
        "client_id": "client-uuid",
        "week_start": "2025-12-08",
        "week_end": "2025-12-14",
        "total_impressions": 125000,
        "total_clicks": 3125,
        "total_conversions": 45,
        "total_revenue": 2250.00,
        "total_spend": 1562.50,
        "avg_ctr": 2.50,
        "avg_cpc": 0.50,
        "avg_cpa": 34.72,
        "avg_roas": 1.44,
        "created_at": "2025-12-15T07:00:00"
    },
    ...
]
```

**Verification:**
- Week spans Monday-Sunday
- Aggregated totals sum correctly
- Averages calculated properly

---

### **Test 6: Get Monthly Summaries**

**Request:**
```
GET http://localhost:8000/api/v1/metrics/monthly?year=2025&limit=12
```

**Expected Response (200 OK):**
```json
[
    {
        "id": "uuid-here",
        "client_id": "client-uuid",
        "year": 2025,
        "month": 11,
        "total_impressions": 500000,
        "total_clicks": 12500,
        "total_conversions": 180,
        "total_revenue": 9000.00,
        "total_spend": 6250.00,
        "avg_ctr": 2.50,
        "avg_cpc": 0.50,
        "avg_cpa": 34.72,
        "avg_roas": 1.44,
        "created_at": "2025-12-01T08:00:00"
    },
    ...
]
```

**Verification:**
- Month 1-12 corresponds to Jan-Dec
- Totals match sum of daily_metrics for that month

---

### **Test 7: Get Metrics Summary**

**Request:**
```
GET http://localhost:8000/api/v1/metrics/summary?start_date=2025-11-01&end_date=2025-11-30
```

**Expected Response (200 OK):**
```json
{
    "total_impressions": 500000,
    "total_clicks": 12500,
    "total_conversions": 180,
    "total_revenue": 9000.00,
    "total_spend": 6250.00,
    "avg_ctr": 2.50,
    "avg_cpc": 0.50,
    "avg_cpa": 34.72,
    "avg_roas": 1.44
}
```

**Verification:**
- All totals accurate
- Averages calculated correctly
- No per-record data, just aggregates

---

### **Test 8: Trigger Manual Aggregation (Admin Only)**

**Request:**
```
POST http://localhost:8000/api/v1/metrics/aggregate/week?week_start=2025-12-08
Authorization: Bearer <admin_token>
```

**Expected Response (200 OK):**
```json
{
    "status": "success",
    "count": 5  // 5 clients aggregated
}
```

**Database Verification:**
```sql
SELECT * FROM weekly_summaries 
WHERE week_start = '2025-12-08'
ORDER BY created_at DESC;
```

**Should see:** New entries for each client for that week

---

### **Test 9: Trigger Monthly Aggregation**

**Request:**
```
POST http://localhost:8000/api/v1/metrics/aggregate/month?year=2025&month=11
Authorization: Bearer <admin_token>
```

**Expected Response:**
```json
{
    "status": "success",
    "count": 5
}
```

---

## **Database Verification**

### **Check Daily Metrics:**
```sql
SELECT 
    date,
    campaign_name,
    source,
    impressions,
    clicks,
    spend,
    ctr,
    conversions,
    conversion_revenue
FROM daily_metrics
WHERE client_id = '<client-uuid>'
  AND date BETWEEN '2025-11-01' AND '2025-11-30'
ORDER BY date DESC, campaign_name;
```

### **Verify Calculations:**
```sql
-- CTR should be (clicks / impressions * 100)
SELECT 
    impressions,
    clicks,
    ctr,
    ROUND((clicks::decimal / impressions * 100), 2) as calculated_ctr
FROM daily_metrics
WHERE clicks > 0
LIMIT 10;

-- Spend should be (impressions / 1000 * cpm)
SELECT 
    impressions,
    spend,
    c.cpm,
    ROUND((impressions::decimal / 1000 * c.cpm), 2) as calculated_spend
FROM daily_metrics dm
JOIN clients c ON dm.client_id = c.id
LIMIT 10;
```

### **Check Weekly Summaries:**
```sql
SELECT 
    week_start,
    week_end,
    total_impressions,
    total_spend,
    avg_ctr,
    created_at
FROM weekly_summaries
WHERE client_id = '<client-uuid>'
ORDER BY week_start DESC;
```

### **Verify Weekly Aggregation:**
```sql
-- Compare weekly_summaries to sum of daily_metrics
SELECT 
    DATE_TRUNC('week', date) as week_start,
    SUM(impressions) as total_impressions,
    SUM(spend) as total_spend,
    AVG(ctr) as avg_ctr
FROM daily_metrics
WHERE client_id = '<client-uuid>'
  AND date BETWEEN '2025-12-08' AND '2025-12-14'
GROUP BY week_start;

-- Should match weekly_summaries for that week
```

---

## **Common Testing Scenarios**

### **Scenario 1: Performance Analysis**
```
1. GET /metrics/summary for Q4 (Oct-Dec)
2. Compare to previous quarter
3. Identify trends in ROAS and CPA
```

### **Scenario 2: Campaign Comparison**
```
1. GET /metrics/daily filtered by "Campaign A"
2. GET /metrics/daily filtered by "Campaign B"
3. Compare CTR and spend
```

### **Scenario 3: Source Performance**
```
1. GET /metrics/summary?source=surfside
2. GET /metrics/summary?source=vibe
3. GET /metrics/summary?source=facebook
4. Identify best performing source
```

### **Scenario 4: Weekly Trends**
```
1. GET /metrics/weekly?limit=52 (whole year)
2. Plot total_spend over time
3. Identify seasonal patterns
```

---

## **Error Handling Tests**

### **Test: Invalid Date Range**
```
GET /metrics/daily?start_date=2025-13-01&end_date=2025-11-30
```

**Expected:** 422 Unprocessable Entity (invalid date format)

### **Test: Missing Required Params**
```
GET /metrics/daily
```

**Expected:** 422 Unprocessable Entity (start_date and end_date required)

### **Test: Unauthorized Access**
```
GET /metrics/daily?start_date=2025-11-01&end_date=2025-11-30
(No Authorization header)
```

**Expected:** 401 Unauthorized

### **Test: Client User Accessing Another Client**
```
GET /metrics/daily?client_id=<different-client-uuid>
(Logged in as client user, not admin)
```

**Expected:** No data returned (filtered to current user's client automatically)

### **Test: Non-Admin Triggering Aggregation**
```
POST /metrics/aggregate/week?week_start=2025-12-08
(Logged in as client user)
```

**Expected:** 403 Forbidden

---

## **Performance Testing**

### **Large Date Range:**
```
GET /metrics/daily?start_date=2024-01-01&end_date=2025-12-31&limit=1000
```

**Expected:**
- Query completes in < 2 seconds
- Pagination works correctly
- No timeout errors

### **High Volume Aggregation:**
```
POST /metrics/aggregate/month?year=2025&month=11
(For 100+ clients with 1M+ daily records)
```

**Expected:**
- Completes in < 30 seconds
- No database locks
- All clients aggregated successfully

---

## **Metrics Calculation Verification**

### **CTR (Click-Through Rate):**
```
Formula: (clicks / impressions) * 100
Example: (1250 / 50000) * 100 = 2.50%
```

### **CPC (Cost Per Click):**
```
Formula: spend / clicks
Example: $625 / 1250 = $0.50
Note: Returns null if clicks = 0
```

### **CPA (Cost Per Acquisition):**
```
Formula: spend / conversions
Example: $625 / 45 = $13.89
Note: Returns null if conversions = 0
```

### **ROAS (Return on Ad Spend):**
```
Formula: revenue / spend
Example: $2250 / $625 = 3.60
Note: Returns Decimal('0') if spend = 0
```

### **Spend:**
```
Formula: (impressions / 1000) * CPM
Example: (50000 / 1000) * $12.50 = $625.00
```

---

## **Access Control Testing**

### **Admin User:**
- [ ] Can query metrics for any client
- [ ] Can filter by client_id
- [ ] Can trigger manual aggregations
- [ ] Can see all weekly/monthly summaries

### **Client User:**
- [ ] Can only see own client's metrics
- [ ] client_id filter ignored (auto-filtered to own client)
- [ ] Cannot trigger aggregations
- [ ] Only see own weekly/monthly summaries

---

## **Troubleshooting**

### **No Data Returned**
**Causes:**
- No metrics exist for date range
- Wrong client_id
- Client user trying to access another client

**Solutions:**
```sql
-- Check if data exists
SELECT COUNT(*) FROM daily_metrics
WHERE date BETWEEN '2025-11-01' AND '2025-11-30';

-- If 0, upload data first
```

### **Incorrect Calculations**
**Causes:**
- CPM not set for client
- Metrics calculator bug

**Solutions:**
```sql
-- Verify CPM exists
SELECT id, name, cpm FROM clients WHERE id = '<uuid>';

-- Recalculate manually
UPDATE daily_metrics SET 
    ctr = (clicks::decimal / impressions * 100),
    spend = (impressions::decimal / 1000 * <cpm>)
WHERE client_id = '<uuid>';
```

### **Aggregation Missing Data**
**Causes:**
- Daily metrics not ingested yet
- Aggregation ran before daily ingestion

**Solutions:**
- Run daily ingestion first
- Manually trigger aggregation for specific week/month

---

## **Production Recommendations**

1. **Caching:**
   - Cache weekly/monthly summaries (rarely change)
   - Cache popular date ranges (last 30 days)
   - Invalidate cache on new data ingestion

2. **Indexing:**
```sql
-- Essential indexes
CREATE INDEX idx_daily_metrics_client_date ON daily_metrics(client_id, date);
CREATE INDEX idx_daily_metrics_campaign ON daily_metrics(campaign_id);
CREATE INDEX idx_daily_metrics_source ON daily_metrics(source);
```

3. **Query Optimization:**
   - Limit default page size to 100
   - Use date range indexes
   - Materialize frequently queried views

4. **Real-time Updates:**
   - WebSocket notifications on new data
   - Auto-refresh dashboards every 5 minutes
   - Show "last updated" timestamp

---

## **Expected Test Results Summary**

✅ **All Tests Passing:**
- Daily metrics query returns data
- Filters work correctly (campaign, source, date)
- Pagination functions properly
- Weekly summaries aggregate correctly
- Monthly summaries aggregate correctly
- Summary endpoint calculates accurate totals
- Manual aggregations create expected records
- Access control enforced (admin vs client)
- Calculations match formulas (CTR, CPC, CPA, ROAS, Spend)
- Large date ranges perform adequately

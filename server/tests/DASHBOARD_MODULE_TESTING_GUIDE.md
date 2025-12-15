# Dashboard Module Testing Guide

## **Module Overview**

The Dashboard module (`app/dashboard/`) provides comprehensive analytics and visualization data for client performance monitoring through structured API endpoints.

### **Purpose**
- Provide unified dashboard view with all key metrics
- Break down performance by campaigns and data sources
- Show daily trends and time-series data
- Identify top performing campaigns, placements, and creatives
- Support period-over-period comparisons
- Enable quick stats views (today, this week, this month)

### **Key Components**
- **Router** (`router.py`): API endpoints for dashboard views
- **Service** (`service.py`): Complex queries and data aggregation logic
- **Schemas** (`schemas.py`): Response models for dashboard data structures

---

## **Available Endpoints**

### **1. Get Complete Dashboard**
```
GET /api/v1/dashboard/
```

**Purpose:** Single endpoint returning all dashboard data
**Includes:** Summary, campaigns, sources, trends, top performers

**Query Parameters:**
- `start_date` (required): YYYY-MM-DD
- `end_date` (required): YYYY-MM-DD
- `client_id` (optional): Client UUID (admin only)

**Response:** ClientDashboard object with all sections

---

### **2. Get Dashboard Summary**
```
GET /api/v1/dashboard/summary
```

**Purpose:** High-level KPIs and aggregated metrics

**Response Structure:**
```json
{
    "total_impressions": 500000,
    "total_clicks": 12500,
    "total_conversions": 180,
    "total_revenue": 9000.00,
    "total_spend": 6250.00,
    "overall_ctr": 2.50,
    "overall_cpc": 0.50,
    "overall_cpa": 34.72,
    "overall_roas": 1.44,
    "active_campaigns": 5,
    "data_sources": ["surfside", "vibe", "facebook"]
}
```

---

### **3. Get Campaign Breakdown**
```
GET /api/v1/dashboard/campaigns
```

**Purpose:** Performance metrics grouped by campaign

**Query Parameters:**
- `start_date`, `end_date`, `client_id`
- `limit` (default: 10, max: 50): Top N campaigns

**Response Structure:**
```json
[
    {
        "campaign_name": "Prospecting",
        "total_impressions": 250000,
        "total_clicks": 6250,
        "total_conversions": 90,
        "total_revenue": 4500.00,
        "total_spend": 3125.00,
        "ctr": 2.50,
        "cpc": 0.50,
        "cpa": 34.72,
        "roas": 1.44
    },
    ...
]
```

**Sorted By:** Total spend (highest first)

---

### **4. Get Source Breakdown**
```
GET /api/v1/dashboard/sources
```

**Purpose:** Performance comparison across data sources

**Response Structure:**
```json
[
    {
        "source": "surfside",
        "total_impressions": 300000,
        "total_clicks": 7500,
        "total_conversions": 108,
        "total_revenue": 5400.00,
        "total_spend": 3750.00,
        "ctr": 2.50,
        "cpc": 0.50,
        "cpa": 34.72,
        "roas": 1.44
    },
    {
        "source": "vibe",
        ...
    },
    {
        "source": "facebook",
        ...
    }
]
```

---

### **5. Get Daily Trends**
```
GET /api/v1/dashboard/trends
```

**Purpose:** Time-series data for charting

**Response Structure:**
```json
[
    {
        "date": "2025-12-01",
        "impressions": 20000,
        "clicks": 500,
        "conversions": 7,
        "revenue": 350.00,
        "spend": 250.00
    },
    {
        "date": "2025-12-02",
        "impressions": 21000,
        "clicks": 525,
        "conversions": 8,
        "revenue": 400.00,
        "spend": 262.50
    },
    ...
]
```

**Use Case:** Line charts showing metrics over time

---

### **6. Get Top Performers**
```
GET /api/v1/dashboard/top-performers
```

**Purpose:** Best performing entities across multiple dimensions

**Query Parameters:**
- `start_date`, `end_date`, `client_id`
- `limit` (default: 5, max: 20): Top N per category

**Response Structure:**
```json
{
    "top_campaigns_by_roas": [
        {
            "name": "Retargeting Campaign",
            "value": 4.85,
            "metric_label": "ROAS"
        },
        ...
    ],
    "top_campaigns_by_conversions": [...],
    "top_placements_by_ctr": [...],
    "top_creatives_by_clicks": [...]
}
```

---

### **7. Get Quick Stats**
```
GET /api/v1/dashboard/quick-stats
```

**Purpose:** Snapshot of current performance periods

**Response Structure:**
```json
{
    "today": {
        "total_impressions": 5000,
        "total_spend": 62.50,
        ...
    },
    "this_week": {
        "total_impressions": 35000,
        "total_spend": 437.50,
        ...
    },
    "this_month": {
        "total_impressions": 125000,
        "total_spend": 1562.50,
        ...
    }
}
```

---

## **Testing with Postman**

### **Prerequisites**

1. **Setup Test Data:**
   - Ensure Surfside data uploaded for date range
   - Multiple campaigns with varying performance
   - Data spanning multiple days for trends

2. **Authentication:**
   - POST `/api/v1/auth/login`
   - Store access_token

3. **Get Client ID:**
   - GET `/api/v1/clients`

---

### **Test 1: Get Complete Dashboard**

**Request:**
```
GET http://localhost:8000/api/v1/dashboard/?start_date=2025-11-01&end_date=2025-11-30&client_id=<uuid>
```

**Headers:**
```
Authorization: Bearer <token>
```

**Expected Response (200 OK):**
```json
{
    "summary": {
        "total_impressions": 500000,
        "total_clicks": 12500,
        "total_conversions": 180,
        "total_revenue": 9000.00,
        "total_spend": 6250.00,
        "overall_ctr": 2.50,
        "overall_cpc": 0.50,
        "overall_cpa": 34.72,
        "overall_roas": 1.44,
        "active_campaigns": 5,
        "data_sources": ["surfside", "vibe", "facebook"]
    },
    "campaigns": [
        {
            "campaign_name": "Prospecting",
            "total_impressions": 250000,
            ...
        },
        ...
    ],
    "sources": [
        {
            "source": "surfside",
            "total_impressions": 300000,
            ...
        },
        ...
    ],
    "daily_trends": [
        {
            "date": "2025-11-01",
            "impressions": 16667,
            ...
        },
        ...
    ],
    "top_performers": {
        "top_campaigns_by_roas": [...],
        "top_campaigns_by_conversions": [...],
        "top_placements_by_ctr": [...],
        "top_creatives_by_clicks": [...]
    }
}
```

**Verification:**
- All 5 sections present
- Summary metrics match sum of daily_metrics
- Campaigns sorted by spend
- Daily trends have 30 entries (Nov 1-30)
- Top performers show correct top N

---

### **Test 2: Dashboard Summary Only**

**Request:**
```
GET http://localhost:8000/api/v1/dashboard/summary?start_date=2025-11-01&end_date=2025-11-30
```

**Expected Response:**
```json
{
    "total_impressions": 500000,
    "total_clicks": 12500,
    "total_conversions": 180,
    "total_revenue": 9000.00,
    "total_spend": 6250.00,
    "overall_ctr": 2.50,
    "overall_cpc": 0.50,
    "overall_cpa": 34.72,
    "overall_roas": 1.44,
    "active_campaigns": 5,
    "data_sources": ["surfside", "vibe"]
}
```

**Verification:**
- Aggregated totals accurate
- CTR = (12500 / 500000) * 100 = 2.50%
- CPC = 6250 / 12500 = 0.50
- CPA = 6250 / 180 = 34.72
- ROAS = 9000 / 6250 = 1.44
- Active campaigns count correct
- Data sources list unique sources

---

### **Test 3: Campaign Breakdown**

**Request:**
```
GET http://localhost:8000/api/v1/dashboard/campaigns?start_date=2025-11-01&end_date=2025-11-30&limit=10
```

**Expected Response:**
```json
[
    {
        "campaign_name": "Prospecting",
        "total_impressions": 250000,
        "total_clicks": 6250,
        "total_conversions": 90,
        "total_revenue": 4500.00,
        "total_spend": 3125.00,
        "ctr": 2.50,
        "cpc": 0.50,
        "cpa": 34.72,
        "roas": 1.44
    },
    {
        "campaign_name": "Retargeting",
        "total_impressions": 150000,
        ...
    },
    ...
]
```

**Verification:**
- Campaigns sorted by total_spend DESC
- Maximum 10 campaigns returned
- Each campaign shows aggregated metrics
- Totals per campaign accurate

---

### **Test 4: Source Breakdown**

**Request:**
```
GET http://localhost:8000/api/v1/dashboard/sources?start_date=2025-11-01&end_date=2025-11-30
```

**Expected Response:**
```json
[
    {
        "source": "surfside",
        "total_impressions": 300000,
        "total_clicks": 7500,
        "total_conversions": 108,
        "total_revenue": 5400.00,
        "total_spend": 3750.00,
        "ctr": 2.50,
        "cpc": 0.50,
        "cpa": 34.72,
        "roas": 1.44
    },
    {
        "source": "vibe",
        "total_impressions": 150000,
        "total_clicks": 3750,
        "total_conversions": 54,
        "total_revenue": 2700.00,
        "total_spend": 1875.00,
        "ctr": 2.50,
        "cpc": 0.50,
        "cpa": 34.72,
        "roas": 1.44
    },
    {
        "source": "facebook",
        "total_impressions": 50000,
        "total_clicks": 1250,
        "total_conversions": 18,
        "total_revenue": 900.00,
        "total_spend": 625.00,
        "ctr": 2.50,
        "cpc": 0.50,
        "cpa": 34.72,
        "roas": 1.44
    }
]
```

**Verification:**
- All active sources included
- Metrics aggregated per source
- Sum of sources = overall summary totals

---

### **Test 5: Daily Trends**

**Request:**
```
GET http://localhost:8000/api/v1/dashboard/trends?start_date=2025-11-01&end_date=2025-11-07
```

**Expected Response:**
```json
[
    {
        "date": "2025-11-01",
        "impressions": 16667,
        "clicks": 417,
        "conversions": 6,
        "revenue": 300.00,
        "spend": 208.33
    },
    {
        "date": "2025-11-02",
        "impressions": 17000,
        "clicks": 425,
        "conversions": 7,
        "revenue": 350.00,
        "spend": 212.50
    },
    ...
]
```

**Verification:**
- One entry per date in range
- Ordered chronologically
- Use for line chart: X-axis = date, Y-axis = spend/revenue/etc

---

### **Test 6: Top Performers**

**Request:**
```
GET http://localhost:8000/api/v1/dashboard/top-performers?start_date=2025-11-01&end_date=2025-11-30&limit=5
```

**Expected Response:**
```json
{
    "top_campaigns_by_roas": [
        {
            "name": "Retargeting Campaign",
            "value": 4.85,
            "metric_label": "ROAS"
        },
        {
            "name": "Brand Awareness",
            "value": 3.12,
            "metric_label": "ROAS"
        },
        ...
    ],
    "top_campaigns_by_conversions": [
        {
            "name": "Prospecting",
            "value": 90,
            "metric_label": "Conversions"
        },
        ...
    ],
    "top_placements_by_ctr": [
        {
            "name": "Display Banner - Homepage",
            "value": 3.45,
            "metric_label": "CTR %"
        },
        ...
    ],
    "top_creatives_by_clicks": [
        {
            "name": "Creative A",
            "value": 2500,
            "metric_label": "Clicks"
        },
        ...
    ]
}
```

**Verification:**
- Each category shows top N (limit param)
- Sorted DESC by respective metric
- Helpful for quick performance insights

---

### **Test 7: Quick Stats**

**Request:**
```
GET http://localhost:8000/api/v1/dashboard/quick-stats
```

**Expected Response:**
```json
{
    "today": {
        "total_impressions": 5000,
        "total_clicks": 125,
        "total_conversions": 2,
        "total_revenue": 100.00,
        "total_spend": 62.50,
        "overall_ctr": 2.50,
        "overall_cpc": 0.50,
        "overall_cpa": 31.25,
        "overall_roas": 1.60,
        "active_campaigns": 3,
        "data_sources": ["surfside"]
    },
    "this_week": {
        "total_impressions": 35000,
        "total_clicks": 875,
        "total_conversions": 14,
        "total_revenue": 700.00,
        "total_spend": 437.50,
        "overall_ctr": 2.50,
        "overall_cpc": 0.50,
        "overall_cpa": 31.25,
        "overall_roas": 1.60,
        "active_campaigns": 4,
        "data_sources": ["surfside", "vibe"]
    },
    "this_month": {
        "total_impressions": 125000,
        "total_clicks": 3125,
        "total_conversions": 45,
        "total_revenue": 2250.00,
        "total_spend": 1562.50,
        "overall_ctr": 2.50,
        "overall_cpc": 0.50,
        "overall_cpa": 34.72,
        "overall_roas": 1.44,
        "active_campaigns": 5,
        "data_sources": ["surfside", "vibe", "facebook"]
    }
}
```

**Verification:**
- Today = current date
- This week = Monday to today
- This month = 1st of month to today
- Each period shows appropriate scope

---

## **Database Verification**

### **Verify Summary Calculations:**
```sql
-- Manual aggregation to compare
SELECT 
    SUM(impressions) as total_impressions,
    SUM(clicks) as total_clicks,
    SUM(conversions) as total_conversions,
    SUM(conversion_revenue) as total_revenue,
    SUM(spend) as total_spend,
    ROUND(AVG(ctr), 2) as avg_ctr,
    COUNT(DISTINCT campaign_id) as active_campaigns
FROM daily_metrics
WHERE client_id = '<client-uuid>'
  AND date BETWEEN '2025-11-01' AND '2025-11-30';
```

**Should match dashboard summary totals**

### **Verify Campaign Breakdown:**
```sql
SELECT 
    campaign_name,
    SUM(impressions) as total_impressions,
    SUM(clicks) as total_clicks,
    SUM(conversions) as total_conversions,
    SUM(conversion_revenue) as total_revenue,
    SUM(spend) as total_spend
FROM daily_metrics
WHERE client_id = '<client-uuid>'
  AND date BETWEEN '2025-11-01' AND '2025-11-30'
GROUP BY campaign_name
ORDER BY SUM(spend) DESC
LIMIT 10;
```

**Should match dashboard campaigns array**

### **Verify Daily Trends:**
```sql
SELECT 
    date,
    SUM(impressions) as impressions,
    SUM(clicks) as clicks,
    SUM(conversions) as conversions,
    SUM(conversion_revenue) as revenue,
    SUM(spend) as spend
FROM daily_metrics
WHERE client_id = '<client-uuid>'
  AND date BETWEEN '2025-11-01' AND '2025-11-07'
GROUP BY date
ORDER BY date;
```

**Should match dashboard trends array**

---

## **Access Control Testing**

### **Admin User Tests:**
- [ ] Can access dashboard for any client via client_id param
- [ ] Can see all campaigns across all clients
- [ ] Quick stats show all data sources

### **Client User Tests:**
- [ ] Automatically filtered to own client (client_id ignored)
- [ ] Cannot see other clients' data
- [ ] Quick stats show only own client's sources

### **Test Forbidden Access:**
```
GET /dashboard/?client_id=<other-client-uuid>
(Logged in as client user)
```

**Expected:** Data filtered to current user's client, not other-client-uuid

---

## **Performance Testing**

### **Large Date Ranges:**
```
GET /dashboard/?start_date=2024-01-01&end_date=2025-12-31
```

**Expected:**
- Query completes in < 3 seconds
- Aggregations accurate
- No timeout errors

### **Many Campaigns:**
```
GET /dashboard/campaigns?limit=50
(For client with 100+ active campaigns)
```

**Expected:**
- Returns top 50 by spend
- Query optimized with proper indexes
- Response time < 2 seconds

---

## **Error Handling Tests**

### **Test: Missing Date Range**
```
GET /dashboard/
```

**Expected:** 422 Unprocessable Entity (start_date and end_date required)

### **Test: Invalid Date Format**
```
GET /dashboard/?start_date=2025-13-45&end_date=2025-11-30
```

**Expected:** 422 Unprocessable Entity

### **Test: Client Not Found**
```
GET /dashboard/?start_date=2025-11-01&end_date=2025-11-30&client_id=<invalid-uuid>
```

**Expected:** 404 Not Found (client not found)

### **Test: No Data for Date Range**
```
GET /dashboard/?start_date=2020-01-01&end_date=2020-01-31
```

**Expected Response:**
```json
{
    "summary": {
        "total_impressions": 0,
        "total_clicks": 0,
        ...
        "overall_ctr": 0.00,
        "overall_cpc": null,
        ...
    },
    "campaigns": [],
    "sources": [],
    "daily_trends": [],
    "top_performers": {
        "top_campaigns_by_roas": [],
        ...
    }
}
```

---

## **Frontend Integration Examples**

### **React Dashboard Component:**

```javascript
import { useState, useEffect } from 'react';

function Dashboard() {
    const [data, setData] = useState(null);
    
    useEffect(() => {
        fetch('/api/v1/dashboard/?start_date=2025-11-01&end_date=2025-11-30', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(res => res.json())
        .then(setData);
    }, []);
    
    if (!data) return <div>Loading...</div>;
    
    return (
        <div>
            <h1>Dashboard</h1>
            
            {/* Summary Cards */}
            <div className="summary">
                <Card label="Impressions" value={data.summary.total_impressions} />
                <Card label="Clicks" value={data.summary.total_clicks} />
                <Card label="Spend" value={`$${data.summary.total_spend}`} />
                <Card label="ROAS" value={data.summary.overall_roas} />
            </div>
            
            {/* Campaign Table */}
            <table>
                <thead>
                    <tr>
                        <th>Campaign</th>
                        <th>Spend</th>
                        <th>Conversions</th>
                        <th>ROAS</th>
                    </tr>
                </thead>
                <tbody>
                    {data.campaigns.map(c => (
                        <tr key={c.campaign_name}>
                            <td>{c.campaign_name}</td>
                            <td>${c.total_spend}</td>
                            <td>{c.total_conversions}</td>
                            <td>{c.roas}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
            
            {/* Chart */}
            <LineChart data={data.daily_trends} />
        </div>
    );
}
```

---

## **Common Use Cases**

### **1. Executive Summary:**
- GET `/dashboard/summary` for current month
- Display KPIs: Impressions, Spend, ROAS
- Show month-over-month comparison

### **2. Campaign Optimization:**
- GET `/dashboard/campaigns` 
- Identify underperformers (low ROAS, high CPA)
- Pause or adjust campaigns

### **3. Budget Allocation:**
- GET `/dashboard/sources`
- Compare Surfside vs Vibe vs Facebook performance
- Shift budget to best performing source

### **4. Trend Analysis:**
- GET `/dashboard/trends` for last 90 days
- Plot in line chart
- Identify seasonal patterns or anomalies

### **5. Performance Highlights:**
- GET `/dashboard/top-performers`
- Show in weekly stakeholder report
- Highlight wins to celebrate

---

## **Production Recommendations**

1. **Caching:**
   - Cache dashboard data for 5-15 minutes
   - Use Redis with TTL
   - Invalidate on new data ingestion

2. **Real-Time Updates:**
   - WebSocket connection for live updates
   - Auto-refresh every 5 minutes
   - Show "last updated" timestamp

3. **Materialized Views:**
```sql
-- Create for faster queries
CREATE MATERIALIZED VIEW campaign_daily_summary AS
SELECT 
    client_id,
    date,
    campaign_name,
    SUM(impressions) as total_impressions,
    SUM(spend) as total_spend,
    ...
FROM daily_metrics
GROUP BY client_id, date, campaign_name;

-- Refresh daily
REFRESH MATERIALIZED VIEW campaign_daily_summary;
```

4. **Query Optimization:**
   - Add covering indexes
   - Denormalize frequently queried data
   - Partition large tables by date

5. **Monitoring:**
   - Track dashboard API response times
   - Alert if > 2 seconds
   - Monitor database query performance

---

## **Expected Test Results Summary**

✅ **All Tests Passing:**
- Complete dashboard returns all 5 sections
- Summary shows accurate aggregated totals
- Campaign breakdown sorted by spend
- Source breakdown includes all active sources
- Daily trends show one entry per date
- Top performers identify best entities
- Quick stats calculate today/week/month correctly
- Access control enforced (admin vs client)
- Large date ranges perform adequately
- Error handling works for edge cases

🎯 **Dashboard Ready for Production**

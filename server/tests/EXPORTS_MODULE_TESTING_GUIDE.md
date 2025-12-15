# Exports Module Testing Guide (CSV & PDF)

## **Module Overview**

The Exports module (`app/exports/`) provides functionality to export performance data in CSV and PDF formats for reporting and analysis.

### **Purpose**
- Export daily metrics to CSV for Excel analysis
- Export campaign summaries to CSV
- Generate PDF dashboard reports with charts and tables
- Support date range filtering and client-specific exports

### **Key Components**
- **CSV Export Service** (`csv_export.py`): Generates CSV files
- **PDF Export Service** (`pdf_export.py`): Generates PDF reports with ReportLab
- **Router** (`router.py`): API endpoints for downloading exports

---

## **Available Endpoints**

### **1. Export Daily Metrics to CSV**
```
GET /api/v1/exports/csv/daily-metrics
```

**Query Parameters:**
- `start_date` (required): Start date (YYYY-MM-DD)
- `end_date` (required): End date (YYYY-MM-DD)
- `client_id` (optional): Filter by client (admin only)
- `source` (optional): Filter by source (surfside/vibe/facebook)

**Response:** CSV file download

### **2. Export Campaign Summary to CSV**
```
GET /api/v1/exports/csv/campaign-summary
```

**Query Parameters:**
- `start_date` (required): Start date
- `end_date` (required): End date
- `client_id` (optional): Filter by client (admin only)

**Response:** Aggregated campaign CSV

### **3. Export Dashboard Report to PDF**
```
GET /api/v1/exports/pdf/dashboard-report
```

**Query Parameters:**
- `start_date` (required): Start date
- `end_date` (required): End date
- `client_id` (optional): Filter by client (admin only)

**Response:** PDF file download

---

## **CSV Export Structure**

### **Daily Metrics CSV Columns:**
```csv
Date,Campaign,Strategy,Placement,Creative,Source,Impressions,Clicks,Conversions,Revenue,CTR (%),Spend,CPC,CPA,ROAS
2025-12-14,Holiday Campaign,Retargeting,Banner Ad,Creative A,surfside,50000,1250,45,2250.00,2.50,625.00,0.50,13.89,3.60
```

### **Campaign Summary CSV Columns:**
```csv
Campaign,Total Impressions,Total Clicks,Total Conversions,Total Revenue,Total Spend,CTR (%),CPC,CPA,ROAS
Holiday Campaign,500000,12500,450,22500.00,6250.00,2.50,0.50,13.89,3.60
```

---

## **PDF Report Structure**

### **Report Sections:**
1. **Header**
   - Client name and logo
   - Date range
   - Report generation timestamp

2. **Summary Section**
   - Total impressions, clicks, conversions
   - Total spend and revenue
   - Overall CTR, CPC, CPA, ROAS

3. **Campaign Breakdown Table**
   - Top 10 campaigns by spend
   - Performance metrics per campaign

4. **Source Breakdown**
   - Performance by data source (Surfside, Vibe, Facebook)

5. **Daily Trends Chart**
   - Line graph showing daily metrics over time

6. **Top Performers**
   - Best campaigns by ROAS
   - Best creatives by CTR
   - Best placements by conversions

---

## **Testing with Postman**

### **Step 1: Authenticate**

1. **POST** `http://localhost:8000/api/v1/auth/login`
2. Body (x-www-form-urlencoded):
   - `username`: admin@example.com
   - `password`: your_password
3. Copy the `access_token`

### **Step 2: Export Daily Metrics CSV**

1. **GET** `http://localhost:8000/api/v1/exports/csv/daily-metrics`
2. **Params:**
   - `start_date`: 2025-12-01
   - `end_date`: 2025-12-15
   - `client_id`: <your_client_uuid>
   - `source`: surfside *(optional)*
3. **Auth:** Bearer Token (paste access_token)
4. **Send**

**Expected Response:**
- Status: 200 OK
- Headers: `Content-Disposition: attachment; filename=daily_metrics_2025-12-01_2025-12-15.csv`
- Body: CSV content (viewable in Postman or downloads as file)

**Postman Tips:**
- Click "Send and Download" to save file
- Or view response in "Preview" tab as formatted table

### **Step 3: Export Campaign Summary CSV**

1. **GET** `http://localhost:8000/api/v1/exports/csv/campaign-summary`
2. **Params:**
   - `start_date`: 2025-12-01
   - `end_date`: 2025-12-15
   - `client_id`: <your_client_uuid>
3. **Auth:** Bearer Token
4. **Send and Download**

**Expected Response:**
- CSV with aggregated campaign data
- One row per campaign
- Sorted by total spend (descending)

### **Step 4: Export PDF Dashboard Report**

1. **GET** `http://localhost:8000/api/v1/exports/pdf/dashboard-report`
2. **Params:**
   - `start_date`: 2025-12-01
   - `end_date`: 2025-12-15
   - `client_id`: <your_client_uuid>
3. **Auth:** Bearer Token
4. **Send and Download**

**Expected Response:**
- Status: 200 OK
- Headers: `Content-Type: application/pdf`
- Headers: `Content-Disposition: attachment; filename=dashboard_report_2025-12-01_2025-12-15.pdf`
- PDF file downloads automatically

---

## **Testing with cURL (Command Line)**

### **Export CSV:**
```powershell
$token = "your_access_token_here"
$url = "http://localhost:8000/api/v1/exports/csv/daily-metrics?start_date=2025-12-01&end_date=2025-12-15&client_id=<uuid>"

Invoke-WebRequest -Uri $url `
  -Headers @{"Authorization"="Bearer $token"} `
  -OutFile "daily_metrics.csv"
```

### **Export PDF:**
```powershell
$token = "your_access_token_here"
$url = "http://localhost:8000/api/v1/exports/pdf/dashboard-report?start_date=2025-12-01&end_date=2025-12-15&client_id=<uuid>"

Invoke-WebRequest -Uri $url `
  -Headers @{"Authorization"="Bearer $token"} `
  -OutFile "dashboard_report.pdf"
```

---

## **Verification Checklist**

### **CSV Export Checks**
- [ ] File downloads successfully
- [ ] CSV opens in Excel/Google Sheets
- [ ] All columns present and labeled correctly
- [ ] Date formatting is correct (YYYY-MM-DD)
- [ ] Numbers formatted with proper decimals
- [ ] Currency values show 2 decimal places
- [ ] Percentages calculated correctly
- [ ] Data matches database records
- [ ] Empty values show as blank (not "None")
- [ ] Special characters don't break formatting

### **PDF Export Checks**
- [ ] PDF opens without errors
- [ ] Client name displays correctly
- [ ] Date range shown in header
- [ ] All sections included (summary, breakdown, trends, top performers)
- [ ] Tables formatted and readable
- [ ] Numbers aligned properly
- [ ] Charts/graphs render (if implemented)
- [ ] Page breaks work correctly
- [ ] Footer includes page numbers
- [ ] No text overflow or truncation

---

## **Common Export Scenarios**

### **Scenario 1: Full Month Export**
```
start_date: 2025-12-01
end_date: 2025-12-31
Result: All December data for client
```

### **Scenario 2: Week-over-Week Comparison**
Export two CSVs:
```
Week 1: 2025-12-01 to 2025-12-07
Week 2: 2025-12-08 to 2025-12-15
Compare in Excel pivot table
```

### **Scenario 3: Multi-Source Analysis**
```
Export 1: source=surfside
Export 2: source=vibe
Export 3: source=facebook
Compare source performance
```

### **Scenario 4: Campaign Deep Dive**
```
1. Export campaign summary CSV
2. Identify top campaign
3. Export daily metrics filtered by that campaign
4. Generate PDF for stakeholder presentation
```

---

## **Database Verification**

Before exporting, verify data exists:

```sql
-- Check daily metrics for date range
SELECT 
    date,
    source,
    COUNT(*) as record_count,
    SUM(impressions) as total_impressions,
    SUM(spend) as total_spend
FROM daily_metrics
WHERE client_id = '<client_uuid>'
  AND date BETWEEN '2025-12-01' AND '2025-12-15'
GROUP BY date, source
ORDER BY date DESC;

-- Verify export will have data
SELECT COUNT(*) FROM daily_metrics
WHERE client_id = '<client_uuid>'
  AND date BETWEEN '2025-12-01' AND '2025-12-15';
```

If count is 0, upload test data first!

---

## **Troubleshooting**

### **Error: "No data found for export"**
**Cause:** No metrics in database for date range
**Solution:**
- Upload Facebook/Surfside data
- Adjust date range to match available data
- Verify client_id is correct

### **Error: "Client not found"**
**Cause:** Invalid client_id UUID
**Solution:**
- GET `/api/v1/clients` to get valid client IDs
- Ensure UUID format is correct

### **Error: 403 Forbidden**
**Cause:** Client user trying to export another client's data
**Solution:**
- Login as admin, OR
- Omit client_id parameter (will use current user's client)

### **CSV Opens as Gibberish in Excel**
**Cause:** Encoding issue
**Solution:**
- Save file with UTF-8 encoding
- Use Excel "Data → From Text/CSV" import wizard
- Specify UTF-8 encoding during import

### **PDF Generation Fails**
**Cause:** ReportLab library missing or corrupted
**Solution:**
```powershell
pip install --upgrade reportlab
```

### **PDF Charts Not Rendering**
**Cause:** Missing chart implementation (may be TODO)
**Solution:**
- Check if charts are implemented in PDF service
- For now, rely on tabular data only

---

## **Performance Considerations**

### **Large Exports:**
For exports > 100,000 records:
- Expect 5-15 second generation time
- CSV generation is faster than PDF
- Consider pagination or splitting by month

### **Memory Usage:**
- CSV: ~1MB per 10,000 records
- PDF: ~2-3MB per 10,000 records (with styling)

### **Optimization Tips:**
- Use date range filtering
- Filter by source if only need one
- Export campaigns separately if needed
- Schedule large exports during off-peak hours

---

## **Excel Analysis Examples**

After exporting CSV, you can:

### **1. Pivot Table Analysis**
```
Rows: Campaign
Columns: Date
Values: Sum of Spend, Sum of Conversions
```

### **2. Chart Creation**
- Select date and spend columns
- Insert → Line Chart
- Shows spend trend over time

### **3. Conditional Formatting**
- Highlight ROAS > 3.0 in green
- Highlight CPA > 20 in red
- Shows performance at a glance

### **4. Formulas**
```excel
=AVERAGE(K:K)  // Average CTR
=SUM(L:L)      // Total Spend
=MAX(O:O)      // Best ROAS
```

---

## **API Integration Examples**

### **Python Script to Auto-Download Daily:**

```python
import requests
from datetime import date, timedelta

API_URL = "http://localhost:8000/api/v1"
TOKEN = "your_access_token"

def download_daily_export():
    yesterday = date.today() - timedelta(days=1)
    
    response = requests.get(
        f"{API_URL}/exports/csv/daily-metrics",
        params={
            "start_date": yesterday,
            "end_date": yesterday,
            "client_id": "your-client-uuid"
        },
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    
    with open(f"metrics_{yesterday}.csv", "wb") as f:
        f.write(response.content)
    
    print(f"Downloaded metrics for {yesterday}")

download_daily_export()
```

---

## **Production Recommendations**

1. **Caching**
   - Cache frequently requested exports (24h TTL)
   - Use Redis for caching large CSVs
   - Invalidate cache on new data ingestion

2. **Compression**
   - GZIP compress large CSV files
   - Reduce download size by 80%+

3. **Async Generation**
   - For exports > 50MB, use background tasks
   - Email download link when ready
   - Show progress indicator

4. **Access Control**
   - Log all export requests
   - Rate limit to prevent abuse
   - Audit trail for compliance

5. **Scheduled Exports**
   - Auto-generate weekly reports
   - Email to stakeholders every Monday
   - S3 archival for historical exports

---

## **Expected Test Results**

### **Successful CSV Export:**
```csv
Date,Campaign,Strategy,Placement,Creative,Source,Impressions,Clicks,Conversions,Revenue,CTR (%),Spend,CPC,CPA,ROAS
2025-12-14,Prospecting,Audience | Cannabis Consumers,Ad Placement,Creative 2,surfside,8865,6,0,0.00,0.07,110.81,18.47,,0.00
2025-12-13,Prospecting,Audience | Cannabis Consumers,Ad Placement,Creative 2,surfside,7234,4,0,0.00,0.06,90.43,22.61,,0.00
```

### **Successful PDF Report:**
- File size: 150KB - 500KB
- Multiple pages with proper formatting
- Logo and branding present
- All metrics calculated correctly
- Tables fit within page margins

---

## **Client Use Cases**

### **Monthly Board Report:**
1. Export PDF dashboard report for previous month
2. Includes all visualizations and summaries
3. Present to executives/stakeholders

### **Campaign Optimization:**
1. Export campaign summary CSV
2. Identify underperforming campaigns (high CPA, low ROAS)
3. Pause or adjust targeting

### **Budget Reconciliation:**
1. Export daily metrics CSV for billing period
2. Sum spend column in Excel
3. Match against invoices from ad platforms

### **Trend Analysis:**
1. Export last 90 days to CSV
2. Create line charts in Excel
3. Identify seasonal patterns or anomalies

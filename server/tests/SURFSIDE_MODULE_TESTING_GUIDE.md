# Surfside Module Testing Guide (Postman Edition)

This guide provides step-by-step instructions to test the Surfside module using **Postman** for manual file uploads (simulating S3 ingestion), spanning file uploads, ETL processing, and data verification.

## **1. Prerequisites**

Before starting, ensure you have:
1.  **Postman Installed**: Download it [here](https://www.postman.com/downloads/).
2.  **Running Server**: The FastAPI server must be running locally at `http://localhost:8000` (or your configured port).
3.  **Database**: PostgreSQL must be running, and the schema must be applied.
4.  **Admin Credentials**: Valid admin email and password.
5.  **No S3 Access Required**: This guide uses manual file upload instead of S3 automation.

---

## **2. Test Data Preparation**

Create a CSV file named `surfside_test_data.csv` on your local machine with the following content.

**File Content (`surfside_test_data.csv`):**
```csv
Date,Campaign,Strategy,Placement,Creative,Impressions,Clicks,Conversions,Conversion Revenue,CTR
2025-12-01,Holiday Campaign 2025,Retargeting Strategy,Display Banner - Homepage,Creative A,50000,1250,45,2250.00,2.50
2025-12-01,Holiday Campaign 2025,Retargeting Strategy,Display Banner - Product Page,Creative B,35000,980,32,1600.00,2.80
2025-12-01,Brand Awareness Q4,Prospecting Strategy,Video Ad - YouTube,Creative C,120000,2400,15,750.00,2.00
2025-12-02,Holiday Campaign 2025,Retargeting Strategy,Display Banner - Homepage,Creative A,52000,1350,48,2400.00,2.60
2025-12-02,Brand Awareness Q4,Prospecting Strategy,Native Ad - News Sites,Creative D,85000,1700,22,1100.00,2.00
```

**Alternative XLSX Test File:**
You can also create an Excel file (`surfside_test_data.xlsx`) with the same data structure.

*Save the file to a known location, e.g., your Desktop.*

---

## **3. Surfside Data Format Specification**

### **Required Columns:**
- `Date`: Date in YYYY-MM-DD format
- `Campaign`: Campaign name
- `Strategy`: Strategy/Ad Set name
- `Placement`: Placement identifier
- `Creative`: Creative name or identifier
- `Impressions`: Number of impressions (integer)
- `Clicks`: Number of clicks (integer)
- `Conversions`: Number of conversions (integer)
- `Conversion Revenue`: Revenue from conversions (decimal)

### **Optional Columns:**
- `CTR`: Click-through rate (will be calculated if not provided)

### **Data Mapping:**
```
Surfside Structure → Database Metrics
├── Date → date
├── Campaign → campaign_name
├── Strategy → strategy_name
├── Placement → placement_name
├── Creative → creative_name
├── Impressions → impressions
├── Clicks → clicks
├── Conversions → conversions
└── Conversion Revenue → conversion_revenue
```

---

## **4. Step-by-Step Postman Testing Guide**

### **Step 1: Authenticate (Get Token)**

1.  Create a new **POST** request in Postman.
2.  **URL**: `http://localhost:8000/api/v1/auth/login`
3.  **Body**:
    *   Select **x-www-form-urlencoded**.
    *   Key: `username` | Value: `admin@example.com`
    *   Key: `password` | Value: `your_secure_password`
4.  **Send** the request.
5.  **Copy the Token**: In the response JSON, copy the `access_token` string (without quotes).

**Expected Response (200 OK):**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

---

### **Step 2: Get Client ID**

1.  Create a new **GET** request.
2.  **URL**: `http://localhost:8000/api/v1/clients`
3.  **Auth**:
    *   Go to the **Authorization** tab.
    *   Type: **Bearer Token**.
    *   Token: Paste the token from Step 1.
4.  **Send** the request.
5.  **Copy Client ID**: Find your target client in the list and copy their `id` (UUID format).

**Expected Response (200 OK):**
```json
[
    {
        "id": "a2d6c8ee-e906-4764-8948-30d84d27ebf9",
        "name": "Test Client",
        "cpm": 15.00,
        ...
    }
]
```

---

### **Step 3: Upload Surfside File (Core Test)**

This step uploads the CSV/XLSX file using `multipart/form-data`.

1.  Create a new **POST** request.
2.  **URL**: `http://localhost:8000/api/v1/surfside/upload`
3.  **Params** (Query Params):
    *   Key: `client_id` | Value: `<your_copied_client_id>`
4.  **Auth**:
    *   Go to **Authorization** tab.
    *   Type: **Bearer Token**.
    *   Token: Paste your token.
5.  **Body**:
    *   Select **form-data** (IMPORTANT).
    *   **Key**: Type `file`.
    *   **Type**: Hover over the right side of the Key field. Change dropdown from "Text" to **File**.
    *   **Value**: Click "Select File" and choose `surfside_test_data.csv` from your computer.
6.  **Send** the request.

**Expected Response (200 OK):**
```json
{
    "upload_id": "73e1c9a6-b120-4eac-a8e3-a20e3af9d144",
    "file_name": "surfside_test_data.csv",
    "status": "processed",
    "records_count": 5,
    "created_at": "2025-12-15T10:30:00.123456",
    "processed_at": "2025-12-15T10:30:05.654321",
    "error_message": null
}
```

**Status Values:**
- `pending`: Upload received, not yet processed
- `processing`: Currently parsing and running ETL
- `processed`: Successfully completed
- `failed`: Error occurred (check `error_message`)

---

### **Step 4: Verify Upload History**

1.  Create a new **GET** request.
2.  **URL**: `http://localhost:8000/api/v1/surfside/uploads/<your_client_id>`
3.  **Auth**: Bearer Token (same as above).
4.  **Optional Query Params**:
    *   Key: `limit` | Value: `50` (default: 50, max: 100)
5.  **Send** the request.

**Expected Response (200 OK):**
```json
{
    "uploads": [
        {
            "upload_id": "73e1c9a6-b120-4eac-a8e3-a20e3af9d144",
            "file_name": "surfside_test_data.csv",
            "status": "processed",
            "records_count": 5,
            "created_at": "2025-12-15T10:30:00.123456",
            "processed_at": "2025-12-15T10:30:05.654321",
            "error_message": null
        }
    ],
    "total": 1
}
```

---

### **Step 5: Get Specific Upload Details**

1.  Create a new **GET** request.
2.  **URL**: `http://localhost:8000/api/v1/surfside/upload/<upload_id>`
3.  **Auth**: Bearer Token.
4.  **Send** the request.

**Expected Response (200 OK):**
```json
{
    "upload_id": "73e1c9a6-b120-4eac-a8e3-a20e3af9d144",
    "file_name": "surfside_test_data.csv",
    "status": "processed",
    "records_count": 5,
    "created_at": "2025-12-15T10:30:00.123456",
    "processed_at": "2025-12-15T10:30:05.654321",
    "error_message": null
}
```

---

## **5. Database Verification (SQL)**

After successful upload, verify the data was processed correctly using SQL queries.

### **5.1 Check Daily Metrics (Final Destination)**

```sql
SELECT 
    date,
    campaign_name,
    strategy_name,
    placement_name,
    creative_name,
    impressions,
    clicks,
    conversions,
    conversion_revenue,
    spend,
    ctr
FROM daily_metrics 
WHERE client_id = '<your_client_id>' 
  AND source = 'surfside'
ORDER BY date DESC, created_at DESC
LIMIT 10;
```

**Expected Results:**
- 5 rows (matching the 5 records in test CSV)
- `spend` should be calculated: `(impressions / 1000) * client_cpm`
- `ctr` should be calculated: `(clicks / impressions) * 100`
- All campaign/strategy/placement names should match test data

---

### **5.2 Check Staging Area (Raw Data)**

```sql
SELECT 
    campaign_name,
    strategy_name,
    placement_name,
    impressions,
    clicks,
    conversions,
    conversion_revenue,
    raw_data
FROM staging_media_raw 
WHERE campaign_name = 'Holiday Campaign 2025'
ORDER BY created_at DESC;
```

**Verify:**
- Raw records are stored in `raw_data` JSONB column
- All field mappings are correct
- Source is 'surfside'

---

### **5.3 Check Upload Records**

```sql
SELECT 
    id,
    client_id,
    file_name,
    upload_status,
    records_count,
    created_at,
    processed_at,
    error_message
FROM uploaded_files 
WHERE source = 'surfside' 
  AND client_id = '<your_client_id>'
ORDER BY created_at DESC;
```

**Verify:**
- `upload_status` is 'processed'
- `records_count` is 5
- `processed_at` is populated
- `error_message` is NULL

---

### **5.4 Check Ingestion Logs**

```sql
SELECT 
    id,
    client_id,
    source,
    status,
    records_processed,
    records_failed,
    message,
    run_date,
    created_at
FROM ingestion_logs 
WHERE source = 'surfside' 
  AND client_id = '<your_client_id>'
ORDER BY created_at DESC;
```

**Verify:**
- `status` is 'success'
- `records_processed` is 5
- `records_failed` is 0
- `message` contains success details

---

## **6. Common Postman Errors & Troubleshooting**

| Error | Cause | Fix |
| :--- | :--- | :--- |
| **422 Unprocessable Entity** | Missing columns in CSV or wrong body type | Ensure **Body** is set to **form-data** and file has all required columns |
| **401 Unauthorized** | Missing or expired token | Re-authenticate and paste fresh token in **Auth** tab |
| **403 Forbidden** | Wrong user role or client ID mismatch | Ensure you're Admin or the client owner for that ID |
| **404 Not Found** | Wrong URL or Client ID doesn't exist | Check URL spelling and verify UUID exists in database |
| **500 Internal Error** | Server-side bug or database issue | Check terminal logs where `uvicorn` is running for Python tracebacks |
| **"Missing required columns"** | CSV headers don't match expected format | Verify column names: `Date`, `Campaign`, `Strategy`, `Placement`, `Creative`, `Impressions`, `Clicks`, `Conversions`, `Conversion Revenue` |
| **"File too large"** | File exceeds 100MB limit | Split large files or increase `MAX_FILE_SIZE` in code |
| **"Invalid file type"** | Wrong file extension | Use `.csv`, `.xlsx`, or `.xls` files only |

---

## **7. Advanced Testing Scenarios**

### **7.1 Test with XLSX File**

1. Create `surfside_test_data.xlsx` with the same data structure
2. Upload using same POST endpoint
3. Verify same successful processing

### **7.2 Test Error Handling - Missing Columns**

Create a CSV with missing required columns:
```csv
Date,Campaign,Impressions
2025-12-01,Test Campaign,50000
```

**Expected Response (422 or 500 with error):**
```json
{
    "detail": "Failed to parse file: Missing required columns in Surfside file: Strategy, Placement, Creative, Clicks, Conversions, Conversion Revenue"
}
```

### **7.3 Test Error Handling - Empty File**

1. Create an empty CSV file
2. Upload it
3. Expected: `"File is empty"` error

### **7.4 Test Duplicate Upload**

1. Upload the same file twice
2. Verify two separate upload records are created
3. Check that metrics are duplicated (or deduplicated based on your business logic)

---

## **8. Integration Test Checklist**

- [ ] Authentication successful (Step 1)
- [ ] Client ID retrieved (Step 2)
- [ ] CSV file upload successful (Step 3)
- [ ] XLSX file upload successful (Advanced 7.1)
- [ ] Upload history displays correctly (Step 4)
- [ ] Upload details retrievable (Step 5)
- [ ] Daily metrics created in database (SQL 5.1)
- [ ] Staging records created (SQL 5.2)
- [ ] Upload status is 'processed' (SQL 5.3)
- [ ] Ingestion log shows 'success' (SQL 5.4)
- [ ] Spend calculated correctly (`impressions/1000 * cpm`)
- [ ] CTR calculated correctly (`clicks/impressions * 100`)
- [ ] Error handling works for missing columns (Advanced 7.2)
- [ ] Error handling works for empty file (Advanced 7.3)

---

## **9. Comparison: Surfside vs Facebook Modules**

| Feature | Facebook Module | Surfside Module |
| :--- | :--- | :--- |
| **Upload Endpoint** | `/api/v1/facebook/upload` | `/api/v1/surfside/upload` |
| **Date Column** | `Reporting Starts` (TODO) | `Date` |
| **Campaign Hierarchy** | Campaign → Ad Set → Ad | Campaign → Strategy → Placement → Creative |
| **Required Metrics** | Impressions only (TODO others) | Impressions, Clicks, Conversions, Revenue |
| **Regional Data** | Appends region to placement | N/A |
| **File Formats** | CSV, XLSX | CSV, XLSX |
| **S3 Integration** | No (manual upload only) | Yes (scheduler exists, disabled for testing) |
| **Data Source Tag** | `facebook` | `surfside` |

---

## **10. Next Steps**

After successful Surfside module testing:

1. **Dashboard Integration**: Verify Surfside data appears in dashboard metrics
2. **Export Testing**: Test CSV/PDF exports include Surfside data
3. **Campaign Management**: Ensure Surfside campaigns are manageable via campaign endpoints
4. **Performance Metrics**: Test aggregated metrics (total impressions, spend, ROI)
5. **S3 Scheduler**: When S3 access is available, test automated daily ingestion
6. **Multi-Source Testing**: Upload Facebook + Surfside data for same client and verify aggregation

---

## **11. Production Deployment Notes**

Before deploying Surfside module to production:

- [ ] Configure actual S3 credentials in environment variables
- [ ] Set up S3 bucket structure: `s3://bucket/surfside/<client_prefix>/YYYY-MM-DD_report.csv`
- [ ] Enable daily scheduler for automated S3 ingestion
- [ ] Configure appropriate file size limits for production
- [ ] Set up monitoring/alerts for failed uploads
- [ ] Document Surfside file naming conventions for clients
- [ ] Test S3 download retry logic and error handling
- [ ] Verify database indexes are optimized for Surfside queries

---

## **12. Support & Troubleshooting**

**Server Logs Location:**
Check the terminal where `uvicorn` is running for detailed error messages.

**Database Connection Issues:**
```sql
-- Test connection
SELECT current_database(), current_user;
```

**File Upload Directory:**
Default: `uploads/surfside/<client_id>/`
Verify permissions: `chmod 755 uploads/`

**Common Log Messages:**
- ✓ `"Parsed X records from Surfside file"` - Success
- ✗ `"Missing required columns"` - CSV format error
- ✗ `"File too large"` - Exceeds 100MB limit
- ✗ `"Surfside upload processing failed"` - ETL pipeline error

# Vibe Module Testing Guide (Postman)

This guide provides a complete walkthrough for testing the Vibe Integration module using Postman. It covers the full data flow: **Credentials Configuration -> Ingestion Trigger -> ETL Processing -> Database Verification**.

**Note:** The Vibe module interacts with an external API. For valid functional testing, you need valid Vibe API credentials, or you must expect connection errors in the logs.

---

## **1. Prerequisites**

1.  **Server Running**: `uvicorn app.main:app --reload`
2.  **Admin Token**: You must be logged in as an Admin (`POST /api/v1/auth/login`).
3.  **Client ID**: You need a target client ID (`GET /api/v1/clients`).

---

## **2. Step-by-Step Testing Flow**

### **Step 0: Get Advertiser & App IDs (Utility)**
Use these endpoints to find the correct IDs *before* configuring credentials.

**A. Get Advertiser IDs**
*   **Endpoint:** `GET /api/v1/vibe/utils/advertisers?api_key=YOUR_REAL_API_KEY`
*   **Auth:** Bearer Token (Admin)
*   **Response:**
    ```json
    [
      { "advertiser_id": "e3f628ee-...", "advertiser_name": "My Agency" }
    ]
    ```

**B. Get App IDs (Optional)**
*   **Endpoint:** `GET /api/v1/vibe/utils/apps?api_key=YOUR_REAL_API_KEY&advertiser_id=UUID_FROM_ABOVE`
*   **Response:**
    ```json
    {
      "app_ids": ["com.example.app", "123456"]
    }
    ```

### **Step 1: Configure Vibe Credentials**

Before Vibe data can be fetched, the system needs API keys linked to a client.

*   **Endpoint:** `POST /api/v1/vibe/credentials/{client_id}`
*   **Auth:** Bearer Token (Admin)
*   **Body (JSON):**
    ```json
    {
      "api_key": "vibe_test_key_12345",
      "advertiser_id": "e3f628ee-35a4-4895-80f1-d4f8a56986ad"
    }
    ```
*   **Test:** Send request.
*   **Expected (200 OK):**
    ```json
    {
      "api_key": "vibe_test_key_12345",
      "advertiser_id": "adv_555666",
      "id": "uuid-string...",
      "client_id": "uuid-string...",
      "is_active": true,
      "created_at": "...",
      "updated_at": "..."
    }
    ```

### **Step 2: Verify Credentials Storage**
*   **Endpoint:** `GET /api/v1/vibe/credentials/{client_id}`
*   **Auth:** Bearer Token (Admin)
*   **Expected:** Returns the credentials object you just created.

---

### **Step 3: Trigger Data Ingestion (The Core Test)**
This endpoint manually forces the daily ETL job for a specific client. It simulates what the Scheduler does at 5:00 AM.

*   **Endpoint:** `POST /api/v1/vibe/ingest/{client_id}`
*   **Auth:** Bearer Token (Admin)
*   **Query Params (Optional):**
    *   `target_date`: `2025-01-01` (YYYY-MM-DD). Defaults to yesterday if omitted.
*   **Test:** Send request.
*   **Expected Behavior:**
    *   **Success (200 OK):** If Vibe API connects and processes data.
        ```json
        {
          "status": "success",
          "client_id": "uuid-string...",
          "message": "Successfully ingested Vibe data for 2025-01-01",
          "records_processed": 0
        }
        ```
    *   **Server Error (500):** If Vibe API is unreachable (likely if using fake credentials for testing without mocks). **Check your terminal/console logs for details.**

**Console Log Check:**
Look for logs starting with `[VibeService]` or `[VibeETL]`.
*   *Success flow:* "Requesting report..." -> "Report status: DONE" -> "Downloading..." -> "Processing CSV...".
*   *Failure flow:* "VibeAPIError: 401 Unauthorized" (if fake keys used).

---

## **3. Database Verification (SQL)**

Even if the API call finishes, you must verify the database to ensure the "ETL to Insertion" part worked.

### **3.1 Check Report Requests**
Tracks the async job status with Vibe.
```sql
SELECT * FROM vibe_report_requests 
WHERE client_id = '<your_client_id>' 
ORDER BY created_at DESC;
```
*   **Look for:** `status = 'done'` (or 'failed').
*   **Check:** `download_url` should be populated if success.

### **3.2 Check Raw Data (Staging)**
```sql
SELECT * FROM staging_media_raw 
WHERE client_id = '<your_client_id>' 
AND creative_name LIKE '%vibe%'; -- Vibe/Surfside data usually identified by source/campaigns
```

### **3.3 Check Final Metrics (Crucial)**
The ultimate goal is data in `daily_metrics`.
```sql
SELECT * FROM daily_metrics 
WHERE client_id = '<your_client_id>' 
AND source = 'vibe' 
ORDER BY date DESC;
```
*   **Verify Spend:** Ensure `spend` = `(Impressions / 1000) * Client_CPM`.

---

## **4. Troubleshooting Common Errors**

| Error | Cause | Fix |
| :--- | :--- | :--- |
| **404 Client Not Found** | Invalid UUID in URL. | Copy ID from `GET /api/v1/clients`. |
| **400 No Credentials** | Step 1 skipped. | Run Step 1 to add credentials first. |
| **500 VibeAPIError** | Invalid API Key/Advertiser ID. | Use valid real-world Vibe credentials or Mock API for full integration testing. |
| **Timeout** | Report generation took too long. | In production this runs in background; for testing, try a smaller date range or check logs. |

---

## **5. Cleanup (Optional)**
To reset for a clean test:
```sql
DELETE FROM vibe_credentials WHERE client_id = '<your_client_id>';
DELETE FROM vibe_report_requests WHERE client_id = '<your_client_id>';
```

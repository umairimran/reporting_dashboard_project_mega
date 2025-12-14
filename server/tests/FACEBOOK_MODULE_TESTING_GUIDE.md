# Facebook Module Testing Guide (Postman Edition)

This guide provides step-by-step instructions to test the Facebook module using **Postman**, spanning file uploads, ETL processing, and data verification.

## **1. Prerequisites**

Before starting, ensure you have:
1.  **Postman Installed**: Download it [here](https://www.postman.com/downloads/).
2.  **Running Server**: The FastAPI server must be running locally at `http://localhost:8000` (or your configured port).
3.  **Database**: PostgreSQL must be running, and the schema must be applied.
4.  **Admin Credentials**: Valid admin email and password.

---

## **2. Test Data Preparation**

Create a CSV file named `meta_ads_test.csv` on your local machine with the following content.

**File Content (`meta_ads_test.csv`):**
```csv
Date,Campaign Name,Ad Set Name,Ad Name,Impressions,Clicks,Conversions,Revenue
2025-01-01,Test Campaign 2025,Test AdSet A,Ad Variant 1,1000,50,5,100.00
2025-01-01,Test Campaign 2025,Test AdSet A,Ad Variant 2,2000,80,8,150.50
2025-01-02,Test Campaign 2025,Test AdSet B,Ad Variant 3,1500,60,2,80.00
```
*Save this file to a known location, e.g., your Desktop.*

---

## **3. Step-by-Step Postman Guide**

### **Step 1: Authenticate (Get Token)**

1.  Create a new **POST** request in Postman.
2.  **URL**: `http://localhost:8000/api/v1/auth/login`
3.  **Body**:
    *   Select **x-www-form-urlencoded**.
    *   Key: `username` | Value: `admin@example.com`
    *   Key: `password` | Value: `your_secure_password`
4.  **Send** the request.
5.  **Copy the Token**: In the response JSON, copy the `access_token` string (without quotes).

### **Step 2: Get Client ID**

1.  Create a new **GET** request.
2.  **URL**: `http://localhost:8000/api/v1/clients`
3.  **Auth**:
    *   Go to the **Authorization** tab.
    *   Type: **Bearer Token**.
    *   Token: Paste the token from Step 1.
4.  **Send** the request.
5.  **Copy Client ID**: Find your target client in the list and copy their `id` (e.g., `123e4567-e89b-12d3-a456-426614174000`).

### **Step 3: Upload Facebook File (The Core Test)**

This step uses `multipart/form-data` to upload the file.

1.  Create a new **POST** request.
2.  **URL**: `http://localhost:8000/api/v1/facebook/upload`
3.  **Params** (Query Params):
    *   Key: `client_id` | Value: `<your_copied_client_id>`
4.  **Auth**:
    *   Go to **Authorization** tab.
    *   Type: **Bearer Token**.
    *   Token: Paste your token.
5.  **Body**:
    *   Select **form-data** (IMPORTANT).
    *   **Key**: Type `file`.
    *   **Type**: Hover over the right side of the Key field. You will see a dropdown that says "Text". Change it to **File**.
    *   **Value**: Click "Select File" and choose `meta_ads_test.csv` from your computer.
6.  **Send** the request.

**Expected Response (200 OK):**
```json
{
    "upload_id": "uuid...",
    "file_name": "meta_ads_test.csv",
    "status": "success",
    "records_count": 3,
    ...
}
```

### **Step 4: Verify Upload History**

1.  Create a new **GET** request.
2.  **URL**: `http://localhost:8000/api/v1/facebook/uploads/<your_client_id>`
3.  **Auth**: Bearer Token (same as above).
4.  **Send** the request.
5.  **Verify**: You should see your recent upload in the list.

---

## **4. Database Verification (SQL)**

Postman confirms the API received the file, but SQL confirms the data was processed correctly.

Run these queries in your SQL client (e.g., pgAdmin, DBeaver):

**1. Check Usage Metrics:**
```sql
SELECT * FROM daily_metrics 
WHERE client_id = '<your_client_id>' 
ORDER BY created_at DESC;
```
*   **Check**: Are there 3 rows?
*   **Check**: Is `spend` calculated? (It should be `Impressions / 1000 * Client_CPM`).

**2. Check Staging Area:**
```sql
SELECT * FROM staging_media_raw WHERE campaign_name = 'Test Campaign 2025';
```

---

## **5. Common Postman Errors**

| Error | Cause | Fix |
| :--- | :--- | :--- |
| **422 Unprocessable Entity** | Missing fields or wrong body type. | Ensure **Body** is set to **form-data** and the key is named `file`. |
| **401 Unauthorized** | Missing or expired token. | Go to **Auth** tab and re-paste a fresh token. |
| **403 Forbidden** | Wrong user role or client ID. | Ensure you are Admin or the generic Client Owner for that ID. |
| **404 Not Found** | Wrong URL or Client ID. | Check spelling of URL and UUID. |
| **500 Internal Error** | Server-side bug. | Check the terminal where `uvicorn` is running for python tracebacks. |

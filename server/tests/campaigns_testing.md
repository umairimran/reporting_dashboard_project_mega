# Campaigns Module Guide (Postman)

**Goal:** Manage the 4-Level Campaign Hierarchy (Create, Read, Update, Delete).

**Prerequisites:**
1.  **Auth:** Bearer Token (Admin).
2.  **Base URL:** `http://localhost:8000/api/v1` (`{{baseUrl}}`).

---

## 1. Create Hierarchy (Create)
*See previous guide for Create steps.*
*   **Campaign:** `POST /campaigns`
*   **Strategy:** `POST /campaigns/strategies`
*   **Placement:** `POST /campaigns/placements`
*   **Creative:** `POST /campaigns/creatives`

---

## 2. Update Operations (PUT) 🛡️
**Note:** Only Admin can update entities.

### 2.1 Update Campaign
*   **Method:** `PUT`
*   **URL:** `{{baseUrl}}/campaigns/{campaign_id}`
*   **Body** (Raw JSON):
    ```json
    {
      "name": "Summer Launch 2024 - REVISED"
    }
    ```
*   **Expected:** `200 OK`

### 2.2 Update Strategy
*   **Method:** `PUT`
*   **URL:** `{{baseUrl}}/campaigns/strategies/{strategy_id}`
*   **Body:** `{"name": "New Strategy Name"}`

### 2.3 Update Placement
*   **Method:** `PUT`
*   **URL:** `{{baseUrl}}/campaigns/placements/{placement_id}`
*   **Body:** `{"name": "New Placement Name"}`

### 2.4 Update Creative
*   **Method:** `PUT`
*   **URL:** `{{baseUrl}}/campaigns/creatives/{creative_id}`
*   **Body:**
    ```json
    {
      "name": "new_video.mp4",
      "preview_url": "http://new-url.com"
    }
    ```

---

## 3. Delete Operations (DELETE) ⚠️
**Warning:** Deleting a parent deletes ALL children (Cascade).
*   Deleting a Campaign -> Deletes its Strategies, Placements, Creatives.

### 3.1 Delete Campaign
*   **Method:** `DELETE`
*   **URL:** `{{baseUrl}}/campaigns/{campaign_id}`
*   **Expected:** `204 No Content`

### 3.2 Delete Strategy
*   **Method:** `DELETE`
*   **URL:** `{{baseUrl}}/campaigns/strategies/{strategy_id}`

### 3.3 Delete Placement
*   **Method:** `DELETE`
*   **URL:** `{{baseUrl}}/campaigns/placements/{placement_id}`

### 3.4 Delete Creative
*   **Method:** `DELETE`
*   **URL:** `{{baseUrl}}/campaigns/creatives/{creative_id}`

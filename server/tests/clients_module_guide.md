# Clients Module Guide (Postman)

**Goal:** Manage Client entities and their CPM configurations.

**Prerequisites:**
1.  **Admin Token:** You must be logged in as an Admin (`/auth/login`).
2.  **Base URL:** `{{baseUrl}}` refers to `http://localhost:8000/api/v1`.

---

## 1. Helper: Find User ID 🛡️
Instead of listing all users, you can now find a specific user's ID by their email. Use this ID when creating a client.

*   **Method:** `GET`
*   **URL:** `{{baseUrl}}/auth/user-id-by-email`
*   **Authorization:** Bearer Token (Admin).
*   **Params:**
    *   `email`: `client@example.com` (The email of the user you want to link)
*   **Expected:** `200 OK`. Copy the `id` (User UUID) from the response.

---

## 2. Create Client 🛡️
**Step 1:** Get the `user_id` using the helper above.

**Step 2:** Create Request.
*   **Method:** `POST`
*   **URL:** `{{baseUrl}}/clients`
*   **Authorization:** Bearer Token (Admin).
*   **Body** (Raw JSON):
    ```json
    {
      "name": "Acme Corp",
      "user_id": "paste_user_uuid_here",
      "status": "active"
    }
    ```
*   **Expected:** `201 Created`.

---

## 3. Helper: Find Client ID 🛡️
If you forgot the Client ID, retrieve it using the name and linked user.

*   **Method:** `GET`
*   **URL:** `{{baseUrl}}/clients/id-by-name-and-user`
*   **Authorization:** Bearer Token (Admin).
*   **Params:**
    *   `name`: `Acme Corp`
    *   `user_id`: `paste_user_uuid_here`
*   **Expected:** `200 OK`. Copy the `id` (Client UUID).

---

## 4. Configure CPM Settings 🛡️
**Purpose:** Set the Cost Per Mille (CPM) rate used to calculate spend.

*   **Method:** `POST`
*   **URL:** `{{baseUrl}}/clients/{client_uuid}/cpm`
*   **Authorization:** Bearer Token (Admin).
*   **Body** (Raw JSON):
    ```json
    {
      "cpm": 12.50,
      "currency": "USD",
      "effective_date": "2024-01-01"
    }
    ```
*   **Expected:** `201 Created`.

---

## 5. Get All Clients 🛡️
*   **Method:** `GET`
*   **URL:** `{{baseUrl}}/clients`
*   **Authorization:** Bearer Token (Admin).
*   **Params:**
    *   `limit`: `10`
*   **Expected:** `200 OK`.

---

## 6. Get Client Details 🛡️
*   **Method:** `GET`
*   **URL:** `{{baseUrl}}/clients/{client_uuid}`
*   **Authorization:** Bearer Token.
*   **Expected:** `200 OK` (Includes `current_cpm`).

---

## 7. Update Client 🛡️
*   **Method:** `PUT`
*   **URL:** `{{baseUrl}}/clients/{client_uuid}`
*   **Authorization:** Bearer Token (Admin).
*   **Body** (Raw JSON):
    ```json
    {
      "name": "Acme Corporation Global"
    }
    ```
*   **Expected:** `200 OK`.

---

## 8. Delete Client 🛡️
*   **Method:** `DELETE`
*   **URL:** `{{baseUrl}}/clients/{client_uuid}`
*   **Authorization:** Bearer Token (Admin).
*   **Expected:** `204 No Content`

# Postman Guide: Authentication Module

**Goal:** Configure Postman to interact with the Auth API.

> [!TIP]
> **Base URL:** Set a variable `{{baseUrl}}` to `http://localhost:8000/api/v1` in Postman to save typing.

---

## 1. Login (Get Token)
**Step 1:** Create a new request.
*   **Method:** `POST`
*   **URL:** `{{baseUrl}}/auth/login`

**Step 2:** Configure **Body** tab.
*   Select **x-www-form-urlencoded** (NOT raw JSON).
*   Add Key-Value pairs:
    *   `username`: `admin@example.com`
    *   `password`: `securepassword123`

**Step 3:** Send & Save Token.
*   Click **Send**.
*   Copy the `access_token` from the response JSON.

---

## 2. Setting up Authorization (For all other requests)
For any request that requires `🔐` or `🛡️`:

**Option A (Manual Header):**
1.  Go to the **Headers** tab.
2.  Key: `Authorization`
3.  Value: `Bearer <paste_your_token_here>`

**Option B (Postman Auth Tab - Recommended):**
1.  Go to the **Authorization** tab.
2.  Type: Select **Bearer Token**.
3.  Token: Paste your `access_token`.

---

## 3. Register User (Admin Only) 🛡️
*   **Method:** `POST`
*   **URL:** `{{baseUrl}}/auth/register`
*   **Authorization:** Set Bearer Token (as above).
*   **Body** tab:
    *   Select **raw** -> **JSON**.
    *   Paste:
        ```json
        {
          "email": "client@example.com",
          "password": "clientpass123",
          "role": "client"
        }
        ```

---

## 4. Get Current User 🔐
*   **Method:** `GET`
*   **URL:** `{{baseUrl}}/auth/me`
*   **Authorization:** Set Bearer Token.
*   **Body:** None.

---

## 5. Change Password 🔐
*   **Method:** `PUT`
*   **URL:** `{{baseUrl}}/auth/change-password`
*   **Authorization:** Set Bearer Token.
*   **Body** tab (raw JSON):
    ```json
    {
      "old_password": "currentPassword",
      "new_password": "newSecurePassword!"
    }
    ```

---

## 6. User Management (Admin Only) 🛡️

### 6.1 Get All Users
*   **Method:** `GET`
*   **URL:** `{{baseUrl}}/auth/users`
*   **Authorization:** Bearer Token (Admin).

### 6.2 Get User by ID
*   **Method:** `GET`
*   **URL:** `{{baseUrl}}/auth/users/{user_id}`

### 6.3 Update User
*   **Method:** `PUT`
*   **URL:** `{{baseUrl}}/auth/users/{user_id}`
*   **Authorization:** Bearer Token (Admin).
*   **Body** (Raw JSON):
    ```json
    {
      "email": "updated@example.com",
      "role": "admin",
      "is_active": true
    }
    ```

### 6.4 Delete User
*   **Method:** `DELETE`
*   **URL:** `{{baseUrl}}/auth/users/{user_id}`
*   **Authorization:** Bearer Token (Admin).
*   **Expected:** `204 No Content`

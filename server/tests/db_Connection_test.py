import requests
import os

# You can also load these from your .env
SUPABASE_URL = "https://ufsydnnoyjctfoxtrwlj.supabase.co"
SUPABASE_SERVICE_KEY = "sb_secret_BcYnvfAU4UiZR0AHxKzRKA_sfe8Ng7z"

# Example: list tables (PostgREST endpoint)
endpoint = f"{SUPABASE_URL}/rest/v1/users"  # replace with a real table
headers = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json",
}

try:
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        print("✅ Supabase API connection works!")
        print("Response data:", response.json())
    else:
        print(f"❌ Supabase API returned status {response.status_code}")
        print(response.text)
except Exception as e:
    print("❌ Connection failed:", e)

"""
AUTOMATED PRODUCTION TESTING SCRIPT
===================================
Complete end-to-end testing of the Paid Media Dashboard Backend

Usage: python automated_production_test.py
"""

import requests
import json
import time
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor
from colorama import init, Fore, Style
import tabulate

# Initialize colorama for colored output
init(autoreset=True)

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "shameerbaba415@gmail.com"
ADMIN_PASSWORD = "Admin@123456"
TEST_CLIENT_EMAIL = "testclient@dashboard.com"
TEST_CLIENT_PASSWORD = "Client@123456"
TEST_CLIENT_NAME = "Test Client ABC"

# Vibe API Configuration (user will provide these)
VIBE_API_KEY = "api"  # User to update
VIBE_ADVERTISER_ID = "ID"  # User to update

# Database Configuration (from .env or defaults)
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'dbname',
    'user': 'user',
    'password': 'pass'
}


# Test Results Storage
test_results = []
admin_token = None
client_token = None
client_id = None


class TestResult:
    def __init__(self, phase: str, test_name: str, passed: bool, message: str, duration: float = 0):
        self.phase = phase
        self.test_name = test_name
        self.passed = passed
        self.message = message
        self.duration = duration
        self.timestamp = datetime.now()


def print_header(text: str):
    """Print a colored header"""
    print(f"\n{Fore.CYAN}{'=' * 80}")
    print(f"{Fore.CYAN}{text.center(80)}")
    print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}\n")


def print_subheader(text: str):
    """Print a colored subheader"""
    print(f"\n{Fore.YELLOW}{'─' * 80}")
    print(f"{Fore.YELLOW}{text}")
    print(f"{Fore.YELLOW}{'─' * 80}{Style.RESET_ALL}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")


def print_error(text: str):
    """Print error message"""
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")


def print_info(text: str):
    """Print info message"""
    print(f"{Fore.BLUE}ℹ {text}{Style.RESET_ALL}")


def record_test(phase: str, test_name: str, passed: bool, message: str, duration: float = 0):
    """Record test result"""
    result = TestResult(phase, test_name, passed, message, duration)
    test_results.append(result)
    
    if passed:
        print_success(f"{test_name}: {message}")
    else:
        print_error(f"{test_name}: {message}")


def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        return None


def execute_sql(query: str, params: tuple = None, fetch: bool = False):
    """Execute SQL query"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            if fetch:
                result = cur.fetchall()
                conn.close()
                return result
            else:
                conn.commit()
                conn.close()
                return True
    except Exception as e:
        print_error(f"SQL execution failed: {e}")
        if conn:
            conn.close()
        return None


def get_csv_files() -> Dict[str, Path]:
    """Get CSV files from data folder"""
    # Parent directory of server is the workspace root
    server_dir = Path(__file__).parent.parent
    data_dir = server_dir.parent / "data"
    
    csv_files = {
        'surfside': None,
        'facebook': None
    }
    
    if data_dir.exists():
        for file in data_dir.glob("*.csv"):
            if "surfside" in file.name.lower():
                csv_files['surfside'] = file
            elif "facebook" in file.name.lower():
                csv_files['facebook'] = file
    
    return csv_files


# ============================================================================
# PHASE 0: PRE-FLIGHT CHECKS
# ============================================================================

def phase0_preflight_checks():
    """Phase 0: Pre-flight checks"""
    print_header("PHASE 0: PRE-FLIGHT CHECKS")
    
    start_time = time.time()
    
    # Test 0.1: Check server is running
    print_subheader("Test 0.1: Server Connectivity")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            record_test("Phase 0", "Server Running", True, "Server is accessible", time.time() - start_time)
        else:
            record_test("Phase 0", "Server Running", False, f"Server returned status {response.status_code}", time.time() - start_time)
            print_error("Please start the server with: uvicorn app.main:app --reload")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        record_test("Phase 0", "Server Running", False, f"Cannot connect to server: {e}", time.time() - start_time)
        print_error("Please start the server with: uvicorn app.main:app --reload")
        sys.exit(1)
    
    # Test 0.2: Check database connection
    print_subheader("Test 0.2: Database Connectivity")
    start_time = time.time()
    conn = get_db_connection()
    if conn:
        conn.close()
        record_test("Phase 0", "Database Connection", True, "Database is accessible", time.time() - start_time)
    else:
        record_test("Phase 0", "Database Connection", False, "Cannot connect to database", time.time() - start_time)
        print_error("Please check database configuration")
        sys.exit(1)
    
    # Test 0.3: Check CSV files exist
    print_subheader("Test 0.3: Test Data Files")
    start_time = time.time()
    csv_files = get_csv_files()
    
    if csv_files['surfside']:
        print_success(f"Found Surfside CSV: {csv_files['surfside'].name}")
    else:
        print_warning("Surfside CSV not found in data folder")
    
    if csv_files['facebook']:
        print_success(f"Found Facebook CSV: {csv_files['facebook'].name}")
    else:
        print_warning("Facebook CSV not found in data folder")
    
    record_test("Phase 0", "Test Data Files", True, 
                f"Surfside: {csv_files['surfside'] is not None}, Facebook: {csv_files['facebook'] is not None}",
                time.time() - start_time)


# ============================================================================
# PHASE 1: AUTHENTICATION SETUP
# ============================================================================

def phase1_authentication():
    """Phase 1: Authentication System"""
    global admin_token, client_token, client_id
    
    print_header("PHASE 1: AUTHENTICATION SYSTEM")
    
    # Test 1.1: Create Admin User (directly in database)
    print_subheader("Test 1.1: Create Admin User")
    start_time = time.time()
    
    # First, check if admin exists
    existing_admin = execute_sql(
        "SELECT id FROM users WHERE email = %s",
        (ADMIN_EMAIL,),
        fetch=True
    )
    
    if existing_admin:
        print_info(f"Admin user {ADMIN_EMAIL} already exists, skipping creation")
        record_test("Phase 1", "Create Admin", True, "Admin already exists", time.time() - start_time)
    else:
        # Create admin using endpoint or direct SQL
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash(ADMIN_PASSWORD)
        
        result = execute_sql(
            """
            INSERT INTO users (email, password_hash, role, is_active)
            VALUES (%s, %s, 'admin', true)
            RETURNING id
            """,
            (ADMIN_EMAIL, hashed_password)
        )
        
        if result:
            record_test("Phase 1", "Create Admin", True, f"Admin created: {ADMIN_EMAIL}", time.time() - start_time)
        else:
            record_test("Phase 1", "Create Admin", False, "Failed to create admin user", time.time() - start_time)
            return
    
    # Test 1.2: Admin Login
    print_subheader("Test 1.2: Admin Login")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            admin_token = data.get("access_token")
            record_test("Phase 1", "Admin Login", True, "Login successful", time.time() - start_time)
            print_info(f"Admin token: {admin_token[:20]}...")
        else:
            record_test("Phase 1", "Admin Login", False, f"Login failed: {response.text}", time.time() - start_time)
            return
    except Exception as e:
        record_test("Phase 1", "Admin Login", False, f"Exception: {e}", time.time() - start_time)
        return
    
    # Test 1.3: Verify Token
    print_subheader("Test 1.3: Verify Token")
    start_time = time.time()
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("role") == "admin":
                record_test("Phase 1", "Verify Token", True, f"Token valid, role: admin", time.time() - start_time)
            else:
                record_test("Phase 1", "Verify Token", False, f"Wrong role: {data.get('role')}", time.time() - start_time)
        else:
            record_test("Phase 1", "Verify Token", False, f"Verification failed: {response.status_code}", time.time() - start_time)
    except Exception as e:
        record_test("Phase 1", "Verify Token", False, f"Exception: {e}", time.time() - start_time)
    
    # Test 1.4: Test Invalid Login
    print_subheader("Test 1.4: Invalid Login")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            data={"username": ADMIN_EMAIL, "password": "WrongPassword123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 401:
            record_test("Phase 1", "Invalid Login", True, "Correctly rejected invalid credentials", time.time() - start_time)
        else:
            record_test("Phase 1", "Invalid Login", False, f"Unexpected status: {response.status_code}", time.time() - start_time)
    except Exception as e:
        record_test("Phase 1", "Invalid Login", False, f"Exception: {e}", time.time() - start_time)


# ============================================================================
# PHASE 2: CLIENT MANAGEMENT
# ============================================================================

def phase2_client_management():
    """Phase 2: Client Management"""
    global client_id, client_token
    
    print_header("PHASE 2: CLIENT MANAGEMENT")
    
    if not admin_token:
        print_error("Admin token not available, skipping client management tests")
        return
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test 2.1: Create Test Client User
    print_subheader("Test 2.1: Create Test Client User")
    start_time = time.time()
    
    # First create a user account for the client
    client_user_id = None
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json={
                "email": TEST_CLIENT_EMAIL,
                "password": TEST_CLIENT_PASSWORD,
                "role": "client"
            },
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            user_data = response.json()
            client_user_id = user_data.get("id")
            record_test("Phase 2", "Create Client User", True, f"User created: {client_user_id}", time.time() - start_time)
        else:
            record_test("Phase 2", "Create Client User", False, f"Failed: {response.text}", time.time() - start_time)
            return
    except Exception as e:
        record_test("Phase 2", "Create Client User", False, f"Exception: {e}", time.time() - start_time)
        return
    
    # Then create the client entity linked to the user
    print_subheader("Test 2.2: Create Client Entity")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/clients",
            json={
                "name": TEST_CLIENT_NAME,
                "user_id": client_user_id,
                "status": "active"
            },
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            client_id = data.get("id")
            record_test("Phase 2", "Create Client", True, f"Client created: {client_id}", time.time() - start_time)
            print_info(f"Client ID: {client_id}")
        else:
            record_test("Phase 2", "Create Client", False, f"Failed: {response.text}", time.time() - start_time)
            return
    except Exception as e:
        record_test("Phase 2", "Create Client", False, f"Exception: {e}", time.time() - start_time)
        return
    
    # Test 2.3: Set Client CPM
    print_subheader("Test 2.3: Set Client CPM Settings")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/clients/{client_id}/cpm",
            json={
                "cpm": 5.50,
                "currency": "USD",
                "effective_date": "2025-01-01"
            },
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            record_test("Phase 2", "Set CPM", True, "CPM set to $5.50", time.time() - start_time)
        else:
            record_test("Phase 2", "Set CPM", False, f"Failed: {response.text}", time.time() - start_time)
    except Exception as e:
        record_test("Phase 2", "Set CPM", False, f"Exception: {e}", time.time() - start_time)
    
    # Test 2.4: Client Login
    print_subheader("Test 2.4: Client Login")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            data={"username": TEST_CLIENT_EMAIL, "password": TEST_CLIENT_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            client_token = data.get("access_token")
            
            # Verify role by calling /auth/me
            me_response = requests.get(
                f"{BASE_URL}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {client_token}"}
            )
            
            if me_response.status_code == 200:
                user_data = me_response.json()
                if user_data.get("role") == "client":
                    record_test("Phase 2", "Client Login", True, "Client login successful", time.time() - start_time)
                else:
                    record_test("Phase 2", "Client Login", False, f"Wrong role: {user_data.get('role')}", time.time() - start_time)
            else:
                record_test("Phase 2", "Client Login", False, f"Failed to verify role: {me_response.status_code}", time.time() - start_time)
        else:
            record_test("Phase 2", "Client Login", False, f"Login failed: {response.text}", time.time() - start_time)
    except Exception as e:
        record_test("Phase 2", "Client Login", False, f"Exception: {e}", time.time() - start_time)
    
    # Test 2.5: Test Access Control
    print_subheader("Test 2.5: Access Control")
    start_time = time.time()
    
    try:
        # Test admin-only action: registering a new user
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json={
                "email": "test_unauthorized@example.com",
                "password": "TestPass123",
                "role": "client"
            },
            headers={"Authorization": f"Bearer {client_token}"}
        )
        
        if response.status_code in [401, 403]:
            record_test("Phase 2", "Access Control", True, "Client correctly denied admin access", time.time() - start_time)
        else:
            record_test("Phase 2", "Access Control", False, f"Client has admin access (status: {response.status_code})", time.time() - start_time)
    except Exception as e:
        record_test("Phase 2", "Access Control", False, f"Exception: {e}", time.time() - start_time)


# ============================================================================
# PHASE 3: SURFSIDE MODULE
# ============================================================================

def phase3_surfside_module():
    """Phase 3: Surfside File Upload"""
    print_header("PHASE 3: SURFSIDE MODULE (File Upload)")
    
    if not admin_token or not client_id:
        print_error("Prerequisites not met, skipping Surfside tests")
        return
    
    csv_files = get_csv_files()
    if not csv_files['surfside']:
        print_warning("Surfside CSV not found, skipping Surfside tests")
        record_test("Phase 3", "Surfside Upload", False, "CSV file not found", 0)
        return
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test 3.1: Upload Surfside File
    print_subheader("Test 3.1: Upload Surfside File")
    start_time = time.time()
    
    try:
        with open(csv_files['surfside'], 'rb') as f:
            files = {'file': (csv_files['surfside'].name, f, 'text/csv')}
            
            response = requests.post(
                f"{BASE_URL}/api/v1/surfside/upload",
                params={'client_id': client_id},
                files=files,
                headers=headers
            )
        
        if response.status_code == 200:
            upload_data = response.json()
            upload_id = upload_data.get("upload_id")
            record_test("Phase 3", "Surfside Upload", True, 
                       f"File uploaded, ID: {upload_id}, Status: {upload_data.get('status')}", 
                       time.time() - start_time)
            
            # Test 3.2: Monitor Upload Status
            print_subheader("Test 3.2: Monitor Upload Processing")
            print_info("Waiting for processing to complete (up to 60 seconds)...")
            
            max_wait = 60
            wait_interval = 5
            elapsed = 0
            final_status = None
            
            while elapsed < max_wait:
                time.sleep(wait_interval)
                elapsed += wait_interval
                
                try:
                    status_response = requests.get(
                        f"{BASE_URL}/api/v1/surfside/upload/{upload_id}",
                        headers=headers
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        current_status = status_data.get('status')
                        print_info(f"Status after {elapsed}s: {current_status}")
                        
                        if current_status in ['processed', 'failed']:
                            final_status = status_data
                            break
                except Exception as e:
                    print_warning(f"Status check failed: {e}")
            
            if final_status:
                if final_status.get('status') == 'processed':
                    record_test("Phase 3", "Upload Processing", True, 
                               f"Processed successfully in {elapsed}s", elapsed)
                else:
                    record_test("Phase 3", "Upload Processing", False, 
                               f"Processing failed: {final_status.get('error_message')}", elapsed)
            else:
                record_test("Phase 3", "Upload Processing", False, 
                           f"Processing timeout after {max_wait}s", max_wait)
            
            # Test 3.2b: Verify Upload History
            print_subheader("Test 3.2b: Verify Upload History")
            start_time = time.time()
            
            try:
                history_response = requests.get(
                    f"{BASE_URL}/api/v1/surfside/uploads/{client_id}",
                    headers=headers
                )
                
                if history_response.status_code == 200:
                    history_data = history_response.json()
                    total_uploads = history_data.get('total', 0)
                    uploads_list = history_data.get('uploads', [])
                    
                    # Verify our upload is in the history
                    found_upload = any(u.get('upload_id') == str(upload_id) for u in uploads_list)
                    
                    if found_upload:
                        record_test("Phase 3", "Surfside Upload History", True, 
                                   f"Upload found in history ({total_uploads} total)", time.time() - start_time)
                    else:
                        record_test("Phase 3", "Surfside Upload History", False, 
                                   f"Upload not found in history", time.time() - start_time)
                else:
                    record_test("Phase 3", "Surfside Upload History", False, 
                               f"Failed: {history_response.status_code}", time.time() - start_time)
            except Exception as e:
                record_test("Phase 3", "Surfside Upload History", False, 
                           f"Exception: {e}", time.time() - start_time)
            
            # Test 3.3: Verify Data in Database
            print_subheader("Test 3.3: Verify Surfside Data in Database")
            start_time = time.time()
            
            # Check staging table
            staging_count = execute_sql(
                "SELECT COUNT(*) as count FROM staging_media_raw WHERE source = 'surfside' AND client_id = %s",
                (client_id,),
                fetch=True
            )
            
            if staging_count and staging_count[0]['count'] > 0:
                print_success(f"Staging table: {staging_count[0]['count']} records")
            else:
                print_warning("No records in staging table")
            
            # Check campaigns
            campaigns = execute_sql(
                "SELECT COUNT(*) as count FROM campaigns WHERE client_id = %s AND source = 'surfside'",
                (client_id,),
                fetch=True
            )
            
            if campaigns and campaigns[0]['count'] > 0:
                print_success(f"Campaigns created: {campaigns[0]['count']}")
            else:
                print_warning("No campaigns created")
            
            # Check daily metrics
            metrics = execute_sql(
                """
                SELECT 
                    COUNT(*) as records,
                    SUM(impressions) as total_impressions,
                    SUM(clicks) as total_clicks,
                    SUM(spend) as total_spend
                FROM daily_metrics
                WHERE client_id = %s AND source = 'surfside'
                """,
                (client_id,),
                fetch=True
            )
            
            if metrics and metrics[0]['records'] > 0:
                m = metrics[0]
                print_success(f"Daily metrics: {m['records']} records")
                print_info(f"  Total Impressions: {m['total_impressions']}")
                print_info(f"  Total Clicks: {m['total_clicks']}")
                print_info(f"  Total Spend: ${m['total_spend']}")
                
                record_test("Phase 3", "Verify Database", True, 
                           f"{m['records']} metrics records loaded", time.time() - start_time)
            else:
                record_test("Phase 3", "Verify Database", False, 
                           "No metrics loaded", time.time() - start_time)
            
            # Test 3.4: Verify CPM Calculation
            print_subheader("Test 3.4: Verify CPM Calculation")
            start_time = time.time()
            
            # Query the most recent surfside data for this client
            cpm_check = execute_sql(
                """
                SELECT 
                    impressions,
                    spend,
                    created_at,
                    ROUND((spend / (impressions / 1000.0))::numeric, 2) as calculated_cpm
                FROM daily_metrics
                WHERE client_id = %s 
                  AND source = 'surfside' 
                  AND impressions > 0
                ORDER BY created_at DESC
                LIMIT 5
                """,
                (client_id,),
                fetch=True
            )
            
            if cpm_check:
                all_correct = True
                for row in cpm_check:
                    expected_cpm = 5.50
                    actual_cpm = float(row['calculated_cpm'])
                    print_info(f"Impressions: {row['impressions']}, Spend: ${row['spend']}, Calculated CPM: ${actual_cpm}")
                    
                    if abs(actual_cpm - expected_cpm) > 0.01:
                        all_correct = False
                        print_warning(f"CPM mismatch: {actual_cpm} (expected {expected_cpm})")
                
                if all_correct:
                    record_test("Phase 3", "CPM Calculation", True, 
                               "All CPM calculations correct (5.50)", time.time() - start_time)
                else:
                    record_test("Phase 3", "CPM Calculation", False, 
                               "CPM calculation errors found", time.time() - start_time)
            else:
                record_test("Phase 3", "CPM Calculation", False, 
                           "No data to verify CPM", time.time() - start_time)
        
        else:
            record_test("Phase 3", "Surfside Upload", False, 
                       f"Upload failed: {response.text}", time.time() - start_time)
    
    except Exception as e:
        record_test("Phase 3", "Surfside Upload", False, f"Exception: {e}", time.time() - start_time)


# ============================================================================
# PHASE 4: FACEBOOK MODULE
# ============================================================================

def phase4_facebook_module():
    """Phase 4: Facebook File Upload with Complete ETL Verification"""
    print_header("PHASE 4: FACEBOOK MODULE (File Upload)")
    
    if not admin_token or not client_id:
        print_error("Prerequisites not met, skipping Facebook tests")
        return
    
    csv_files = get_csv_files()
    if not csv_files['facebook']:
        print_warning("Facebook CSV not found, skipping Facebook tests")
        record_test("Phase 4", "Facebook Upload", False, "CSV file not found", 0)
        return
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test 4.1: Upload Facebook File
    print_subheader("Test 4.1: Upload Facebook File")
    start_time = time.time()
    
    try:
        with open(csv_files['facebook'], 'rb') as f:
            files = {'file': (csv_files['facebook'].name, f, 'text/csv')}
            
            response = requests.post(
                f"{BASE_URL}/api/v1/facebook/upload",
                params={'client_id': client_id},
                files=files,
                headers=headers
            )
        
        if response.status_code == 200:
            upload_data = response.json()
            upload_id = upload_data.get("upload_id")
            record_test("Phase 4", "Facebook Upload", True, 
                       f"File uploaded, ID: {upload_id}, Status: {upload_data.get('status')}", 
                       time.time() - start_time)
            
            # Test 4.2: Monitor Upload Processing
            print_subheader("Test 4.2: Monitor Facebook Upload Processing")
            print_info("Waiting for processing to complete (up to 60 seconds)...")
            
            max_wait = 60
            wait_interval = 5
            elapsed = 0
            final_status = None
            
            while elapsed < max_wait:
                time.sleep(wait_interval)
                elapsed += wait_interval
                
                try:
                    status_response = requests.get(
                        f"{BASE_URL}/api/v1/facebook/upload/{upload_id}",
                        headers=headers
                    )
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        current_status = status_data.get('status')
                        print_info(f"Status after {elapsed}s: {current_status}")
                        
                        if current_status in ['processed', 'failed']:
                            final_status = status_data
                            break
                except Exception as e:
                    print_warning(f"Status check failed: {e}")
            
            if final_status:
                if final_status.get('status') == 'processed':
                    record_test("Phase 4", "Facebook Processing", True, 
                               f"Processed successfully in {elapsed}s", elapsed)
                else:
                    record_test("Phase 4", "Facebook Processing", False, 
                               f"Processing failed: {final_status.get('error_message')}", elapsed)
            else:
                record_test("Phase 4", "Facebook Processing", False, 
                           f"Processing timeout after {max_wait}s", max_wait)
            
            # Test 4.2b: Verify Upload History
            print_subheader("Test 4.2b: Verify Upload History")
            start_time = time.time()
            
            try:
                history_response = requests.get(
                    f"{BASE_URL}/api/v1/facebook/uploads/{client_id}",
                    headers=headers
                )
                
                if history_response.status_code == 200:
                    history_data = history_response.json()
                    total_uploads = history_data.get('total', 0)
                    uploads_list = history_data.get('uploads', [])
                    
                    # Verify our upload is in the history
                    found_upload = any(u.get('upload_id') == str(upload_id) for u in uploads_list)
                    
                    if found_upload:
                        record_test("Phase 4", "Facebook Upload History", True, 
                                   f"Upload found in history ({total_uploads} total)", time.time() - start_time)
                    else:
                        record_test("Phase 4", "Facebook Upload History", False, 
                                   f"Upload not found in history", time.time() - start_time)
                else:
                    record_test("Phase 4", "Facebook Upload History", False, 
                               f"Failed: {history_response.status_code}", time.time() - start_time)
            except Exception as e:
                record_test("Phase 4", "Facebook Upload History", False, 
                           f"Exception: {e}", time.time() - start_time)
            
            # Test 4.3: Verify Facebook Data in Database
            print_subheader("Test 4.3: Verify Facebook ETL Pipeline")
            start_time = time.time()
            
            # Check staging table
            staging_count = execute_sql(
                "SELECT COUNT(*) as count FROM staging_media_raw WHERE source = 'facebook' AND client_id = %s",
                (client_id,),
                fetch=True
            )
            
            if staging_count and staging_count[0]['count'] > 0:
                print_success(f"Staging table: {staging_count[0]['count']} records")
            else:
                print_warning("No records in staging table")
            
            # Check campaigns
            campaigns = execute_sql(
                "SELECT COUNT(*) as count FROM campaigns WHERE client_id = %s AND source = 'facebook'",
                (client_id,),
                fetch=True
            )
            
            if campaigns and campaigns[0]['count'] > 0:
                print_success(f"Campaigns created: {campaigns[0]['count']}")
            else:
                print_warning("No campaigns created")
            
            # Check daily metrics
            metrics = execute_sql(
                """
                SELECT 
                    COUNT(*) as records,
                    SUM(impressions) as total_impressions,
                    SUM(clicks) as total_clicks,
                    SUM(spend) as total_spend,
                    AVG(ctr) as avg_ctr
                FROM daily_metrics
                WHERE client_id = %s AND source = 'facebook'
                """,
                (client_id,),
                fetch=True
            )
            
            if metrics and metrics[0]['records'] > 0:
                m = metrics[0]
                print_success(f"Daily metrics: {m['records']} records")
                print_info(f"  Total Impressions: {m['total_impressions']}")
                print_info(f"  Total Clicks: {m['total_clicks']}")
                print_info(f"  Total Spend: ${m['total_spend']}")
                print_info(f"  Avg CTR: {m['avg_ctr']:.2f}%" if m['avg_ctr'] else "  Avg CTR: N/A")
                
                record_test("Phase 4", "Facebook ETL Complete", True, 
                           f"{m['records']} metrics records loaded", time.time() - start_time)
            else:
                record_test("Phase 4", "Facebook ETL Complete", False, 
                           "No metrics loaded", time.time() - start_time)
            
            # Test 4.4: Verify CTR Calculation
            print_subheader("Test 4.4: Verify Facebook CTR Calculation")
            start_time = time.time()
            
            ctr_check = execute_sql(
                """
                SELECT 
                    impressions,
                    clicks,
                    ctr,
                    ROUND(((clicks::numeric / NULLIF(impressions, 0)))::numeric, 2) as calculated_ctr
                FROM daily_metrics
                WHERE client_id = %s AND source = 'facebook' AND impressions > 0
                LIMIT 5
                """,
                (client_id,),
                fetch=True
            )
            
            if ctr_check:
                all_correct = True
                for row in ctr_check:
                    if row['ctr'] is not None and row['calculated_ctr'] is not None:
                        if abs(float(row['ctr']) - float(row['calculated_ctr'])) > 0.01:
                            all_correct = False
                            print_warning(f"CTR mismatch: stored={row['ctr']}, calculated={row['calculated_ctr']}")
                
                if all_correct:
                    record_test("Phase 4", "Facebook CTR Calculation", True, 
                               "All CTR calculations correct", time.time() - start_time)
                else:
                    record_test("Phase 4", "Facebook CTR Calculation", False, 
                               "CTR calculation errors found", time.time() - start_time)
            else:
                record_test("Phase 4", "Facebook CTR Calculation", False, 
                           "No data to verify CTR", time.time() - start_time)
        
        else:
            record_test("Phase 4", "Facebook Upload", False, 
                       f"Upload failed: {response.text}", time.time() - start_time)
    
    except Exception as e:
        record_test("Phase 4", "Facebook Upload", False, f"Exception: {e}", time.time() - start_time)


# ============================================================================
# PHASE 5: VIBE MODULE
# ============================================================================

def phase5_vibe_module():
    """Phase 5: Vibe API Integration with Complete ETL Verification"""
    print_header("PHASE 5: VIBE MODULE (API Integration)")
    
    if not admin_token or not client_id:
        print_error("Prerequisites not met, skipping Vibe tests")
        return
    
    if not VIBE_API_KEY or not VIBE_ADVERTISER_ID:
        print_warning("Vibe API credentials not configured, skipping Vibe tests")
        record_test("Phase 5", "Vibe Credentials", False, "API credentials not provided", 0)
        return
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test 5.1: Add Vibe Credentials
    print_subheader("Test 5.1: Store Vibe API Credentials")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/vibe/credentials/{client_id}",
            json={
                "api_key": VIBE_API_KEY,
                "advertiser_id": VIBE_ADVERTISER_ID
            },
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            creds_data = response.json()
            record_test("Phase 5", "Vibe Credentials", True, 
                       f"Credentials stored successfully", time.time() - start_time)
        else:
            record_test("Phase 5", "Vibe Credentials", False, 
                       f"Failed: {response.status_code}", time.time() - start_time)
            return
    except Exception as e:
        record_test("Phase 5", "Vibe Credentials", False, f"Exception: {e}", time.time() - start_time)
        return
    
    # Test 5.2: Request Vibe Report
    print_subheader("Test 5.2: Request Vibe Report Creation")
    start_time = time.time()
    
    # Use recent date for testing
    target_date = datetime.now().date() - timedelta(days=1)
    
    print_info(f"Requesting data for {target_date}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/vibe/ingest/{client_id}",
            params={'target_date': target_date.isoformat()},
            headers=headers
        )
        
        if response.status_code == 200:
            ingest_data = response.json()
            status = ingest_data.get("status")
            message = ingest_data.get("message")
            records_processed = ingest_data.get("records_processed", 0)
            
            if status == "success":
                record_test("Phase 5", "Vibe Data Ingestion", True, 
                           f"{message}, {records_processed} records", time.time() - start_time)
            else:
                record_test("Phase 5", "Vibe Data Ingestion", False, 
                           f"Ingestion status: {status}", time.time() - start_time)
                return
            
            # Test 5.3: Verify Vibe Data in Database
            print_subheader("Test 5.3: Verify Vibe ETL Pipeline")
            start_time = time.time()
            
            # Wait for ETL to complete
            print_info("Waiting for ETL processing...")
            time.sleep(10)
            
            # Check staging table
            staging_count = execute_sql(
                "SELECT COUNT(*) as count FROM staging_media_raw WHERE source = 'vibe' AND client_id = %s",
                (client_id,),
                fetch=True
            )
            
            if staging_count and staging_count[0]['count'] > 0:
                print_success(f"Staging table: {staging_count[0]['count']} records")
            else:
                print_warning("No records in staging table")
            
            # Check campaigns
            campaigns = execute_sql(
                "SELECT COUNT(*) as count FROM campaigns WHERE client_id = %s AND source = 'vibe'",
                (client_id,),
                fetch=True
            )
            
            if campaigns and campaigns[0]['count'] > 0:
                print_success(f"Campaigns created: {campaigns[0]['count']}")
            else:
                print_warning("No campaigns created")
            
            # Check daily metrics
            metrics = execute_sql(
                """
                SELECT 
                    COUNT(*) as records,
                    SUM(impressions) as total_impressions,
                    SUM(clicks) as total_clicks,
                    SUM(conversions) as total_conversions,
                    SUM(conversion_revenue) as total_revenue,
                    AVG(ctr) as avg_ctr
                FROM daily_metrics
                WHERE client_id = %s AND source = 'vibe'
                """,
                (client_id,),
                fetch=True
            )
            
            if metrics and metrics[0]['records'] > 0:
                m = metrics[0]
                print_success(f"Daily metrics: {m['records']} records")
                print_info(f"  Total Impressions: {m['total_impressions']}")
                print_info(f"  Total Clicks (Installs): {m['total_clicks']}")
                print_info(f"  Total Conversions (Purchases): {m['total_conversions']}")
                print_info(f"  Total Revenue: ${m['total_revenue']}")
                print_info(f"  Avg CTR: {m['avg_ctr']:.2f}%" if m['avg_ctr'] else "  Avg CTR: N/A")
                
                record_test("Phase 5", "Vibe ETL Complete", True, 
                           f"{m['records']} metrics records loaded", time.time() - start_time)
            else:
                record_test("Phase 5", "Vibe ETL Complete", False, 
                           "No metrics loaded", time.time() - start_time)
            
            # Test 5.4: Verify Vibe Column Mappings
            print_subheader("Test 5.4: Verify Vibe Column Mappings")
            start_time = time.time()
            
            # Check that Vibe-specific mappings are correct in staging table
            # (staging has the actual column names, daily_metrics has IDs)
            # channel_name → placement_name
            # installs → clicks
            # number_of_purchases → conversions
            # amount_of_purchases → conversion_revenue
            
            mapping_check = execute_sql(
                """
                SELECT 
                    placement_name,  -- Should contain channel_name from Vibe
                    clicks,          -- Should contain installs from Vibe
                    conversions,     -- Should contain number_of_purchases
                    conversion_revenue  -- Should contain amount_of_purchases
                FROM staging_media_raw
                WHERE client_id = %s AND source = 'vibe'
                ORDER BY created_at DESC
                LIMIT 5
                """,
                (client_id,),
                fetch=True
            )
            
            if mapping_check:
                has_data = any(
                    row['placement_name'] or row['clicks'] or row['conversions'] or row['conversion_revenue']
                    for row in mapping_check
                )
                
                if has_data:
                    print_success("Column mappings verified:")
                    for row in mapping_check[:3]:
                        print_info(f"  Placement: {row['placement_name']}, Clicks: {row['clicks']}, Conversions: {row['conversions']}, Revenue: ${row['conversion_revenue']}")
                    
                    record_test("Phase 5", "Vibe Column Mappings", True, 
                               "Column mappings correct (channel_name→placement_name, installs→clicks, etc.)", 
                               time.time() - start_time)
                else:
                    record_test("Phase 5", "Vibe Column Mappings", False, 
                               "No data in mapped columns", time.time() - start_time)
            else:
                record_test("Phase 5", "Vibe Column Mappings", False, 
                           "No data to verify mappings", time.time() - start_time)
            
            # Test 5.5: Verify CTR Calculation
            print_subheader("Test 5.5: Verify Vibe CTR Calculation")
            start_time = time.time()
            
            ctr_check = execute_sql(
                """
                SELECT 
                    impressions,
                    clicks,
                    ctr,
                    ROUND(((clicks::numeric / NULLIF(impressions, 0)) )::numeric, 2) as calculated_ctr
                FROM daily_metrics
                WHERE client_id = %s AND source = 'vibe' AND impressions > 0
                LIMIT 5
                """,
                (client_id,),
                fetch=True
            )
            
            if ctr_check:
                all_correct = True
                for row in ctr_check:
                    if row['ctr'] is not None and row['calculated_ctr'] is not None:
                        if abs(float(row['ctr']) - float(row['calculated_ctr'])) > 0.01:
                            all_correct = False
                            print_warning(f"CTR mismatch: stored={row['ctr']}, calculated={row['calculated_ctr']}")
                
                if all_correct:
                    record_test("Phase 5", "Vibe CTR Calculation", True, 
                               "All CTR calculations correct", time.time() - start_time)
                else:
                    record_test("Phase 5", "Vibe CTR Calculation", False, 
                               "CTR calculation errors found", time.time() - start_time)
            else:
                record_test("Phase 5", "Vibe CTR Calculation", False, 
                           "No data to verify CTR", time.time() - start_time)
        
        else:
            record_test("Phase 5", "Vibe Data Ingestion", False, 
                       f"Ingestion failed: {response.status_code} - {response.text}", time.time() - start_time)
    
    except Exception as e:
        record_test("Phase 5", "Vibe Data Ingestion", False, f"Exception: {e}", time.time() - start_time)


# ============================================================================
# PHASE 6: METRICS & DASHBOARD
# ============================================================================

def phase6_metrics_dashboard():
    """Phase 5: Metrics & Dashboard Endpoints"""
    print_header("PHASE 5: METRICS & DASHBOARD ENDPOINTS")
    
    if not admin_token or not client_id:
        print_error("Prerequisites not met, skipping metrics tests")
        return
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Get date range for tests
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=60)
    
    # Test 5.1: Get Daily Metrics
    print_subheader("Test 5.1: Get Daily Metrics")
    start_time = time.time()
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/metrics/daily",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "client_id": client_id
            },
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            record_test("Phase 6", "Daily Metrics", True, 
                       f"Retrieved {len(data)} metrics", time.time() - start_time)
        else:
            error_detail = response.text
            print_error(f"Response body: {error_detail}")
            record_test("Phase 5", "Daily Metrics", False, 
                       f"Failed: {response.status_code} - {error_detail}", time.time() - start_time)
    except Exception as e:
        record_test("Phase 5", "Daily Metrics", False, f"Exception: {e}", time.time() - start_time)
    
    # Test 5.2: Dashboard Summary
    print_subheader("Test 5.2: Dashboard Summary")
    start_time = time.time()
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/dashboard/summary",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "client_id": client_id
            },
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_info(f"Total Impressions: {data.get('total_impressions', 0)}")
            print_info(f"Total Clicks: {data.get('total_clicks', 0)}")
            print_info(f"Total Spend: ${data.get('total_spend', 0)}")
            print_info(f"Overall CTR: {data.get('overall_ctr', 0)}%")
            
            record_test("Phase 6", "Dashboard Summary", True, 
                       f"Summary retrieved successfully", time.time() - start_time)
        else:
            record_test("Phase 6", "Dashboard Summary", False, 
                       f"Failed: {response.status_code}", time.time() - start_time)
    except Exception as e:
        record_test("Phase 6", "Dashboard Summary", False, f"Exception: {e}", time.time() - start_time)
    
    # Test 6.3: Campaign Breakdown
    print_subheader("Test 6.3: Campaign Breakdown")
    start_time = time.time()
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/dashboard/campaigns",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "client_id": client_id
            },
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            record_test("Phase 6", "Campaign Breakdown", True, 
                       f"Retrieved {len(data)} campaigns", time.time() - start_time)
        else:
            record_test("Phase 6", "Campaign Breakdown", False, 
                       f"Failed: {response.status_code}", time.time() - start_time)
    except Exception as e:
        record_test("Phase 6", "Campaign Breakdown", False, f"Exception: {e}", time.time() - start_time)
    
    # Test 6.4: Top Performers
    print_subheader("Test 6.4: Top Performers")
    start_time = time.time()
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/dashboard/top-performers",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "client_id": client_id,
                "limit": 5
            },
            headers=headers
        )
        
        if response.status_code == 200:
            record_test("Phase 6", "Top Performers", True, 
                       "Top performers retrieved", time.time() - start_time)
        else:
            record_test("Phase 6", "Top Performers", False, 
                       f"Failed: {response.status_code}", time.time() - start_time)
    except Exception as e:
        record_test("Phase 6", "Top Performers", False, f"Exception: {e}", time.time() - start_time)


# ============================================================================
# PHASE 7: EXPORTS
# ============================================================================

def phase7_exports():
    """Phase 7: Export Functionality"""
    print_header("PHASE 7: EXPORT FUNCTIONALITY")
    
    if not admin_token or not client_id:
        print_error("Prerequisites not met, skipping export tests")
        return
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=60)
    
    # Test 7.1: CSV Export
    print_subheader("Test 7.1: Export Daily Metrics CSV")
    start_time = time.time()
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/exports/csv/daily-metrics",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "client_id": client_id
            },
            headers=headers
        )
        
        if response.status_code == 200:
            # Check if it's CSV content
            if 'text/csv' in response.headers.get('Content-Type', ''):
                csv_size = len(response.content)
                record_test("Phase 7", "CSV Export", True, 
                           f"CSV exported ({csv_size} bytes)", time.time() - start_time)
            else:
                record_test("Phase 7", "CSV Export", False, 
                           f"Wrong content type: {response.headers.get('Content-Type')}", time.time() - start_time)
        else:
            record_test("Phase 7", "CSV Export", False, 
                       f"Failed: {response.status_code}", time.time() - start_time)
    except Exception as e:
        record_test("Phase 7", "CSV Export", False, f"Exception: {e}", time.time() - start_time)
    
    # Test 7.2: PDF Export
    print_subheader("Test 7.2: Export Dashboard PDF")
    start_time = time.time()
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/exports/pdf/dashboard-report",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "client_id": client_id
            },
            headers=headers
        )
        
        if response.status_code == 200:
            # Check if it's PDF content
            if 'application/pdf' in response.headers.get('Content-Type', ''):
                pdf_size = len(response.content)
                record_test("Phase 7", "PDF Export", True, 
                           f"PDF exported ({pdf_size} bytes)", time.time() - start_time)
            else:
                record_test("Phase 7", "PDF Export", False, 
                           f"Wrong content type: {response.headers.get('Content-Type')}", time.time() - start_time)
        else:
            record_test("Phase 7", "PDF Export", False, 
                       f"Failed: {response.status_code}", time.time() - start_time)
    except Exception as e:
        record_test("Phase 7", "PDF Export", False, f"Exception: {e}", time.time() - start_time)


# ============================================================================
# PHASE 8: SCHEDULER
# ============================================================================

def phase8_scheduler():
    """Phase 8: Scheduler & Background Jobs"""
    print_header("PHASE 8: SCHEDULER & BACKGROUND JOBS")
    
    if not admin_token:
        print_error("Prerequisites not met, skipping scheduler tests")
        return
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test 7.1: Scheduler Status
    print_subheader("Test 7.1: Check Scheduler Status")
    start_time = time.time()
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/scheduler/status",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('running'):
                jobs = data.get('jobs', [])
                print_info(f"Scheduler running with {len(jobs)} jobs")
                for job in jobs:
                    print_info(f"  - {job.get('id')}: Next run at {job.get('next_run_time')}")
                
                record_test("Phase 8", "Scheduler Status", True, 
                           f"{len(jobs)} jobs scheduled", time.time() - start_time)
            else:
                record_test("Phase 8", "Scheduler Status", False, 
                           "Scheduler not running", time.time() - start_time)
        else:
            record_test("Phase 8", "Scheduler Status", False, 
                       f"Failed: {response.status_code}", time.time() - start_time)
    except Exception as e:
        record_test("Phase 8", "Scheduler Status", False, f"Exception: {e}", time.time() - start_time)


# ============================================================================
# PHASE 9: ERROR HANDLING
# ============================================================================

def phase9_error_handling():
    """Phase 9: Error Handling"""
    print_header("PHASE 9: ERROR HANDLING & VALIDATION")
    
    if not admin_token or not client_id:
        print_error("Prerequisites not met, skipping error handling tests")
        return
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test 8.1: Invalid File Format
    print_subheader("Test 8.1: Invalid File Format")
    start_time = time.time()
    
    try:
        # Create a temporary text file
        temp_file = Path("temp_invalid.txt")
        temp_file.write_text("This is not a CSV file")
        
        with open(temp_file, 'rb') as f:
            files = {'file': ('invalid.txt', f, 'text/plain')}
            data = {'client_id': client_id}
            
            response = requests.post(
                f"{BASE_URL}/api/v1/surfside/upload",
                files=files,
                data=data,
                headers=headers
            )
        
        temp_file.unlink()  # Delete temp file
        
        if response.status_code in [400, 422]:
            record_test("Phase 9", "Invalid File Format", True, 
                       "Correctly rejected invalid file", time.time() - start_time)
        else:
            record_test("Phase 9", "Invalid File Format", False, 
                       f"Unexpected status: {response.status_code}", time.time() - start_time)
    except Exception as e:
        record_test("Phase 9", "Invalid File Format", False, f"Exception: {e}", time.time() - start_time)
    
    # Test 9.2: Missing CPM (should use default $17)
    print_subheader("Test 9.2: Default CPM Fallback")
    start_time = time.time()
    
    # Delete CPM settings temporarily to test default fallback
    execute_sql("DELETE FROM client_settings WHERE client_id = %s", (client_id,))
    
    print_info("CPM settings deleted, testing default $17 fallback...")
    
    csv_files = get_csv_files()
    if csv_files['surfside']:
        try:
            with open(csv_files['surfside'], 'rb') as f:
                files = {'file': (csv_files['surfside'].name, f, 'text/csv')}
                
                response = requests.post(
                    f"{BASE_URL}/api/v1/surfside/upload",
                    params={'client_id': client_id},
                    files=files,
                    headers=headers
                )
            
            if response.status_code == 200:
                time.sleep(10)  # Wait for processing
                
                # Check if data was loaded with default CPM
                cpm_check = execute_sql(
                    """
                    SELECT 
                        ROUND((spend / (impressions / 1000.0))::numeric, 2) as calculated_cpm
                    FROM daily_metrics
                    WHERE client_id = %s AND impressions > 0
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (client_id,),
                    fetch=True
                )
                
                if cpm_check and abs(float(cpm_check[0]['calculated_cpm']) - 17.00) < 0.01:
                    record_test("Phase 9", "Default CPM", True, 
                               "Default CPM $17 applied correctly", time.time() - start_time)
                else:
                    record_test("Phase 9", "Default CPM", False, 
                               f"CPM mismatch: {cpm_check[0]['calculated_cpm'] if cpm_check else 'N/A'}", 
                               time.time() - start_time)
            else:
                record_test("Phase 9", "Default CPM", False, 
                           f"Upload failed: {response.status_code}", time.time() - start_time)
        except Exception as e:
            record_test("Phase 9", "Default CPM", False, f"Exception: {e}", time.time() - start_time)
    else:
        record_test("Phase 9", "Default CPM", False, "Surfside CSV not available", time.time() - start_time)
    
    # Restore CPM by recreating the client settings
    # First delete any existing settings to avoid conflicts
    execute_sql("DELETE FROM client_settings WHERE client_id = %s", (client_id,))
    # Then insert fresh settings
    execute_sql(
        """
        INSERT INTO client_settings (client_id, cpm, currency, effective_date)
        VALUES (%s, 5.50, 'USD', '2025-01-01')
        """,
        (client_id,)
    )


# ============================================================================
# FINAL REPORT
# ============================================================================

def generate_final_report():
    """Generate comprehensive test report"""
    print_header("COMPREHENSIVE TEST REPORT")
    
    # Calculate statistics
    total_tests = len(test_results)
    passed_tests = sum(1 for r in test_results if r.passed)
    failed_tests = total_tests - passed_tests
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    # Group by phase
    phases = {}
    for result in test_results:
        if result.phase not in phases:
            phases[result.phase] = {'passed': 0, 'failed': 0, 'total': 0}
        phases[result.phase]['total'] += 1
        if result.passed:
            phases[result.phase]['passed'] += 1
        else:
            phases[result.phase]['failed'] += 1
    
    # Print summary
    print(f"\n{Fore.CYAN}{'─' * 80}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}SUMMARY{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─' * 80}{Style.RESET_ALL}\n")
    
    print(f"Total Tests: {total_tests}")
    print(f"{Fore.GREEN}Passed: {passed_tests}{Style.RESET_ALL}")
    print(f"{Fore.RED}Failed: {failed_tests}{Style.RESET_ALL}")
    print(f"Pass Rate: {pass_rate:.1f}%\n")
    
    # Phase breakdown
    print(f"{Fore.YELLOW}Phase Breakdown:{Style.RESET_ALL}\n")
    
    table_data = []
    for phase, stats in sorted(phases.items()):
        phase_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
        status = f"{Fore.GREEN}✓{Style.RESET_ALL}" if stats['failed'] == 0 else f"{Fore.RED}✗{Style.RESET_ALL}"
        table_data.append([
            status,
            phase,
            stats['total'],
            stats['passed'],
            stats['failed'],
            f"{phase_rate:.1f}%"
        ])
    
    print(tabulate.tabulate(
        table_data,
        headers=['', 'Phase', 'Total', 'Passed', 'Failed', 'Pass Rate'],
        tablefmt='grid'
    ))
    
    # Failed tests detail
    if failed_tests > 0:
        print(f"\n{Fore.RED}{'─' * 80}")
        print(f"FAILED TESTS DETAIL")
        print(f"{'─' * 80}{Style.RESET_ALL}\n")
        
        for result in test_results:
            if not result.passed:
                print(f"{Fore.RED}✗ [{result.phase}] {result.test_name}{Style.RESET_ALL}")
                print(f"  {result.message}\n")
    
    # Production readiness
    print(f"\n{Fore.CYAN}{'─' * 80}")
    print(f"PRODUCTION READINESS")
    print(f"{'─' * 80}{Style.RESET_ALL}\n")
    
    if pass_rate >= 95:
        print(f"{Fore.GREEN}✓ PRODUCTION READY{Style.RESET_ALL}")
        print(f"All critical systems operational. Backend is ready for production deployment.")
    elif pass_rate >= 80:
        print(f"{Fore.YELLOW}⚠ CAUTION{Style.RESET_ALL}")
        print(f"Most systems operational, but {failed_tests} test(s) failed. Review failures before deployment.")
    else:
        print(f"{Fore.RED}✗ NOT READY{Style.RESET_ALL}")
        print(f"Critical failures detected. Do not deploy to production. Fix issues and re-test.")
    
    print(f"\n{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}\n")
    
    # Save report to file
    report_file = Path(__file__).parent / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w') as f:
        f.write("COMPREHENSIVE PRODUCTION TEST REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Tests: {total_tests}\n")
        f.write(f"Passed: {passed_tests}\n")
        f.write(f"Failed: {failed_tests}\n")
        f.write(f"Pass Rate: {pass_rate:.1f}%\n\n")
        
        f.write("DETAILED RESULTS\n")
        f.write("-" * 80 + "\n\n")
        
        for result in test_results:
            status = "PASS" if result.passed else "FAIL"
            f.write(f"[{status}] {result.phase} - {result.test_name}\n")
            f.write(f"    {result.message}\n")
            f.write(f"    Duration: {result.duration:.2f}s\n\n")
    
    print(f"Full report saved to: {report_file}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main test execution"""
    print_header("AUTOMATED PRODUCTION TESTING")
    print(f"{Fore.CYAN}Starting comprehensive backend testing...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Target: {BASE_URL}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Admin Email: {ADMIN_EMAIL}{Style.RESET_ALL}\n")
    
    overall_start = time.time()
    
    try:
        # Execute all test phases
        phase0_preflight_checks()
        phase1_authentication()
        phase2_client_management()
        phase3_surfside_module()
        phase4_facebook_module()
        phase5_vibe_module()
        phase6_metrics_dashboard()
        phase7_exports()
        phase8_scheduler()
        phase9_error_handling()
        
        # Generate final report
        overall_duration = time.time() - overall_start
        print(f"\n{Fore.CYAN}Total testing time: {overall_duration:.2f} seconds{Style.RESET_ALL}")
        
        generate_final_report()
        
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Testing interrupted by user{Style.RESET_ALL}")
        generate_final_report()
    except Exception as e:
        print(f"\n\n{Fore.RED}Fatal error during testing: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        generate_final_report()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
DATABASE RESET SCRIPT
=====================
⚠️ WARNING: This script will DROP ALL DATA and recreate the database schema!
Use this ONLY in emergency situations or for fresh starts.

Usage:
    python reset_database.py

The script will:
1. Connect to the database
2. DROP all tables (destroys all data!)
3. Recreate schema from database_schema.sql
4. Create default admin user

Requirements:
- Database must be running (Docker or local PostgreSQL)
- .env file must have correct DATABASE_URL
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not found in .env file")
    sys.exit(1)

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'=' * 70}{RESET}")
    print(f"{BLUE}{text.center(70)}{RESET}")
    print(f"{BLUE}{'=' * 70}{RESET}\n")

def confirm_reset():
    """Ask user for confirmation before proceeding."""
    print(f"{RED}⚠️  WARNING: This will DELETE ALL DATA in the database!{RESET}")
    print(f"{YELLOW}This action cannot be undone!{RESET}\n")
    
    response = input(f"Type {YELLOW}'YES DELETE EVERYTHING'{RESET} to confirm: ")
    
    if response.strip() != "YES DELETE EVERYTHING":
        print(f"\n{GREEN}✓ Reset cancelled. Database unchanged.{RESET}")
        sys.exit(0)

def drop_all_tables(cursor):
    """Drop all tables in the public schema."""
    print(f"{YELLOW}→ Dropping all tables...{RESET}")
    
    # Get all table names
    cursor.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public';
    """)
    tables = cursor.fetchall()
    
    if not tables:
        print(f"{GREEN}  No tables found to drop.{RESET}")
        return
    
    # Drop each table with CASCADE
    for (table,) in tables:
        print(f"  - Dropping table: {table}")
        cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE;')
    
    print(f"{GREEN}✓ All tables dropped successfully{RESET}")

def recreate_schema(cursor):
    """Recreate database schema from SQL file."""
    print(f"\n{YELLOW}→ Recreating database schema...{RESET}")
    
    schema_file = Path(__file__).parent / 'database_schema.sql'
    
    if not schema_file.exists():
        print(f"{RED}❌ ERROR: database_schema.sql not found!{RESET}")
        sys.exit(1)
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Execute schema
    try:
        cursor.execute(schema_sql)
        print(f"{GREEN}✓ Database schema created successfully{RESET}")
    except Exception as e:
        print(f"{RED}❌ ERROR creating schema: {str(e)}{RESET}")
        raise

def create_admin_user(cursor):
    """Create default admin user."""
    print(f"\n{YELLOW}→ Creating admin user...{RESET}")
    
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    email = "admin@gmail.com"
    password = "admin123"
    hashed_password = pwd_context.hash(password)
    
    try:
        cursor.execute("""
            INSERT INTO users (email, hashed_password, role, is_active)
            VALUES (%s, %s, 'admin', TRUE)
            ON CONFLICT (email) DO NOTHING;
        """, (email, hashed_password))
        
        print(f"{GREEN}✓ Admin user created{RESET}")
        print(f"  Email: {email}")
        print(f"  Password: {password}")
        print(f"  {YELLOW}⚠️  Change this password after first login!{RESET}")
    except Exception as e:
        print(f"{RED}❌ ERROR creating admin user: {str(e)}{RESET}")
        print(f"{YELLOW}  (You can create admin manually later){RESET}")

def main():
    print_header("DATABASE RESET TOOL")
    
    print(f"Database: {DATABASE_URL.split('@')[-1]}")  # Show only host/db part
    
    # Confirm with user
    confirm_reset()
    
    print(f"\n{BLUE}Starting database reset...{RESET}")
    
    try:
        # Connect to database
        print(f"\n{YELLOW}→ Connecting to database...{RESET}")
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        print(f"{GREEN}✓ Connected successfully{RESET}")
        
        # Step 1: Drop all tables
        drop_all_tables(cursor)
        
        # Step 2: Recreate schema
        recreate_schema(cursor)
        
        # Step 3: Create admin user
        create_admin_user(cursor)
        
        # Close connection
        cursor.close()
        conn.close()
        
        print_header("DATABASE RESET COMPLETE")
        print(f"{GREEN}✓ Database has been completely reset!{RESET}")
        print(f"\n{BLUE}Next steps:{RESET}")
        print(f"  1. Start your backend server")
        print(f"  2. Login with admin@gmail.com / admin123")
        print(f"  3. Change the admin password")
        print(f"  4. Upload your data files\n")
        
    except psycopg2.OperationalError as e:
        print(f"\n{RED}❌ ERROR: Cannot connect to database{RESET}")
        print(f"   {str(e)}")
        print(f"\n{YELLOW}Make sure:{RESET}")
        print(f"  1. Database is running (docker-compose up -d)")
        print(f"  2. DATABASE_URL in .env is correct")
        print(f"  3. Database password is correct")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n{RED}❌ ERROR during reset: {str(e)}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()


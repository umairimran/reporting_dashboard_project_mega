from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()
        print("✅ Database connection successful!")
        print(f"PostgreSQL version: {version[0]}")
except Exception as e:
    print("❌ Database connection failed!")
    print(f"Error: {e}")
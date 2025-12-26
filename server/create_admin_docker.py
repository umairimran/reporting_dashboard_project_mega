"""
Create admin user for Docker deployment.
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import bcrypt

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres123@db:5432/reporting_dashboard")

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # Admin credentials
    admin_email = "admin@gmail.com"
    admin_password = "admin123"
    
    # Check if admin already exists
    result = db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": admin_email})
    existing_admin = result.fetchone()
    
    if existing_admin:
        print(f"Ok Admin user '{admin_email}' already exists")
    else:
        # Hash password
        hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create admin user
        db.execute(text("""
            INSERT INTO users (email, hashed_password, role, is_active)
            VALUES (:email, :password, 'admin', true)
        """), {
            "email": admin_email,
            "password": hashed_password
        })
        
        db.commit()
        print(f"OK Admin user created successfully!")
        print(f"  Email: {admin_email}")
        print(f"  Password: {admin_password}")
    
    db.close()
    
except Exception as e:
    print(f"✗ Error creating admin user: {str(e)}")
    sys.exit(1)



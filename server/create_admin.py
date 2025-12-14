# create_admin.py
import asyncio
import getpass

from app.auth.security import hash_password as get_password_hash
from app.core.database import SessionLocal
from app.auth.models import User
# Import all models to ensure relationships are resolved
from app.clients.models import Client, ClientSettings
from app.campaigns.models import Campaign, Strategy, Placement, Creative
from app.metrics.models import DailyMetrics, WeeklySummary, MonthlySummary, StagingMediaRaw, IngestionLog, AuditLog
from app.vibe.models import VibeCredentials, VibeReportRequest
from app.facebook.models import UploadedFile


async def create_admin_user():
    """Create an admin user from terminal input."""
    db = SessionLocal()

    try:
        # Get input from terminal
        email = input("Enter admin email: ").strip()

        password = getpass.getpass("Enter password: ")
        confirm_password = getpass.getpass("Confirm password: ")

        if password != confirm_password:
            print("✗ Passwords do not match!")
            return

        if not password:
            print("✗ Password cannot be empty!")
            return

        # Check if admin already exists
        admin = db.query(User).filter(User.email == email).first()
        if admin:
            print("✗ User with this email already exists!")
            return

        # Create new admin user
        admin_user = User(
            email=email,
            password_hash=get_password_hash(password),
            role="admin",
            is_active=True
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("\n✓ Admin user created successfully!")
        print(f"  Email: {admin_user.email}")
        print(f"  Role: {admin_user.role}")
        print(f"  ID: {admin_user.id}")
        
        # Expunge the object so closing doesn't trigger rollback
        db.expunge(admin_user)

    except Exception as e:
        print(f"✗ Error creating admin user: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(create_admin_user())
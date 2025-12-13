#!/usr/bin/env python3
"""
Reset admin user password for Archivia
Run with: python reset_admin.py
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, create_tables
from app.services.auth import AuthService
from app.schemas.user import UserCreate


def reset_admin():
    """Reset or create admin user with default password"""

    print("=" * 50)
    print("Archivia - Reset/Create Admin User")
    print("=" * 50)
    print()

    # Default credentials
    username = "admin"
    password = "archivia123"

    # Create tables if they don't exist
    print("Ensuring database tables exist...")
    create_tables()

    db = SessionLocal()
    try:
        auth_service = AuthService()

        # Check if user exists
        existing_user = auth_service.get_user_by_username(db, username)
        if existing_user:
            print(f"User '{username}' already exists. Resetting password...")
            # Delete and recreate
            db.delete(existing_user)
            db.commit()
            print(f"✓ Existing user '{username}' deleted")

        # Create new user
        user_data = UserCreate(username=username, password=password)
        user = auth_service.create_user(db, user_data)

        print()
        print("✅ Admin user created/reset successfully!")
        print(f"   Username: {user.username}")
        print(f"   Password: {password}")
        print(f"   User ID: {user.id}")
        print()
        print("You can now login at: http://localhost:3000")
        print()

    except Exception as e:
        print(f"❌ Error creating user: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    reset_admin()

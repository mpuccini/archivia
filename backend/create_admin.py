#!/usr/bin/env python3
"""
Create initial admin user for Archivia
Run with: python create_admin.py
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, create_tables
from app.services.auth import AuthService
from app.schemas.user import UserCreate
import getpass


def create_admin_user():
    """Create an admin user interactively"""

    print("=" * 50)
    print("Archivia - Create Admin User")
    print("=" * 50)
    print()

    # Create tables if they don't exist
    print("Ensuring database tables exist...")
    create_tables()

    # Get username
    username = input("Enter admin username (default: admin): ").strip() or "admin"

    # Get password
    while True:
        password = getpass.getpass("Enter admin password (min 8 chars): ")
        if len(password) < 8:
            print("❌ Password must be at least 8 characters long")
            continue

        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("❌ Passwords don't match. Try again.")
            continue

        break

    # Create user
    db = SessionLocal()
    try:
        auth_service = AuthService()

        # Check if user exists
        existing_user = auth_service.get_user_by_username(db, username)
        if existing_user:
            print(f"❌ User '{username}' already exists!")

            overwrite = input("Do you want to reset this user's password? (yes/no): ").lower()
            if overwrite == 'yes':
                # Delete and recreate
                db.delete(existing_user)
                db.commit()
                print(f"✓ Existing user '{username}' deleted")
            else:
                print("Aborted.")
                return

        # Create new user
        user_data = UserCreate(username=username, password=password)
        user = auth_service.create_user(db, user_data)

        print()
        print("✅ Admin user created successfully!")
        print(f"   Username: {user.username}")
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
    create_admin_user()

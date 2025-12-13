#!/usr/bin/env python3
"""
Update admin user password for Archivia
Run with: python update_admin_password.py
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, create_tables
from app.models.user import User
from passlib.context import CryptContext


def update_admin_password():
    """Update admin user password"""

    print("=" * 50)
    print("Archivia - Update Admin Password")
    print("=" * 50)
    print()

    # Default credentials
    username = "admin"
    new_password = "archivia123"

    # Password context for hashing
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # Create tables if they don't exist
    print("Ensuring database tables exist...")
    create_tables()

    db = SessionLocal()
    try:
        # Find admin user
        user = db.query(User).filter(User.username == username).first()

        if not user:
            print(f"User '{username}' not found. Creating new user...")
            user = User(
                username=username,
                hashed_password=pwd_context.hash(new_password)
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print("✅ Admin user created successfully!")
        else:
            print(f"User '{username}' found. Updating password...")
            user.hashed_password = pwd_context.hash(new_password)
            db.commit()
            print("✅ Password updated successfully!")

        print()
        print(f"   Username: {user.username}")
        print(f"   Password: {new_password}")
        print(f"   User ID: {user.id}")
        print()
        print("You can now login at: http://localhost:3000")
        print()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    update_admin_password()

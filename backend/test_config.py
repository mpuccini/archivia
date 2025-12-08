#!/usr/bin/env python3
"""Test if configuration loads correctly"""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.core.config import settings

    print("✅ Configuration loaded successfully!")
    print()
    print("Configuration values:")
    print(f"  DATABASE_URL: {settings.DATABASE_URL[:30]}...")
    print(f"  SECRET_KEY: {settings.SECRET_KEY[:20]}...")
    print(f"  CORS_ORIGINS: {settings.CORS_ORIGINS}")
    print(f"  MINIO_ENDPOINT: {settings.MINIO_ENDPOINT}")
    print(f"  MINIO_ACCESS_KEY: {settings.MINIO_ACCESS_KEY}")
    print(f"  MINIO_BUCKET_NAME: {settings.MINIO_BUCKET_NAME}")
    print(f"  MINIO_SECURE: {settings.MINIO_SECURE}")
    print()
    print("All settings loaded correctly! ✨")

except Exception as e:
    print(f"❌ Configuration error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

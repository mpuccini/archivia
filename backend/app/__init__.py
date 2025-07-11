"""
Archivia - Modular File Archiving API

This package provides a modular FastAPI application for file archiving with:
- Authentication and user management
- MinIO integration for object storage  
- Multipart upload support for large files
- Modular architecture for easy expansion

Package Structure:
- core/: Configuration and database setup
- models/: SQLAlchemy database models
- schemas/: Pydantic schemas for API validation
- services/: Business logic and external service integration
- routes/: FastAPI route handlers
- utils/: Utility functions and helpers
"""

__version__ = "2.0.0"
__author__ = "Archivia Team"

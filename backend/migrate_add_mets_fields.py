#!/usr/bin/env python3
"""
Migration script to add new METS fields to the documents table
Run this script to safely add the new columns to existing databases
"""

import sys
import logging
from sqlalchemy import create_engine, text, inspect
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_add_mets_fields():
    """Add new METS fields to documents table if they don't exist"""
    
    engine = create_engine(settings.DATABASE_URL)
    
    # New columns to add
    new_columns = {
        'fund_name': 'VARCHAR(255)',
        'series_name': 'VARCHAR(255)', 
        'folder_number': 'VARCHAR(100)',
        'date_from': 'VARCHAR(50)',
        'date_to': 'VARCHAR(50)',
        'period': 'VARCHAR(255)',
        'location': 'VARCHAR(255)',
        'language': 'VARCHAR(100)',
        'subjects': 'TEXT'
    }
    
    try:
        with engine.connect() as conn:
            # Check if table exists
            inspector = inspect(engine)
            if 'documents' not in inspector.get_table_names():
                logger.info("Documents table doesn't exist yet. The columns will be created when create_tables() is called.")
                return
            
            # Get existing columns
            existing_columns = [col['name'] for col in inspector.get_columns('documents')]
            logger.info(f"Existing columns in documents table: {existing_columns}")
            
            # Add missing columns
            for column_name, column_type in new_columns.items():
                if column_name not in existing_columns:
                    try:
                        sql = f"ALTER TABLE documents ADD COLUMN {column_name} {column_type}"
                        logger.info(f"Adding column: {sql}")
                        conn.execute(text(sql))
                        conn.commit()
                        logger.info(f"✓ Added column: {column_name}")
                    except Exception as e:
                        logger.error(f"✗ Failed to add column {column_name}: {e}")
                        # Continue with other columns
                else:
                    logger.info(f"✓ Column {column_name} already exists")
            
            logger.info("Migration completed successfully!")
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("Starting METS fields migration...")
    migrate_add_mets_fields()
    logger.info("Migration finished!")

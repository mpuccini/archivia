"""
MinIO object path utilities for consistent file storage

Implements content-addressable storage with category-based organization
"""


def get_minio_object_path(
    user_id: int,
    file_hash: str,
    file_category: str,
    original_filename: str
) -> str:
    """
    Generate consistent MinIO object path for all files

    Uses content-addressable storage with category folders:
    Format: {user_id}/{file_category}/{short_hash}.{ext}

    Examples:
        - 2/master/abc123def.dng
        - 2/export_high/xyz789uvw.jpg
        - 3/metadata/mets_123.xml

    Args:
        user_id: Owner user ID
        file_hash: SHA256 hash of file content (full hash, will be shortened to first 16 chars)
        file_category: Category (master, normalized, export_high, etc.)
        original_filename: Original filename (for extension extraction)

    Returns:
        String path for MinIO object storage
    """
    # Extract extension from original filename
    extension = ''
    if '.' in original_filename:
        extension = '.' + original_filename.split('.')[-1].lower()

    # Default category to 'other' if not provided
    category = file_category or 'other'

    # Use first 16 characters of hash for shorter, more readable paths
    short_hash = file_hash[:16] if len(file_hash) >= 16 else file_hash

    return f"{user_id}/{category}/{short_hash}{extension}"


def get_export_folder_name(file_category: str) -> str:
    """
    Map storage category to ECO-MiC export folder name

    Args:
        file_category: Storage category

    Returns:
        ECO-MiC standard folder name
    """
    folder_mapping = {
        'master': 'Master',
        'normalized': 'Normalized',
        'export_high': 'Export300',
        'export_low': 'Export150',
        'metadata': 'Metadata',
        'icc': 'ICC',
        'logs': 'Logs',
        'other': 'Other'
    }
    return folder_mapping.get(file_category, 'Other')

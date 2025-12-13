"""File validation utilities using magic number verification"""
import magic
import io
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException

# Allowed MIME types and their corresponding magic number prefixes
ALLOWED_MIME_TYPES = {
    'image/jpeg': [b'\xff\xd8\xff'],  # JPEG magic numbers
    'image/png': [b'\x89\x50\x4e\x47'],  # PNG magic number
    'image/tiff': [b'\x49\x49\x2a\x00', b'\x4d\x4d\x00\x2a'],  # TIFF magic numbers (little/big endian)
    'image/x-adobe-dng': [b'\x49\x49\x2a\x00', b'\x4d\x4d\x00\x2a'],  # DNG (Digital Negative) - TIFF-based
    'image/dng': [b'\x49\x49\x2a\x00', b'\x4d\x4d\x00\x2a'],  # DNG alternate MIME type
    'application/pdf': [b'\x25\x50\x44\x46'],  # PDF magic number (%PDF)
}

# Maximum allowed file sizes per type (in bytes)
MAX_FILE_SIZES = {
    'image/jpeg': 100 * 1024 * 1024,  # 100MB
    'image/png': 100 * 1024 * 1024,   # 100MB
    'image/tiff': 500 * 1024 * 1024,  # 500MB
    'image/x-adobe-dng': 80 * 1024 * 1024 * 1024,  # 80GB for DNG files
    'image/dng': 80 * 1024 * 1024 * 1024,  # 80GB for DNG files
    'application/pdf': 200 * 1024 * 1024,  # 200MB
}


async def validate_file_type_and_size(file: UploadFile, max_size: Optional[int] = None) -> Tuple[str, bool]:
    """
    Validate file type using magic numbers and check file size.

    Args:
        file: The uploaded file to validate
        max_size: Optional maximum file size in bytes (overrides type-specific limits)

    Returns:
        Tuple of (detected_mime_type, is_valid)

    Raises:
        HTTPException: If file is invalid or too large
    """
    # Read first 2048 bytes for magic number detection
    content_preview = await file.read(2048)
    await file.seek(0)  # Reset file pointer

    # Detect MIME type using magic
    mime = magic.Magic(mime=True)
    detected_mime_type = mime.from_buffer(content_preview)

    # Validate against allowed types
    if detected_mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type detected: {detected_mime_type}. Allowed types: JPEG, PNG, TIFF, DNG, PDF"
        )

    # Verify magic number matches expected patterns
    magic_valid = False
    for magic_number in ALLOWED_MIME_TYPES[detected_mime_type]:
        if content_preview.startswith(magic_number):
            magic_valid = True
            break

    if not magic_valid:
        raise HTTPException(
            status_code=400,
            detail=f"File magic number validation failed for {detected_mime_type}"
        )

    # Get file size - use file.size attribute instead of seeking
    # Note: UploadFile.seek() only takes 1 argument (position), not 2
    file_size = file.size
    await file.seek(0)  # Reset to beginning

    # Check file size
    size_limit = max_size if max_size else MAX_FILE_SIZES.get(detected_mime_type, 100 * 1024 * 1024)
    if file_size > size_limit:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size for {detected_mime_type} is {size_limit / (1024*1024):.1f}MB"
        )

    return detected_mime_type, True


def validate_filename(filename: str) -> str:
    """
    Sanitize and validate filename to prevent path traversal and other attacks.

    Args:
        filename: The original filename

    Returns:
        Sanitized filename safe for storage
    """
    import re
    import os

    # Extract just the filename (remove any path components)
    filename = os.path.basename(filename)

    # Split extension
    name, ext = os.path.splitext(filename)

    # Remove or replace dangerous characters
    # Only allow alphanumeric, hyphens, and underscores in the name
    name = re.sub(r'[^\w\-]', '_', name)

    # Ensure extension is safe (only alphanumeric and dots)
    ext = re.sub(r'[^\w\.]', '', ext.lower())

    # Remove leading/trailing dots and spaces
    name = name.strip('. ')

    # Limit length (reserve space for extension)
    max_name_length = 200
    if len(name) > max_name_length:
        name = name[:max_name_length]

    # Combine back together
    sanitized = f"{name}{ext}" if name else f"file{ext}"

    # Final safety check - ensure no path traversal
    if '..' in sanitized or '/' in sanitized or '\\' in sanitized:
        raise HTTPException(status_code=400, detail="Invalid filename")

    return sanitized

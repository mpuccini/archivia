import hashlib
from typing import BinaryIO


def calculate_file_hash(file: BinaryIO, algorithm: str = "sha256") -> str:
    """Calculate file hash"""
    hash_obj = hashlib.new(algorithm)
    
    # Reset file pointer
    file.seek(0)
    
    # Read file in chunks
    while chunk := file.read(8192):
        hash_obj.update(chunk)
    
    # Reset file pointer again
    file.seek(0)
    
    return hash_obj.hexdigest()


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def validate_filename(filename: str) -> bool:
    """Validate filename for security"""
    # Basic validation - no path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        return False
    
    # Check for empty or too long names
    if not filename or len(filename) > 255:
        return False
    
    return True

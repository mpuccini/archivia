import logging
from datetime import datetime
from typing import Any, Dict


def setup_logging():
    """Setup application logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log')
        ]
    )


def log_api_call(method: str, endpoint: str, user_id: int = None, **kwargs):
    """Log API call for monitoring"""
    logger = logging.getLogger("api_monitor")
    
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "method": method,
        "endpoint": endpoint,
        "user_id": user_id,
        **kwargs
    }
    
    logger.info(f"API Call: {log_data}")


def log_file_operation(operation: str, file_id: int, user_id: int, details: Dict[str, Any] = None):
    """Log file operations for auditing"""
    logger = logging.getLogger("file_operations")
    
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "operation": operation,
        "file_id": file_id,
        "user_id": user_id,
        "details": details or {}
    }
    
    logger.info(f"File Operation: {log_data}")

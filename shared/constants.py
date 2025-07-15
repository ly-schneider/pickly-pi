"""
Shared constants for Pickly Pi project
"""

# File extensions
SUPPORTED_RAW_EXTENSIONS = ['.CR2', '.NEF', '.ARW', '.RAF', '.ORF', '.DNG', '.RW2']
SUPPORTED_JPEG_EXTENSIONS = ['.JPG', '.JPEG']
ALL_SUPPORTED_EXTENSIONS = SUPPORTED_RAW_EXTENSIONS + SUPPORTED_JPEG_EXTENSIONS

# File size limits
MIN_PHOTO_FILE_SIZE = 1000000  # 1MB
MAX_PHOTO_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Transfer settings
DEFAULT_CHUNK_SIZE = 1048576  # 1MB
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 5  # seconds

# Phase definitions
PHASES = {
    1: "Basic file transfer system",
    2: "Core image processing pipeline", 
    3: "Web dashboard",
    4: "Advanced CV features",
    5: "Lightroom integration and notifications",
    6: "Error handling and optimization"
}

# Processing statuses
class ProcessingStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Transfer statuses  
class TransferStatus:
    WAITING = "waiting"
    TRANSFERRING = "transferring"
    VERIFYING = "verifying"
    SUCCESS = "success"
    FAILED = "failed"
    DUPLICATE = "duplicate"
    SKIPPED = "skipped"
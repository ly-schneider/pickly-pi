"""
Logging utilities for Pickly Pi Agent
"""

import logging
import logging.handlers
import os
from pathlib import Path


def setup_logging(logging_config: dict) -> logging.Logger:
    """Setup logging configuration"""
    
    # Get configuration values
    level = logging_config.get('level', 'INFO').upper()
    log_file = logging_config.get('file', '/var/log/pickly-pi/agent.log')
    max_size = logging_config.get('max_size', '10MB')
    backup_count = logging_config.get('backup_count', 5)
    
    # Convert max_size to bytes
    max_bytes = _parse_size_string(max_size)
    
    # Create log directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, level))
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        
    except (OSError, PermissionError) as e:
        # Fallback to current directory if can't write to specified location
        fallback_log = 'pickly-pi-agent.log'
        print(f"Warning: Cannot write to {log_file}: {e}")
        print(f"Falling back to {fallback_log}")
        
        file_handler = logging.handlers.RotatingFileHandler(
            fallback_log,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, level))
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    return logger


def _parse_size_string(size_str: str) -> int:
    """Parse size string like '10MB' into bytes"""
    size_str = size_str.upper().strip()
    
    multipliers = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 * 1024,
        'GB': 1024 * 1024 * 1024
    }
    
    # Extract number and unit
    for unit, multiplier in multipliers.items():
        if size_str.endswith(unit):
            try:
                number = float(size_str[:-len(unit)])
                return int(number * multiplier)
            except ValueError:
                break
    
    # Default to treating as bytes
    try:
        return int(size_str)
    except ValueError:
        return 10 * 1024 * 1024  # Default 10MB


class TransferProgressLogger:
    """Helper class for logging file transfer progress"""
    
    def __init__(self, logger: logging.Logger, total_files: int):
        self.logger = logger
        self.total_files = total_files
        self.completed_files = 0
        self.failed_files = 0
        
    def log_file_start(self, filename: str, file_size: int):
        """Log start of file transfer"""
        self.logger.info(f"Starting transfer: {filename} ({self._format_size(file_size)})")
        
    def log_file_success(self, filename: str, file_size: int, transfer_time: float):
        """Log successful file transfer"""
        self.completed_files += 1
        speed = file_size / transfer_time if transfer_time > 0 else 0
        
        self.logger.info(
            f"Transfer completed: {filename} "
            f"({self._format_size(file_size)} in {transfer_time:.1f}s, "
            f"{self._format_size(speed)}/s) "
            f"[{self.completed_files}/{self.total_files}]"
        )
        
    def log_file_failure(self, filename: str, error: str):
        """Log failed file transfer"""
        self.failed_files += 1
        self.logger.error(f"Transfer failed: {filename} - {error}")
        
    def log_session_complete(self):
        """Log completion of transfer session"""
        self.logger.info(
            f"Transfer session completed: "
            f"{self.completed_files} successful, "
            f"{self.failed_files} failed, "
            f"{self.total_files} total"
        )
        
    def _format_size(self, size_bytes: int) -> str:
        """Format byte size into human readable string"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
"""
Configuration management for Pickly Pi Agent
"""

import json
import os
from typing import Dict, Any, List


class ConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
            
    def get_smb_config(self) -> Dict[str, Any]:
        """Get SMB connection configuration"""
        return self.config.get('smb', {})
        
    def get_paths_config(self) -> Dict[str, str]:
        """Get path configuration"""
        return self.config.get('paths', {})
        
    def get_transfer_config(self) -> Dict[str, Any]:
        """Get file transfer configuration"""
        return self.config.get('transfer', {})
        
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration"""
        return self.config.get('monitoring', {})
        
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self.config.get('logging', {})
        
    def get_poll_interval(self) -> int:
        """Get polling interval in seconds"""
        return self.get_monitoring_config().get('poll_interval', 2)
        
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions"""
        return self.get_monitoring_config().get('supported_extensions', [])
        
    def get_min_file_size(self) -> int:
        """Get minimum file size for processing"""
        return self.get_monitoring_config().get('min_file_size', 1000000)
        
    def get_sd_mount_base(self) -> str:
        """Get SD card mount base path"""
        return self.get_paths_config().get('sd_mount_base', '/media/pi')
        
    def get_temp_dir(self) -> str:
        """Get temporary directory for processing"""
        return self.get_paths_config().get('temp_dir', '/tmp/pickly-transfer')
        
    def get_remote_base_path(self) -> str:
        """Get remote base path on SMB share"""
        return self.get_paths_config().get('remote_base_path', '/incoming')
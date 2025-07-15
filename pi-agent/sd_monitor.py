"""
SD Card monitoring and file detection
"""

import os
import time
from pathlib import Path
from typing import List, Set
import psutil
import logging


class SDCardMonitor:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.processed_cards = set()  # Track already processed cards
        
    def scan_for_cards(self) -> List[str]:
        """Scan for newly inserted SD cards"""
        current_cards = self._get_mounted_cards()
        new_cards = []
        
        for card in current_cards:
            if card not in self.processed_cards:
                # Verify it's actually an SD card with photos
                if self._is_photo_card(card):
                    new_cards.append(card)
                    self.processed_cards.add(card)
                    
        # Clean up processed cards that are no longer mounted
        self._cleanup_processed_cards(current_cards)
        
        return new_cards
        
    def _get_mounted_cards(self) -> Set[str]:
        """Get list of currently mounted removable devices"""
        cards = set()
        mount_base = self.config.get_sd_mount_base()
        
        try:
            # Check for mounted devices under the mount base
            if os.path.exists(mount_base):
                for item in os.listdir(mount_base):
                    mount_point = os.path.join(mount_base, item)
                    if os.path.ismount(mount_point):
                        cards.add(mount_point)
                        
            # Also check using psutil for all mounted devices
            for partition in psutil.disk_partitions():
                if self._is_removable_device(partition):
                    cards.add(partition.mountpoint)
                    
        except Exception as e:
            self.logger.error(f"Error scanning for mounted cards: {e}")
            
        return cards
        
    def _is_removable_device(self, partition) -> bool:
        """Check if a partition is a removable device (likely SD card)"""
        # Check mount options for removable devices
        if 'removable' in partition.opts:
            return True
            
        # Check device path patterns typical for SD cards
        device_patterns = ['/dev/sd', '/dev/mmcblk']
        for pattern in device_patterns:
            if partition.device.startswith(pattern):
                return True
                
        return False
        
    def _is_photo_card(self, mount_point: str) -> bool:
        """Check if the mounted device contains photo files"""
        try:
            # Look for common camera folder structures
            dcim_path = os.path.join(mount_point, 'DCIM')
            if os.path.exists(dcim_path):
                return self._has_photo_files(dcim_path)
                
            # Also check root directory
            return self._has_photo_files(mount_point)
            
        except Exception as e:
            self.logger.error(f"Error checking if {mount_point} is photo card: {e}")
            return False
            
    def _has_photo_files(self, directory: str) -> bool:
        """Check if directory contains photo files"""
        supported_extensions = [ext.lower() for ext in self.config.get_supported_extensions()]
        min_file_size = self.config.get_min_file_size()
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    if file_ext in supported_extensions:
                        try:
                            if os.path.getsize(file_path) >= min_file_size:
                                return True
                        except OSError:
                            continue
                            
        except Exception as e:
            self.logger.error(f"Error scanning directory {directory}: {e}")
            
        return False
        
    def scan_photos(self, card_path: str) -> List[str]:
        """Scan SD card for photo files"""
        photo_files = []
        supported_extensions = [ext.lower() for ext in self.config.get_supported_extensions()]
        min_file_size = self.config.get_min_file_size()
        
        self.logger.info(f"Scanning for photos in {card_path}")
        
        try:
            # Check DCIM folder first (standard camera structure)
            dcim_path = os.path.join(card_path, 'DCIM')
            if os.path.exists(dcim_path):
                photo_files.extend(self._scan_directory(dcim_path, supported_extensions, min_file_size))
                
            # Also scan root directory
            photo_files.extend(self._scan_directory(card_path, supported_extensions, min_file_size))
            
            # Remove duplicates
            photo_files = list(set(photo_files))
            
        except Exception as e:
            self.logger.error(f"Error scanning photos in {card_path}: {e}")
            
        return photo_files
        
    def _scan_directory(self, directory: str, supported_extensions: List[str], min_file_size: int) -> List[str]:
        """Scan a specific directory for photo files"""
        files = []
        
        try:
            for root, dirs, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    file_ext = os.path.splitext(filename)[1].lower()
                    
                    if file_ext in supported_extensions:
                        try:
                            if os.path.getsize(file_path) >= min_file_size:
                                files.append(file_path)
                        except OSError as e:
                            self.logger.warning(f"Cannot access file {file_path}: {e}")
                            
        except Exception as e:
            self.logger.error(f"Error scanning directory {directory}: {e}")
            
        return files
        
    def _cleanup_processed_cards(self, current_cards: Set[str]):
        """Remove unmounted cards from processed set"""
        self.processed_cards = self.processed_cards.intersection(current_cards)
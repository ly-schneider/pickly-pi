"""
File transfer management via SMB
"""

import os
import hashlib
import time
import uuid
import datetime
from pathlib import Path
from typing import List, Dict, Optional
import logging

from smbprotocol.connection import Connection
from smbprotocol.session import Session
from smbprotocol.tree import TreeConnect
from smbprotocol.file import File, CreateDisposition, CreateOptions, FileAttributes
from smbprotocol.open import Open


class FileTransferManager:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.smb_config = config.get_smb_config()
        self.transfer_config = config.get_transfer_config()
        
        # Connection objects
        self.connection = None
        self.session = None
        self.tree = None
        
    def transfer_files(self, file_paths: List[str], source_card: str) -> int:
        """Transfer files to SMB share"""
        success_count = 0
        
        try:
            self._connect_smb()
            
            # Create session directory based on timestamp
            session_dir = self._create_session_directory(source_card)
            
            for file_path in file_paths:
                try:
                    if self._transfer_single_file(file_path, session_dir):
                        success_count += 1
                        self.logger.info(f"Successfully transferred: {file_path}")
                    else:
                        self.logger.error(f"Failed to transfer: {file_path}")
                        
                except Exception as e:
                    self.logger.error(f"Error transferring {file_path}: {e}")
                    
        except Exception as e:
            self.logger.error(f"SMB connection error: {e}")
        finally:
            self._disconnect_smb()
            
        return success_count
        
    def _connect_smb(self):
        """Establish SMB connection"""
        try:
            server = self.smb_config.get('server')
            port = self.smb_config.get('port', 445)
            username = self.smb_config.get('username')
            password = self.smb_config.get('password')
            domain = self.smb_config.get('domain', '')
            share = self.smb_config.get('share')
            
            self.logger.info(f"Connecting to SMB server {server}:{port}")
            
            # Create connection
            self.connection = Connection(uuid.uuid4(), server, port)
            self.connection.connect()
            
            # Create session
            self.session = Session(self.connection, username, password, domain)
            self.session.connect()
            
            # Connect to tree (share)
            self.tree = TreeConnect(self.session, f"\\\\{server}\\{share}")
            self.tree.connect()
            
            self.logger.info("SMB connection established")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to SMB: {e}")
            raise
            
    def _disconnect_smb(self):
        """Close SMB connection"""
        try:
            if self.tree:
                self.tree.disconnect()
            if self.session:
                self.session.disconnect()
            if self.connection:
                self.connection.disconnect()
                
            self.logger.info("SMB connection closed")
            
        except Exception as e:
            self.logger.error(f"Error disconnecting SMB: {e}")
            
    def _create_session_directory(self, source_card: str) -> str:
        """Create a unique directory for this transfer session"""
        # Extract card identifier (last part of path)
        card_name = os.path.basename(source_card.rstrip('/'))
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = f"{timestamp}_{card_name}"
        
        remote_base = self.config.get_remote_base_path().strip('/')
        remote_session_path = f"{remote_base}/{session_dir}"
        
        try:
            self._create_remote_directory(remote_session_path)
            self.logger.info(f"Created session directory: {remote_session_path}")
            return remote_session_path
            
        except Exception as e:
            self.logger.error(f"Failed to create session directory: {e}")
            raise
            
    def _create_remote_directory(self, remote_path: str):
        """Create directory on remote SMB share"""
        try:
            # Convert to SMB path format
            smb_path = remote_path.replace('/', '\\')
            
            file_handle = File(self.tree, smb_path)
            open_info = file_handle.create(
                CreateDisposition.FILE_CREATE,
                CreateOptions.FILE_DIRECTORY_FILE,
                FileAttributes.FILE_ATTRIBUTE_DIRECTORY
            )
            file_handle.close()
            
        except Exception as e:
            # Directory might already exist
            if "object name already exists" not in str(e).lower():
                raise
                
    def _transfer_single_file(self, local_path: str, remote_session_dir: str) -> bool:
        """Transfer a single file with retry logic"""
        max_retries = self.transfer_config.get('max_retries', 3)
        retry_delay = self.transfer_config.get('retry_delay', 5)
        
        for attempt in range(max_retries):
            try:
                return self._do_file_transfer(local_path, remote_session_dir)
                
            except Exception as e:
                self.logger.warning(f"Transfer attempt {attempt + 1} failed for {local_path}: {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    self.logger.error(f"All {max_retries} transfer attempts failed for {local_path}")
                    
        return False
        
    def _do_file_transfer(self, local_path: str, remote_session_dir: str) -> bool:
        """Perform the actual file transfer"""
        filename = os.path.basename(local_path)
        remote_file_path = f"{remote_session_dir}/{filename}".replace('/', '\\')
        
        chunk_size = self.transfer_config.get('chunk_size', 1048576)
        verify_checksums = self.transfer_config.get('verify_checksums', True)
        
        try:
            # Check if file already exists and skip if duplicate
            if self._check_duplicate_file(local_path, remote_file_path):
                self.logger.info(f"File already exists (duplicate): {filename}")
                return True
                
            # Open local file
            with open(local_path, 'rb') as local_file:
                # Create remote file
                remote_file = File(self.tree, remote_file_path)
                file_handle = remote_file.create(
                    CreateDisposition.FILE_CREATE,
                    CreateOptions.FILE_NON_DIRECTORY_FILE,
                    FileAttributes.FILE_ATTRIBUTE_NORMAL
                )
                
                try:
                    # Transfer file in chunks
                    total_size = os.path.getsize(local_path)
                    transferred = 0
                    local_hash = hashlib.sha256() if verify_checksums else None
                    
                    while True:
                        chunk = local_file.read(chunk_size)
                        if not chunk:
                            break
                            
                        remote_file.write(chunk, transferred)
                        transferred += len(chunk)
                        
                        if local_hash:
                            local_hash.update(chunk)
                            
                        # Log progress for large files
                        if total_size > 10 * 1024 * 1024:  # 10MB
                            progress = (transferred / total_size) * 100
                            if transferred % (5 * 1024 * 1024) == 0:  # Every 5MB
                                self.logger.info(f"Transfer progress for {filename}: {progress:.1f}%")
                                
                    # Verify transfer if enabled
                    if verify_checksums and not self._verify_transfer(
                        local_path, remote_file_path, local_hash.hexdigest()
                    ):
                        return False
                        
                    self.logger.info(f"Transfer completed: {filename} ({transferred} bytes)")
                    return True
                    
                finally:
                    remote_file.close()
                    
        except Exception as e:
            self.logger.error(f"File transfer failed for {local_path}: {e}")
            return False
            
    def _check_duplicate_file(self, local_path: str, remote_path: str) -> bool:
        """Check if file already exists on remote share"""
        try:
            remote_file = File(self.tree, remote_path)
            
            # Try to get file info
            info = remote_file.query_info()
            if info:
                # Compare file sizes
                local_size = os.path.getsize(local_path)
                remote_size = info['end_of_file'].get_value()
                
                if local_size == remote_size:
                    self.logger.info(f"Duplicate file detected: {os.path.basename(local_path)}")
                    return True
                    
        except Exception:
            # File doesn't exist or error accessing it
            pass
            
        return False
        
    def _verify_transfer(self, local_path: str, remote_path: str, local_checksum: str) -> bool:
        """Verify transferred file integrity"""
        try:
            # Read remote file and calculate checksum
            remote_file = File(self.tree, remote_path)
            file_handle = remote_file.open()
            
            remote_hash = hashlib.sha256()
            chunk_size = self.transfer_config.get('chunk_size', 1048576)
            offset = 0
            
            try:
                while True:
                    chunk = remote_file.read(chunk_size, offset)
                    if not chunk:
                        break
                    remote_hash.update(chunk)
                    offset += len(chunk)
                    
                remote_checksum = remote_hash.hexdigest()
                
                if local_checksum == remote_checksum:
                    return True
                else:
                    self.logger.error(f"Checksum mismatch for {os.path.basename(local_path)}")
                    return False
                    
            finally:
                remote_file.close()
                
        except Exception as e:
            self.logger.error(f"Verification failed for {local_path}: {e}")
            return False
#!/usr/bin/env python3
"""
Pickly Pi - Main SD Card Monitor Service
Phase 1: Basic file transfer from Pi to server via SMB
"""

import os
import sys
import time
import signal
import logging
from pathlib import Path

from config_manager import ConfigManager
from sd_monitor import SDCardMonitor
from file_transfer import FileTransferManager
from utils.logger import setup_logging


class PicklyPiAgent:
    def __init__(self, config_path="config.json"):
        self.config = ConfigManager(config_path)
        self.logger = setup_logging(self.config.get_logging_config())
        self.running = False
        
        # Initialize components
        self.sd_monitor = SDCardMonitor(self.config)
        self.transfer_manager = FileTransferManager(self.config)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        
    def start(self):
        """Start the main monitoring loop"""
        self.logger.info("Starting Pickly Pi Agent...")
        self.running = True
        
        try:
            while self.running:
                # Check for new SD cards
                detected_cards = self.sd_monitor.scan_for_cards()
                
                for card_path in detected_cards:
                    self.logger.info(f"New SD card detected: {card_path}")
                    
                    try:
                        # Process the SD card
                        self._process_sd_card(card_path)
                    except Exception as e:
                        self.logger.error(f"Error processing SD card {card_path}: {e}")
                        
                # Wait before next scan
                time.sleep(self.config.get_poll_interval())
                
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Unexpected error in main loop: {e}")
        finally:
            self.stop()
            
    def _process_sd_card(self, card_path):
        """Process a detected SD card"""
        self.logger.info(f"Processing SD card at {card_path}")
        
        # Scan for photo files
        photo_files = self.sd_monitor.scan_photos(card_path)
        if not photo_files:
            self.logger.info(f"No photo files found on {card_path}")
            return
            
        self.logger.info(f"Found {len(photo_files)} photo files")
        
        # Transfer files to server
        success_count = self.transfer_manager.transfer_files(
            photo_files, 
            card_path
        )
        
        self.logger.info(f"Successfully transferred {success_count}/{len(photo_files)} files")
        
        # TODO: Optional SD card cleanup/formatting in later phases
        
    def stop(self):
        """Stop the agent"""
        self.running = False
        self.logger.info("Pickly Pi Agent stopped")


def main():
    """Main entry point"""
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        print("Please copy config.example.json to config.json and configure it")
        sys.exit(1)
        
    agent = PicklyPiAgent(config_path)
    agent.start()


if __name__ == "__main__":
    main()
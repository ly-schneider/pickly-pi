#!/usr/bin/env python3
"""
Configuration validation script for Pickly Pi Agent
"""

import sys
import os
from pathlib import Path

try:
    from config_manager import ConfigManager
    from smbprotocol.connection import Connection
    from smbprotocol.session import Session
    from smbprotocol.tree import TreeConnect
except ImportError as e:
    print(f"Import error: {e}")
    print("Please install requirements: pip3 install -r requirements.txt")
    sys.exit(1)


def test_config_file(config_path):
    """Test configuration file loading"""
    print(f"Testing configuration file: {config_path}")
    
    try:
        config = ConfigManager(config_path)
        print("✓ Configuration file loaded successfully")
        return config
    except Exception as e:
        print(f"✗ Configuration file error: {e}")
        return None


def test_smb_connection(config):
    """Test SMB connection"""
    print("\nTesting SMB connection...")
    
    smb_config = config.get_smb_config()
    required_fields = ['server', 'share', 'username', 'password']
    
    # Check required fields
    for field in required_fields:
        if not smb_config.get(field):
            print(f"✗ Missing required SMB field: {field}")
            return False
    
    try:
        server = smb_config['server']
        port = smb_config.get('port', 445)
        username = smb_config['username']
        password = smb_config['password']
        domain = smb_config.get('domain', '')
        share = smb_config['share']
        
        print(f"  Server: {server}:{port}")
        print(f"  Share: {share}")
        print(f"  Username: {username}")
        
        # Test connection
        connection = Connection(uuid.uuid4(), server, port)
        connection.connect()
        print("✓ Network connection established")
        
        # Test authentication
        session = Session(connection, username, password, domain)
        session.connect()
        print("✓ Authentication successful")
        
        # Test share access
        tree = TreeConnect(session, f"\\\\{server}\\{share}")
        tree.connect()
        print("✓ Share access successful")
        
        # Cleanup
        tree.disconnect()
        session.disconnect()
        connection.disconnect()
        
        print("✓ SMB connection test passed")
        return True
        
    except Exception as e:
        print(f"✗ SMB connection failed: {e}")
        return False


def test_paths(config):
    """Test path configuration"""
    print("\nTesting path configuration...")
    
    paths_config = config.get_paths_config()
    
    # Check SD mount base
    sd_mount_base = paths_config.get('sd_mount_base', '/media/pi')
    if os.path.exists(sd_mount_base):
        print(f"✓ SD mount base exists: {sd_mount_base}")
    else:
        print(f"⚠ SD mount base not found: {sd_mount_base}")
    
    # Check temp directory
    temp_dir = paths_config.get('temp_dir', '/tmp/pickly-transfer')
    try:
        Path(temp_dir).mkdir(parents=True, exist_ok=True)
        print(f"✓ Temp directory accessible: {temp_dir}")
    except Exception as e:
        print(f"✗ Temp directory error: {temp_dir} - {e}")
    
    return True


def test_monitoring_config(config):
    """Test monitoring configuration"""
    print("\nTesting monitoring configuration...")
    
    monitoring_config = config.get_monitoring_config()
    
    extensions = monitoring_config.get('supported_extensions', [])
    if extensions:
        print(f"✓ Supported extensions: {', '.join(extensions)}")
    else:
        print("⚠ No supported extensions configured")
    
    min_size = monitoring_config.get('min_file_size', 0)
    print(f"✓ Minimum file size: {min_size:,} bytes")
    
    poll_interval = monitoring_config.get('poll_interval', 2)
    print(f"✓ Poll interval: {poll_interval} seconds")
    
    return True


def main():
    """Main test function"""
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    
    print("Pickly Pi Agent Configuration Test")
    print("=" * 40)
    
    # Test configuration loading
    config = test_config_file(config_path)
    if not config:
        sys.exit(1)
    
    # Test individual components
    tests_passed = 0
    total_tests = 4
    
    if test_paths(config):
        tests_passed += 1
        
    if test_monitoring_config(config):
        tests_passed += 1
    
    # SMB test is optional since server might not be available
    print("\nTesting SMB connection (optional)...")
    smb_test = input("Test SMB connection? (y/N): ").lower().strip()
    
    if smb_test == 'y':
        if test_smb_connection(config):
            tests_passed += 1
        total_tests += 1
    
    # Summary
    print("\n" + "=" * 40)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("✓ All tests passed! Configuration is ready.")
        sys.exit(0)
    else:
        print("⚠ Some tests failed. Please review configuration.")
        sys.exit(1)


if __name__ == "__main__":
    import uuid
    main()
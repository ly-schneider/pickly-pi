# Pickly Pi Agent - Phase 1

The Raspberry Pi component of the Pickly Pi photography workflow automation system. This agent monitors for SD card insertion and automatically transfers photo files to a server via SMB.

## Features

- **Automatic SD Card Detection**: Monitors for newly inserted SD cards
- **Smart File Recognition**: Identifies photo files by extension and minimum size
- **SMB File Transfer**: Secure transfer to network storage with authentication
- **Duplicate Detection**: Avoids transferring files that already exist
- **Progress Tracking**: Detailed logging of transfer progress and errors
- **Retry Logic**: Automatic retry on transfer failures
- **Session Organization**: Creates timestamped directories for each transfer session

## Installation

### Quick Installation

```bash
# Clone the repository
git clone <repository-url>
cd pickly-pi/pi-agent

# Run installation script
sudo ./install.sh
```

### Manual Installation

```bash
# Install dependencies
pip3 install -r requirements.txt

# Copy configuration
cp config.example.json config.json

# Edit configuration (see Configuration section)
nano config.json

# Run the agent
python3 main.py
```

## Configuration

Edit `config.json` with your specific settings:

### SMB Configuration
```json
{
  "smb": {
    "server": "192.168.1.101",     // Your SMB server IP
    "share": "leys",               // SMB share name
    "username": "leys",            // SMB username
    "password": "leys",            // SMB password
    "domain": "",                  // Windows domain (optional)
    "port": 445                    // SMB port
  }
}
```

### Path Configuration
```json
{
  "paths": {
    "sd_mount_base": "/media/pi",        // Where SD cards mount
    "temp_dir": "/tmp/pickly-transfer",  // Temporary processing directory
    "remote_base_path": "/incoming"      // Base path on SMB share
  }
}
```

### File Monitoring
```json
{
  "monitoring": {
    "supported_extensions": [".CR2", ".NEF", ".ARW", ".RAF", ".ORF", ".DNG", ".JPG", ".JPEG"],
    "min_file_size": 1000000,     // Minimum file size (1MB)
    "poll_interval": 2            // Seconds between SD card scans
  }
}
```

## Usage

### As a Service (Recommended)

After installation with `sudo ./install.sh`:

```bash
# Start the service
sudo systemctl start pickly-pi-agent

# Enable auto-start on boot
sudo systemctl enable pickly-pi-agent

# Check status
sudo systemctl status pickly-pi-agent

# View logs
sudo journalctl -u pickly-pi-agent -f
```

### Manual Execution

```bash
# Run in foreground
python3 main.py

# Run with custom config
python3 main.py /path/to/config.json
```

## How It Works

1. **SD Card Detection**: Continuously monitors `/media/pi` and other mount points for new removable devices
2. **File Discovery**: Scans detected cards for photo files matching configured extensions and size requirements
3. **Session Creation**: Creates a timestamped directory on the SMB share for organization
4. **File Transfer**: Transfers files in chunks with progress tracking and checksum verification
5. **Duplicate Handling**: Skips files that already exist with matching sizes
6. **Error Recovery**: Retries failed transfers with configurable delays

## File Organization

On the SMB share, files are organized as:
```
/incoming/
  └── 20250713_143022_sdcard1/
      ├── IMG_001.CR2
      ├── IMG_002.CR2
      └── ...
```

Directory naming: `YYYYMMDD_HHMMSS_<card_identifier>`

## Logging

Logs are written to:
- **System install**: `/var/log/pickly-pi/agent.log`
- **User install**: `$HOME/.local/log/pickly-pi/agent.log`
- **Console output**: Real-time status and errors

Log rotation is automatic with configurable size limits.

## Troubleshooting

### SD Card Not Detected
- Check mount point configuration in `config.json`
- Verify SD card is properly mounted: `lsblk` or `mount`
- Check file permissions on mount directory

### SMB Connection Issues
- Test SMB connectivity: `smbclient -L //server_ip -U username`
- Verify network connectivity: `ping server_ip`
- Check firewall settings on server and Pi

### Transfer Failures
- Check SMB credentials and permissions
- Verify disk space on server
- Review logs for specific error messages

### Permission Denied
- Ensure Pi user has read access to SD card mount points
- Check SMB share permissions
- Verify log directory permissions

## Development

### Testing
```bash
# Run with debug logging
python3 main.py config.json

# Test configuration
python3 -c "from config_manager import ConfigManager; print(ConfigManager('config.json').get_smb_config())"
```

### Adding Features
The modular design allows easy extension:
- `sd_monitor.py`: SD card detection logic
- `file_transfer.py`: SMB transfer implementation
- `config_manager.py`: Configuration handling
- `utils/logger.py`: Logging utilities

## Security Considerations

- Store SMB credentials securely
- Use dedicated SMB user with minimal permissions
- Consider encrypted SMB connections
- Regular log monitoring for anomalies
- Network isolation of photography workflow systems
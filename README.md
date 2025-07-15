# Pickly Pi - Photography Workflow Automation

A comprehensive photography workflow automation system that replaces commercial tools like Narrative and Aftershoot. Automatically processes RAW photos from SD cards with intelligent analysis and culling.

## Architecture

- **Pi Agent**: Raspberry Pi service for SD card monitoring and file transfer
- **Processing Engine**: Computer vision and ML models for image analysis  
- **Web Interface**: Next.js dashboard for monitoring and manual controls
- **API Layer**: RESTful services connecting all components
- **Database**: Processing history and metadata storage
- **Telegram Bot**: Real-time notifications

## Phase 1: Basic File Transfer ✅ COMPLETED

Phase 1 implements the core file transfer system from Raspberry Pi to server via SMB.

### Setup

1. **Raspberry Pi Setup**:
   ```bash
   cd pi-agent
   sudo ./install.sh
   # Edit /opt/pickly-pi/pi-agent/config.json with your SMB settings
   sudo systemctl start pickly-pi-agent
   ```

2. **Alternative Docker Setup**:
   ```bash
   cd pi-agent
   cp config.example.json config.json
   # Edit config.json with your settings
   docker-compose up -d
   ```

3. **Server Setup**:
   - Ensure SMB share is accessible
   - Configure authentication in pi-agent config

### Features

- ✅ SD card detection on Pi
- ✅ Secure SMB file transfer with authentication
- ✅ Duplicate detection and prevention
- ✅ Progress tracking and detailed logging
- ✅ Error recovery with retry logic
- ✅ Checksum verification
- ✅ Session-based file organization
- ✅ Systemd service integration
- ✅ Docker deployment option

## Development Phases

1. **Phase 1**: Basic file transfer system ✅
2. **Phase 2**: Core image processing pipeline
3. **Phase 3**: Web dashboard
4. **Phase 4**: Advanced CV features
5. **Phase 5**: Lightroom integration and notifications
6. **Phase 6**: Error handling and optimization
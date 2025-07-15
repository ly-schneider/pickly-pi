#!/bin/bash
# Installation script for Pickly Pi Agent

set -e

echo "Installing Pickly Pi Agent..."

# Check if running as root for system installation
if [[ $EUID -eq 0 ]]; then
    INSTALL_PATH="/opt/pickly-pi"
    SERVICE_INSTALL=true
    echo "Installing system-wide to $INSTALL_PATH"
else
    INSTALL_PATH="$HOME/pickly-pi"
    SERVICE_INSTALL=false
    echo "Installing user-mode to $INSTALL_PATH"
fi

# Create installation directory
mkdir -p "$INSTALL_PATH/pi-agent"
mkdir -p "/var/log/pickly-pi" 2>/dev/null || mkdir -p "$HOME/.local/log/pickly-pi"

# Copy files
echo "Copying files..."
cp -r ./* "$INSTALL_PATH/pi-agent/"

# Install Python dependencies
echo "Installing Python dependencies..."
cd "$INSTALL_PATH/pi-agent"
pip3 install -r requirements.txt

# Setup configuration
if [ ! -f "$INSTALL_PATH/pi-agent/config.json" ]; then
    echo "Creating configuration file..."
    cp config.example.json config.json
    echo "Please edit $INSTALL_PATH/pi-agent/config.json with your settings"
fi

# Install systemd service (if root)
if [ "$SERVICE_INSTALL" = true ]; then
    echo "Installing systemd service..."
    
    # Update service file paths if needed
    sed -i "s|/opt/pickly-pi|$INSTALL_PATH|g" pickly-pi-agent.service
    
    cp pickly-pi-agent.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable pickly-pi-agent
    
    echo "Service installed. Start with: sudo systemctl start pickly-pi-agent"
    echo "Check status with: sudo systemctl status pickly-pi-agent"
    echo "View logs with: sudo journalctl -u pickly-pi-agent -f"
else
    echo "Service installation skipped (not root)"
    echo "Run manually with: cd $INSTALL_PATH/pi-agent && python3 main.py"
fi

# Set permissions
if [ "$SERVICE_INSTALL" = true ]; then
    chown -R pi:pi "$INSTALL_PATH"
    chmod +x "$INSTALL_PATH/pi-agent/main.py"
    
    # Create log directory
    mkdir -p /var/log/pickly-pi
    chown pi:pi /var/log/pickly-pi
fi

echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit configuration: $INSTALL_PATH/pi-agent/config.json"
echo "2. Test the configuration: cd $INSTALL_PATH/pi-agent && python3 main.py"
if [ "$SERVICE_INSTALL" = true ]; then
    echo "3. Start the service: sudo systemctl start pickly-pi-agent"
fi
echo ""
echo "Configuration example:"
echo "- Set your SMB server details in the 'smb' section"
echo "- Verify SD card mount path in 'paths.sd_mount_base'"
echo "- Adjust file extensions in 'monitoring.supported_extensions'"
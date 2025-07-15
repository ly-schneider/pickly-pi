FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    udev \
    util-linux \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 pickly && \
    chown -R pickly:pickly /app
USER pickly

# Create directories for logs and temp files
RUN mkdir -p /app/logs /app/temp

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose volume mount points
VOLUME ["/media", "/app/logs", "/app/config"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "from config_manager import ConfigManager; ConfigManager('/app/config/config.json')" || exit 1

# Run the application
CMD ["python3", "main.py", "/app/config/config.json"]
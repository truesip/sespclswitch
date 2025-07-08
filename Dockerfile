# Use Ubuntu as base image for better SIP support
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies including PJSIP tools, Redis, and Supervisor
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    espeak \
    espeak-data \
    ffmpeg \
    curl \
    wget \
    build-essential \
    software-properties-common \
    redis-server \
    supervisor \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install PJSIP from source for better compatibility
RUN cd /tmp && \
    wget https://github.com/pjsip/pjproject/archive/refs/tags/2.14.tar.gz && \
    tar -xzf 2.14.tar.gz && \
    cd pjproject-2.14 && \
    ./configure --prefix=/usr/local --enable-shared --disable-sound --disable-resample --disable-video --disable-opencore-amr && \
    make dep && \
    make && \
    make install && \
    # Build and install PJSUA application
    cd pjsip-apps/build && \
    make && \
    cp ../bin/pjsua-x86_64-unknown-linux-gnu /usr/local/bin/pjsua && \
    chmod +x /usr/local/bin/pjsua && \
    ldconfig && \
    cd /tmp && \
    rm -rf pjproject-2.14 2.14.tar.gz

# Install additional audio tools
RUN apt-get update && apt-get install -y \
    alsa-utils \
    pulseaudio \
    sox \
    && rm -rf /var/lib/apt/lists/*

# Configure Redis
RUN mkdir -p /var/lib/redis && chown redis:redis /var/lib/redis

# Create application directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy configuration files
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY gunicorn.conf.py /app/

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/audio_files /app/logs /tmp/audio /app/temp_audio

# Set permissions
RUN chmod +x /app/entrypoint.sh || true

# Expose ports
EXPOSE 5000 6379

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run with Supervisor to manage all processes
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

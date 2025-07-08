"""
Gunicorn configuration for Voice Call API
Optimized for high-performance telecom workloads
"""
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', 5000)}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1  # Recommended formula
worker_class = "gevent"  # Async worker for I/O intensive tasks
worker_connections = 1000  # Max concurrent connections per worker
max_requests = 10000  # Restart workers after handling this many requests
max_requests_jitter = 1000  # Randomize restart to avoid thundering herd
preload_app = True  # Load application before forking workers

# Timeouts
timeout = 120  # Worker timeout (important for long SIP calls)
keepalive = 2
graceful_timeout = 30

# Performance
worker_tmp_dir = "/dev/shm"  # Use shared memory for better performance

# Logging
loglevel = "info"
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "voice-call-api"

# SSL (if needed)
# keyfile = "path/to/keyfile"
# certfile = "path/to/certfile"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# For debugging (disable in production)
reload = os.getenv('DEBUG', 'false').lower() == 'true'

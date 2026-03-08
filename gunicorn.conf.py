# ============================================
# Gunicorn Configuration for Production
# ============================================

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5011"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "-"  # stdout
errorlog = "-"  # stderr
loglevel = os.getenv("LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "smart-pet-feeder"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment jika pakai HTTPS)
# keyfile = "/path/to/key.pem"
# certfile = "/path/to/cert.pem"

# Restart workers after this many requests (prevent memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Graceful timeout
graceful_timeout = 30


# Pre/Post fork hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("🚀 Starting Smart Pet Feeder Application")


def when_ready(server):
    """Called just after the server is started."""
    server.log.info(f"✅ Server ready. Workers: {workers}")


def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("🔄 Reloading workers...")


def worker_int(worker):
    """Called when worker receives the SIGINT or SIGQUIT signal."""
    worker.log.info(f"⚠️ Worker {worker.pid} received signal")


def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    worker.log.error(f"❌ Worker {worker.pid} aborted")

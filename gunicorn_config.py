import multiprocessing
import os

# Gunicorn config
bind = "0.0.0.0:" + os.environ.get("PORT", "10000")
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gthread"
threads = 2
worker_connections = 1000
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
graceful_timeout = 120
forwarded_allow_ips = "*"
proxy_protocol = True
proxy_allow_ips = "*"
accesslog = "-"
errorlog = "-"
loglevel = "info"
capture_output = True
enable_stdio_inheritance = True 
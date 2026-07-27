from slowapi import Limiter
from slowapi.util import get_remote_address

# Vive en su propio módulo (en vez de main.py) para que app/routers/auth.py
# pueda importarlo sin generar un import circular con app.main.
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

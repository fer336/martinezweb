FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# --proxy-headers hace que uvicorn lea X-Forwarded-For y reescriba la IP de
# cliente que ve la app; sin esto, todo el tráfico (que siempre llega vía
# Traefik, este contenedor no publica puertos directos) se ve como si viniera
# de la IP interna de Traefik y el rate limiting por IP no sirve de nada.
# forwarded-allow-ips='*' confía en cualquier upstream porque solo Traefik
# puede llegar a este contenedor por la red de Swarm — la garantía real de
# que el header no esté spoofeado depende de que Traefik esté configurado
# para sanear/reemplazar X-Forwarded-For en su entrypoint público.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]

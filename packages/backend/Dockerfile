FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    pkg-config \
    build-essential \
    libgomp1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Keep the per-deploy build SHA after the expensive OS and Python dependency
# layers so a new commit does not force those layers to rebuild.
ARG BUILD_SHA=unknown
ARG APP_VERSION=1.0.0
ENV PANACEA_BUILD_SHA=${BUILD_SHA} \
    PANACEA_VERSION=${APP_VERSION}

EXPOSE 5000

# Migrations + gunicorn are inlined here (rather than a separate entrypoint.sh)
# so the startup command lives in the image's own metadata — immune to a
# docker-compose bind mount shadowing /app with an incomplete host directory.
# Migrations create any missing tables (base schema + database/migrations).
# A failure is logged loudly but doesn't block gunicorn: a database problem
# should show up in /health/db and the logs, not take the whole API down.
ENTRYPOINT ["sh", "-c", "python -m database.migrate || echo '[migrate] FAILED - see error above; /health/db will report the database as unavailable' >&2; exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 \"app:create_app()\""]

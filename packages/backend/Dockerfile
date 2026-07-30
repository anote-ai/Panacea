FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    pkg-config \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x entrypoint.sh

EXPOSE 5000

# Invoked via `sh` rather than relying on the executable bit: docker-compose's
# local-dev bind mount (`./packages/backend:/app`) overwrites this image's
# files — and their permissions — with the host copy, so a non-executable
# host-side entrypoint.sh (e.g. checked out on a filesystem/git config that
# doesn't preserve +x) would otherwise fail with "permission denied" even
# though this RUN chmod succeeded at build time.
ENTRYPOINT ["sh", "entrypoint.sh"]

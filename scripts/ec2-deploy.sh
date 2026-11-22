#!/usr/bin/env bash
# Runs ON the EC2 host (sent by .github/workflows/deploy.yml via SSM).
#
# Inputs (environment): IMAGE_URI, ECR_REGISTRY, AWS_REGION, HEALTH_PORT.
#
# What it does, and why:
# - Recreates ONLY the backend container. The old deploy ran
#   `docker compose down` + `up`, which also recreated MySQL/Redis/Tika on
#   every deploy; a database container without a named volume comes back
#   empty that way.
# - Makes the backend run the image this deploy just pushed. The host's
#   docker-compose.yml may name a fixed tag instead of ${IMAGE_URI}; the new
#   image is tagged as whatever the compose file names, so either works.
# - Runs the new image's production config check before touching anything,
#   so an unsafe config can't replace a running backend with one that won't
#   start.
# - Runs the Coworker background worker alongside the backend (generated from
#   the backend's settings when the host compose file has no worker service).
# - Fails (with container status and backend logs) unless the backend is
#   live (/health) AND its database is usable (/health/db).
set -euo pipefail

APP_HOME=/home/ssm-user/app
SECRET_ID=panacea/prod
: "${IMAGE_URI:?IMAGE_URI is required}"
: "${ECR_REGISTRY:?ECR_REGISTRY is required}"
: "${AWS_REGION:=us-east-1}"
: "${HEALTH_PORT:=5000}"
export IMAGE_URI

cd "$APP_HOME"

echo "==> Writing .env from Secrets Manager ($SECRET_ID)"
aws secretsmanager get-secret-value --secret-id "$SECRET_ID" --region "$AWS_REGION" \
  --query SecretString --output text \
  | python3 -c 'import sys,json; [print(f"{k}={v}") for k,v in json.load(sys.stdin).items()]' > .env

echo "==> Pulling $IMAGE_URI"
aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "$ECR_REGISTRY" >/dev/null
docker pull "$IMAGE_URI"

# The backend refuses to start in production with an unsafe config (see
# packages/backend/coworker/config.py). Run that check with the NEW image
# against the real .env first: on failure, stop here and leave the running
# backend (and every tag) untouched. Messages name settings, never values.
echo "==> Checking production config with the new image"
if ! docker run --rm --env-file .env -e APP_ENV=production --entrypoint python "$IMAGE_URI" -m coworker.config; then
  echo "CONFIG_CHECK_FAILED: the new backend would refuse to start with this configuration."
  echo "Fix the settings named above in Secrets Manager ($SECRET_ID); the running backend was left as it is."
  exit 1
fi

BACKEND_IMAGE=$(docker compose config --format json 2>/dev/null \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["services"]["backend"].get("image",""))' 2>/dev/null || true)
if [[ -n "$BACKEND_IMAGE" && "$BACKEND_IMAGE" != "$IMAGE_URI" ]]; then
  echo "==> docker-compose.yml runs '$BACKEND_IMAGE' for backend; pointing it at the new build"
  docker tag "$IMAGE_URI" "$BACKEND_IMAGE"
fi

echo "==> Starting any stopped services (existing db/redis/tika containers are kept as-is)"
docker compose up -d --no-recreate

echo "==> Recreating backend only"
docker compose up -d --no-deps --force-recreate backend

dump_and_fail() {
  echo "BACKEND_UNHEALTHY: $1"
  docker compose ps
  docker compose logs --tail 80 backend
  exit 1
}

echo "==> Waiting for /health"
for _ in $(seq 1 24); do
  curl -fsS "http://localhost:$HEALTH_PORT/health" >/dev/null 2>&1 && break
  sleep 5
done
curl -fsS "http://localhost:$HEALTH_PORT/health" || dump_and_fail "/health did not respond"
echo

db_ok() {
  python3 -c 'import sys,json; sys.exit(0 if json.loads(sys.argv[1]).get("database") == "ok" else 1)' "$1" 2>/dev/null
}

echo "==> Checking /health/db"
DB_STATUS=""
for _ in $(seq 1 6); do
  DB_STATUS=$(curl -sS "http://localhost:$HEALTH_PORT/health/db" || true)
  db_ok "$DB_STATUS" && break
  sleep 5
done
echo "$DB_STATUS"
db_ok "$DB_STATUS" || dump_and_fail "database unavailable (errno 2003 = can't connect, 1045 = access denied, 1049 = unknown database, 1146 = table missing)"

# Background worker: scheduled tasks, inbox watching and other autonomous
# Coworker work run here, not in the web process. If the host's compose file
# doesn't define one, generate docker-compose.worker.yml from the backend's
# resolved settings (same image, environment and volumes; no ports) on every
# deploy, so it never drifts from the backend.
start_worker() {
  if docker compose config --services 2>/dev/null | grep -qx coworker-worker; then
    echo "==> Recreating coworker-worker (defined in docker-compose.yml)"
    docker compose up -d --no-deps --force-recreate coworker-worker
    return
  fi
  echo "==> Generating docker-compose.worker.yml from the backend's settings"
  if ! docker compose config --format json | python3 -c '
import json, sys
cfg = json.load(sys.stdin)
backend = cfg["services"]["backend"]
if not backend.get("image"):
    sys.exit("backend has no image to reuse")
keep = ("image", "environment", "env_file", "volumes", "networks", "extra_hosts", "user", "working_dir")
worker = {k: v for k, v in backend.items() if k in keep}
worker.update({
    "entrypoint": ["python", "-m", "coworker.worker", "--interval", "60"],
    "command": [],
    "restart": "unless-stopped",
    "healthcheck": {"test": ["CMD", "python", "-m", "coworker.ops", "--check"],
                    "interval": "2m", "timeout": "30s", "start_period": "5m", "retries": 2},
})
if "db" in cfg["services"]:
    worker["depends_on"] = {"db": {"condition": "service_started"}}
json.dump({"services": {"coworker-worker": worker}}, sys.stdout, indent=2)
' > docker-compose.worker.yml.new; then
    rm -f docker-compose.worker.yml.new
    echo "WORKER_NOT_STARTED: couldn't derive a worker from the backend service (see above)."
    return
  fi
  mv docker-compose.worker.yml.new docker-compose.worker.yml
  chmod 600 docker-compose.worker.yml   # holds the same settings as .env
  docker compose -f docker-compose.yml -f docker-compose.worker.yml up -d --no-deps --force-recreate coworker-worker
}
start_worker

echo "==> Waiting for the worker to report in"
WORKER=""
for _ in $(seq 1 18); do
  WORKER=$(curl -fsS "http://localhost:$HEALTH_PORT/health" 2>/dev/null \
    | python3 -c 'import sys,json; print(json.load(sys.stdin).get("worker",""))' 2>/dev/null || true)
  [[ "$WORKER" == ok ]] && break
  sleep 10
done
if [[ "$WORKER" == ok ]]; then
  echo "==> Worker OK"
else
  # Don't fail the deploy over the worker (the web app is healthy); make it loud instead.
  echo "WORKER_NOT_HEALTHY: /health reports worker=${WORKER:-unknown}. Worker logs:"
  docker logs --tail 60 "$(docker ps -aq --filter label=com.docker.compose.service=coworker-worker | head -1)" 2>&1 || true
fi

docker image prune -f >/dev/null
echo "==> Deploy OK: $(curl -fsS "http://localhost:$HEALTH_PORT/api/version")"

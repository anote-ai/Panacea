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

docker image prune -f >/dev/null
echo "==> Deploy OK: $(curl -fsS "http://localhost:$HEALTH_PORT/api/version")"

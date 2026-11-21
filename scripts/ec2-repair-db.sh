#!/usr/bin/env bash
# Runs ON the EC2 host (sent by .github/workflows/repair-db-credentials.yml).
#
# Fixes "Access denied" (MySQL errno 1045) between the backend and the
# docker-compose MySQL service: the password in panacea/prod (DB_PASSWORD)
# no longer matches what MySQL was initialized with. MySQL only reads
# MYSQL_ROOT_PASSWORD when its data directory is first created, so changing
# the secret later doesn't change the database.
#
# Steps (nothing is deleted; no password is ever printed):
# 1. If MySQL already accepts DB_USER / DB_PASSWORD from .env: nothing to fix.
# 2. Else, if the db container's own MYSQL_ROOT_PASSWORD (or, after an earlier
#    repair, root with DB_PASSWORD) still works: use it
#    to set DB_USER's password to DB_PASSWORD (creating DB_USER and granting
#    it DB_NAME if DB_USER isn't root), so panacea/prod stays the source of
#    truth. Then restart the backend and require /health/db.
# 3. Else: stop and report; no known password works.
#
# Inputs (environment): HEALTH_PORT (default 5000).
set -euo pipefail

APP_HOME=/home/ssm-user/app
: "${HEALTH_PORT:=5000}"
cd "$APP_HOME"

# Read DB settings from .env without sourcing it (values may contain shell
# metacharacters).
read_env() {
  python3 - "$1" "$2" <<'PY'
import sys
key, default = sys.argv[1], sys.argv[2]
value = default
for line in open(".env", encoding="utf-8"):
    line = line.rstrip("\n")
    if line.startswith(key + "="):
        value = line[len(key) + 1:]
print(value)
PY
}
DB_USER=$(read_env DB_USER root)
DB_NAME=$(read_env DB_NAME anote)
DB_PASSWORD=$(read_env DB_PASSWORD "")
echo "==> Backend connects as user '$DB_USER' to database '$DB_NAME'"

if ! docker compose ps --status running --services 2>/dev/null | grep -qx db; then
  echo "REPAIR_STOPPED: the compose 'db' service isn't running here, so the backend's database is"
  echo "somewhere else (check DB_HOST in panacea/prod). Nothing was changed."
  docker compose ps
  exit 1
fi

# MYSQL_PWD keeps passwords out of argv; nothing below echoes them.
secret_works() {
  docker compose exec -T -e MYSQL_PWD="$DB_PASSWORD" db mysql -u"$DB_USER" -e "SELECT 1" >/dev/null 2>&1
}
# Admin access: the db container's MYSQL_ROOT_PASSWORD, or (after an earlier
# repair aligned root to the secret) root with DB_PASSWORD.
ADMIN_MODE=""
find_admin() {
  if docker compose exec -T db sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot -e "SELECT 1"' >/dev/null 2>&1; then
    ADMIN_MODE=container; return 0
  fi
  if docker compose exec -T -e MYSQL_PWD="$DB_PASSWORD" db mysql -uroot -e "SELECT 1" >/dev/null 2>&1; then
    ADMIN_MODE=secret; return 0
  fi
  return 1
}
admin_sql() {
  if [[ "$ADMIN_MODE" == container ]]; then
    docker compose exec -T db sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot'
  else
    docker compose exec -T -e MYSQL_PWD="$DB_PASSWORD" db mysql -uroot
  fi
}

check_backend() {
  echo "==> Restarting backend and checking /health/db"
  docker compose up -d --no-deps --force-recreate backend
  for _ in $(seq 1 24); do
    curl -fsS "http://localhost:$HEALTH_PORT/health" >/dev/null 2>&1 && break
    sleep 5
  done
  status=$(curl -sS "http://localhost:$HEALTH_PORT/health/db" || true)
  echo "$status"
  if python3 -c 'import sys,json; sys.exit(0 if json.loads(sys.argv[1]).get("database") == "ok" else 1)' "$status" 2>/dev/null; then
    echo "==> REPAIRED: the backend can use its database."
  else
    echo "REPAIR_INCOMPLETE: credentials now match, but /health/db still fails (see errno above)."
    docker compose logs --tail 60 backend
    exit 1
  fi
}

if secret_works; then
  echo "==> MySQL already accepts the panacea/prod credentials for '$DB_USER'. No password change needed."
  check_backend
  exit 0
fi
echo "==> MySQL rejects the panacea/prod password for '$DB_USER'."

if ! find_admin; then
  echo "REPAIR_STOPPED: MySQL rejects root with both the db container's MYSQL_ROOT_PASSWORD and DB_PASSWORD, so no known password"
  echo "works. Nothing was changed. Options: recover the original root password, or (if the database"
  echo "holds nothing to keep) recreate the db container's data volume so it initializes with DB_PASSWORD."
  exit 1
fi
echo "==> Admin access OK (via $ADMIN_MODE root password); setting '$DB_USER' to the panacea/prod password."

# Build the SQL with values escaped for single-quoted MySQL strings and
# backtick identifiers, and feed it on stdin (never on the command line).
SQL=$(DB_USER="$DB_USER" DB_NAME="$DB_NAME" DB_PASSWORD="$DB_PASSWORD" python3 - <<'PY'
import os
def s(v): return "'" + v.replace("\\", "\\\\").replace("'", "\\'") + "'"
def ident(v): return "`" + v.replace("`", "``") + "`"
user, db, pw = os.environ["DB_USER"], os.environ["DB_NAME"], os.environ["DB_PASSWORD"]
stmts = [f"CREATE DATABASE IF NOT EXISTS {ident(db)}"]
for host in ("%", "localhost"):
    account = f"{s(user)}@{s(host)}"
    stmts.append(f"CREATE USER IF NOT EXISTS {account} IDENTIFIED BY {s(pw)}")
    stmts.append(f"ALTER USER {account} IDENTIFIED BY {s(pw)}")
    if user != "root":
        stmts.append(f"GRANT ALL PRIVILEGES ON {ident(db)}.* TO {account}")
stmts.append("FLUSH PRIVILEGES")
print(";\n".join(stmts) + ";")
PY
)
printf '%s\n' "$SQL" | admin_sql

if secret_works; then
  echo "==> MySQL now accepts the panacea/prod credentials."
else
  echo "REPAIR_INCOMPLETE: the password was updated but MySQL still rejects it."
  exit 1
fi
check_backend

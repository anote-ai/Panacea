#!/bin/sh
set -e

if [ "${SKIP_DB_MIGRATIONS:-}" != "1" ]; then
    python -m database.migrate
fi

exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 "app:create_app()"

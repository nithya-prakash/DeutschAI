#!/bin/sh
set -e

echo "Waiting for Postgres at ${POSTGRES_HOST:-postgres}:${POSTGRES_PORT:-5432}..."
until python -c "
import socket, os, sys
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(1)
try:
    s.connect((os.environ.get('POSTGRES_HOST', 'postgres'), int(os.environ.get('POSTGRES_PORT', 5432))))
except OSError:
    sys.exit(1)
"; do
  sleep 1
done
echo "Postgres is up. Running migrations..."
alembic upgrade head

echo "Starting API..."
exec "$@"

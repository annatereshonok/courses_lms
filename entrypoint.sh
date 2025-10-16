#!/usr/bin/env bash
set -e

until python - <<'PY'
import os, psycopg2, time
from psycopg2 import OperationalError
host=os.getenv("POSTGRES_HOST","db"); port=int(os.getenv("POSTGRES_PORT","5432"))
user=os.getenv("POSTGRES_USER","lms"); pwd=os.getenv("POSTGRES_PASSWORD","lms"); db=os.getenv("POSTGRES_DB","lms")
for _ in range(30):
    try:
        psycopg2.connect(host=host, port=port, user=user, password=pwd, dbname=db).close()
        break
    except OperationalError:
        time.sleep(1)
else:
    raise SystemExit("DB not ready")
PY
do
  echo "Waiting for Postgres..."
  sleep 1
done

echo "➡️  migrate"
python manage.py migrate --noinput

if [ "${SEED_DEMO}" = "1" ]; then
  echo "➡️  seed demo data"
  python manage.py add_course_data || true
fi

echo "➡️  runserver"
exec python manage.py runserver 0.0.0.0:8000
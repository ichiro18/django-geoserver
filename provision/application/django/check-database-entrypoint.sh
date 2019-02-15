#!/bin/bash
set -e

ERRORS=0

if [[ -z ${DATABASE_DB} ]]; then
    echo "ERROR: DATABASE_DB env variable is empty"
    ERRORS=$((ERRORS + 1))
fi

if [[ -z ${DATABASE_USER} ]]; then
    echo "ERROR: DATABASE_USER env variable is empty"
    ERRORS=$((ERRORS + 1))
fi

if [[ -z ${DATABASE_PASSWORD} ]]; then
    echo "ERROR: DATABASE_PASSWORD env variable is empty"
    ERRORS=$((ERRORS + 1))
fi

if [[ -z ${POSTGRES_HOST} ]]; then
    echo "ERROR: POSTGRES_HOST env variable is empty"
    ERRORS=$((ERRORS + 1))
fi

if [[ -z ${POSTGRES_PORT} ]]; then
    echo "ERROR: POSTGRES_PORT env variable is empty"
    ERRORS=$((ERRORS + 1))
fi

if [[ ${ERRORS} > 0 ]]; then
    echo "DANGER: There are ${ERRORS} errors. See the console above. Exiting..."
    exit 1
fi


database_ready() {
python << END
import sys
import psycopg2

try:
    psycopg2.connect(
        dbname="${DATABASE_DB}",
        user="${DATABASE_USER}",
        password="${DATABASE_PASSWORD}",
        host="${POSTGRES_HOST}",
        port="${POSTGRES_PORT}",
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)

END
}

echo "------"
echo "GEOSERVER_DATABASE_HOST=${POSTGRES_HOST}"
echo "GEOSERVER_DATABASE_PORT=${POSTGRES_PORT}"
echo "GEOSERVER_DATABASE=${DATABASE_DB}"
echo "GEOSERVER_DATABASE_USER=${DATABASE_USER}"
echo "GEOSERVER_DATABASE_PASSWORD=${DATABASE_PASSWORD}"
echo "------"

until database_ready; do
  >&2 echo 'Waiting for connecting database...'
  sleep 1
done
>&2 echo 'Database connection successful!'


export DATABASE_URL="postgres://${DATABASE_USER}:${DATABASE_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${DATABASE_DB}"

exec "$@"
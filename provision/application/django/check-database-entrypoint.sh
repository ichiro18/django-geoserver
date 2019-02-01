#!/bin/bash
set -e

ERRORS=0

if [ -z "${POSTGRES_DB}" ]; then
    echo "ERROR: POSTGRES_DB env variable is empty"
    ERRORS=$((ERRORS + 1))
fi

if [ -z "${POSTGRES_USER}" ]; then
    echo "ERROR: POSTGRES_USER env variable is empty"
    ERRORS=$((ERRORS + 1))
fi

if [ -z "${POSTGRES_PASSWORD}" ]; then
    echo "ERROR: POSTGRES_PASSWORD env variable is empty"
    ERRORS=$((ERRORS + 1))
fi

if [ -z "${POSTGRES_HOST}" ]; then
    echo "ERROR: POSTGRES_HOST env variable is empty"
    ERRORS=$((ERRORS + 1))
fi

if [ -z "${POSTGRES_PORT}" ]; then
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
        dbname="${POSTGRES_DB}",
        user="${POSTGRES_USER}",
        password="${POSTGRES_PASSWORD}",
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
echo "GEOSERVER_DATABASE=${POSTGRES_DB}"
echo "GEOSERVER_DATABASE_USER=${POSTGRES_USER}"
echo "GEOSERVER_DATABASE_PASSWORD=${POSTGRES_PASSWORD}"
echo "------"

until database_ready; do
  >&2 echo 'Waiting for connecting database...'
  sleep 1
done
>&2 echo 'Database connection successful!'


export DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"

exec "$@"
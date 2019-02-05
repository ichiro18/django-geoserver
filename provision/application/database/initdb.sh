#!/bin/bash
set -e


function create_database() {
    local db=$1
    local user=$2
    local password=$3
    echo "Creating user and database '$db'"
    psql -v ON_ERROR_STOP=1 --username "${POSTGRES_USER}" <<-EOSQL
        CREATE USER ${user};
            ALTER USER ${user} with encrypted password '${password}';
        CREATE DATABASE ${db};
        GRANT ALL PRIVILEGES ON DATABASE ${db} TO ${user};
EOSQL
}

function patch_database() {
    local db=$1
    echo "Patching database '$db' with extension"
    psql -v ON_ERROR_STOP --username "${POSTGRES_USER}" --dbname "$db" <<-EOSQL
        CREATE EXTENSION postgis;
EOSQL
}


if [[ -n ${DATABASE_DB} ]]; then
    echo "Creating main database '${DATABASE_DB}'"
    create_database ${DATABASE_DB} ${DATABASE_USER} ${DATABASE_PASSWORD}
    patch_database ${DATABASE_DB}
    echo "Main database created"
fi

if [[ -n ${GEODATABASE_DB} ]]; then
    echo "Creating geo database '${GEODATABASE_DB}'"
    create_database ${GEODATABASE_DB} ${GEODATABASE_USER} ${GEODATABASE_PASSWORD}
    patch_database ${GEODATABASE_DB}
    echo "Geo database created"
fi
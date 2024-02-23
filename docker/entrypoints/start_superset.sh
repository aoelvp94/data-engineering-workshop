#!/bin/bash
# Script that allows the user and connection creation for Superset service. Also it would allow us to import dashboards/datasources.
if [ "$SUPERSET_CREATE_USER" = true ]; then
    echo "Creating superset user..."
    superset-init --username "$SUPERSET_USER" --password "$SUPERSET_PASSWORD" --firstname "$SUPERSET_FIRSTNAME" --lastname "$SUPERSET_LASTNAME" --email "$SUPERSET_EMAIL"
    pip3 install duckdb-engine
    superset set_database_uri -d duckdb -u duckdb:///data.duckdb
fi

gunicorn --bind 0.0.0.0:"$SUPERSET_PORT" -w 10 --timeout 120 "superset.app:create_app()"
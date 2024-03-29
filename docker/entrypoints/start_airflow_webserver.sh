#!/bin/bash
# Script that allows the users creations for Airflow service.

poetry run airflow db init
if [ "$AIRFLOW_CREATE_USER_CONN" = true ]; then
    # Create User
    echo "Creating airflow user..."
    poetry run airflow users create -r "$AIRFLOW_ROLE" -u "$AIRFLOW_USER" -p "$AIRFLOW_PASSWORD" -f "$AIRFLOW_FIRST" -l "$AIRFLOW_LAST" -e "$AIRFLOW_EMAIL"
fi

cd dbt_project && poetry run dbt deps
poetry run airflow webserver -p "$AIRFLOW_PORT"

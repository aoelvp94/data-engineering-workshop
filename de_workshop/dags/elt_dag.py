"""DBT DAG to transform raw data into bronze models."""
import datetime

import duckdb
from airflow.decorators import task
from airflow.models import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator

from de_workshop.config import DBT_PROJECT_DIR
from de_workshop.dags.task_groups.dbt_taskgroup import dbt_task_group
from de_workshop.extract import get_data_from_gnews
from de_workshop.helpers import create_minio_bucket

default_args = {
    "owner": "mutt",
    "retries": 0,
    "start_date": datetime.datetime(2023, 11, 22),
}
with DAG(
    "elt_dag",
    default_args=default_args,
    schedule=None,
) as dag:

    @task
    def create_duckdb_table():
        """Create duckdb table from minio csv location"""
        conn = duckdb.connect(str(DBT_PROJECT_DIR / "data.duckdb"))
        conn.sql("INSTALL httpfs")
        conn.sql("LOAD httpfs")
        conn.sql("SET s3_url_style='path';")
        conn.sql("SET s3_endpoint='host.docker.internal:9000';")
        conn.sql("SET s3_access_key_id='minioadmin';")
        conn.sql("SET s3_secret_access_key='minioadmin';")
        conn.sql("SET s3_region='us-east-1'")
        conn.sql("SET http_keep_alive='false'")
        conn.execute("SET s3_use_ssl='false'")
        conn.sql(
            "CREATE TABLE IF NOT EXISTS raw_data AS SELECT * FROM read_csv('s3://de-data-bronze/data.csv', header=true, all_varchar=1, ignore_errors = true)"
        )
        conn.close()

    pre_dbt_task = EmptyOperator(task_id="pre_dbt_task")

    ingest_data = PythonOperator(
        task_id="ingest_data",
        python_callable=get_data_from_gnews,
        op_args=["Messi"],
    )

    create_silver_bucket = PythonOperator(
        task_id="create_silver_bucket",
        python_callable=create_minio_bucket,
        op_args=["minioadmin",
        "minioadmin",
        "host.docker.internal:9000",
        "de-data-silver"],
    )

    bronze_to_silver = dbt_task_group(model_name="silver")

    create_gold_bucket = PythonOperator(
        task_id="create_gold_bucket",
        python_callable=create_minio_bucket,
        op_args=["minioadmin",
        "minioadmin",
        "host.docker.internal:9000",
        "de-data-gold"],
    )

    silver_to_gold = dbt_task_group(model_name="gold")


    post_dbt_task = EmptyOperator(task_id="post_dbt_task")

    (  # pylint: disable=W0104
        pre_dbt_task
        >> ingest_data
        >> create_duckdb_table()
        >> create_silver_bucket
        >> bronze_to_silver
        >> create_gold_bucket
        >> silver_to_gold
        >> post_dbt_task
    )

from datetime import timedelta

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG
from pendulum import datetime


AIRFLOW_HOME = "/usr/local/airflow"
DBT_PROJECT_DIR = f"{AIRFLOW_HOME}/dbt/triplens_dbt"
DBT_EXECUTABLE = f"{AIRFLOW_HOME}/dbt_venv/bin/dbt"


with DAG(
    dag_id="triplens_countries_pipeline",
    description="Extract country data, store it in MinIO, load Snowflake, and run dbt.",
    start_date=datetime(2026, 7, 21, tz="Europe/London"),
    schedule="0 6 * * 1",
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "triplens",
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
    },
    tags=["triplens", "countries", "data-engineering"],
) as dag:

    extract_countries = BashOperator(
        task_id="extract_countries",
        bash_command=f"""
            set -euo pipefail
            python {AIRFLOW_HOME}/include/triplens/extract_countries.py
        """,
        cwd=AIRFLOW_HOME,
    )

    upload_to_minio = BashOperator(
        task_id="upload_to_minio",
        bash_command=f"""
            set -euo pipefail
            export MINIO_ENDPOINT="$MINIO_AIRFLOW_ENDPOINT"
            python {AIRFLOW_HOME}/include/triplens/upload_to_minio.py
        """,
        cwd=AIRFLOW_HOME,
    )

    load_raw_to_snowflake = BashOperator(
        task_id="load_raw_to_snowflake",
        bash_command=f"""
            set -euo pipefail
            export MINIO_ENDPOINT="$MINIO_AIRFLOW_ENDPOINT"
            python {AIRFLOW_HOME}/include/triplens/load_raw_to_snowflake.py
        """,
        cwd=AIRFLOW_HOME,
    )

    run_dbt_models = BashOperator(
        task_id="run_dbt_models",
        bash_command=f"""
            set -euo pipefail
            {DBT_EXECUTABLE} run --profiles-dir .
        """,
        cwd=DBT_PROJECT_DIR,
    )

    run_dbt_tests = BashOperator(
        task_id="run_dbt_tests",
        bash_command=f"""
            set -euo pipefail
            {DBT_EXECUTABLE} test --profiles-dir .
        """,
        cwd=DBT_PROJECT_DIR,
    )

    (
        extract_countries
        >> upload_to_minio
        >> load_raw_to_snowflake
        >> run_dbt_models
        >> run_dbt_tests
    )
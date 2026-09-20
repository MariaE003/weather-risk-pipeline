from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from datetime import datetime

default_args = {#peut reessayee deux fois
    "retries": 2
}

with DAG(
    dag_id="weather_risk_pipeline",
    start_date=datetime(2026, 9, 18),
    schedule="@daily",
    catchup=False,
    default_args=default_args
) as dag:

    extract_weather = BashOperator(
        task_id="extract_weather",
        bash_command="cd /opt/airflow && python extraction/extract.py"
    )

    transform_weather = BashOperator(
        task_id="transform_weather",
        bash_command="cd /opt/airflow && python transformation/transform.py"
    )

    load_postgres = BashOperator(
        task_id="load_postgres",
        bash_command="cd /opt/airflow && python sql/main.py"
    )

    extract_weather >> transform_weather >> load_postgres
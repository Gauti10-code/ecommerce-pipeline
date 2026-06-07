from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'eden',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id='dbt_transformation',
    default_args=default_args,
    description='Run dbt models for transformation',
    schedule_interval='@daily',
    start_date=datetime(2026, 6, 5),
    catchup=False,
    tags=['transformation']
) as dag:

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd /home/eden/ecommerce_pipeline/dbt && source /home/eden/ecommerce_pipeline/venv/bin/activate && dbt run',
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='cd /home/eden/ecommerce_pipeline/dbt && source /home/eden/ecommerce_pipeline/venv/bin/activate && dbt test',
    )

    dbt_run >> dbt_test
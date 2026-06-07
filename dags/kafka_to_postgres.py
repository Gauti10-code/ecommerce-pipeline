from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'eden',
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id='kafka_to_postgres',
    default_args=default_args,
    description='Produce data to Kafka and consume into PostgreSQL',
    schedule_interval='@daily',
    start_date=datetime(2026, 6, 5),
    catchup=False,
    tags=['ingestion']
) as dag:

    produce_data = BashOperator(
        task_id='produce_to_kafka',
        bash_command='source /home/eden/ecommerce_pipeline/venv/bin/activate && python /home/eden/ecommerce_pipeline/kafka/producer.py',
    )

    consume_data = BashOperator(
        task_id='consume_from_kafka',
        bash_command='source /home/eden/ecommerce_pipeline/venv/bin/activate && python /home/eden/ecommerce_pipeline/kafka/consumer.py',
    )

    produce_data >> consume_data
from airflow import DAG
from airflow.models import Variable
from airflow.operators.dummy import DummyOperator
from airflow.utils.task_group import TaskGroup
from operators.api_to_s3 import APIToS3Operator
from datetime import datetime
from datetime import timedelta

with DAG(
    dag_id="football_leagues_dimensions",
    start_date=datetime(2023,5,1),
    schedule="@daily",
    catchup=False,
    tags= ["api"],
    default_args={
        "owner": "adrian.pasek",
        "retries": 5,
        "retry_delay": timedelta(seconds=10),
        "sla": timedelta(hours=24),
        "execution_timeout": timedelta(hours=1)
    },
    params={
        "env": "dev",
        "http_conn": "api-football",
        "aws_conn": "football-leagues-data-loader",
        "code": "PL",
        "season": "2023"
    }
) as dag:
    
    start_dag = DummyOperator(task_id="start_dag", dag=dag)
    
    with TaskGroup("ingest_source_data") as ingest_source_data:

        timezone = APIToS3Operator(
            task_id="timezone",
            params={"entity": "timezone"},
            http_conn_id="{{ params.http_conn }}",
            aws_conn_id="{{ params.aws_conn }}",
            s3_bucket=Variable.get("s3_bucket_name"),
            s3_key="{{ params.env }}/{{ params.entity }}/{{ params.entity}}.json",
            endpoint="{{ params.entity }}",
        )
    
# s3_key="timezone/players_{{ data_interval_start | ds }}.json",
if __name__ == "__main__":
    dag.test()
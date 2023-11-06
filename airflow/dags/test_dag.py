from airflow import DAG
from airflow.models import Variable
from operators.api_to_s3 import APIToS3Operator
from datetime import datetime

with DAG(
    dag_id="api_test",
    start_date=datetime(2023,11,6),
    schedule="@daily",
    catchup=False,
    tags= ["api"],
    default_args={
        "owner": "adrian.pasek",
        "retries": 2,
    }
) as dag:
    
    t1 = APIToS3Operator(
        task_id="api_to_s3",
        http_conn_id="api-football",
        aws_conn_id="football-leagues-data-loader",
        s3_bucket=Variable.get("s3_bucket_name"),
        s3_key="timezone/timezone_{{ data_interval_start | ds }}.json",
        endpoint="timezone",
    )
    
    t1

if __name__ == "__main__":
    dag.test()
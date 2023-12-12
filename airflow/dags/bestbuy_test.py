import json
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.providers.http.operators.http import HttpOperator
from operators.http_to_s3 import HttpToS3Operator
from airflow.models import Variable
from datetime import datetime
from datetime import timedelta
import time




with DAG(
    dag_id="bestbuy-api",
    start_date=datetime(2023,5,1),
    schedule="@daily",
    catchup=False,
    tags= ["bestbuy"],
    default_args={
        "owner": "adrian.pasek",
        "retries": 5,
        "retry_delay": timedelta(seconds=10),
        "execution_timeout": timedelta(hours=1)
    },
    params={
        "http_conn_id": "bestbuy-api",
    }
) as dag:
    
    def get_next_page(response):

        time.sleep(1)
        current_page = response.json().get("currentPage")
        total_pages = response.json().get("totalPages")
        next_page = current_page + 1

        # # filter the response and overwrite the content of original Response object
        # filtered_response = response.json().get("products")
        # # Add UTC timestamp for every item
        # for item in filtered_response:
        #     item["retrievalTimestamp"] = datetime.utcnow().isoformat() + "Z"
        # response._content = json.dumps(filtered_response).encode()

        if next_page <= total_pages:
            return dict(data={"page": next_page})
        return None
    
    start_task = EmptyOperator(
        task_id="start_task"
    )

    test_task = HttpToS3Operator(
        task_id="test_task",
        http_conn_id="bestbuy-api",
        method="GET",
        endpoint='products(categoryPath.id=abcat0700000&onSale=true&freeShipping=true&inStoreAvailability=true)?apiKey=vPfPIjFVswznNKfOB7R8BA9e&pageSize=100&format=json',
        pagination_function=get_next_page,
        aws_conn_id="football-leagues-data-loader",
        s3_bucket=Variable.get("s3_bucket_name"),
        s3_key="dev/bestbuy/test/response_{{ ds }}.json",
    )

    start_task >> test_task

if __name__ == "__main__":
    dag.test()

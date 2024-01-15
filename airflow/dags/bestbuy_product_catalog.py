from airflow import DAG
from airflow.operators.empty import EmptyOperator
from operators.http_to_s3 import HttpToS3Operator
from airflow.models import Variable
from datetime import datetime
from datetime import timedelta
import time
import os

API_KEY = os.getenv("BESTBUY_API_KEY")
PRODUCT_FIELD_LIST = [
    "sku", "name", "type", "start_date", "active", "active_update_date",
    "regular_price", "sale_price", "price_update_date", "on_sale", "url",
    "upc", "category_path", "alternate_categories", "customer_review_count",
    "customer_review_average", "customer_top_rated", "free_shipping",
    "in_store_availability", "in_store_availability_update_date",
    "item_update_date", "online_availability",
    "online_availability_update_date", "release_date", "shipping_cost",
    "manufacturer", "model_number", "dollar_savings", "percent_savings"
]

def filter_response(response, key):
    return [item.json().get(key) for item in response]

with DAG(
    dag_id="bestbuy_product_catalog",
    start_date=datetime(2023,11,1),
    schedule="@daily",
    catchup=True,
    max_active_runs=1,
    tags= ["bestbuy", "http_operator"],
    default_args={
        "owner": "adrian.pasek",
        "retries": 5,
        "retry_delay": timedelta(seconds=10),
        "execution_timeout": timedelta(hours=1),
        "depends_on_past": True,
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

        if next_page <= total_pages:
            return dict(data={"page": next_page})
        return None
    
    start_task = EmptyOperator(
        task_id="start_task"
    )

    get_products_task = HttpToS3Operator(
        task_id="get_products_task",
        http_conn_id="bestbuy-api",
        method="GET",
        endpoint=f"products(categoryPath.id=abcat0700000)?apiKey={API_KEY}&show={','.join(PRODUCT_FIELD_LIST)}&pageSize=100&format=json",
        response_filter=lambda response: filter_response(response, "products"), 
        pagination_function=get_next_page,
        aws_conn_id="bestbuy-product-catalog-data-loader",
        s3_bucket=Variable.get("s3_bucket_name"),
        s3_key="bestbuy/products/products_{{ ds }}.json",
        do_xcom_push=False,
    )

    end_task = EmptyOperator(
        task_id="end_task"
    )


    start_task >> get_products_task >> end_task
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from operators.http_to_s3 import HttpToS3Operator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from great_expectations_provider.operators.great_expectations import GreatExpectationsOperator
from airflow.models import Variable
from datetime import datetime
from datetime import timedelta
import os
import time

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
    start_date=datetime(2023,12,2),
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
        "snowflake_conn_id": "snowflake",
        "warehouse": "DATA_LOAD_XS",
        "role": "DATA_LOADER",
        "raw_schema": "BESTBUY_RAW.PUBLIC",
        "raw_table": "JSON_RAW"
    },
    template_searchpath="/opt/airflow/plugins/sql",
) as dag:
    
    def get_next_page(response):

        # throttle call due to rate limit
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

    # Define a list of product categories
    product_categories = {"video_games": "(pcmcat1487699281907)",
                           "tvs": "(abcat0101001)",
                           "headphones": "(abcat0204000)",
                           "laptops": "(abcat0502000)",
                           "smartphones": "(pcmcat311200050005)",
                           "toys": "(pcmcat1492451998184)",
                           "gaming_furniture": "(pcmcat219100050010)",
                           "wearable_technology": "(pcmcat332000050000)",
    }
    endpoints = [f"products(categoryPath.id in {category})?apiKey={API_KEY}&show={','.join(PRODUCT_FIELD_LIST)}&pageSize=100&format=json" for category in product_categories.values()]
    s3_paths = [f"bestbuy/products/categories/{category}/" + "{{ ds }}" + ".json" for category in product_categories]
    # Create a kwargs list with the endpoint and s3_path for each product category
    zipped = zip(endpoints, s3_paths)
    kwargs_list = [{"endpoint": endpoint, "s3_key": s3_path} for endpoint, s3_path in zipped]

    # Retrieve data from API and transfer it to S3
    get_products_task = HttpToS3Operator.partial(
        task_id="get_products_task",
        http_conn_id="bestbuy-api",
        method="GET",
        response_filter=lambda response: filter_response(response, "products"), 
        pagination_function=get_next_page,
        aws_conn_id="bestbuy-product-catalog-data-loader",
        s3_bucket=Variable.get("s3_bucket_name"),
        do_xcom_push=False,
        pool="one_slot"
    ).expand_kwargs(
        kwargs_list
    )


    # Copy into Snowflake
    copy_into_snowflake_task = SQLExecuteQueryOperator(
        task_id="copy_into_snowflake_task",
        conn_id="snowflake",
        autocommit=True,
        sql="copy_into_json.sql",
        split_statements=True
    )

    # Check row count
    check_copy_into_row_count = GreatExpectationsOperator(
        task_id="check_copy_into_row_count",
        conn_id="snowflake",
        schema="PUBLIC",
        data_asset_name="JSON_RAW",
        data_context_root_dir="include/gx",
        query_to_validate="SELECT COUNT(*) FROM {{ params.raw_schema }}.{{ params.raw_table}} WHERE LOAD_DATE = '{{ ds }}'",
        expectation_suite_name="standard_suite"
    )

    end_task = EmptyOperator(
        task_id="end_task"
    )

    start_task >> get_products_task >> copy_into_snowflake_task >> check_copy_into_row_count >> end_task
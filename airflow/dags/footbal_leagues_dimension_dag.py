from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable
from airflow.operators.dummy import DummyOperator
from airflow.utils.task_group import TaskGroup
from operators.api_to_s3 import APIToS3Operator
from datetime import datetime
from datetime import timedelta
from itertools import product

@task
def get_xcom_iterables(xcom_task_ids: list, xcom_key: str, s3_key: str = None, **kwargs):
    ti = kwargs["ti"]
    # Get a list of returned xcoms produced by tasks
    xcoms = [ti.xcom_pull(task_ids=x, key=xcom_key) for x in xcom_task_ids]
    # Create a product (all combinations) of xcoms in form of list of tuples
    xcom_combinations = list(product(*xcoms))
    # If s3_key was provided, return a list of S3 paths
    if s3_key:
        result = [s3_key.format(*combo) for combo in xcom_combinations]
    # Otherwise return a list of dicts that will serve as query_params
    if isinstance(xcom_combinations[0][0], dict):
        result = []
        for combo in xcom_combinations:
            merged_dict = {}
            for d in combo:
                merged_dict.update(d)
            result.append(merged_dict)
    return result
    
with DAG(
    dag_id="football_leagues_dimensions",
    start_date=datetime(2023,5,1),
    schedule="@daily",
    catchup=False,
    tags= ["football-leagues"],
    default_args={
        "owner": "adrian.pasek",
        "retries": 5,
        "retry_delay": timedelta(seconds=10),
        "execution_timeout": timedelta(hours=1)
    },
    params={
        "env": "dev",
        "http_conn_id": "api-football",
        "aws_conn_id": "football-leagues-data-loader",
        "country": "poland",

    }
) as dag:
    
    start_dag = DummyOperator(task_id="start_dag", dag=dag)
    

    timezone = APIToS3Operator(
        task_id="timezone",
        params={"entity": "timezone"},
        http_conn_id="{{ params.http_conn_id }}",
        aws_conn_id="{{ params.aws_conn_id }}",
        s3_bucket=Variable.get("s3_bucket_name"),
        s3_key="{{ params.env }}/{{ params.entity }}/{{ params.entity}}.json",
        endpoint="{{ params.entity }}",
    )

    country = APIToS3Operator(
        task_id="country",
        params={"entity": "country"},
        http_conn_id="{{ params.http_conn_id }}",
        aws_conn_id="{{ params.aws_conn_id }}",
        s3_bucket=Variable.get("s3_bucket_name"),
        s3_key="{{ params.env }}/{{ params.entity }}/{{ params.entity}}_{{ data_interval_start | ds }}.json",
        endpoint="countries",
    )

    league = APIToS3Operator(
        task_id="league",
        params={"entity": "league"},
        http_conn_id="{{ params.http_conn_id }}",
        aws_conn_id="{{ params.aws_conn_id }}",
        s3_bucket=Variable.get("s3_bucket_name"),
        s3_key="{{ params.env }}/{{ params.entity }}/{{ params.entity}}_{{ data_interval_start | ds }}.json",
        query_params={"type": "{{ params.entity}}",
                      "id": 106},
        endpoint="leagues",
        do_xcom_push=True,
        entity_key="{{ params.entity }}",
    )

    season = APIToS3Operator(
        task_id="season",
        params={"entity": "season"},
        http_conn_id="{{ params.http_conn_id }}",
        aws_conn_id="{{ params.aws_conn_id }}",
        s3_bucket=Variable.get("s3_bucket_name"),
        s3_key="{{ params.env }}/{{ params.entity }}/{{ params.entity}}.json",
        endpoint="leagues/seasons",
        do_xcom_push=True,
        entity_key="{{ params.entity }}",
    )

    prepare_team_s3_paths = get_xcom_iterables.override(
        task_id="prepare_team_s3_paths")(
            ["league", "season"],
            "entity_ids",
            "{{ params.env }}/team/teams_{}_{}_{{ data_interval_start | ds }}.json",
        )

    prepare_team_query_params = get_xcom_iterables.override(
        task_id="prepare_team_query_params")(
            ["league", "season"],
            "query_params_list",
        )
    
    team = APIToS3Operator.partial(
        task_id="team",
        params={"entity": "team"},
        http_conn_id="{{ params.http_conn_id }}",
        aws_conn_id="{{ params.aws_conn_id }}",
        s3_bucket=Variable.get("s3_bucket_name"),
        endpoint="teams",
    ).expand(
        s3_key=prepare_team_s3_paths,
        query_params=prepare_team_query_params,
    )

    [league, season] >> prepare_team_s3_paths


# if __name__ == "__main__":
#     dag.test()
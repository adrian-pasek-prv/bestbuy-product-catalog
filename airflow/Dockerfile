ARG _PYTHON_VERSION=3.11
FROM apache/airflow:2.8.1-python${_PYTHON_VERSION}
ARG _PYTHON_VERSION
COPY requirements.txt /
RUN pip install --no-cache-dir apache-airflow[crypto,postgres,amazon,snowflake,dbt-cloud,tableau,http]==${AIRFLOW_VERSION} \
  -r /requirements.txt \
  --constraint https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${_PYTHON_VERSION}.txt
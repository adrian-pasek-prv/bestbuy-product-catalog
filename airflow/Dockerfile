ARG _PYTHON_VERSION=3.9
FROM apache/airflow:2.7.1-python${_PYTHON_VERSION}
ARG _PYTHON_VERSION
COPY requirements.txt /
RUN pip install --no-cache-dir apache-airflow[postgres,amazon,snowflake,dbt-cloud,tableau]==${AIRFLOW_VERSION} \
  -r /requirements.txt \
  --constraint https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${_PYTHON_VERSION}.txt
from ast import excepthandler
from typing import Sequence
from airflow.models.baseoperator import BaseOperator
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.exceptions import AirflowException

class APIToS3Operator(BaseOperator):
    """
    Connect to API using http_conn and upload response from endpoint to S3 bucket as a JSON 
    using a date suffix.

    Args:
        http_conn_id (str): http_conn_id from Airflow connections
        aws_conn_id (str): AWS credentials from Airflow connections
        s3_bucket (str): S3 bucket name
        s3_key (str): templateable S3 bucket key, adding a date suffix from {{ data_interval_date }} recommended
        endpoint (str): API endpoint to call
        replace_s3_obj (bool, optional): replace an S3 object. Defaults to True.
        method (str, optional): API method to call. Defaults to "GET".
    """   

    template_fields: Sequence[str] = ("endpoint", "s3_key",)

    def __init__(self,
                 http_conn_id: str,
                 aws_conn_id: str,
                 s3_bucket: str,
                 s3_key: str,
                 endpoint: str,
                 replace_s3_obj: bool = True,
                 method: str = "GET",
                 **kwargs) -> None:     
        super().__init__(**kwargs)
        self.http_conn_id = http_conn_id
        self.aws_conn_id = aws_conn_id
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.endpoint = endpoint
        self.replace_s3_obj = replace_s3_obj
        self.method = method
    

    def execute(self, context):

        # Get the rendered fields
        endpoint = self.endpoint.format(**context)
        s3_key = self.s3_key.format(**context)
        self.log.info(f"Rendered fields:\nendpoint: {endpoint},\ns3_key: {s3_key}")

        # Establish hooks
        http_hook = HttpHook(method=self.method, http_conn_id=self.http_conn_id)
        s3_hook = S3Hook(aws_conn_id=self.aws_conn_id)

        # Get the response from endpoint
        self.log.info(f"Getting response from endpoint: {self.endpoint}")
        response = http_hook.run(endpoint=endpoint)

        # Check for response other than 2xx and 3xx
        try:
            http_hook.check_response(response)
        except AirflowException as e:
            self.log.error(f"Response unsuccessful from endpoint: '{self.endpoint}':")
            self.log.error(e)
            raise e
        # Check if response contains errors:
        if response.json().get("errors"):
            self.log.error(f"Response contains errors from endpoint: '{self.endpoint}':")
            self.log.error(response.json().get("errors"))
            raise AirflowException(response.json().get("errors"))
        # Check if response contains any data:
        if len(response.json().get("response")) == 0:
            self.log.error(f"Response contains no data from endpoint: '{self.endpoint}':")
            raise AirflowException(f"Response contains no data from endpoint: '{self.endpoint}'")
        
        # Log if response was successful
        self.log.info(f"Response sucessful from endpoint: '{self.endpoint}'")

        # PUT reponse in form of bytes to S3 and save as JSON
        self.log.info(f"Saving response to S3: s3://{self.s3_bucket}/{s3_key}")
        try:
            s3_hook.load_bytes(bytes_data=response.content,
                            key=s3_key,
                            bucket_name=self.s3_bucket,
                            replace=self.replace_s3_obj)
        except AirflowException as e:
            self.log.error(f"Error saving response to S3: s3://{self.s3_bucket}/{s3_key}")
            self.log.error(e)
            raise e
        self.log.info(f"Successfully saved reponse to S3: s3://{self.s3_bucket}/{s3_key}")



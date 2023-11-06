from typing import Sequence
from airflow.models.baseoperator import BaseOperator
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

class APIToS3Operator(BaseOperator):

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
        self.log.info(f"Response successfull from endpoint: {self.endpoint}")

        # PUT reponse in form of bytes to S3 and save as JSON
        self.log.info(f"Saving response to S3: s3://{self.s3_bucket}/{s3_key}")
        s3_hook.load_bytes(bytes_data=response.content,
                           key=s3_key,
                           bucket_name=self.s3_bucket,
                           replace=self.replace_s3_obj)
        self.log.info(f"Successfully saved reponse to S3: s3://{self.s3_bucket}/{s3_key}")



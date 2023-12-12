from typing import Any
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import json

class HttpToS3Operator(HttpOperator):
    template_fields = HttpOperator.template_fields + ("aws_conn_id", "s3_bucket", "s3_key")

    def __init__(
        self,
        aws_conn_id: str = "aws_default",
        s3_bucket: str = None,
        s3_key: str = None,
        replace: bool = True,
        do_xcom_push: bool = False,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.aws_conn_id = aws_conn_id
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.replace = replace
        self.do_xcom_push = do_xcom_push

    def execute(self, context) -> Any:

        if self.deferrable:
            response = super().execute_async(context=context)
        else:
            response = super().execute_sync(context=context)

        # If response is paginated it contains a list of JSON-like strings
        # so convert strings into valid dicts
        response = [json.loads(item) for item in response]
        response_bytes = json.dumps(response).encode("utf-8")

        s3_hook = S3Hook(aws_conn_id=self.aws_conn_id)

        s3_hook.load_bytes(
            response_bytes,
            self.s3_key,
            self.s3_bucket,
            self.replace
        )




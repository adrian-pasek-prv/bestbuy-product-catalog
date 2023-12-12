import requests
import time
import json
import sys
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
        query_params (dict, optional): query parameters to pass to the endpoint. Defaults to {}
        replace_s3_obj (bool, optional): replace an S3 object. Defaults to True.
        method (str, optional): API method to call. Defaults to "GET".
    """

    template_fields = ("query_params", "s3_key", "http_conn_id", "aws_conn_id", "endpoint", "entity_key")

    def __init__(
        self,
        http_conn_id: str,
        aws_conn_id: str,
        s3_bucket: str,
        s3_key: str,
        endpoint: str,
        response_key: str = "response",
        query_params: dict = {},
        replace_s3_obj: bool = True,
        method: str = "GET",
        do_xcom_push: bool = False,
        entity_key: str = None,
        entity_id_key: str = "id",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.http_conn_id = http_conn_id
        self.aws_conn_id = aws_conn_id
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.endpoint = endpoint
        self.response_key = response_key
        self.query_params = query_params
        self.replace_s3_obj = replace_s3_obj
        self.method = method
        self.do_xcom_push = do_xcom_push
        self.entity_key = entity_key
        self.entity_id_key = entity_id_key

    def handle_api_exceptions(
        self,
        http_hook: HttpHook,
        response: requests.Response,
        endpoint: str = None,
        response_key: str = None,
        error_key: str = "errors",
    ):
        """
        Handle API exceptions like reponse other than 2xx, 3xx or no data

        Args:
            http_hook (HttpHook): http_hook.
            endpoint (str, optional): endpoint string. Defaults to None.
            response (requests.Response, optional): response object in JSON. Defaults to None.
            error_key (str, optional): dict key of the error inside requests.Response. Defaults to "errors"
            response_key (str, optional): dict key of the response inside requests.Response. Defaults to "response"
        Raises:
            e: Airflow Exception
        """
        endpoint = self.endpoint
        response_key = self.response_key

        # Check for response other than 2xx and 3xx
        try:
            http_hook.check_response(response)
        except AirflowException as e:
            self.log.error(f"Response unsuccessful from endpoint: '{endpoint}':")
            self.log.error(e)
            raise e
        # Check if response contains errors:
        if response.json().get(error_key):
            self.log.error(f"Response contains errors from endpoint: '{endpoint}':")
            self.log.error(response.json().get(error_key))
            raise AirflowException(response.json().get(error_key))
        # Check if response contains any data:
        if len(response.json().get(response_key)) == 0:
            self.log.warning(f"Response contains no data from endpoint: '{endpoint}':")
            sys.exit(0)

    def process_response(
        self, 
        http_hook: HttpHook,
        endpoint: str = None,
        query_params: dict = None,
        response_key: str = None, 
        paging_key: str = "paging",
        total_pages_key: str = "total",
        current_page_key: str = "current"
    ) -> dict:
        """
        Process the response from the API and return a dictionary. If response contains
        multiple pages iterate through them and extend the dictionary.

        Args:
            http_hook (HttpHook): Airflow HttpHook object
            endpoint (str, optional): API endpoint. Defaults to None.
            query_params (dict, optional): API endpoint query parameters as dict. Defaults to None.
            response_key (str, optional): API response key indicating response content. Defaults to "response".
            paging_key (str, optional): API response key indicating paging info. Defaults to "paging".
            total_pages_key (str, optional): API response key indicating total number of pages. Defaults to "total"
            current_page_key (str, optional): API response key indicating current page. Defaults to "current".

        Raises:
            AirflowException: _description_

        Returns:
            dict: _description_
        """

        # Set params to ones provided in the class
        endpoint = self.endpoint
        query_params = self.query_params
        response_key = self.response_key

        self.log.info(f"Getting response from endpoint: {self.endpoint}")
        # Get the initial response in order to determine number of pages
        initial_response = http_hook.run(endpoint=endpoint, data=query_params)
        self.handle_api_exceptions(http_hook, initial_response)
        # Set initial_reponse to JSON
        initial_response = initial_response.json()
        # Initialize page counters
        total_pages = initial_response[paging_key][total_pages_key]
        current_page = initial_response[paging_key][current_page_key]
        # Remove unnecessary keys
        keys = ["errors", "results", "paging"]
        try:
            for key in keys:
                del initial_response[key]
        except KeyError as e:
            self.log.error(f"Couldn't remove key: '{key}' because it doesn't exists")
            raise e
        self.log.info(f"Returning response from endpoint: '{endpoint}'")
        self.log.info(f"Total pages: {total_pages}, Current page: {current_page} in endpoint: '{endpoint}'")
        # Go to next page
        current_page += 1
        while current_page <= total_pages:
            self.log.info(f"Total pages: {total_pages}, Current page: {current_page} in endpoint: '{endpoint}'")
            page = {"page": current_page}
            response = http_hook.run(endpoint=endpoint, 
                                        data=query_params | page)
            self.handle_api_exceptions(http_hook, response)
            # Set reponse to JSON
            response = response.json()
            # Iterate over items in response and append to initial response
            for item in response[response_key]:
                initial_response[response_key].append(item)
            current_page += 1
            time.sleep(1)
        return initial_response


    def execute(self, context):
        # Establish hooks
        http_hook = HttpHook(method=self.method, http_conn_id=self.http_conn_id)
        s3_hook = S3Hook(aws_conn_id=self.aws_conn_id)

        # Get the response from endpoint
        response = self.process_response(http_hook)

        # Add processing timestamp as a string
        response["processing_timestamp"] = context["ts"]

        # Convert JSON reponse to bytes
        response_bytes = json.dumps(response).encode('utf-8')

        # PUT reponse in form of bytes to S3 and save as JSON
        self.log.info(f"Saving response to S3: s3://{self.s3_bucket}/{self.s3_key}")
        try:
            s3_hook.load_bytes(
                bytes_data=response_bytes,
                key=self.s3_key,
                bucket_name=self.s3_bucket,
                replace=self.replace_s3_obj,
            )
        except AirflowException as e:
            self.log.error(
                f"Error saving response to S3: s3://{self.s3_bucket}/{self.s3_key}"
            )
            self.log.error(e)
            raise e
        self.log.info(
            f"Successfully saved reponse to S3: s3://{self.s3_bucket}/{self.s3_key}"
        )

        if self.do_xcom_push:
            # We need to return a list of ids that we can later iterate on with API calls that require some id parameters
            # If the response contains a list of dicts of entities we need to extract their ids into a list
            # Otherwise if response is just a list then it's a list of ids
            response_content = response[self.response_key]
            if isinstance(response_content[0], dict):
                entity_ids= []
                for item in response_content:
                    entity = item.get(self.entity_key)
                    entity_ids.append(entity.get(self.entity_id_key))
            # Else it must be a simple list of ids
            else:
                entity_ids = [id for id in response_content]
            context["ti"].xcom_push(key="entity_ids", value=entity_ids)
            # Also provide a list of dicts for query_params eg. [{"league": 1}, {"league": 2}] so we can iterate in query_params
            query_params_list = [{self.entity_key: id} for id in entity_ids]
            context["ti"].xcom_push(key="query_params_list", value=query_params_list)
                
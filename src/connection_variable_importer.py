import json
import logging
from pathlib import Path

from airflow import settings
from airflow.models import Connection

def add_connection(json_file, user_name_key, conn_id, conn_type, role_key):
    '''
    Add connection to Airflow backend database using Connection class 
    where a json file with credentials will be passed
    
    :param json_file: Path to json file with credentials
    :param user_name_key: Key of user name in json file
    :param conn_id: Connection id
    :param conn_type: Connection type
    :param role_key: Key of role in json file
    
    :return: None
    
    :raises: Exception if error adding connection to Airflow backend database
    
    :Example:
    
    >>> add_connection(json_file="credentials.json",
                       user_name_key="user_name",
                       conn_id="aws_credentials",
                       conn_type="aws",
                       role_key="role")
    '''
    
    with open(json_file) as f:
        data = json.load(f)
        
    credentials = data["users"]["value"][user_name_key]
    variables = data["variables"]["value"]
    
    # Create Connection object
    conn = Connection(conn_id=conn_id,
                      conn_type=conn_type,
                      login=credentials["access_key"],
                      password=credentials["access_secret"],
                      extra={
                          "region_name": variables["aws_region"],
                          "role_arn": variables[role_key]
                      }
    )
    
    # Create Airflow session
    logging.info(f"Creating Airflow session")
    session = settings.Session()
    logging.info(f"Adding connection {conn_id} to Airflow backend database")
    try:
        session.add(conn)
        session.commit()
    except:
        logging.exception(f"Error adding connection {conn_id} to Airflow backend database")
        raise
    
    
    
    
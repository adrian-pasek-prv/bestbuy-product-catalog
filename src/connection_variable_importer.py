import json
import logging

from airflow import settings
from airflow.models import Connection
from airflow.models import Variable

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
    logging.info(f"Adding connection '{conn_id}' to Airflow metadata database")
    try:
        # Check if the conn_id already exists in the database. If so, then delete it
        duplicate_connection = session.query(Connection).filter(Connection.conn_id == conn_id)
        if duplicate_connection:
            logging.warning(f"Connection '{conn_id}' already exists in the Airflow database. Overwriting ...")
            duplicate_connection.delete()
            session.commit()
        # Add new connection
        session.add(conn)
        session.commit()
        logging.info(f"Successfully added connection '{conn_id}' to Airflow database")
    except Exception as e:
        logging.exception(f"There was a problem with adding connection '{conn_id}':\n {e}")
        raise
    
def add_variable(json_file, variable_key, variable_name):
    '''
    Add variable to Airflow backend database using Variable class 
    where a json file with credentials will be passed
    
    :param json_file: Path to json file with credentials
    :param variable_key: Key of variable in json file
    :param variable_name: Name of the variable in Airflow
    
    :return: None
    
    :raises: Exception if error adding variable to Airflow backend database
    
    :Example:
    
    >>> add_variable(json_file="credentials.json",
                        variable_key="aws_region",
                        variable_name"aws_region")
    '''
    
    with open(json_file) as f:
        data = json.load(f)
    variables = data["variables"]["value"]
    
    # Set Variable object
    try:
        logging.info(f"Setting variable '{variable_name}' from key '{variable_key}'")
        Variable.set(key=variable_name, value=variables[variable_key])
        logging.info(f"Successfully set variable '{variable_name}'")
    except Exception as e:
        logging.exception(f"There was a problem with setting variable '{variable_name}':\n e")
    
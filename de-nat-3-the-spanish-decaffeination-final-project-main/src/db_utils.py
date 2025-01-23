import psycopg2 as psycopg2
import boto3
import logging
import json

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
# Initialize the AWS Systems Manager (SSM) client to retrieve parameters
ssm_client = boto3.client('ssm')

# Function to retrieve a parameter from AWS Systems Manager Parameter Store
def get_ssm_param(param_name):
    LOGGER.info(f'get_ssm_param: getting param_name={param_name}')
    # Retrieve the parameter details from the SSM Parameter Store
    parameter_details = ssm_client.get_parameter(Name=param_name)
    # Parse the JSON string in the parameter value to a dictionary
    redshift_details = json.loads(parameter_details['Parameter']['Value'])
    host = redshift_details['host']
    user = redshift_details['user']
    db = redshift_details['database-name']
    LOGGER.info(f'get_ssm_param: loaded for db={db}, user={user}, host={host}')
    # Return the Redshift connection details
    return redshift_details

# Function to open a connection to a Redshift database and create a cursor
def open_sql_database_connection_and_cursor(redshift_details):
    try:
        LOGGER.info('open_sql_database_connection_and_cursor: opening connection...')
        # Use psycopg2 to connect to the database using the provided details
        db_connection = psycopg2.connect(
            host=redshift_details['host'],
            database=redshift_details['database-name'],
            user=redshift_details['user'],
            password=redshift_details['password'],
            port=redshift_details['port'],
        )
        # Create a cursor object for executing SQL commands
        cursor = db_connection.cursor()
        LOGGER.info('open_sql_database_connection_and_cursor: connection ready')
        # Return the connection and cursor
        return db_connection, cursor
    except ConnectionError as ex:
        LOGGER.info(f'open_sql_database_connection_and_cursor: failed to open connection: {ex}')
        raise ex

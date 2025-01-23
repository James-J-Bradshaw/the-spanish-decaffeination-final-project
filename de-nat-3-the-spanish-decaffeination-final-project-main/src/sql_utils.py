import uuid
import logging

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

### Used to create tables onto the data warehouse using the connection, cursor and query provided
def create_db_tables(connection, cursor, query):
    LOGGER.info('create_db_tables: started')
    try:
        cursor.execute(query)
        connection.commit()
    except Exception as ex:
        LOGGER.info(f'create_db_tables: failed to run sql: {ex}')
        raise ex

### Used to load data onto the tables using the connection, cursor and query provided
def load_data_onto_db(connection,cursor,query):
    LOGGER.info('load_data_onto_db: started')
    try:
        cursor.execute(query)
        connection.commit()
    except Exception as ex:
        LOGGER.info(f'load_data_onto_db: failed to run sql: {ex}')
        raise ex

### Used to retrieve data from the tables in the data warehouse using the connection, cursor and query provided
def retrieve_data_from_db(connection,cursor,query):
    LOGGER.info('retrieve_data_from_db: started')
    try:
        cursor.execute(query)
        row = cursor.fetchone()
        connection.commit()
        return row
    except Exception as ex:
        LOGGER.info(f'retrieve_data_from_db: failed to run sql: {ex}')
        raise ex

### Used to create a genuinely unique identifier which is used for every single id for every single table
def create_guid():
    return str(uuid.uuid4())
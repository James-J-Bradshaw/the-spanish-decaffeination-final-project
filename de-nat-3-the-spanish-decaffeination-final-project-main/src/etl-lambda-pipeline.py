import db_utils, sql_utils, s3_utils
from data_transformation import *
from io import StringIO
import logging
from seperate_product_prices import *
import os

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

SSM_ENV_VAR_NAME = "SSM_PARAMETER_NAME"

#function lambda_handler is called whenever a file is uploaded to the S3 bucket on AWS
#Sets up a connection to the redshift data warehouse, creating new instances of tables if they don't exist already
#It retrieves the csv file from the S3 Bucket into python
#Then Transforms and Cleans the csv file into useable data
#Then it separates and loads this cleaned data onto the tables and joins them for 3NF dependencies
def lambda_handler(event, context):
    LOGGER.info("lambda_handler: starting")
    file_path = "NOT_SET"  # makes the exception handler compile

    try:
        ssm_param_name = os.environ[SSM_ENV_VAR_NAME] or "NOT_SET"
        LOGGER.info(
            f"lambda_handler: ssm_param_name={ssm_param_name} from ssm_env_var_name={SSM_ENV_VAR_NAME}"
        )

        ### This gets the csv file that was just uploaded into the bucket
        bucket_name, file_path = s3_utils.get_file_info(event)
        csv_text = s3_utils.load_file(bucket_name, file_path)
        csv_buffer = StringIO(csv_text)
        copy_buffer = StringIO(csv_text)

        ### This connects to the data warehouse and allows us to execute queries onto it
        redshift_details = db_utils.get_ssm_param(ssm_param_name)
        conn, cur = db_utils.open_sql_database_connection_and_cursor(redshift_details)

        ### This creates tables onto the data warehouse if it does not exist already
        sql_utils.create_db_tables(
            conn,
            cur,
            "CREATE TABLE IF NOT EXISTS product (product_id VARCHAR(36) PRIMARY KEY, product_name VARCHAR(100) NOT NULL, price REAL NOT NULL);",
        )
        sql_utils.create_db_tables(
            conn,
            cur,
            "CREATE TABLE IF NOT EXISTS branch (branch_id VARCHAR(36) PRIMARY KEY, branch_location VARCHAR(100) NOT NULL);",
        )
        sql_utils.create_db_tables(
            conn,
            cur,
            "CREATE TABLE IF NOT EXISTS payment_method (method_id VARCHAR(36) PRIMARY KEY, method VARCHAR(50));",
        )
        sql_utils.create_db_tables(
            conn,
            cur,
            "CREATE TABLE IF NOT EXISTS transaction_number (transaction_id VARCHAR(36) PRIMARY KEY, date_time TIMESTAMP WITHOUT TIME ZONE NOT NULL, branch_id VARCHAR(36), method_id VARCHAR(36), FOREIGN KEY (branch_id) REFERENCES branch(branch_id), FOREIGN KEY (method_id) REFERENCES payment_method(method_id));",
        )
        sql_utils.create_db_tables(
            conn,
            cur,
            "CREATE TABLE IF NOT EXISTS transactions (transaction_id VARCHAR(36), product_id VARCHAR(36), FOREIGN KEY (transaction_id) REFERENCES transaction_number(transaction_id), FOREIGN KEY (product_id) REFERENCES product(product_id));",
        )
        sql_utils.create_db_tables(
            conn,
            cur,
            "CREATE TABLE IF NOT EXISTS reports (report_id VARCHAR(36) PRIMARY KEY, branch_id VARCHAR(36), total_sales DECIMAL(18, 2) NOT NULL, total_transactions INT NOT NULL, date_generated TIMESTAMP WITHOUT TIME ZONE NOT NULL, FOREIGN KEY (branch_id) REFERENCES branch(branch_id));",
        )
        sql_utils.create_db_tables(
            conn,
            cur,
            "CREATE TABLE IF NOT EXISTS product (product_id VARCHAR(36) DEFAULT uuid_generate_v4() PRIMARY KEY, product_name VARCHAR(100) NOT NULL,price REAL NOT NULL)",
        )

        ### This transforms and cleans data specifically to retrieve products and price
        ### which is then loaded onto the database
        product_names, product_prices = load_products_and_price(csv_buffer)
        for i in range(len(product_names)):
            uuid = sql_utils.create_guid()
            query = f"INSERT INTO product (product_id, product_name, price) SELECT '{uuid}', '{product_names[i]}', {product_prices[i]} WHERE NOT EXISTS (SELECT 1 FROM product WHERE product_name = '{product_names[i]}')"
            sql_utils.load_data_onto_db(conn, cur, query)

        ### This extracts data to be used for the rest of the tables
        data = extract_data(copy_buffer)
        ### This cleans and formats the date time part of the data
        data = format_dates_in_csv(data)
        
        ### Whenever a new csv is uploaded, usually a new branch is added
        ### Which gets retrieved and loaded onto the table here
        branch_id = sql_utils.create_guid()
        row = data.iloc[0]
        branch_name = get_location(row)
        query = f"INSERT INTO branch (branch_id, branch_location) SELECT '{branch_id}', '{branch_name}' WHERE NOT EXISTS (SELECT 1 FROM branch WHERE branch_location = '{branch_name}')"
        sql_utils.load_data_onto_db(conn, cur, query)

        ### Ids of CASH and CARD are loaded onto the table which is referenced later by other tables
        method_id = sql_utils.create_guid()
        query = f"INSERT INTO payment_method (method_id, method) SELECT '{method_id}', 'CASH' WHERE NOT EXISTS (SELECT 1 FROM payment_method WHERE method = 'CASH')"
        sql_utils.load_data_onto_db(conn, cur, query)
        method_id = sql_utils.create_guid()
        query = f"INSERT INTO payment_method (method_id, method) SELECT '{method_id}', 'CARD' WHERE NOT EXISTS (SELECT 1 FROM payment_method WHERE method = 'CARD')"
        sql_utils.load_data_onto_db(conn, cur, query)

        ### for loop that links the data of the other tables into one transaction id
        for i in range(len(data)):
            transaction = data.iloc[i]
            transaction_id = sql_utils.create_guid()
            branch = get_location(transaction)
            datetime = extract_datetime(transaction)
            payment_method = load_payment_methods(transaction)
            products = load_ordered_products(transaction)
            query = f"INSERT INTO transaction_number (transaction_id, date_time, branch_id, method_id) SELECT '{transaction_id}', '{datetime}', b.branch_id, pm.method_id FROM branch b JOIN payment_method pm ON pm.method = '{payment_method}'WHERE b.branch_location = '{branch}'"
            sql_utils.load_data_onto_db(conn, cur, query)
            for product in products:
                query = f"INSERT INTO transactions (transaction_id, product_id) SELECT '{transaction_id}', p.product_id FROM product p WHERE p.product_name = '{product}'"
                sql_utils.load_data_onto_db(conn, cur, query)
            

        conn.commit()

        cur.close()
        conn.close()

        LOGGER.info(f"lambda_handler: done, file={file_path}")

    except Exception as err:
        LOGGER.error(f"lambda_handler: failure: error={err}, file={file_path}")
        raise err

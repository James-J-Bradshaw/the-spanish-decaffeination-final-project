import pandas as pd
import csv
from data_transformation import *
from database import Database

# db = Database()

# create_product_table = db.execute_query(
#     "CREATE TABLE IF NOT EXISTS product (product_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,product_name VARCHAR(100) NOT NULL,price REAL NOT NULL)"
# )
# create_branch_table = db.execute_query(
#     "CREATE TABLE IF NOT EXISTS branch (branch_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,branch_location VARCHAR(100) NOT NULL)"
# )
# create_payment_method_table = db.execute_query(
#     "CREATE TABLE IF NOT EXISTS payment_method (method_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,method VARCHAR(50))"
# )
# create_transaction_number_table = db.execute_query(
#     "CREATE TABLE IF NOT EXISTS transaction_number (transaction_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,date_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,branch_id UUID,method_id UUID,FOREIGN KEY(branch_id) REFERENCES branch(branch_id),FOREIGN KEY(method_id) REFERENCES payment_method(method_id))"
# )
# create_transactions_table = db.execute_query(
#     "CREATE TABLE IF NOT EXISTS transactions (transaction_id UUID,product_id UUID,FOREIGN KEY(transaction_id) REFERENCES transaction_number(transaction_id),FOREIGN KEY(product_id) REFERENCES product(product_id))"
# )
# create_report_table = db.execute_query(
#     "CREATE TABLE IF NOT EXISTS reports (report_id UUID DEFAULT gen_random_uuid() PRIMARY KEY, branch_id UUID,total_sales DECIMAL NOT NULL, total_transactions DECIMAL NOT NULL, date_generated TIMESTAMP WITHOUT TIME ZONE NOT NULL, FOREIGN KEY(branch_id) REFERENCES branch(branch_id));"
# )

original_csv = '../csv_data/uppingham.csv'
cleaned_csv = '../csv_data/transformed_data.csv'
formatted_csv = '../csv_data/transformed_data.csv'



clean_data_to_csv(original_csv, cleaned_csv)
format_dates_in_csv(cleaned_csv, formatted_csv, date_column_index=0)
data = format_dates_in_csv(cleaned_csv, formatted_csv, date_column_index=0)
print(data)

# db.close()

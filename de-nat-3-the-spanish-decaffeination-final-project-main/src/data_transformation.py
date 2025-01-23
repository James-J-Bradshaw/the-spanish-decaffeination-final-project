import pandas as pd
import csv
import re

# Function to extract relevant data from a CSV file
def extract_data(filename):
    data = pd.read_csv(
        filename,
        header=None,
        usecols=[0, 1, 3, 4, 5],
        names=["date_time", "branch", "order", "price", "method"],
    )
    return data

# Function to format the "date_time" column in the DataFrame
def format_dates_in_csv(data):
    data["date_time"] = pd.to_datetime(data["date_time"], errors="coerce").dt.strftime(
        "%m/%d/%Y %H:%M"
    )
    return data

# Function to extract the "branch" column from the DataFrame
def get_location(file):
    data = file["branch"]

    return data

# Function to extract the "date_time" column from the DataFrame
def extract_datetime(data):

    return data["date_time"]

# Function to extract the "method" (payment method) column from the DataFrame
def load_payment_methods(filename):
    payment_methods = filename["method"]

    return payment_methods

# Function to extract ordered product names from a CSV file
def load_ordered_products(filename):
    ordered_products = []
    ordered_product = filename["order"]
    # Split the 'order' column value by commas to get individual items
    orders = ordered_product.split(",")
    for order in orders:
        # Clean and format the order string
        order = order.replace(" - ", " ") # Replace " - " with a space
        order = order.strip() # Remove leading/trailing spaces
        # Use regex to separate product name and quantity/price
        match = re.match(r"([a-zA-Z& ]+)([0-9 .]+)", order, re.I)
        if match:
            order = match.groups() # Extract matched groups (name and quantity/price)
            ordered_products.append(order)
    # Convert tuples to mutable lists and extract product names only
    mutable_products = order_to_list(ordered_products)
    finished_product_names = product_name_only(mutable_products)

    return finished_product_names

# Helper function to convert tuples of product details into lists
def order_to_list(products):
    mutable_products = []
    for product in products:
        mutable_product = list(product)
        mutable_products.append(mutable_product)

    return mutable_products

# Helper function to extract product names only from a list of product details
def product_name_only(products):
    formatted_product_names = []
    for product in products:
        product_name = product[0]
        formatted_product_names.append(product_name)

    return formatted_product_names

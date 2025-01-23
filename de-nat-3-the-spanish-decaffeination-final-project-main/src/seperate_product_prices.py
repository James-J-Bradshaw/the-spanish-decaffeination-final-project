import re
from data_transformation import *


# Takes all products and their prices out of desired CSV
def load_products_and_price(filename):
    clean_products = []
    orders = []
    df = extract_data(filename)
    data = df.to_dict(orient="records")
    for purchase in data:
        order = purchase["order"]
        orders.append(order)

    # This for loop cleans any undesired characters from the list of orders
    for order in orders:
        order = order.replace(" - ", " ")
        products = order.split(",")
        for product in products:
            product = product.strip()
            match = re.match(r"([a-zA-Z& ]+)([0-9 .]+)", product, re.I)
            if match:
                product = match.groups()
                clean_products.append(product)
    products = no_dupe(clean_products)
    mutable_products = price_to_list(products)
    finished_products, finished_prices = price_to_float(mutable_products)

    return finished_products, finished_prices


# This function takes the list of products and prices and gets rid of any duplicates within the list
def no_dupe(clean_csv_dict):
    seen = set()
    unique_tuples = []
    for t in clean_csv_dict:
        if t not in seen:
            unique_tuples.append(t)
            seen.add(t)
    return unique_tuples


# Due to the library we use in this code (RE), it would turn our list of lists into a list of tuples, so this function just turns them back into lists
def price_to_list(products):
    mutable_products = []
    for product in products:
        mutable_product = list(product)
        mutable_products.append(mutable_product)

    return mutable_products


# This function splits the product name and price, and then formats the prices from strings into floats
def price_to_float(products):
    formatted_product_names = []
    formatted_prices = []
    for product in products:
        product_name = product[0]
        formatted_product_names.append(product_name)
        product_price = product[1]
        formatted_prices.append(product_price)

    for price in range(len(formatted_prices)):
        formatted_prices[price] = float(formatted_prices[price])

    return formatted_product_names, formatted_prices

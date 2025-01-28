from MySQLLoader import MySQLLoader
import os
import pandas as pd
from DataCleaner import DataCleaner

# Retrieve my password
with open('MySQL_password.txt', 'r') as file:
    pwd = file.readline().strip()

ml = MySQLLoader('root', pwd, 'marketdata')

# Create tables
target_tables = {
    'Customer':['CustomerId', 'FirstName', 'LastName', 'Email', 'Phone', 'Street', 'State', 
                'City', 'PostalCode', 'Gender', 'Occupation', 'IncomeLevel'],
    '`Order`':['OrderId', 'CustomerId', 'OrderDate'],
    'Sales':['SaleId', 'TransactionDate', 'TransactionTime', 'InvoiceNum', 
             'SalesChannel', 'QuantitySold', 'TotalAmount', 'CustomerId', 'ProductId'],
    'Purchase':['PurchaseId', 'ProductId', 'PurchaseDate', 'QuantityPurchased', 
                'PurchasePrice', 'SupplierName', 'SupplierContactInfo'],
    'Product':['ProductId', 'ProductName', 'SKU', 'Price', 'DiscountedPrice', 'BrandId', 
               'CategoryId'],
    'Category':['CategoryId', 'CategoryName'],
    'Brand':['BrandId', 'BrandName']
}

data_types = {
    'Customer':['CHAR(8)', 'VARCHAR(20)', 'VARCHAR(20)', 'VARCHAR(50)', 'VARCHAR(20)', 'VARCHAR(100)', 'CHAR(2)', 
                'VARCHAR(20)', 'INT', 'VARCHAR(6)', 'VARCHAR(20)', 'VARCHAR(20)'],
    '`Order`':['CHAR(10)', 'CHAR(8)', 'DATE'],
    'Sales':['CHAR(8)', 'DATETIME', 'TIME', 'CHAR(8)', 
             'VARCHAR(20)', 'INT', 'INT', 'Char(8)', 'CHAR(8)'],
    'Purchase':['CHAR(10)', 'CHAR(8)', 'DATETIME', 'INT', 
                'DECIMAL(8,2)', 'VARCHAR(50)', 'VARCHAR(100)'],
    'Product':['CHAR(8)', 'VARCHAR(50)', 'CHAR(12)', 'DECIMAL(8,2)', 'DECIMAL(8,2)', 'VARCHAR(10)', 
               'VARCHAR(10)'],
    'Category':['VARCHAR(10)', 'VARCHAR(10)'],
    'Brand':['VARCHAR(10)', 'VARCHAR(10)']
}

primary_keys = {
    'Customer':['CustomerId'],
    '`Order`':['OrderId'],
    'Sales':['SaleId'],
    'Purchase':['PurchaseId'],
    'Product':['ProductId'],
    'Category':['CategoryId'],
    'Brand':['BrandId']
}

'''
cus = pd.read_csv("filtered_data/('fashion_store_data_cleaned',)_filtered/Customer.csv", index_col=0)
print('Customer' in target_tables.keys())
'''

flag = True
if flag:
    for tb, col in target_tables.items():
        # Create empty table
        query = ml.create_table(tb, col, data_types[tb], primary_keys[tb], {})
        ml.execute_query(query)

        # Upload data
        if tb[0] == '`':
            tb = tb[1:-1]
        table_resource = pd.read_csv(
            f"filtered_data/('fashion_store_data_cleaned',)_filtered/{tb}.csv", 
            index_col=0
        )
        query = ml.upload_data(tb, col)
        for _, row in table_resource.iterrows():
            ml.execute_query(query, tuple(row), 'upload')

    ml.close_connect()

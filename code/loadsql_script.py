from MySQLLoader import MySQLLoader
import pandas as pd

# Retrieve my password
with open('MySQL_password.txt', 'r') as file:
    pwd = file.readline().strip()

ml = MySQLLoader('yuxuan', pwd, 'realworlddata', host='172.233.137.237')

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
    'Customer':['VARCHAR(25)', 'VARCHAR(100)', 'VARCHAR(100)', 'VARCHAR(100)', 'VARCHAR(100)', 'VARCHAR(100)', 
                'CHAR(2)', 'VARCHAR(100)', 'INT', 'VARCHAR(20)', 'VARCHAR(100)', 'VARCHAR(20)'],
    '`Order`':['VARCHAR(25)', 'VARCHAR(25)', 'DATE'],
    'Sales':['VARCHAR(25)', 'DATETIME', 'TIME', 'VARCHAR(50)', 
             'VARCHAR(20)', 'INT', 'INT', 'VARCHAR(25)', 'VARCHAR(25)'],
    'Purchase':['VARCHAR(25)', 'VARCHAR(25)', 'DATETIME', 'INT', 
                'DECIMAL(8,2)', 'VARCHAR(50)', 'VARCHAR(100)'],
    'Product':['VARCHAR(25)', 'VARCHAR(50)', 'CHAR(12)', 'DECIMAL(8,2)', 'DECIMAL(8,2)', 'VARCHAR(25)', 
               'VARCHAR(25)'],
    'Category':['VARCHAR(25)', 'VARCHAR(20)'],
    'Brand':['VARCHAR(25)', 'VARCHAR(20)']
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

fk = {
    'Customer':{},
    '`Order`':{'CustomerId':'Customer'},
    'Sales':{'CustomerId':'Customer', 'ProductId':'Product'},
    'Purchase':{'ProductId':'Product'},
    'Product':{'BrandId':'Brand', 
               'CategoryId':'Category'},
    'Category':{},
    'Brand':{}
}


## --- Main Function ---
# Sort creation order to prioritize root tables
sorted_tables = ['Customer', 'Category', 'Brand', '`Order`', 'Product', 'Purchase', 'Sales']
folder = 'clea_filtered'

for tb in sorted_tables:
    # Create empty table
    query = ml.create_table(tb, target_tables[tb], data_types[tb], primary_keys[tb], fk[tb])
    ml.execute_query(tb, query)

    # Upload data
    if tb[0] == '`':
        tb_name = tb[1:-1]
    else:
        tb_name = tb

    table_resource = pd.read_csv(f"filtered_data/{folder}/{tb_name}.csv")
    query = ml.upload_data(tb, target_tables[tb])
    tuple_list = [tuple(None if pd.isna(x) else x for x in row) for row in table_resource.itertuples(index=False, name=None)]
    ml.execute_query(tb, query, tuple_list, 'upload')

ml.close_connect()

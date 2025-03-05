import sys
import pandas as pd
from MySQLLoader import MySQLLoader

# Ensure a file path is provided from `app.py`
if len(sys.argv) < 2:
    print("No file path provided.")
    sys.exit(1)

filtered_file_path = sys.argv[1]  # Get the filtered CSV file path from `app.py`
table_name = filtered_file_path.split('/')[-1].replace('_filtered.csv', '')  # Extract table name

# Connect to MySQL
try:
    with open('MySQL_password.txt', 'r') as file:
        pwd = file.readline().strip()
    ml = MySQLLoader('yuxuan', pwd, 'marketdata', host='172.233.137.237')
except Exception as e:
    print(f"Error connecting to MySQL: {e}")
    sys.exit(1)

# Read the CSV file
try:
    df = pd.read_csv(filtered_file_path)
    if df.empty:
        print(f"Warning: {filtered_file_path} is empty. No data to upload.")
        sys.exit(1)
except Exception as e:
    print(f"Error reading {filtered_file_path}: {e}")
    sys.exit(1)

# Define all possible table schemas
table_definitions = {
    'Customer': (['CustomerId', 'FirstName', 'LastName', 'Email', 'Phone', 'Street', 'State', 
                  'City', 'PostalCode', 'Gender', 'Occupation', 'IncomeLevel'],
                 ['VARCHAR(25)', 'VARCHAR(100)', 'VARCHAR(100)', 'VARCHAR(100)', 'VARCHAR(100)', 
                  'VARCHAR(100)', 'CHAR(2)', 'VARCHAR(100)', 'INT', 'VARCHAR(15)', 'VARCHAR(100)', 'VARCHAR(20)'],
                 ['CustomerId'], {}),

    '`Order`': (['OrderId', 'CustomerId', 'OrderDate'],
                ['VARCHAR(25)', 'VARCHAR(25)', 'DATE'],
                ['OrderId'], {'CustomerId': 'Customer'}),

    'Sales': (['SaleId', 'TransactionDate', 'TransactionTime', 'InvoiceNum', 
               'SalesChannel', 'QuantitySold', 'TotalAmount', 'CustomerId', 'ProductId'],
              ['VARCHAR(25)', 'DATETIME', 'TIME', 'CHAR(8)', 
               'VARCHAR(20)', 'INT', 'DECIMAL(8,2)', 'VARCHAR(25)', 'VARCHAR(25)'],
              ['SaleId'], {'CustomerId': 'Customer', 'ProductId': 'Product'}),

    'Purchase': (['PurchaseId', 'ProductId', 'PurchaseDate', 'QuantityPurchased', 
                  'PurchasePrice', 'SupplierName', 'SupplierContactInfo'],
                 ['VARCHAR(25)', 'VARCHAR(25)', 'DATETIME', 'INT', 
                  'DECIMAL(8,2)', 'VARCHAR(50)', 'VARCHAR(100)'],
                 ['PurchaseId'], {'ProductId': 'Product'}),

    'Product': (['ProductId', 'ProductName', 'SKU', 'Price', 'DiscountedPrice', 'BrandId', 'CategoryId'],
                ['VARCHAR(25)', 'VARCHAR(50)', 'CHAR(12)', 'DECIMAL(8,2)', 'DECIMAL(8,2)', 'INT', 'INT'],
                ['ProductId'], {'BrandId': 'Brand', 'CategoryId': 'Category'}),

    'Category': (['CategoryId', 'CategoryName'],
                 ['INT', 'VARCHAR(20)'],
                 ['CategoryId'], {}),

    'Brand': (['BrandId', 'BrandName'],
              ['INT', 'VARCHAR(20)'],
              ['BrandId'], {})
}

# Check if the table exists, if not, create it
if table_name in table_definitions:
    columns, datatypes, primary_key, foreign_keys = table_definitions[table_name]
    
    if not ml.check_table_exists(table_name):
        create_query = ml.create_table(table_name, columns, datatypes, primary_key, foreign_keys)
        try:
            ml.execute_query(table_name, create_query, execution_type='create')
            print(f"Table '{table_name}' created successfully.")
        except Exception as e:
            print(f"Error creating table '{table_name}': {e}")
            sys.exit(1)
else:
    print(f"Table definition for '{table_name}' is missing.")
    sys.exit(1)

# Upload data to MySQL
try:
    query = ml.upload_data(table_name, df.columns.tolist())
    tuple_list = [tuple(row) for row in df.itertuples(index=False, name=None)]
    
    ml.execute_query(table_name, query, tuple_list, 'upload')
    print(f"Successfully uploaded data to table '{table_name}'.")
except Exception as e:
    print(f"Error uploading data to MySQL: {e}")
    sys.exit(1)

# Close the MySQL connection
ml.close_connect()

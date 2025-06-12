import mysql.connector
import pandas as pd
from faker import Faker
import random
from datetime import datetime
fake = Faker()
class MySQLLoader:
    def __init__(self, db_config, db_name='realworlddata'):
        self.db_name = db_name
        try:
            self.conn = mysql.connector.connect(**db_config)
            self.cursor = self.conn.cursor()
            print("MySQL connected.")
            # Recreate database fresh
            self.cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
            self.cursor.execute(f"CREATE DATABASE {db_name}")
            self.cursor.execute(f"USE {db_name}")
        except mysql.connector.Error as e:
            print(f"Error: {e}")
            self.conn = None
            self.cursor = None
    def create_table(self, table_name, columns, datatypes, primary_key, foreign_keys):
        if len(columns) != len(datatypes):
            raise ValueError("Columns and datatypes count mismatch.")
        query = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
        for col, dtype in zip(columns, datatypes):
            query += f"  {col} {dtype},\n"
        pk = ", ".join(primary_key)
        query += f"  PRIMARY KEY ({pk})"
        if foreign_keys:
            for fk_col, ref_table in foreign_keys.items():
                query += f",\n  FOREIGN KEY ({fk_col}) REFERENCES {ref_table}({fk_col})"
        query += "\n);"
        print(f"Creating table {table_name}:\n{query}\n")
        self.cursor.execute(query)
    def insert_data(self, table_name, columns, data):
        placeholders = ", ".join(["%s"] * len(columns))
        cols = ", ".join(columns)
        query = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
        self.cursor.executemany(query, data)
        self.conn.commit()
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Connection closed.")
def max_len_in_column(df, col):
    return df[col].dropna().astype(str).map(len).max()
# --- Configuration ---
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'port': 1001,
}
N_CUSTOMERS = 1000
N_CATEGORIES = 20
N_BRANDS = 20
N_PRODUCTS = 1000
N_ORDERS = 1000
N_PURCHASES = 1000
N_SALES = 1000

category_ids = [fake.uuid4() for _ in range(N_CATEGORIES)]
brand_ids = [fake.uuid4() for _ in range(N_BRANDS)]
customer_ids = [fake.uuid4() for _ in range(N_CUSTOMERS)]
product_ids = [fake.uuid4() for _ in range(N_PRODUCTS)]

tables = {
    'Customer': {
        'columns': ['CustomerId', 'FirstName', 'LastName', 'Email', 'Phone', 'Street', 'State',
                    'City', 'PostalCode', 'Gender', 'Occupation', 'IncomeLevel'],
        'datatypes': ['VARCHAR(50)', 'VARCHAR(100)', 'VARCHAR(100)', 'VARCHAR(100)', 'VARCHAR(100)', 'VARCHAR(100)',
                    'CHAR(2)', 'VARCHAR(100)', 'INT', 'VARCHAR(20)', 'VARCHAR(100)', 'VARCHAR(20)'],
        'primary_key': ['CustomerId'],
        'foreign_keys': {}
    },
    'Category': {
        'columns':['CategoryId', 'CategoryName'],
        'datatypes':['VARCHAR(50)', 'VARCHAR(20)'],
        'primary_key': ['CategoryId'],
        'foreign_keys': {}
    },
    'Brand': {
        'columns' :['BrandId', 'BrandName'],
        'datatypes' :['VARCHAR(100)', 'VARCHAR(50)'],
        'primary_key': ['BrandId'],
        'foreign_keys': {}
    },
    'Product': {
        'columns':['ProductId', 'ProductName', 'SKU', 'Price', 'DiscountedPrice', 'BrandId',
                'CategoryId'],
        'datatypes':['VARCHAR(50)', 'VARCHAR(50)', 'CHAR(12)', 'DECIMAL(8,2)', 'DECIMAL(8,2)', 'VARCHAR(50)',
                'VARCHAR(50)'],
        'primary_key': ['ProductId'],
        'foreign_keys': {'BrandId': 'Brand',
                'CategoryId': 'Category'}
    },
    '`Order`': {
        'columns' : ['OrderId', 'CustomerId', 'OrderDate'],
        'datatypes' : ['VARCHAR(50)', 'VARCHAR(50)', 'VARCHAR(50)'],
        'primary_key':  ['OrderId'],
        'foreign_keys': {'CustomerId': 'Customer'}
    },
    'Sales': {
        'columns' :['SaleId', 'TransactionDate', 'TransactionTime', 'InvoiceNum',
                'SalesChannel', 'QuantitySold', 'TotalAmount', 'CustomerId', 'ProductId'],
        'datatypes' : ['VARCHAR(50)', 'DATE', 'TIME', 'VARCHAR(50)',
                    'VARCHAR(50)', 'INT', 'DECIMAL(10,2)', 'VARCHAR(50)', 'VARCHAR(50)'],
        'primary_key': ['SaleId'],
        'foreign_keys': {'CustomerId': 'Customer', 'ProductId': 'Product'}
    },
    'Purchase': {
        'columns':['PurchaseId', 'ProductId', 'PurchaseDate', 'QuantityPurchased',
                'PurchasePrice', 'SupplierName', 'SupplierContactInfo'],
        'datatypes':['VARCHAR(50)', 'VARCHAR(50)', 'DATETIME', 'INT',
                'DECIMAL(8,2)', 'VARCHAR(50)', 'VARCHAR(100)'],
        'primary_key': ['PurchaseId'],
        'foreign_keys': {'ProductId': 'Product'}
    },
}
id_map = {
    'Category': [(cid, fake.word().capitalize()) for cid in category_ids],
    'Brand': [(bid, fake.company()) for bid in brand_ids],
    'Customer': [
        (cid, fake.first_name(), fake.last_name(), fake.email(), fake.phone_number(),
        fake.street_address(), fake.state_abbr(), fake.city(), fake.random_int(10000, 99999),
        random.choice(['Male', 'Female', 'Other']), fake.job(), random.choice(['Low', 'Medium', 'High']))
        for cid in customer_ids
    ],
    'Product': [
        (pid, fake.word().capitalize(), fake.bothify(text='???-########'),
        round(random.uniform(100, 1000), 2), round(random.uniform(50, 999), 2),
        random.choice(brand_ids), random.choice(category_ids))
        for pid in product_ids
    ],
    '`Order`': [
        (fake.uuid4(), random.choice(customer_ids), fake.date())
        for _ in range(N_ORDERS)
    ],
    'Purchase': [
        (fake.uuid4(), random.choice(product_ids), fake.date_time_this_decade(),
        random.randint(1, 50), round(random.uniform(100, 1000), 2),
        fake.company(), fake.phone_number())
        for _ in range(N_PURCHASES)
    ],
    'Sales': [
        (fake.uuid4(), fake.date(), fake.time(), fake.bothify(text='INV#######'),
        random.choice(['Online', 'Retail']), random.randint(1, 10),
        round(random.uniform(100, 5000), 2), random.choice(customer_ids),
        random.choice(product_ids))
        for _ in range(N_SALES)
    ]
}
# Create and populate tables
loader = MySQLLoader(db_config)
for table_name, info in tables.items():
    loader.create_table(table_name, info['columns'], info['datatypes'], info['primary_key'], info['foreign_keys'])
    data = id_map[table_name]
    loader.insert_data(table_name, info['columns'], data)
    print(f"Fake data inserted into {table_name}")
loader.close()

import os
import sys
from ColumnFilter import ColumnFilter
'''
# Ensure a file path is provided
if len(sys.argv) < 2:
    print("No file path provided.")
    sys.exit(1)

# Normalize file path (cross-platform)
file_path = os.path.normpath(sys.argv[1])
'''

def __list_csv_files(folder_path:str)->list[str]:
    csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]
    return csv_files

file_path = "cleaned_data"
print(f"Reading files from {file_path}...")

# Extract folder name for filtered output
FILTERED_FOLDER = "filtered_data"
os.makedirs(FILTERED_FOLDER, exist_ok=True)

# Initialize ColumnFilter with target table schema
cf = ColumnFilter(
    dfs=__list_csv_files(file_path),
    target_tables={
        'Customer':['CustomerId', 'FirstName', 'LastName', 'Email', 'Phone', 'Street', 'State',
                    'City', 'PostalCode', 'Gender', 'Occupation', 'IncomeLevel'],
        'Order':['OrderId', 'CustomerId', 'OrderDate'],
        'Sales':['SaleId', 'TransactionDate', 'TransactionTime', 'InvoiceNum',
                 'SalesChannel', 'QuantitySold', 'TotalAmount', 'CustomerId', 'ProductId'],
        'Purchase':['PurchaseId', 'ProductId', 'PurchaseDate', 'QuantityPurchased',
                    'PurchasePrice', 'SupplierName', 'SupplierContactInfo'],
        'Product':['ProductId', 'ProductName', 'SKU', 'Price', 'DiscountedPrice', 'BrandId',
                   'CategoryId'],
        'Category':['CategoryId', 'CategoryName'],
        'Brand':['BrandId', 'BrandName']
    },
)

# Apply filtering logic to keep only matching columns
# try:
cf.filter_cols(local=True)
print("Filtering completed and saved to 'filtered_data' folder.")
'''
except Exception as e:
    print(f"Filtering failed: {e}")
    sys.exit(1)
'''
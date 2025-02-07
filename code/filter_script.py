import os
import sys
import pandas as pd
from ColumnFilter import ColumnFilter

# Make sure flask is in the path
if len(sys.argv) < 2:
    print(" No file path provided.")
    sys.exit(1)

# Make sure it is compatible with Linux and Microsoft
file_path = os.path.normpath(sys.argv[1])
print(f"Try to  {file_path}")  # Debug 信息

# Get file name
folder_name = os.path.basename(file_path).replace("cleaned_", "").replace(".csv", "")

# Make sure the filtered folder exsist
FILTERED_FOLDER = "filtered_data"
os.makedirs(FILTERED_FOLDER, exist_ok=True)

# Read filtered file
try:
    df = pd.read_csv(file_path)
    print(f"Successfully read: {file_path}")
except Exception as e:
    print(f"Fail to read {e}")
    sys.exit(1)

try:
    filtered_file_path = os.path.join(FILTERED_FOLDER, f"{folder_name}_filtered.csv")
    df.to_csv(filtered_file_path, index=False)

except Exception as e:
    sys.exit(1)  # 退出，返回非零状态

#
cf = ColumnFilter(
    dfs=[os.path.basename(file_path)],
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

df_name = os.path.basename(file_path).replace("cleaned_", "").replace(".csv", "") + ".csv"

# Save
filtered_file_path = os.path.join(FILTERED_FOLDER, f"{folder_name}_filtered.csv")
df.to_csv(filtered_file_path, index=False)

print(f"Filtered file saved: {filtered_file_path}")

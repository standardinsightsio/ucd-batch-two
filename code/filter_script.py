import os
from ColumnFilter import ColumnFilter

# Retrieve my API
with open('gemini_api.txt', 'r') as file:
    api_key = file.readline().strip()

# Filter columns
for subdir, _, files in os.walk('cleaned_data'):
    folder_name = os.path.basename(subdir)
    if len(files) == 0:
        continue
    cf = ColumnFilter(
        folder = folder_name,
        dfs=files, 
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
        api_key=api_key
    )
    cf.filter_cols()
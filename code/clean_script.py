import os
import pandas as pd
from DataCleaner import DataCleaner
import warnings
warnings.filterwarnings('ignore')

# Retrieve my API
with open('gemini_api.txt', 'r') as file:
    api_key = file.readline().strip()

# Clean data
for subdir, _, files in os.walk('raw_data'):
    folder_name = os.path.basename(subdir)
    if len(files) == 0:
        continue
    for f in files:
        cleaner = DataCleaner(pd.read_csv(f'raw_data/{folder_name}/{f}'), api_key)

        # cleaning process
        cleaner.handle_missing_data()
        cleaner.handle_duplicates()
        cleaner.break_values()
        cleaner.break_values(breaker='address')

        # Save cleaned data
        os.makedirs(f'cleaned_data/{folder_name}_cleaned', exist_ok=True)
        cleaner.save_to_csv(f"cleaned_{f}", path=f"cleaned_data/{folder_name}_cleaned/")


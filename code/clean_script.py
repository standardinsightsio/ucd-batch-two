import os
import pandas as pd
from DataCleaner import DataCleaner
import warnings

warnings.filterwarnings('ignore')
CLEANED_FOLDER = "cleaned_data"
os.makedirs(CLEANED_FOLDER, exist_ok=True)


def clean_uploaded_file(file_path:str, cleaned_filename:str, info_break:bool=True)->str:
    # Read file
    if file_path[-3:] == 'csv':
        df = pd.read_csv(file_path)
    elif file_path[-4:] == 'xlsx':
        df = pd.read_excel(file_path, sheet_name='Sheet1')

    # Create an instance of the DataCleaner class
    cleaner = DataCleaner(df)

    # Clean the data
    cleaner.handle_missing_data()
    cleaner.handle_duplicates()
    if info_break:
        cleaner.break_values()
        cleaner.break_values(breaker='address')

    # Create file path
    cleaned_path = os.path.join(CLEANED_FOLDER, cleaned_filename)

    # Save cleaned file
    cleaner.save_to_csv(cleaned_filename, path=CLEANED_FOLDER)

    return cleaned_path



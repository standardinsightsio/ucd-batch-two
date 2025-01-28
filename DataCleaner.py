import pandas as pd
import os
from typing import Literal
import google.generativeai as genai

class DataCleaner:
    def __init__(self, df:pd.DataFrame, api_key:str, model=genai.GenerativeModel("gemini-pro")):
        self.df = df
        self.length = len(df)
        genai.configure(api_key=api_key)
        self.model = model

    # Generate the prompt for value break
    def __gen_prompt(self, val:str) -> str:
        text1 = 'Below is an American address:\n'
        text2 = '''
        \nBreak it into street, city, state, and postal code. 
        respond me with a single list of [street, city, state, postal code]
        e.g.: input: 2397 Janet Mountain Apt. 508, Donaldhaven, ID 47928
        output: ['2397 Janet Mountain Apt. 508', 'Donaldhaven', 'ID', '47928']
        '''
        return text1 + val + text2
    
    # Prompt to the LLM
    def __ask(self, prompt:str) -> str:
        response = self.model.generate_content(contents=prompt)
        return response.text


    # Deal with null values
    def handle_missing_data(self, strategy: str = 'drop', column: list[str] = None, value: list = None):
        if strategy == 'drop':
            self.df = self.df.dropna(subset=column) if column else self.df.dropna()
        elif strategy == 'fill' and column:
            for col, val in zip(column, value):
                if col in self.df.columns:
                    self.df[col] = self.df[col].fillna(val)
        return self

    # Deal with inconsistent values
    def correct_inconsistent_data(self, column: str, mapping_dict: dict):
        if column in self.df.columns:
            self.df[column] = self.df[column].str.lower()
            self.df[column] = self.df[column].replace(mapping_dict)
        return self

    # Deal with incorrect datatypes
    def correct_data_types(self, column: str = None, dtype: Literal['datetime', 'category', 'numeric'] = None):
        if dtype == 'datetime' and column is None:
            for col in self.df.select_dtypes(include=['object']).columns:
                if 'date' in col.lower() or 'time' in col.lower():
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                    print(f"Converted '{col}' to datetime.")
        elif column in self.df.columns:
            if dtype == 'datetime':
                self.df[column] = pd.to_datetime(self.df[column], errors='coerce')
            elif dtype == 'category':
                self.df[column] = self.df[column].astype('category')
            elif dtype == 'numeric':
                self.df[column] = pd.to_numeric(self.df[column], errors='coerce')
        else:
            print(f"Warning: Column '{column}' not found in DataFrame.")
        return self

    # Deal with duplicated values
    def handle_duplicates(self, column: list[str] = None):
        self.df = self.df.drop_duplicates(subset=column) if column else self.df.drop_duplicates()
        return self

    # Deal with outliers
    def handle_outliers(self, column: str, method: str = 'iqr'):
        if method == 'iqr':
            Q1 = self.df[column].quantile(0.25)
            Q3 = self.df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            self.df = self.df[~((self.df[column] < lower_bound) | (self.df[column] > upper_bound))]
        elif method == 'clip':
            lower_cap = self.df[column].quantile(0.05)
            upper_cap = self.df[column].quantile(0.95)
            self.df[column] = self.df[column].clip(lower_cap, upper_cap)
        return self
    
    # Break mixed data
    def break_values(self, breaker:str='name'):
        if breaker == 'name':
            column_to_break = [col for col in self.df.columns if 'full' in col.lower() and 'name' in col.lower()]
            if column_to_break:
                col_name = column_to_break[0]
                self.df[['FirstName', 'LastName']] = self.df[col_name].str.split(' ', 1, expand=True)
                # Drop the original column
                self.df.drop(columns=[col_name], inplace=True)
            else:
                pass

        elif breaker == 'address':
            column_to_break = [col for col in self.df.columns if 'address' in col.lower() and 'email' not in col.lower()]
            if column_to_break:
                col_name = column_to_break[0]
                temp = self.df[col_name].str.slice(0, -9).str.rstrip(',')
                self.df[['Street', 'City']] = (
                    temp.str.rsplit(',', n=1, expand=True)
                    .apply(lambda col: col.str.strip())
                )
                self.df['State'] = self.df[col_name].str.slice(-8, -6)
                self.df['PostalCode'] = self.df[col_name].str.slice(-5)
                    
                # Drop the original column
                self.df.drop(columns=[col_name], inplace=True)
            else:
                pass

    # Return the cleaned table
    def get_cleaned_data(self):
        return self.df

    # Save data to local
    def save_to_csv(self, filename: str, path: str = None):
        if path:
            self.df.to_csv(os.path.join(path, filename), index=False)
        else:
            self.df.to_csv(filename, index=False)

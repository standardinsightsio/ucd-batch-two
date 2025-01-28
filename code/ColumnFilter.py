import numpy as np
import pandas as pd
import os
import random
import google.generativeai as genai

class ColumnFilter:
    def __init__(
            self, 
            folder:str,
            dfs:list[str],
            target_tables:dict,
            api_key:str, 
            model=genai.GenerativeModel("gemini-pro")
        ):
        genai.configure(api_key=api_key)
        self.df_names = dfs
        self.__folder_name = folder,
        self.__dfs = {name: pd.read_csv(f'cleaned_data/{folder}/{name}') for name in dfs}
        self.df_count = len(dfs)
        self.model = model
        self.__target_tables = target_tables
    
    # Retrieve column names of the table
    def get_cols(self) -> dict:
        samples = {}
        for df_name, df in self.__dfs.items():
            lists = df.columns.tolist()

            # Grab sample data for detection
            for c_name in lists:
                raw_sample_data = df[c_name].sample(n=10)
                sample_data = []

                # Mask sensitive information
                if 'address' in c_name.lower() or 'phone' in c_name.lower() or 'mail' in c_name.lower():
                    for s_data in raw_sample_data:
                        # Randomly select 8 unique indices
                        indices_to_mask = random.sample(range(len(s_data)), 10)
                        str_list = list(s_data)
                        # Replace selected indices with 'x'
                        for idx in indices_to_mask:
                            str_list[idx] = 'x'
                        sample_data.append(''.join(str_list))
                else:
                    sample_data = raw_sample_data.tolist()

                samples[c_name] = str(sample_data)
        return samples
    
    # Quick selection of the columns (based on word similarity)
    def similarity_match(self, colnames:list[str])->dict:
        matched_cols = {}

        for df, cols in self.__target_tables.items():
            col_rst = []
            for std_c in cols:
                std_c_ = std_c.lower()
                flag = False
                for c in colnames:
                    c_ = c.lower().strip().replace(' ', '')
                    if 'id' in std_c_:
                        if (std_c_ in c_ or c_ in std_c_) and ('id' in c_):
                            flag = True
                            break
                    else:
                        if std_c_ in c_ or c_ in std_c_:
                            flag = True
                            break
                if flag:
                    col_rst.append(c)
                else:
                    col_rst.append(f'{std_c}_null')

            matched_cols[df] = col_rst
        return matched_cols
    
    # Output the filtered data
    def __store_tables(self, tables:dict[str, pd.DataFrame]):
        os.makedirs(f'filtered_data/{self.__folder_name[0]}_filtered', exist_ok=True)
        for tb_name, tb in tables.items():
            tb.to_csv(f'filtered_data/{self.__folder_name[0]}_filtered/'+tb_name+'.csv')

    # Change dictionary into dataframe
    def __dict_to_df(self, dictionary:dict[str, pd.DataFrame])->pd.DataFrame:
        table = {'table':[], 'colname':[]}
        for k, v in dictionary.items():
            for i in v.columns:
                table['table'].append(k)
                table['colname'].append(i)
        return pd.DataFrame(table).set_index('colname')

    # Filter data
    def filter_cols(self, local:bool=True):
        result_set = {}
        samples = self.get_cols()
        selected = self.similarity_match(list(samples.keys()))

        # Label the columns
        col_df = {}
        for dfn, data in self.__dfs.items():
            for c_name in data.columns:
                if c_name not in col_df.keys():
                    col_df[c_name] = dfn

        for sel_df, sel_col in selected.items():
            filtered_cols = pd.DataFrame([])
            for i in range(len(sel_col)):
                col = sel_col[i]
                std_col = self.__target_tables[sel_df][i]
                if 'null' in col:
                    filtered_cols[col[:-5]] = np.nan
                else:
                    filtered_cols[std_col] = self.__dfs[col_df[col]][col]
            result_set[sel_df] = filtered_cols

        if local:
            self.__store_tables(result_set)
import numpy as np
import pandas as pd
import os
import google.generativeai as genai

class ColumnFilter:
    def __init__(
            self, 
            folder:str,
            dfs:list[str],
            target_tables:dict[str, list[str]],
            api_key:str, 
            model=genai.GenerativeModel("gemini-pro")
        ):
        genai.configure(api_key=api_key)
        self.__api_key = api_key
        self.df_names = dfs
        self.__folder_name = folder
        self.__dfs = {name: pd.read_csv(f'cleaned_data/{folder}/{name}') for name in dfs}
        self.df_count = len(dfs)
        self.model = model
        self.__target_tables = target_tables
    
    # Retrieve column names of the table
    def get_cols(self) -> pd.DataFrame:
        c_names = []
        df_names = []
        for df_name, df in self.__dfs.items():
            lists = df.columns.tolist()
            c_names += lists
            df_names += [df_name] * len(lists)
        return pd.DataFrame({'colname':c_names, 'dfname':df_names})
    
    # Quick selection of the columns (based on word similarity)
    def similarity_match(self, colnames:list[str])->dict[str, list[str]]:
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
                    if 'id' in std_c_:
                        col_rst.append(f'{std_c}_idnull')
                    else:
                        col_rst.append(f'{std_c}_null')

            matched_cols[df] = col_rst
        return matched_cols
    
    # Output the filtered data
    def __store_tables(self, tables:dict[str, pd.DataFrame]):
        os.makedirs(f'filtered_data/{self.__folder_name}_filtered', exist_ok=True)
        for tb_name, tb in tables.items():
            tb.to_csv(f'filtered_data/{self.__folder_name}_filtered/'+tb_name+'.csv')

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
        colndf = self.get_cols()
        selected = self.similarity_match(colndf['colname'].unique().tolist())

        for sel_df, sel_col in selected.items():
            filtered_cols = pd.DataFrame([])
            marker = False

            for i in range(len(sel_col)):
                col = sel_col[i]
                std_col = self.__target_tables[sel_df][i]
                if '_null' in col:
                    filtered_cols[col[:-5]] = None
                elif '_idnull' in col:
                    other_not_null = [s for s in selected[col[:-9]] if "null" not in s]
                    # Implement marker (related dataframe) if not yet
                    if not marker:
                        marker = colndf.loc[colndf['colname'].isin(other_not_null), 'dfname'].iloc[0]
                    filtered_cols[col[:-7]] = self.__dfs[marker][other_not_null].apply(tuple, axis=1).factorize()[0]
                else:
                    # Match column length
                    if len(filtered_cols) == 0:
                        marker = colndf.loc[colndf['colname']==col, 'dfname'].iloc[0]

                    filtered_cols[std_col] = self.__dfs[marker][col]

            # Check duplication
            filtered_cols.drop_duplicates(inplace=True)

            # Fill id column
            if filtered_cols.iloc[:, 0].isna().all():
                filtered_cols.iloc[:, 0] = filtered_cols.index

            result_set[sel_df] = filtered_cols

        if local:
            self.__store_tables(result_set)
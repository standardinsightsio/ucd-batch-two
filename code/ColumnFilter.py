import pandas as pd
import os


class ColumnFilter:
    def __init__(
            self,
            dfs: list[str],
            target_tables: dict
    ):
        self.df_names = dfs
        self.__dfs = {
            os.path.basename(name).replace("cleaned_", "").replace(".csv", "") + ".csv":
            pd.read_csv(os.path.join("cleaned_data", name))
            for name in dfs
        }
        self.df_count = len(dfs)
        self.__target_tables = target_tables

    # Get column name
    def get_cols(self) -> dict:
        column_samples = {}
        for df_name, df in self.__dfs.items():
            column_samples[df_name] = df.columns.tolist()
        return column_samples

    # Find match column
    def similarity_match(self, colnames: list[str]) -> dict:
        matched_cols = {}

        for df, expected_cols in self.__target_tables.items():
            matched = []
            for expected_col in expected_cols:
                found = None
                for col in colnames:
                    if expected_col.lower() == col.lower():
                        found = col
                        break
                matched.append(found if found else f'{expected_col}_null')
            matched_cols[df] = matched

        return matched_cols

    # Save filtered table
    def __store_tables(self, tables: dict[str, pd.DataFrame]):
        filtered_folder = f'filtered_data/{self.__folder_name}_filtered'
        os.makedirs(filtered_folder, exist_ok=True)
        for table_name, table in tables.items():
            table.to_csv(f'{filtered_folder}/{table_name}.csv', index=False)

    # Filter table
    def filter_cols(self, local: bool = True):
        result_set = {}
        column_samples = self.get_cols()

        for df_name, col_names in column_samples.items():
            selected_columns = self.similarity_match(col_names)
            print("Available keys in self.__dfs:", list(self.__dfs.keys()))
            print("Requested df_name:", df_name)
            print(f"Checking df_name existence: '{df_name}' in {list(self.__dfs.keys())}")
            print(f"df_name exact match: {df_name == list(self.__dfs.keys())[0]}")
            print(f"df_name repr: {repr(df_name)}")
            filtered_df = self.__dfs[df_name][[col for col in selected_columns[df_name] if 'null' not in col]]
            result_set[df_name] = filtered_df

        if local:
            self.__store_tables(result_set)

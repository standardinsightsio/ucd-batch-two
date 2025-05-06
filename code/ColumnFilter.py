import pandas as pd
import os


class ColumnFilter:
    def __init__(
            self,
            dfs: list[str],
            target_tables: dict[str, list[str]]
    ):
        self.df_names = dfs
        self.__folder_name = dfs[0][:4]
        self.__dfs = {
            os.path.basename(name):
            pd.read_csv(os.path.join("cleaned_data", name))
            for name in dfs
        }
        self.df_count = len(dfs)
        self.__target_tables = target_tables

    # Get column name
    def get_cols(self) -> list[tuple[str]]:
        column_samples = []
        for df_name, df in self.__dfs.items():
            col_list = df.columns.tolist()
            column_samples.extend(zip(col_list, [df_name]*len(col_list)))
        return column_samples

    # Find match column
    def similarity_match(self, colnames: list[tuple[str]]) -> dict[tuple[str], list[str]]:
        def __similarity(s1: str, s2: str) -> float:
            """
            Strict similarity: only considers the longest consecutive matching substring.
            Returns a ratio based on the length of the longest common substring 
            over the average string length.
            """
            len1, len2 = len(s1), len(s2)
            matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]
            longest = 0

            for i in range(len1):
                for j in range(len2):
                    if s1[i] == s2[j]:
                        matrix[i+1][j+1] = matrix[i][j] + 1
                        longest = max(longest, matrix[i+1][j+1])

            avg_len = (len1 + len2) / 2
            return longest / avg_len if avg_len else 0.0

        matched_cols = {}
        
        for df, expected_cols in self.__target_tables.items():
            matched = []
            label = None  # Label the matching table
            for expected_col in expected_cols:
                found = None
                for col in colnames:
                    sub_col = col[0].lower().replace('item', 'product')
                    if expected_col.lower() == sub_col and (not label or col[1]==label):
                        found = col[0]
                        break
                if found:
                    if not label: label = col[1]
                    matched.append(found if found else f'{expected_col}_null')
                    continue

                for col in colnames:
                    sub_col = col[0].lower().replace('item', 'product')
                    if 'id' in expected_col.lower() and __similarity(
                        expected_col.lower(), sub_col
                    ) >= 0.5 and (
                        'id' in sub_col or 'number' in sub_col
                    ) and (not label or col[1]==label):
                        found = col[0]
                        break
                if found:
                    if not label: label = col[1]
                    matched.append(found if found else f'{expected_col}_null')
                    continue
                
                for col in colnames:
                    sub_col = col[0].lower().replace('item', 'product')
                    if (
                        __similarity(expected_col.lower(), sub_col) >= 0.5 \
                        or expected_col.lower() in sub_col \
                        or sub_col in expected_col.lower() \
                    ) and (not label or col[1]==label):
                        found = col[0]
                        break
                if not label: label = col[1]
                matched.append(found if found else f'{expected_col}_null')

            matched_cols[(df, label)] = matched

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

        selected_columns = self.similarity_match(column_samples)
        for df_pair, f_col in selected_columns.items():
            source = self.__dfs[df_pair[1]]
            this_table = pd.DataFrame()
            for i, f in enumerate(f_col):
                if f in source.columns:
                    new_column = pd.DataFrame({self.__target_tables[df_pair[0]][i]:source[f]})
                    this_table = pd.concat([this_table, new_column], axis=1)
                else:
                    this_table = pd.concat(
                        [this_table, pd.DataFrame({f[:-5]: [None]*len(source)})], 
                        axis=1
                    )

            # Handle missing id
            if this_table.iloc[0, 0]:
                # Handle duplications
                this_table.drop_duplicates(subset=this_table.columns[0], inplace=True)
            else:
                # Handle duplications
                this_table.drop_duplicates(inplace=True)

                this_table.iloc[:, 0] = [
                    f'{df_pair[0][:3].upper()}{str(i).zfill(5)}' 
                    for i in range(1, len(this_table) + 1)
                ]

            result_set[df_pair[0]] = this_table

        if local:
            self.__store_tables(result_set)

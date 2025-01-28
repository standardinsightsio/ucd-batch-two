import mysql.connector
import pandas as pd

## Package for data loading (python to MySQL)
class MySQLLoader:
    def __init__(self, user:str, password:str, base_name:str, port:int=3306, host:str='localhost'):
        try:
            self.__connection = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=base_name
            )
            self.__cursor = self.__connection.cursor()
            print('\n========\nMySQL connected.\n========')
        except mysql.connector.Error as e:
            print(f"Error: {e}")
    
    # Function for table creation
    def create_table(self, table_name:str, 
                           columns:list[str], 
                           datatypes:list[str], 
                           primary_key:list[str], 
                           foreign_keys:dict)->str:
        if len(columns) != len(datatypes):
            print('\n========\nColumns and datatypes are mismatched!\n========')
        
        # Normal query
        query = f'CREATE TABLE IF NOT EXISTS {table_name} (\n'
        for i in range(len(columns)):
            query += f'\t{columns[i]} {datatypes[i]},\n'
        if len(primary_key) < 2:
            query += f"\tPRIMARY KEY ({primary_key[0]})"
        else:
            query += f"\tPRIMARY KEY ({', '.join(primary_key)})"
        # Add foreign key references
        if foreign_keys:
            for fk, ftb in foreign_keys.items():
                query += f',\n\tFOREIGN KEY ({fk}) REFERENCES {ftb}({fk}),'
        query += '\n)'
        return query

    # Function for data upload
    def upload_data(self, table:str, columns:list[str])->str:
        query = f"INSERT IGNORE INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['%s']*len(columns))})"
        return query
        
    # Function for query execution
    def execute_query(self, query:str, data_row:tuple=None, execution_type:str='create'):
        # Execute queries
        if execution_type == 'create':
            self.__cursor.execute(query)
        elif execution_type == 'upload':
            self.__cursor.execute(query, data_row)
        self.__connection.commit()

    # Function for closing connection
    def close_connect(self):
        self.__cursor.close()
        self.__connection.close()
        print('\n========\nConnection closed.\n========')

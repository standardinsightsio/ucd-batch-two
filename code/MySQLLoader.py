import mysql.connector

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
            print('✅ MySQL connected.')
        except mysql.connector.Error as e:
            print(f"Error: {e}")
            sys.exit(1)

    # Check if a table exists in the database
    def check_table_exists(self, table_name: str) -> bool:
        query = f"SHOW TABLES LIKE '{table_name}'"
        self.__cursor.execute(query)
        return bool(self.__cursor.fetchone())

    # Create table if it does not exist
    def create_table(self, table_name:str, columns:list[str], datatypes:list[str], primary_key:list[str], foreign_keys:dict[str, str]) -> str:
        if len(columns) != len(datatypes):
            raise ValueError("Columns and datatypes length mismatch.")

        query = f'CREATE TABLE IF NOT EXISTS {table_name} (\n'
        for i in range(len(columns)):
            query += f'\t{columns[i]} {datatypes[i]},\n'
        query += f"\tPRIMARY KEY ({', '.join(primary_key)})"

        for fk, ref_table in foreign_keys.items():
            query += f',\n\tFOREIGN KEY ({fk}) REFERENCES {ref_table}({fk})'

        query += '\n);'
        return query

    # Generate SQL query for inserting data
    def upload_data(self, table: str, columns: list[str]) -> str:
        return f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"

    # Execute SQL query
    def execute_query(self, tb_name: str, query: str, data_row: list[tuple] = None, execution_type: str = 'create'):
        try:
            if execution_type == 'create':
                self.__cursor.execute(query)
            elif execution_type == 'upload':
                self.__cursor.executemany(query, data_row)
            self.__connection.commit()
        except mysql.connector.Error as e:
            print(f"SQL Execution Error: {e}")
            sys.exit(1)

    # Close MySQL connection
    def close_connect(self):
        self.__cursor.close()
        self.__connection.close()
        print('✅ MySQL connection closed.')


import mysql.connector
from datetime import timedelta

def get_connection(db_config):
    return mysql.connector.connect(**db_config)

def fetch_all(cursor, query, params=None):
    cursor.execute(query, params or ())
    return cursor.fetchall()

def fetch_one(cursor, query, params=None):
    cursor.execute(query, params or ())
    return cursor.fetchone()

def serialize_row(row):
    for key, val in row.items():
        if isinstance(val, timedelta):
            row[key] = str(val)
    return row

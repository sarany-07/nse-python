import os
from contextlib import contextmanager

import mysql.connector


TABLE_NAMES = {
    "stocks_data": "stocks_data",
    "raw": "rawtabel",
    "stocks": "stocks_list",
}

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3307")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "nse_sme_announcements"),
}


@contextmanager
def database_cursor(commit=False):
    """Provide a cursor and always clean up the cursor and connection."""
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()

    try:
        yield cursor
        if commit:
            connection.commit()
    except Exception:
        if commit:
            connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def get_existed_stock_names():
    query = f"SELECT id, symbol FROM {TABLE_NAMES['stocks']}"

    with database_cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def insert_stock_list_data(insert_data):
    query = f"""
        INSERT INTO {TABLE_NAMES['stocks']} (symbol, stock_name)
        VALUES (%s, %s)
    """

    with database_cursor(commit=True) as cursor:
        cursor.execute(query, insert_data[0])
        rows_created = cursor.rowcount

    print("Rows created:", rows_created)
    

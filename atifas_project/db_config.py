# db_config.py
"""
Database connection helper.
Edit USER, PASSWORD, HOST to match your MySQL server.
"""

import mysql.connector 
from mysql.connector import Error 

DB_NAME = 'library_db'
HOST = 'localhost'
USER = 'root'
PASSWORD = '30102004'  # <-- set your MySQL root password or other user password


def get_connection():
    """
    Returns a new MySQL connection.
    Caller should close() the connection when done.
    """
    try:
        conn = mysql.connector.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DB_NAME,
            autocommit=True
        )
        return conn
    except Error as e:
        raise e

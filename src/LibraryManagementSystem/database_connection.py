# database_connection.py

import mysql.connector
from mysql.connector import Error

connection = None  # Initialize connection

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",                # Default user in XAMPP
        password="",                # Leave empty unless you set one
        database="db_library")      # Must exist in phpMyAdmin

    if connection.is_connected():
        print("Connected to MySQL database successfully! ✅ ")

except Error as e:
    print("Error while connecting to MySQL: ❌", e)

finally:
    if connection and connection.is_connected():  # safe check
        connection.close()
        print("MySQL connection closed. ✅")
import mysql.connector
from mysql.connector import Error
import os

connection = None
cursor = None

def connect():

    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',          # Your MySQL username
            password='',  # Your MySQL password
            database='RestaurantSales'    # The name of your database
        )

        if connection.is_connected():
            cursor = connection.cursor()
            print('db connection established')
    except Error as e:
        print(f"Error: {e}")

def disconnect():
    if connection and connection.is_connected():
        cursor.close()
        connection.close()
        print("\nMySQL connection closed.")
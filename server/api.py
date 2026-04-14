import os
import subprocess
import time
import mysql.connector
import customtkinter as ctk
from tkinter import messagebox

# --- CONFIGURATION & PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MYSQL_PATH = os.path.join(BASE_DIR, "mysql", "bin", "mysqld.exe")
DATA_DIR = os.path.join(BASE_DIR, "mysql_data")
DB_PORT = 3306


def start_mysql_server():
    """Initializes and starts the local MySQL server."""
    if not os.path.exists(MYSQL_PATH):
        print(f"ERROR: Could not find MySQL at {MYSQL_PATH}")
        return False

    # 1. Initialize data directory if it's the first run
    if not os.path.exists(DATA_DIR):
        print("Initializing database for the first time...")
        subprocess.run([
            MYSQL_PATH, 
            "--initialize-insecure", 
            f"--datadir={DATA_DIR}"
        ], check=True)

    # 2. Start the server process
    print(f"Starting MySQL on port {DB_PORT}...")
    subprocess.Popen([
        MYSQL_PATH, 
        f"--datadir={DATA_DIR}", 
        f"--port={DB_PORT}",
        "--console"
    ], creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    
    # Wait for the server to wake up
    time.sleep(5)
    return True

def end_mysql_server():
    """Safely shuts down the local MySQL server."""
    # Locate the mysqladmin executable
    MYSQL_ADMIN = os.path.join(BASE_DIR, "mysql", "bin", "mysqladmin.exe")
    
    if os.path.exists(MYSQL_ADMIN):
        print("Shutting down MySQL...")
        try:
            # We use the 'shutdown' command via mysqladmin
            subprocess.run([
                MYSQL_ADMIN, 
                "-u", "root", 
                f"--port={DB_PORT}", 
                "shutdown"
            ], check=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            print("MySQL stopped successfully.")
        except subprocess.CalledProcessError:
            print("MySQL was already stopped or could not be reached.")
    else:
        print("Could not find mysqladmin.exe to shut down the server.")



# helper functions
def get_db_connection(db_name='RestaurantSales'):
    """Returns a connection to the database."""
    return mysql.connector.connect(
        host="localhost",
        port=DB_PORT,
        user="root",
        password=""
    )

class CRUDApp(ctk.CTk): # main api class
    def __init__(self): # constructor
        super().__init__()
        self.title("Database Manager")
        self.geometry("500x400")

        try:
            self.connection = get_db_connection()

            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
                print('db connection established')
        except:
            print(f"Error couldnt connect to db")

    def __del__(self): # destructor 
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("\nMySQL connection closed.")


    def setup_table(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS my_app_db")
            cursor.execute("USE my_app_db")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Setup Error: {e}")

    def add_user(self):
        pass

    def list_users(self):
        pass


# --- MAIN EXECUTION ---
# everything that appears here will appear the same to frontend
if __name__ == "__main__":
    if start_mysql_server():
        try:
            ctk.set_appearance_mode("dark")
            app = CRUDApp()
            app.mainloop()
        finally:
            # This runs when the mainloop stops (window is closed)
            end_mysql_server()
    else:
        print("Failed to launch MySQL. Check your 'mysql' folder.")

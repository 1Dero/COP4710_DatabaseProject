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
DB_PORT = "3307" 


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

def get_db_connection():
    """Returns a connection to the database."""
    return mysql.connector.connect(
        host="localhost",
        port=DB_PORT,
        user="root",
        password=""
    )

class CRUDApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("One-Click MySQL Manager")
        self.geometry("500x400")
        
        # Setup Database Table if not exists
        self.setup_table()

        # UI Elements
        self.label = ctk.CTkLabel(self, text="Database Manager", font=("Arial", 20, "bold"))
        self.label.pack(pady=20)

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Enter Name")
        self.name_entry.pack(pady=10)

        self.btn_insert = ctk.CTkButton(self, text="Add User", command=self.add_user)
        self.btn_insert.pack(pady=5)

        self.btn_view = ctk.CTkButton(self, text="List Users", command=self.list_users)
        self.btn_view.pack(pady=5)

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
        name = self.name_entry.get()
        if not name:
            messagebox.showwarning("Input Error", "Please enter a name")
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("USE my_app_db")
        cursor.execute("INSERT INTO users (name) VALUES (%s)", (name,))
        conn.commit()
        cursor.close()
        conn.close()
        
        self.name_entry.delete(0, 'end')
        messagebox.showinfo("Success", f"Added {name} to the database!")

    def list_users(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("USE my_app_db")
        cursor.execute("SELECT name FROM users")
        rows = cursor.fetchall()
        
        user_list = "\n".join([r[0] for r in rows])
        messagebox.showinfo("Users", user_list if user_list else "No users found.")
        
        cursor.close()
        conn.close()

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    if start_mysql_server():
        ctk.set_appearance_mode("dark")
        app = CRUDApp()
        app.mainloop()
    else:
        print("Failed to launch MySQL. Check your 'mysql' folder.")
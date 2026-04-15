import os
import sys
import subprocess
import time
import mysql.connector
import customtkinter as ctk
from tkinter import messagebox
import sqlite3

# --- CONFIGURATION & PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MYSQL_PATH = os.path.join(BASE_DIR, "mysql", "bin", "mysqld.exe")
DATA_DIR = os.path.join(BASE_DIR, "mysql_data")
DB_PORT = 3306
PARENT_DIR = os.path.dirname(BASE_DIR)
sys.path.append(PARENT_DIR)


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

class Connection(): 
    def __init__(self): # constructor
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
            with open(os.path.join(PARENT_DIR, "F9_39.sql"), 'r') as f:
                sql_script = f.read()
            self.cursor.execute(sql_script)
            self.cursor.commit()
        except Exception as e:
            print(f"Setup Error: {e}")
        
        messagebox.showinfo("Success", "Database tables set up successfully!")

    def add_full_time_employee(self, name, role, email, phone, salary):
        if not name.strip() or not role.strip():
            messagebox.showwarning("Input Error", "Employee name and role are required")
            return

        try:
            conn = self.connection
            cursor = conn.cursor

            # Insert into Employees (superclass)
            cursor.execute("""
                INSERT INTO Employees (name, role, email, phone)
                VALUES (%s, %s, %s, %s)
            """, (name.strip(), role.strip(), email.strip(), phone.strip()))

            eid = cursor.lastrowid

            # Insert into FullTime (subclass)
            cursor.execute("""
                INSERT INTO FullTime (eid, salary)
                VALUES (%s, %s)
            """, (eid, salary))

            conn.commit()

            messagebox.showinfo("Success", f"Full-time employee added with eid = {eid}")
            return eid

        except Exception as e:
            messagebox.showerror("Database Error", str(e))
    
    def add_part_time_employee(self, name, role, email, phone, hours, pay):
        if not name.strip() or not role.strip():
            messagebox.showwarning("Input Error", "Employee name and role are required")
            return

        try:
            conn = self.connection
            cursor = self.cursor

            # Insert into Employees (superclass)
            cursor.execute("""
                INSERT INTO Employees (name, role, email, phone)
                VALUES (%s, %s, %s, %s)
            """, (name.strip(), role.strip(), email.strip(), phone.strip()))

            eid = cursor.lastrowid

            # Insert into PartTime (subclass)
            cursor.execute("""
                INSERT INTO PartTime (eid, hours, pay)
                VALUES (%s, %s, %s)
            """, (eid, hours, pay))

            conn.commit()

            messagebox.showinfo("Success", f"Part-time employee added with eid = {eid}")
            return eid

        except Exception as e:
            messagebox.showerror("Database Error", str(e))
    
    def add_ingredient(self, name, cost, quantity):
        if not name.strip():
            messagebox.showwarning("Input Error", "Ingredient name is required")
            return

        try:
            conn = self.connection
            cursor = self.cursor

            # Insert into Item
            cursor.execute("""
                INSERT INTO Item (name, cost, quantity)
                VALUES (%s, %s, %s)
            """, (name.strip(), cost, quantity))

            iid = cursor.lastrowid

            # Insert into Ingredients
            cursor.execute("""
                INSERT INTO Ingredients (iid)
                VALUES (%s)
            """, (iid,))

            conn.commit()

            messagebox.showinfo("Success", f"Ingredient added with iid = {iid}")
            return iid

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def add_appliance(self, name, cost, quantity):
        if not name.strip():
            messagebox.showwarning("Input Error", "Appliance name is required")
            return

        try:
            conn = self.connection
            cursor = self.cursor

            # Insert into Item
            cursor.execute("""
                INSERT INTO Item (name, cost, quantity)
                VALUES (%s, %s, %s)
            """, (name.strip(), cost, quantity))

            iid = cursor.lastrowid

            # Insert into Appliances
            cursor.execute("""
                INSERT INTO Appliances (iid)
                VALUES (%s)
            """, (iid,))

            conn.commit()

            messagebox.showinfo("Success", f"Appliance added with iid = {iid}")
            return iid

        except Exception as e:
            messagebox.showerror("Database Error", str(e))
    
    def add_menu(self, name, price):
        if not name.strip():
            messagebox.showwarning("Input Error", "Menu name is required")
            return

        try:
            conn = self.connection
            cursor = self.cursor

            cursor.execute("""
                INSERT INTO Menu (name, price)
                VALUES (%s, %s)
            """, (name.strip(), price))
            mid = cursor.lastrowid

            conn.commit()

            messagebox.showinfo("Success", f"Menu item added with mid = {mid}")
            return mid

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def add_order(self, price, o_date, tip=0):
        try:
            conn = self.connection
            cursor = self.cursor

            cursor.execute("""
                INSERT INTO Orders (price, tip, o_date)
                VALUES (%s, %s, %s)
            """, (price, tip, o_date))

            conn.commit()
            oid = cursor.lastrowid


            messagebox.showinfo("Success", f"Order added with oid = {oid}")
            return oid

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    

    


# --- MAIN EXECUTION ---
# everything that appears here will appear the same to frontend
if __name__ == "__main__":
    pass

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
            cursor.execute("CREATE DATABASE IF NOT EXISTS RestaurantSales")
            cursor.execute("USE RestaurantSales")
            

            #   =======================
            #          Entities
            #   =======================

            # Employee Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Employees(
                eid INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                role VARCHAR(50) NOT NULL,
                email VARCHAR(50),
                phone VARCHAR(20)
            )
        """)
            
            # Full Time Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS FullTime(
                eid INT PRIMARY KEY,
                salary DECIMAL(10,2) UNSIGNED NOT NULL,
                FOREIGN KEY (eid) REFERENCES Employees(eid)
                    ON DELETE CASCADE
            )
        """)

            # Part Time Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS PartTime(
                eid INT PRIMARY KEY,
                hours INT NOT NULL,
                pay DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (eid) REFERENCES Employees(eid)
                    ON DELETE CASCADE
            )
        """)
            
            # Menu Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Menu(
                mid INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                price DECIMAL(10,2) NOT NULL
            )
        """)
            
            # Orders Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Orders(
                oid INT AUTO_INCREMENT PRIMARY KEY,
                price DECIMAL(10,2) NOT NULL,
                tip DECIMAL(10,2) DEFAULT 0,
                o_date DATE NOT NULL
            )
        """)

            # Item Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Item(
                iid INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL,
                cost DECIMAL(10,2) UNSIGNED NOT NULL,
                quantity INT UNSIGNED NOT NULL
            )
        """)
            
            # Ingredients Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Ingredients(
                iid INT PRIMARY KEY,
                FOREIGN KEY (iid) REFERENCES Item(iid)
                    ON DELETE CASCADE
            )
        """)
            
            # Appliances Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Appliances(
                iid INT PRIMARY KEY,
                FOREIGN KEY (iid) REFERENCES Item(iid)
                    ON DELETE CASCADE
            )
        """)
            
            #   =======================
            #       Relationships
            #   =======================


            # OrderMenuItem
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS OrderMenuItem(
                oid INT,
                mid INT,
                PRIMARY KEY (oid, mid),
                FOREIGN KEY (oid) REFERENCES Orders(oid)
                    ON DELETE CASCADE,
                FOREIGN KEY (mid) REFERENCES Menu(mid)
            )
        """)
            
            # MenuItemUses
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS MenuItemUses(
                mid INT,
                iid INT,
                PRIMARY KEY (mid, iid),
                FOREIGN KEY (mid) REFERENCES Menu(mid),
                FOREIGN KEY (iid) REFERENCES Ingredients(iid)
            )
        """)
            
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Setup Error: {e}")
        
        messagebox.showinfo("Success", "Database tables set up successfully!")

    def add_full_time_employee(self, name, role, email, phone, salary):
        if not name.strip() or not role.strip():
            messagebox.showwarning("Input Error", "Employee name and role are required")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

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
            cursor.close()
            conn.close()

            messagebox.showinfo("Success", f"Full-time employee added with eid = {eid}")
            return eid

        except Exception as e:
            messagebox.showerror("Database Error", str(e))
    
    def add_part_time_employee(self, name, role, email, phone, hours, pay):
        if not name.strip() or not role.strip():
            messagebox.showwarning("Input Error", "Employee name and role are required")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

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
            cursor.close()
            conn.close()

            messagebox.showinfo("Success", f"Part-time employee added with eid = {eid}")
            return eid

        except Exception as e:
            messagebox.showerror("Database Error", str(e))
    
    def add_ingredient(self, name, cost, quantity):
        if not name.strip():
            messagebox.showwarning("Input Error", "Ingredient name is required")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

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
            cursor.close()
            conn.close()

            messagebox.showinfo("Success", f"Ingredient added with iid = {iid}")
            return iid

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def add_appliance(self, name, cost, quantity):
        if not name.strip():
            messagebox.showwarning("Input Error", "Appliance name is required")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

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
            cursor.close()
            conn.close()

            messagebox.showinfo("Success", f"Appliance added with iid = {iid}")
            return iid

        except Exception as e:
            messagebox.showerror("Database Error", str(e))
    
    def add_menu(self, name, price):
        if not name.strip():
            messagebox.showwarning("Input Error", "Menu name is required")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO Menu (name, price)
                VALUES (%s, %s)
            """, (name.strip(), price))

            conn.commit()
            mid = cursor.lastrowid

            cursor.close()
            conn.close()

            messagebox.showinfo("Success", f"Menu item added with mid = {mid}")
            return mid

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def add_order(self, price, o_date, tip=0):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO Orders (price, tip, o_date)
                VALUES (%s, %s, %s)
            """, (price, tip, o_date))

            conn.commit()
            oid = cursor.lastrowid

            cursor.close()
            conn.close()

            messagebox.showinfo("Success", f"Order added with oid = {oid}")
            return oid

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

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
        try:
            ctk.set_appearance_mode("dark")
            app = CRUDApp()
            app.mainloop()
        finally:
            # This runs when the mainloop stops (window is closed)
            end_mysql_server()
    else:
        print("Failed to launch MySQL. Check your 'mysql' folder.")
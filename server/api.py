import os
import sys
import subprocess
import time
from unittest import result
import mysql.connector

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
def get_db_connection(db_name="RestaurantSales"):
    """Returns a connection to the database."""
    return mysql.connector.connect(
        host="localhost",
        port=DB_PORT,
        user="root",
        password="",
        database=db_name
    )

def get_server_connection():
    """Returns a connection to the MySQL server without specifying a database."""
    return mysql.connector.connect(
        host="localhost",
        port=DB_PORT,
        user="root",
        password=""
    )

class Connection(): 
    def __init__(self):
        self.connection = None
        self.cursor = None

        if not start_mysql_server():
            print("Failed to initiate MySQL process.")
            sys.exit(1)
        else:
            print("MySQL server has been started.")

        # Retry logic: Server might take a moment to bind to the port

        retries = 5
        while retries > 0:
            try:
                self.setup_database()
                self.connection = get_db_connection()
                if self.connection.is_connected():
                    self.cursor = self.connection.cursor()
                    print('Database connection established')
                    return
            except mysql.connector.Error as err:
                print(f"Waiting for MySQL... ({retries} retries left). Error: {err}")
                time.sleep(2)
                retries -= 1
        
        print("Error: Could not connect to MySQL after multiple attempts.")
        sys.exit(1)

    def close(self):
        """Manually close the connection and stop the server."""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
                print("MySQL connection closed.")
        except Exception:
            # Ignore errors during shutdown if objects are already gone
            pass
        finally:
            end_mysql_server()

    def __del__(self):
        try:
            self.close()
        except:
            pass


    def setup_database(self):
        conn = get_server_connection()
        cursor = conn.cursor()
        print("Creating RestaurantSales Database...")
        try:
            with open(os.path.join(PARENT_DIR, "FP_39.sql"), "r", encoding="utf-8") as f:
                sql_script = f.read()
                
                # Execute the script
                statements = sql_script.split(';')
                for statement in statements:
                    if statement.strip():
                        print(f"Executing: {statement}\n")
                        cursor.execute(statement)
                
                # We MUST consume the generator fully to finish the execution

            # CRITICAL: Commit the changes to the disk
            conn.commit()
            
        except Exception as e:
            print(f"Setup Error: {e}")
            conn.rollback()
        finally:
            print("\n----------------------------- Database created -----------------------------\n")
            cursor.close()
            conn.close()

    def add_full_time_employee(self, name, role, email, phone, salary):
        if not name.strip() or not role.strip():
            print("Employee name and role are required")
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

            print(f"Full-time employee added with eid = {eid}")
            return eid

        except Exception as e:
            print("Database Error", str(e))
    
    def add_part_time_employee(self, name, role, email, phone, hours, pay):
        if not name.strip() or not role.strip():
            print("Employee name and role are required")
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

            print(f"Part-time employee added with eid = {eid}")
            return eid

        except Exception as e:
            print("Database Error", str(e))
    
    def add_ingredient(self, name, cost, quantity):
        if not name.strip():
            print("Ingredient name is required")
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

            print(f"Ingredient added with iid = {iid}")
            return iid

        except Exception as e:
            print("Database Error", str(e))

    def add_appliance(self, name, cost, quantity):
        if not name.strip():
            print("Appliance name is required")
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

            print(f"Appliance added with iid = {iid}")
            return iid

        except Exception as e:
            print("Database Error", str(e))
    
    def add_menu(self, name, price):
        if not name.strip():
            print("Menu name is required")
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

            print(f"Menu item added with mid = {mid}")
            return mid

        except Exception as e:
            print("Database Error", str(e))

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


            print(f"Order added with oid = {oid}")
            return oid

        except Exception as e:
            print("Database Error", str(e))

    def delete_by_id(self, table_name, record_id):
        try:
            pk_map = {
                "Restaurant": "rid",
                "Employees": "eid",
                "PartTime": "eid",
                "FullTime": "eid",
                "Menu": "mid",
                "Item": "iid",
                "Ingredients": "iid",
                "Appliances": "aid",
                "Orders": "oid"
            }

            if table_name not in pk_map:
                print("Invalid table name")
                return

            pk_column = pk_map[table_name]
            
            self.cursor.execute(f"""
                DELETE FROM {table_name}
                WHERE {pk_column} = {record_id}
            """)
            self.connection.commit()

        except Exception as e:
            print("Database Error:", str(e))

    def list_table(self,table_name):
        self.cursor.execute(f'SELECT * FROM {table_name}')
        
        return self.cursor.fetchall()
    
    def get_restaurant_name(self):
        try:
            self.cursor.execute("""
                SELECT name 
                FROM Restaurant 
                WHERE rid = 1
            """)
            result = self.cursor.fetchone()
            return result[0] if result else None

        except Exception as e:
            print("Database Error:", str(e))
    
    def set_restaurant_name(self, new_name: str):
        if not new_name.strip():
            print("Restaurant name cannot be empty")
            return

        try:
            self.cursor.execute(f"""
                UPDATE Restaurant
                SET name = "{new_name.strip()}"
                WHERE rid = 1
            """)

            self.connection.commit()

        except Exception as e:
            print("Database Error:", str(e))
    

# --- MAIN EXECUTION ---
# everything that appears here will appear the same to frontend
if __name__ == "__main__":
    server = Connection()
    server.list_table("Employees")

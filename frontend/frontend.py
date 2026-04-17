#IMPROTS 
import customtkinter as ctk
from tkinter import ttk, messagebox
import os
import sys

# ACCESS SERVER
# Get the absolute path to the directory containing this script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the path to the parent directory
parent_dir = os.path.dirname(current_dir)
# Add the parent directory to sys.path
sys.path.append(parent_dir)
from server.api import Connection, get_db_connection


# GLOBAL VARS
VIEWS = ('employeeview','restaurantsummary', 'menuoverview') # views, no add button
RELATIONSHIPS = ('ordermenuitem','restaurantstock','menuitemuses')
ALLOWED_TABLES = ['employeeview', 'restaurantsummary', 'menuoverview', 'menu', 'orders', 'item', 'employees']

# Mapping of Database Name -> UI Display Name
DISPLAY_NAMES = {
    'employeeview': 'Staff Overview',
    'restaurantsummary': 'Financial Summary',
    'menuoverview': 'Menu Overview',
    'item': 'Inventory'
}

import customtkinter as ctk

# Set UCF color scheme
ctk.set_appearance_mode("dark")  # Dark mode for black background
ctk.set_default_color_theme("dark-blue")  # Base theme, will override colors

class ClickableLabel(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.master = master 
        self.placeholder = master.server.get_restaurant_name()
        
        # Define the header style
        # ("Font Name", Size, "weight")
        self.header_font = ("Helvetica", 32, "bold")
        
        # 1. The Label (Styled as a Header)
        self.label = ctk.CTkLabel(
            self, 
            text=self.placeholder, 
            font=self.header_font,
            text_color="#FFC904",  # UCF Gold
            cursor="hand2"
        )
        self.label.pack(padx=10, pady=10)
        
        # Bind the click event
        self.label.bind("<Button-1>", lambda e: self.show_entry())

        # 2. The Entry (Styled to match the header size)
        self.entry = ctk.CTkEntry(
            self, 
            font=self.header_font,
            justify="center", # Centers text while typing
            height=50         # Taller box for larger font
        )
        self.entry.bind("<Return>", lambda e: self.handle_submit())
        # Also bind FocusOut so it reverts if the user clicks away
        self.entry.bind("<FocusOut>", lambda e: self.revert())

    def show_entry(self):
        self.label.pack_forget()
        self.entry.pack(padx=10, pady=10)
        
        current_text = self.label.cget("text")
        self.entry.delete(0, 'end')
        self.entry.insert(0, current_text)
        self.entry.focus()

    def handle_submit(self):
        input_text = self.entry.get().strip()
        
        if input_text != "":
            # Update the Backend (SQL/Server)
            self.master.server.set_restaurant_name(input_text)
            
            # Update UI
            self.label.configure(text=input_text)
            self.revert()
        else:
            self.revert()

    def revert(self):
        """Helper to swap back to label mode"""
        self.entry.pack_forget()
        self.label.pack(padx=10, pady=10)

# --- Popup Window Class ---
class InputPopup(ctk.CTkToplevel):
    def __init__(self, parent, edit_data=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.edit_data = edit_data  # Store the data we are editing
        self.is_edit_mode = edit_data is not None
        if self.is_edit_mode:
            self.title("Update Entry")
        else:
            self.title("Add New Entry")
        self.geometry("600x900")
        self.attributes("-topmost", True)
        self.grab_set()

        self.label = ctk.CTkLabel(self, text="Enter Details", font=("Arial", 16, "bold"))
        self.label.pack(pady=10)

        # Container for the dynamic entry fields
        self.entry_container = ctk.CTkFrame(self, fg_color="transparent")
        self.entry_container.pack(fill="both", expand=True, padx=20)

        self.entries = {}
        
        # Special logic for the 'employees' table
        if self.parent.name == "employees":
            self.is_full_time = ctk.BooleanVar(value=True)
            self.type_toggle = ctk.CTkCheckBox(
                self, 
                text="Full-Time Employee", 
                variable=self.is_full_time,
                command=self.refresh_employee_fields,
                fg_color="#FFC904",
                hover_color="#E6B800"
            )
            self.type_toggle.pack(pady=5)
            self.refresh_employee_fields()
        elif self.parent.name == "item":
            # Only show the checkbox if we are ADDING a new entry
            if not self.is_edit_mode:
                self.is_ingredient = ctk.BooleanVar(value=True)
                self.check = ctk.CTkCheckBox(self.entry_container, text="Is Ingredient", 
                                             variable=self.is_ingredient, 
                                             command=self.refresh_item_fields)
                self.check.pack(pady=10)
            
            self.refresh_item_fields()
            
            # If updating, the common fields (name, cost, qty) are filled normally
            if self.is_edit_mode:
                self.autofill_data()
        elif self.parent.name == "menu":
            self.geometry("400x600")
            
            # 1. Create the standard Name and Price fields first
            self.build_fields(['name', 'price'])
            
            # 2. Add a label for the ingredients section
            label = ctk.CTkLabel(self.entry_container, text="Select Ingredients:", font=("Arial", 12, "bold"))
            label.pack(anchor="w", pady=(10, 0))
            
            # 3. Fetch Ingredients from DB
            self.parent.server.cursor.execute("SELECT i.iid, it.name FROM Ingredients i JOIN Item it ON i.iid = it.iid")
            ingredient_options = self.parent.server.cursor.fetchall()
            
            # 4. Build the multi-select WITHOUT clearing the Name/Price fields
            self.build_multi_select(ingredient_options, clear_first=False)
        else:
            # Default behavior for other tables
            self.columns = parent.columns[(1 if not self.parent.is_relationship else 0):]
            self.build_fields(self.columns)

        if self.is_edit_mode:
            self.autofill_data()

        self.submit_btn = ctk.CTkButton(self, text="Submit", command=self.submit, fg_color="#FFC904", text_color="black")
        self.submit_btn.pack(side="bottom", pady=20)

    def build_fields(self, columns):
        """Clears and rebuilds entry widgets based on column list."""
        for widget in self.entry_container.winfo_children():
            widget.destroy()
        
        self.entries = {}
        for col in columns:
            lbl = ctk.CTkLabel(self.entry_container, text=col.capitalize())
            lbl.pack(anchor="w")
            entry = ctk.CTkEntry(self.entry_container, placeholder_text=col)
            entry.pack(pady=(0, 10), fill="x")
            self.entries[col] = entry
    
    def build_multi_select(self, options, clear_first=True):
        """Creates a scrollable list of checkboxes for ingredients."""
        if clear_first:
            for widget in self.entry_container.winfo_children():
                widget.destroy()

        self.ingredient_vars = {}
        
        scroll_frame = ctk.CTkScrollableFrame(self.entry_container, height=250)
        scroll_frame.pack(fill="both", expand=True, pady=10)

        for iid, name in options:
            var = ctk.BooleanVar(value=False)
            cb = ctk.CTkCheckBox(
                scroll_frame, 
                text=name, 
                variable=var, 
                fg_color="#FFC904", 
                hover_color="#E6B800",
                text_color="white"
            )
            cb.pack(anchor="w", pady=5)
            self.ingredient_vars[iid] = var

    def autofill_data(self):
        """Fills standard fields from the table row data for any table."""
        # Create a dictionary mapping Column Name -> Row Value
        # e.g., {'iid': 1, 'name': 'Tomato', 'cost': 0.5, 'quantity': 100}
        data_map = dict(zip(self.parent.columns, self.edit_data))

        # Handle Employee initial state (needed for the FT/PT checkbox)
        if self.parent.name in ("employees", "employeeview"):
            self.refresh_employee_fields(is_initial_load=True)

        # Iterate through the entry widgets we built (name, cost, quantity, etc.)
        for col_name, entry_widget in self.entries.items():
            if col_name in data_map:
                val = str(data_map[col_name])
                
                # Clean up display strings
                if val.lower() in ("none", "---", "null"): 
                    val = ""
                
                # Clear and insert
                entry_widget.delete(0, 'end')
                entry_widget.insert(0, val)
        
        # Handle the specialized Menu ingredient checkboxes
        if self.parent.name == "menu":
            self.autofill_ingredients()
    
    def autofill_ingredients(self):
        """Fetches existing ingredient IDs for the menu item and checks the boxes."""
        if not self.is_edit_mode or not hasattr(self, 'ingredient_vars'):
            return
            
        mid = self.edit_data[0] # The mid is the first column in 'menu' table
        query = "SELECT iid FROM MenuItemUses WHERE mid = %s"
        
        try:
            self.parent.server.cursor.execute(query, (mid,))
            # Create a list of iids currently used by this menu item
            linked_iids = [row[0] for row in self.parent.server.cursor.fetchall()]
            
            # Set checkbox variables to True if their ID is in the linked list
            for iid, var in self.ingredient_vars.items():
                var.set(iid in linked_iids)
        except Exception as e:
            print(f"Error autofilling ingredients: {e}")
    
    def refresh_employee_fields(self, is_initial_load=False):
        """Rebuilds fields and handles DB lookups for salary/hours/pay."""
        # 1. Save current basic info (name, role, etc.) to restore later
        current_values = {col: entry.get() for col, entry in self.entries.items()}
        
        server = self.parent.server
        eid = self.edit_data[0] if self.is_edit_mode else None

        # 2. If opening an existing record, determine type from DB
        if self.is_edit_mode and is_initial_load:
            server.cursor.execute("SELECT salary FROM FullTime WHERE eid = %s", (eid,))
            if server.cursor.fetchone():
                self.is_full_time.set(True)
            else:
                self.is_full_time.set(False)

        # 3. Define and build the columns
        common = ['name', 'role', 'email', 'phone']
        if self.is_full_time.get():
            cols = common + ['salary']
        else:
            cols = common + ['hours', 'pay']
        
        self.build_fields(cols)

        # 4. Restore common fields
        for col, value in current_values.items():
            if col in self.entries and value:
                self.entries[col].insert(0, value)

        # 5. Fetch and fill the specialized data from the sub-tables
        if self.is_edit_mode:
            if self.is_full_time.get():
                server.cursor.execute("SELECT salary FROM FullTime WHERE eid = %s", (eid,))
                res = server.cursor.fetchone()
                if res and self.entries['salary'].get() == "":
                    self.entries['salary'].insert(0, str(res[0]))
            else:
                server.cursor.execute("SELECT hours, pay FROM PartTime WHERE eid = %s", (eid,))
                res = server.cursor.fetchone()
                if res:
                    if self.entries['hours'].get() == "": self.entries['hours'].insert(0, str(res[0]))
                    if self.entries['pay'].get() == "": self.entries['pay'].insert(0, str(res[1]))
    
    def refresh_item_fields(self):
        """Builds standard fields for Inventory items (Name, Cost, Quantity)."""
        cols = ['name', 'cost', 'quantity']
        self.build_fields(cols)
        
        mode = "Update" if self.is_edit_mode else "Add"
        self.title(f"{mode} Inventory Item")

    def submit(self):
        data = {col: entry.get().strip() for col, entry in self.entries.items()}
        
        if any(not val for val in data.values()):
            messagebox.showwarning("Warning", "All fields are required.")
            return

        server = self.parent.server
        table = self.parent.name
        success = False

        record_id = self.edit_data[0] if self.is_edit_mode else None

        try:
            if self.is_edit_mode:
                # EDIT Logic
                if table == "employees":
                    if self.is_full_time.get():
                        success = server.update_full_time_employee(
                            record_id, data['name'], data['role'], data['email'], data['phone'], float(data['salary'])
                        )
                    else:
                        success = server.update_part_time_employee(
                            record_id, data['name'], data['role'], data['email'], data['phone'], int(data['hours']), float(data['pay'])
                        )
                elif table == "item":
                        success = server.update_item(record_id, data['name'], float(data['cost']), int(data['quantity']))
                elif table == "menu":
                    # Update basic info (name/price)
                    success = server.update_menu(record_id, data['name'], float(data['price']))
                    if success:
                        # Update the ingredients list
                        selected_iids = [iid for iid, var in self.ingredient_vars.items() if var.get()]
                        server.update_menu_ingredients(record_id, selected_iids)
                elif table == "orders":
                    success = server.add_order(
                        float(data['price']), data['o_date'], float(data.get('tip', 0))
                    )
                
                if success:
                    # Refresh current table data directly
                    new_data = server.list_table(table)
                    self.parent.load_data(new_data)
                    self.destroy()
                    messagebox.showinfo("Success", "Record updated successfully!")
            else:
                # ADD Logic
                if table == "employees":
                    if self.is_full_time.get():
                        success = server.add_full_time_employee(
                            data['name'], data['role'], data['email'], data['phone'], float(data['salary'])
                        )
                    else:
                        success = server.add_part_time_employee(
                            data['name'], data['role'], data['email'], data['phone'], int(data['hours']), float(data['pay'])
                        )
                elif table == "item":
                    if self.is_ingredient.get():
                        success = server.add_ingredient(
                            data['name'], float(data['cost']), int(data['quantity'])
                        )
                    else:
                        success = server.add_appliance(
                            data['name'], float(data['cost']), int(data['quantity'])
                        )
                elif table == "menu":
                    # 1. Add the Menu Item
                    new_mid = server.add_menu(data['name'], float(data['price']))
                    
                    if new_mid:
                        # 2. Get all checked ingredient IDs
                        selected_iids = [iid for iid, var in self.ingredient_vars.items() if var.get()]
                        
                        # 3. Link them in MenuItemUses
                        for iid in selected_iids:
                            server.link_menu_ingredient(new_mid, iid)
                        
                        success = True
                elif table == "orders":
                    success = server.add_order(float(data['price']), data['o_date'], float(data.get('tip', 0)))
                else:
                    # Fallback to the generic add for tables without specialized functions
                    success = server.add(table, tuple(data.values()), list(data.keys()))

                if success:
                    # Refresh current table data
                    new_data = server.list_table(table)
                    self.parent.load_data(new_data)
                    self.destroy()
                    messagebox.showinfo("Success", "Record added successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Submission failed: {e}")

class MySQLDataTable(ctk.CTkFrame):
    def __init__(self, master, columns, table_name, server, db_config=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.is_view = bool(table_name in VIEWS)
        self.is_relationship = bool(table_name in RELATIONSHIPS)
        self.master = master
        self.name = table_name
        self.server = server
        self.columns = columns
        self.db_config = db_config
        self.full_data = []
        self.popup_window = None

        # Layout Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- 1. Top Bar (Search & Add) ---
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.search_entry = ctk.CTkEntry(self.top_bar, placeholder_text="Filter results...", width=250)
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.filter_data)


        

        # --- 2. Table Container ---
        self.container = ctk.CTkFrame(self)
        self.container.grid(row=1, column=0, padx=10, pady=0, sticky="nsew")
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(self.container, columns=self.columns, show="headings")
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        self.scrollbar = ctk.CTkScrollbar(self.container, command=self.tree.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # --- 3. Bottom Bar (Edit & Delete) ---
        
        if not self.is_view:
            self.action_bar = ctk.CTkFrame(self, fg_color="transparent")
            self.action_bar.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

            self.add_btn = ctk.CTkButton(self.action_bar, text="+ Add Entry", fg_color="#FFC904", 
                                         hover_color="#E6B800", text_color="#000000", command=self.add_action)
            self.add_btn.pack(side="left", padx=10)

            # ADD THIS BUTTON:
            self.update_btn = ctk.CTkButton(self.action_bar, text="Update Selected", 
                                            fg_color="#FFC904", hover_color="#E6B800", 
                                            text_color="#000000", command=self.update_action)
            self.update_btn.pack(side="left", padx=10)

            self.delete_btn = ctk.CTkButton(self.action_bar, text="Delete Selected", 
                                            fg_color="#FFC904", hover_color="#E6B800", 
                                            text_color="#000000", command=self.delete_action)
            self.delete_btn.pack(side="left")
        else: 
            pass

        self._apply_style()

    def _apply_style(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#000000", foreground="#FFFFFF", 
                        fieldbackground="#000000", borderwidth=0, rowheight=30)
        style.map('Treeview', background=[('selected', '#FFC904')])
        style.configure("Treeview.Heading", background="#FFC904", foreground="#000000", relief="flat")

    # --- CRUD Placeholder Logic ---

    def add_action(self):
        # Prevent opening multiple instances of the same popup
        if self.popup_window is None or not self.popup_window.winfo_exists():
            self.popup_window = InputPopup(self)


        else:
            self.popup_window.focus()
        # After database insertion, you would call self.fetch_from_mysql()
        
    

    def delete_action(self):
        """Identifies selected row and removes it."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a row to delete.")
            return

        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?"):
            return
        
        item_values = self.tree.item(selected_item)['values']
        print(f"Deleting record with ID: {item_values[0]}")
        self.server.delete_by_id(self.name,item_values[0])

        for item in self.tree.get_children(): # deletes all elements that have matching keys
            if(self.tree.item(item)['values'][0] == item_values[0]):
                self.tree.delete(item)

            # Run SQL: DELETE FROM table WHERE id = item_values[0]
    
    def update_action(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a record to update.")
            return
        
        # Get the full list of values from the selected row
        values = self.tree.item(selected[0])['values']
        
        # Open the same popup, but pass the data
        InputPopup(self, edit_data=values)

    # --- Data Handling ---

    def load_data(self, data):
        self.full_data = data
        self.update_view(self.full_data)

    def update_view(self, rows):
        """Clears the table and inserts new rows, replacing None with '---'"""
        # 1. Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 2. Insert rows with the replacement logic
        for row in rows:
            # Create a new list where None becomes '---'
            # We use str(cell) if it's not None to keep numbers and text intact
            clean_row = [str(cell) if cell is not None else "---" for cell in row]
            
            self.tree.insert("", "end", values=clean_row)

    def filter_data(self, event=None):
        query = self.search_entry.get().lower()
        filtered = [row for row in self.full_data if any(query in str(cell).lower() for cell in row)]
        self.update_view(filtered)



class PortableDatabaseTabs(ctk.CTkTabview):
    def __init__(self, master, categories, columns, fetch_callback, **kwargs):
        """
        :param categories: List of strings for tab names
        :param columns: Tuple of column headers
        :param fetch_callback: A function that returns data based on a category string
        """
        super().__init__(master, **kwargs)
        
        self.fetch_callback = fetch_callback
        self.table_widgets = {}

        # Google-style styling
        self.configure(segmented_button_fg_color="transparent")

        # Setup Tab Change Event
        self.configure(command=self._on_tab_event)

        # Build Tabs and Tables
        for name in categories:
            tab_page = self.add(name)
            table = MySQLDataTable(tab_page, columns=columns)
            table.pack(expand=True, fill="both")
            self.table_widgets[name] = table

        # Load first tab data immediately
        self._on_tab_event()

    def _on_tab_event(self):
        current_tab = self.get()
        # Call the external fetch function provided by the user
        new_data = self.fetch_callback(current_tab)
        self.table_widgets[current_tab].load_data(new_data)


class MainApp(ctk.CTk):
    def __init__(self, server):
        super().__init__()
        self.geometry("1300x800")
        self.title("Restaurant Sales")

        self.server = server

        # Initialize our custom widget
        self.editable_field = ClickableLabel(self)
        self.editable_field.pack(side="top", anchor="nw", padx=5, pady=5)

        self.server.cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'restaurantsales' 
        """)
        raw_tables = [t[0] for t in self.server.cursor.fetchall()]
        self.categories = [t for t in raw_tables if t in ALLOWED_TABLES]

        # 2. Store Table References
        # This dict will map Tab Names -> MySQLDataTable objects
        self.table_widgets = {}
        self.tabview = ctk.CTkTabview(
            self, 
            command=self.on_tab_switched, # <--- Triggered on click
            segmented_button_selected_color="#FFC904",
            segmented_button_selected_hover_color="#E6B800"
        )
        self.tabview._segmented_button.configure(
            selected_color="black",           # Your specific request
            selected_hover_color="#333333"   # Slightly lighter black on hover
        )
        self.tabview.pack(expand=True, fill="both", padx=20, pady=20)

        # 4. Pre-create the tab structures
        for db_name in self.categories:
            ui_label = DISPLAY_NAMES.get(db_name, db_name.capitalize())
            tab_object = self.tabview.add(ui_label)
            
            # Fetch columns using the actual DB name
            self.server.cursor.execute(f"""
                SELECT COLUMN_NAME FROM information_schema.columns 
                WHERE table_schema = "restaurantsales" AND table_name = "{db_name}"
                ORDER BY ORDINAL_POSITION
            """)
            cols = [col[0] for col in self.server.cursor.fetchall()]

            # Pass the REAL db_name to the table so SQL queries don't break
            table = MySQLDataTable(tab_object, 
                                   columns=cols, 
                                   table_name=db_name,
                                   server=self.server)
            table.pack(expand=True, fill="both")

            self.table_widgets[ui_label] = table

        # 5. Load the initial tab manually on startup
        self.on_tab_switched()

    def on_tab_switched(self):
        """This runs every time the user clicks a tab."""
        selected_tab = self.tabview.get()
        
        if not selected_tab or selected_tab not in self.table_widgets:
            return

        # Get the specific table widget for this tab
        target_table = self.table_widgets[selected_tab]
        
        # FIX: Pass target_table.name (the real DB name) instead of selected_tab
        db_results = self.server.list_table(target_table.name)

        # Insert the data into the widget
        target_table.load_data(db_results)




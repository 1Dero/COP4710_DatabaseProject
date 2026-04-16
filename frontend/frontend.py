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
VIEWS = ('EmployeeView','RestaurantSummary') # views, no add button
RELATIONSHIPS = ('OrderMenuItem','RestaurantStock','MenuItemUses')

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
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.columns = parent.columns[(1 if not self.parent.is_relationship else 0):] # skip the id if parent is a relationship, 0 otherwise
        self.title("Add New Entry")
        self.geometry("300x250")
        
        # Ensure the popup stays on top and grabs focus
        self.attributes("-topmost", True)
        self.grab_set()

        self.label = ctk.CTkLabel(self, text="Enter Details", font=("Arial", 16, "bold"))
        self.label.pack(pady=10)

        self.entires = {}
        for col in self.columns:
            self.entires[col] = ctk.CTkEntry(self, placeholder_text=col)
            self.entires[col].pack(pady=10, padx=20, fill="x")

        self.submit_btn = ctk.CTkButton(self, text="Submit", command=self.submit)
        self.submit_btn.pack(pady=20)

    def submit(self):
        entires = tuple([value.get() for value in  self.entires.values()])
        for entry in entires: # check if all entries are present
            if not entry:
                messagebox.showwarning("Warning", "All fields are required.")
                return


        if self.parent.server.add(self.parent.name,entires, self.columns):
            self.parent.server.cursor.execute(f"""SELECT * FROM {self.parent.name} 
                                              ORDER BY 1 
                                              DESC LIMIT 1
                                              """)
            last_row = self.parent.server.cursor.fetchone()

            self.parent.tree.insert("", "end", values=last_row)
            messagebox.showinfo("Success", "Data added to MySQL!")
            self.destroy() # Close popup
        else:
            messagebox.showerror("Error", "Failed to connect to database.")

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
        self.action_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.action_bar.grid(row=2, column=0, padx=10, pady=10, sticky="ew")


        if not self.is_view:
            self.add_btn = ctk.CTkButton(self.action_bar, text="+ Add Entry", fg_color="#FFC904", 
                                         hover_color="#E6B800", text_color="#000000", command=self.add_action)
            self.add_btn.pack(side="left", padx=10)

            self.delete_btn = ctk.CTkButton(self.action_bar, text="Delete Selected", 
                                            fg_color="#FFC904", hover_color="#E6B800", 
                                            text_color="#000000", command=self.delete_action)
            self.delete_btn.pack(side="left")

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

    # --- Data Handling ---

    def load_data(self, data):
        self.full_data = data
        self.update_view(self.full_data)

    def update_view(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", "end", values=row)

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
            WHERE table_schema = 'RestaurantSales' 
            ORDER BY create_time ASC
        """)
        raw_tables = self.server.cursor.fetchall()
        self.categories = [table[0] for table in raw_tables]

        # 2. Store Table References
        # This dict will map Tab Names -> MySQLDataTable objects
        self.table_widgets = {}

        # 3. Create TabView with a 'command' callback
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
        for name in self.categories:
            tab_object = self.tabview.add(name)
            
            # Create the table widget inside the tab immediately
            # but leave it empty for now
            self.server.cursor.execute(f"""
                SELECT COLUMN_NAME 
                FROM information_schema.columns 
                WHERE table_schema = "RestaurantSales"
                AND table_name = "{name}"
                ORDER BY ORDINAL_POSITION
            """)


            table = MySQLDataTable(tab_object, 
                                   columns=self.server.cursor.fetchall(), 
                                   table_name=name,
                                   server=self.server)
            table.pack(expand=True, fill="both")
            
            # Save reference to the table so we can update it later
            self.table_widgets[name] = table

        # 5. Load the initial tab manually on startup
        self.on_tab_switched()

    def on_tab_switched(self):
        """This runs every time the user clicks a tab."""
        selected_tab = self.tabview.get()
        print(f"Table switched to: {selected_tab}")

        # Get the specific table widget for this tab
        target_table = self.table_widgets[selected_tab]
        # Simulation: Fetching data based on the tab name
        # In production, replace this with: 
        # data = db.execute(f"SELECT * FROM employees WHERE dept='{selected_tab}'")
        db_results = self.server.list_table(selected_tab)

        # Insert the data into the widget
        target_table.load_data(db_results)




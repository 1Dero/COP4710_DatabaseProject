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
app = None # app is a global variable


class foo:
    def get_restaurant_name():
        return 'resty'
    def set_restaurant_name(name):
        print('restaurant name set')
        return


# click on label and input box pops up
class ClickableLabel(ctk.CTkFrame):
    def __init__(self, master, placeholder="Blank", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.placeholder = foo.get_restaurant_name()
        
        # 1. The Label (Visible by default)
        self.label = ctk.CTkLabel(self, text=self.placeholder, cursor="hand2")
        self.label.pack(padx=5, pady=5)
        
        # Bind the click event to the label
        self.label.bind("<Button-1>", lambda e: self.show_entry())

        # 2. The Entry (Hidden by default)
        self.entry = ctk.CTkEntry(self)
        # Bind the Enter key to the submission logic
        self.entry.bind("<Return>", lambda e: self.handle_submit())

    def show_entry(self):
        """Hide label and show the entry box"""
        self.label.pack_forget()
        self.entry.pack(padx=5, pady=5)
        self.entry.focus()
        # Pre-fill entry with current label text if it's not the placeholder
        current_text = self.label.cget("text")
        if current_text != self.placeholder:
            self.entry.insert(0, current_text)

    def handle_submit(self): # gets the entry 
        """Logic to run when user presses Enter"""
        input_text = self.entry.get().strip()
        
        if input_text != "":
            # Run your custom function here

            foo.set_restaurant_name(input_text) # submits r name
            
            # Update label and swap back
            self.label.configure(text=input_text)
            self.entry.delete(0, 'end')
            self.entry.pack_forget()
            self.label.pack(padx=5, pady=5)
        else:
            # If empty, maybe just revert or show placeholder
            print("Input was empty - ignoring.")
            self.entry.pack_forget()
            self.label.pack(padx=5, pady=5)

class MySQLDataTable(ctk.CTkFrame):
    def __init__(self, master, columns, db_config=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.columns = columns
        self.db_config = db_config
        self.full_data = []

        # Layout Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- 1. Top Bar (Search & Add) ---
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.search_entry = ctk.CTkEntry(self.top_bar, placeholder_text="Filter results...", width=250)
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.filter_data)

        self.add_btn = ctk.CTkButton(self.top_bar, text="+ Add Entry", fg_color="#28a745", 
                                     hover_color="#218838", width=100, command=self.add_action)
        self.add_btn.pack(side="right")

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

        self.edit_btn = ctk.CTkButton(self.action_bar, text="Edit Selected", 
                                      fg_color="#1f538d", command=self.edit_action)
        self.edit_btn.pack(side="left", padx=(0, 10))

        self.delete_btn = ctk.CTkButton(self.action_bar, text="Delete Selected", 
                                        fg_color="#dc3545", hover_color="#c82333", 
                                        command=self.delete_action)
        self.delete_btn.pack(side="left")

        self._apply_style()

    def _apply_style(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", 
                        fieldbackground="#2b2b2b", borderwidth=0, rowheight=30)
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat")

    # --- CRUD Placeholder Logic ---

    def add_action(self):
        """Logic for adding a new record (usually opens a popup)."""
        # Example: Open a CTkToplevel window with entry fields
        print("Add button clicked: Open input dialog or new window here.")
        # After database insertion, you would call self.fetch_from_mysql()

    def edit_action(self):
        """Identifies selected row and triggers edit logic."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a row to edit.")
            return
        
        item_values = self.tree.item(selected_item)['values']
        print(f"Editing record: {item_values}")
        # Here you would open a popup pre-filled with item_values

    def delete_action(self):
        """Identifies selected row and removes it."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a row to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?")
        if confirm:
            item_values = self.tree.item(selected_item)['values']
            print(f"Deleting record with ID: {item_values[0]}")
            # Run SQL: DELETE FROM table WHERE id = item_values[0]
            self.tree.delete(selected_item)

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
    def __init__(self):
        super().__init__()
        self.geometry("400x200")
        self.title("Editable Label Demo")


        # Initialize our custom widget
        self.editable_field = ClickableLabel(self)
        self.editable_field.pack(side="top", anchor="nw", padx=5, pady=5)

        self.categories = ["Engineering", "Marketing", "Sales", "HR"]
        
        # 2. Store Table References
        # This dict will map Tab Names -> MySQLDataTable objects
        self.table_widgets = {}

        # 3. Create TabView with a 'command' callback
        self.tabview = ctk.CTkTabview(
            self, 
            command=self.on_tab_switched, # <--- Triggered on click
            segmented_button_selected_color="#1f538d"
        )
        self.tabview.pack(expand=True, fill="both", padx=20, pady=20)

        # 4. Pre-create the tab structures
        for name in self.categories:
            tab_object = self.tabview.add(name)
            
            # Create the table widget inside the tab immediately
            # but leave it empty for now
            table = MySQLDataTable(tab_object, columns=("ID", "Name", "Department", "Status"))
            table.pack(expand=True, fill="both")
            
            # Save reference to the table so we can update it later
            self.table_widgets[name] = table

        # 5. Load the initial tab manually on startup
        self.on_tab_switched()

    def on_tab_switched(self):
        """This runs every time the user clicks a tab."""
        selected_tab = self.tabview.get()
        print(f"User switched to: {selected_tab}")

        # Get the specific table widget for this tab
        target_table = self.table_widgets[selected_tab]

        # Simulation: Fetching data based on the tab name
        # In production, replace this with: 
        # data = db.execute(f"SELECT * FROM employees WHERE dept='{selected_tab}'")
        db_results = self.get_data(selected_tab)

        # Insert the data into the widget
        target_table.load_data(db_results)

    def get_data(self, department):
        """Generates dynamic data based on the tab name."""
        return [
            (department, "Alice", department, "Online"),
            ("102", "Bob", department, "Away"),
            ("103", "Charlie", department, "Busy"),
        ]

if __name__ == "__main__":
    server = Connection()
    
    frontend = MainApp()
    frontend.mainloop()

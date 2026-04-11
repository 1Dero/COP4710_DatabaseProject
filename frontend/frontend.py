#IMPROTS 
import customtkinter as ctk
import api
import os
import sys

# ACCESS SERVER
# Get the absolute path to the directory containing this script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the path to the parent directory
parent_dir = os.path.dirname(current_dir)
# Add the parent directory to sys.path
sys.path.append(parent_dir)
from server.api import CRUDApp, get_db_connection


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



class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x200")
        self.title("Editable Label Demo")


        # Initialize our custom widget
        self.editable_field = ClickableLabel(self)
        self.editable_field.pack(side="top", anchor="nw", padx=5, pady=5)

if __name__ == "__main__":
    server = CRUDApp()
    frontend = MainApp()
    frontend.mainloop()

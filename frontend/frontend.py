import api
import os
import sys
# Get the absolute path to the directory containing this script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the path to the parent directory
parent_dir = os.path.dirname(current_dir)
# Add the parent directory to sys.path
sys.path.append(parent_dir)
from server.api import CRUDApp, get_db_connection

if __name__ == '__main__':
    app= CRUDApp()
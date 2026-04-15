from frontend.frontend import *
from server.api import * 

if __name__ == "__main__":
    server = Connection()
    
    frontend = MainApp(server)
    frontend.mainloop()
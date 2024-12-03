import threading
import time
from gui import App
from tools_definition import *
from helpers import *
from tools import *
import logging

def main():
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Start the GUI
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
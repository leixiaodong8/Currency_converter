"""
Convenience script to get python file path (both in executable and in script).
Stores the paths in constants.
"""

import os
import sys
from appdirs import *


# getting database path
DATA_DIR = user_data_dir(appname="Currency Converter", appauthor="Leixiaodong8")
DB_DIR = os.path.join(DATA_DIR, "Databases")
DB = os.path.join(DB_DIR, "Currencies.db")

# getting other paths
BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRAPER_DIR = os.path.join(BASE_DIR, "currency_scraper")
GUI_DIR = os.path.join(BASE_DIR, "Gui")
MAIN_FILE = os.path.join(GUI_DIR, "main.ui")
ICON = os.path.join(GUI_DIR, "Images", "currencies.ico")

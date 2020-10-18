# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
"""
This pipeline takes items from the 'investor' spider and
dumps the data into a Sqlite3 database
"""

import os
import sys
import sqlite3 as sql3
from appdirs import *


# getting directory for database
DATA_DIR = user_data_dir(appname="Currency Converter", appauthor="Leixiaodong8")
DB_DIR = os.path.join(DATA_DIR, "Databases")
DB = os.path.join(DB_DIR, "Currencies.db")

class Sqlite3Pipeline:

    def __init__(self):
        self.conn = sql3.connect(DB)
        self.cursor = self.conn.cursor()
        

    def process_item(self, item, spider):
        """Passes item to `switcher()` function"""
        self.switcher(item)
        return item

    def switcher(self, item):
        """Passes item to `dump_db()` function using 'switch statements'"""
        switch_cases = {
            "brazilian_real": lambda: self.dump_db(
                *[value for key, value in item.items() if key != "brazilian_real"]
                ),
            "american_dollar": lambda: self.dump_db(
                *[value for key, value in item.items() if key != "american_dollar"]
                ),
            "european_euro": lambda: self.dump_db(
                *[value for key, value in item.items() if key != "european_euro"]
                ),
            "british_pound": lambda: self.dump_db(
                *[value for key, value in item.items() if key != "british_pound"]
                ),
            "japanese_yen": lambda: self.dump_db(
                *[value for key, value in item.items() if key != "japanese_yen"]
                ),
            "swiss_frank": lambda: self.dump_db(
                *[value for key, value in item.items() if key != "swiss_frank"]
                ),
            "canadian_dollar": lambda: self.dump_db(
                *[value for key, value in item.items() if key != "canadian_dollar"]
                ),
            "australian_dollar": lambda: self.dump_db(
                *[value for key, value in item.items() if key != "australian_dollar"]
                )
            }
        # item["name"] will determine which case to choose from
        case = switch_cases.get(item["name"], lambda: Exception("Invalid item"))
        return case()

    def dump_db(self, *args):
        """Dumps data into database and commits changes using context manager"""
        values = []
        for arg in args:
            if isinstance(arg, float): # float values are already in order, so this works
                values.append(arg)
            elif isinstance(arg, str):
                item_name = arg
            else:
                date = arg
        with self.conn:
            self.cursor.execute(
                """
                INSERT INTO {} VALUES(
                    ?, ?, ?, ?, ?, ?, ?, ?
                )
                """.format(item_name),
                (*values, date)
            )

    def close_spider(self, spider):
        """
        Runs `VACUUM` command to reset `rowid` values and closes connection to database
        after closing the spider (`close_spider()` is a defalut function in scrapy)
        """
        with self.conn:
            self.cursor.execute("""VACUUM""")
        self.conn.close()

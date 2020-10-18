"""Convenience functions to create and retrieve information from database"""

from __future__ import absolute_import
import os
import sqlite3 as sql3
from .get_path import DB_DIR, DB


def create_tables(*args):
    """Creates tables if they don't exist, with columns being determined by `args`"""
    conn = sql3.connect(DB)
    cursor = conn.cursor()
    if len(args) == 8:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS {}(
                {} REAL,
                {} REAL,
                {} REAL,
                {} REAL,
                {} REAL,
                {} REAL,
                {} REAL,
                date TEXT
            )
            """.format(*args)
        )
    else:
        raise IndexError("Invalid number of arguments")


def create_triggers(*args):
    """
    Creates trigger to dinamically delete items if item's number >= 720 (2 years of records)
    before adding new elements
    """
    conn = sql3.connect(DB)
    cursor = conn.cursor()
    with conn: # commits changes automatically, with no need to conn.commit()
        if len(args) == 2:
            cursor.execute(
                """
                CREATE TRIGGER IF NOT EXISTS {trigger}
                    BEFORE INSERT ON {table}
                    WHEN (SELECT COUNT(*) FROM {table}) >= 720
                BEGIN
                    /*
                    delete first registered element
                    from https://stackoverflow.com/a/31872916/13825145
                    */
                    DELETE FROM {table} WHERE rowid IN (
                        SELECT rowid FROM {table} ORDER BY rowid ASC LIMIT 1
                        );
                END;
                """.format(trigger=args[0], table=args[1])
            )
        else:
            raise IndexError("Invalid number of arguments")


def create_database():
    """Creates database with all tables and triggers ready"""
    currency_list = [
        "brazilian_real",
        "american_dollar",
        "european_euro",
        "british_pound",
        "japanese_yen",
        "swiss_frank",
        "canadian_dollar",
        "australian_dollar"
    ]
    # Creates database directory if it doesn't exist yet (with exist_of flag set to True)
    os.makedirs(DB_DIR, exist_ok=True)
    # swithcing places using a temp variable to store the value from list at current iteration
    trigger_num = 0
    for currency in currency_list:
        temp = currency_list[currency_list.index(currency)]
        currency_list[currency_list.index(currency)] = currency_list[0]
        currency_list[0] = temp
        create_tables(*currency_list)
        create_triggers("trigger{}".format(trigger_num), currency_list[0])
        trigger_num += 1


def select_records(table_name, records_num):
    """Loads selected ammount of records from selected table"""
    conn = sql3.connect(DB)
    cursor = conn.cursor()
    with conn:
        cursor.execute(
            """SELECT * FROM {} ORDER BY rowid DESC LIMIT {}""".format(table_name, str(records_num))
        )
    return cursor.fetchall()


def load_all(table_name):
    """Loads all records from selected table"""
    conn = sql3.connect(DB)
    cursor = conn.cursor()
    with conn:
        cursor.execute(
            """SELECT * FROM {} ORDER BY rowid DESC""".format(table_name)
        )
    return cursor.fetchall()

"""Contains all warnings"""

from __future__ import absolute_import
import os
import sys
from PyQt5.QtWidgets import QMessageBox
from .load_db import create_database
from .get_path import DB_DIR


def on_loading_values():
    """
    If there are not enough items in the database this error will be prompted
    recommending the user to update the database
    """
    message = QMessageBox()
    message.setWindowTitle("Not enough items in the database")
    message.setText(
        """There are not enough items in the database, please update by clicking "update database"."""
        )
    message.setIcon(QMessageBox.Warning)
    message.setStandardButtons(QMessageBox.Ok)
    # to make it work a .exec_() function needs to be included
    message.exec_()

def update_notification():
    """Prompts the user after updating values from the database"""
    message = QMessageBox()
    message.setWindowTitle("Update successfull!")
    message.setText(
        "Successfully updated values from the database."
        )
    message.exec_()

def on_clicked_delete():
    """Before deleting the database, this message will be prompted"""
    message = QMessageBox()
    message.setWindowTitle("Delete database?")
    message.setText(
        "Are you sure you want to delete the database? All data will be lost."
        )
    message.setIcon(QMessageBox.Warning)
    message.setStandardButtons(QMessageBox.Ok|QMessageBox.Cancel)
    message.setDefaultButton(QMessageBox.Cancel)
    # adding functionality
    message.buttonClicked.connect(on_clicked_warning)
    message.exec_()

def warning_file_not_found():
    message = QMessageBox()
    message.setWindowTitle("File not found")
    message.setText("There are no database files in the system.")
    message.setIcon(QMessageBox.Warning)
    message.setStandardButtons(QMessageBox.Ok)
    message.exec_()

def warning_already_updated():
    """
    TEMPORARY FIX:
    When triyng to update the database for a second time, this message will be raised
    asking the user to restart the application so that it can run the spider again
    """
    message = QMessageBox()
    message.setWindowTitle("Alredy updated database")
    message.setText(
        "Already updated the database in this session. Please restart the program to update."
    )
    message.setIcon(QMessageBox.Warning)
    message.setStandardButtons(QMessageBox.Ok|QMessageBox.Cancel)
    message.setDefaultButton(QMessageBox.Ok)
    # adding functionality
    message.buttonClicked.connect(on_clicked_update_warning)
    message.exec_()

def on_clicked_warning(button):
    if button.text() == "OK":
        os.chdir(DB_DIR)
        try:
            os.remove("Currencies.db")
            create_database() # creates empty database again to prevent errors
        except FileNotFoundError:
            warning_file_not_found()

def on_clicked_update_warning(button):
    if button.text() == "OK":
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
"""Establishes connection to `.ui` file and loads GUI"""

import os
import sys
import qt5reactor
from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem
from twisted.internet import reactor, error
from scrapy import crawler
from Gui import gui_warnings
from Gui.get_path import GUI_DIR, DB_DIR, MAIN_FILE, ICON
from Gui.load_db import create_database, select_records, load_all
from Gui.graphs import Canvas
from currency_scraper.currency_scraper.spiders.investor import InvestorSpider


TITLE = "Currency Converter"

class MainWindow(QMainWindow):
    """Implements logic into static GUI"""

    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi(MAIN_FILE, self)
        self.setWindowTitle(TITLE)
        self.setWindowIcon(QIcon(ICON))

        # string to handle number values
        self.arg_nums = []

        """
        ADDING FUNCTIONALITY - WIDGET NAMES FOUND INSIDE .UI FILE
        """
        # graph, history and title
        self.choose_currency.currentTextChanged.connect(self.on_chosen_currency)
        self.choose_relation_currency.currentTextChanged.connect(self.on_chosen_relation_currency)

        # load currency values and change symbols
        self.choose_currency_conversion_top.currentTextChanged.connect(
            lambda: self.on_chosen_currency_combobox(self.choose_currency_conversion_top)
            )
        self.choose_currency_conversion_bottom.currentTextChanged.connect(
            lambda: self.on_chosen_currency_combobox(self.choose_currency_conversion_bottom)
            )

        # determine which label was selected with a click
        # logic for buttons is implemented within on_mouse_selected_currency
        self.currency_value_top.mouseReleaseEvent = lambda event: self.on_mouse_selected_currency(
            event, self.currency_value_top
            )
        self.currency_value_bottom.mouseReleaseEvent = lambda event: self.on_mouse_selected_currency(
            event, self.currency_value_bottom
            )

        # clear and back buttons have their own functionalities
        self.clear_button.clicked.connect(self.on_clear_button)
        self.back_button.clicked.connect(self.on_back_button)

        # update and delete buttons
        self.update_db_button.clicked.connect(self.on_clicked_update)
        self.delete_db_button.clicked.connect(gui_warnings.on_clicked_delete)


    def on_chosen_currency(self):
        """Shows title, table and graph for selected currency on `choose_currency` combobox"""
        main_currency_title = self.choose_currency.currentText()
        # the string needs to be modified to be compatible with the database values
        main_currency = main_currency_title.replace(" ", "_").lower()
        relation_currency = self.choose_relation_currency.currentText().replace(" ", "_").lower()
        # graph
        if len(load_all(main_currency)) < 2:
            gui_warnings.on_loading_values()
        else:
            try:
                canvas = Canvas(relation_currency, self)
                canvas.plot(main_currency)
            except ValueError:
                pass # plots empty graph if main_currency = relation_currency
            self.clear_graph_layout(self.graph_layout)
            self.graph_layout.addWidget(canvas)
        # title
        self.gui_title.setText(main_currency_title)
        # table
        self.currency_table.setRowCount(0)
        currency_list = [
            "Brazilian Real",
            "American Dollar",
            "European Euro",
            "British Pound",
            "Japanese Yen",
            "Swiss Frank",
            "Canadian Dollar",
            "Australian Dollar"
        ]
        for currency in currency_list:
            temp = currency_list[currency_list.index(currency)]
            currency_list[currency_list.index(currency)] = currency_list[0]
            currency_list[0] = temp
            if main_currency_title == currency:
                self.currency_table.setHorizontalHeaderLabels((*currency_list[1:], "Date"))
        # from https://www.youtube.com/watch?v=l2OoXj1Z2hM&t=411s
        records = enumerate(load_all(main_currency))
        for row_num, row_data in records:
            self.currency_table.insertRow(row_num)
            for column_num, data in enumerate(row_data):
                self.currency_table.setItem(
                    row_num, column_num, QTableWidgetItem(str(data))
                    )

    def on_chosen_relation_currency(self):
        """
        Shows graph for selected currency on `choose_relation_currency` combobox
        in relation to selected currency on `choose_currency` combobox
        """
        main_currency = self.choose_currency.currentText().replace(" ", "_").lower()
        relation_currency = self.choose_relation_currency.currentText().replace(" ", "_").lower()
        if len(load_all(main_currency)) < 2:
            gui_warnings.on_loading_values()
        else:
            try:
                canvas = Canvas(relation_currency, self)
                canvas.plot(main_currency.replace(" ", "_").lower())
            except ValueError:
                pass
            self.clear_graph_layout(self.graph_layout)
            self.graph_layout.addWidget(canvas)

    # from https://stackoverflow.com/a/10067548/13825145
    def clear_graph_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def on_chosen_currency_combobox(self, combobox):
        """
        Changes currency symbol and loads database value for the currency selected
        with the chosen widget
        """
        main_currency = combobox.currentText()
        main_currency = main_currency.replace(" ", "_").lower()
        switch_cases = {
            "brazilian_real": "R$",
            "american_dollar": "$",
            "european_euro": "€",
            "british_pound": "£",
            "japanese_yen": "¥",
            "swiss_frank": "CHF",
            "canadian_dollar": "$",
            "australian_dollar": "$"
        }
        case = switch_cases.get(main_currency)
        symbol_top = self.currency_value_top.text().split()[0]
        symbol_bottom = self.currency_value_bottom.text().split()[0]
        if combobox == self.choose_currency_conversion_top:
            self.currency_value_top.setText("{} 1.0".format(case))
            self.currency_value_bottom.setText("{} 1.0".format(symbol_bottom))
        else:
            self.currency_value_bottom.setText("{} 1.0".format(case))
            self.currency_value_top.setText("{} 1.0".format(symbol_top))
        # resetting arg_nums everytime there's a new combobox click
        self.arg_nums = []

    def on_mouse_selected_currency(self, event, label):
        """
        Changes font to bold if currency is selected and passes it to `buttons_logic()`.
        """
        font_bold = QFont("Microsoft Sans Serif", 36)
        font_bold.setBold(True)
        default_font = QFont("Microsoft Sans Serif", 36)
        default_font.setBold(False)
        label.setFont(font_bold)
        if label == self.currency_value_top:
            self.currency_value_bottom.setFont(default_font)
        else:
            self.currency_value_top.setFont(default_font)
        self.buttons_logic(label)
        # resetting arg_nums everytime there's a new mouse click event
        self.arg_nums = []

    def buttons_logic(self, label):
        """Disconnects old connection and reconnects button logic to selected currency"""
        try:
            # from https://stackoverflow.com/a/21587045/13825145
            for n in range(0, 10):
                getattr(self, "num_{}".format(n)).clicked.disconnect()
            self.float_value_button.disconnect()
        # if button has not established any connections yet, this error will occur
        except TypeError:
            pass
        # can't use loop because it only computes number 9
        self.num_0.clicked.connect(lambda: self.on_number_button_clicked(self.num_0, label))
        self.num_1.clicked.connect(lambda: self.on_number_button_clicked(self.num_1, label))
        self.num_2.clicked.connect(lambda: self.on_number_button_clicked(self.num_2, label))
        self.num_3.clicked.connect(lambda: self.on_number_button_clicked(self.num_3, label))
        self.num_4.clicked.connect(lambda: self.on_number_button_clicked(self.num_4, label))
        self.num_5.clicked.connect(lambda: self.on_number_button_clicked(self.num_5, label))
        self.num_6.clicked.connect(lambda: self.on_number_button_clicked(self.num_6, label))
        self.num_7.clicked.connect(lambda: self.on_number_button_clicked(self.num_7, label))
        self.num_8.clicked.connect(lambda: self.on_number_button_clicked(self.num_8, label))
        self.num_9.clicked.connect(lambda: self.on_number_button_clicked(self.num_9, label))
        self.float_value_button.clicked.connect(
            lambda: self.on_number_button_clicked(self.float_value_button, label)
            )

    def on_number_button_clicked(self, button, label):
        """
        Adds value typed to the screen and calculates related currency
        with values loaded from the database
        """
        currency_top = self.choose_currency_conversion_top.currentText()
        currency_top = currency_top.replace(" ", "_").lower()
        symbol_top = self.currency_value_top.text().split()[0]
        currency_bottom = self.choose_currency_conversion_bottom.currentText()
        currency_bottom = currency_bottom.replace(" ", "_").lower()
        symbol_bottom = self.currency_value_bottom.text().split()[0]
        values_top = self.get_values(currency_top)
        values_bottom = self.get_values(currency_bottom)

        # 0 at index 1 should not be computed again
        # and should be overriden if another button is pressed
        if button.text() == "0" and self.arg_nums == ["0"]:
            pass
        elif button.text() != "0" and self.arg_nums == ["0"]:
            self.arg_nums[0] = button.text()
        elif button.text() == "." and self.arg_nums == []:
            self.arg_nums.append("0")
            self.arg_nums.append(button.text())
            self.arg_nums.append("00")
        elif button.text() != "0" and "".join(self.arg_nums) == "0.00":
            self.arg_nums[2] = button.text()
        else:
            self.arg_nums.append(button.text())

        arg_string = "".join(self.arg_nums)
        try:
            if label == self.currency_value_top and 0 < len(self.arg_nums) < 12:
                label.setText("{} {}".format(symbol_top, arg_string))
                try:
                    value_bottom = values_top[currency_bottom][0]
                    self.currency_value_bottom.setText(
                        "{} {}".format(symbol_bottom, str(round((float(arg_string) * value_bottom), 2)))
                        )
                except TypeError: # if the currency is the same in both comboboxes
                    self.currency_value_bottom.setText("{} {}".format(symbol_bottom, arg_string))
            elif label == self.currency_value_bottom and 0 < len(self.arg_nums) < 12:
                label.setText("{} {}".format(symbol_bottom, arg_string))
                try:
                    value_top = values_bottom[currency_top][0]
                    self.currency_value_top.setText(
                        "{} {}".format(symbol_top, str(round((float(arg_string) * value_top), 2)))
                        )
                except TypeError:
                    self.currency_value_top.setText("{} {}".format(symbol_top, arg_string))
        except IndexError:
            gui_warnings.on_loading_values()

    def get_values(self, currency):
        """Creates dict object dynamically depending on value of `currency` argument"""
        curr_dict = {
            "brazilian_real": None,
            "american_dollar": None,
            "european_euro": None,
            "british_pound": None,
            "japanese_yen": None,
            "swiss_frank": None,
            "canadian_dollar": None,
            "australian_dollar": None
        }
        index = 0
        for key in curr_dict:
            if key != currency:
                # list comprehension to get values from data
                curr_dict[key] = [
                    element for record in select_records(currency, 1) for element in record
                    if element == record[index] and isinstance(element, float)
                    ]
                index += 1
            else:
                continue
        return curr_dict

    def on_back_button(self):
        """Erases last digit typed"""
        symbol_top = self.currency_value_top.text().split()[0]
        symbol_bottom = self.currency_value_bottom.text().split()[0]    
        try:
            if len(self.arg_nums) == 1:
                self.currency_value_top.setText("{} 0.0".format(symbol_top))
                self.currency_value_bottom.setText("{} 0.0".format(symbol_bottom))
                self.arg_nums.pop()
            elif len(self.arg_nums) > 12: # max number displayed on screen
                self.arg_nums = self.arg_nums[:10]
                arg_string = "".join(self.arg_nums)
                self.currency_value_top.setText("{} {}".format(symbol_top, arg_string))
                self.currency_value_bottom.setText("{} {}".format(symbol_bottom, arg_string))
            else:
                self.arg_nums.pop()
                arg_string = "".join(self.arg_nums)
                self.currency_value_top.setText("{} {}".format(symbol_top, arg_string))
                self.currency_value_bottom.setText("{} {}".format(symbol_bottom, arg_string))
        except IndexError: # if the list is empty
            pass

    def on_clear_button(self):
        """Clears the screen when the CE button is pressed"""
        symbol_top = self.currency_value_top.text().split()[0]
        symbol_bottom = self.currency_value_bottom.text().split()[0]
        self.currency_value_top.setText("{} 0.0".format(symbol_top))
        self.currency_value_bottom.setText("{} 0.0".format(symbol_bottom))
        self.arg_nums = []

    def on_clicked_update(self):
        """Gives command to run scraper and fetch data from the website"""
        process = crawler.CrawlerProcess(
            {
                "USER_AGENT": "currency scraper",
                "SCRAPY_SETTINGS_MODULE": "currency_scraper.currency_scraper.settings",
                "ITEM_PIPELINES": {
                    "currency_scraper.currency_scraper.pipelines.Sqlite3Pipeline": 300,
                }
            }
        )
        process.crawl(InvestorSpider)
        try:
            process.start()
            gui_warnings.update_notification()
        except error.ReactorNotRestartable:
            gui_warnings.warning_already_updated()

    def closeEvent(self, event):
        """Default PyQt5 function when closing the program"""
        super(MainWindow, self).closeEvent(event)
        try:
            reactor.stop()
        except error.ReactorNotRunning: # if reactor has not been run in the session
            pass


def open_window():
    """Initiates instance of the class `MainWindow()` and opens GUI"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    create_database()
    open_window()
    qt5reactor.install()
    reactor.run()

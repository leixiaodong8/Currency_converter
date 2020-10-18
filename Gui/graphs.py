"""Graphs for all currencies will be made based on the class Canvas"""


from __future__ import absolute_import
import datetime as dt
from matplotlib import use
from matplotlib import style
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# using absolute import when __name__ != "__main__"
from .load_db import load_all


class Canvas(FigureCanvas):
    """Draws graph of currencies in PyQt5 canvas"""
    use("Qt5Agg")

    def __init__(self, currency, parent=None, width=5, height=5, dpi=80):
        self.CURR = currency
        self.DATA = load_all(self.CURR)
        self.TIME = [
            dt.datetime.strptime(element, "%Y-%m-%d %H:%M:%S.%f")
            for record in self.DATA for element in record if element == record[-1]
        ]
        self.values = self.get_currency_values()
        # canvas related
        fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

    def get_currency_values(self):
        """Creates dict object dynamically depending on value of CURR"""
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
            if key != self.CURR:
                # list comprehension to get values from data
                curr_dict[key] = [
                    element for record in self.DATA for element in record
                    if element == record[index] and isinstance(element, float)
                ]
                index += 1
            else:
                continue
        return curr_dict

    def plot(self, currency):
        """Plots graph with data retrieved from database"""
        curr = self.CURR.replace("_", " ").title()
        name = currency.replace("_", " ").title()
        style.use("seaborn-notebook")
        # position=[left, bottom, width, height] in add_subplot function
        graph = self.figure.add_subplot(111, position=[0.115, 0.15, 0.84, 0.75])
        graph.set_xlabel("Time")
        graph.set_ylabel("Value in relation to {}".format(name))
        graph.plot(self.TIME, self.values[currency], label=curr, linewidth=1.8)
        # if label argument is passed in graph.plot there's no need to define it in graph.legend()
        graph.legend()

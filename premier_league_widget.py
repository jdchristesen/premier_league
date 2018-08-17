# -*- coding: utf-8 -*-
"""
Created on Fri Sep  9 16:23:50 2016

@author: manu
"""
import urllib.request
from bs4 import BeautifulSoup
import os
import json
import matplotlib.pyplot as plt
from matplotlib.offsetbox import (TextArea, DrawingArea, OffsetImage,
                                  AnnotationBbox)
from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import re
import numpy as np
import get_data
from caan_table_widget import CaanTable
from season_schedule_widget import SeasonScheduleTable


class GenericThread(QtCore.QThread):
    """
    This class allows for various methods to be run on their own thread. It
    takes in a callable function (method) and a list of args and kwargs, and
    then calls the function when the thread is started.
    """

    def __init__(self, method, *args, **kwargs):
        QtCore.QThread.__init__(self)
        self.method = method
        self.args = args
        self.kwargs = kwargs

    def __del__(self):
        self.wait()

    def run(self):
        """
        Default method which is called when QThread.start() is run. It calls the
        function with arguments of args and kwargs
        """
        self.method(*self.args, **self.kwargs)


class PremierLeagueWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setObjectName('Premier League Widget')
        main_layout = QtWidgets.QHBoxLayout(self)
        self.tab = QtWidgets.QTabWidget()
        self.caan_table = CaanTable()
        self.season_schedule = SeasonScheduleTable()

        self.tab.addTab(self.caan_table, 'Caan Table')
        self.tab.addTab(self.season_schedule, 'Season Schedule')

        main_layout.addWidget(self.tab)

        self.caan_table.update_table()
        self.season_schedule.update_table()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    premier_league_widget = PremierLeagueWidget()
    premier_league_widget.show()
    app.exec_()
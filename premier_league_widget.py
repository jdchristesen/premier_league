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
        self.caan_table = QtWidgets.QTableWidget()

        self.tab.addTab(self.caan_table, 'Caan Table')
        main_layout.addWidget(self.tab)
        self.update_caan_table()
        self.resize()

    def update_caan_table(self, **kwargs):

        image_size = kwargs.get('image-size', 50)
        year = kwargs.get('year', 2018)
        str_year = '{}-{}'.format(year, int(str(year)[-2:]) + 1)

        if not os.path.isfile('premier_league_table_{}.json'.format(str_year)):
            return

        with open('premier_league_table_{}.json'.format(str_year)) as fp:
            teams = json.load(fp)

        with open('premier_league_teams.json'.format(str_year)) as fp:
            teams_abbr = json.load(fp)

        with open('.badge-{}.json'.format(image_size)) as fp:
            pos = json.load(fp)

        max_points = max([int(x['Pts']) for x in teams])
        self.caan_table.setRowCount(max_points + 1)
        self.caan_table.setColumnCount(20)
        print([str(max_points - i) for i in range(max_points + 1)])
        self.caan_table.setVerticalHeaderLabels([str(max_points - i)
                                       for i in range(max_points + 1)])
        for i in range(self.caan_table.rowCount()):
            self.caan_table.setRowHeight(i, image_size)

        for i in range(self.caan_table.columnCount()):
            self.caan_table.setColumnWidth(i, image_size)

        point_totals = {}
        for team in teams:
            team_name = team.get('Team', None)
            points = team.get('Pts', None)
            if team_name is None or points is None:
                continue

            if points in point_totals:
                point_totals[points] += 1
            else:
                point_totals[points] = 1

            image_loc = 'images/badges-{}-sprite.png'.format(image_size)
            if not os.path.isfile(image_loc):
                continue

            # Annotate the 2nd position with another image (a Grace Hopper portrait)
            team_pos = pos[
                '.badge-{}.{}'.format(image_size, teams_abbr[team_name])]
            x = 0 - int(team_pos[0])
            y = 0 - int(team_pos[1])
            label = QtWidgets.QLabel()
            pix_map = QtGui.QPixmap(image_loc)
            crop = QtCore.QRect(x, y, image_size, image_size)
            cropped = pix_map.copy(crop)
            label.setPixmap(cropped)
            self.caan_table.setCellWidget(max_points - int(points),
                                point_totals[points] - 1,
                                label)

        self.caan_table.setColumnCount(max([x for x in point_totals.values()]))

        # self.caan_table.show()
        # vwidth = self.caan_table.verticalHeader().width()
        # hwidth = self.caan_table.horizontalHeader().length()
        # swidth = self.caan_table.style().pixelMetric(QtWidgets.QStyle.PM_ScrollBarExtent)
        # self.caan_table.setFixedWidth(vwidth + hwidth + swidth)
        #
        # vheight = self.caan_table.verticalHeader().length()
        # hheight = self.caan_table.horizontalHeader().height()
        # sheight = self.caan_table.style().pixelMetric(QtWidgets.QStyle.PM_ScrollBarExtent)
        # self.caan_table.setFixedHeight(vheight + hheight + sheight)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    premier_league_widget = PremierLeagueWidget()
    premier_league_widget.show()
    app.exec_()
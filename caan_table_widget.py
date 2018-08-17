import sys
from PyQt5 import QtCore, QtWidgets, QtGui
import json
import os


class CaanTable(QtWidgets.QTableWidget):

    def __init__(self):
        super().__init__()
        self.horizontalHeader().hide()

    def sizeHint(self):
        horizontal = self.horizontalHeader()
        vertical = self.verticalHeader()
        frame = self.frameWidth() * 2
        return QtCore.QSize(horizontal.length() + vertical.width() + frame,
                            vertical.length() + horizontal.height() + frame)


    def update_table(self, **kwargs):

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
        self.setRowCount(max_points + 1)
        self.setColumnCount(20)
        print([str(max_points - i) for i in range(max_points + 1)])
        self.setVerticalHeaderLabels([str(max_points - i)
                                      for i in range(max_points + 1)])
        for i in range(self.rowCount()):
            self.setRowHeight(i, image_size)

        for i in range(self.columnCount()):
            self.setColumnWidth(i, image_size)

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
            self.setCellWidget(max_points - int(points),
                               point_totals[points] - 1,
                               label)

        self.setColumnCount(max([x for x in point_totals.values()]))
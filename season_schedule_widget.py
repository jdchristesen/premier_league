from PyQt5 import QtCore, QtWidgets, QtGui
import json
import os
import datetime


class SeasonScheduleTable(QtWidgets.QTableWidget):

    def __init__(self):
        super().__init__()
        self.setRowCount(38)
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels(['Team', 'Date', '2017/18',
                                        '2018/19', 'Current Points',
                                        'Difference', 'Predicted Points'])

    def sizeHint(self):
        horizontal = self.horizontalHeader()
        vertical = self.verticalHeader()
        frame = self.frameWidth() * 2
        return QtCore.QSize(horizontal.length() + vertical.width() + frame,
                            vertical.length() + horizontal.height() + frame)

    def update_table(self, **kwargs):

        image_size = kwargs.get('image-size', 50)
        year = kwargs.get('year', 2017)
        str_year = '{}-{}'.format(year, year + 1)

        if not os.path.isfile('Tottenham-Hotspur-results.json'):
            return

        with open('Tottenham-Hotspur-results.json') as fp:
            results = json.load(fp)

        with open('premier_league_teams.json'.format(str_year)) as fp:
            teams_abbr = json.load(fp)

        with open('.badge-{}.json'.format(image_size)) as fp:
            pos = json.load(fp)

        with open('premier_league_promotion_relegation.json') as fp:
            pro_rel = json.load(fp)

        for i in range(self.rowCount()):
            self.setRowHeight(i, image_size)

        self.setColumnWidth(0, image_size)

        image_loc = 'images/badges-{}-sprite.png'.format(image_size)
        if not os.path.isfile(image_loc):
            return

        games = results[str_year]
        prev_games = results['{}-{}'.format(year - 1, year)]
        current_running_points = 0
        prev_running_points = 0
        for i, game in enumerate(games):
            team_name = game.get('opponent', None)
            result = game.get('result', None)
            score = game.get('score', None)
            home_or_away = game.get('home_or_away', None)
            date = game.get('date', None)
            print(pro_rel[str_year])
            abbr = teams_abbr.get(team_name, None)
            if abbr in pro_rel[str_year]:
                current_game = [pro_rel[str_year][abbr], home_or_away]
            else:
                current_game = [abbr, home_or_away]

            for prev_game in prev_games:
                name = teams_abbr.get(prev_game['opponent'], None)
                if [name, prev_game['home_or_away']] == current_game:
                    label = QtWidgets.QLabel(prev_game['score'])
                    self.setCellWidget(i, 2, label)
                    if prev_game['result'] == 'W':
                        background = 'background-color: #bbf3bb'
                        prev_running_points += 3
                    elif prev_game['result'] == 'D':
                        prev_running_points += 1
                        background = 'background-color: #ffffbb'
                    else:
                        prev_running_points += 0
                        background = 'background-color: #ffbbbb'
                    self.cellWidget(i, 2).setStyleSheet(background)
                    break

            if date is not None:
                try:
                    date = datetime.datetime.strptime(date, '%A %d %B %Y')
                    label = QtWidgets.QLabel(date.strftime('%d/%m/%Y'))
                    self.setCellWidget(i, 1, label)
                except ValueError:
                    pass

            if team_name in teams_abbr:
                team_pos = pos['.badge-{}.{}'.format(image_size,
                                                        teams_abbr[team_name])]

                x = 0 - int(team_pos[0])
                y = 0 - int(team_pos[1])
                label = QtWidgets.QLabel('({})'.format(home_or_away))
                pix_map = QtGui.QPixmap(image_loc)
                crop = QtCore.QRect(x, y, image_size, image_size)
                cropped = pix_map.copy(crop)
                label.setPixmap(cropped)
                self.setCellWidget(i, 0, label)
            else:
                print(team_name)

            if result is not None and score is not None:
                label = QtWidgets.QLabel(score)
                self.setCellWidget(i, 3, label)
                background = ''
                if result == 'W':
                    background = 'background-color: #bbf3bb'
                    current_running_points += 3
                    self.setCellWidget(i, 4, QtWidgets.QLabel(
                        str(current_running_points)))
                elif result == 'D':
                    current_running_points += 1
                    self.setCellWidget(i, 4, QtWidgets.QLabel(
                        str(current_running_points)))
                    background = 'background-color: #ffffbb'
                else:
                    current_running_points += 0
                    self.setCellWidget(i, 4, QtWidgets.QLabel(
                        str(current_running_points)))
                    background = 'background-color: #ffbbbb'
                self.cellWidget(i, 3).setStyleSheet(background)
                diff = current_running_points - prev_running_points
                predict = current_running_points / (i + 1) * 38
                self.setCellWidget(i, 5, QtWidgets.QLabel(str(diff)))
                self.setCellWidget(i, 6, QtWidgets.QLabel(str(predict)))
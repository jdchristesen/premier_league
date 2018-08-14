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


def get_team_names():
    base_url = 'https://www.premierleague.com'
    with urllib.request.urlopen(base_url + '/tables') as response:
        html = response.read()

    soup = BeautifulSoup(html.decode(), 'html.parser')

    teams = []
    for team in soup.find_all('td', {'class': 'team'}):
        long_name = team.find('span', {'class': 'long'}).contents[0]
        short_name = team.find('span', {'class': 'short'}).contents[0]
        teams.append((long_name, short_name))

        if not os.path.isfile('images\\{}_logo.png'.format(long_name)):
            logo_url = team.find('a')['href']
            with urllib.request.urlopen(base_url + logo_url) as response:
                html = response.read()

            image_soup = BeautifulSoup(html.decode(), 'html.parser')
            image_url = image_soup.find('img', {'class': 'clubBadgeFallback'})
            urllib.request.urlretrieve('http:' + image_url['src'], long_name + '_logo.png')

    with open('premier_league_teams.json', 'w') as f:
        json.dump(teams[:20], f, indent=2)

    with open('all_teams.json', 'w') as f:
        json.dump(teams, f, indent=2)


def get_table(**kwargs):
    base_url = 'https://en.wikipedia.org/wiki/{}_Premier_League'
    year = kwargs.get('year', 2018)
    str_year = '{}-{}'.format(year, int(str(year)[-2:]) + 1)
    with urllib.request.urlopen(base_url.format(str_year)) as response:
        html = response.read()

    soup = BeautifulSoup(html.decode(), 'html.parser')
    header = soup.find('span', {'id': 'League_table'}).parent
    table = header.find_next_sibling('table')
    headers = table.find('tr')
    team_dict_str = []
    for header in headers.find_all('th'):
        child = header.contents[0]
        if child.string is None and child.has_attr('title'):
            team_dict_str.append(child.title)
        else:
            team_dict_str.append(child.string)

    teams = []
    rows = table.find_all('tr')
    for row in rows[1:]:
        team_dict = {}
        elements = row.contents
        elements = list(filter(lambda a: a != '\n', elements))
        for i, element in enumerate(elements):
            if element.string is None:
                if element.find('a') and element != elements[-1]:
                    val = element.a.string.replace(u'\u2212', '-')
                    team_dict[team_dict_str[i]] = val
                    team_dict['link'] = element.a['href']
            else:
                val = element.string.rstrip().replace(u'\u2212', '-')
                team_dict[team_dict_str[i]] = val
        teams.append(team_dict)

    with open('premier_league_table_{}.json'.format(str_year), 'w') as fp:
        json.dump(teams, fp, indent=2)

    with open('premier_league_teams_links.json', 'w') as fp:
        team_data = {}
        for team in teams:
            team_data[team['Team']] = team['link']
        json.dump(team_data, fp, indent=2)


def caan_table_pyqt5(**kwargs):
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('Caan Table')
    table = QtWidgets.QTableWidget()

    image_size = kwargs.get('image-size', 50)
    year = kwargs.get('year', 2018)
    str_year = '{}-{}'.format(year, int(str(year)[-2:]) + 1)

    if not os.path.isfile('premier_league_table_{}.json'.format(str_year)):
        get_table(year=year)

    with open('premier_league_table_{}.json'.format(str_year)) as fp:
        teams = json.load(fp)

    with open('premier_league_teams.json'.format(str_year)) as fp:
        teams_abbr = json.load(fp)

    with open('.badge-{}.json'.format(image_size)) as fp:
        pos = json.load(fp)

    max_points = max([int(x['Pts']) for x in teams])
    table.setRowCount(max_points + 1)
    table.setColumnCount(20)
    print([str(max_points - i) for i in range(max_points + 1)])
    table.setVerticalHeaderLabels([str(max_points - i)
                                     for i in range(max_points + 1)])
    for i in range(table.rowCount()):
        table.setRowHeight(i, image_size)

    for i in range(table.columnCount()):
        table.setColumnWidth(i, image_size)

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
        team_pos = pos['.badge-{}.{}'.format(image_size, teams_abbr[team_name])]
        x = 0 - int(team_pos[0])
        y = 0 - int(team_pos[1])
        label = QtWidgets.QLabel()
        pix_map = QtGui.QPixmap(image_loc)
        print(pix_map.size())
        print(team_name, x, y)
        print(image_size)
        crop = QtCore.QRect(x, y, image_size, image_size)
        cropped = pix_map.copy(crop)
        label.setPixmap(cropped)
        table.setCellWidget(max_points - int(points), point_totals[points] - 1,
                            label)

    table.setColumnCount(max([x for x in point_totals.values()]))

    table.show()
    vwidth = table.verticalHeader().width()
    hwidth = table.horizontalHeader().length()
    swidth = table.style().pixelMetric(QtWidgets.QStyle.PM_ScrollBarExtent)
    table.setFixedWidth(vwidth + hwidth + swidth )

    vheight = table.verticalHeader().length()
    hheight = table.horizontalHeader().height()
    sheight = table.style().pixelMetric(QtWidgets.QStyle.PM_ScrollBarExtent)
    table.setFixedHeight(vheight + hheight + sheight)

    sys.exit(app.exec_())


def caan_table(**kwargs):
    # plt.rcParams["figure.dpi"] = 140
    zoom_factor = kwargs.get('zoom_factor', 0.25)
    image_size = kwargs.get('image-size', 50)
    year = kwargs.get('year', 2018)
    str_year = '{}-{}'.format(year, int(str(year)[-2:]) + 1)

    if not os.path.isfile('premier_league_table_{}.json'.format(str_year)):
        get_table(year=year)

    with open('premier_league_table_{}.json'.format(str_year)) as fp:
        teams = json.load(fp)

    with open('premier_league_teams.json'.format(str_year)) as fp:
        teams_abbr = json.load(fp)

    fig, ax = plt.subplots()
    arr_img = plt.imread('images/badges-{}-sprite.png'.format(image_size),
                         format='png')
    with open('.badge-{}.json'.format(image_size)) as fp:
        pos = json.load(fp)

    point_totals = {}
    for team in teams:

        team_name = team.get('Team', None)
        print(team_name)
        points = team.get('Pts', None)
        if team_name is None or points is None:
            continue

        if points in point_totals:
            point_totals[points] += 1
        else:
            point_totals[points] = 1

        # Annotate the 2nd position with another image (a Grace Hopper portrait)
        team_pos = pos['.badge-{}.{}'.format(image_size, teams_abbr[team_name])]
        y = 0 - int(team_pos[0])
        x = 0 - int(team_pos[1])
        print(x, y)
        print(int(team_pos[0]), int(team_pos[1]))
        mask = np.zeros(arr_img.shape)
        mask[x:x + image_size, y:y + image_size] = 1
        m = mask > 0

        width = 500  # pixels
        height = 150
        margin = 50  # pixels
        dpi = 100.  # dots per inch

        figsize = (
        (width + 2 * margin) / dpi, (height + 2 * margin) / dpi)  # inches
        left = margin / dpi / figsize[0]  # axes ratio
        bottom = margin / dpi / figsize[1]
        image = arr_img[m].reshape((y + image_size - y, x + image_size - x, 4))
        plt.imshow(image, interpolation='nearest')
        break
        imagebox = OffsetImage(image)
        imagebox.image.axes = ax

        ab = AnnotationBbox(imagebox, (point_totals[points], int(points)),
                            # xybox=(120., -80.),
                            xycoords='data',
                            # boxcoords='offset points',
                            frameon=False
                            # pad=0.5
                            # arrowprops=dict(
                            #     arrowstyle="->",
                            #     connectionstyle="angle,angleA=0,angleB=90,rad=3")
                            )

        ax.add_artist(ab)
        # ax.add_artist(imagebox)

    # Fix the display limits to see everything
    # xlim = -1
    # ylim = -1
    # for key, value in point_totals.items():
    #     xlim = max(xlim, value)
    #     ylim = max(ylim, int(key))
    # ax.set_xlim(0, xlim)
    # ax.set_ylim(0, ylim)
    # ax.spines['top'].set_visible(False)
    # ax.spines['right'].set_visible(False)
    # ax.spines['bottom'].set_visible(False)
    # ax.spines['left'].set_visible(False)
    plt.show()


def team_seasons(**kwargs):
    team_name = kwargs.get('team_name', 'Tottenham Hotspur')
    start_year = kwargs.get('start_year', 2015)
    end_year = kwargs.get('end_year', 2018)
    fig, ax = plt.subplots()
    for year in range(start_year, end_year + 1):
        print(year)
        str_year = '{}-{}'.format(year, int(str(year)[-2:]) + 1)

        with open('premier_league_teams_links.json') as fp:
            teams = json.load(fp)

        if team_name not in teams:
            return

        base_url = 'https://en.wikipedia.org/wiki/'
        team_link = '{}_{}_season'.format(str_year, teams[team_name].split('/')[-1])
        print(base_url + team_link)
        with urllib.request.urlopen(base_url + team_link) as response:
            html = response.read()

        soup = BeautifulSoup(html.decode(), 'html.parser')
        header = soup.find('span', {'id': re.compile('Results_by_*')}).parent
        table = header.find_next_sibling('table')
        rows = table.find_all('tr')
        points_tally = [0]
        for row in rows:
            elements = row.contents
            elements = list(filter(lambda a: a != '\n', elements))
            for element in elements:
                points = None
                if isinstance(element.string, str):
                    element.string = element.string.rstrip()
                if element.string == 'W':
                    points = 3
                elif element.string == 'D':
                    points = 1
                elif element.string == 'L':
                    points = 0

                if points is not None:
                    points_tally.append(points + points_tally[-1])

        ax.plot(points_tally, label=str_year, marker='.', markersize=8,
                linewidth=1)
        print(points_tally)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels)
    ax.set_xlabel('Matchday')
    ax.set_ylabel('Points')
    ax.set_title('{} Points Tally from {} to {}'.format(team_name, start_year,
                                                        end_year))
    plt.show()


def compare_teams(**kwargs):
    team_names = kwargs.get('team_names', ['Tottenham Hotspur', 'Arsenal'])
    year = kwargs.get('year', 2015)
    fig, ax = plt.subplots()
    for team_name in team_names:
        str_year = '{}-{}'.format(year, int(str(year)[-2:]) + 1)

        with open('premier_league_teams_links.json') as fp:
            teams = json.load(fp)

        if team_name not in teams:
            return

        base_url = 'https://en.wikipedia.org/wiki/'
        team_link = '{}_{}_season'.format(str_year,
                                          teams[team_name].split('/')[-1])
        print(base_url + team_link)
        with urllib.request.urlopen(base_url + team_link) as response:
            html = response.read()

        soup = BeautifulSoup(html.decode(), 'html.parser')
        header = soup.find('span', {'id': re.compile('Results_by_*')}).parent
        table = header.find_next_sibling('table')
        rows = table.find_all('tr')
        points_tally = [0]
        for row in rows:
            elements = row.contents
            elements = list(filter(lambda a: a != '\n', elements))
            for element in elements:
                points = None
                if isinstance(element.string, str):
                    element.string = element.string.rstrip()
                if element.string == 'W':
                    points = 3
                elif element.string == 'D':
                    points = 1
                elif element.string == 'L':
                    points = 0

                if points is not None:
                    points_tally.append(points + points_tally[-1])

        ax.plot(points_tally, label=team_name, marker='.', markersize=8,
                linewidth=1)
        print(points_tally)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels)
    ax.set_xlabel('Matchday')
    ax.set_ylabel('Points')
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels)
    ax.set_title('{} Season'.format(year))
    plt.show()


def premier_league_dot_com_sprites():
    # base_url = 'https://www.premierleague.com'
    # with urllib.request.urlopen(base_url + '/tables?co=1&se=210&ha=-1') as response:
    #     html = response.read()
    #
    # soup = BeautifulSoup(html.decode(), 'html.parser')
    #
    # teams = []
    # active_tab = soup.find('div', {'class': 'mainTableTab'})
    # print(active_tab['data-compseason'])
    # table = active_tab.find('table')
    # body = table.find('tbody')
    # rows = soup.find_all('tr', {'data-compseason': 210})
    # print(len(rows))
    # for row in rows:
    #     team = row.find('td', {'class': 'team'})
    #     badge = team.find('span', {'class': re.compile('badge-25*')})

    import cssutils
    base_url = 'https://www.premierleague.com/resources/ver/'

    css_parser = cssutils.CSSParser()
    sheet = css_parser.parseUrl(base_url + 'styles/badge-abbreviations.css')
    position_dict = {}
    position_file_name = ''
    for rule in sheet.cssRules:
        if isinstance(rule, cssutils.css.CSSStyleRule):
            image = rule.style.getProperty('background-image')
            if image is not None:
                print(rule)
                if position_file_name != '':
                    with open(position_file_name + '.json', 'w') as fp:
                        json.dump(position_dict, fp, indent=2)
                    position_dict = {}
                position_file_name = rule.selectorText
                print(position_file_name)
                rel_url = image.value[7:-1]
                print(base_url + rel_url)
                file_name = 'images/' + rel_url.split('/')[-1]
                urllib.request.urlretrieve(base_url + rel_url, file_name)

            pos = rule.style.getProperty('background-position')
            if pos is not None:
                xy = [elem[:-2] if elem.endswith('px') else elem for elem in pos.value.split(' ')]
                position_dict[rule.selectorText] = xy

    with open(position_file_name + '.json', 'w') as fp:
        json.dump(position_dict, fp, indent=2)



    # table = soup.find('')
    # for team in soup.find_all('td', {'class': 'team'}):
    #     long_name = team.find('span', {'class': 'long'}).contents[0]
    #     short_name = team.find('span', {'class': 'short'}).contents[0]
    #     teams.append((long_name, short_name))


if __name__ == "__main__":
    # get_table()
    caan_table_pyqt5(year=2018, image_size=25)
    # team_seasons(end_year=2018, start_year=2014, team_name='Manchester City')
    # compare_teams(team_names=['Tottenham Hotspur', 'Arsenal', 'Chelsea', 'Manchester City', 'Liverpool'], year=2017)
    # premier_league_dot_com_sprites()

    # get_team_names()
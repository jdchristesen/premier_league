import urllib.request
from bs4 import BeautifulSoup
import os
import json
import matplotlib.pyplot as plt
from matplotlib.offsetbox import (TextArea, DrawingArea, OffsetImage,
                                  AnnotationBbox)
from PyQt5 import QtWidgets, QtGui, QtCore, QtWebEngineWidgets
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


def get_all_tables(**kwargs):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.action_chains import ActionChains
    import time
    start_time = time.time()

    # --| Setup
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--log-level=3')
    browser = webdriver.Chrome(chrome_options=chrome_options,
                               executable_path=r'/home/jchrist/PycharmProjects/premier_league/chromedriver')

    table = {}
    base_url = 'https://www.premierleague.com/tables'
    browser.get(base_url)
    time.sleep(1)
    start_year = 2018
    end_year = 2019

    seasons = ['210', '79', '54', '42', '27']
    for x in range(22, 0, -1):
        seasons.append(str(x))
    for season in seasons:
        season_key = '{}-{}'.format(start_year, end_year)
        print(season_key)
        print(season)
        table[season_key] = []
        start_year -= 1
        end_year -= 1
        element = browser.find_element_by_xpath('//ul[@data-dropdown-list="compSeasons"]/li[@data-option-id="{}"]'.format(season))
        browser.execute_script("arguments[0].click();", element)

        time.sleep(3)

        table_html = browser.find_element_by_tag_name('table')
        rows = table_html.find_elements_by_tag_name('tr')
        while len(rows) < 20:
            table_html = browser.find_element_by_tag_name('table')
            rows = table_html.find_elements_by_tag_name('tr')

        for row in rows:
            if row.get_attribute('data-compseason') != season:
                continue
            team_data = row.text.split('\n')[1].split()
            badge = row.find_element_by_xpath('.//span[starts-with(@class, "badge")]').get_attribute('class').split()[1]
            print(badge)
            # for b in badge:[
            #     if 'badge' in b.get_attribute('class'):
            #         badge = b.get_attribute('class').split()[1]
            #         break
            team = {'badge': badge,
                    'place': int(row.text.split('\n')[0]),
                    'team': ' '.join(team_data[:-8]),
                    'played': int(team_data[-8]),
                    'won': int(team_data[-7]),
                    'drawn': int(team_data[-6]),
                    'lost': int(team_data[-5]),
                    'gf': int(team_data[-4]),
                    'ga': int(team_data[-3]),
                    'gd': int(team_data[-2]),
                    'points': int(team_data[-1])
                    }
            table[season_key].append(team)
        with open('premier_league_tables.json'.format(season_key),'w') as fp:
            json.dump(table, fp, indent=2, sort_keys=True)
    #
    #     fixture_list = []
    #
    # print('Total Time: ', time.time() - start_time)
    #
    # with open('premier_league_table_{}.json'.format(str_year), 'w') as fp:
    #     json.dump(teams, fp, indent=2)
    #
    # with open('premier_league_teams_links.json', 'w') as fp:
    #     team_data = {}
    #     for team in teams:
    #         team_data[team['Team']] = team['link']
    #     json.dump(team_data, fp, indent=2)


# def caan_table(**kwargs):
#     # plt.rcParams["figure.dpi"] = 140
#     zoom_factor = kwargs.get('zoom_factor', 0.25)
#     image_size = kwargs.get('image-size', 50)
#     year = kwargs.get('year', 2018)
#     str_year = '{}-{}'.format(year, int(str(year)[-2:]) + 1)
#
#     if not os.path.isfile('premier_league_table_{}.json'.format(str_year)):
#         get_table(year=year)
#
#     with open('premier_league_table_{}.json'.format(str_year)) as fp:
#         teams = json.load(fp)
#
#     with open('premier_league_teams.json'.format(str_year)) as fp:
#         teams_abbr = json.load(fp)
#
#     fig, ax = plt.subplots()
#     arr_img = plt.imread('images/badges-{}-sprite.png'.format(image_size),
#                          format='png')
#     with open('.badge-{}.json'.format(image_size)) as fp:
#         pos = json.load(fp)
#
#     point_totals = {}
#     for team in teams:
#
#         team_name = team.get('Team', None)
#         print(team_name)
#         points = team.get('Pts', None)
#         if team_name is None or points is None:
#             continue
#
#         if points in point_totals:
#             point_totals[points] += 1
#         else:
#             point_totals[points] = 1
#
#         # Annotate the 2nd position with another image (a Grace Hopper portrait)
#         team_pos = pos['.badge-{}.{}'.format(image_size, teams_abbr[team_name])]
#         y = 0 - int(team_pos[0])
#         x = 0 - int(team_pos[1])
#         print(x, y)
#         print(int(team_pos[0]), int(team_pos[1]))
#         mask = np.zeros(arr_img.shape)
#         mask[x:x + image_size, y:y + image_size] = 1
#         m = mask > 0
#
#         width = 500  # pixels
#         height = 150
#         margin = 50  # pixels
#         dpi = 100.  # dots per inch
#
#         figsize = (
#         (width + 2 * margin) / dpi, (height + 2 * margin) / dpi)  # inches
#         left = margin / dpi / figsize[0]  # axes ratio
#         bottom = margin / dpi / figsize[1]
#         image = arr_img[m].reshape((y + image_size - y, x + image_size - x, 4))
#         plt.imshow(image, interpolation='nearest')
#         break
#         imagebox = OffsetImage(image)
#         imagebox.image.axes = ax
#
#         ab = AnnotationBbox(imagebox, (point_totals[points], int(points)),
#                             # xybox=(120., -80.),
#                             xycoords='data',
#                             # boxcoords='offset points',
#                             frameon=False
#                             # pad=0.5
#                             # arrowprops=dict(
#                             #     arrowstyle="->",
#                             #     connectionstyle="angle,angleA=0,angleB=90,rad=3")
#                             )
#
#         ax.add_artist(ab)
#         # ax.add_artist(imagebox)
#
#     # Fix the display limits to see everything
#     # xlim = -1
#     # ylim = -1
#     # for key, value in point_totals.items():
#     #     xlim = max(xlim, value)
#     #     ylim = max(ylim, int(key))
#     # ax.set_xlim(0, xlim)
#     # ax.set_ylim(0, ylim)
#     # ax.spines['top'].set_visible(False)
#     # ax.spines['right'].set_visible(False)
#     # ax.spines['bottom'].set_visible(False)
#     # ax.spines['left'].set_visible(False)
#     plt.show()


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
                # if position_file_name != '':
                #     with open(position_file_name + '.json', 'w') as fp:
                #         json.dump(position_dict, fp, indent=2)
                #     position_dict = {}
                position_file_name = rule.selectorText
                print(position_file_name)
                rel_url = image.value[7:-1]
                print(base_url + rel_url)
                file_name = 'images/' + rel_url.split('/')[-1]
                urllib.request.urlretrieve(base_url + rel_url, file_name)

            pos = rule.style.getProperty('background-position')
            if pos is not None:
                xy = [elem[:-2] if elem.endswith('px') else elem for elem in pos.value.split(' ')]
                for selectorRule in rule.selectorList:
                    if selectorRule.selectorText == '.badge-25.t21':
                        print('WTF')
                    position_dict[selectorRule.selectorText] = xy

    with open('badge_pos.json', 'w') as fp:
        json.dump(position_dict, fp, indent=2)


def get_all_fixtures(**kwargs):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    import time
    start_time = time.time()

    # --| Setup
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--log-level=3')
    browser = webdriver.Chrome(chrome_options=chrome_options,
                               executable_path=r'/home/jchrist/PycharmProjects/premier_league/chromedriver')

    fixture_list = []
    base_url = 'https://www.premierleague.com/'
    start_year = 2018
    end_year = 2019
    current_season_key = '{}-{}'.format(start_year, end_year)

    browser.get(base_url + 'fixtures')
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    fixtures = browser.find_element_by_class_name('fixtures')
    fix = fixtures.find_elements_by_class_name('matchFixtureContainer')
    num_fix = 1000
    while len(fix) != num_fix:
        num_fix = len(fix)
        time.sleep(2)
        fixtures = browser.find_element_by_class_name('fixtures')
        fix = fixtures.find_elements_by_class_name('matchFixtureContainer')

    print(len(fix))
    for f in fix:
        result = {}
        parent = f.find_element_by_xpath('..')
        grand_parent = parent.find_element_by_xpath('..')
        date = grand_parent.get_attribute('data-competition-matches-list')
        result['date'] = date
        split = f.text.split('\n')
        home_team = {'team': split[0]}
        away_team = {'team': split[2]}

        badges = f.find_elements_by_tag_name('span')
        home = True
        for badge in badges:
            if 'badge' in badge.get_attribute('class'):
                if home:
                    home_team['badge'] = badge.get_attribute('class')
                    home = False
                else:
                    away_team['badge'] = badge.get_attribute('class')

        result['home_team'] = home_team
        result['away_team'] = away_team
        fixture_list.append(result)
        with open('premier_league_results_{}.json'.format(current_season_key), 'w') as fp:
            json.dump(fixture_list, fp, indent=2, sort_keys=True)

    with open('premier_league_results_{}.json'.format(current_season_key), 'w') as fp:
        json.dump(fixture_list, fp, indent=2, sort_keys=True)

    seasons = ['210', '79', '54', '42', '27']
    for x in range(22, 0, -1):
        seasons.append(str(x))
    for season in seasons:
        current_num_of_fixtures = len(fixture_list)
        season_key = '{}-{}'.format(start_year, end_year)
        print(season_key)
        start_year -= 1
        end_year -= 1
        browser.get(base_url + 'results?co=1&se={}'.format(season))
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        fixtures = browser.find_element_by_class_name('fixtures')
        fix = fixtures.find_elements_by_class_name('matchFixtureContainer')
        while len(fix) < 380 - current_num_of_fixtures:
            time.sleep(0.5)
            fixtures = browser.find_element_by_class_name('fixtures')
            fix = fixtures.find_elements_by_class_name('matchFixtureContainer')

        print(len(fix))
        for f in fix:
            result = {}
            parent = f.find_element_by_xpath('..')
            grand_parent = parent.find_element_by_xpath('..')
            date = grand_parent.get_attribute('data-competition-matches-list')
            result['date'] = date
            split = f.text.split('\n')
            result['score'] = split[1]
            home_score = int(split[1].split('-')[0])
            away_score = int(split[1].split('-')[1])
            home_team = {'team': split[0],
                         'goals': home_score}
            away_team = {'team': split[2],
                         'goals': away_score}
            if home_score == away_score:
                home_team['result'] = 'D'
                away_team['result'] = 'D'
                result['result'] = 'D'
            elif home_score > away_score:
                home_team['result'] = 'W'
                away_team['result'] = 'L'
            else:
                home_team['result'] = 'L'
                away_team['result'] = 'W'

            badges = f.find_elements_by_tag_name('span')
            home = True
            for badge in badges:
                if 'badge' in badge.get_attribute('class'):
                    if home:
                        home_team['badge'] = badge.get_attribute('class')
                        home = False
                    else:
                        away_team['badge'] = badge.get_attribute('class')

            result['home_team'] = home_team
            result['away_team'] = away_team
            fixture_list.append(result)
        with open('premier_league_results_{}.json'.format(season_key), 'w') as fp:
            json.dump(fixture_list, fp, indent=2, sort_keys=True)

        fixture_list = []

    print('Total Time: ', time.time() - start_time)


if __name__ == "__main__":
    # get_table()
    # caan_table_pyqt5(year=2018, image_size=25)
    # team_seasons(end_year=2018, start_year=2014, team_name='Manchester City')
    # compare_teams(team_names=['Tottenham Hotspur', 'Arsenal', 'Chelsea', 'Manchester City', 'Liverpool'], year=2017)
    # premier_league_dot_com_sprites()

    # get_team_names()
    # get_all_fixtures()
    get_all_tables()
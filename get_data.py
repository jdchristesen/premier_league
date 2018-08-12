import urllib.request
from bs4 import BeautifulSoup
import os
import json


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
    print(teams)
    print(len(teams))

    with open('premier_league_teams.json', 'w') as f:
        json.dump(teams[:20], f, indent=2)

    with open('all_teams.json', 'w') as f:
        json.dump(teams, f, indent=2)
    print(teams[:20])

def test():
    base_url = 'https://www.premierleague.com'
    with urllib.request.urlopen('https://en.wikipedia.org/wiki/2018-19_Premier_League') as response:
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
                if element.find('a'):
                    print(element.a.string)
                    team_dict[team_dict_str[i]] = element.a.string
            else:
                team_dict[team_dict_str[i]] = element.string.rstrip()
        teams.append(team_dict)

    print(teams)


if __name__ == "__main__":
    test()
    # get_team_names()
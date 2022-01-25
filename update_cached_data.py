import requests
import zipfile
import re
import os


def download_game_params():
    """Downloads the game parameters from the server"""
    url = 'https://github.com/EdibleBug/WoWSFT-Kotlin/blob/master/WoWSFT-Data/src/main/resources/json/live/GameParams.zip?raw=true'
    r = requests.get(url)
    with open('cache/params.zip', 'wb') as f:
        f.write(r.content)


def unzip_game_params():
    """Unzips the game parameters"""
    with zipfile.ZipFile('cache/params.zip', 'r') as zip_ref:
        zip_ref.extractall('cache/')


def get_ship_battles_raw():
    """Downloads the ship battles from the server"""
    url = 'https://wows-numbers.com/ships/'
    r = requests.get(url).text
    # parse html with regex
    regex_str = 'dataProvider.ships = (.*);'
    regex = re.compile(regex_str)
    ship_battles_raw = regex.findall(r)[0]

    with open('cache/ship_battles_raw.json', 'w') as f:
        f.write(ship_battles_raw)


if __name__ == '__main__':
    if not os.path.exists('cache'):
        os.mkdir('cache')
    download_game_params()
    unzip_game_params()
    get_ship_battles_raw()

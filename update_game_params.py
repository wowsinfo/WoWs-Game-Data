import requests
import zipfile


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


if __name__ == '__main__':
    download_game_params()
    unzip_game_params()

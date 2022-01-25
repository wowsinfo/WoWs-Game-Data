import os
from update_cached_data import download_game_params, unzip_game_params, get_ship_battles_raw
from extract_game_params import writeAll, writeExtra, merge_all

if __name__ == '__main__':
    print('Updating cached data...')
    if not os.path.exists('cache'):
        os.mkdir('cache')
    download_game_params()
    unzip_game_params()
    get_ship_battles_raw()
    print('Done.')

    print('Extracting game parameters...')
    writeAll()
    writeExtra()
    merge_all()
    os.system('npx prettier --write .')
    print('Done.')

# %%
"""
import required modules and helper methods
"""
import json


def read_json(filename: str) -> dict:
    with open(filename, 'r', encoding='utf8') as f:
        json_dict = json.load(f)
    return json_dict


def read_gameparams() -> dict:
    return read_json('GameParams-0.json')


def write_json(data: dict, filename: str):
    with open(filename, 'w') as f:
        json_str = json.dumps(data, ensure_ascii=False)
        f.write(json_str)


def tree(data: any, depth: int = 2, tab: int = 0, show_value: bool = False):
    """
    Show the structure tree of a dict. This is useful when analysing the data.
    """
    if depth == 0:
        if show_value:
            if isinstance(data, dict):
                print('{}- dict'.format('\t' * tab))
            else:
                print('{}- {}'.format('\t' * tab, data))
        return
    if not isinstance(data, dict):
        # print empty string when it is empty
        if data == '':
            print('\t' * tab, '- empty string')
        else:
            print('{}- {}'.format('\t' * tab, data))
        return

    for level in data:
        print('\t' * tab + '- ' + level)
        tree(data[level], depth - 1, tab + 1, show_value=show_value)


def IDS(key: str) -> str:
    return 'IDS_' + key


# %%
# experiment here
params = read_gameparams()
params_keys = list(params.keys())
lang = read_json('en_lang.json')

# %%
"""
Put unpack methods here
"""


def unpack_ship_params(item: dict, params: dict, lang: dict) -> dict:
    # get the structure overall
    # tree(item, depth=2, show_value=True)
    ship_params = {}
    ship_index = item['index']
    ship_id = item['id']
    lang_key = IDS(ship_index)
    ship_params['name'] = lang_key
    ship_params['description'] = lang_key + '_DESCR'
    ship_params['year'] = lang_key + '_YEAR'
    ship_params['paperShip'] = item['isPaperShip']
    ship_params['id'] = ship_id
    ship_params['index'] = ship_index
    ship_params['tier'] = item['level']
    ship_params['region'] = IDS(item['typeinfo']['nation'].upper())
    ship_params['type'] = IDS(item['typeinfo']['species'].upper())
    ship_params['permoflages'] = item['permoflages']
    # TODO: debug only, to be removed
    ship_params['codeName'] = item['name']

    # get ShipUpgradeInfo to know all modules of the ship
    ship_upgrade_info = item['ShipUpgradeInfo']
    ship_params['costXP'] = ship_upgrade_info['costXP']
    ship_params['costGold'] = ship_upgrade_info['costGold']
    ship_params['costCR'] = ship_upgrade_info['costCR']
    for module in ship_upgrade_info:
        current_module = ship_upgrade_info[module]
        # find the _Hull module
        if current_module['ucType'] == '_Hull':
            ship_hull = current_module
            break

    # get everything from the hull
    for component in ship_hull['components']:
        current_component = ship_hull['components'][component]
        if len(current_component) == 0:
            continue

        for module_key in current_component:
            module = item[module_key]
            if 'Hull' in module_key:
                ship_params['health'] = module['health']
                ship_params['speed'] = module['maxSpeed']
                # tree(module, depth=2, show_value=True)

    return {ship_id: ship_params}


# %%
ships = {}
for key in params_keys:
    item = params[key]
    # ships
    if item['typeinfo']['type'] == 'Ship':
        ships.update(unpack_ship_params(item, params, lang))
        if item['typeinfo']['nation'] != 'Events':
            # battleship with torpedoes
            # if 'PGSB210' in key:
            #     print(unpack_ship_params(item, params, lang))
            pass

# save all ships
print("There are {} ships in the game".format(len(ships)))
write_json(ships, 'ships.json')
# %%

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


def roundUp(num: float, digits: int = 1) -> float:
    # TODO: in the future, we may need to keep more digits in case our calculation in app is not accurate
    return round(num, digits)


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


def unpack_air_defense(aura_key: str, air_defense: dict, module: dict):
    """
    Write air defense info to air_defense dict
    """
    aura = module[aura_key]
    if not 'Aura' in aura_key:
        return

    min_distance = aura['minDistance'] / 1000
    max_distance = aura['maxDistance'] / 1000
    gun_range = '{} - {}'.format(min_distance, max_distance)
    if 'Bubbles' in aura_key:
        bubbles = {}
        # handle black cloud (bubbles), this deals massive damage
        inner_bubble_count = int(aura['innerBubbleCount'])
        outer_bubble_count = int(aura['outerBubbleCount'])
        bubble_count = '{} + {}'.format(
            inner_bubble_count, outer_bubble_count)
        bubbles['count'] = bubble_count
        bubbles['rof'] = aura['shotDelay']
        bubbles['range'] = gun_range
        bubbles['spawnTime'] = aura['shotTravelTime']
        # value 7 is from WoWsFT, seems to be a fixed value
        bubbles['damage'] = aura['bubbleDamage'] * 7
        air_defense['bubbles'] = bubbles

    rate_of_fire = aura['areaDamagePeriod']
    damage = aura['areaDamage']
    dps = roundUp(damage / rate_of_fire)

    air_defense_info = {}
    air_defense_info['range'] = gun_range
    air_defense_info['hitChance'] = aura['hitChance']
    air_defense_info['damage'] = damage
    air_defense_info['rof'] = roundUp(rate_of_fire, digits=2)
    air_defense_info['dps'] = dps

    if aura_key == 'AuraFar':
        air_defense['far'] = air_defense_info
    if aura_key == 'AuraMedium':
        air_defense['medium'] = air_defense_info
    if aura_key == 'AuraNear':
        air_defense['near'] = air_defense_info


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
    if (len(item['permoflages']) > 0):
        ship_params['permoflages'] = item['permoflages']
    ship_params['group'] = item['group']
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

    # consumables
    consumables = []
    ship_abilities = item['ShipAbilities']
    for ability_key in ship_abilities:
        ability_slot = ship_abilities[ability_key]
        abilities = ability_slot['abils']
        if len(abilities) == 0:
            continue
        ability_list = []
        for a in abilities:
            ability_list.append({'name': a[0], 'type': a[1]})
        consumables.append(ability_list)
    ship_params['consumables'] = consumables

    # air defense can be the main battery, secondaries and dedicated air defense guns
    air_defense = {}

    # get everything from the hull
    for component in ship_hull['components']:
        current_component = ship_hull['components'][component]
        if len(current_component) == 0:
            continue

        for module_key in current_component:
            module = item[module_key]
            # TODO: TODO: the key value is not fixed, need to get from ShipUpgradeInfo manually
            # TODO: break down into separate methods later
            if 'Hull' in module_key:
                ship_params['health'] = module['health']
                # floodNode contains flood related info
                flood_nodes = module['floodNodes']
                flood_probablity = flood_nodes[0][0]
                torpedo_protecion = 100 - flood_probablity * 3 * 100
                # not all ships have a torpedo protection
                if torpedo_protecion >= 1:
                    ship_params['protection'] = roundUp(torpedo_protecion)

                concealment = {}
                visibility = module['visibilityFactor']
                visibility_plane = module['visibilityFactorByPlane']
                fire_coeff = module['visibilityCoefFire']
                fire_coeff_plane = module['visibilityCoefFireByPlane']
                # only need max value here, min is always 0
                # TODO: this value is always the same as visibilityPlane, can be removed
                visibility_submarine = module['visibilityFactorsBySubmarine']['PERISCOPE']
                concealment['sea'] = roundUp(visibility)
                concealment['plane'] = roundUp(visibility_plane)
                concealment['seaInSmoke'] = roundUp(
                    module['visibilityCoefGKInSmoke']
                )
                concealment['planeInSmoke'] = roundUp(
                    module['visibilityCoefGKByPlane']
                )
                concealment['submarine'] = roundUp(
                    visibility_submarine
                )
                concealment['seaFireCoeff'] = fire_coeff
                concealment['planeFireCoeff'] = fire_coeff_plane
                ship_params['visibility'] = concealment

                mobility = {}
                mobility['speed'] = module['maxSpeed']
                mobility['turningRadius'] = module['turningRadius']
                # got the value from WoWsFT
                mobility['rudderTime'] = roundUp(
                    module['rudderTime'] / 1.305
                )
                ship_params['mobility'] = mobility

            if 'Artillery' in module_key:
                artillery = {}
                ship_params['artillery'] = artillery

                # check air defense
                for aura_key in module:
                    unpack_air_defense(aura_key, air_defense, module)

            if 'ATBA' in module_key:
                secondaries = {}
                if len(secondaries) > 0:
                    ship_params['secondaries'] = secondaries

                # check air defense
                for aura_key in module:
                    unpack_air_defense(aura_key, air_defense, module)

            if 'AirDefense' in module_key:
                for aura_key in module:
                    unpack_air_defense(aura_key, air_defense, module)

            if 'AirSupport' in module_key:
                air_support = {}
                air_support['name'] = IDS(module['planeName'])
                air_support['reload'] = module['reloadTime']
                air_support['range'] = roundUp(module['maxDist'] / 1000)
                ship_params['airSupport'] = air_support

            if 'DepthChargeGuns' in module_key:
                depth_charge = {}
                depth_charge['reload'] = module['reloadTime']
                total_bombs = 0
                for launcher_key in module:
                    launcher = module[launcher_key]
                    if not isinstance(launcher, dict):
                        continue

                    # TODO: just use the first launcher for now, this may change in the future
                    if total_bombs == 0:
                        ammo_key = launcher['ammoList'][0]
                        ammo = params[ammo_key]
                        depth_charge['damage'] = ammo['alphaDamage']

                    # accumulate the total number of bombs
                    total_bombs += launcher['numBombs']
                total_bombs *= module['numShots']
                depth_charge['bombs'] = total_bombs
                depth_charge['groups'] = module['maxPacks']
                ship_params['depthCharge'] = depth_charge

    if len(air_defense) > 0:
        ship_params['airDefense'] = air_defense
    return {ship_id: ship_params}


# %%
ships = {}
for key in params_keys:
    item = params[key]
    # ships
    if item['typeinfo']['type'] == 'Ship':
        # battleship with torpedoes
        # if 'PGSB210' in key:
        #     print(unpack_ship_params(item, params, lang))
        #     break
        ships.update(unpack_ship_params(item, params, lang))


# %%

# %%
# save all ships
print("There are {} ships in the game".format(len(ships)))
write_json(ships, 'ships.json')

# %%
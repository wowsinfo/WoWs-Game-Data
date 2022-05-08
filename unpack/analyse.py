# %%
"""
import required modules and helper methods
"""
import json
import os


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


def list_dir(dir: str) -> list:
    """
    List all files in a directory
    """
    return os.listdir(dir)


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
    # TODO: should return a dict instead here, don't modify the original dict from this function
    """
    Write air defense info to air_defense dict
    """
    aura = module[aura_key]
    if not 'Aura' in aura_key:
        return

    min_distance = aura['minDistance'] / 1000
    max_distance = aura['maxDistance'] / 1000

    if 'Bubbles' in aura_key:
        bubbles = {}
        # handle black cloud (bubbles), this deals massive damage
        bubbles['inner'] = int(aura['innerBubbleCount'])
        bubbles['outer'] = int(aura['outerBubbleCount'])
        bubbles['rof'] = aura['shotDelay']
        bubbles['minRange'] = min_distance
        bubbles['maxRange'] = max_distance
        bubbles['spawnTime'] = aura['shotTravelTime']
        # value 7 is from WoWsFT, seems to be a fixed value
        bubbles['damage'] = aura['bubbleDamage'] * 7
        air_defense['bubbles'] = bubbles

    rate_of_fire = aura['areaDamagePeriod']
    damage = aura['areaDamage']
    dps = roundUp(damage / rate_of_fire)

    air_defense_info = {}
    air_defense_info['minRange'] = min_distance
    air_defense_info['maxRange'] = max_distance
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


def unpack_ship_components(module_name: str, module_type: str, ship: dict, air_defense: dict) -> dict:
    # TODO: how to air defense here??
    """
    Unpack the ship components
    """
    ship_components = {}

    module = ship[module_name]
    # TODO: break down into separate methods later
    if 'hull' in module_type:
        ship_components['health'] = module['health']
        # floodNode contains flood related info
        flood_nodes = module['floodNodes']
        flood_probablity = flood_nodes[0][0]
        torpedo_protecion = 100 - flood_probablity * 3 * 100
        # not all ships have a torpedo protection
        if torpedo_protecion >= 1:
            ship_components['protection'] = roundUp(
                torpedo_protecion)

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
        ship_components['visibility'] = concealment

        mobility = {}
        mobility['speed'] = module['maxSpeed']
        mobility['turningRadius'] = module['turningRadius']
        # got the value from WoWsFT
        mobility['rudderTime'] = roundUp(
            module['rudderTime'] / 1.305
        )
        ship_components['mobility'] = mobility
    elif 'artillery' in module_type:
        artillery = {}
        artillery['range'] = module['maxDist']
        artillery['sigma'] = module['sigmaCount']

        guns = []
        for gun_key in module:
            if not 'HP' in gun_key:
                continue

            # check each gun
            gun_module = module[gun_key]
            if not isinstance(gun_module, dict):
                raise Exception('gun_module is not a dict')

            # can share with torpedoes
            current_gun = {}
            current_gun['reload'] = gun_module['shotDelay']
            current_gun['rotation'] = gun_module['rotationSpeed'][0]
            # TODO: count should be int, share with torpedoes
            current_gun['count'] = gun_module['numBarrels']
            current_gun['ammo'] = gun_module['ammoList']
            guns.append(current_gun)
        artillery['guns'] = guns
        ship_components.update(artillery)

        # check air defense
        for aura_key in module:
            unpack_air_defense(aura_key, air_defense, module)
    elif 'atba' in module_type:
        secondaries = {}
        secondaries['range'] = module['maxDist']
        secondaries['sigma'] = module['sigmaCount']

        guns = []
        for gun_key in module:
            if not 'HP' in gun_key:
                continue

            # check each gun
            gun_module = module[gun_key]
            if not isinstance(gun_module, dict):
                raise Exception('gun_module is not a dict')

            # can share with torpedoes
            current_gun = {}
            current_gun['reload'] = gun_module['shotDelay']
            current_gun['rotation'] = gun_module['rotationSpeed'][0]
            # TODO: count should be int, share with torpedoes
            current_gun['count'] = gun_module['numBarrels']
            current_gun['ammo'] = gun_module['ammoList']
            guns.append(current_gun)
        secondaries['guns'] = guns
        ship_components.update(secondaries)

        # check air defense
        for aura_key in module:
            unpack_air_defense(aura_key, air_defense, module)
    elif 'airDefense' in module_type:
        # TODO: air defense can change, need to consider this
        for aura_key in module:
            unpack_air_defense(aura_key, air_defense, module)
    elif 'airSupport' in module_type:
        air_support = {}
        air_support['name'] = IDS(module['planeName'])
        air_support['reload'] = module['reloadTime']
        air_support['bombs'] = module['chargesNum']
        air_support['range'] = roundUp(
            module['maxDist'] / 1000)
        ship_components['airSupport'] = air_support
    elif 'depthCharges' in module_type:
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
                depth_charge['ammo'] = ammo_key

            # accumulate the total number of bombs
            total_bombs += launcher['numBombs']
        total_bombs *= module['numShots']
        depth_charge['bombs'] = total_bombs
        depth_charge['groups'] = module['maxPacks']
        ship_components['depthCharge'] = depth_charge
    elif 'airArmament' in module_type:
        pass
    elif 'radars' in module_type:
        # TODO: this might be the radar on the ship, not the radar consumable
        pass
    elif 'torpedoes' in module_type:
        torpedo = {}
        torpedo['singleShot'] = module['useOneShot']

        # need to make sure if all launchers are the same
        launchers = []
        for torpedo_key in module:
            if not 'HP' in torpedo_key:
                continue

            # check each torpedo launcher
            torpedo_launcher = module[torpedo_key]
            if not isinstance(torpedo_launcher, dict):
                raise Exception('torpedo_launcher is not a dict')

            current_launcher = {}
            current_launcher['reload'] = torpedo_launcher['shotDelay']
            current_launcher['rotation'] = torpedo_launcher['rotationSpeed'][0]
            current_launcher['count'] = torpedo_launcher['numBarrels']
            current_launcher['ammo'] = torpedo_launcher['ammoList']
            launchers.append(current_launcher)
        torpedo['launchers'] = launchers
        ship_components.update(torpedo)
    elif 'pinger' in module_type:
        # this seems to be the submarine pinger
        pinger = {}
        pinger['reload'] = module['waveReloadTime']
        pinger['range'] = module['waveDistance']
        sectors = module['sectorParams']
        if len(sectors) != 2:
            raise ValueError('pinger has more than 2 sectors')

        pinger['lifeTime1'] = sectors[0]['lifetime']
        pinger['lifeTime2'] = sectors[1]['lifetime']
        # TODO: taking the first value for now, this is metre per second
        pinger['speed'] = module['waveParams'][0]['waveSpeed'][0]
        ship_components.update(pinger)
    elif 'engine' in module_type:
        # TODO: not sure what this does
        pass
    elif 'specials' in module_type:
        # TODO: add this if needed
        pass
    elif 'abilities' in module_type:
        # TODO: not sure what this does
        pass
    elif 'directors' in module_type:
        # TODO: not sure what this does
        pass
    elif 'finders' in module_type:
        # TODO: not sure what this does
        pass
    elif 'wcs' in module_type:
        # TODO: not sure what this does
        pass
    else:
        raise Exception('Unknown module type: {}'.format(module_type))

    return {module_name: ship_components}


def unpack_ship_params(item: dict, params: dict) -> dict:
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

    # ShipUpgradeInfo is the key, simply relying on module_key is not reliable
    ship_upgrade_info = item['ShipUpgradeInfo']
    ship_params['costXP'] = ship_upgrade_info['costXP']
    ship_params['costGold'] = ship_upgrade_info['costGold']
    ship_params['costCR'] = ship_upgrade_info['costCR']

    # module and component are separated so we can take whichever we need from the app
    module_tree = {}
    component_tree = {}
    for module_key in ship_upgrade_info:
        current_module = ship_upgrade_info[module_key]
        if not isinstance(current_module, dict):
            continue

        if not module_key in params:
            raise Exception('{} is not in params'.format(module_key))

        # get the credit + xp needed for this module
        cost = {}
        module_cost = params[module_key]
        cost['costCR'] = module_cost['costCR']
        cost['costXP'] = module_cost['costXP']

        module_info = {}
        module_info['cost'] = cost

        module_type = current_module['ucType']

        # TODO: the dictionary seems to be sorted so this might not be necessary but just in case, we do this for now
        # find the index of the current module
        module_index = 0
        prev = current_module['prev']
        while prev != '':
            prev = ship_upgrade_info[prev]['prev']
            module_index += 1
        module_info['index'] = module_index

        # now, we need to read the info about it from hull
        if module_type == '_Hull':
            next_ship = current_module['nextShips']
            # there can be multiple next ships, write this to the root
            if len(next_ship) > 0:
                ship_params['nextShip'] = next_ship
            # simply save it to the module tree
            components = current_module['components']
            module_info['components'] = components

            for component_key in components:
                # ignore empty components
                component_list = components[component_key]
                if len(component_list) == 0:
                    continue

                for component_name in component_list:
                    component = unpack_ship_components(
                        component_name, component_key, item, air_defense
                    )
                    component_tree.update(component)

        # elif module_type == '_Artillery':
        #     pass
        # elif module_type == '_Engine':
        #     pass
        # elif module_type == '_Suo':
        #     pass
        # elif module_type == '_Torpedoes':
        #     pass
        # elif module_type == '_TorpedoBomber':
        #     pass
        # elif module_type == '_DiveBomber':
        #     pass
        # elif module_type == '_FlightControl':
        #     pass
        # elif module_type == '_Fighter':
        #     pass
        # elif module_type == '_SkipBomber':
        #     pass
        # elif module_type == '_Sonar':
        #     pass
        # elif module_type == '_Abilities':
        #     # this is events only I think
        #     pass
        # elif module_type == '_PrimaryWeapons':
        #     pass
        # elif module_type == '_SecondaryWeapons':
        #     pass
        # else:
        #     raise Exception('Unknown module type: {}'.format(module_type))

        # there can be multiple modules of the same type
        if module_type in module_tree:
            module_tree[module_type].update({module_key: module_info})
        else:
            module_tree[module_type] = {module_key: module_info}
    ship_params['modules'] = module_tree
    ship_params['components'] = component_tree

    if len(air_defense) > 0:
        ship_params['airDefense'] = air_defense
    return {ship_id: ship_params}


def unpack_achievements(item: dict, key: str) -> dict:
    """
    The app will handle icon, achievement name, and description
    """
    achievements = {}
    achievements['type'] = item['battleTypes']
    achievements['ui'] = item['uiName']
    achievements['id'] = item['id']
    achievements['constants'] = item['constants']
    return {key: achievements}


def unpack_exteriors(item: dict, key: str) -> dict:
    """
    Unpack flags, camouflage and permoflages
    """
    exterior = {}

    exterior['id'] = item['id']
    costCR = item['costCR']
    if (costCR >= 0):
        exterior['costCR'] = costCR
    costGold = item['costGold']
    if (costGold >= 0):
        exterior['costGold'] = costGold
    if len(item['modifiers']) > 0:
        exterior['modifiers'] = item['modifiers']
    exterior['type'] = item['typeinfo']['species']
    # exterior['name'] = item['name']
    # exterior['name'] = item['name']
    # exterior['name'] = item['name']
    # exterior['name'] = item['name']
    # exterior['name'] = item['name']
    return {key: exterior}


def unpack_modernization(item: dict, params: dict) -> dict:
    """
    Unpack ship upgrades
    """
    slot = item['slot']
    if (slot < 0):
        return

    modernization = {}
    modernization['slot'] = slot
    modernization['id'] = item['id']
    if len(item['shiplevel']) > 0:
        modernization['level'] = item['shiplevel']
    if len(item['shiptype']) > 0:
        modernization['type'] = item['shiptype']
    if len(item['nation']) > 0:
        modernization['nation'] = item['nation']
    modernization['modifiers'] = item['modifiers']

    ships = item['ships']
    ships_id = []
    for ship in ships:
        if not ship in params:
            continue
        ships_id.append(params[ship]['id'])
    if len(ships_id) > 0:
        modernization['ships'] = ships_id

    excludes = item['excludes']
    excludes_id = []
    for exclude in excludes:
        if not exclude in params:
            continue
        excludes_id.append(params[exclude]['id'])
    if len(excludes_id) > 0:
        modernization['excludes'] = excludes_id
    return {key: modernization}


def unpack_weapons(item: dict, key: str) -> dict:
    """
    Unpack all weapons (anti-air, main battery, seondaries, torpedoes and more)
    """
    # TODO: to be removed because this is included in the ship, not sure if this is needed at all.
    weapon = {}
    weapon_type = item['typeinfo']['species']
    weapon['type'] = weapon_type
    if 'ammoList' in item:
        weapon['ammo'] = item['ammoList']

    if weapon_type == 'DCharge':
        # depth charge
        pass
    elif weapon_type == 'Torpedo':
        # torpedoes
        pass
    elif weapon_type == 'AAircraft':
        # anti-aircraft
        pass
    elif weapon_type == 'Main':
        # main battery
        pass
    elif weapon_type == 'Secondary':
        # secondaries
        pass
    else:
        # unknown weapon type
        raise Exception('Unknown weapon type: {}'.format(weapon_type))
    return {key: weapon}


def unpack_shells(item: dict) -> dict:
    """
    Unpack shells, HE & AP shells, HE & AP bombs and more
    """
    projectile = {}
    ammo_type = item['ammoType']
    projectile['ammoType'] = ammo_type
    projectile['speed'] = item['bulletSpeed']

    # HE & SAP penetration value
    pen_cs = item['alphaPiercingCS']
    if pen_cs > 0:
        projectile['penSAP'] = pen_cs
    pen_he = item['alphaPiercingHE']
    if pen_he > 0:
        projectile['penHE'] = pen_he

    projectile['damage'] = item['alphaDamage']
    burn_chance = item['burnProb']
    if burn_chance > 0:
        # AP and SAP cannot cause fires
        projectile['burnChance'] = burn_chance

    # ricochet angle
    ricochet_angle = item['bulletRicochetAt']
    if ricochet_angle <= 90:
        projectile['ricochetAngle'] = ricochet_angle
        projectile['ricochetAlways'] = item['bulletAlwaysRicochetAt']

    diameter = item['bulletDiametr']
    projectile['diameter'] = diameter
    if ammo_type == 'AP':
        ap_info = {}
        ap_info['diameter'] = diameter
        # get values needed to calculate the penetration of AP
        ap_info['weight'] = item['bulletMass']
        ap_info['drag'] = item['bulletAirDrag']
        ap_info['velocity'] = item['bulletSpeed']
        ap_info['krupp'] = item['bulletKrupp']
        projectile['ap'] = ap_info
        # caliber is not changing, and overmatch should ignore decimals & no rounding because 8.9 is the same as 8
        overmatch = int(diameter * 1000 / 14.3)
        projectile['overmatch'] = overmatch
        projectile['fuseTime'] = item['bulletDetonator']
    return projectile


def unpack_projectiles(item: dict, key: str) -> dict:
    """
    Unpack all projectiles, like shells, torpedoes, and more. This is launched, fired or emitted? from a weapon.
    """
    projectile = {}
    projectile_type = item['typeinfo']['species']
    projectile['type'] = projectile_type
    projectile_nation = item['typeinfo']['nation']
    projectile['nation'] = projectile_nation

    if projectile_type == 'Torpedo':
        projectile['speed'] = item['speed']
        projectile['visibility'] = item['visibilityFactor']
        # TODO: divide by 33.3333 to become the real value here or in app?
        projectile['range'] = item['maxDist']
        projectile['floodChance'] = item['uwCritical'] * 100
        projectile['alphaDamage'] = item['alphaDamage']
        projectile['damage'] = item['damage']
        projectile['deepWater'] = item['isDeepWater']
        # deep water torpedoes cannot hit certain classes of ships
        ignore_classes = item['ignoreClasses']
        if len(ignore_classes) > 0:
            projectile['ignoreClasses'] = ignore_classes
    elif projectile_type == 'Artillery':
        projectile.update(unpack_shells(item))
    elif projectile_type == 'Bomb':
        # TODO: need to consider what we want from bomb
        projectile.update(unpack_shells(item))
    elif projectile_type == 'SkipBomb':
        # TODO: same as above
        projectile.update(unpack_shells(item))
    elif projectile_type == 'Rocket':
        # TODO: same as above
        projectile.update(unpack_shells(item))
    elif projectile_type == 'DepthCharge':
        projectile['damage'] = item['alphaDamage']
        projectile['burnChance'] = item['burnProb']
        projectile['floodChance'] = item['uwCritical'] * 100
        pass
    elif projectile_type == 'Mine':
        # TODO: we don't do this for now
        pass
    elif projectile_type == 'Laser':
        # TODO: we don't do this for now
        pass
    elif projectile_type == 'PlaneTracer':
        # TODO: we don't do this for now
        pass
    elif projectile_type == 'Wave':
        # TODO: we don't do this for now
        pass
    else:
        # unknown projectile type
        raise Exception('Unknown projectile type: {}'.format(projectile_type))
    return {key: projectile}


def unpack_game_map() -> dict:
    """
    Unpack the game map
    """
    game_map = {}
    for f in list_dir('spaces'):
        if os.path.exists('spaces/{}/minimap_water.png'.format(f)):
            # valid map
            curr_map = {}
            map_name = f.upper()
            lang_name = 'IDS_SPACES/{}'.format(map_name)
            curr_map['name'] = lang_name
            curr_map['description'] = lang_name + '_DESCR'
            game_map[map_name] = curr_map
    return game_map


def unpack_commander_skills(item: dict) -> dict:
    """
    Unpack the commander skills
    """
    skills = {}
    for key in item:
        skills[key] = item[key]
    return skills


def unpack_language(item: dict, key: str) -> list:
    """
    Get everything we need from the language file, return a list of keys
    """
    return []


# %%
# TODO: make this a function when everything is done
ships = {}
achievements = {}
exteriors = {}
modernizations = {}
skills = {}
weapons = {}
projectiles = {}
for key in params_keys:
    item = params[key]
    item_type = item['typeinfo']['type']
    item_nation = item['typeinfo']['nation']
    item_species = item['typeinfo']['species']

    if item_type == 'Ship':
        # if 'PGSS108' in key:
        #     write_json(item, 'u190.json')
        #     # print(unpack_ship_params(item, params))
        #     break
        ships.update(unpack_ship_params(item, params))
    elif item_type == 'Achievement':
        achievements.update(unpack_achievements(item, key))
    elif item_type == 'Exterior':
        exteriors.update(unpack_exteriors(item, key))
    elif item_type == 'Modernization':
        modernization = unpack_modernization(item, params)
        if modernization != None:
            modernizations.update(modernization)
    elif item_type == 'Crew':
        # save all commander skills once
        if skills == {}:
            skills = item['Skills']
    elif item_type == 'Gun':
        weapons.update(unpack_weapons(item, key))
    elif item_type == 'Projectile':
        projectiles.update(unpack_projectiles(item, key))

# %%

# %%
# save everything
print("There are {} ships in the game".format(len(ships)))
write_json(ships, 'ships.json')
print("There are {} achievements in the game".format(len(achievements)))
write_json(achievements, 'achievements.json')
print("There are {} exteriors in the game".format(len(exteriors)))
write_json(exteriors, 'exteriors.json')
print("There are {} modernizations in the game".format(len(modernizations)))
write_json(modernizations, 'modernizations.json')
print("There are {} weapons in the game".format(len(weapons)))
write_json(weapons, 'weapons.json')
print("There are {} projectiles in the game".format(len(projectiles)))
write_json(projectiles, 'projectiles.json')

game_maps = unpack_game_map()
print("There are {} game maps in the game".format(len(game_maps)))
write_json(game_maps, 'game_maps.json')

commander_skills = unpack_commander_skills(skills)
print("There are {} commander skills in the game".format(len(commander_skills)))
write_json(commander_skills, 'commander_skills.json')

# %%

# %%
if __name__ == '__main__':
    # TODO: add function call here
    pass

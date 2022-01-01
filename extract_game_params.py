# %%
import json
import os
from merge_all import merge_all
from ap_pen import *

# %%


def writeToJson(json_dict, name):
    """write json object to disk"""
    with open(name, 'w+') as l:
        l.write(json.dumps(sort(json_dict)) + '\n')


def findKey(name, keys):
    """find keys in object, can be improved to go deep"""
    temp = []
    for key in keys:
        if name.lower() in key.lower():
            temp.append(key)
    return temp


def findFirstObject(name, dic, rootMode=False):
    """find the first object from the dict"""
    if isinstance(dic, dict):
        for key in dic.keys():
            temp = dic[key]
            # check if this is the object we want
            if name == key:
                if rootMode is True:
                    return dic
                else:
                    return temp
            result = findFirstObject(name, temp, rootMode)
            if result != None:
                return result
    elif isinstance(dic, list):
        # go through the list
        for value in dic:
            result = findFirstObject(name, value, rootMode)
            if result != None:
                return result


def sort(d):
    """sort dictionary by keys"""
    if isinstance(d, dict):
        return {k: d[k] for k in sorted(d)}
    return d


def notEmpty(anything):
    return len(anything) > 0


def splitFirst(long_string: str):
    return long_string.split('_', 1)[0]


# %%
# load everything from json, at least 2GB of ram is needed for this
game = {}
# all keys inside game params
keys = {}
with open('cache/GameParams.json', 'r') as j:
    # this is now a list and index 0 is the data we need
    game = json.load(j)[0]
    keys = game.keys()
    # just to make sure something is printed and everything are read
    print(len(keys))

# it might be good just to load it from the game because you don't need to update it manually
ships = {}
# with open('tools/ship_all.json', 'r') as j:
#     ships = json.load(j)
#     print(len(ships))
for key in keys:
    curr = game[key]
    if 'typeinfo' in curr and curr['typeinfo']['type'] == 'Ship':
        ship_id = curr['id']
        ships[ship_id] = {'ship_id_str': curr['index'], 'name': curr['name']}
print(len(ships))

# save this to extra as well
writeToJson(ships, 'extra/ships.json')

# %%
# upgrade, NO LONGER NEEDED


def writeUniqueUpgrades():
    # Find unique update and their ship
    unique_upgrades = findKey('Special_Mod', keys)
    # this adds ship id to legendary upgrade
    legendary = {}
    # this add legendary upgrades to ship
    ship_upgrade = {}
    # get their id and the ship they belong to
    for upgrade in unique_upgrades:
        temp = game[upgrade]
        upgrade_id = temp['id']
        upgrade_id_str = str(upgrade_id)
        # remember to add slot later
        slot = temp['slot']

        legendary[upgrade_id_str] = []
        for ship in temp['ships']:
            ship_id = game[ship]['id']
            ship_id_str = str(ship_id)

            # init
            if not ship_id_str in ship:
                ship_upgrade[ship_id_str] = {"legendary_upgrades": []}

            # you need to the slot as well
            ship_upgrade[ship_id_str]["legendary_upgrades"].append(
                {"upgrade_id": upgrade_id_str, "slot": slot})
            legendary[upgrade_id_str].append(
                {"ship_id": ship_id, "slot": slot})

    writeToJson(legendary, 'data/legendary_upgrades.json')
    writeToJson(ship_upgrade, 'data/ship_legendary_upgrades.json')


# %%
# find all keys from data
# findKey('PASX005', keys)

# %%
# save anything to json
# writeToJson(game['PCM002_Torpedo_Mod_I'], 'PCM002_Torpedo_Mod_I.json')

# %%
# preview anything
# game['PASX005_St_Clair']

# %%
additional = {}
with open('data/ship_additional.json', 'r') as j:
    additional = json.load(j)
    print(len(additional))

# %%
# ship_id = '3760142032'
# the_ship = additional[ship_id]
# print(the_ship)
# get_ap_penetration(the_ship['ap'])

# %%


def retrieveDataFromShip(ship):
    temp = {}
    # extract permo flages
    permoflages = ship['permoflages'].copy()
    nativePermoflage = ship['nativePermoflage']
    permoflages.append(nativePermoflage)
    # we need to get all permoflage_id
    permo_ids = []
    for permo in permoflages:
        if permo != '':
            permo_ids.append(game[permo]['id'])
    # add it to temp, there is at least one
    if len(permo_ids) > 0:
        temp['permoflages'] = permo_ids

    # extract HE penetration
    artillery = findFirstObject('HitLocationArtillery', ship, rootMode=True)
    if artillery != None:
        ammoList = artillery['ammoList']
        he = [x for x in ammoList if '_HE' in x]
        # some ships doesn't have HE
        if len(he) > 0:
            # add it to temp
            temp['alphaPiercingHE'] = game[he[0]]['alphaPiercingHE']

        cs = [x for x in ammoList if '_CS' in x]
        # some ships doesn't have cs (SAP)
        if len(cs) > 0:
            # add it to temp
            temp['alphaPiercingCS'] = game[cs[0]]['alphaPiercingCS']

        # get ap info here as well
        ap = [x for x in ammoList if '_AP' in x]
        if len(ap) > 0:
            saved_info = {}
            shell = game[ap[0]]
            saved_info['weight'] = shell['bulletMass']
            saved_info['diameter'] = shell['bulletDiametr']
            saved_info['drag'] = shell['bulletAirDrag']
            saved_info['velocity'] = shell['bulletSpeed']
            saved_info['krupp'] = shell['bulletKrupp']
            temp['ap'] = saved_info

    # get sigma
    sigma = findFirstObject('ammoPool', ship, rootMode=True)
    if sigma != None:
        temp['sigma'] = sigma['sigmaCount']

    # save consumables
    ability = findFirstObject('ShipAbilities', ship)
    if ability != None:
        temp['consumables'] = []
        # append slot and abilities in
        for slot in ability:
            s = ability[slot]
            # x[0] is the name of the consumable
            abils = [x for x in s['abils'] if x[0].endswith('Premium')]
            o = []
            for a in abils:
                o.append({'name': a[0], 'type': a[1]})
            # o is used to make a list of objects
            if len(o) > 0:
                # check there is at least one inside, not all ships have 5 consumables
                temp['consumables'].append(o)

    isPaperShip = ship['isPaperShip']
    if (isPaperShip):
        temp['isPaperShip'] = isPaperShip
    return temp

# %%
# additional data


def writeShipAdditional():
    # loop through all ship
    additional_ship_info = {}
    for ship in ships:
        ship_str = ships[ship]['ship_id_str']
        # it should only has one
        additional_ship_info[ship] = retrieveDataFromShip(
            game[findKey(ship_str, keys)[0]])

    battles = {}
    with open('cache/ship_battles_raw.json', 'r') as j:
        battles = json.load(j)

    # add ship battles
    for ship in battles:
        # id is now a number
        ship_id = ship['ship_id']
        if ship['battles'] > 0:
            additional_ship_info[ship_id]['battles'] = ship['battles']
    writeToJson(additional_ship_info, 'data/ship_additional.json')

# writeShipAdditional()

# %%
# remove empty strings and any strings with .xml


def cleanupConsumables(dic):
    if isinstance(dic, dict):
        for k in dic.copy().keys():
            t = dic[k]
            if k == 'typeinfo' or k == 'group':
                del dic[k]

            if isinstance(t, str):
                if t == "" or ".xml" in t:
                    del dic[k]
            elif isinstance(t, float):
                if t == 0.0:
                    del dic[k]
            elif isinstance(t, int):
                if t == -1:
                    del dic[k]
            elif isinstance(t, list):
                if len(t) == 0:
                    del dic[k]
            else:
                cleanupConsumables(t)
    elif isinstance(dic, list):
        for e in dic:
            cleanupConsumables(e)

# %%
# save all consumables into one file and removed entries that are not needed


def writeConsumables():
    consumables = {}
    for ship in ships:
        ship_str = ships[ship]['ship_id_str']
        the_one = game[findKey(ship_str, keys)[0]]
        # find abilities
        ability = findFirstObject('ShipAbilities', the_one)
        if ability != None:
            for slot in ability:
                s = ability[slot]
                # x[0] is the name of the consumable
                abils = [x for x in s['abils'] if x[0].endswith('Premium')]
                for a in abils:
                    if not a[0] in consumables:
                        consumables[a[0]] = game[a[0]]

    cleanupConsumables(consumables)
    normal = ['canBuy', 'canBuyCustom', 'costCR',
              'freeOfCharge', 'id', 'index', 'name']
    for c in consumables:
        # move some data inside an array
        curr = consumables[c]
        temp = {}
        for k in curr.copy().keys():
            if not (k in normal):
                temp[k] = curr[k]
                del curr[k]
        curr['data'] = temp

    writeToJson(consumables, 'data/consumables.json')
    # print out all types for icons
    for c in consumables:
        t = consumables[c]
        one = t['data']
        for k in one:
            print(one[k]['consumableType'])
            break

# writeConsumables()

# %%
# long range torpedoes


def writeLongTorpedos():
    long_torpedos = []
    for k in keys:
        o = game[k]
        if 'typeinfo' in o and o['typeinfo']['species'] == 'Torpedo' and o['typeinfo']['type'] == 'Projectile':
            if o['maxDist'] > 399:
                dist = o['maxDist'] / 33.35
                speed = o['speed'] * 1.05
                spotted = o['visibilityFactor']
                reaction = spotted * 1000 / 2.6 / speed
                long_torpedos.append({'name': o['name'], 'dist': dist, 'speed': speed,
                                     'spotted': spotted, 'reaction': reaction, 'type': o['typeinfo']['nation']})
    writeToJson(long_torpedos, 'extra/long_torpedoes.json')
# writeLongTorpedos()

# %%
# big guns


def writeBigSmallGuns():
    big_guns = []
    small_guns = []
    for k in keys:
        o = game[k]
        if 'typeinfo' in o and o['typeinfo']['species'] == 'Artillery' and o['typeinfo']['type'] == 'Projectile':
            if o['bulletDiametr'] > 0.409:
                alphaDamage = o['alphaDamage']
                speed = o['bulletSpeed']
                diametre = o['bulletDiametr'] * 1000
                if (o['ammoType'] == 'AP'):
                    big_guns.append(
                        {'name': o['name'], 'damage': alphaDamage, 'speed': speed, 'diametre': diametre})
            elif o['bulletDiametr'] < 0.120:
                alphaDamage = o['alphaDamage']
                speed = o['bulletSpeed']
                diametre = o['bulletDiametr'] * 1000
                if (o['ammoType'] == 'HE'):
                    small_guns.append(
                        {'name': o['name'], 'damage': alphaDamage, 'speed': speed, 'diametre': diametre})
    writeToJson(big_guns, 'extra/big_guns.json')
    writeToJson(small_guns, 'extra/small_guns.json')

# writeBigSmallGuns()

# %%
# long range torpedoes


def writeFastSlowGuns():
    fast_guns = []
    slow_guns = []
    for k in keys:
        c = game[k]
        if 'unpeculiarShip' in c:
            delay = findFirstObject('HitLocationArtillery', c, rootMode=True)
            if delay != None:
                if delay['shotDelay'] < 4:
                    fast_guns.append({
                        'name': c['name'],
                        'tier': c['level'],
                        'reload': delay['shotDelay']
                    })
                elif delay['shotDelay'] > 30:
                    slow_guns.append({
                        'name': c['name'],
                        'tier': c['level'],
                        'reload': delay['shotDelay']
                    })
    writeToJson(fast_guns, 'extra/fast_guns.json')
    writeToJson(slow_guns, 'extra/slow_guns.json')

# writeFastSlowGuns()

# %%
# removed temporarily
# save all commanders and legendary commanders


def writeCommanders():
    commanders = []
    legendary_commanders = []
    for key in keys:
        if 'CrewPersonality' in game[key]:
            crew = game[key]['CrewPersonality']
            # get unique and collab
            if crew['isUnique'] == True or crew['peculiarity'] != 'default':
                commanders.append(key)
            if len(game[key]['UniqueSkills'].keys()) > 0:
                legendary_commanders.append(key)
    writeToJson(commanders, 'data/commanders.json')
    writeToJson(legendary_commanders, 'data/legendary_commanders.json')

# %%


def writeModernization():
    modernization = {}
    for key in keys:
        curr = game[key]
        if 'typeinfo' in curr:
            if 'type' in curr['typeinfo']:
                if curr['typeinfo']['type'] == 'Modernization':
                    # slot is the best way to determine whether this is still available
                    if (curr['slot']) > -1:
                        modernization[curr['id']] = {
                            'slot': curr['slot'],
                        }

                        # add only if they are not empty to save space
                        if notEmpty(curr['nation']):
                            modernization[curr['id']
                                          ]['nation'] = curr['nation']
                        if notEmpty(curr['shiplevel']):
                            modernization[curr['id']
                                          ]['shiplevel'] = curr['shiplevel']
                        if notEmpty(curr['ships']):
                            formatted = list(map(splitFirst, curr['ships']))
                            modernization[curr['id']]['ships'] = formatted
                        if notEmpty(curr['shiptype']):
                            modernization[curr['id']
                                          ]['shiptype'] = curr['shiptype']
                        if notEmpty(curr['excludes']):
                            formatted = list(map(splitFirst, curr['excludes']))
                            modernization[curr['id']]['excludes'] = formatted
    writeToJson(modernization, 'data/modernizations.json')

# %%
# merge with ship_alias?


def writeOldShips():
    old_ships = {}
    for key in keys:
        if 'group' in game[key]:
            # this group are all ships that are removed
            if game[key]['group'] == 'preserved':
                curr = game[key]
                formated_name = ' '.join(curr['name'].split('_')[1:])
                old_ships[game[key]['id']] = {
                    'name': formated_name, 'tier': curr['level']}
    writeToJson(old_ships, 'data/removed_ships.json')


# %%


def getSubmarines():
    subs = []
    for key in keys:
        ship = game[key]
        if 'typeinfo' in ship:
            curr = ship['typeinfo']
            if 'species' in curr and curr['species'] == 'Submarine':

                subs.append({'name': ship['name'], 'typeinfo': curr, 'tier': ship['level'],
                            'concealment': findFirstObject('visibilityFactor', ship), 'id': ship['id']})
    writeToJson(subs, 'extra/submarines.json')


# %%
# all in one


def writeAll():
    writeConsumables()
    writeShipAdditional()
    # writeCommanders()
    writeModernization()
    getSubmarines()
    # it doesn't need to update that often
    writeOldShips()


def writeExtra():
    writeLongTorpedos()
    writeBigSmallGuns()
    writeFastSlowGuns()


if __name__ == '__main__':
    writeAll()
    writeExtra()
    merge_all()
    os.system('npx prettier --write .')

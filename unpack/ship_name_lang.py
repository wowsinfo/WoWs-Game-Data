"""
Get all ship names based on ship_index.json from langs/
"""

import json


def generate_ship_names():
    """
    Generate ship names
    """
    with open('ship_index.json', 'r', encoding='utf8') as f:
        ship_index = json.load(f)

    ship_names = {}
    for lang in ['zh_sg', 'en']:
        with open('langs/{}_lang.json'.format(lang), 'r', encoding='utf8') as f:
            raw_lang = json.load(f)

        curr_lang = {}
        for ship in ship_index:
            curr_ship = ship_index[ship]
            curr_index = curr_ship['index']
            # the raw id is like IDS_PHSC109
            ids = 'IDS_' + curr_index
            curr_lang[ship] = raw_lang[ids]
        
        simple_lang = lang.split('_')[0]
        ship_names[simple_lang] = curr_lang
    return ship_names


if __name__ == '__main__':
    ship_names = generate_ship_names()
    with open('ship_names.json', 'w', encoding='utf8') as f:
        jsonStr = json.dumps(ship_names, ensure_ascii=False)
        f.write(jsonStr)
    print('Done')

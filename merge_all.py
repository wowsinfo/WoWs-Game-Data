'''
merge everything in 'data/' folder into just one file,
the goal is to download only one file from this repo
'''
import json

json_files = [
  {'path': 'data/consumables.json', 'name': 'consumables'},
  {'path': 'data/modernizations.json', 'name': 'upgrades'},
  {'path': 'data/removed_ships.json', 'name': 'old_ships'},
  {'path': 'data/ship_additional.json', 'name': 'ship_wiki'},
]

MERGED_NAME = 'data/plugin.json'

merged = {}
for f in json_files:
  print(f)
  # remember to add correct encoding here
  with open(f['path'], 'r', encoding='utf8') as j:
    curr = json.load(j)
    merged[f['name']] = curr

# write it to json
with open(MERGED_NAME, 'w+') as l:
    l.write(json.dumps(merged) + '\n')
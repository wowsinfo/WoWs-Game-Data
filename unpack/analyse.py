# %%
# imports and helpers
import json


def read_gameparams() -> dict:
    with open('GameParams-0.json', 'r') as f:
        gameparams = json.load(f)
    return gameparams


def write_json(data: dict, filename: str):
    with open(filename, 'w') as f:
        json_str = json.dumps(data, ensure_ascii=False)
        f.write(json_str)


# %%
# experiment here
params = read_gameparams()
params_keys = list(params.keys())

# %%
for key in params_keys:
    item = params[key]
    if item['typeinfo']['type'] == 'Ship' and item['typeinfo']['nation'] != 'Events':
        if 'shimakaze' in key.lower():
            # write_json(item, 'shimakaze.json')

            # get the structure overall
            try:
                for level1 in item:
                    print(level1)
                    # make sure it is a dict
                    if isinstance(item[level1], dict):
                        for level2 in item[level1]:
                            print('\t- ' + level2)
            except TypeError:
                print('\t- no structure')

# %%

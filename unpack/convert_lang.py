"""
Convert the old react native language file to arb.
"""

import json

if __name__ == '__main__':
    with open('lang.js', 'r', encoding='utf8') as lang:
        lang_str = lang.read()

    # remove first two lines
    lang_str = lang_str[lang_str.index('\n') + 2:]
    json_str = ''
    # print the first line
    for line in lang_str.split('\n'):
        if 'export const lang' in line:
            json_str += '{\n'
            continue

        if ': {' in line:
            lang_code = line.split(': {')[0].strip().replace("'", '')
            json_str += '    "' + lang_code + '": {\n'
            continue

        if '},' in line:
            # remove the last ,
            json_str = json_str[:-2]
            json_str += '    },\n'
            continue

        temp = line.split(': ')
        if len(temp) == 2:
            json_str += '        "' + \
                temp[0].strip() + '": ' + \
                temp[1].strip().replace("'", '"') + '\n'
    # remove the last ,
    json_str = json_str[:-2]
    json_str += '}\n'

    # with open('temp_lang.json', 'w', encoding='utf8') as lang:
    #     lang.write(json_str)

    # read as json
    json_obj = json.loads(json_str)
    with open('lang_final.json', 'w', encoding='utf8') as f:
        json_str = json.dumps(json_obj, ensure_ascii=False)
        f.write(json_str)

    # separate the lang code
    for lang in json_obj:
        with open('converted_' + lang + '.json', 'w', encoding='utf8') as f:
            json_str = json.dumps(json_obj[lang], ensure_ascii=False)
            f.write(json_str)

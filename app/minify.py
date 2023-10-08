import json
import sys
import glob

if __name__ == "__main__":
    # minify all json files from the current directory
    for filename in glob.glob("**/*.json", recursive=True):
        with open(filename, 'r', encoding='utf8') as f:
            data = json.load(f)
        with open(filename, 'w') as outfile:
            json_str = json.dumps(data, ensure_ascii=False)
            outfile.write(json_str)

import json
import gnu_mo_files as mo
import shutil
import os
import sys
from wows_gameparams.WoWsGameParams import WoWsGameParams
sys.path.append('unpack/wows_gameparams')


class WoWsUnpack:
    def __init__(self, path):
        self.path = path

    def _findLatestBinFolder(self):
        """
        Finds the latest folder in the bin folder
        """
        bin_folders = os.listdir("{}/bin".format(self.path))
        if (len(bin_folders) == 0):
            raise ValidationError("Nothing inside bin folder")
        bin_folders.sort()
        return bin_folders[-1]

    def _wowsunpack(self, list: bool = False) -> str:
        latest_bin = self._findLatestBinFolder()
        print("Latest bin folder: " + latest_bin)
        flag = '-l' if list else '-x'
        return 'wowsunpack.exe {} {}/bin/{}/idx -p ../../../res_packages'.format(flag, self.path, latest_bin)

    def writeContentList(self):
        """
        Writes the content list to a file, DEBUG ONLY
        """
        os.system(self._wowsunpack(list=True) + ' > contents.txt')
        print("done writing content list")

    def unpackGameParams(self):
        """
        Unpacks *.data from the bin folder
        """
        os.system(self._wowsunpack() + ' -I content/*.data')
        print("done unpacking game params")

    def decodeGameParams(self):
        """
        Decodes GameParams.data from content folder
        """
        data_path = 'content/GameParams.data'
        if os.path.exists(data_path):
            gp = WoWsGameParams(data_path)
            print("decoding game params")
            gp.decode()
            print("done decoding game params")
        else:
            raise FileNotFoundError("GameParams.data not found")

    def unpackGameIcons(self):
        """
        Unpack game icons from the bin folder
        """
        os.system(self._wowsunpack() + ' -I gui/*.png')
        print("done unpacking game icons")

    def unpackGameMaps(self):
        """
        Unpack game maps from the bin folder
        """
        os.system(self._wowsunpack() + ' -I spaces/*')
        print("done unpacking game icons")

    def decodeLanguages(self):
        """
        Decodes the language from global.mo
        """
        latest_bin = self._findLatestBinFolder()
        language_folder = '{}\\bin\\{}\\res\\texts'.format(
            self.path, latest_bin)

        # only decode en, zh and jp
        for folder in os.listdir(language_folder):
            if folder in ['en', 'zh', 'ja']:
                decoded_dict = mo.read_mo_file(
                    language_folder + '\\' + folder + '\\LC_MESSAGES\\global.mo')
                del decoded_dict['']
                with open('{}_lang.json'.format(folder), 'w', encoding="utf-8") as outfile:
                    json_str = json.dumps(decoded_dict, ensure_ascii=False)
                    outfile.write(json_str)

        print("done decoding languages")


if __name__ == "__main__":
    print("Make sure the game path is valid!")
    print()
    print("Unpacking...")
    if os.path.exists('game.path'):
        with open('game.path', 'r') as f:
            path = f.read()
        unpack = WoWsUnpack(path)
        # unpack.unpackGameIcons()
        # unpack.unpackGameMaps()
        # unpack.unpackGameParams()
        unpack.decodeGameParams()
        # unpack.decodeLanguages()
    else:
        with open('game.path', 'w') as f:
            print("Created game.path")
            print("Please place your game path in it")
        exit(-1)

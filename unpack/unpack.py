import os
from wows_gameparams import WoWsUnpack


if __name__ == "__main__":
    print("Make sure the game path is valid!")
    print()
    print("Unpacking...")
    if os.path.exists('game.path'):
        with open('game.path', 'r') as f:
            path = f.read()
        unpack = WoWsUnpack(path)
        unpack.unpackGameParams()
        unpack.decodeGameParams()

        unpack.unpackGameMaps()
        unpack.decodeLanguages()

        unpack.unpackGameIcons()
        # unpack.packAppAssets()
    else:
        with open('game.path', 'w') as f:
            print("Created game.path")
            print("Please place your game path in it")
        exit(-1)

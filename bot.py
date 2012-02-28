import sys
from os.path import join
sys.path.append(join(sys.path[0], 'lib'))
sys.path.append(join(sys.path[0], 'ameliabot'))
from ameliabot import amelia

amelia.SERVER   = 'localhost'
amelia.PORT     = 6667
amelia.NICK     = 'DungeonBot'
amelia.USER     = 'DungeonBot'
amelia.NAME     = 'http://github.com/JosephCrowe/DungeonBot'
amelia.CHANNELS = ['#DungeonBot']
amelia.PLUGINS  = ['dungeon']

amelia.main()
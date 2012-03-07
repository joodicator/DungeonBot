import sys, os.path
for dir in 'ameliabot', 'dungeonbot', 'lib':
    sys.path.append(os.path.join(sys.path[0], dir))

conf = {
    'server':   'localhost',
    'port':     6667,
    'nick':     'DungeonBot',
    'user':     'DungeonBot',
    'name':     'http://github.com/JosephCrowe/DungeonBot',
    'channels': ['#DungeonBot'],
    'plugins':  ['message', 'control', 'dungeon']
}
execfile('conf/bot.txt', conf)

from amelia import AmeliaBot
AmeliaBot(conf).mainloop()

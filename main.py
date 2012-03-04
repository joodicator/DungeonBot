import sys, os.path
for dir in 'ameliabot', 'dungeonbot', 'lib', 'conf':
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
execfile('bot.txt', dict(), conf)

from amelia import AmeliaBot
AmeliaBot(conf).mainloop()

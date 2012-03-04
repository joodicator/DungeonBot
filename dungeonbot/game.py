from util import table, fdict

dungeons = table('dungeons.txt', 'dungeon_spec')
sizes    = fdict('sizes.txt')

class Game(object):
    __slots__ = 'install', 'uninstall', 'chan', 'time'
    link = LinkSet()
    
    def __init__(self, chan):
        self.install, self.uninstall = \
            self.link.map(lambda (e, f): ((e, chan), bind(f, self)))
        self.chan = chan
        self.time = 0

    def msg(self, bot, msg):
        bot.send_msg(self.chan, msg)
    
    @link('!help')
    def help(self, bot, id, args):
        self.msg(bot, 'I only help those who help themselves.')

class Hero(object):
    __slots__ = 'name', 'skill', 'exp'

    def __init__(self, name):
        self.name = name
        self.skill = {}
        self.exp = {''}

class Dungeon(object):
    __slots__ = 'spec'
    
    def __init__(self, spec):
        self.spec = spec

    
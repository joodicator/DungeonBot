from util import LinkSet, table, fdict, bind
from itertools import *
import re

dungeons = table('conf/dungeons.txt', 'dungeon_spec')
conf = fdict('conf/general.txt')

def normalise_name(name):
    name = name.strip()
    name = re.sub(r'[\x00-\x1F]', '', name)
    name = re.sub(r'\s+', ' ', name)
    return name

class Game(object):
    __slots__ = 'install', 'uninstall', 'chan', 'heroes', 'turn', 'rounds'
    conf = conf['game']
    link = LinkSet()
    
    def __init__(self, chan):
        self.install, self.uninstall = \
            self.link.map(lambda (e, f): ((e, chan), bind(f, self)))
        self.chan = chan
        self.heroes = dict()
        self.turn = []
        self.rounds = 0

    def msg(self, bot, msg, *args):
        bot.send_msg(self.chan, msg % args)
    
    @link('!help')
    def help(self, bot, id, args):
        self.msg(bot, 'I only help those who help themselves.')

    @link('!join')
    def join(self, bot, id, args):
        nick = id.nick
        if (id.nick in self.heroes):
            name = self.heroes[nick].name
            return self.msg(bot, '%s: you are already playing as %s.',
                nick, name)
        
        name = normalise_name(args)
        for (onick, ohero) in self.heroes.iteritems():
            if ohero.name.upper() != name.upper(): continue
            return self.msg(bot, '%s: %s is already being played by %s.',
                nick, ohero.name, onick)
        
        self.heroes[nick] = Hero(name)
        self.turn.append(nick)
        self.msg(bot, '%s joins the game.', name)
    
    @link('!retire')
    def retire(self, bot, id, args):
        nick = id.nick
        if nick not in self.heroes: return
        if nick in self.turn: self.turn.remove(nick)
        hero = self.heroes[nick]
        del self.heroes[nick]
        self.msg(bot, '%s retires from the game.', hero.name)

    @link('!explore')
    def explore(self, bot, id, args):
        pass
    
    @link('!delve')
    def delve(self, bot, id, args):
        pass

    @link('!list')
    def list(self, bot, id, args):
        pass
    
    @link('!stats')
    def stats(self, bot, id, args):
        pass
    
    @link('!train')
    def train(self, bot, id, args):
        pass

    @link('!research')
    def research(self, bot, id, args):
        pass
    
class Dungeon(object):
    __slots__ = 'spec', 'danger', 'mystery', 'level'
    base = conf['dungeon_base']
    sizes = conf['dungeon_sizes']
    
    def __init__(self, spec):
        self.spec = spec
        self.danger = self.base['danger_start'] + spec['danger_start']
        self.mystery = self.base['mystery_start'] + spec['mystery_start']
        self.level = 0


class Hero(object):
    __slots__ = 'name', 'fight_skill', 'fight_exp', 'lore_skill', 'lore_exp'
    conf = conf['hero']
    
    def __init__(self, name):
        self.name = name
        self.fight_skill = self.conf['fight_start']
        self.lore_skill = self.conf['lore_start']
        self.fight_exp = 0
        self.lore_exp = 0

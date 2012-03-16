from util import LinkSet, table, fdict, bind, after
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
    
    def hero(func):
        def hero_decd(self, bot, id, args):
            if id.nick not in self.heroes: return False
            return func(self, bot, id, args, self.heroes[id.nick])
        return hero_decd
    
    @after(hero)
    def hero_turn(func):
        def turn_decd(self, bot, id, args, hero):
            if not(self.turn and self.turn[0] == hero): return False
            res = func(self, bot, id, args, hero)
            if res is not False: self.end_turn(bot)
            return res
        return turn_decd
    
    def end_turn(self, bot):
        self.turn.pop(0)
        if self.turn:
            self.start_turn(bot)
        else:
            self.end_round(bot)
    
    def start_turn(self, bot):
        self.msg(bot, 'It is %s\'s turn.', self.turn[0].name)
    
    def end_round(self, bot):
        self.rounds += 1
        self.turn = self.heroes.values()
        self.start_turn(bot)
    
    @link('!help')
    def help(self, bot, id, args):
        self.msg(bot, 'Help yourself.')

    @link('!list')
    def list(self, bot, id, args):
        self.msg(bot, 'The list is empty.')

    @link('!join')
    def join(self, bot, id, args):
        nick = id.nick
        if (nick in self.heroes):
            name = self.heroes[nick].name
            return self.msg(bot, '%s: you are already playing as %s.',
                nick, name)
        
        name = normalise_name(args)
        for (onick, ohero) in self.heroes.iteritems():
            if ohero.name.upper() != name.upper(): continue
            return self.msg(bot, '%s: %s is already being played by %s.',
                nick, ohero.name, onick)
        
        hero = Hero(name)
        self.heroes[nick] = hero
        self.msg(bot, '%s joins the game.', name)
        
        self.turn.append(hero)
        if len(self.turn) == 1: self.start_turn(bot)
    
    @link('!retire')
    @hero
    def retire(self, bot, id, args, hero):
        if hero in self.turn: self.turn.remove(hero)
        del self.heroes[id.nick]
        self.msg(bot, '%s retires from the game.', hero.name)
    
    @link('!stats')
    @hero
    def stats(self, bot, id, args, hero):
        self.msg(bot, '%s stats', hero.name)
    
    @link('!explore')
    @hero_turn
    def explore(self, bot, id, args, hero):
        self.msg(bot, '%s explores the land.', hero.name)
    
    @link('!delve')
    @hero_turn
    def delve(self, bot, id, args, hero):
        self.msg(bot, '%s journeys to %s.', hero.name, args)
    
    @link('!train')
    @hero_turn
    def train(self, bot, id, args, hero):
        self.msg(bot, '%s sharpens their martial skills.', hero.name)

    @link('!research')
    @hero_turn
    def research(self, bot, id, args, hero):
        self.msg(bot, '%s studies ancient tomes.', hero.name)

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

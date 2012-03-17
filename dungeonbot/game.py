from util import LinkSet, table, fdict, bind, after, dice
from auth import admin
from collections import OrderedDict
from itertools import *
from functools import *
import random
import re

dungeons = table('conf/dungeons.txt', 'dungeon_spec')
conf = fdict('conf/general.txt')

DANGER  = 1
MYSTERY = 2

def normalise_name(name):
    name = name.strip()
    name = re.sub(r'[\x00-\x1F]', '', name)
    name = re.sub(r'\s+', ' ', name)
    return name

def hero_names(heroes):
    names = map(lambda h: h.name, heroes)
    names = ', '.join(names[:-2] + [' and '.join(names[-2:])])
    return names

class Game(object):
    __slots__ = (
        'install', 'uninstall', 'chan',
        'hidden_dungeons', 'found_dungeons', 'complete',
        'heroes', 'rounds', 'turn', 'attacks')

    conf = conf['game']
    link = LinkSet()
    
    def __init__(self, chan):
        self.install, self.uninstall = \
            self.link.map(lambda (e, f): ((e, chan), bind(f, self)))
        self.chan = chan
        self.start_game()
    
    # Decorates a command function so that it is only usable by a user who
    # controls a hero. Appends a parameter giving their Hero instance.
    def hero(func):
        def hero_decd(self, bot, id, args):
            if id.nick not in self.heroes: return False
            return func(self, bot, id, args, self.heroes[id.nick])
        return hero_decd
    
    # Acts like the @hero decorator, except that the command is now only usable
    # by the hero whose current turn it is, and calls end_turn() if the function
    # terminates without returning False.
    @after(hero)
    def hero_turn(func):
        def turn_decd(self, bot, id, args, hero):
            if not(hero in self.turn): return False
            res = func(self, bot, id, args, hero)
            if res is not False: self.end_turn(bot, hero)
            return res
        return turn_decd

    # Decorator to add the given command to the !help listing. The first word
    # in the help string should be all lowercase and the name of the command,
    # e.g. '!command'.
    def help(string):
        def help_dec(func):
            func.func_dict['help_string'] = string
            return func
        return help_dec

    def msg(self, bot, msg, *args):
        bot.send_msg(self.chan, msg % args)
    
    def start_game(self):
        self.hidden_dungeons = set(dungeons)
        self.found_dungeons = OrderedDict()
        self.heroes = OrderedDict()
        self.complete = False
        self.rounds = 0
        self.turn = []
        self.attacks = OrderedDict()
    
    def end_game(self, bot):
        self.msg(bot, 'Game over.')
    
    def start_turn(self, bot):
        pass
        
    def end_turn(self, bot, hero):
        self.turn.remove(hero)
        if self.turn:
            plural = len(self.turn) > 1
            names = hero_names(self.turn)
            self.msg(bot, '%s %s as yet strategising.',
                names, 'are' if plural else 'is')
        else:
            self.end_round(bot)
    
    def end_round(self, bot):
        for dungeon, attackers in self.attacks.iteritems():
            self.attack(bot, dungeon, attackers)
        
        self.rounds += 1
        self.msg(bot, 'Day %s has ended.', self.rounds)
        
        if self.complete:
            self.msg(bot,
                'Success! The final dungeon has been cleared.')
            self.end_game()
        elif self.rounds >= self.conf['doom']:
            self.msg(bot,
                'Failure! the objective was not completed in time.')
            self.end_game()
        else:
            self.turn = self.heroes.values()
            self.attacks.clear()
            self.start_turn(bot)
    
    def attack(self, bot, dungeon, heroes):
        advanced = 0
        while not dungeon.cleared():
            defeated = 0
            for hero in heroes: defeated |= hero.attack(dungeon)
            if not defeated & (DANGER | MYSTERY): break
            dungeon.advance()
            advanced += 1
        
        plural = len(heroes) > 1
        names = hero_names(heroes)
        if advanced:
            self.msg(bot, '%s %s %s to level %s%s',
                names, 'clear' if plural else 'clears',
                dungeon.spec.name, dungeon.level,
                ', completely conquering it!' if dungeon.cleared() else '.')
            if dungeon.cleared() and dungeon.spec.size == 'huge':
                self.complete = True
        else:
            self.msg(bot, '%s %s to advance in %s.', 
                names, 'fail' if plural else 'fails', dungeon.spec.name)
    
    @link('!help')
    def _help(self, bot, id, args):
        # Available commands are encoded as the 'help_string' attribute of
        # the corresponding functions in the class namespace, using the @help
        # decorator.
        cmds = type(self).__dict__.itervalues()
        cmds = (f.help_string for f in cmds if hasattr(f, 'help_string'))
        cmds = {re.match(r'\S+', s).group():s for s in cmds}
        
        args = re.sub(r'^!?(?=\S)', '!', args.strip().lower())
        if args in cmds:
            self.msg(bot, cmds[args])
        elif args == '!help':
            self.msg(bot, '!help [COMMAND] -- displays information about the'
                'specified command, or a list of commands if none is given.')
        elif args:
            self.msg(bot, 'There is no help on that topic.')
        else:
            self.msg(bot, 'Available commands: %s, or !help [COMMAND].',
                ', '.join(cmds.iterkeys()))

    @link('!reset')
    @help('!reset -- (admin) clears the current game and starts a new one.')
    @admin
    def _reset(self, bot, id, args):
        self.end_game(bot)

    @link('!list')
    @help('!list -- lists the currently known dungeons.')
    def _list(self, bot, id, args):
        self.msg(bot, '== Known Dungeons ==')
        for dungeon in self.found_dungeons.itervalues():
            for line in dungeon.report(): self.msg(bot, line)
        self.msg(bot, '== End of List ==')

    @link('!join')
    @help('!join NAME -- joins the game with the given character name.')
    def _join(self, bot, id, args):
        nick = id.nick
        if (nick in self.heroes):
            name = self.heroes[nick].name
            return self.msg(bot, '%s: you are already playing as %s.',
                nick, name)
        
        name = normalise_name(args)
        if not name:
            return self.msg(bot, '%s: please choose a more substantial name.',
                nick)
        
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
    @help('!retire -- removes your character from the game.')
    @hero
    def _retire(self, bot, id, args, hero):
        if hero in self.turn: self.turn.remove(hero)
        del self.heroes[id.nick]
        self.msg(bot, '%s retires from the game.', hero.name)
    
    @link('!stats')
    @help("!stats -- displays your character's attributes.")
    @hero
    def _stats(self, bot, id, args, hero):
        for line in hero.report(): self.msg(bot, line)
    
    @link('!explore')
    @help("!explore -- search the land for undiscovered places of interest.")
    @hero_turn
    def _explore(self, bot, id, args, hero):
        if not self.hidden_dungeons:
            self.msg(bot, '%s explores the land, but finds nothing.', hero.name)
            return
        [dungeon] = random.sample(self.hidden_dungeons, 1)
        self.hidden_dungeons.remove(dungeon)
        dungeon = Dungeon(dungeon)
        self.found_dungeons[dungeon.spec.name] = dungeon
        self.msg(bot, '%s explores the land, uncovering a dungeon:', hero.name)
        for line in dungeon.intro(): self.msg(bot, line)
    
    @link('!delve')
    @help("!delve DUNGEON -- descend into a previously discovered dungeon.")
    @hero_turn
    def _delve(self, bot, id, args, hero):
        args = normalise_name(args)
        matches = re.compile(re.escape(args), re.I).search
        matches = filter(matches, self.found_dungeons.iterkeys())
        if not matches:
            self.msg(bot, 'No dungeon by that name is known.')
            return False
        if len(matches) > 1:
            self.msg(bot, 'Please be more specific.')
            return False
        [name] = matches
        dungeon = self.found_dungeons[name]
        if dungeon.cleared():
            self.msg(bot, '%s has already been cleared.', name)
            return False
        if dungeon not in self.attacks: self.attacks[dungeon] = []
        self.attacks[dungeon].append(hero)
        self.msg(bot, '%s journeys to %s.', hero.name, name)
    
    @link('!train')
    @help('!train -- increase your fighting experience.')
    @hero_turn
    def _train(self, bot, id, args, hero):
        hero.train_fight()
        self.msg(bot, '%s sharpens their martial skills.', hero.name)

    @link('!research')
    @help('!research -- increase your experience of lore.')
    @hero_turn
    def _research(self, bot, id, args, hero):
        hero.train_lore()
        self.msg(bot, '%s studies ancient tomes.', hero.name)

    @link('!pass')
    @help('!pass -- ends your turn without doing anything.')
    @hero_turn
    def _pass(self, bot, id, args, hero):
        self.msg(bot, '%s does nothing.', hero.name)

class Dungeon(object):
    __slots__ = 'spec', 'size', 'danger', 'mystery', 'level'
    base = conf['dungeon_base']
    sizes = conf['dungeon_sizes']
    
    def __init__(self, spec):
        self.spec = spec
        self.danger = self.base['danger_start'] + spec.danger_start
        self.mystery = self.base['mystery_start'] + spec.mystery_start
        self.size = self.sizes[self.spec.size]
        self.level = 0

    def cleared(self):
        return self.level >= self.size

    def intro(self):
        yield '%s (%s); danger: %s, mystery: %s.' \
        % (self.spec.name, self.spec.size, self.danger, self.mystery)

    def report(self):
        yield '%s (%s); danger: %s, mystery: %s, levels cleared: %s/%s.' \
        % (self.spec.name, self.spec.size, self.danger, self.mystery,
           self.level, self.size if self.cleared() else '?')
    
    def advance(self):
        self.level += 1
        self.danger += self.base['danger_step'] + self.spec.danger_step
        self.mystery += self.base['mystery_step'] + self.spec.mystery_step
        
        total = self.base['random_step'] + self.spec.random_step
        sides = total + 1 - 2*(total//4) # Must have opposite parity to total.
        step = dice(3, sides) + (total - 3*(sides + 1))/2
        if self.danger + step < 0 or self.mystery + total - step < 0:
            step = total - step
        self.danger += step
        self.mystery += total - step

class Hero(object):
    __slots__ = 'name', 'fight_skill', 'fight_xp', 'lore_skill', 'lore_xp'
    conf = conf['hero']
    
    def __init__(self, name):
        self.name = name
        self.fight_xp = self.lore_xp = self.fight_skill = self.lore_skill = 0
        self.better_fight(self.conf['fight_xp_start'])
        self.better_lore(self.conf['lore_xp_start'])

    def report(self):
        yield '%s\'s skills: fighting: %s, lore: %s.' \
            % (self.name, self.fight_skill, self.lore_skill)

    def train_fight(self):
        self.better_fight(self.conf['fight_xp_train'])
    
    def train_lore(self):
        self.better_lore(self.conf['lore_xp_train'])

    def better_fight(self, xp):
        self.fight_xp += xp
        self.fight_skill = self.fight_xp // self.conf['fight_xp_level']
    
    def better_lore(self, xp):
        self.lore_xp += xp
        self.lore_skill =  self.lore_xp // self.conf['lore_xp_level']

    # Issues an attack against the current level of the given dungeon, returning
    # a bitwise combination of DANGER and MYSTERY to indicate which aspects of
    # the dungeon, if any, were defeated.
    def attack(self, dungeon):
        result = 0
        if self.attack_danger(dungeon): result |= DANGER
        if self.attack_mystery(dungeon): result |= MYSTERY
        return result
    
    # Issues an attack against the Danger of the given dungeon, returning True
    # if the attack is successful or otherwise False.
    def attack_danger(self, dungeon):
        diff = dungeon.danger - self.fight_skill
        won = self.conf['fight_damage'](self.fight_skill) >= dungeon.danger
        self.better_fight(self.conf
            ['fight_xp_win' if won else 'fight_xp_lose']
            [0 if diff<0 else 1 if diff==0 else 2])
        return won
    
    # Issues an attack against the Mystery of the given dungeon, returning True
    # if the attack is successful or otherwise False.
    def attack_mystery(self, dungeon):
        diff = dungeon.mystery - self.lore_skill
        won = self.conf['lore_damage'](self.lore_skill) >= dungeon.mystery
        self.better_lore(self.conf
            ['lore_xp_win' if won else 'lore_xp_lose']
            [0 if diff<0 else 1 if diff==0 else 2])
        return won

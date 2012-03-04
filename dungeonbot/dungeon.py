from util import LinkSet
from game import Game

games = dict()
link = LinkSet()

def install(bot):
    link.install(bot)

def uninstall(bot):
    link.uninstall(bot)
    for channel in games.itervalues(): channel.uninstall(bot)
    games.clear()

@link('MESSAGE')
def message(bot, id, chan, msg):
    if chan == None: return
    if chan in games: return
    game = Game(chan)
    game.install(bot)
    games[chan] = game

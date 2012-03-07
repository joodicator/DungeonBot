from untwisted.magic import sign
from util import LinkSet, ID
import re

link, install, uninstall = LinkSet().triple()

@link('PRIVMSG')
def privmsg(bot, nick, user, host, target, msg, *args):
    msg = re.sub('^:', '', msg)
    if target == bot.nick: target = None
    id = ID(nick, user, host)
    yield sign('MESSAGE', bot, id, target, msg)
    yield sign(('MESSAGE', target), bot, id, msg)
    match = re.match('(?P<cmd>!\S+)\s*(?P<arg>.*)$', msg)
    if match:
        cmd, arg = match.group('cmd', 'arg')
        yield sign(cmd, bot, id, target, arg)
        yield sign((cmd, target), bot, id, arg)

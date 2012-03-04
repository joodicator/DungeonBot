from untwisted.mode import Mode, hold, apply
from util import ID, just, msign
import inspect
import re

with open('admins.txt') as file:
    admins = re.findall(r'\S+', file.read())

nickserv = ID('NickServ', 'services', 'services.newnet.net')

# Returns an object which may be yielded in an untwisted event handler to obtain
# [True] if the specified user is authenticated by NickServ as a user listed in
# admins.txt, or otherwise [False].
def check(bot, id):
    if id.nick not in admins: return just(False)
    mode = Mode()
    def notice(bot, nick, user, host, target, msg):
        if target != bot.nick: return
        if ID(nick, user, host) != nickserv: return
        match = re.match(r':STATUS (?P<nick>\S+) (?P<code>\S+)', msg)
        if match.group('nick') != id.nick: return
        code = int(match.group('code'))
        yield msign(mode, 'RESULT', code >= 3)
        bot.unlink('NOTICE', notice)
    bot.link('NOTICE', notice)
    bot.send_msg(nickserv.nick, 'STATUS ' + id.nick)
    return hold(mode, 'RESULT')

# Decorates an untwisted event handler which takes arguments 'bot' and 'id',
# causing its body to be executed iff the specified user is an admin according
# to check(bot, id).
def admin(func):
    def dfunc(*args, **kwds):
        cargs = inspect.getcallargs(func, *args, **kwds)
        [ok] = yield check(cargs['bot'], cargs['id'])
        if not ok: return
        gen = func(*args, **kwds)
        if not inspect.isgenerator(gen): return
        last = None
        try:
            while True: last = yield gen.send(last)
        except StopIteration: pass
    dfunc.__name__ = func.__name__ + '_admin'
    return dfunc

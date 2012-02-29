from utils.misc import send_msg
from channel import Channel
import collections
import re

channels = dict()
ID = collections.namedtuple('ID', ('nick', 'user', 'host'))

def init(bot):
    global BOT
    BOT = bot

def install(poll):
    poll.link('PRIVMSG', privmsg)

def privmsg(work, nick, user, host, target, msg):
    if target == BOT.NICK: return
    id = ID(nick, user, host)
    msg = re.sub(r'^:', '', msg)
    reply = lambda msg: send_msg(target, msg)
    if target not in channels: channels[target] = Channel()
    channels[target].said(id, reply, msg)

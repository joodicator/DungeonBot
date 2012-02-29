import re
from dispatcher import Dispatcher

__all__ = 'Channel'

class Channel(object):
    def said(self, id, reply, msg):
        Channel.dispatch(msg, self, id, reply)
    
    def help(self, id, reply):
        reply('%s: fuck off.' % id.nick)
    
    dispatch = Dispatcher()
    dispatch.hook(help, r'!help(\s|$)')

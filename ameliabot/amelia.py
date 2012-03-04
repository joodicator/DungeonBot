import stdlog as std
from untwisted.network import *
from utils.misc import *
import xirclib
from socket import *
from importlib import import_module
import sys
from plugins.standard import head

default_conf = {
    'server':   'irc.freenode.net',
    'port':     6667,
    'nick':     'ameliabot',
    'user':     'ameliabot',
    'name':     'ameliabot',
    'host':     '0',
    'channels': ['#untwisted'],
    'plugins':  []
}

class AmeliaBot(Mac):
    send_cmd = send_cmd
    send_msg = send_msg

    def __init__(self, conf=None):
        # Load configuration
        self.conf = default_conf.copy()
        if conf: self.conf.update(conf)
        
        # Initialise socket
        sock = socket(AF_INET, SOCK_STREAM)
        address = gethostbyname(self.conf['server'])
        sock.connect((address, self.conf['port']))
        Mac.__init__(self, Gear(), sock)#, default=self.default)
        
        # Initialise events
        std.install(self)
        xirclib.install(self)
        self.link('433', self.err_nicknameinuse)
        self.link('001', self.registered)
        
        # Load plugins
        def plugins():
            yield head
            for name in self.conf['plugins']:
                print '! plugin: %s' % name
                yield import_module(name)
        for plugin in plugins():
            plugin.install(self)
        
        # Start registration
        self.nick = self.conf['nick']
        self.send_cmd('NICK %s' % self.nick)
        self.send_cmd('USER %(user)s %(host)s %(server)s :%(name)s' % self.conf) 
    
    def err_nicknameinuse(self, bot, *args):
        self.nick += "_"
        self.send_cmd('NICK %s' % self.nick)

    def registered(self, *args):
        for channel in self.conf['channels']:
            self.send_cmd('JOIN %s' % channel)

    def mainloop(self):
        return self.gear.mainloop()
    
    def default(self, event, *args, **kwds):
        if type(event) == int: return
        print '~ ' + repr(event)


if __name__ == '__main__':
    gear = AmeliaBot()
    gear.mainloop()


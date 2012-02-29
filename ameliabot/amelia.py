from untwisted.utils import std
from untwisted.network import *
from utils.misc import *
import xirclib
import socket
import cmd
import importlib
import sys

#plugins which are always be loaded.
import plugins.standard.head

#This file contains settings like server address, nick etc
from stuff import *


def main():
    self = sys.modules[__name__]

    #Initialize the basic objects
    gear = Gear()
    poll = Poll(gear)


    #Install the basic event callbacks
    std.install(poll)

    #Install the xirclib protocol
    xirclib.install(poll)

    #Install the bot system of commands
    cmd.install(poll)

    #It loads the plugins
    def iplugins():
        yield plugins.standard.head
        for name in PLUGINS or []:
            yield importlib.import_module(name)
    for plugin in iplugins():
        if hasattr(plugin, 'init'): plugin.init(self)
        plugin.install(poll)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    address = socket.gethostbyname(SERVER)
    sock.connect((address, PORT))

    server = Work(poll, sock)

    send_cmd(server, 'NICK %s' % NICK)
    send_cmd(server, 'USER %s %s %s %s' % (USER, NAME, 'alpha', 'beta'))
    for channel in CHANNELS or []:
        send_cmd(server, 'JOIN %s' % channel)

    gear.mainloop()


if __name__ == '__main__':
    main()

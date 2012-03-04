# Copyright (C) 2011  Iury O. G. Figueiredo
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA
#
# Iury <robatsch@hotmail.com>


""" The untwisted core. """

from select import select
from untwisted.mode import *
from socket import *

""" 
    These are the mainstream events. 
    If a given work is ready to be read then use READ.
    For writting use WRITE.
    If a given exception occured in one of the works/sockets then use ERR.
    If a given work/socket was closed use CLOSE.
    If it is a socket server initialized with

    work = Work(poll, sock)
    work.server = True

    then you use ACCEPT.

"""


#These events are never handled by
#a call to Mod.drive(data)

READ   = 1
WRITE  = 2
EXC    = 3
CLOSE  = 4
ACCEPT = 5
FOUND  = 6
LOAD   = 7
BUFFER = 8
LOCAL  = 9
RECV   = 10

class Gear(object):
    def __init__(self, timeout=None):
        self.timeout = timeout

        self.rlist = []
        self.wlist = []
        self.xlist = []

        self.SIZE = 1024

 
    def mainloop(self):
        while True:
            self.update()

    def update(self):
        r, w, x = [], [], []

        rmap = lambda obj: obj.is_read
        wmap = lambda obj: obj.is_write or obj.is_dump
        xmap = lambda obj: obj.is_write and obj.is_read
        
        r = filter(rmap, self.rlist)
        w = filter(wmap, self.wlist)
        x = filter(xmap, self.xlist)

        resource = select(r , w , x, self.timeout)

        self.rsock, self.wsock, self.xsock = resource

        self.process_rsock()
        self.process_wsock()
        self.process_xsock()

    def process_rsock(self):
        for ind in self.rsock:
            ind.poll.drive(READ, ind)

    def process_wsock(self):
        for ind in self.wsock:
            ind.poll.drive(WRITE, ind)

    def process_xsock(self):
        for ind in self.xsock:
            ind.poll.drive(EXC, ind)
 

class Poll(Mode):
    """ 
        This class holds a pool of sockets/works 
        which are sharing a same reader. 

        The reader callback works as a terminator.
        It returns True or False.
        If it returns True it means it was found a terminator.

        Using this model makes things loose.
        Which permits you even use variable terminators.
      
        ***

        For a detailed example see /sample/sandbox/box.py
        Where it uses ';' as terminator.
    """
    def __init__(self, gear):
        Mode.__init__(self, self.default)

        self.gear = gear
        """ Adding itself to the gear """

    def default(self, event, child=None, *args, **kwargs):
        if isinstance(child, Fish):
            child.drive(event, child, *args, **kwargs)


class Work(socket):
    def __init__(self, poll, sock, is_read=True, is_write=False):
        socket.__init__(self, _sock=sock)

        self.is_read  = is_read

        """ To use yield hold(obj, WRITE)
            you need to pass is_write = True
            to tell the core to add this socket instance
            to the list of selectable objects for writting.
        """
        self.is_write = is_write

        """ Initially we aren't dumping anything. """
        self.is_dump  = False

        self.poll = poll
        self.sock = sock

        #If it is not a socket server.
        self.server = False

        #Registering itself.
        poll.gear.rlist.append(self)
        poll.gear.wlist.append(self)
        poll.gear.xlist.append(self)

        self.BLOCK = 1024
        self.SIZE = 1024

        #The socket stack.
        self.stack = ''
        self.data = ''

        self.queue = ''

    def dump(self, data):
        """ If you are going to use send 
            then you can't use dump.
            Otherwise you might have some odd behavior.

        """
        self.queue   = self.queue + data
        self.is_dump = True

    def destroy(self):
        self.poll.gear.rlist.remove(self)
        self.poll.gear.wlist.remove(self)
        self.poll.gear.xlist.remove(self)

class Fish(Work, Mode):
    def __init__(self, poll, sock, is_read=True, is_write=False, default=None):
        Work.__init__(self, poll, sock, is_read, is_write)
        Mode.__init__(self, default)


class Mac(Fish):
    def __init__(self, gear, sock, is_read=True, is_write = False, default=None):
        self.gear = gear
        Fish.__init__(self, self, sock, is_read, is_write, default)

_all__ = [
            'Work', 
            'Poll', 
            'Fish',
            'Gear', 
            'READ', 
            'WRITE',
            'EXC', 
            'FOUND',
            'LOAD', 
            'BUFFER', 
            'sign',
            'CLOSE',
            'ACCEPT',
            'hold',
            'sign',
            'Mac'
          ]


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
    def __init__(self):
        self.pool = []

    def mainloop(self):
        while True:
            self.update()

    def update(self):
        for ind in self.pool[:]:
            ind.update()

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
    
        The timeout param for the constructor is passed to select.select.
        It determins how long select will wait for a socket being ready.
    """
    #receives protocol
    def __init__(self, gear, timeout=0):
        Mode.__init__(self, self.default)

        self.gear = gear
        self.timeout = timeout

        self.rlist = []
        self.wlist = []
        self.xlist = []
        self.slist = []

        self.SIZE = 1024

        """ Adding itself to the gear """
        gear.pool.append(self)

    def isalive(self):
        """ 
            It returns True if self.rlist, self.wlist, self.xlist 
            holds some socket which is actually being processed.
        """

        return self.rlist or self.wlist or self.xlist

    def update(self):
        if not self.isalive():
            return

        resource = select(self.rlist, 
                          self.wlist, 
                          self.xlist, self.timeout)

        self.rsock, self.wsock, self.xsock = resource

        self.process_rsock()
        self.process_wsock()
        self.process_xsock()

    def process_rsock(self):
        for ind in self.rsock:
            self.drive(READ, ind)

    def process_wsock(self):
        for ind in self.wsock:
            self.drive(WRITE, ind)

    def process_xsock(self):
        for ind in self.xsock:
            self.drive(EXC, ind)
   
    def default(self, event, child=None, *args, **kwargs):
        if isinstance(child, Fish):
            child.drive(event, child, *args, **kwargs)


class Work(socket):
    def __init__(self, poll, sock):
        socket.__init__(self, _sock=sock)

        self.poll = poll
        self.sock = sock

        #If it is not a socket server.
        self.server = False

        #Registering itself.
        poll.rlist.append(self)
        poll.wlist.append(self)
        poll.xlist.append(self)

        self.BLOCK = 1024
        self.SIZE = 1024

        #The socket stack.
        self.stack = ''
        self.data = ''

        self.queue = ''

    def dump(self, data):
        self.queue = self.queue + data


    def deactive(self, poll):
        pass
    
    def active(self, poll):
        pass

    def destroy(self):
        self.poll.rlist.remove(self)
        self.poll.wlist.remove(self)
        self.poll.xlist.remove(self)

class Fish(Work, Mode):
    def __init__(self, poll, sock):
        Work.__init__(self, poll, sock)
        Mode.__init__(self)

class Shell:
    def __init__(self, poll, sock):
        self.server = False

    def update(self):
        resource = select([self], 
                          [self], 
                          [], self.timeout)

        self.rsock, self.wsock, self.xsock = resource

        if self.rsock:
            if self.server:
                self.handle_accept()

        if self.wsock:
            self.handle_write()

        if self.xsock:
            self.handle_exc

    def recv(self, size):
            
        pass

    def handle_write(self):
        pass

    def handle_read(self):
        pass

    def handle_close(self):
        pass

    def handle_error(self):
        pass

    def handle_exc(self):
        pass

class Mac(socket, Mode):
    def __init__(self, gear, sock, timeout=0):
        socket.__init__(self, _sock=sock)
        Mode.__init__(self)
        self.server = False
        self.gear = gear
        self.timeout = timeout
        #I should rmeove this method
        self.sock = sock

        gear.pool.append(self)
        self.BLOCK = 1024
        self.SIZE = 1024

        #The socket stack.
        self.stack = ''
        self.data = ''

        self.queue = ''

    def dump(self, data):
        self.queue = self.queue + data

    def update(self):
        resource = select([self], 
                          [self], 
                          [self], self.timeout)

        self.rsock, self.wsock, self.xsock = resource

        if self.rsock:
            self.drive(READ, self)
        if self.wsock:
            self.drive(WRITE, self)
        if self.xsock:
            self.drive(EXC, self)

    def destroy(self):
        self.gear.pool.remove(self)

class Hub(socket, Mode):
    def __init__(self, poll, sock):
        Work.__init__(self, poll, sock)

        self.send_list = []
        self.recv_list = []
        self.outgoing = None
        self.incoming = None

    def update(self):
        pass

    def send_file(self, filename):
        pass

    def recv_file(self, filename, size_file=-1):
        pass

    def stop(self):
        pass


__all__ = [
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


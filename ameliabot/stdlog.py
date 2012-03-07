from untwisted.network import *
from untwisted.utils.common import read, write
from untwisted.event import *

ibuf = ''
obuf = ''
TERM = '\r\n'

def install(obj):
    """ 
        If you don't want bufferizaiton with stack
        just pass lambda obj: None
    """

    obj.link(READ, update)
    obj.link(WRITE, flush)

def update(obj):
    if obj.server:
        #if this object is a socket
        #server and it is ready to be read
        #then some host connected
        yield sign(ACCEPT, obj)
    else:
        #update the obj.data variable
        #so clients of this instance
        #can use it
        obj.data = read(obj)
        ilog(obj.data)
        if not obj.data:
            #socket returns '' in case of
            #the host having closed
            yield sign(CLOSE, obj)
        else:
            #the LOAD event means 
            #we have received the data
            yield sign(LOAD, obj)

            #we need this event in order
            #to make charset cohercion
            #and use the append callback
            #to glue the incoming data
            yield sign(DATA, obj)

def flush(obj):
    """
        This function dumps data in blocks through
        the socket
    """
    #sends data in blocks
    size = write(obj, obj.queue[:obj.BLOCK])
    olog(obj.queue[:size])

    #slices the string leaving
    #what remains to send
    obj.queue = obj.queue[size:]

    if not obj.queue and obj.is_dump:
        #if obj.queue is empty and obj.is_dump
        #is set true then we have sent
        #all data
        obj.is_dump = False
        yield sign(DUMPED, obj)

def ilog(data):
    global ibuf
    ibuf += data
    ibuf = ibuf.split(TERM)
    for line in ibuf[:-1]:
        print '> ' + line
    ibuf = ibuf[-1]
    
def olog(data):
    global obuf
    obuf += data
    obuf = obuf.split(TERM)
    for line in obuf[:-1]:
        print '< ' + line
    obuf = obuf[-1]
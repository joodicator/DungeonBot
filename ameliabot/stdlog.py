from untwisted.network import *
from untwisted.utils.common import read, write

ibuf = ''
obuf = ''
TERM = '\r\n'

def install(poll):
    poll.link(READ, update)
    poll.link(WRITE, flush)

def update(work):
    if work.server:
        yield sign(ACCEPT, work)
    else:
        work.data = read(work)
        ilog(work.data)
        work.stack = work.stack + work.data
        """ If the connection was closed. """
        if not work.data:
            yield sign(CLOSE, work)
        else:
            yield sign(LOAD, work)


def flush(work):
    size = write(work, work.queue[:work.BLOCK])
    olog(work.queue[:size])
    work.queue = work.queue[size:]

    if not work.queue:
        work.is_dump = False

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

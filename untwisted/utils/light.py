from std import flush
from untwisted.network import *
from untwisted.utils.common import read, write

def install(poll):
    poll.link(READ, update)
    poll.link(WRITE, flush)

def update(work):
    if work.server:
        yield sign(ACCEPT, work)
    else:
        work.data = read(work)
        """ If the connection was closed. """
        if not work.data:
            yield sign(CLOSE, work)
        else:
            yield sign(LOAD, work)



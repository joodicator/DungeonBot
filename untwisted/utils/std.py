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
        work.stack = work.stack + work.data
        """ If the connection was closed. """
        if not work.data:
            yield sign(CLOSE, work)
        else:
            yield sign(LOAD, work)


def flush(work):
    size = write(work, work.queue[:work.BLOCK])
    work.queue = work.queue[size:]



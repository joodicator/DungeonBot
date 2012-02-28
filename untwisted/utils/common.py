from untwisted.network import sign, FOUND, BUFFER

def shrug(work, stack, delim='\r\n'):
    chain = stack.split(delim)
    for chunk in chain[:-1]:
        yield sign(FOUND, work, chunk)
    work.stack = chain[-1]

def yuck(work, stack, size=1024):
    pass

def charset(work, name='utf-8'):
    chunk = work.stack.decode(name, 'replace')
    yield sign(BUFFER, work, chunk)

def read(work):
    """ This function can be substituted """
    return work.recv(work.SIZE)

def write(work, data):
    """ This function can be substituted """
    return work.send(data)


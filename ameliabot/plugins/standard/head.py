from untwisted.network import BUFFER

def install(poll):
    poll.link('PING', pong)
    poll.link(BUFFER, log)

def pong(work, prefix, server):
    reply = 'PONG :%s\r\n' % server
    work.dump(reply)
    print('PING PONG')

def log(work, stack):
    print(stack)


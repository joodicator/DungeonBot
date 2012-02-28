def install(poll):
    poll.link('PRIVMSG', privmsg)

def privmsg(work, *args, **kwds):
    print 'privmsg', work, args, kwds

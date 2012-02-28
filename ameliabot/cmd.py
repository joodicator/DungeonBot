from untwisted.network import sign
import re

ARG_STR = "[^ ]+"
#This regex supports "alpha beta gama" parameters between ""
#ARG_STR = '[^" ]+|"[^"]+"'
ARG_REG = re.compile(ARG_STR)

def install(poll):
    poll.link('PRIVMSG', split) 

def split(*args):
    msg = args[-1].lstrip(':')
    
    if not msg.startswith('.'):
        return

    cmdlist = re.findall(ARG_REG, msg)
    yield sign(cmdlist[0], args[0], args[1:], *cmdlist[1:])


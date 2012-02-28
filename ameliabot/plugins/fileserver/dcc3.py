from untwisted.network import *
from untwisted.utils import light
from untwisted.utils import std
from socket import SHUT_RDWR
from socket import SHUT_WR
from utils.misc import *
from stuff import NICK
import socket
from utils.misc import send_msg
from utils.ipshape import *
from utils import codepad

import os

HEADER = '\001DCC SEND %s %s %s %s\001' 
FOLDER = '/home/tau/Desktop/%s'
PORT = 56667
BLOCK = 1024

def install(poll):
    poll.link('DCC SEND', download)
    poll.link('.enlist', enlist)
    poll.link('.upload', upload)
    poll.link(CLOSE, handle_close)
    upserver(poll)

def uninstall(poll):
    poll.unlink('DCC', download)
    poll.unlink('.enlist', enlist)
    poll.unlink('.upload', upload)
    poll.unlink(CLOSE, handle_close)


def upserver(poll):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', PORT))
    sock.listen(1)
    local = Work(poll, sock)
    local.server = True

def handle_close(work):
    work.destroy()
    work.close()

def handle_failure(mac, path):
    mac.destroy()
    mac.close()
    path.close()

def enlist(work, user):
    target = user[3]
    content = '\n'.join(os.listdir(FOLDER % ''))
    addr, url = codepad.post(content, '') 
    send_msg(work, target, url)

def download(server, *args):
    filename     = args[4]
    address      = long_to_ip(int(args[5]))
    port         = int(args[6])
    file_size    = int(args[7])

    sock    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((address, port))

    path = open(FOLDER % filename, 'wb')

    proc = Mac(server.poll.gear, sock)
    light.install(proc)

    proc.link(CLOSE, handle_failure, path)

    ind = hold(proc, LOAD)
    while True:
        yield ind   
        path.write(proc.data)
        if path.tell() >= file_size:
            path.close()
            proc.shutdown(SHUT_RDWR)
            proc.close()
            proc.destroy()
            break
    

def upload(server, user, filename):
    send_cmd(server, 'USERHOST %s' % NICK)

    work, server_address, nick, ident = yield hold(server.poll, '302')

    local_address = extract_address(ident)
    file_size = os.path.getsize(FOLDER % filename)

    packet = HEADER % (filename, local_address , PORT, file_size)

    nick = user[0]
    send_msg(server, nick, packet)

    work, = yield hold(server.poll, ACCEPT)
    sock, addr = work.accept()

    path = open(FOLDER % filename, 'rb')

    host = Mac(server.poll.gear, sock)
    light.install(host)

    host.link(CLOSE, handle_failure, path)

    ind = hold(host, WRITE)
    while True:
        yield ind   
        data = path.read(BLOCK)
        if not data:
            path.close()
            host.shutdown(SHUT_WR)
            host.destroy()
            break
        else:
            host.dump(data)

def extract_address(chunk):
    address = chunk.split('@')[1]
    return ip_to_long(address)
    

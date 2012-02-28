from untwisted.network import *
from untwisted.utils import light
from untwisted.utils import std
from socket import SHUT_RDWR
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
    poll.link('DCC', download)
    poll.link('.enlist', enlist)
    poll.link('.upload', upload)
    poll.link(CLOSE, handle_close)
    upserver(poll)

def uninstall(poll):
    pass

def upserver(poll):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', PORT))
    sock.listen(1)
    local = Work(poll, sock)
    local.server = True

def handle_close(work):
    work.destroy()
    work.close()

def handle_failure(work, path):
    work.destroy()
    work.close()
    path.close()

def enlist(work, user):
    target = user[3]
    content = '\n'.join(os.listdir(FOLDER % ''))
    addr, url = codepad.post(content, '') 
    send_msg(work, target, url)

def download(server, *args):
    option       = args[4]
    filename     = args[5]
    address      = args[6]
    port         = args[7]
    file_size    = args[8]

    if option != 'SEND':
        return

    address = long_to_ip(int(address))
    port    = int(port)
    file_size    =  int(file_size)

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
    nick = user[0]
    target = user[3]

    send_cmd(server, 'USERHOST %s' % NICK)

    alpha = hold(server.poll, '302')
    profile = yield alpha

    chunk = profile[3]
    addr = extract_address(chunk)
    addr = ip_to_long(addr)

    file_size = os.path.getsize(FOLDER % filename)

    packet = HEADER % (filename, addr , PORT, file_size)

    send_msg(server, nick, packet)

    flag = hold(server.poll, ACCEPT)
    work, = yield flag

    sock, addr = work.accept()

    path = open(FOLDER % filename, 'rb')

    host = Mac(server.poll.gear, sock)
    std.install(host)

    host.link(CLOSE, handle_failure, path)

    ind = hold(host, WRITE)
    while True:
        yield ind   
        data = path.read(BLOCK)
        if not data:
            path.close()
            host.shutdown(SHUT_RDWR)
            host.close()
            host.destroy()
            break
        else:
            host.dump(data)

def extract_address(chunk):
    return chunk.split('@')[1]


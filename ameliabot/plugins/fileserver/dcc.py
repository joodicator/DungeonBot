from untwisted.network import *
from untwisted.utils import light
from socket import SHUT_RDWR
from utils.misc import *
from stuff import NICK
import socket
from utils.misc import send_msg
from utils.ipshape import *
from utils import codepad
import os

FOLDER = '/home/tau/Desktop/%s'


def install(poll):
    downlist = Poll(poll.gear)
    uplist   = Poll(poll.gear)

    light.install(downlist)
    light.install(uplist)

    downlist.link(LOAD, process_incoming_file)
    downlist.link(CLOSE, handle_close)

    poll.link('DCC', download, downlist)

    poll.link('.enlist', enlist)
    poll.link('.upload', upload, uplist)
    poll.link(CLOSE, handle_close)

    uplist.link(ACCEPT, handle_client)
    uplist.link(WRITE, process_outgoing_file)
    uplist.link(CLOSE, handle_close)

def handle_close(work):
    work.destroy()
    work.close()
    work.path.close()

def uninstall(poll):
    pool.unlink(LOAD, process_incoming_file)
    poll.unlink('DCC', download)
    poll.unlink('.enlist', enlist)
    poll.unlink('.upload', upload)

def enlist(work, user):
    target = user[3]
    content = '\n'.join(os.listdir(FOLDER % ''))
    addr, url = codepad.post(content, '') 
    send_msg(work, target, url)

def download(server, *args):
    option   = args[4]
    filename = args[5]
    address  = args[6]
    port     = args[7]
    size     = args[8]
    downlist     = args[9]

    if option != 'SEND':
        return

    sock    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    address = long_to_ip(int(address))
    port    = int(port)
    size    =  int(size)

    work = Work(downlist, sock)

    try:
        work.connect((address, port))
    except:
        work.destroy()
        work.close()
        return

    path = open(FOLDER % filename, 'wb')

    work.shell = path, size

def upload(server, user, filename, port, uplist):
    nick = user[0]
    target = user[3]

    if not os.path.isfile(FOLDER % filename):
        send_msg(server, target, 'There is no such file.')
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.bind(('', int(port)))
    except:
        send_msg(server, nick, 'The port is in use.')

    sock.listen(1)

    local = Work(uplist, sock)
    local.filename = filename
    local.server = True

    send_cmd(server, 'USERHOST %s' % NICK)

    profile = yield hold('302')
    chunk = profile[3]
    
    addr = extract_address(chunk)

    size = os.path.getsize(FOLDER % filename)

    header = '\001DCC SEND %s %s %s %s\001' 
    packet = header % (filename, ip_to_long(addr) , port, size)

    send_msg(server, nick, packet)
    
def process_incoming_file(work):
    path, size = work.shell
    path.write(work.data)
    block = path.tell()
    if block == size:
        path.close()
        work.destroy()
        work.shutdown(SHUT_RDWR)
        work.close()
    
def process_outgoing_file(work):
    BLOCK = 1024
    data = work.path.read(BLOCK)
    if not data:
        work.path.close()
        work.destroy()
        work.shutdown(SHUT_RDWR)
        work.close()
    else:
        work.dump(data)

def handle_client(work):
    conn, addr = work.accept()

    host = Work(work.poll, conn)
    work.destroy()

    path = open(FOLDER % work.filename, 'rb') 
    host.path = path

    #data = path.read()
    #path.close()
    #host.BLOCK = 2 ** 20
    #host.dump(data)

def extract_address(chunk):
    return chunk.split('@')[1]


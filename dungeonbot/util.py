from types import MethodType as instancemethod
from collections import namedtuple
from itertools import *
from functools import *
import inspect
import re

ID = namedtuple('ID', ('nick', 'user', 'host'))

# Given a function and an instance, returns an instancemethod appearing as that
# function as a method of the instnace's class, bound to the instance.
def bind(func, inst):
    return instancemethod(func, inst, inst.__class__)

# Reads a list of namedtuples from a file, where each line evalutes to a tuple,
# and the first line is a tuple of strings giving the names. Lines containing
# only whitespace are ignored.
def table(path, name='table_row'):
    with open(path) as file:
        lines = ifilter(re.compile(r'\S').search, file)
        head = namedtuple(name, eval(lines.next()))
        return imap(head, imap(eval, lines))

# Executes a file of Python statements, returning the resulting local
# dictionary.
def fdict(path):
    locals = dict()
    execfile(path, dict(), locals)
    return locals

# A LinkSet maintains a list of bindings between events and event handlers,
# providing some convenience methods for changing and using this list.
class LinkSet(object):
    __slots__ = 'links'
    
    def __init__(self):
        self.links = []
    
    # When called, a LinkSet produces a decorator that just adds given handler,
    # bound to the given event, to its list.
    def __call__(self, event):
        def link(func):
            self.links.append((event, func))
            return func
        return link
    
    # Installs all the current event bindings into the given Mode instance.
    def install(self, mode):
        for link in self.links: mode.link(*link)
    
    # Uninstalls the current event bindings from the given Mode instance.
    def uninstall(self, mode):
        for pair in self.links: mode.unlink(*link)
    
    # Maps the given function over the current bindings, returning a pair of
    # functions that respectively install and uninstall the resulting bindings.
    def map(self, func):
        links = map(func, self.links)
        def mapped_install(mode):
            for link in links: mode.link(*link)
        def mapped_uninstall(mode):
            for link in links: mode.unlink(*link)
        return mapped_install, mapped_uninstall
    
    # Syntactic sugar for one-line inclusion in modules.
    def triple(self):
        return self, self.install, self.uninstall

# Returns an object which may be yielded in an untwisted event handler to obtain
# just a list containing the given arguments, without any other effects.
def just(*args):
    def act(source, chain):
        try: chain.send(args)(source, chain)
        except StopIteration: pass
    return act

# Returns an object which may be yielded in an untwisted event handler to raise
# the given event in the given Mode instance. Compare: untwisted.mode.sign.
def msign(target, event, *args, **kwds):
    def act(source, chain):
        target.drive(event, *args, **kwds)
    return act
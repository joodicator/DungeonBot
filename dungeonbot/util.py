from types import MethodType as instancemethod
from types import ClassType as classobj
from collections import namedtuple
from itertools import *
from functools import *
import os.path
import inspect
import random
import sys
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
        return map(lambda t: head(*t), imap(eval, lines))

# Executes a file of Python statements, returning the resulting dictionary, in
# which any top-level classes have been changed to dicts.
def fdict(path):
    thedict = dict()
    execfile(path, thedict)
    return {k:cdict(v) for (k,v) in thedict.iteritems()
            if not k.startswith('_')}

# If the given object is a class, returns a copy of its dictionary with any
# __scored__ names removed, otherwise returns the same object unchanged.
def cdict(obj):
    if not isinstance(obj, (type, classobj)): return obj
    return {k:v for (k,v) in obj.__dict__.iteritems()
            if not k.startswith('_')}

# A LinkSet maintains a list of bindings between events and event handlers,
# providing some convenience methods for changing and using this list.
class LinkSet(object):
    __slots__ = 'links'
    
    def __init__(self):
        self.links = []
    
    # When called, a LinkSet produces a decorator that just adds given handler,
    # bound to the given event, to its list.
    # IMPORTANT: this decorator should be applied after any other decorators,
    # (i.e. it should be first in the list) so that the right function is bound.
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
        for link in self.links: mode.unlink(*link)
    
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
# just the given argument, with no other effects.
def just(arg):
    def act(source, chain):
        try: chain.send(arg)(source, chain)
        except StopIteration: pass
    return act

# Returns an object which may be yielded in an untwisted event handler to raise
# the given event in the given Mode instance. Compare: untwisted.mode.sign.
def msign(target, event, *args, **kwds):
    def act(source, chain):
        target.drive(event, *args, **kwds)
    return act

# Returns a decorator causing the return value of the decorated function to be
# passed to the given function, whose return value is finally returned.
def after(after):
    return partial(compose, after)

# Returns the functional composition of the two given functions.
def compose(after, before):
    return lambda *a, **k: after(before(*a, **k))

def deep_reload(mod, seen=None):
    if seen is None: seen = set()
    if not islocalmodule(mod): return
    if mod in seen: return
    seen.add(mod)
    for key, child in mod.__dict__.iteritems():
        if not inspect.ismodule(child):
            child = inspect.getmodule(child)
            if not child: continue
        elif hasattr(child, 'install'): continue
        deep_reload(child, seen)
    print '! reloading: %s' % mod
    reload(mod)

def islocalmodule(mod):
    if not hasattr(mod, '__file__'): return
    root = os.path.dirname(__file__)
    return os.path.commonprefix([mod.__file__, root]) == root

def dice(throws, sides):
    return sum(random.randint(1, sides) for n in xrange(throws))

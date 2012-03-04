import UserDict
import traceback

def apply(handle, *args, **kwargs):
    try:
        seq = handle(*args, **kwargs)
        return seq
    except StopPropagation:
        raise
    except:
        traceback.print_exc()

def chain(poll, seq):
    try:
        for ind in seq:
            ind(poll, seq)
    except StopIteration:
        pass

def mix(*args):
    total = dict()
    for ind in args:
        total.update(ind)
    return total

def glue(*args):
    total = tuple()
    for ind in args:
        total = total + ind
    return total

class sign(object):
    def __call__(self, mod, seq):
        mod.drive(self.event, *self.args, **self.kwargs)

    def __init__(self, event, *args, **kwargs):
        self.event = event
        self.args = args
        self.kwargs = kwargs
"""
class hold(object):
    def __call__(self, mod, seq):
        mod.link(self.event, self.layer) 
        self.mod = mod
        self.seq = seq
        raise StopIteration

    def __init__(self, event):
        self.event = event

    def layer(self, *args):
        try:
            self.seq.send(args)
        except StopIteration:
            pass

        self.mod.unlink(self.event, self.layer)

        return self.seq
"""

class hold(object):
    def __call__(self, mod, seq):
        self.mod = mod
        self.seq = seq
        self.obj.link(self.event, self.back) 
        raise StopIteration

    def __init__(self, obj, event):
        self.obj = obj
        self.event = event

    def back(self, *args):
        try:
            while True:
                point = self.seq.send(args)
                if isinstance(point, hold):
                    if not point is self:
                        point(self.mod, self.seq)
                    else:
                        break
                else:
                    point(self.mod, self.seq)
        except StopIteration:
                self.obj.unlink(self.event, self.back)
"""
class do(object):
    def __call__(self, mod, seq):
        chain(mod, self.obj)

    def __init__(self, obj, event=None):
        self.obj = obj
"""

def arg(*args, **kwargs):
    return (args, kwargs)

class Mode(object):
    def __init__(self, default=None):
        if default == None: default = lambda event, *args, **kwargs: None
        self.base = dict()
        self.default = default

    def drive(self, event, *args, **kwargs):
        #safe = self.base.copy()
        #keys = safe.keys()
        try:
            for signal, handle in self.base.keys():
                if signal == event:
                    old_args, old_kwargs = self.base[signal, handle] 
                    new_args = glue(args, old_args)
                    new_kwargs = mix(kwargs, old_kwargs)
                    seq = apply(handle, *new_args, **new_kwargs)
                    if seq:
                        apply(chain, self, seq)        
            #Generating the all event to spread event to children.
            self.default(event, *args, **kwargs)
        except StopPropagation:
            pass

    def link(self, event, callback, *args, **kwargs):
        self.base[event, callback] = arg(*args, **kwargs)

    def unlink(self, event, callback):
        del self.base[event, callback]


class StopPropagation(Exception):
    pass

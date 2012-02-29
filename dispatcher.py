import re

__all__ = 'Dispatcher'

class Dispatcher(object):
    __slots__ = 'hooks'

    def __init__(self):
        self.hooks = []

    def hook(self, call, patt, flags=0, block=True):
        self.hooks.append((re.compile(patt, flags), call, block))

    def __call__(self, data, *args):
        for rexp, call, block in self.hooks:
            match = rexp.match(data)
            if not match: continue
            call(*args, **match.groupdict())
            if block: break

class sign(object):
    def __call__(self, mod, seq):
        mod.drive(self.event, *self.args)

    def __init__(self, event, *args):
        self.event = event
        self.args = args

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
                elif isinstance(point, sign):
                    point(self.mod, self.seq)
        except StopIteration:
                self.obj.unlink(self.event, self.back)




from usual import *
from mode import *

class Dispatch(Mode):
    """
        This class works similarly to Mode except
        it drives events sequentially.

        Example:

        x = Mode()

        x.link('bar', alpha)
        x.link('bar', beta)
        x.link('bar', zeta)

        x.drive('bar')
        We would have alpha being called first than beta and 
        beta first than zeta.
        That behavior isn't warranted in the Mode root class instance.
    """

    def __init__(self, default=lambda event, *args: None):
        """ constructor """

        #since we aim a order 
        #we just use lists
        self.base      = list()
        self.base_args = list()

        #the default handle which is
        #called whenever an event is driven
        self.default = default

    def drive(self, event, *args):
        """ This function drives event through the callbacks """
        for signal, handle in self.base:
            #match to find the right handle
            if signal == event:
                #if some of the callbacks processed
                #has removed some of the events
                #then we dont have our chain of events
                #broken
                try:
                    ind = self.base.index((signal, handle))
                except ValueError:
                    continue

                #get the args which we mean 
                #to pass to our functions
                old_args = self.base_args[ind] 

                #args is passed first 
                new_args = glue(args, old_args)

                #calls the handle with new_args
                #if it occurs an exception
                #apply doesn't let it pass
                seq = apply(handle, *new_args)
                if seq:
                    #if handle has hold/sign
                    #interface-events we just chain it
                    apply(chain, self, seq)        

        #Generating the all event to spread event to children.
        self.default(event, *args)

    def link(self, event, callback, *args):
        """ This function maps an event to a callback """
        self.base.append((event, callback))
        self.base_args.append(args)

    def unlink(self, event, callback):
        """ It unmpas events """
        ind = self.base.index((event, callback))
        del self.base[ind]
        del self.base_args[ind]


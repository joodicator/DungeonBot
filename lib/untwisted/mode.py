from usual import *

class Mode(object):
    """
        This class is a context for a socket.
        It works so:

        x = Mode()

        def callback(data):
            pass

        x.link(event, callback)
    
        x.drive(event, 'foo')
        
        We will have callback function being called with 'foo'
        as argument.

        Inside callback we can have sequences of yield.
        The values yielded are classes from usual.
        These classes are meant to generate events
        and block the code prossesment until a given event
        is driven.

        def drive_event():
            yield sign('bar', 'apple')

        def bar_handle(data):
            pass

        x.link('root', drive_event)
        
        x.link('bar', bar_handle)

        x.drive('root')

        We will have bar_handle being called with 'apple'
        as argument.
        drive_event is called when 'root' is driven.
        Consequently drive_event generates 'bar' event with 'apple' as argment.
        Since we linked 'bar' to bar_handle we have bar_handle called in a
        hierarchical way.
    """

    def __init__(self, default=lambda event, *args: None):
        """ 
            Constructor for Mode 
        """
        #the dict which contains the mappings
        #for the events
        self.base = dict()
        self.default = default

    def drive(self, event, *args):
        for signal, handle in self.base.keys():
            #if signal is equal to event
            #then obtain the event handle
            #to spread it
            if signal == event:
                try:
                    #if the event was unlinked
                    #in the previous callbacks
                    #it just throws an exception
                    #then continues
                    old_args = self.base[signal, handle] 
                except KeyError:
                    continue

                #glue the class's user argument 
                #to the event argument
                #the event argument is that when sign
                #is called with parameters
                new_args = glue(args, old_args)

                #so, call handle with all arguments
                seq = apply(handle, *new_args)

                #handle must return a sequence
                #of iterators or None
                #if it is a sequence then we must
                #chain it in order to execute the
                #remaining code which is dependent
                #of the events defined in the sequence
                #returned by handle
                if seq:
                    apply(chain, self, seq)        

        #spread the event through the children
        self.default(event, *args)

    def link(self, event, callback, *args):
        """ 
            This function maps an event to a callback 
            event might be whatever kind of data.
            The argument args is given to callback
            when the event is fired.
        """

        #Map (event, callback) to the args
        self.base[event, callback] = args

    def unlink(self, event, callback):
        """ 
            This function unmap an event to a callback 
        """

        del self.base[event, callback]



event_count = 0

def get_event():
    global event_count

    event_count = event_count + 1
    return event_count

READ   = get_event()
WRITE  = get_event()
EXC    = get_event()
CLOSE  = get_event()
ACCEPT = get_event()
FOUND  = get_event()
DATA   = get_event()
LOAD   = get_event()
DATA   = get_event()
BUFFER = get_event()
LOCAL  = get_event()
RECV   = get_event()
DUMPED = get_event()

_all__ = [
            'get_event',
            'READ', 
            'WRITE',
            'EXC', 
            'FOUND',
            'LOAD', 
            'BUFFER', 
            'sign',
            'CLOSE',
            'ACCEPT',
          ]



from abc import ABC

class Message(ABC):
    def __init__(self, src=None, payload=None, dest=None, stamp=None):
        self.src = src
        self.payload = payload
        self.dest = dest
        self.stamp = stamp

class Broadcast(Message):
    def __init__(self, src=None, payload=None, dest=None, stamp=None):
        super().__init__(src, payload, dest, stamp)

class SendTo(Message):
    def __init__(self, src=None, payload=None, dest=None, stamp=None):
        super().__init__(src, payload, dest, stamp)

class Token:
    def __init__(self, dest):
        super().__init__(dest)
        self.dest = dest
    
    def getHolder(self):
        return self.dest
    
    def setHolder(self, dest):
        self.dest = dest

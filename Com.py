import threading
from time import sleep
from pyeventbus3.pyeventbus3 import *

from Message import *

class Com(Thread):
    def __init__(self, process, nbProcess):
        Thread.__init__(self)
        self.clock = 0
        self.semaphore = threading.Semaphore()
        self.mailbox = []
        self.process = process
        self.nbProcess = nbProcess
        self.myId = process.getName()
        waiting = False

        # Inscription au bus d'événements
        PyBus.Instance().register(self, self)

    def inc_clock(self):
        with self.semaphore:
            self.clock += 1
            return self.clock

    def get_clock(self):
        return self.clock

    def broadcast(self, msg):
        self.inc_clock()
        message = Broadcast(self.myId, msg, None, self.get_clock())
        PyBus.Instance().post(message)
        print(self.myId + " broadcast: " + msg)

    @subscribe(threadMode=Mode.PARALLEL, onEvent=Broadcast)
    def recev(self, message):
        if message.src != self.process.getName():
            self.inc_clock()
            self.mailbox.append(message)
            print(self.myId + " received: " + message.payload)

    def sendTo(self, msg, dest):
        self.inc_clock()
        message = SendTo(self.myId, msg, dest, self.get_clock)

        PyBus.Instance().post(message)
        print(self.myId + " send ", msg, "to", dest)

    @subscribe(threadMode=Mode.PARALLEL, onEvent=SendTo)
    def recev(self, message):
        if message.dest == self.myId:
            self.inc_clock()
            self.mailbox.append(message)
            print(self.myId + " received: " + message.payload, "from", message.src)


    def RequestSC(self):
        pass

    def nextHolder(self):
        #calcule le prochain holder du token
        pass

    @subscribe(threadMode=Mode.PARALLEL, onEvent=Token)
    def recev(self, message):
        if waiting:
            self.inc_clock()
            self.mailbox.append(message)
            print(self.myId + " received: " + message.payload, "from", message.src)
            waiting = False
            self.semaphore.release()
        else:
            self.inc_clock()
            self.mailbox.append(message)
            



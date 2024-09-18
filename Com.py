from Message import *
import threading

from pyeventbus3.pyeventbus3 import *

class Com():
    def __init__(self):
        self.nbProcess = 3
        self.myId = 0
        self.lamportClock = 0
        self.semaphore = threading.Semaphore()
        self.mailbox = []

    def setlamportClock(self,lamportClock):
        self.lamportClock = lamportClock

    def getNbProcess(self):
        return self.nbProcess
    
    def getMyId(self): 
        return self.myId

    def getlamportClock(self):
        return self.lamportClock
    
    def incrementLamportClock(self):
        with self.semaphore:
            self.lamportClock += 1
        return self.lamportClock
    
    def Broadcast(self, payload):
        self.incrementLamportClock()
        return BroadcastMessage(self.lamportClock, payload, self.myId)
    
    def sendTo(self, payload, receiver):
        self.incrementLamportClock()
        print("Envoi de message à "+str(receiver))
        return Message(self.lamportClock, payload)
    
    def broadcast(self, payload):
        self.mailbox.append(self.Broadcast(payload))
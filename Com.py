from Message import *
import threading

class Com():
    def __init__(self):
        self.nbProcess = 3
        self.myId = 0
        self.lamportClock = 0
        self.semaphore = threading.Semaphore()


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
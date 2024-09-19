import threading
from time import sleep
from pyeventbus3.pyeventbus3 import *
from Message import Message, BroadcastMessage


class Com(Thread):
    def __init__(self, process):
        self.clock = 0 
        self.semaphore = threading.Semaphore() # Semaphore pour la gestion des accès concurrents à l'horloge
        self.mailbox = [] 
        self.owner = process.name # Le processus qui utilise cette instance de Com
        self.process = process 

        PyBus.Instance().register(self, self)

    def inc_clock(self):
        with self.semaphore:
            self.clock += 1
            return self.clock
        
    def get_clock(self):
        return self.clock
    
    def getFirstMessage(self) -> Message:
        return self.mailbox.pop(0)

    def __addMessageToMailbox(self, msg: Message):
        self.mailbox.append(msg)

    def broadcast(self, payload: object):
        """
        Envoie un message à tous les autres processus via le bus d'événements
        """
        self.inc_clock()

        message = BroadcastMessage(src=self.owner, payload=payload, stamp=self.clock)

        print(f"Process {self.owner} envoie un message broadcasté : {message.payload}")
        PyBus.Instance().post(message)

    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, event):
        """
        Lire un message broadcasté sur le bus
        """
        if event.src != self.owner:
            sleep(1)
            if self.clock > event.stamp:
                self.inc_clock()
            else:
                self.clock = event.stamp

            self.__addMessageToMailbox(event)
            
            print(f"Process {self.owner} a reçu un message broadcasté : {event.payload}")
            sleep(1)

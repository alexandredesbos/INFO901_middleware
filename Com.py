import threading
from time import sleep
from pyeventbus3.pyeventbus3 import *

from Message import *

class Com(Thread):
    def __init__(self, process, has_token=False):
        Thread.__init__(self)
        self.clock = 0
        self.semaphore = threading.Semaphore()
        self.mailbox = []
        self.process = process
        self.owner = process.name
        self.cptSync = 0

        self.nbProcess = process.nbProcess

        self.local_counter = 0
        self.assigned_ids = []

        # Gestion du Token
        self.token = Token(self.owner) if has_token else None 
        self.process.state = State.NONE

        PyBus.Instance().register(self, self)

    def inc_clock(self):
        with self.semaphore:
            self.clock += 1
            return self.clock
        
    def get_clock(self):
        return self.clock
    
    def getFirstMessage(self) -> Message:
        return self.mailbox.pop(0)

    def addMessageToMailbox(self, msg: Message):
        self.mailbox.append(msg)

    def isMailboxEmpty(self):
        return len(self.mailbox) == 0


    def broadcast(self, payload: object):
        """
        Envoie un message broadcasté à tous les processus
        Args:
            payload (object): Le contenu du message
        """
        
        self.inc_clock()
        message = BroadcastMessage(src=self.owner, payload=payload, stamp=self.clock)

        print(f"Process {self.owner} envoie un message broadcasté : {message.payload}")
        PyBus.Instance().post(message)

    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, event):
        """
        Recoit un message broadcasté
        Args:
            event (BroadcastMessage): Le message broadcasté
        """
    
        if event.src != self.owner:
            sleep(1)
            if self.clock > event.stamp:
                self.inc_clock()
            else:
                self.clock = event.stamp

            self.addMessageToMailbox(event)
            
            print(f"Process {self.owner} a reçu un message broadcasté : {self.getFirstMessage().payload}")
            sleep(1)


    def sendTo(self, payload, to):
        """
        Envoie un message à un processus
        Args:
            payload (object): Le contenu du message
            to (str): Le destinataire
        """
        self.inc_clock()
        messageTo = MessageTo(self.clock, payload, self.owner, to) 

        print(f"Process {self.owner} envoie un message à {to} : {messageTo.payload} "
              f"avec timestamp {messageTo.stamp} de {messageTo.src}")

        PyBus.Instance().post(messageTo)

    @subscribe(threadMode=Mode.PARALLEL, onEvent=MessageTo)
    def onMessageTo(self, event):
        """
        Recoit un message
        Args:
            event (MessageTo): Le message reçu
        """
        if event.getReceiver() == self.owner:
            if self.clock > event.stamp:
                self.inc_clock()
            else:
                self.clock = event.stamp
            self.addMessageToMailbox(event)


    # Gestion du jeton
    def requestSC(self):
        """
        Demande d'entrer en section critique
        args:
            token (Token): Le jeton
        """
        self.process.state = State.REQUEST
        print(f"{self.owner} veut entrer en SC.")

        while self.process.state != State.SC:
            sleep(1)


    def releaseSC(self):
        """
        Libère la section critique
        """
        self.process.state = State.RELEASE
        print(f"{self.owner} libère le jeton.")

    def sendTokenTo(self, token: Token):
    
        PyBus.Instance().post(token)
        print(f"{self.owner} a envoyé le jeton a {token.dest}.")

    @subscribe(threadMode=Mode.PARALLEL, onEvent=Token)
    def on_token(self, event):
        """
        Recoit le jeton
        Args:
            event (Token): Le jeton
        """
        if self.owner == event.dest and self.process.alive:
            sleep(1)
            print(f"{self.owner} a le jeton.")
            if self.process.state == State.REQUEST:
                self.process.state = State.SC
                print(f"{self.owner} entre en SC.")
                
                while self.process.state != State.RELEASE:
                    sleep(1)
                    print(f"{self.owner} est en SC.")
                print(f"{self.owner} quitte la SC.")


            numberOwner = int(self.owner[1:])
            
            # Calcul du prochain processus
            nextProcessNumber = (numberOwner + 1) % self.process.nbProcess
            
            nextProcess = "P" + str(nextProcessNumber)
            self.sendTokenTo(Token(nextProcess))
            self.process.state = State.NONE


    #« synchronize() » qui attend que tous les processus aient invoqué cette méthode pour tous les débloquer.
    def synchronize(self):
        """
        Synchronise les processus
        args:
            nbProcess (int): Le nombre de processus
        """
        messageSync = SyncMessage(self.owner, self.clock)

        print(f"{self.owner} En attente de synchronisation.")
        PyBus.Instance().post(messageSync)

        while self.cptSync < self.nbProcess - 1:
            sleep(1)

        # reset cptSync
        print(f"{self.owner} est synchronisé.")
        self.cptSync = 0


    @subscribe(threadMode=Mode.PARALLEL, onEvent=SyncMessage)
    def on_sync(self, event):
        if event.src != self.owner:
            sleep(1)
            self.cptSync += 1

    def broadcastSync(self, payload: object, from_id: str):
        """
        Envoie un message broadcasté synchronisé
        Args:
            payload (object): Le contenu du message
            from_id (str): L'identifiant du processus qui envoie le message
        """
        self.inc_clock()
        if self.owner == from_id:
            message = BroadcastMessage(src=self.owner, payload=payload, stamp=self.clock)
            print(f"Process {self.owner} envoie un message broadcasté synchronisé : {message.payload}")
            PyBus.Instance().post(message)


        else:
            while self.isMailboxEmpty():
                sleep(1)
            msg = self.getFirstMessage()
            if isinstance(msg, BroadcastMessage) and msg.src == from_id:
                print(f"Process {self.owner} a reçu un message broadcasté synchronisé : {msg.payload}")
                self.cptSync += 1

    def sendToSync(self, payload: object, dest: str):
        """
        Envoie un message synchronisé
        Args:
            payload (object): Le contenu du message
            dest (str): Le destinataire
        """
        self.inc_clock()
        message = MessageTo(self.clock, payload, self.owner, dest)
        print(f"Process {self.owner} envoie un message synchronisé à {dest}: {message.payload}")
        PyBus.Instance().post(message)


    def receiveFromSync(self, from_id: str):
        """
        Recoit un message synchronisé
        Args:
            from_id (str): L'identifiant du processus qui envoie le message
        """
        print(f"Process {self.owner} attend un message de {from_id}...")
        while self.isMailboxEmpty():
            sleep(0.1)

        msg = self.getFirstMessage()
        if isinstance(msg, MessageTo) and msg.src == from_id:
            print(f"Process {self.owner} a reçu un message synchronisé de {from_id}: {msg.payload}")


    def assign_unique_id(self):
        assigned_id = self.local_counter
        self.local_counter += 1
        self.assigned_ids.append(assigned_id)
        return assigned_id


    
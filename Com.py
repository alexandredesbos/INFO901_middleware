import threading
from time import sleep
from pyeventbus3.pyeventbus3 import *
from Message import Message, BroadcastMessage, MessageTo, Token
class Com(Thread):
    def __init__(self, process, has_Token=False):
        Thread.__init__(self)

        self.clock = 0
        self.semaphore = threading.Semaphore()
        self.mailbox = []
        self.process = process
        self.owner = process.name
        self.waiting_for_token = False
        self.token_condition = threading.Condition() 
        self.token = Token(holder_id=self.owner) if has_Token else Token(holder_id=None)


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

    # Envoie un message à tous les autres processus via le bus d'événements
    def broadcast(self, payload: object):
        
        self.inc_clock()

        message = BroadcastMessage(src=self.owner, payload=payload, stamp=self.clock)

        print(f"Process {self.owner} envoie un message broadcasté : {message.payload}")
        PyBus.Instance().post(message)

    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, event):
    
        # Si le message n'a pas été envoyé par ce processus
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
        self.inc_clock()
        messageTo = MessageTo(self.clock, payload, self.owner, to)

        print(f"Process {self.owner} envoie un message à {to} : {messageTo.payload} "
              f"avec timestamp {messageTo.stamp} de {messageTo.src}")

    
        PyBus.Instance().post(messageTo)

    # Méthode appelée lors de la réception d'un message dédié
    @subscribe(threadMode=Mode.PARALLEL, onEvent=MessageTo)
    def onMessageTo(self, event):
        if event.getReceiver() == self.owner:
            if self.clock > event.stamp:
                self.inc_clock()
            else:
                self.clock = event.stamp
            self.addMessageToMailbox(event)


    def requestSC(self):
        """
        Demande l'accès à la section critique. Bloque jusqu'à l'obtention du jeton.
        """
        with self.token_condition:
            self.waiting_for_token = True
            print(f"{self.owner} demande la section critique.")

            while self.token.getHolder() != self.owner:
                self.token_condition.wait()
            print(f"{self.owner} a obtenu la section critique.")

    def releaseSC(self):
        """
        Libère la section critique et passe le jeton au prochain processus dans l'anneau.
        """
        with self.token_condition:
            print(f"{self.owner} libère la section critique et passe le jeton.")
            self.token.setHolder(self.get_next_process()) 
            self.token_condition.notify_all()

            token_message = Token(token=self.token)
            PyBus.Instance().post(token_message)

    def get_next_process(self):
        """
        Détermine le processus suivant dans l'anneau.
        À implémenter selon la logique de l'anneau.
        """

        process_list = ["P0", "P1", "P2"]
        current_index = process_list.index(self.owner)
        next_index = (current_index + 1) % len(process_list)
        return process_list[next_index]

    @subscribe(threadMode=Mode.PARALLEL, onEvent=Token)
    def onTokenMessage(self, event):
        """
        Réception d'un message contenant le jeton.
        """
        if event.token.getHolder() == self.owner:
            with self.token_condition:
                self.token = event.token
                print(f"{self.owner} a reçu le jeton.")
                self.token_condition.notify_all()

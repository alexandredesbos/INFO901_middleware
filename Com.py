import threading
from time import sleep
from pyeventbus3.pyeventbus3 import *
from Message import Message, BroadcastMessage, MessageTo, Token

class Com(Thread):
    def __init__(self, process):
        Thread.__init__(self)
        self.clock = 0
        self.semaphore = threading.Semaphore()
        self.mailbox = []
        self.process = process
        self.owner = process.name
        self.token = None  # Initialise sans jeton
        self.has_token = False  # Indique si le processus possède le jeton
        self.requesting_sc = False
        self.request_queue = []  # File d'attente des demandes de SC
        self.lock = threading.Lock()  # Pour protéger l'accès aux ressources critiques
        self.token_thread = threading.Thread(target=self.token_manager)
        self.token_thread.start()


        # Inscription au bus d'événements
        PyBus.Instance().register(self, self)

    def inc_clock(self):
        with self.semaphore:
            self.clock += 1
            return self.clock

    def get_clock(self):
        return self.clock

    def getFirstMessage(self) -> Message:
        if self.mailbox:
            return self.mailbox.pop(0)
        else:
            return None

    def addMessageToMailbox(self, msg: Message):
        with self.semaphore:
            self.mailbox.append(msg)
        
    def isMailboxEmpty(self):
        return len(self.mailbox) == 0

    def broadcast(self, payload: object):
        self.inc_clock()
        message = BroadcastMessage(src=self.owner, payload=payload, stamp=self.clock)
        print(f"Process {self.owner} envoie un message broadcasté : {message.payload}")
        PyBus.Instance().post(message)

    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, event):
        if event.src != self.owner:
            sleep(1)
            with self.semaphore:
                if self.clock > event.stamp:
                    self.inc_clock()
                else:
                    self.clock = event.stamp
            self.addMessageToMailbox(event)
            print(f"Process {self.owner} a reçu un message broadcasté : {self.getFirstMessage().payload}")
            sleep(1)

    def sendTo(self, payload, to):
        self.inc_clock()
        messageTo = MessageTo(src=self.owner, dest=to, payload=payload, stamp=self.clock)
        print(f"Process {self.owner} envoie un message à {to} : {messageTo.payload}")
        PyBus.Instance().post(messageTo)

    @subscribe(threadMode=Mode.PARALLEL, onEvent=MessageTo)
    def onMessageTo(self, event):
        if event.dest == self.owner:
            sleep(1)
            with self.semaphore:
                if self.clock > event.stamp:
                    self.inc_clock()
                else:
                    self.clock = event.stamp
            self.addMessageToMailbox(event)
            print(f"Process {self.owner} a reçu un message de {event.src} : {self.getFirstMessage().payload}")
            sleep(1)


    def requestSC(self):
        """Méthode pour demander la section critique."""
        self.lock.acquire()
        self.requesting_sc = True
        if self.has_token:
            # Si on possède le jeton, on peut entrer directement en section critique
            self.enter_critical_section()
        else:
            # Sinon, on envoie une demande de SC
            self.send_request_for_token()
        self.lock.release()

    def releaseSC(self):
        """Méthode pour libérer la section critique."""
        self.lock.acquire()
        self.requesting_sc = False
        if self.has_token:
            self.pass_token_to_next()
        self.lock.release()

    def enter_critical_section(self):
        """Entrer en section critique."""
        print(f"Process {self.owner} est dans la section critique.")
        # Simuler la section critique
        time.sleep(2)  # Simuler du travail
        print(f"Process {self.owner} quitte la section critique.")
        self.releaseSC()

    def send_request_for_token(self):
        """Envoyer une demande pour obtenir le jeton."""
        print(f"Process {self.owner} demande le jeton.")
        # Ajoute la demande à la file d'attente
        self.request_queue.append(self.owner)
        # Ici, tu devras envoyer un message aux autres processus pour demander le jeton

    def pass_token_to_next(self):
        """Passer le jeton au prochain processus qui le demande."""
        if self.request_queue:
            next_process = self.request_queue.pop(0)
            print(f"Process {self.owner} passe le jeton au Process {next_process}.")
            self.has_token = False
            # Envoie le jeton au processus suivant
            self.send_token_to_process(next_process)

    def send_token_to_process(self, owner):
        """Méthode pour envoyer le jeton à un autre processus."""
        token_message = Token(sender=self.owner, receiver=owner)
        # Ici, il faut envoyer le message via les mécanismes de communication du middleware
        print(f"Envoi du jeton à Process {owner}")

    def token_manager(self):
        """Thread pour gérer la réception du jeton."""
        while True:
            # Ici, on attend de recevoir le jeton
            # Simuler la réception d'un jeton
            time.sleep(5)  # Simuler une attente
            self.has_token = True  # Pour l'exemple, on simule la réception du jeton
            if self.requesting_sc:
                self.enter_critical_section()
class Message:
    def __init__(self, timestamp, payload):
        self.timestamp = timestamp  # Horloge de Lamport
        self.payload = payload      # Contenu du message (payload)

    def getTimestamp(self):
        return self.timestamp

    def getPayload(self):
        return self.payload

class BroadcastMessage(Message):
    def __init__(self, timestamp, payload, sender):
        super().__init__(timestamp, payload)
        self.sender = sender

    def getSender(self):
        return self.sender

class MessageTo(Message):
    def __init__(self, timestamp, payload, sender, receiver):
        super().__init__(timestamp, payload)
        self.sender = sender
        self.receiver = receiver

    def getSender(self):
        return self.sender
    def getReceiver(self):
        return self.receiver
    
    
class Token:
    def __init__(self, holder_id):
        self.holder_id = holder_id

    def getHolder(self):
        return self.holder_id

    def setHolder(self, holder_id):
        self.holder_id = holder_id

from threading import Lock, Thread

from time import sleep

from Com import Com
from Message import Token

class Process(Thread):
    
    def __init__(self, name, nbProcess):
        Thread.__init__(self)

        self.nbProcess = nbProcess
        self.name = name
        self.com = Com(self)
        self.setName(name)

        self.alive = True
        self.start()
    

    def run(self):
        loop = 0
        while self.alive:
            print(self.getName() + " Loop: " + str(loop))
            sleep(1)
        
            # Lance le token a l'initialisation
            # if loop == 0 and self.name == "P0":
            #     t = Token("P1")
            #     self.com.sendTokenTo(t)

            # if loop == 2 and self.name == "P1":
            #     self.com.requestSC()
            #     self.com.releaseSC()

            # if loop == 2 and self.name == "P2":
            #     self.com.requestSC()
            #     self.com.releaseSC()

            # if loop == 2 and self.name == "P1":
            #     self.com.synchronize()

            # if loop == 4 and self.name == "P2":
            #     self.com.synchronize()

            # if loop == 3 and self.name == "P0":
            #     self.com.synchronize()

            if loop == 1 and self.name == "P0":
                payload = f"Message synchronisé de {self.name}"
                self.com.broadcastSync(payload, from_id="P0")

            loop+=1
        print(self.getName() + " stopped")

    def stop(self):
        self.alive = False
        self.join()

    def waitStopped(self):
        self.join()
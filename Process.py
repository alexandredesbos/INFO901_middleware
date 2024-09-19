from threading import Lock, Thread

from time import sleep
import time

from Com import Com

class Process(Thread):
    
    def __init__(self,name, nbProcess):
        Thread.__init__(self)

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
            
            if loop == 2 and self.name == "P0":
                self.com.sendTo("Hello","P1")

            if loop == 4 and self.name == "P1":
                if len(self.com.mailbox) > 0:
                    print(f"Message reçu par {self.name} : {self.com.getFirstMessage().payload}")


            if self.getName() == "P0":
                    
                self.com.requestSC()
                if self.com.isMailboxEmpty():
                    print("Catched !")
                    self.com.broadcast("J'ai gagné !!!")
                else:
                    print("J'ai pas eu le jeton")
                    msg = self.com.getFirstMessage()
                    print(str(msg.getSender())+" à eu le jeton en premier")
                self.com.releaseSC()

            loop+=1
        print(self.getName() + " stopped")

    def stop(self):
        self.alive = False
        self.join()

    def waitStopped(self):
        self.join()
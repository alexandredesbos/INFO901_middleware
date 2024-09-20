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
            if loop == 0 and self.name == "P0":
                t = Token("P1")
                self.com.sendTokenTo(t)

            if loop == 2 and self.name == "P1":
                self.com.requestSC()
                self.com.releaseSC()

            if loop == 2 and self.name == "P2":
                self.com.requestSC()
                self.com.releaseSC()


            # if self.getName() == "P0":
            #     self.com.sendTo("j'appelle 2 et je te recontacte après", 1)
                
            #     self.com.sendToSync("J'ai laissé un message à 2, je le rappellerai après, on se sychronise tous et on attaque la partie ?", 2)
            #     self.com.recevFromSync(msg, 2)
               
            #     self.com.sendToSync("2 est OK pour jouer, on se synchronise et c'est parti!",1)
                    
            #     self.com.synchronize()
                    
            #     self.com.requestSC()
            #     if self.com.mailbox.isEmpty():
            #         print("Catched !")
            #         self.com.broadcast("J'ai gagné !!!")
            #     else:
            #         msg = self.com.mailbox.getMsg()
            #         print(str(msg.getSender())+" à eu le jeton en premier")
            #     self.com.releaseSC()


            # if self.getName() == "P1":
            #     if not self.com.mailbox.isEmpty():
            #         self.com.mailbox.getMessage()
            #         self.com.recevFromSync(msg, 0)

            #         self.com.synchronize()
                    
            #         self.com.requestSC()
            #         if self.com.mailbox.isEmpty():
            #             print("Catched !")
            #             self.com.broadcast("J'ai gagné !!!")
            #         else:
            #             msg = self.com.mailbox.getMsg()
            #             print(str(msg.getSender())+" à eu le jeton en premier")
            #         self.com.releaseSC()
                    
            # if self.getName() == "P2":
            #     self.com.recevFromSync(msg, 0)
            #     self.com.sendToSync("OK", 0)

            #     self.com.synchronize()
                    
            #     self.com.requestSC()
            #     if self.com.mailbox.isEmpty():
            #         print("Catched !")
            #         self.com.broadcast("J'ai gagné !!!")
            #     else:
            #         msg = self.com.mailbox.getMsg()
            #         print(str(msg.getSender())+" à eu le jeton en premier")
            #     self.com.releaseSC()
                

            loop+=1
        print(self.getName() + " stopped")

    def stop(self):
        self.alive = False
        self.join()

    def waitStopped(self):
        self.join()
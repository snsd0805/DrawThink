import socket,threading,sys

MAX = 1024

class Server:
    def __init__(self,ip,port):
        self.ip = ip
        self.port = port
    def start(self):
        print("Set server on {}:{}".format(self.ip,self.port))
        listensock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        listensock.bind((self.ip,self.port))
        listensock.listen(5)
        while True:
            sock,sockname = listensock.accept()
            print("{} has connected.".format(sockname))
            setTypeThread = threading.Thread(target = self.selectType,args=(sock,))
            setTypeThread.start()            

    def selectType(self,sock):
        print("SelectType() function started")
        data = sock.recv(MAX).decode('utf-8')

        print(data)
        if data == "MAIN":
            sock.send("OK.SERVER".encode('utf-8'))
        elif data == "CLIENT":
            sock.send("OK.CLIENT".encode('utf-8'))
        else:
            sock.send("FAIL".encode('utf-8'))
        
        print("SelectType() function closed")

class Client:
    def __init__(self,ip,port):
        self.ip = ip
        self.port = port

    def start(self):
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect((self.ip,self.port))
        self.setType(sock)

    def setType(self,sock):
        print("Type in 'MAIN' to set a new room\nType in 'CLIENT' to join a room")
        msg = input("> ")
        sock.send(msg.encode('utf-8'))
        receiveMsg = sock.recv(MAX).decode('utf-8')
        print(receiveMsg)

def main():
    ip = sys.argv[2]
    port = sys.argv[3]
    port = int(port)
    print(ip,port)
    if(sys.argv[1]=='server'):
        server = Server(ip,port)
        server.start()
    elif(sys.argv[1]=='client'):
        client = Client(ip,port)
        client.start()
    else:
        print("Usage: python main.py {server,client} ip port")

main()
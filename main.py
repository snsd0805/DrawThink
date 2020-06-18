import socket,threading,sys,random,multiprocessing,time

MAX = 1024

class Server:
    roomList = []
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
        data = sock.recv(MAX).decode('utf-8')

        print(data)
        if data == "MAIN":
            sock.send("OK.SERVER".encode('utf-8'))
            self.main(sock)
        elif data == "CLIENT":
            sock.send("OK.CLIENT".encode('utf-8'))
        else:
            sock.send("FAIL".encode('utf-8'))
        
    def main(self,sock):            
        portNum = random.randint(1025,65535)    #決定port
        roomNum = chr(random.randint(65,90)) + chr(random.randint(65,90))

        flag = 1
        while flag:
            portNum = random.randint(1025,65535)    #決定port
            roomNum = chr(random.randint(65,90)) + chr(random.randint(65,90))
            flag = 0
            for i in self.roomList:
                if i['portNum'] == portNum or i['roomNum'] == roomNum:
                    flag =1
        room = Room(self.ip,portNum)
        roomProcess = multiprocessing.Process(target=room.start)
        roomProcess.start()
        self.roomList.append(
            {
                'portNum' : portNum,
                'roomNum' : roomNum,
            }
        )
        print(self.roomList)
        sock.send("{} {}".format(roomNum,portNum).encode('utf-8'))
    # def getPort(self):
    #     sock
class Room:
    startFlag = False
    def __init__(self,ip,portNum):
        self.ip = ip
        self.portNum = portNum
    def start(self):
        listensock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        listensock.bind((self.ip,self.portNum))
        print("\t{}:{}".format(self.ip,self.portNum))
        listensock.listen(5)
        while True:
            sock,sockname = listensock.accept()
            print("[ {} ]{} has connected.".format(self.portNum,sockname))
            sock.send('WELCOME'.encode('utf-8'))
    def connect(self):
        time.sleep(0.5)
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect((self.ip,self.portNum))
        print(sock.recv(MAX).decode('utf-8'))

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
        if receiveMsg=="OK.SERVER":
            receiveMsg = sock.recv(MAX).decode('utf-8')
            print(receiveMsg)
            connectData = receiveMsg.split(' ')
            room = Room(self.ip,int(connectData[1]))
            room.connect()
        elif receiveMsg=="OK.CLIENT":
            print("CLIENT")
        else:
            print("ERROR TYPE")

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
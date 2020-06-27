import socket,threading,sys,random,multiprocessing,time
import draw
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
            setTypeThread = threading.Thread(target = self.selectType,args=(sock,)) # Create a thread for communicating with client.
            setTypeThread.start()

    def selectType(self,sock):
        data = sock.recv(MAX).decode('utf-8')

        print(data)
        if data == "MAIN":
            sock.send("OK.SERVER".encode('utf-8'))
            self.main(sock)
        elif data == "CLIENT":
            sock.send("OK.CLIENT".encode('utf-8'))
            self.client(sock)
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
    def client(self,sock):
        receiveMsg = sock.recv(MAX).decode('utf-8')
        flag = False
        for i in self.roomList:
            if i['roomNum'] == receiveMsg:
                sock.send(str(i['portNum']).encode('utf-8'))
                flag = True
        if not flag:
            sock.send("FAIL".encode('utf-8'))
        
class Room:
    startFlag = False
    sockList = []
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

            self.sockList.append(sock)      # 把sock放入list
            
            receiveDataThread = threading.Thread(target=self.receiveData,args=(sock,))
            receiveDataThread.start()

    def connect(self):
        time.sleep(0.5)
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect((self.ip,self.portNum))
        return sock
    def receiveData(self,sock):
        while True:
            origin = sock.recv(MAX)
            data = origin.decode('utf-8')
            if data:
                print(data)
                for clientSock in self.sockList:    # 遍歷socket list
                    if clientSock != sock:          # 不是自己的才傳送資料
                        clientSock.send(origin) 

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
            sock = room.connect()       # sock可覆蓋了

            # receiveDataThread = threading.Thread(target=self.receiveData,args=(sock,))
            # receiveDataThread.start()
            # sendDataThread = threading.Thread(target=self.sendData,args=(sock,))
            # sendDataThread.start()
            draw.sendDraw(sock,)

        elif receiveMsg=="OK.CLIENT":
            roomNum = input("Room Number> ")
            sock.send(roomNum.encode('utf-8'))
            receiveMsg = sock.recv(MAX).decode('utf-8')
            room = Room(self.ip,int(receiveMsg))
            sock = room.connect()       # sock可覆蓋了
            
            # receiveDataThread = threading.Thread(target=self.receiveData,args=(sock,))
            # receiveDataThread.start()
            # sendDataThread = threading.Thread(target=self.sendData,args=(sock,))
            # sendDataThread.start()
            draw.receiveDraw(sock)
        else:
            print("ERROR TYPE")

    def receiveData(self,sock):
        while True:
            data = sock.recv(MAX).decode('utf-8')
            if data:
                print(data)
    def sendData(self,sock):
        while True:
            data = input("> ")
            sock.send(data.encode('utf-8'))
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
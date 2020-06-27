import socket,threading,sys,random,multiprocessing,time
import draw
MAX = 1024

class Server:
    roomList = []
    def __init__(self,ip,port):
        self.ip = ip
        self.port = port
    def start(self):

        # Base server
        # Set the room for mainClient and redirect client into the room
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
            self.main(sock) # Set main client mode
        elif data == "CLIENT":
            sock.send("OK.CLIENT".encode('utf-8'))
            self.client(sock)   # Set client mode
        else:
            sock.send("FAIL".encode('utf-8'))   # Error type
        
    def main(self,sock):            
        portNum = random.randint(1025,65535)    #決定port
        roomNum = chr(random.randint(65,90)) + chr(random.randint(65,90))   # 隨機房號，給client方便導向，不需要ip:port

        flag = 1

        # 防止房號相同，若重複必須重新設定
        while flag:
            portNum = random.randint(1025,65535)    #決定port
            roomNum = chr(random.randint(65,90)) + chr(random.randint(65,90))
            flag = 0
            for i in self.roomList:
                if i['portNum'] == portNum or i['roomNum'] == roomNum:
                    flag =1
        

        room = Room(self.ip,portNum)
        # Room process, process the game.
        # Should handle all client which are redirected to this room.
        roomProcess = multiprocessing.Process(target=room.start)
        roomProcess.start()

        # Set a list which save all rooms' info
        self.roomList.append(
            {
                'portNum' : portNum,
                'roomNum' : roomNum,
            }
        )
        print(self.roomList)

        # Let main client know the roomNumber.So it can connect to this room and share it's roomNumber to his/her friends.
        sock.send("{} {}".format(roomNum,portNum).encode('utf-8'))


    def client(self,sock):
        # Get roomNumber which client want to join.
        receiveMsg = sock.recv(MAX).decode('utf-8')
        flag = False
        for i in self.roomList:
            # Find PORT NUMBER to let clients' socket can connect to.
            if i['roomNum'] == receiveMsg:
                # send PORT NUMBER to let client can connecte
                sock.send(str(i['portNum']).encode('utf-8'))
                flag = True
        if not flag:
            # NO THIS NUMBER
            sock.send("FAIL".encode('utf-8'))
        
class Room:
    startFlag = False
    sockList = [] # Client's sock list

    problem = "apple"

    def __init__(self,ip,portNum):
        self.ip = ip
        self.portNum = portNum
    def start(self):
        # Build a room's socket to start game
        listensock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        listensock.bind((self.ip,self.portNum))
        print("\t{}:{}".format(self.ip,self.portNum))
        listensock.listen(5)
        while True:
            sock,sockname = listensock.accept()
            print("[ {} ]{} has connected.".format(self.portNum,sockname))

            self.sockList.append(sock)      # 把sock放入list
            
            receiveDataThread = threading.Thread(target=self.receiveData,args=(sock,))
            # 負責與client通信，傳輸遊戲所必須的指令
            receiveDataThread.start()

    def connect(self):
        time.sleep(0.5)
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect((self.ip,self.portNum))
        return sock

    def receiveData(self,sock): 
        # room's socket receive MAINCLIENT'S mouse position.
        # And send this MOUSE position to other client.
        # Let them can draw the same picture on the screen 
        while True:
            origin = sock.recv(MAX)
            data = origin.decode('utf-8')
            if data:
                print(data)
                if data[0]=='(': # Form MAIN CLIENT,it is position data
                    for clientSock in self.sockList:    # 遍歷socket list
                        if clientSock != sock:          # 不是自己的才傳送資料.Needn't send position to MAIN
                            clientSock.send(origin) 
                else:   # it is from other client. He/she want to send answer to check the answer
                    if data == self.problem:
                        sock.send('y'.encode('utf-8'))
                    else:
                        sock.send('n'.encode('utf-8'))

class Client:
    def __init__(self,ip,port):
        self.ip = ip
        self.port = port

    def start(self):
        # START to choose MAIN OR CLIENT.
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect((self.ip,self.port))
        self.setType(sock)

    def setType(self,sock):
        print("Type in 'MAIN' to set a new room\nType in 'CLIENT' to join a room")
        msg = input("> ")
        sock.send(msg.encode('utf-8'))
        receiveMsg = sock.recv(MAX).decode('utf-8') # Get response
        if receiveMsg=="OK.SERVER":
            receiveMsg = sock.recv(MAX).decode('utf-8')
            print(receiveMsg)
            # get ROOMNUM and PORTNUM
            connectData = receiveMsg.split(' ')
            room = Room(self.ip,int(connectData[1]))
            sock = room.connect()       # sock可覆蓋了

            # receiveDataThread = threading.Thread(target=self.receiveData,args=(sock,))
            # receiveDataThread.start()
            # sendDataThread = threading.Thread(target=self.sendData,args=(sock,))
            # sendDataThread.start()
            draw.sendDraw(sock,)    # 開始繪圖

        elif receiveMsg=="OK.CLIENT":
            roomNum = input("Room Number> ")
            sock.send(roomNum.encode('utf-8'))
            receiveMsg = sock.recv(MAX).decode('utf-8')
            # Get port number
            room = Room(self.ip,int(receiveMsg))
            sock = room.connect()       # sock可覆蓋了
            
            # receiveDataThread = threading.Thread(target=self.receiveData,args=(sock,))
            # receiveDataThread.start()
            # sendDataThread = threading.Thread(target=self.sendData,args=(sock,))
            # sendDataThread.start()
            draw.receiveDraw(sock) # Start to receive mouse position to draw picture what MAIN client draw. 
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
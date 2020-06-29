import socket,threading,sys,random,multiprocessing,time
import draw,pygame
import requests,json # Get problem
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
            setTypeThread = threading.Thread(target = self.selectType,args=(sock,),daemon=True) # Create a thread for communicating with client.
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
    startFlag = True
    sockList = [] # Client's sock list

    def __init__(self,ip,portNum):
        self.ip = ip
        self.portNum = portNum
        self.problem = self.getProblem()
        print(self.problem)
    def start(self):
        # Build a room's socket to start game
        listensock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        listensock.bind((self.ip,self.portNum))
        print("\t{}:{}".format(self.ip,self.portNum))
        listensock.listen(5)
        emptyFlag = True
        while self.startFlag:
            sock,sockname = listensock.accept()
            print("[ {} ]{} has connected.".format(self.portNum,sockname))

            allPeerName = []
            self.sockList.append(sock)      # 把sock放入list

            # Send socket list to client to build a user list and put it beside picture.
            for i in self.sockList:
                allPeerName.append(i.getpeername())
            for sock in self.sockList:
                sock.send("[list] {}".format(json.dumps(allPeerName)).encode('utf-8'))
            receiveDataThread = threading.Thread(target=self.receiveData,args=(sock,),daemon=True)
            # 負責與client通信，傳輸遊戲所必須的指令
            receiveDataThread.start()

            if emptyFlag:
                self.game()
                emptyFlag = False

    def game(self):
        mainSocket = random.choice(self.sockList)
        time.sleep(4)
        print("GAME SEND PROBLEM")
        for clientSock in self.sockList:
            if clientSock == mainSocket:
                clientSock.send('[prob] {}'.format(self.problem).encode('utf-8'))
            else:
                clientSock.send('[gues]'.encode('utf-8'))
    def connect(self):
        time.sleep(0.5)
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect((self.ip,self.portNum))
        return sock
    def getProblem(self):
        jsonResponse = requests.get('https://ncnu-hungrycat.com/pyGartic.php')
        jsonData = json.loads(jsonResponse.text)
        return jsonData['problem']
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
                elif data=='[restart]':  # [restart]
                    print('game restart')
                    time.sleep(1)
                    for clientSock in self.sockList:
                        clientSock.send('restart'.encode('utf-8'))
                
                    self.game() #restart

                else:   # it is from other client. He/she want to send answer to check the answer
                    if data == self.problem:
                        sock.send('y'.encode('utf-8'))
                    elif data == 'exit':
                        sock.send('exitok'.encode('utf-8'))
                        self.sockList.remove(sock)
                        allPeerName = []
                        # Send socket list to client to build a user list and put it beside picture.
                        for i in self.sockList:
                            allPeerName.append(i.getpeername())
                        for sock in self.sockList:
                            sock.send("[list] {}".format(json.dumps(allPeerName)).encode('utf-8'))
                        # Close Process
                        if len(self.sockList):
                            self.startFlag = False
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
        sock.close()

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
            sock.close()
            sock = room.connect()       # sock可覆蓋了

            # receiveDataThread = threading.Thread(target=self.receiveData,args=(sock,))
            # receiveDataThread.start()
            # sendDataThread = threading.Thread(target=self.sendData,args=(sock,))
            # sendDataThread.start()

        elif receiveMsg=="OK.CLIENT":
            roomNum = input("Room Number> ")
            sock.send(roomNum.encode('utf-8'))
            receiveMsg = sock.recv(MAX).decode('utf-8')
            # Get port number
            room = Room(self.ip,int(receiveMsg))
            sock.close()
            sock = room.connect()       # sock可覆蓋了
            
            # receiveDataThread = threading.Thread(target=self.receiveData,args=(sock,))
            # receiveDataThread.start()
            # sendDataThread = threading.Thread(target=self.sendData,args=(sock,))
            # sendDataThread.start()
        
        else:
            print("ERROR TYPE")
            exit

        userList = sock.recv(1024).decode('utf-8')
        print("List: ",userList)
                
        ## SET PYGAME
        pygame.init()
        pygame.display.set_caption('Mouse Example')
        size= [1080, 480]
        screen= pygame.display.set_mode(size)
        
        
        continueFlag = False
        while not continueFlag:
            screen.fill((255, 255, 255))
            pgStringVar = pygame.font.Font(None,25).render("Please wait...",False,(0,0,0))# 文字物件
            screen.blit(pgStringVar,(500,240))# draw font
            pygame.display.update()

            print("START RECEIVE.")
            data = sock.recv(1024).decode('utf-8')
            role = data[1:5]
           
            print("Role: ",role)
            if role == "prob":
                problem = data.split(' ')[1]
                continueFlag = draw.sendDraw(sock,userList,screen,problem)
                
            elif role == "gues":
                continueFlag = draw.receiveDraw(sock,screen,userList)
                
            elif role == "list":
                userList = data
                print("List: ",userList)
                continueFlag = False
                
            else:   #useless position
                continueFlag = False

        pygame.quit()
    # def receiveData(self,sock):
    #     while True:
    #         data = sock.recv(MAX).decode('utf-8')
    #         if data:
    #             print(data)
    # def sendData(self,sock):
    #     while True:
    #         data = input("> ")
    #         sock.send(data.encode('utf-8'))
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
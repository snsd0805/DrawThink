import pygame, sys,threading
import json,time

def drawUserList(nowUserList,screen):
    listSTR = nowUserList[7:]
            
    listJSON = json.loads(listSTR)
    #[['127.0.0.1', 52362], ['127.0.0.1', 52370]]
    y = 100
    cross = 20
    pygame.draw.rect(screen,(255,255,255),[900,100,200,380])
    for sockName in listJSON:
        pygame.draw.rect(screen,(171, 254, 250),[900,y,200,30],0)    # 輸入匡的矩形
        pgStringVar = pygame.font.Font(None,25).render(str(sockName),False,(0,0,0))# 文字物件
        screen.blit(pgStringVar,(910,y+10))# draw font
        pygame.display.update()
        y = y+30+cross

def drawerReceive(sock,screen):
    while True:
        data = sock.recv(1024).decode('utf-8')
        if data[0:6] == "[list]":
            drawUserList(data,screen)
        elif data == "restart":
            print("restart")
            break
        elif data == 'exitok':
            break
    print("drawerRECEIVE CLOSED")

def sendDraw(sock,nowUserList,screen,problem):
    
    # Set white background
    screen.fill((255, 255, 255))
    
    # Set problem font
    pgStringVar = pygame.font.Font(None,30).render("Problem: {}".format(problem),False,(0,0,0))# 文字物件
    screen.blit(pgStringVar,(30,450))
    
    pygame.draw.rect(screen,(171, 254, 250),[100,400,100,50],0)
    pygame.draw.rect(screen,(255, 0, 0),[250,400,100,50],0)
    
    white= (255, 255, 255)
    black= (0, 0, 0)
    clock= pygame.time.Clock()
    # 開始話user list
    drawUserList(nowUserList,screen)
    drawerRecvThreading = threading.Thread(target=drawerReceive,args=(sock,screen),daemon=True)
    drawerRecvThreading.start()
    # 使系統滑鼠圖標不可見
    #pygame.mouse.set_visible(False)
    
    dotPos = []

    mouseFlag = False

    pygame.display.update()
    tempPos = ()
    #detectFlag = True
    print("可以開始畫圖")
    while True:
        for event in pygame.event.get():
            if event.type== pygame.QUIT:
                return True
        
        # 如果按下滑鼠
        # get_pressed() 告訴按下哪個滑鼠按鈕
            if event.type == pygame.MOUSEBUTTONDOWN:
                print ('mouse pressed',pygame.mouse.get_pressed())
                if pygame.mouse.get_pressed()[0]:
                    pos = pygame.mouse.get_pos()
                    # 100,400,100,50
                    if pos[0]>=100 and pos[0]<=200 and pos[1]>=400 and pos[1]<=450:
                        sock.send("[restart]".encode('utf-8'))
                        #if data == 'restart':
                        time.sleep(1) #drawerReceive
                        #detectFlag = False
                        return False
                        #print("restart")
                    # 250,400,100,50
                    if pos[0]>=250 and pos[0]<=350 and pos[1]>=400 and pos[1]<=450:
                        sock.send('exit'.encode('utf-8'))
                        return True
                    mouseFlag = True
        # 如果釋放滑鼠
            elif event.type == pygame.MOUSEBUTTONUP:
                print ('mouse released', pygame.mouse.get_pressed())
                if pygame.mouse.get_pressed()[0] == 0:
                    mouseFlag = False
        # 如果滑鼠在運動中
            if event.type == pygame.MOUSEMOTION:
                #print ('mouse is moving', pygame.mouse.get_pos())
                if mouseFlag:
                    #dotPos.append(pygame.mouse.get_pos())
                    if(pygame.mouse.get_pos()!=tempPos):
                        sock.send("{}+".format(pygame.mouse.get_pos()).encode('utf-8'))
                        pygame.draw.circle(screen,black,pygame.mouse.get_pos(),5,0)
                        pygame.display.update()
                        tempPos = pygame.mouse.get_pos()
            
        
        # feature
        # 在滑鼠周圍畫一個圓
        #for i in range(len(dotPos)-1):
        #    pygame.draw.line(screen,black,dotPos[i],dotPos[i+1],5)
        #pos= (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        #pygame.draw.circle(screen, black, pos, 5, 0)
        

        clock.tick(30)
    print("停止畫圖")



startFlag = True
def guessInput(screen,sock):
    global startFlag
    guessStr = ""
    while startFlag:
        for event in pygame.event.get() :
            if event.type== pygame.QUIT:    # close GUI
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:  # Key down. 
                if event.key>=97 and event.key<122: #a~z
                    guessStr = guessStr + chr(event.key)   
                elif event.key == 13:       #enter,send to server,clean
                    sock.send(guessStr.encode('utf-8'))
                    guessStr = ""
                elif event.key == 8 :       #backspace
                    guessStr = guessStr[0:-1]

                pygame.draw.rect(screen,(171, 254, 250),[100,450,500,550],0)    # 輸入匡的矩形
                pgStringVar = pygame.font.Font(None,30).render(guessStr,False,(0,0,0))# 文字物件
                print(guessStr) # for test
                screen.blit(pgStringVar,(120,455))# draw font
                pygame.display.update()

def receiveDraw(sock,screen):
    global startFlag
    print("進入receiveDraw")
    print(startFlag)
    white= (255, 255, 255)
    black= (0, 0, 0)
    
    screen.fill((255, 255, 255))
    pygame.draw.rect(screen,(171, 254, 250),[100,450,500,550],0)
    pygame.display.update()
    print("draw start")

    guessThreading = threading.Thread(target=guessInput,args=(screen,sock),daemon=True) # guest input
    guessThreading.start()
    
    while startFlag:
        data = sock.recv(1024).decode('utf-8')
        if data == 'exitok':
            startFlag = False
            return True
        elif data[0:6] == "[list]":
            drawUserList(data,screen)
            continue
        elif data == 'restart':
            startFlag = False
            time.sleep(0.5)
            startFlag = True
            return False
        elif data == 'y':
            pgStringVar = pygame.font.Font(None,80).render("CORRECT!!!",False,(255,0,0))# 文字物件
            screen.blit(pgStringVar,(540,240))# draw font
            pygame.display.update()
        elif data == 'n':
            pgStringVar = pygame.font.Font(None,80).render("WRONG!!!",False,(255,0,0))# 文字物件
            screen.blit(pgStringVar,(100,450))# draw font
            pygame.display.update()
        #print(data)
        else:
            li = data.split('+')   # 送來的座標可能一次有多個，規範以+隔開
            for i in li:
                if i!="":
                    # 切割取得座標
                    i = i.lstrip('(')
                    i = i.rstrip(')')
                    i = i.replace(',','')
                    i = i.split(' ')
                    print(i)    #for test
                    if len(i)==2 :       # 防止傳送過程疏漏
                        if i[0]!='' and i[1]!='':   # 防止傳送過程疏漏
                            pos = (int(i[0]),int(i[1]))
                            # pygame.draw.circle(screen, black, pos, 5, 0)
                            pygame.draw.circle(screen,black,pos,5,0)
                            pygame.display.update()
    startFlag = True
    print("退出receiveDraw")

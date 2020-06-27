import pygame, sys,threading


def sendDraw(sock):
    white= (255, 255, 255)
    black= (0, 0, 0)

    pygame.init()
    pygame.display.set_caption('Mouse Example')
    size= [640, 480]
    screen= pygame.display.set_mode(size)
    clock= pygame.time.Clock()

    # 使系統鼠標圖標不可見
    #pygame.mouse.set_visible(False)
    
    dotPos = []

    mouseFlag = False
    screen.fill((255, 255, 255))
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type== pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        # 如果按下鼠標
        # get_pressed() 告訴您按下哪個鼠標按鈕
            if event.type == pygame.MOUSEBUTTONDOWN:
                print ('mouse pressed',pygame.mouse.get_pressed())
                if pygame.mouse.get_pressed()[0]:
                    mouseFlag = True
        # 如果釋放鼠標
            elif event.type == pygame.MOUSEBUTTONUP:
                print ('mouse released', pygame.mouse.get_pressed())
                if pygame.mouse.get_pressed()[0] == 0:
                    mouseFlag = False
        # 如果鼠標在運動中
        # get_rel() - 返回自上次調用此函數以來X和Y的移動量
            if event.type == pygame.MOUSEMOTION:
                print ('mouse is moving', pygame.mouse.get_pos())
                if mouseFlag:
                    dotPos.append(pygame.mouse.get_pos())
                    sock.send("{}+".format(pygame.mouse.get_pos()).encode('utf-8'))

                    pygame.draw.circle(screen,black,pygame.mouse.get_pos(),5,0)
            
        
        # feature
        # 在鼠標周圍畫一個圓
        #for i in range(len(dotPos)-1):
        #    pygame.draw.line(screen,black,dotPos[i],dotPos[i+1],5)
        #pos= (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        #pygame.draw.circle(screen, black, pos, 5, 0)
        
        pygame.display.update()

        clock.tick(30)

def guessInput(screen):
    guessStr = ""
    while True:
        for event in pygame.event.get() :
            if event.type== pygame.QUIT:    # close GUI
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:  # Key down. 
                if event.key>=97 and event.key<122: #a~z
                    guessStr = guessStr + chr(event.key)   
                elif event.key == 13:       #enter,send to server,clean
                    guessStr = ""
                elif event.key == 8 :       #backspace
                    guessStr = guessStr[0:-1]

                pygame.draw.rect(screen,(171, 254, 250),[100,450,500,550],0)    # 輸入匡的矩形
                pgStringVar = pygame.font.Font(None,30).render(guessStr,False,(0,0,0))# 文字物件
                print(guessStr) # for test
                screen.blit(pgStringVar,(120,455))# draw font
                pygame.display.update()

def receiveDraw(sock):
    white= (255, 255, 255)
    black= (0, 0, 0)

    pygame.init()
    pygame.display.set_caption('Mouse Example')
    size= [640, 480]

    screen= pygame.display.set_mode(size)

    clock= pygame.time.Clock()
    screen.fill((255, 255, 255))
    pygame.draw.rect(screen,(171, 254, 250),[100,450,500,550],0)
    pygame.display.update()
    print("draw start")

    guessThreading = threading.Thread(target=guessInput,args=(screen,)) # guest input
    guessThreading.setDaemon(False)
    guessThreading.start()
    
    while True:
        data = sock.recv(1024).decode('utf-8')
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

    
import pygame, sys


def sendDraw(sock):
    white= (255, 255, 255)
    black= (0, 0, 0)

    pygame.init()
    pygame.display.set_caption('Mouse Example')
    size= [640, 480]
    screen= pygame.display.set_mode(size)
    clock= pygame.time.Clock()

    # 使系統鼠標圖標不可見
    pygame.mouse.set_visible(False)

    mouseFlag = False
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
                    sock.send("{}+".format(pygame.mouse.get_pos()).encode('utf-8'))
            
        screen.fill((255, 255, 255))

        # 在鼠標周圍畫一個圓
        pos= (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        pygame.draw.circle(screen, black, pos, 10, 0)

        pygame.display.update()

        clock.tick(30)

def receiveDraw(sock):
    white= (255, 255, 255)
    black= (0, 0, 0)

    pygame.init()
    pygame.display.set_caption('Mouse Example')
    size= [640, 480]

    screen= pygame.display.set_mode(size)

    clock= pygame.time.Clock()
    print("draw start")
    while True:
        for event in pygame.event.get():
            if event.type== pygame.QUIT:
                pygame.quit()
                sys.exit()
        data = sock.recv(1024).decode('utf-8')
        li = data.split('+')
        #print((li))
        for i in li:
            if i!="":
                screen.fill((255, 255, 255))

                i = i.lstrip('(')
                i = i.rstrip(')')
                i = i.replace(',','')
                i = i.split(' ')
                # 在鼠標周圍畫一個圓
                pos = (int(i[0]),int(i[1]))
                print(pos)
                pygame.draw.circle(screen, black, pos, 10, 0)
                
                pygame.display.update()


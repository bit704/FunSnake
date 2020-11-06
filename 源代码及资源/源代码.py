# 贪玩snake
# By LR and MHN

import random,pygame,sys,os,win32api,win32con, time
from pygame.locals import *

FPS = 10
screenx = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)   # 获取电脑屏幕宽度
screeny = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)   # 获取电脑屏幕高度
WINDOWWIDTH = 1280  # 窗体宽度
WINDOWHEIGHT = 720  # 窗体高度
CELLSIZE = 40
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
BGCOLOR = BLACK

# 定义方向
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0 # syntactic sugar: index of the worm's head

# 食物素材的引入
poison = pygame.image.load('poison.png')
ice = pygame.image.load('ice.png')
fire = pygame.image.load('fire.png')
luckwater = pygame.image.load('luckwater.png')
evilwater = pygame.image.load('evilwater.png')
life = pygame.image.load('life.png')
apple = pygame.image.load('apple.png')

# 蛇头引入
snakeheadright = pygame.image.load('snake head(right).png')
snakeheadleft  = pygame.image.load('snake head(left).png')
snakeheaddown  = pygame.image.load('snake head(down).png')
snakeheadup    = pygame.image.load('snake head(up).png')

# 蛇身引入
snakebodyx = pygame.image.load('snake body(x).png')
snakebodyy = pygame.image.load('snake body(y).png')

# 蛇尾引入
snaketailright = pygame.image.load('snake tail(right).png')
snaketailleft = pygame.image.load('snake tail(left).png')
snaketailup = pygame.image.load('snake tail(up).png')
snaketaildown = pygame.image.load('snake tail(down).png')

# 蛇的转体引入
snaketurnrtu = pygame.image.load('snaketurn(rightup).png')
snaketurnrtd = pygame.image.load('snaketurn(rightdown).png')
snaketurnltu = pygame.image.load('snaketurn(leftup).png')
snaketurnltd = pygame.image.load('snaketurn(leftdown).png')

# 游戏介绍引入
introduction = pygame.image.load('intro.png')

# 开始界面背景图片
startscreen = pygame.image.load('startscreen.png')

# 导入地图
bground1 = pygame.image.load('sea.png')
bground2 = pygame.image.load('desert.png')
bground3 = pygame.image.load('snow.png')

# 导入沙漠地图障碍物
desertobstacle1 = pygame.image.load('desertobstacle1.png')
desertobstacle2 = pygame.image.load('desertobstacle2.png')
desertobstacle3 = pygame.image.load('desertobstacle3.png')
desertobstacle4 = pygame.image.load('desertobstacle4.png')
desertobstacle5 = pygame.image.load('desertobstacle5.png')

# 导入海洋地图障碍物
seeobstacle1 = pygame.image.load('seeobstacle1.png')
seeobstacle2 = pygame.image.load('seeobstacle2.png')
seeobstacle3 = pygame.image.load('seeobstacle3.png')
seeobstacle4 = pygame.image.load('seeobstacle4.png')
seeobstacle5 = pygame.image.load('seeobstacle5.png')

# 导入雪地地图障碍物
snowobstacle = pygame.image.load('snowobstacle.png')

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, state, applesound, toolsound

    pygame.init()
    state = 1

    # 背景音乐
    pygame.mixer.music.load('bgm.wav')
    pygame.mixer.music.play(-1, 0.0)

    # 音效
    applesound = pygame.mixer.Sound('apple_sound.wav')
    toolsound = pygame.mixer.Sound('tool_sound.wav')

    # 使生成的窗口在合适位置
    pos_x = screenx / 2 - WINDOWWIDTH / 2
    pos_y = screeny - WINDOWHEIGHT
    os.environ['SDL_VIDEO_WINDOW_POS'] = '%i,%i' % (pos_x, pos_y)
    os.environ['SDL_VIDEO_CENTERED'] = '0'

    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('贪玩snake')

    # 实现二级窗口
    monitor = showStartScreen()
    if monitor == 0:
        drawintroscreen()

    while True:
        runGame()
        showGameOverScreen()


def runGame():

    #随机障碍的坐标
    block = creatblock()
    coincide = True

    # 初始蛇的位置
    while coincide == True:
        coincide = False
        startx = random.randint(5, CELLWIDTH - 6)
        starty = random.randint(5, CELLHEIGHT- 6)
        wormCoords = [{'x': startx,     'y': starty},
                    {'x': startx - 1, 'y': starty},
                    {'x': startx - 2, 'y': starty}]   # 录入蛇的数据
        for q in range(10):
            for r in range(3):
                if wormCoords[r]['x'] == block[q][0] and wormCoords[r]['y'] == block[q][1]:
                    coincide = True

    direction0 = RIGHT  # 记录初始方向
    direction1 = RIGHT  # 记录转向的方向

    turnplace = []  # 记录转弯的信息
    taildirection = [{'direct': direction0}]  # 蛇尾的方向

    # 生成苹果
    apple = creatapple(block)

    # 生成道具
    item = creatitem(block, apple)

    speed = 10
    pause = False
    starttime = 0
    begintime = -3
    score = 0
    effect = 0  # 加速减速对得分造成的影响
    type = 0
    confuse = False
    tag = 0  # 记录按键方向
    transparent = 0
    unstoppable = 0
    btype = blocktype()

    # 随机地图
    maptype = random.randint(1, 3)
    if maptype == 1:
        bground = bground1
    elif maptype == 2:
        bground = bground2
    else:
        bground = bground3

    while True: # 游戏主循环
        currenttime = time.time()
        if currenttime - starttime < 1 / speed: # 通过时间实现屏幕刷新
            continue
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if (event.key == K_LEFT or event.key == K_a) and direction0 != RIGHT and direction0 != LEFT:
                    tag = LEFT                                                           # 实现道具效果：
                    if confuse:                                                          #         方向转变
                        direction1 = confused(direction1, tag)
                    else:
                        direction1 = LEFT
                    turnplace.append({'direct0': direction0, 'direct1': direction1, 'x': wormCoords[HEAD]['x'],'y': wormCoords[HEAD]['y']})
                    taildirection.append({'direct': direction1})
                elif (event.key == K_RIGHT or event.key == K_d) and direction0 != LEFT and direction0 != RIGHT:
                    tag = RIGHT
                    if confuse:
                        direction1 = confused(direction1, tag)
                    else:
                        direction1 = RIGHT
                    turnplace.append({'direct0': direction0, 'direct1': direction1, 'x': wormCoords[HEAD]['x'],'y': wormCoords[HEAD]['y']})
                    taildirection.append({'direct': direction1})
                elif (event.key == K_UP or event.key == K_w) and direction0 != DOWN and direction0 != UP:
                    tag = UP
                    if confuse:
                        direction1 = confused(direction1, tag)
                    else:
                        direction1 = UP
                    turnplace.append({'direct0': direction0, 'direct1': direction1, 'x': wormCoords[HEAD]['x'],'y': wormCoords[HEAD]['y']})
                    taildirection.append({'direct': direction1})
                elif (event.key == K_DOWN or event.key == K_s) and direction0 != UP and direction0 != DOWN:
                    tag = DOWN
                    if confuse:
                        direction1 = confused(direction1, tag)
                    else:
                        direction1 = DOWN
                    turnplace.append({'direct0': direction0, 'direct1': direction1, 'x': wormCoords[HEAD]['x'],'y': wormCoords[HEAD]['y']})
                    taildirection.append({'direct': direction1})
                elif event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_SPACE:
                    pause = not pause
                direction0 = direction1

        if not pause:
            # 判断蛇是否发生碰撞
            if wormCoords[HEAD]['x'] == -1 or wormCoords[HEAD]['x'] == CELLWIDTH or wormCoords[HEAD]['y'] == -1 or wormCoords[HEAD]['y'] == CELLHEIGHT:
                return
            if unstoppable == 0:
                for a in range(10):
                    if wormCoords[HEAD]['x'] == block[a][0] and wormCoords[HEAD]['y'] == block[a][1]:
                        return
                for wormBody in wormCoords[1:]:
                    if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
                        return

            # 避免苹果产生在蛇上
            for snakebody in wormCoords[1:]:
                if snakebody['x'] == apple['x'] and snakebody['y'] == apple['y']:
                    apple = creatapple(block)

            # 判断蛇是否吃到苹果
            if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
                applesound.play()
                apple = creatapple(block)
                score += (10 + effect)
                unstoppable = 0
            elif wormCoords[HEAD]['x'] == item['x'] and wormCoords[HEAD]['y'] == item['y']:
                toolsound.play()
                item = creatitem(block, apple)

                # 道具效果
                if type == 1:
                    if speed > 2:
                        speed -= 2
                        effect -= 5
                elif type == 2:
                    speed += 2
                    effect += 5
                elif type == 3:
                    unstoppable = 1
                elif type == 4:
                    transparent = 1
                elif type == 5:
                    confuse = False
                    transparent = 0
                    score += 50
                elif type == 6:
                    confuse = True
                del wormCoords[-1]
            else:
                del wormCoords[-1] # 删掉一节身体

            # 随机生成道具
            if random.randint(1,5) == 1 and (time.time() - begintime) > 5:
                type = random.randint(1, 7)
                item = creatitem(block,apple)
                begintime = time.time()

            # 实现蛇的移动
            if direction0 == UP:
                newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
            elif direction0 == DOWN:
                newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}
            elif direction0 == LEFT:
                newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
            elif direction0 == RIGHT:
                newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}
            wormCoords.insert(0, newHead)   #   增加一节身体

            if len(turnplace) != 0:
                if turnplace[0]['x'] == wormCoords[-1]['x'] and turnplace[0]['y'] == wormCoords[-1]['y']:
                    del turnplace[0]
                    del taildirection[0]

        # DISPLAYSURF.fill(BGCOLOR)
        DISPLAYSURF.blit(bground, (0, 0))
        drawblock(maptype,block,btype)
        drawhead(direction1, wormCoords)
        if transparent == 0:
            drawbody(turnplace,wormCoords,direction1)
        drawturn(turnplace)
        drawtail(taildirection, wormCoords)
        drawItem(item, type)
        drawApple(apple)
        high_score = readhigh()
        writehigh(score, high_score)
        drawScore(score)
        drawhigest(high_score)
        pygame.display.update()
        starttime = time.time()
        #FPSCLOCK.tick(FPS)

def creatitem(block, apple):
    coincide = True
    while coincide == True:
        coincide = False
        item = getRandomLocation()
        for w in range(10):
            if item == (block[w][0], block[w][1]) or item == apple:
                coincide = True
    return item

def creatapple(block):
    coincide = True
    while coincide == True:
        coincide = False
        apple = getRandomLocation()
        for w in range(10):
            if apple == (block[w][0], block[w][1]):
                coincide = True
    return apple

def creatblock():
    block = []
    blockx = random.sample(range(1,CELLWIDTH),10)
    blocky = random.sample(range(1,CELLHEIGHT),10)
    for k in range(10):
        block.append([blockx[k],blocky[k]])
    return block

def blocktype():
    a = []
    for i in range(10):
        a.append(random.randint(0,4))
    return a

def drawblock(maptype,block,blocktype):
    if maptype == 1:
        obstacle = [seeobstacle1, seeobstacle2, seeobstacle3, seeobstacle4, seeobstacle5]
        for d in range(10):
            DISPLAYSURF.blit(obstacle[blocktype[d]], (block[d][0] * CELLSIZE, block[d][1] * CELLSIZE))
    if maptype == 2:
        obstacle = [desertobstacle1, desertobstacle2, desertobstacle3, desertobstacle4, desertobstacle5]
        for d in range(10):
            DISPLAYSURF.blit(obstacle[blocktype[d]], (block[d][0] * CELLSIZE, block[d][1] * CELLSIZE))
    if maptype == 3:
        obstacle = snowobstacle
        for d in range(10):
            DISPLAYSURF.blit(obstacle, (block[d][0] * CELLSIZE, block[d][1] * CELLSIZE))

def drawItem(coord,type):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    if type == 1:
        DISPLAYSURF.blit(ice, (x, y))
    elif type == 2:
        DISPLAYSURF.blit(fire, (x, y))
    elif type == 3:
        DISPLAYSURF.blit(life, (x, y))
    elif type == 4:
        DISPLAYSURF.blit(poison, (x, y))
    elif type == 5:
        DISPLAYSURF.blit(luckwater, (x, y))
    elif type == 6:
        DISPLAYSURF.blit(evilwater, (x, y))
    elif type > 6:
        return

def confused(direction,tag):
    if tag == UP:
        if direction == LEFT or direction == RIGHT:
            return(DOWN)
        else:
            return(UP)
    elif tag == DOWN:
        if direction == RIGHT or direction==UP:
            return(UP)
        else:
            return(DOWN)
    elif tag == LEFT:
        if direction == UP or direction==DOWN:
            return(RIGHT)
        else:
            return(LEFT)
    elif tag == RIGHT:
        if direction == UP or direction==DOWN:
            return(LEFT)
        else:
            return(RIGHT)

def checkForKeyPress():
    for event in pygame.event.get():
        if event.type == QUIT:
            terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key

def showStartScreen():  # 开始屏幕
    titleFont = pygame.font.Font('站酷快乐体2016修订版.ttf', 150)
    titleSurf = titleFont.render('贪玩snake', True, WHITE)
    titleRect = titleSurf.get_rect()
    titleRect.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2 - 120)

    # 开始按钮
    startfont = pygame.font.Font('站酷快乐体2016修订版.ttf', 50)
    startsurf = startfont.render('开始游戏', True, WHITE)
    startrect = startsurf.get_rect()
    startrect.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2 + 20)
    startbutton = startrect

    # 游戏信息按钮
    toolfont = pygame.font.Font('站酷快乐体2016修订版.ttf', 50)
    toolsurf = toolfont.render('游戏说明', True, WHITE)
    toolrect = toolsurf.get_rect()
    toolrect.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2 + 100)
    toolbutton = toolrect

    while True:
        DISPLAYSURF.blit(startscreen, (0,0))
        DISPLAYSURF.blit(titleSurf, titleRect)
        DISPLAYSURF.blit(startsurf, startrect)
        DISPLAYSURF.blit(toolsurf, toolrect)

        for event in pygame.event.get():  # 获得事件
            if event.type == pygame.MOUSEBUTTONDOWN:
                if startbutton.collidepoint(event.pos):
                    return 1
                elif toolbutton.collidepoint(event.pos):
                    return 0
            elif event.type == QUIT:
                terminate()

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def drawintroscreen():
    startfont = pygame.font.Font('站酷快乐体2016修订版.ttf', 50)
    startsurf = startfont.render('开始游戏', True, WHITE)
    startrect = startsurf.get_rect()
    startrect.center = (WINDOWWIDTH / 4 - 150, WINDOWHEIGHT - 150)
    startbutton = startrect

    while True:
        DISPLAYSURF.fill(BGCOLOR)
        DISPLAYSURF.blit(introduction, (-100, 0))
        DISPLAYSURF.blit(startsurf, startrect)
        for event in pygame.event.get():  # 获得事件
            if event.type == pygame.MOUSEBUTTONDOWN:
                if startbutton.collidepoint(event.pos):
                    return
            elif event.type == QUIT:
                terminate()

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def terminate():
    pygame.quit()
    sys.exit()

def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}

def showGameOverScreen():   # 游戏结束屏幕
    gameOverFont = pygame.font.Font('站酷快乐体2016修订版.ttf', 150)
    gameSurf = gameOverFont.render('Game Over', True, BLACK)
    gameRect = gameSurf.get_rect()
    gameRect.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)

    DISPLAYSURF.blit(gameSurf, gameRect)
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress()

    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return

def drawScore(scores):  # 分数面板
    scorefont = pygame.font.Font('站酷快乐体2016修订版.ttf', 40)
    score = scorefont.render('Score: %s' % scores, True, BLACK)
    scorerect = score.get_rect()
    scorerect.topleft = (WINDOWWIDTH - 250, 20)
    DISPLAYSURF.blit(score, scorerect)

def readhigh():
    hf = open("high_score.txt", "rt")  # 只读
    high_score = int(hf.readline())
    hf.close()
    return high_score

def writehigh(score,high_score):
    if int(score) > high_score:
        high_score = score
        rf = open("high_score.txt", "wt")  # 覆盖写
        high_score = str(high_score)
        rf.write(high_score)
        rf.close()

def drawhigest(high_score):  # 分数面板
    scorefont = pygame.font.Font('站酷快乐体2016修订版.ttf', 40)
    score = scorefont.render('Top Score: %s' % high_score, True, BLACK)
    scorerect = score.get_rect()
    scorerect.topright = (300, 20)
    DISPLAYSURF.blit(score, scorerect)

def drawhead(direction, place):
    headx = place[HEAD]['x'] * CELLSIZE
    heady = place[HEAD]['y'] * CELLSIZE
    if direction == RIGHT:
        head = snakeheadright
    elif direction == LEFT:
        head = snakeheadleft
    elif direction == UP:
        head = snakeheadup
    elif direction == DOWN:
        head = snakeheaddown
    DISPLAYSURF.blit(head, (headx, heady))

def drawbody(turnplace, snakedata, direction):
    if len(turnplace) == 0:
        for body in snakedata[1: -1]:
            bodyx = body['x'] * CELLSIZE
            bodyy = body['y'] * CELLSIZE
            if direction == LEFT or direction == RIGHT:
                DISPLAYSURF.blit(snakebodyx, (bodyx, bodyy))
            if direction == UP or direction == DOWN:
                DISPLAYSURF.blit(snakebodyy, (bodyx, bodyy))
    else:
        for body in snakedata[1: -1]:
            bodyx = body['x'] * CELLSIZE
            bodyy = body['y'] * CELLSIZE
            for i in range(0, len(turnplace)):
                if body['x'] == turnplace[i]['x'] and body['y'] == turnplace[i]['y']:
                    break
                elif body['x'] == turnplace[i]['x'] and body['y'] != turnplace[i]['y']:
                    DISPLAYSURF.blit(snakebodyy, (bodyx, bodyy))
                elif body['y'] == turnplace[i]['y'] and body['x'] != turnplace[i]['x']:
                    DISPLAYSURF.blit(snakebodyx, (bodyx, bodyy))

def drawturn(turnplace):
        for turn in turnplace[0:]:
            turnx = turn['x'] * CELLSIZE
            turny = turn['y'] * CELLSIZE
            if (turn['direct0'] == RIGHT and turn['direct1'] == UP) or (turn['direct0'] == DOWN and turn['direct1'] == LEFT):
                turnimg = snaketurnrtu
            elif turn['direct0'] == RIGHT and turn['direct1'] == DOWN or (turn['direct0'] == UP and turn['direct1'] == LEFT):
                turnimg = snaketurnrtd
            elif turn['direct0'] == LEFT and turn['direct1'] == UP or (turn['direct0'] == DOWN and turn['direct1'] == RIGHT):
                turnimg = snaketurnltu
            elif turn['direct0'] == LEFT and turn['direct1'] == DOWN or (turn['direct0'] == UP and turn['direct1'] == RIGHT):
                turnimg = snaketurnltd
            DISPLAYSURF.blit(turnimg, (turnx, turny))

def drawtail(taildirection,snakedata):
    tailx = snakedata[-1]['x'] * CELLSIZE
    taily = snakedata[-1]['y'] * CELLSIZE
    if taildirection[0]['direct'] == RIGHT:
        tailimg = snaketailright
    elif taildirection[0]['direct'] == LEFT:
        tailimg = snaketailleft
    elif taildirection[0]['direct'] == UP:
        tailimg = snaketailup
    elif taildirection[0]['direct'] == DOWN:
        tailimg = snaketaildown
    DISPLAYSURF.blit(tailimg, (tailx, taily))

def drawApple(coord):   # 画出苹果
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    DISPLAYSURF.blit(apple,(x,y))

if __name__ == '__main__':
    main()

import pygame, sys, time, random
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 680
GRID_SIZE, GRID_SCALE = 19, 30
CHESS_RADIUS = 13
BLACK_CHESS, WHITE_CHESS = 0, 1
COLOR_LIST = [(0, 0, 0), (255, 255, 255)]
INPUT_DATA, GAMING_BLACK, GAMING_WHITE, WIN, WIN_RULE3, WIN_RULE4, WIN_RULE_MORE = 0, 1, 2, 3, 4, 5, 6
direction = [((0, 1), (0, -1)), ((1, 0), (-1, 0)), ((1, 1), (-1, -1)), ((1, -1), (-1, 1))]
pointlist = [(3, 3), (3, 9), (3, 15), (9, 3), (9, 9),(9, 15), (15, 3), (15, 9), (15, 15)]

def WriteText(scr, fnt, c, txt, x, y):
    pic = fnt.render(txt, True, c)
    scr.blit(pic, (int(x), int(y)))
    return

#检查在(x, y)处落子是否会形成五个连珠胜利
def isfive(grid, x, y, c):
    for i in range(4):
        cnt = 1
        for j in range(2):
            cx, cy = x, y
            for k in range(5):
                cx += direction[i][j][0]
                cy += direction[i][j][1]
                if 0 <= cx < GRID_SIZE and 0 <= cy < GRID_SIZE:
                    if grid[cy][cx] == c:
                        cnt += 1
                    else:
                        break
                else:
                    break
        if cnt == 5:
            return True
    return False

def CheckPos(grid, x, y, c):
    ruleFlag = [0, 0, 0]
    ScoreList = [0] * 8
    #冲2/活2/冲3/活3/冲4/活4/5个/及以上
    AdjScoreList = []

    for i in range(4):
        cnt = 1
        openflag = [1, 1]
        adjl = []
        for j in range(2):
            cx, cy = x, y
            for k in range(5):
                cx += direction[i][j][0]
                cy += direction[i][j][1]
                if cx < 0 or cx >= GRID_SIZE or cy < 0 or cy >= GRID_SIZE or grid[cy][cx] == 1 - c:
                    openflag[j] = 0
                    break
                if grid[cy][cx] == c:
                    cnt += 1

                elif grid[cy][cx] < 0:
                    prev, AdjacentList = 0, []
                    while len(AdjacentList) < 5 or prev == c:
                        AdjacentList.append(grid[cy][cx])
                        prev = grid[cy][cx]
                        cx += direction[i][j][0]
                        cy += direction[i][j][1]
                        if cx < 0 or cx >= GRID_SIZE or cy < 0 or cy >= GRID_SIZE:
                            AdjacentList.append(1 - c)
                            break
                    if len(AdjacentList) >= 1:
                        adjl.append(AdjacentList)
                    break
        AdjScoreList, emptycnt = GetAdjacent(AdjScoreList, adjl, c, cnt, i)
        if cnt < 2 or (cnt < 5 and openflag[0] + openflag[1] <= 0):
            continue
        ScoreList, ruleFlag = GetScoreList(ScoreList, cnt, openflag, emptycnt, ruleFlag)
    return ScoreList, AdjScoreList, ruleFlag


def GetAdjacent (AdjScoreList, adjl, c, currentnum, dr):
    eflag = 1
    for i in range(len(adjl)):
        emptycnt = 0
        AdjacentList = adjl[i]
        if len(AdjacentList) == 1:
            return []
        cnt = 0
        StartFlag = 0
        for i in range(len(AdjacentList)):
            if AdjacentList[i] == c:
                emptycnt += 1
                if StartFlag == 0:
                    AdjScoreList.append([i, 0, 0, currentnum, 0, dr])
                    #空格数 空了的cnt flag cnt
                    StartFlag = 1
                cnt += 1
            if AdjacentList[i] < 0 or i + 1 >= len(AdjacentList):
                emptycnt += 1
                if cnt != 0:
                    StartFlag = 0
                    AdjScoreList[-1][1] = cnt
                    AdjScoreList[-1][2] = 1
                    cnt = 0
                continue
            if AdjacentList[i] == 1 - c:
                if cnt != 0:
                    StartFlag = 0
                    AdjScoreList[-1][1] = cnt
                    cnt = 0
                break
        if emptycnt <= 1:
            eflag = 0
    for i in range(len(AdjScoreList)):
        if eflag == 1:
            AdjScoreList[i][4] = 1
    return AdjScoreList, eflag

def GetScoreList (ScoreList, cnt, openflag, eflag, ruleFlag):
    if cnt == 5:
        ScoreList[6] += 1
        return ScoreList, ruleFlag
    elif cnt > 5:
        ScoreList[7] += 1
        ruleFlag[2] += 1
        return ScoreList, ruleFlag
    else:
        flag = openflag[0] + openflag[1] - 1
        n = (cnt - 2) * 2 + flag
        ScoreList[n] += 1
        if n == 5 or n == 4:
            ruleFlag[1] += 1
        if n == 3 and eflag == 1:
            ruleFlag[0] += 1
    return ScoreList, ruleFlag

def ValueChess (ScoreList1, ScoreList2, AdjacentList1, AdjacentList2, ruleFlag):
    #1是自己的 2是对手的

    #双3，双4，多连
    
    ScoreList = []
    for i in range(len(ScoreList1)):
        ScoreList.append(ScoreList1[i] + ScoreList2[i])
    AdjacentList = AdjacentList1 + AdjacentList2

    score = 0
    score += ScoreList[7] * 100000 + ScoreList[6] * 10000000    #五子
    score += ScoreList[5] * 1000000    #活4
    score += ScoreList1[4] ** 3 * 1000     #冲4
    score += ScoreList2[4] ** 3 * 300
    score += ScoreList[3] ** 5 * 400      #活3
    score += ScoreList[2] * 120     #冲3
    score += ScoreList[1] * 70      #活2
    score += ScoreList[0] * 20      #冲2

    #判断隔了多个子
    for i in AdjacentList:
        #空格数 空了的cnt flag cnt
        if i[1] >= 4:
            continue
        s = 0
        if i[1] == 1:
            s = 40
        elif i[1] == 2:
            s = 100
        elif i[1] == 3:
            s = 200
        if i[2] == 0:
            s /= 3
        s *= 1.2 - i[0] / 5
        s = int(s)
        score += s
    return score, ruleFlag


class CLS_Gobang(object):
    def __init__(self, fnt):
        self.BoardSize = GRID_SIZE * GRID_SCALE
        self.bx0, self.by0 = int((SCREEN_WIDTH - self.BoardSize) / 2) - 20 , int((SCREEN_HEIGHT - self.BoardSize) / 2) - 20
        self.BoardSurface = pygame.Surface((self.BoardSize + 20, self.BoardSize + 20))
        self.ScratchSurface = pygame.Surface((self.BoardSize + 20, self.BoardSize + 20))
        self.fnt = fnt
        return
    
    def ClearBkg(self):
        self.BoardSurface.fill((205, 170, 90))
        x0, y0 = GRID_SCALE / 2 + 20, GRID_SCALE / 2 + 20
        for i in range(GRID_SIZE):
            x, y, w = 0, 0, 1
            if i == GRID_SIZE // 2 or i == 0 or i == GRID_SIZE - 1:
                x, y, w = -1, -1, 3
            pygame.draw.line(self.BoardSurface, (0, 0, 0), (int(x0 + x), int(y0 + i * GRID_SCALE + y)),
                             (int(x0 + (GRID_SIZE - 1) * GRID_SCALE), int(y0 + i * GRID_SCALE + y)), w)
            pygame.draw.line(self.BoardSurface, (0, 0, 0), (int(x0 + i * GRID_SCALE + x), int(y0 + y)),
                             (int(x0 + i * GRID_SCALE + x), int(y0 + (GRID_SIZE - 1) * GRID_SCALE)), w)
            txt = str(i + 1)
            if len(txt) == 1:
                txt = "0" + txt
            WriteText(self.BoardSurface, self.fnt, (255, 255, 255), txt, int(x0 - 30), int(y0 + i * GRID_SCALE - 5))
            WriteText(self.BoardSurface, self.fnt, (255, 255, 255), txt, int(x0 + i * GRID_SCALE - 5), int(y0 - 25))
        for i in pointlist:
            pygame.draw.circle(self.BoardSurface, (0, 0, 0), (int(20 + (i[0] + 0.5) * GRID_SCALE), int(20 + (i[1] + 0.5) * GRID_SCALE)), 5)
        self.ScratchSurface.blit(self.BoardSurface, (0, 0))
        return

    def DrawBkg(self, scr):
        scr.blit(self.BoardSurface, (self.bx0, self.by0))
        return

    def DrawChessMan(self, scr, x, y, c, cfnt, num, rx, ry, ifrect = False):
        self.BoardSurface.blit(self.ScratchSurface, (0, 0))
        pygame.draw.circle(scr, COLOR_LIST[c], \
                    (int(x * GRID_SCALE + GRID_SCALE / 2) + 20, \
                        int(y * GRID_SCALE  + GRID_SCALE / 2) + 20), CHESS_RADIUS)
        WriteText(scr, cfnt, COLOR_LIST[1 - c], num, x * GRID_SCALE + (GRID_SCALE - len(num) * rx) / 2 + 20, y * GRID_SCALE + ry + 20)
        if ifrect == True:
            pygame.draw.rect(scr, (255, 60, 60), (x * GRID_SCALE - 1 + 20, y * GRID_SCALE - 1 + 20, CHESS_RADIUS * 2 + 4, CHESS_RADIUS * 2 + 4), 2)
        return

    def PrintScore(self, ScoreGrid, fnt, rx, ry):
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                num = ScoreGrid[y][x]
                if num <= 0:
                    continue
                WriteText(self.BoardSurface, fnt, (255, 0, 0), str(num), x * GRID_SCALE + (GRID_SCALE - len(str(num)) * rx) / 2, y * GRID_SCALE + ry)

class CLS_Player (object):
    def __init__(self, c, hm, name = "AI: 曲乐成"):
        self.name = name
        self.ishuman = hm
        self.side = c
        self.PlayerName = name
        self.countlist = [0, 0, 0]
        #活3/活4/超过5个
        self.ScoreGrid = []
        for i in range(GRID_SIZE):
            self.ScoreGrid.append([-1]*GRID_SIZE)
        return
    def NextOneStep(self, grid):
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if grid[y][x] != -1:
                    self.ScoreGrid[y][x] = -1
                    continue
                ScoreList1, AdjacentList1, ruleFlag = CheckPos(grid, x, y, self.side)
                ScoreList2, AdjacentList2, r = CheckPos(grid, x, y, 1 - self.side)
                score, ruleFlag = ValueChess(ScoreList1, ScoreList2, AdjacentList1, AdjacentList2, ruleFlag)
                self.ScoreGrid[y][x] = score
        MaxScore, MaxScoreList = 0, []
        '''
        for i in range(GRID_SIZE):
            print(self.ScoreGrid[i])
           ''' 
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if self.ScoreGrid[y][x] > MaxScore:
                    MaxScore = self.ScoreGrid[y][x]
                    MaxScoreList = []
                    MaxScoreList.append((x, y))
                elif self.ScoreGrid[y][x] == MaxScore:
                    MaxScoreList.append((x, y))
        #print(MaxScore)
        if MaxScore == 0:
            MaxScoreList = [(9, 9)]
        return MaxScoreList, len(MaxScoreList) - 1, self.ScoreGrid


class CLS_Framework (object):
    def __init__(self, wfnt, cfnt, bfnt, tx, ty):
        self.grid = []
        for i in range(GRID_SIZE):
            self.grid.append([-1]*GRID_SIZE)
        self.gobang = CLS_Gobang(cfnt)
        self.BoardSize = GRID_SIZE * GRID_SCALE
        self.bx0, self.by0 = (SCREEN_WIDTH - self.BoardSize) / 2, (SCREEN_HEIGHT - self.BoardSize) / 2
        self.state = INPUT_DATA
        self.wfnt, self.tx, self.ty = wfnt, tx, ty
        self.cfnt, self.bfnt = cfnt, bfnt
        self.WinSide = -1
        self.PlayerNum = -1
        self.PlayerList = [0, 0]
        self.ChessNum = 0
        self.lastx, self.lasty = -1, -1
        return

    def draw(self, scr):
        scr.fill((205, 170, 90))
        self.gobang.DrawBkg(scr)
        if self.state <= INPUT_DATA:
            return
        WriteText(scr, self.wfnt, COLOR_LIST[BLACK_CHESS], self.PlayerList[0].name, (SCREEN_WIDTH - self.BoardSize) // 2, 630)
        WriteText(scr, self.wfnt, COLOR_LIST[WHITE_CHESS], self.PlayerList[1].name, \
            SCREEN_WIDTH - (SCREEN_WIDTH - self.BoardSize) / 2 - len(self.PlayerList[1].name) * 12, 630)
        if self.state == GAMING_BLACK or self.state == GAMING_WHITE:
            WriteText(scr, self.wfnt, COLOR_LIST[self.state - GAMING_BLACK], "NEXT PLAYER", self.tx, self.ty)
            pygame.draw.circle(scr, COLOR_LIST[self.state - GAMING_BLACK], (200, int(self.ty + CHESS_RADIUS / 2)), CHESS_RADIUS)
        elif self.state == WIN:
            WriteText(scr, self.wfnt, COLOR_LIST[self.WinSide], self.PlayerList[self.WinSide].name + " WIN BY GETTING 5 OR MORE CONTINUOUS CHESSES", self.tx, self.ty)
        elif self.state == WIN_RULE3:
            WriteText(scr, self.wfnt, COLOR_LIST[self.WinSide], self.PlayerList[self.WinSide].name + " WIN AS THE OPPONENT OPPOSING THE DOUBLE-3 RULE", self.tx, self.ty)
        elif self.state == WIN_RULE4:
            WriteText(scr, self.wfnt, COLOR_LIST[self.WinSide], self.PlayerList[self.WinSide].name + " WIN AS THE OPPONENT OPPOSING THE DOUBLE-4 RULE", self.tx, self.ty)
        elif self.state == WIN_RULE_MORE:
            WriteText(scr, self.wfnt, COLOR_LIST[self.WinSide], self.PlayerList[self.WinSide].name + " WIN AS THE OPPONENT OPPOSING THE MORE-THAN-5 RULE", self.tx, self.ty)
        return

    def DataInput(self, scr):
        global playerName
        PlayerNameList = []
        self.PlayerNum = 1
        if self.PlayerList == [0, 0]:
            '''
            print("How many human players?\nPlease enter a number between 1 and 2.")
            self.PlayerNum = eval(input())
            if self.PlayerNum == 0: 
                self.PlayerList[0] = CLS_Player(0, False)
                self.PlayerList[1] = CLS_Player(1, False)
                self.state = GAMING_BLACK
                self.draw(scr)
                return
            for i in range(self.PlayerNum):
                print("Please enter the name of player", i + 1, ".")
                PlayerName = input()
                PlayerNameList.append("Player: " + PlayerName)
            '''
            PlayerNameList.append("Player: " + input('Input your name:'))
            playerName = PlayerNameList[0][:]
            '''
            print("Please determine the sequence of the players.\nPlayer", PlayerNameList[0], "would go...")
            print("first(holding black) = 1, second(holding white) = 2")
            PlayerSeq = eval(input()) - 1
            '''
        else:
            PlayerNameList.append(playerName)
            self.PlayerList = [0, 0]
        font=pygame.font.Font('simkai.ttf',80)
        WriteText(scr,font,(0,255,255),'(B)lack or (W)hite?',10,10)
        pygame.display.update()
        flag = 0
        while True:
            for event in pygame.event.get():
                if event.type==pygame.KEYDOWN:
                    if event.key == ord('b'):
                        flag = 1
                    if event.key == ord('w'):
                        flag = 2
            if flag:
                break  
        PlayerSeq = flag - 1
        self.PlayerList[PlayerSeq] = CLS_Player(PlayerSeq, True, PlayerNameList[0])
        if self.PlayerNum == 2:
            self.PlayerList[1 - PlayerSeq] = CLS_Player(1 - PlayerSeq, True, PlayerNameList[1])
        else:
            self.PlayerList[1 - PlayerSeq] = CLS_Player(1 - PlayerSeq, False)
        self.state = GAMING_BLACK
        self.draw(scr)
        return
    
    def AddChess(self, scr, x, y):
        ScoreList1, AdjacentList1, ruleFlag = CheckPos(self.grid, x, y, self.state - GAMING_BLACK)
        score, ruleFlag = ValueChess(ScoreList1, [0] * 8, AdjacentList1, [], ruleFlag)

        self.ChessNum += 1
        self.grid[y][x] = self.state - GAMING_BLACK
        if self.lastx != -1 and self.lasty != -1:
            self.gobang.DrawChessMan(self.gobang.ScratchSurface, self.lastx, self.lasty, 1 - (self.state - GAMING_BLACK), self.cfnt, str(self.ChessNum - 1), 8, 9)
        self.gobang.DrawChessMan(self.gobang.BoardSurface, x, y, self.state - GAMING_BLACK, self.bfnt, str(self.ChessNum), 10.5, 6, True)

        if isfive(self.grid, x, y, self.state - GAMING_BLACK) == True or (ruleFlag[2] != 0 and self.state == GAMING_WHITE):
            self.gobang.DrawChessMan(self.gobang.BoardSurface, x, y, self.state - GAMING_BLACK, self.cfnt, str(self.ChessNum), 8, 9)
            self.WinSide = self.state - GAMING_BLACK
            self.state = WIN
            self.draw(scr)
            font=pygame.font.Font('simkai.ttf',80)
            WriteText(scr,font,(0,255,255),'Press R key',10,40)  
            WriteText(scr,font,(0,255,255),'to restart',10,120)           
            return
        self.lastx, self.lasty = x, y
        self.state = 1- (self.state - GAMING_BLACK) + GAMING_BLACK
        self.draw(scr)
        return

    def PreCal(self, scr):
        MaxScoreList, MaxScoreLen, ScoreGrid = self.PlayerList[self.state - GAMING_BLACK].NextOneStep(self.grid)
        pos = MaxScoreList[random.randint(0, MaxScoreLen)]
        self.gobang.PrintScore(ScoreGrid, self.cfnt, 8, 9)
        self.draw(scr)
        return pos

    def mouse_down(self, scr, mx, my):
        if self.state != GAMING_BLACK and self.state != GAMING_WHITE:
            return
        if self.PlayerList[self.state - GAMING_BLACK].ishuman == False:
            return
        x, y = int((mx - self.bx0) // GRID_SCALE), int((my - self.by0) // GRID_SCALE)
        if x < 0 or x >= GRID_SIZE or y < 0 or y >= GRID_SIZE:
            return
        if self.grid[y][x] != -1:
            return
        self.AddChess(scr, x, y)
        return

    def key_down(self, scr, key):
        if key == pygame.K_SPACE and (self.state == GAMING_BLACK or self.state == GAMING_WHITE) :
            if self.PlayerList[self.state - GAMING_BLACK].ishuman == False:
                pos = self.PreCal(scr)
                self.AddChess(scr, pos[0], pos[1])
        if key == pygame.K_q and (self.state == GAMING_BLACK or self.state == GAMING_WHITE):
            if self.PlayerList[self.state - GAMING_BLACK].ishuman == False:
                self.PreCal(scr)
        if key == pygame.K_r:
            self.gobang.ClearBkg()
            self.draw(screen)
            self.grid = []
            for i in range(GRID_SIZE):
                self.grid.append([-1]*GRID_SIZE)
            self.state = INPUT_DATA
            self.DataInput(scr)
            self.lastx, self.lasty = -1, -1
            self.ChessNum = 0
        if key == pygame.K_t:
            x, y = eval(input("dsajklflasjfa"))
            ScoreList1, AdjacentList1, ruleFlag = CheckPos(self.grid, x, y, self.state - GAMING_BLACK)
            ScoreList2, AdjacentList2, r = CheckPos(self.grid, x, y, 1 - (self.state - GAMING_BLACK))
            print(ScoreList1, ScoreList2, AdjacentList1, AdjacentList2)
        return

#==============================================================================================================================================
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("GOBANG  //Designed by Joyce Qu")
WordFont = pygame.font.Font('simkai.ttf', 32)
ChessFont = pygame.font.Font('simkai.ttf', 20)
BigFont = pygame.font.Font('simkai.ttf', 30)
clock = pygame.time.Clock()

framework = CLS_Framework(WordFont, ChessFont, BigFont, 20, 20)
framework.gobang.ClearBkg()
framework.draw(screen)
playerName = ''
framework.DataInput(screen)

while True:
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button != 1:
                continue
            mx, my = event.pos
            framework.mouse_down(screen, mx, my)
        if event.type == pygame.KEYDOWN:
            framework.key_down(screen, event.key)
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    framework.key_down(screen, pygame.K_q)
    framework.key_down(screen, pygame.K_SPACE)
    pygame.display.update()
    clock.tick(2)




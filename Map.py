# Map class, which will be the visualizing class

import cv2 
import numpy as np
from Ghost import Ghost
import time

walls = ['xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
     'x               x               x               x',
     'x                x             x                x',
     'x                 x           x                 x',
     'x        xxxx      x         x                  x',
     'x        x   x      x       x                   x',
     'x        x    x      x     x      xxxxx         x',
     'x        x     x      x   x     xxx   xxx       x',
     'x        x      x      x x     xx       xx      x',
     'x        x       x      x      x         x      x',
     'x        x        x           xx         xx     x',
     'x        x        x           x           x     x',
     'x        x        x           x           x     x',
     'x        x        x           x           x     x',
     'x                 xx         xx           x     x',
     'x                  x         x                  x',
     'x                  xx       xx                  x',
     'x                   xxx   xxx                   x',
     'x                     xxxxx         x           x',
     'x                                   x          xx',
     'x                                   x         xxx',
     'x            x                      x        xxxx',
     'x           xxx                     x       xxxxx',
     'x          xxxxx                    x      xxxxxx',
     'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx']

# walls =['xxxxxxxxx',
#      'x       x',
#      'x xxxxx x',
#      'x   x   x',
#      'x       x',
#      'x x x x x',
#      'x x x x x',
#      'x       x',
#      'xxxxxxxxx']

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (0, 255, 255)
RED = (0, 0, 255)

SF = 30

# Please be in the correct folder (run it outside of pacman133b)
pacmanSprite = cv2.imread('pacman133b/pacman.png', cv2.IMREAD_COLOR)
ghostSprite = cv2.imread('pacman133b/ghost.png', cv2.IMREAD_COLOR)


class Map:
    def __init__(self, spawnPoint):

        self.h = len(walls)
        self.w = len(walls[0])

        print(self.h, self.w)

        self.wallMap = np.zeros((self.w, self.h))

        for x in range(self.w):
            for y in range(self.h):
                if walls[self.h - y - 1][x] == "x":
                    self.wallMap[x, y] = 1

                else:
                    self.wallMap[x, y] = 0

        if self.wallMap[spawnPoint] == 1: 
            raise Exception("Cannot Spawn on Wall")
        
        self.pacmanLocation = spawnPoint
        self.pacmanSprite = cv2.resize(pacmanSprite, (SF, SF))

        self.G = Ghost(self, (1, 1))
        self.ghostSprite = cv2.flip(cv2.resize(ghostSprite, (SF, SF)), 0)

    def generatePacman(self, frame):
        x, y = self.pacmanLocation
        frame[y*SF:(y+1)*SF, x*SF:(x+1)*SF] = self.pacmanSprite
        return frame
    
    def generateGhost(self, frame):
        x, y = self.G.position
        frame[y*SF:(y+1)*SF, x*SF:(x+1)*SF] = self.ghostSprite
        return frame

    def generateImage(self):
        
        whiteScreen = np.zeros((self.h * SF, self.w * SF, 3))

        for x in range(self.w):
            for y in range(self.h):
                if self.wallMap[x,y] == 1:
                    whiteScreen = self.colorLocation(whiteScreen, (x, y), BLACK)
                else:
                    whiteScreen = self.colorLocation(whiteScreen, (x, y), WHITE)

        whiteScreen = self.generatePacman(whiteScreen)
        whiteScreen = self.generateGhost(whiteScreen)

        whiteScreen = cv2.flip(whiteScreen, 0)
        return whiteScreen
    
    def colorLocation(self, frame, location, color):
        x, y = location
        return cv2.rectangle(frame, (x*SF, y*SF), ((x+1)*SF, (y+1)*SF), color, -1)
    
    def colorLocationOutside(self, frame, location, color):
        x, y = location
        flipped = cv2.flip(frame, 0)
        flipped  = cv2.rectangle(flipped, (x*SF, y*SF), ((x+1)*SF, (y+1)*SF), color, -1)
        return cv2.flip(flipped, 0)

    def isWall(self, pt):
        x, y = pt 
        return self.wallMap[x, y] == 1
    
    def getValidMoves(self, location):
        x, y = location

        moves = [(1,0), (-1, 0), (0, 1), (0, -1)]
        validMoves = []

        for (dx, dy) in moves:
            if not self.isWall(((x + dx), (y + dy))):
                validMoves.append((dx, dy))

        return validMoves
    
    def getPacmanLocation(self):
        return self.pacmanLocation

    def movePacman(self, direction):
        '''
        Moves Pacman a given direction, direction is (1,0), (-1, 0), (0, 1), (0, -1) (x, y)
        '''
        dx, dy = direction
        x, y = self.pacmanLocation 
        xf, yf = x + dx, y + dy
        if self.isWall((xf, yf)):
            # Can change
            return 
        
        else:
            self.pacmanLocation = (xf, yf)

    def moveGhost(self):
        self.G.update()


if __name__ == "__main__":
    m = Map((3, 4))
    i = 0

    GHOST_UPDATE_TIME = 2 # 2 seconds for each ghost update
    lastUpdateGhost = time.time()

    while True:
        currentTime = time.time()
        if currentTime - lastUpdateGhost > GHOST_UPDATE_TIME:
            lastUpdateGhost += GHOST_UPDATE_TIME
            # m.moveGhost()

        kp = cv2.waitKey(1)
        if kp == ord('w'):
            m.movePacman((0, 1))

        if kp == ord('a'):
            m.movePacman((-1, 0))

        if kp == ord('s'):
            m.movePacman((0, -1))

        if kp == ord('d'):
            m.movePacman((1, 0))

        if kp == ord('e'):
            m.colorLocation()

        f = m.generateImage()
        cv2.imshow("Map", f)

        if kp & 0xFF == ord('q'):
            break 

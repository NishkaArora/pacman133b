# Map class, which will be the visualizing class

import cv2 
import numpy as np

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

walls =['xxxxxxxxx',
     'x       x',
     'x xxxxx x',
     'x   x   x',
     'x       x',
     'x x x x x',
     'x x x x x',
     'x       x',
     'xxxxxxxxx']

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (0, 255, 255)

SF = 60

pacmanSprite = cv2.imread('pacman133b/pacman.png', cv2.IMREAD_COLOR)

class Map:
    def __init__(self, spawnPoint):

        self.h = len(walls)
        self.w = len(walls[0])

        self.wallMap = np.zeros((self.h, self.w))

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

    def generatePacman(self, frame):
        x, y = self.pacmanLocation
        frame[y*SF:(y+1)*SF, x*SF:(x+1)*SF] = self.pacmanSprite

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

        whiteScreen = cv2.flip(whiteScreen, 0)
        return whiteScreen
    
    def colorLocation(self, frame, location, color):
        x, y = location
        return cv2.rectangle(frame, (x*SF, y*SF), ((x+1)*SF, (y+1)*SF), color, -1)

    def isWall(self, pt):
        x, y = pt 
        return self.wallMap[x, y] == 1

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

if __name__ == "__main__":
    m = Map((3, 4))
    i = 0

    while True:

        kp = cv2.waitKey(1)
        if kp == ord('w'):
            m.movePacman((0, 1))

        if kp == ord('a'):
            m.movePacman((-1, 0))

        if kp == ord('s'):
            m.movePacman((0, -1))

        if kp == ord('d'):
            m.movePacman((1, 0))

        cv2.imshow("Map", m.generateImage())

        if kp & 0xFF == ord('q'):
            break 

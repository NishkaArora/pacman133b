# Map class, which will be the visualizing class

import cv2 
import numpy as np
from Ghost import Ghost
import time
from occupancymap import OccupancyMap

# from playsound import playsound
# from threading import Thread
 
# # for playing note.wav file
# def play_sound():
#     playsound('pacman133b/backgroundmusic.wav')


# thread = Thread(target=play_sound)
# thread.start()

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


walls = [
"xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
"x                          x",
"x xxxx xxxxxx  xxxxxx xxxx x",
"x xxxx xxxxxx  xxxxxx xxxx x",
"x xxxx xxxxxx  xxxxxx xxxx x",
"x                          x",
"x xxxx xx xxxxxxxx xx xxxx x",
"x xxxx xx xxxxxxxx xx xxxx x",
"x      xx    xx    xx      x",
"xxxxxx xxxxx xx xxxxx xxxxxx",
"xxxxxx xxxxx xx xxxxx xxxxxx",
"x      xx          xx      x",
"x xxxx xx xxxxxxxx xx xxxx x",
"x xxxx xx xxxxxxxx xx xxxx x",
"x xxxx    xxxxxxxx    xxxx x",
"x xxxx xx xxxxxxxx xx xxxx x",
"x xxxx xx xxxxxxxx xx xxxx x",
"x      xx          xx      x",
"xxxxxx xx xxxxxxxx xx xxxxxx",
"xxxxxx xx xxxxxxxx xx xxxxxx",
"x            xx            x",
"x xxxxxxxxxx xx xxxxxxxxxx x",
"x xxxxxxxxxx xx xxxxxxxxxx x",
"x   xx                xx   x",
"xxx xx xx xxxxxxxx xx xx xxx",
"xxx xx xx xxxxxxxx xx xx xxx",
"x      xx    xx    xx      x",
"x xxxxxxxxxx xx xxxxxxxxxx x",
"x xxxxxxxxxx xx xxxxxxxxxx x",
"x                          x",
"xxxxxxxxxxxxxxxxxxxxxxxxxxxx"]


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (0, 255, 255)
RED = (0, 0, 255)
BLUE = (255, 0, 0)
PACMAN = (1000, 1000, 1000) # Some non RGB number
GHOST = (-1, -1, -1)

SF = 25

# Please be in the correct folder (run it outside of pacman133b)
pacmanSprite = cv2.imread('pacman133b/pacman.png', cv2.IMREAD_COLOR)
ghostSprite = cv2.imread('pacman133b/ghost.png', cv2.IMREAD_COLOR)


class Map:
    def __init__(self, spawnPoint, probabilityMap=True, nGhosts = 4, ghostPing = 3):
        self.h = len(walls)
        self.w = len(walls[0])

        print(self.h, self.w)

        ghostLocations = [(1, 1), (1, self.h - 2), (self.w - 2, 1), (self.w - 2, self.h - 2)]

        self.defaultColoring = np.zeros((self.w, self.h, 3))

        self.wallMap = np.zeros((self.w, self.h))

        for x in range(self.w):
            for y in range(self.h):
                if walls[self.h - y - 1][x] == "x":
                    self.wallMap[x, y] = 1
                    self.defaultColoring[x, y] = BLACK

                else:
                    self.wallMap[x, y] = 0
                    self.defaultColoring[x, y] = WHITE

        if self.wallMap[spawnPoint] == 1: 
            raise Exception("Cannot Spawn on Wall")
        
        self.pacmanLocation = spawnPoint
        self.pacmanSprite = cv2.resize(pacmanSprite, (SF, SF))

        self.ghosts = [Ghost(self, ghostLocations[i], ghostPing, id=i) for i in range(nGhosts)]

        self.ghostSprite = cv2.flip(cv2.resize(ghostSprite, (SF, SF)), 0)

        self.coloring = np.copy(self.defaultColoring)
        self.futureColoring = np.copy(self.defaultColoring)

        self.testColoring = np.zeros_like(self.futureColoring)

        self.frame = self.generateImageFromScratch()

        self.path = []
        self.pathColor = RED

        if probabilityMap:
            self.probabilityMap = OccupancyMap(self)

    def generatePacman(self, frame):
        x, y = self.pacmanLocation
        frame[y*SF:(y+1)*SF, x*SF:(x+1)*SF] = self.pacmanSprite
        return frame
    
    def generateGhosts(self, frame):

        for ghost in self.ghosts:
            x, y = ghost.position
            frame[y*SF:(y+1)*SF, x*SF:(x+1)*SF] = self.ghostSprite
        return frame

    def generateImageFromScratch(self):
        whiteScreen = np.zeros((self.h * SF, self.w * SF, 3))

        for x in range(self.w):
            for y in range(self.h):
                if self.wallMap[x,y] == 1:
                    whiteScreen = self.colorLocationInternal(whiteScreen, (x, y), BLACK)
                else:
                    whiteScreen = self.colorLocationInternal(whiteScreen, (x, y), WHITE)

        return whiteScreen
    
    def generateImage(self):
        # Save a "prev future coloring"
        self.defaultColoring = np.copy(self.futureColoring)

        self.futureColoring[self.pacmanLocation] = PACMAN
        for ghost in self.ghosts:
            self.futureColoring[ghost.position] = GHOST

        for (x, y) in self.path:
            self.futureColoring[x, y] = self.pathColor

        commonValues = self.futureColoring == self.coloring

        for x in range(self.w):
            for y in range(self.h):
                if not commonValues[x, y].all():
                    
                    if (self.futureColoring[x, y] == PACMAN).all():
                        self.frame = self.generatePacman(self.frame)

                    elif (self.futureColoring[x, y] == GHOST).all():
                        self.frame = self.generateGhosts(self.frame)

                    else:
                        self.frame = self.colorLocationInternal(self.frame, (x, y), self.futureColoring[x, y])

        self.coloring = np.copy(self.futureColoring)
        self.futureColoring = np.copy(self.defaultColoring) 

        return cv2.flip(self.frame, 0)
    
    def colorLocationInternal(self, frame, location, color):
        # ONLY TO BE CALLED INTERNALLY PLEASE 
        x, y = location
        return cv2.rectangle(frame, (x*SF, y*SF), ((x+1)*SF, (y+1)*SF), color, -1)
    
    def highlightPath(self, path, color):
        # Path is the list of (x, y) positions that need to be highlighted
        self.path = path 
        self.pathColor = color  
        

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
            if self.probabilityMap is not None:
                prevProbs = self.probabilityMap.get_prob_map() # Ensure this is only for the "explored" probability, not for the ghost map
                self.probabilityMap.update()
                newProbs = self.probabilityMap.get_prob_map()
                self.updateColorsProbability(prevProbs, newProbs)

            self.pacmanLocation = (xf, yf)

    def updateColorsProbability(self, prevProbs, newProbs):
        self.testColoring = np.zeros_like(self.futureColoring)
        differentProbs = np.ones_like(prevProbs)

        for x in range(self.w):
            for y in range(self.h):
                if differentProbs[x, y]:
                    self.futureColoring[x, y] = self.getTileColoring(x, y, newProbs[x, y])

    def generateTestImage(self):
        blankImage = np.zeros((SF * self.h, SF * self.w, 3))
        for x in range(self.w):
            for y in range(self.h):
                blankImage = self.colorLocationInternal(blankImage, (x, y), self.testColoring[x, y])

        return cv2.flip(blankImage, 0)
                   
    def getTileColoring(self, x, y, newProb):
        if self.isWall((x, y)):
            # If wall, 
            shading = (1 - newProb) * 0.95
            return (shading, shading, shading)
        
        else:
            shading = (1 - (newProb * 0.95))
            return (shading, shading, shading)

    def moveGhost(self):
        for ghost in self.ghosts:
            ghost.update()

    def checkGameComplete(self):
        ghostPositions = [ghost.position for ghost in self.ghosts]
        return self.pacmanLocation in ghostPositions


if __name__ == "__main__":
    GHOST_PING_TIME = 3 # ghost ping sent every 3 minutes 

    m = Map((3, 4), ghostPing=GHOST_PING_TIME)
    i = 0

    GHOST_UPDATE_TIME = 0.3 # 2 seconds for each ghost update
    PACMAN_UPADTE_TIME = 0.1
    lastUpdatePacman = time.time()
    lastUpdateGhost = time.time()

    while True:
        currentTime = time.time()
        if currentTime - lastUpdateGhost > GHOST_UPDATE_TIME:
            lastUpdateGhost += GHOST_UPDATE_TIME
            m.moveGhost()

        kp = cv2.waitKey(1)

        if currentTime - lastUpdatePacman > PACMAN_UPADTE_TIME:
            if kp == ord('w'):
                lastUpdatePacman += PACMAN_UPADTE_TIME
                m.movePacman((0, 1))

            if kp == ord('a'):
                lastUpdatePacman += PACMAN_UPADTE_TIME
                m.movePacman((-1, 0))

            if kp == ord('s'):
                lastUpdatePacman += PACMAN_UPADTE_TIME
                m.movePacman((0, -1))

            if kp == ord('d'):
                lastUpdatePacman += PACMAN_UPADTE_TIME
                m.movePacman((1, 0))

        # if m.checkGameComplete():
        #     print("Game Over")
        #     break

        cv2.imshow("Map", m.generateImage())
        cv2.imshow("Test", m.generateTestImage())
        
        cv2.imshow("Occupancy Map", m.probabilityMap.cv_map)


        if kp & 0xFF == ord('q'):
            break 


    while True:
        # End Screen, no inputs
        cv2.imshow("Map", m.generateImage())
        cv2.imshow("Occupancy Map", m.probabilityMap.cv_map)

        kp = cv2.waitKey(1)
        if kp & 0xFF == ord('q'):
            break 


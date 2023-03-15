# Map class, which will be the visualizing class

import cv2 
import numpy as np
from Ghost import Ghost
import time
from occupancymap import OccupancyMap
from GhostMap import GhostMap
from GhostTrueMap import GhostTrueMap

from dstar_astar import Pacman_Map, run_modified_astar
from colour import Color


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
PINK = Color(hsl=(320/360, 1, 0.5))
BLUE = Color(hsl=(215/360, 1, 0.5))
GREEN = Color(hsl=(150/360, 1, 0.5))
ORANGE = Color(hsl=(25/360, 1, 0.5))

SF = 25

def interpolate(gray, color, p):
    g = gray 
    h = color.get_hue()
    s = (p) * color.get_saturation()
    
    ogl = color.get_luminance()
    l = ogl + (g - ogl) * (1 - p) 
    a = Color(hsl=(h,s,l))
    return (a.get_blue(), a.get_green(), a.get_red())


# Please be in the correct folder (run it outside of pacman133b)
pacmanSprite = cv2.imread('pacman.png', cv2.IMREAD_COLOR)
ghostSprite = cv2.imread('ghost.png', cv2.IMREAD_COLOR)

class Map:
    def __init__(self, spawnPoint, probabilityMap=True, nGhosts = 4, ghostPing = 3):
        self.h = len(walls)
        self.w = len(walls[0])

        self.ghostColors = [PINK, BLUE, GREEN, ORANGE]

        self.pellet_locations = [[21, 20], [10, 10], [15, 19]]

        # print(self.h, self.w)

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

        self.probabilityMap = OccupancyMap(self)

        self.ghostMaps = [GhostTrueMap(ghost, self.w, self.h, self.wallMap) for ghost in self.ghosts]
        #self.ghostMaps = [GhostMap(ghost, self.w, self.h, self.probabilityMap) for ghost in self.ghosts]

        self.ghostSprite = cv2.flip(cv2.resize(ghostSprite, (SF, SF)), 0)

        self.coloring = np.copy(self.defaultColoring)
        self.futureColoring = np.copy(self.defaultColoring)

        self.frame = self.generateImageFromScratch()

        self.mapImage = np.copy(self.frame)

        self.path = []
        self.pathColor = RED
        self.old_pacman_position = None
        self.old_ghost_position = None

    def colorGhostMaps(self, entityFrame):
        claimed = np.zeros_like(self.ghostMaps[0].prob_map)

        for (i, ghostMap) in enumerate(self.ghostMaps):
            impPoints = ghostMap.prob_map > 0.01

            for x in range(self.w):
                for y in range(self.h):
                    if impPoints[x, y] and not claimed[x, y]:
                        claimed[x, y] = 1
                        color = interpolate(self.futureColoring[x, y][0], self.ghostColors[i], min(ghostMap.prob_map[x, y] * 4, 1))
                        self.colorLocationInternal(entityFrame, (x, y), color)

        return entityFrame

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

        # for (x, y) in self.path:
        #     self.futureColoring[x, y] = self.pathColor
            
        commonValues = self.futureColoring == self.coloring

        for x in range(self.w):
            for y in range(self.h):
                if not commonValues[x, y].all():
                    self.frame = self.colorLocationInternal(self.frame, (x, y), self.futureColoring[x, y])

        self.entityFrame = np.copy(self.frame)
        self.entityFrame = self.colorGhostMaps(self.entityFrame)

        for pellet in self.pellet_locations:
            x, y = pellet
            self.entityFrame = cv2.circle(self.entityFrame, (int((x + 1/2)*SF), int((y + 1/2)*SF)), int(SF * 0.2), (255, 255, 0), -1)
        
        self.entityFrame  = self.generatePacman(self.entityFrame)
        self.entityFrame  = self.generateGhosts(self.entityFrame)

        self.coloring = np.copy(self.futureColoring)
        self.futureColoring = np.copy(self.defaultColoring) 

        return cv2.flip(self.entityFrame , 0)

    def generateTotalImage(self):
        toReturnImage = np.copy(self.mapImage)

        for (x, y) in self.path:
            toReturnImage = self.colorLocationInternal(toReturnImage, (x, y), self.pathColor)
            

        for pellet in self.pellet_locations:
            x, y = pellet
            toReturnImage = cv2.circle(toReturnImage, (int((x + 1/2)*SF), int((y + 1/2)*SF)), int(SF * 0.2), (255, 255, 0), -1)

        toReturnImage  = self.generatePacman(toReturnImage)
        toReturnImage  = self.generateGhosts(toReturnImage)

        return cv2.flip(toReturnImage, 0)
    
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
            prevProbs = self.probabilityMap.get_prob_map()
            self.probabilityMap.update()
            newProbs = self.probabilityMap.get_prob_map()
            self.updateColorsProbability(prevProbs, newProbs)
            return False
        
        else:
            # if self.probabilityMap is not None:
            prevProbs = self.probabilityMap.get_prob_map() # Ensure this is only for the "explored" probability, not for the ghost map
            self.pacmanLocation = (xf, yf)
            self.probabilityMap.update()
            newProbs = self.probabilityMap.get_prob_map()
            self.updateColorsProbability(prevProbs, newProbs)
        return True

    def updateColorsProbability(self, prevProbs, newProbs):
        self.testColoring = np.zeros_like(self.futureColoring)
        differentProbs = np.ones_like(prevProbs)

        for x in range(self.w):
            for y in range(self.h):
                if differentProbs[x, y]:
                    self.futureColoring[x, y] = self.getTileColoring(x, y, newProbs[x, y])
      
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
        collision = False
        if self.old_ghost_position != None:
            old_ghost_positions = self.old_ghost_position
            ghost_in_old_pacman_pos = False
            ghost_in_question = 0
            for idx in range(len(ghostPositions)):
                if ghostPositions[idx] == self.old_pacman_position:
                    ghost_in_old_pacman_pos = True
                    ghost_in_question = idx
            if ghost_in_old_pacman_pos:
                if old_ghost_positions[ghost_in_question] == self.pacmanLocation:
                    collision = True
        return self.pacmanLocation in ghostPositions or collision
    
    def combinedMap(self):
        combinedGhostsMap = np.zeros((self.w, self.h))

        for ghost_map in self.ghostMaps:
            combinedGhostsMap += ghost_map.prob_map
        
        return combinedGhostsMap + self.probabilityMap.get_prob_map()


if __name__ == "__main__":
    GHOST_PING_TIME = 4

    pacman_start = (5, 4)# (26, 23)
    m = Map(pacman_start, ghostPing=GHOST_PING_TIME)
    
    pacman_map = Pacman_Map(m.w, m.h, pacman_start, m.pellet_locations)
    i = 0

    GHOST_UPDATE_TIME = 1
    PACMAN_UPADTE_TIME = 1
    GHOST_MAP_UPDATE_TIME = 1

    lastUpdatePacman = time.time()
    lastUpdateGhost = time.time()
    lastUpdateGhostLocations = time.time()

    while True:
        currentTime = time.time()
        if currentTime - lastUpdateGhost > GHOST_UPDATE_TIME:
            m.old_ghost_position = [ghost.position for ghost in m.ghosts]
            lastUpdateGhost += GHOST_UPDATE_TIME
            m.moveGhost()

        kp = cv2.waitKey(1)
        if currentTime - lastUpdatePacman > PACMAN_UPADTE_TIME:
            m.old_pacman_position = m.pacmanLocation
            lastUpdatePacman += PACMAN_UPADTE_TIME
            path, go = run_modified_astar(m, pacman_map)
            if not go:
                break 
            direction = (path[0][0] - m.pacmanLocation[0], path[0][1] - m.pacmanLocation[1])

            m.movePacman(direction)

            # if kp == ord('w'):
            #     lastUpdatePacman += PACMAN_UPADTE_TIME
            #     m.movePacman((0, 1))
            #     path, go = run_modified_astar(m, pacman_map)
            #     if not go:
            #         break

            # if kp == ord('a'):
            #     lastUpdatePacman += PACMAN_UPADTE_TIME
            #     m.movePacman((-1, 0))
            #     path, go = run_modified_astar(m, pacman_map)
            #     if not go:
            #         break

            # if kp == ord('s'):
            #     lastUpdatePacman += PACMAN_UPADTE_TIME
            #     m.movePacman((0, -1))
            #     path, go = run_modified_astar(m, pacman_map)
            #     if not go:
            #         break

            # if kp == ord('d'):
            #     lastUpdatePacman += PACMAN_UPADTE_TIME
            #     m.movePacman((1, 0)) 
            #     path, go = run_modified_astar(m, pacman_map)
            #     if not go:
            #         break
        
        if currentTime - lastUpdateGhostLocations > GHOST_MAP_UPDATE_TIME:
            for i in range(len(m.ghosts)):
                m.ghostMaps[i].updateSpread()

            lastUpdateGhostLocations += GHOST_MAP_UPDATE_TIME

        for i in range(len(m.ghosts)):
            m.ghosts[i].updatePingStatus()
            m.ghostMaps[i].updatePing()

        if m.checkGameComplete():
            print("Game Over")
            break

        cv2.imshow("Map", m.generateImage())
        #cv2.imshow("Ghost map", m.ghostMaps[0].cv_map) # Ghost Map to Debug
        cv2.imshow("Total Information Map", m.generateTotalImage())

        if kp & 0xFF == ord('q'):
            break 

    while True:
        # End Screen, no inputs
        cv2.imshow("Map", m.generateImage())
        kp = cv2.waitKey(1)
        if kp & 0xFF == ord('q'):
            break 


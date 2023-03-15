import numpy as np
import time
import cv2
import Ghost
from math import dist
import math
from numpy.linalg import norm

SF = 25

class GhostTrueMap:
    def __init__(self, ghost, w, h, wall_map):
        # ghost map
        self.ghost = ghost
        self.h, self.w = h, w

        self.true_map = wall_map

        # 0 probability of ghost being anywhere
        self.prob_map = np.zeros((self.w, self.h))

        # for opencv
        self.cv_map = self.generateGhostMap()

    def generateGhostMap(self):
        # ghost map
        whiteScreen = np.zeros((self.h * SF, self.w * SF, 3))

        for x in range(self.w):
            for y in range(self.h):
                whiteScreen = self.colorLocation(whiteScreen, (x, y), self.prob_map[x, y])

        whiteScreen = cv2.flip(whiteScreen, 0)
        return whiteScreen
    
    def colorLocation(self, frame, location, prob):
        x, y = location
        color = (prob*2, prob*2, prob*2)
        return cv2.rectangle(frame, (x*SF, y*SF), ((x+1)*SF, (y+1)*SF), color, -1)

    def updatePing(self):
        if self.ghost.pingAvailable:
            # ghost position is completely known
            _, cur_pos = self.ghost.getPing()

            (gx, gy) = cur_pos
            print('Got Ping')
            self.prob_map = np.zeros((self.w, self.h))
            self.prob_map[gx, gy] = 1 # all prob in one spot

            # update the CV render
            self.cv_map = self.generateGhostMap()

    def updateSpread(self):
        print("spread")
        new_prob_map = np.zeros((self.w, self.h))

        # each pacman step, the prediction ghost position "spreads"
        for x in range(self.w):
            for y in range(self.h):
                if self.prob_map[x, y] != 0: # if there is some support
                    self.spread(x, y, new_prob_map)
        
        self.prob_map = new_prob_map
        self.cv_map = self.generateGhostMap()
        

    def spread(self, x, y, new_prob_map):
            prob_og = self.prob_map[x, y]
            valid_moves = [(0, 0)]
            num_spread = 1
            # count number of boxes to spread to
            for move in [(0, 1), (1, 0), (-1, 0), (0, -1)]:
                dx, dy = move
                if x+dx in range(0, self.w) and y+dy in range(0, self.h) and self.true_map[x+dx, y+dy] == 0:
                    num_spread += 1
                    valid_moves.append(move)
            
            # spread to the valid moves
            prob_each = prob_og / num_spread
            for move in valid_moves:
                dx, dy = move
                new_prob_map[x+dx, y+dy] += prob_each


import numpy as np
import time
import cv2
import Ghost
from math import dist
import math
from numpy.linalg import norm

SF = 25

class GhostMap:
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
        color = (prob*10, prob*10, prob*10)
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
                if x+dx in range(0, self.w) and x+dy in range(0, self.h) and self.true_map[x+dx, y+dy] == 0:
                    num_spread += 1
                    valid_moves.append(move)
            
            # spread to the valid moves
            prob_each = prob_og / num_spread
            for move in valid_moves:
                dx, dy = move
                new_prob_map[x+dx, y+dy] += prob_each

"""
    def get_prob_map(self):
        convert_to_p = lambda l : math.exp(l) / (math.exp(l) + 1.0)
        prob_map = np.array([[convert_to_p(l) for l in row] for row in self.logodds_map])
        return prob_map
    def updateValue(self, cur_pos, ghost_heading, num_moves):
        # implement map updates however you want
        cx, cy = cur_pos
        sq_up = min(cy + num_moves, self.h - 1)
        sq_down = max(cy - num_moves, 0)
        sq_left = max(cx - num_moves, 0)
        sq_right = min(cx + num_moves, self.w - 1)

        for pos_y in range(sq_down, sq_up+1):
            for pos_x in range(sq_left, sq_right+1):
                if (pos_x, pos_y) != (cx, cy):
                    future_vector = np.array((pos_x - cx, pos_y - cy))
                    cos_sim = (future_vector @ ghost_heading.T) / (norm(future_vector)*norm(ghost_heading))
                    cos_sim = (cos_sim+2)/3 # scale to be from 0 to 1
                    self.logoddsmap[pos_x, pos_y] = cos_sim*UPDATE_SCALE + UPDATE_CONST
            
        self.ghost_map = self.get_prob_map()
"""
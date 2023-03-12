import numpy as np
import time
import cv2
import Ghost
from math import dist
import math
from numpy.linalg import norm

SF = 25
UPDATE_CONST = 0.3
UPDATE_SCALE = 1

class GhostMap:
    def __init__(self, ghost, w, h):
        # ghost map
        self.ghost = ghost
        self.ghost_prev_pos = self.ghost.position
        self.h, self.w = h, w

        # equal probability of ghost being anywhere
        self.ghost_map = np.zeros((self.w, self.h)) + (1.0/(self.w * self.h))
        self.logoddsmap = np.zeros((self.w, self.h))

        # for opencv
        self.ghost_map_cv = self.generateGhostMap()

    def generateGhostMap(self):
        # ghost map
        whiteScreen = np.zeros((self.h * SF, self.w * SF, 3))
        prob_map = self.ghost_map

        for x in range(self.w):
            for y in range(self.h):
                whiteScreen = self.colorLocation(whiteScreen, (x, y), prob_map[x, y])

        whiteScreen = cv2.flip(whiteScreen, 0)
        return whiteScreen
    
    def colorLocation(self, frame, location, prob):
        x, y = location
        color = (0, (1-prob)*2, prob*2)
        return cv2.rectangle(frame, (x*SF, y*SF), ((x+1)*SF, (y+1)*SF), color, -1)

    def updateMap(self):
        if self.ghost.pingAvailable:
            id, cur_pos = self.ghost.getPing()

            (x, y) = cur_pos
            ghost_heading = np.array(cur_pos) - np.array(self.ghost_prev_pos)
            ghost_heading = ghost_heading*2
            num_moves = sum(ghost_heading) # estimated number of moves made

            print('Got Ping')

            # when you get the ping, you want a distribution around the ghost position/heading
            # update ghost map with distribution
            #self.ghost_map[x, y] = 1 # uncomment this to track ghost position
            self.updateValue(cur_pos, np.array(ghost_heading), num_moves)

            # update the CV render
            self.ghost_map_cv = self.generateGhostMap()
            # save position to find next heading
            self.ghost_prev_pos = cur_pos

    def get_prob_map(self):
        convert_to_p = lambda l : math.exp(l) / (math.exp(l) + 1.0)
        prob_map = np.array([[convert_to_p(l) for l in row] for row in self.logoddsmap])
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
import numpy as np
import math
from math import sqrt
import cv2

# Log-odds Ratio Constants
INIT_VAL = 0.3
L_FREE = 0.05
#L_IWASHERE = 0.1
L_OCCUPIED = 0.9

### Laser Properties ###
# distance
SEARCH_RAD = 10

# angles
# DTHETA = 30
# thetas = np.arange(0, 360, DTHETA)
SF = 25


class OccupancyMap:
    def __init__(self, map):
        
        self.map = map
        self.true_map = map.wallMap
        self.h, self.w = map.h, map.w

        self.logodds_map = np.zeros((self.w, self.h)) + INIT_VAL
        self.cv_map = self.generateOccupancyMap()

    def get_prob_map(self):
        convert_to_p = lambda l : math.exp(l) / (math.exp(l) + 1.0)
        prob_map = np.array([[convert_to_p(l) for l in row] for row in self.logodds_map])
        return prob_map
    
    def update(self):
        new_loc = self.map.getPacmanLocation()
        #self.logodds_map[new_loc] -= L_IWASHERE # uncomment to leave behind a trail
        cx, cy = new_loc

        # create rays around pacman
        for move in [(0, 1), (1, 0), (-1, 0), (0, -1)]:
            dx, dy = move
            for step in range(0, SEARCH_RAD+1, 1): 
                # start at 0 or 1 depending on what makes sense, 
                # i think 0 makes more sense for our case because
                # if pacman is standing on a box its definitely free
                cur_x, cur_y = cx+step*dx, cy+step*dy
                if cur_x in range(0, self.w) and cur_y in range(0, self.h):
                    if self.true_map[cur_x, cur_y]:
                        self.logodds_map[cur_x, cur_y] += L_OCCUPIED
                        # obstacle reached
                        break
                    else:
                        self.logodds_map[cur_x, cur_y] -= L_FREE
                else:
                    # we're at the ends of the map
                    break
        
        self.cv_map = self.generateOccupancyMap()

    def generateOccupancyMap(self):
        
        whiteScreen = np.zeros((self.h * SF, self.w * SF, 3))
        prob_map = self.get_prob_map()

        for x in range(self.w):
            for y in range(self.h):
                whiteScreen = self.colorLocation(whiteScreen, (x, y), prob_map[x, y])

        whiteScreen = cv2.flip(whiteScreen, 0)
        return whiteScreen
    
    def colorLocation(self, frame, location, prob):
        x, y = location
        color = (0, (1-prob)*2, prob*2)
        return cv2.rectangle(frame, (x*SF, y*SF), ((x+1)*SF, (y+1)*SF), color, -1)


"""

def add_to_rays(x, y):
            if x < 0:
                x = 0
            if x >= self.w - 1:
                x = self.w - 1
            if y < 0:
                y = 0
            if y >= self.h-1:
                y = self.h-1
            
            rays.add((x, y))
    
    def bresenhams_redirector(self, x0, y0, x1, y1):
        if abs(y1 - y0) < abs(x1 - x0):
            if x0 > x1:
                self.bresenhamsLow(x1, y1, x0, y0)
            else:
                self.bresenhamsLow(x0, y0, x1, y1)
        else:
            if y0 > y1:
                self.bresenhamsHigh(x1, y1, x0, y0)
            else:
                self.bresenhamsHigh(x0, y0, x1, y1)
    
    def bresenhamsLow(self, x0, y0, x1, y1):
        dx = x1 - x0
        dy = y1 - y0
        yi = 1
        if dy < 0:
            yi = -1
            dy = -dy
        D = (2 * dy) - dx
        y = y0
        for x in range(x0, x1+1):
            #plot(x, y)
            if not self.true_map[x, y]: # not a wall
                self.logodds_map[x, y] -= L_FREE
            else:
                self.logodds_map[x, y] += L_OCCUPIED
                # break if it makes sense

            if D > 0:
                y = y + yi
                D = D + (2 * (dy - dx))
            else:
                D = D + 2*dy

    def bresenhamsHigh(self, x0, y0, x1, y1):
        dx = x1 - x0
        dy = y1 - y0
        xi = 1
        if dx < 0:
            xi = -1
            dx = -dx
            
        D = (2 * dx) - dy
        x = x0

        for y in range(y0, y1+1, 1):
            #plot(x, y)

            if not self.true_map[x, y]: # not a wall
                self.logodds_map[x, y] -= L_FREE
            else:
                self.logodds_map[x, y] += L_OCCUPIED
                # break if it makes sense
            
            if D > 0:
                x = x + xi
                D = D + (2 * (dx - dy))
            else:
                D = D + 2*dx

    def bresenhams(self, u1, u2, v1, v2):
        # if empty in self.true_map, subtract L_FREE
        # if not empty in self.true_map, add L_OCCUPIED
        # add noise on detection later
        du = - abs(u2-u1)
        dv = abs(v2-v1)

        su = 1 if u1 < u2 else -1
        sv = 1 if v1 < v2 else -1

        err = du + dv
        uk, vk = u1, v1

        while True:
            if not self.true_map[uk, vk]: # not a wall
                self.logodds_map[uk, vk] -= L_FREE
            else:
                self.logodds_map[uk, vk] += L_OCCUPIED
                break # obstacle, don't measure the rest of the line

            if (uk, vk) == (u2, v2):
                break # line done

            if err*2 >= du: # time to move v
                if vk == v2:
                    break # line done

                err = err + du
                vk = vk + sv

            if err*2 <= dv: # time to move u
                if uk == u2:
                    break # line done

                err = err + dv
                uk = uk + su



                def add_to_rays(x, y):

            x_right = min(x+SEARCH_RAD, self.w-1)
            x_left = max(0, x-SEARCH_RAD)

            y_up = min(y+SEARCH_RAD, self.h-1)
            y_down = max(0, y-SEARCH_RAD)

            return set([(x, y_up), (x, y_down), (x_right, y), (x_left, y)])

        rays = add_to_rays(cx, cy)

        # trace each ray
        for ray in rays:
            endx, endy = ray
            #self.logodds_map[endx, endy] -= L_FREE

            if cx == endx:
                # trace in y direction
                for y in range(cy, endy-1 if cy>endy else endy+1, -1 if cy > endy else 1):
                    if not self.true_map[cx, y]: # not a wall
                        self.logodds_map[cx, y] -=L_FREE
                    else:
                        self.logodds_map[cx, y] += L_OCCUPIED
                        break

            elif cy == endy:
                # trace in x direction
                for x in range(cx, endx-1 if cx>endx else endx+1, -1 if cx > endx else 1):
                    if not self.true_map[x, cy]: # not a wall
                        self.logodds_map[x, cy] -=L_FREE
                    else:
                        self.logodds_map[x, cy] += L_OCCUPIED
                        break               

        self.cv_map = self.generateOccupancyMap()
"""
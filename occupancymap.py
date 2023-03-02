import numpy as np
import math
from math import cos, sin


# Log-odds Ratio Constants
INIT_VAL = 0.3
L_FREE = -0.03
L_OCCUPIED = 0.3

### Laser Properties ###
# distance
RMIN = 1
RMAX = 4
# angles
DTHETA = 30
thetas = np.arange(0, 360, DTHETA)


class OccupancyMap:
    def __init__(self, map):
        
        self.map = map
        self.true_map = map.wallMap
        self.h, self.w = map.h, map.w

        self.logodds_map = np.zeros((self.h, self.w)) + INIT_VAL

    def get_prob_map(self):
        convert_to_p = lambda l : math.exp(l) / (math.exp(l) + 1.0)
        prob_map = np.array([[convert_to_p(l) for l in row] for row in self.logodds_map])
        return prob_map
    
    def update(self):
        new_loc = self.map.getPacmanLocation()
        #self.logodds_map[new_loc] = 1 # uncomment to leave behind a trail
        xc, yc = new_loc
        ranges = self.get_laser_ranges(new_loc)

        for r, theta in zip(ranges, thetas):
            x1, y1 = xc + RMIN*cos(theta), yc + RMIN*sin(theta) # start of ray
            x2, y2 = xc + RMAX*cos(theta), yc + RMAX*sin(theta) # end of ray
            u1, v1 = self.to_uv(x1, y1)

            if r > RMIN and r < RMAX: # something was detected
                x2, y2 = xc + r*cos(theta), yc + r*sin(theta) # detection point
                u2, v2 = self.to_uv(x2, y2)
                self.logodds_map[u2, v2] += L_OCCUPIED
            else:
                u2, v2 = self.to_uv(x2, y2)
            
            self.bresenhams_freeing(u1, v1, u2, v2)

        print(self.logodds_map)
        print('\n\n\n\n')
    
    def to_uv(self, x, y):
        return x, y
    
    def bresenhams_freeing(self, u1, v1, u2, v2):
        # free according to bresenhams
        return
    
    def get_laser_ranges(self, pacmanLocation):
        # for each value of theta, calculate the distance of the
        # obstacle in between rmin and rmax from pacman location.
        # 
        return []

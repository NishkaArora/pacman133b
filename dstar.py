import cv2 
import numpy as np
import bisect

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (0, 255, 255)

wall_coordinates = [[2, 2], [2, 3], [4, 2], 
                    [4, 3], [6, 2], [6, 3], 
                    [4, 5], [2, 6], [3, 6], 
                    [4, 6], [5, 6], [6, 6]]

class State:
    # Possible status of each state.
    WALL         = -1 
    UNKNOWN      =  0 
    ONDECKEXPAND =  1 
    ONDECKREMOVE =  5
    PROCESSED    =  2
    PATH         =  3 

    STATUSSTRING = {WALL:           'WALL',
                    UNKNOWN:        'UNKNOWN',
                    ONDECKEXPAND:   'ONDECKEXPAND',
                    ONDECKREMOVE:   'ONDECKREMOVE',
                    PROCESSED:      'PROCESSED',
                    PATH:           'PATH'}

    STATUSCOLOR = {WALL:      np.array([0.0, 0.0, 0.0]),   # Black
                   UNKNOWN:   np.array([1.0, 1.0, 1.0]),   # White
                   ONDECKEXPAND:    np.array([0.0, 1.0, 0.0]), 
                   ONDECKREMOVE: np.array([0.0, 1.0, 1.0]),# Green
                   PROCESSED: np.array([0.0, 0.0, 1.0]),   # Blue
                   PATH:      np.array([1.0, 0.0, 0.0])}   # Red

    # Initialization
    def __init__(self, row, col):
        # Save the location.
        self.row = row
        self.col = col

        # Clear the status and costs.
        self.status = State.UNKNOWN
        self.creach = 0.0       # Actual cost to reach
        self.cost   = 0.0       # Estimated total path cost (to sort)

        # Clear the references.
        self.parent    = None
        self.neighbors = []


    # Define less-than, so we can sort the states by cost.
    def __lt__(self, other):
        return self.cost < other.cost

    # Define the Manhattan distance.
    def distance(self, other):
        return abs(self.row - other.row) + abs(self.col - other.col)

    # Return the representation.
    def __repr__(self):
        return ("<State %d,%d = %s, cost %f>\n" %
                (self.row, self.col,
                 State.STATUSSTRING[self.status], self.cost))

class Pacman_Map:
    def __init__(self, M, N, spawnPoint):
        self.h = N
        self.w = M
        self.wallMap = [[State(m,n) for n in range(N)] for m in range(M)]
        
        # setting initial costs and states
        for x in range(self.w):
            for y in range(self.h):
                # self.wallMap[x][y].cost = 0.5
                self.wallMap[x][y].status = State.UNKNOWN
        
        # setting walls
        for wall in wall_coordinates:
            x = wall[0]
            y = wall[1]
            self.wallMap[x][y].status = State.WALL
        
        # setting neighbors for each box
        for m in range(M):
            for n in range(N):
                if not self.wallMap[m][n].status == State.WALL:
                    for (m1, n1) in [(m-1,n), (m+1,n), (m,n-1), (m,n+1)]:
                        if 0 < m1 < M and 0 < n1 < N:
                            if not self.wallMap[m1][n1].status == State.WALL:
                                self.wallMap[m][n].neighbors.append(self.wallMap[m1][n1])
    # restarting map                               
    def restart_map(self):
            for x in range(self.w):
                for y in range(self.h):
                # self.wallMap[x][y].cost = 0.5
                    self.wallMap[x][y].status = State.UNKNOWN

#
#   D* Algorithm
#
# Estimate the cost to go from state to goal.
def costtogo(state, goal):
    return  10 * state.distance(goal)    

# initial dstar
def dstar_start(start, goal, pacman_map, original_map, frame):
    pacman_map.restart_map()
    onDeck = []
    goal.status = State.ONDECKEXPAND
    onDeck.append(goal)
    frame, onDeck = process(start, goal, original_map, onDeck, frame)
    return frame, onDeck

# dstar if there is an update to the map (currently there is not)
def dstar_later(start, goal, pacman_map, original_map, onDeck, frame):
    if start.status == State.WALL:
        start.status = State.ONDECKREMOVE
        if start not in onDeck:
            bisect.insort(onDeck, start)
        onDeck, new_frame = process(start, goal, original_map, onDeck, frame)
        frame = new_frame
    else:
        frame, onDeck = dstar_start(start, goal, pacman_map, original_map, frame)
    return frame, onDeck
    
# 
def process(start, goal, original_map, onDeck, frame):
    while len(onDeck) != 0:
        node = onDeck.pop(0)
        if node.status == State.ONDECKEXPAND:
            for neighbor in node.neighbors:
                if neighbor.status == State.UNKNOWN:
                    if neighbor in onDeck:
                        onDeck.remove(neighbor)
                    neighbor.parent = node
                    neighbor.cost = node.creach + 1 + costtogo(neighbor, goal)
                    neighbor.status = State.ONDECKEXPAND
                    bisect.insort(onDeck, neighbor)
                elif neighbor.status == State.ONDECKEXPAND:
                    new_cost = node.creach + 1 + costtogo(neighbor, goal)
                    if new_cost < neighbor.cost:
                        neighbor.parent = node
                        neighbor.cost = new_cost
            node.status = State.PROCESSED
            if node == start:
                break
        elif node.status == State.ONDECKREMOVE:
            for neighbor in node.neighbors:
                if neighbor.parent == node:
                    neighbor.status = State.ONDECKREMOVE
                    if neighbor not in onDeck:
                        bisect.insort(onDeck, neighbor)
                elif neighbor.status == State.PROCESSED:
                    neighbor.status = State.ONDECKEXPAND
                    if neighbor not in onDeck:
                        bisect.insort(onDeck, neighbor)
            node.status = State.UNKNOWN

    print("Marking path...")
    #############
    node = start.parent
    node.status = State.PATH
    while node != None:
        node.status = State.PATH
        frame = original_map.colorLocationOutside(frame, [node.row, node.col], (0.0, 1.0, 0.0))
        node = node.parent
    original_map.colorLocationOutside(frame, [goal.row, goal.col], (0.0, 0.0, 1.0))
    #############
    return frame, onDeck
                        
                    
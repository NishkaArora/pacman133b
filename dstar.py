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
    def __init__(self, M, N, spawnPoint, original_map):
        self.h = N
        self.w = M
        self.wallMap = [[State(m,n) for n in range(N)] for m in range(M)]
        
        # setting initial costs and states
        for x in range(self.w):
            for y in range(self.h):
                self.wallMap[x][y].cost = 0
                self.wallMap[x][y].status = State.UNKNOWN
        
        # setting walls
        # for wall in wall_coordinates:
        #     x = wall[0]
        #     y = wall[1]
        #     self.wallMap[x][y].status = State.WALL
        
        # setting neighbors for each box
        for m in range(M):
            for n in range(N):
                if not self.wallMap[m][n].status == State.WALL:
                    for (m1, n1) in [(m-1,n), (m+1,n), (m,n-1), (m,n+1)]:
                        if 0 < m1 < M and 0 < n1 < N:
                            if not self.wallMap[m1][n1].status == State.WALL:
                                self.wallMap[m][n].neighbors.append(self.wallMap[m1][n1])
    # restarting map                               
    def restart_map(self, original_map):
            for x in range(self.w):
                for y in range(self.h):
                    self.wallMap[x][y].cost = original_map.probabilityMap.get_prob_map()[x, y]
                    self.wallMap[x][y].status = State.UNKNOWN

#
#   D* Algorithm
#
# Estimate the cost to go from state to goal.
def costtogo(state, goal):
    return state.distance(goal) * 1/50

# initial dstar
def dstar_start(start, goal, pacman_map, original_map, frame, highlight):
    pacman_map.restart_map(original_map)
    onDeck = []
    goal.status = State.ONDECKEXPAND
    onDeck.append(goal)
    frame, onDeck, path = process(start, goal, original_map, onDeck, frame, highlight)
    return frame, onDeck, path

# dstar if there is an update to the map (currently there is not)
def dstar_later(pacman_x_start, pacman_y_start, pacman_start, start, goal, pacman_map, original_map, old_map, onDeck, frame, changed_places, path):
    count = 0
    for x,y in changed_places:
        node = pacman_map.wallMap[x][y]
        node.cost = original_map.probabilityMap.get_prob_map()[x, y] + costtogo(start, goal)
        if node.cost > 0.8:
            node.status = State.ONDECKREMOVE
        else:
            node.status = State.UNKNOWN
        # bisect.insort(onDeck, node)
    if count == 0:
        # goal.status = State.ONDECKEXPAND
        # onDeck.append(goal)
        print('here2')
        new_frame, onDeck, path = process(start, goal, original_map, onDeck, frame)
        frame = new_frame
    else:
        frame, onDeck, path = dstar_start(start, goal, pacman_map, original_map, frame)
    return frame, onDeck, path
    
# 
def process(start, goal, original_map, onDeck, frame, highlight):
    while len(onDeck) != 0:
        node = onDeck.pop(0)
        if node.status == State.ONDECKEXPAND:
            for neighbor in node.neighbors:
                x = neighbor.row
                y = neighbor.col
                if neighbor.status == State.UNKNOWN:
                    neighbor.parent = node
                    neighbor.cost = node.cost*0.1 + 0.1 + original_map.probabilityMap.get_prob_map()[x, y] + costtogo(neighbor, start)*0.1 #node.cost*0.01 + 0.01 + 
                    neighbor.status = State.ONDECKEXPAND
                    bisect.insort(onDeck, neighbor)
                elif neighbor.status == State.ONDECKEXPAND:
                    new_cost = original_map.probabilityMap.get_prob_map()[x, y] + node.cost*0.1 + 0.1 + costtogo(neighbor, start)*0.1
                    if new_cost < neighbor.cost:
                        neighbor.parent = node
                        neighbor.cost = new_cost
                        onDeck.remove(neighbor)
                        bisect.insort(onDeck, neighbor)
            node.status = State.PROCESSED
            if node == start:
                break
        elif node.status == State.ONDECKREMOVE:
            for neighbor in node.neighbors:
                if neighbor.parent == node:
                    neighbor.status = State.ONDECKREMOVE
                    if neighbor in onDeck:
                        onDeck.remove(neighbor)
                    bisect.insort(onDeck, neighbor)
                elif neighbor.status == State.PROCESSED:
                    neighbor.status = State.ONDECKEXPAND
                    if neighbor in onDeck:
                        onDeck.remove(neighbor)
                    bisect.insort(onDeck, neighbor)
            node.status = State.UNKNOWN

    print("Marking path...")
    #############
    node = start.parent
    node.status = State.PATH
    path = []
    while node != None:
        node.status = State.PATH
        path.append([node.row, node.col])
        # frame = original_map.colorLocationOutside(frame, [node.row, node.col], (0.0, 1.0, 0.0))
        node = node.parent
    if highlight:
        original_map.highlightPath(path, (0.0, 1.0, 0.0))
    # original_map.colorLocationOutside(frame, [goal.row, goal.col], (0.0, 0.0, 1.0))
    #############
    return frame, onDeck, path

def calculate_cost(path, pacman_map):
    cost = 0
    for x,y in path:
        cost += pacman_map.wallMap[x][y].cost 
    return cost
    
                        
                    
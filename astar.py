import cv2 
import numpy as np
import bisect

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (0, 255, 255)

wall_coordinates = [[2, 3], [4, 2], [4, 3], 
                    [6, 2], [6, 3], [4, 5], 
                    [2, 6], [3, 6], [4, 6], 
                    [5, 6], [6, 6]]

class State:
    # Possible status of each state.
    WALL         = -1 
    UNKNOWN      =  0 
    ONDECK       =  1 
    PROCESSED    =  2
    PATH         =  3 

    STATUSSTRING = {WALL:           'WALL',
                    UNKNOWN:        'UNKNOWN',
                    ONDECK:          'ONDECK',
                    PROCESSED:      'PROCESSED',
                    PATH:           'PATH'}

    STATUSCOLOR = {WALL:      np.array([0.0, 0.0, 0.0]),   # Black
                   UNKNOWN:   np.array([1.0, 1.0, 1.0]),   # White
                   ONDECK:    np.array([0.0, 1.0, 1.0]),   # Green
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
    def __init__(self, M, N):
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
                                
    # resetting map for astar       
    def restart_map(self):
            for x in range(self.w):
                for y in range(self.h):
                    self.wallMap[x][y].status = State.UNKNOWN

#
#   A* Algorithm
#
# Estimate the cost to go from state to goal.
def costtogo(state, goal):
    return  10 * state.distance(goal)

def update_cost_parent_creach(node, new_start, goal, state):
    node.parent = new_start
    node.creach = new_start.creach + 1
    node.cost = node.creach + costtogo(node, goal)
    node.status = state
    return node

# Non-Admissable:
def non_admissable(onDeck, new_start, goal, a):
    onDeck.remove(new_start)
    for neighbor in new_start.neighbors:
        if neighbor.status == State.UNKNOWN:
            neighbor = update_cost_parent_creach(neighbor, new_start, goal, State.ONDECK)
            bisect.insort(onDeck, neighbor)
        else:
            new_cost = new_start.creach + 1 + costtogo(neighbor, goal)
            if neighbor.cost > new_cost:
                onDeck.remove(neighbor)
                neighbor = update_cost_parent_creach(neighbor, new_start, goal, State.ONDECK)
                bisect.insort(onDeck, neighbor)     
    if new_start == goal:
        a = False
    new_start.status = State.PROCESSED
    if a:
        new_start = onDeck[0]
    return a, new_start

# Run the full A* algorithm.
def astar(start, goal, pacman_map, original_map, frame):
    onDeck = []
    start.status = State.ONDECK
    start.creach = 0.0
    start.cost   = costtogo(start, goal)
    start.parent = None
    bisect.insort(onDeck, start)

    # Continually expand/build the search tree.
    print("Starting the processing...")
    new_start = start
    a = True
    while a: 
        print("bere")
        # a, new_start = admissable(onDeck, new_start, goal, a)
        a, new_start = non_admissable(onDeck, new_start, goal, a)

    # Create the path to the goal (backwards) and show.
    #############
    node = goal
    node.status = State.PATH
    while node.parent != None:
        node.status = State.PATH
        frame = original_map.colorLocationOutside(frame, [node.row, node.col], (0.0, 1.0, 0.0))
        node = node.parent
    original_map.colorLocationOutside(frame, [goal.row, goal.col], (0.0, 0.0, 1.0))
    #############
    return frame
import cv2 
import numpy as np
import bisect

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (0, 255, 255)

class State:
    # Possible status of each state.
    WALL      = -1  # Not a legal state - just to indicate the wall
    UNKNOWN   =  0      # "Air"
    ONDECK    =  1      # "Leaf"
    PROCESSED =  2      # "Trunk"
    PATH      =  3      # Processed and later marked as on path to goal

    STATUSSTRING = {WALL:      'WALL',
                    UNKNOWN:   'UNKNOWN',
                    ONDECK:    'ONDECK',
                    PROCESSED: 'PROCESSED',
                    PATH:      'PATH'}

    STATUSCOLOR = {WALL:      np.array([0.0, 0.0, 0.0]),   # Black
                   UNKNOWN:   np.array([1.0, 1.0, 1.0]),   # White
                   ONDECK:    np.array([0.0, 1.0, 0.0]),   # Green
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

    # Return the color matching the status.
    def color(self):
        return State.STATUSCOLOR[self.status]

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
    
    
        for x in range(self.w):
            for y in range(self.h):
                # self.wallMap[x][y].cost = 0.5
                self.wallMap[x][y].status = State.UNKNOWN
        
        
        for m in range(M):
            for n in range(N):
                if not self.wallMap[m][n].status == State.WALL:
                    for (m1, n1) in [(m-1,n), (m+1,n), (m,n-1), (m,n+1)]:
                        if 0 < m1 < M and 0 < n1 < N:
                            if not self.wallMap[m1][n1].status == State.WALL:
                                self.wallMap[m][n].neighbors.append(self.wallMap[m1][n1])
        
        self.wallMap[spawnPoint[0]][spawnPoint[1]].cost = 0
        
    def restart_map(self):
            for x in range(self.w):
                for y in range(self.h):
                # self.wallMap[x][y].cost = 0.5
                    self.wallMap[x][y].status = State.UNKNOWN

#
#   A* Algorithm
#
# Estimate the cost to go from state to goal.
def costtogo(state, goal):
    return  10 * state.distance(goal)

def update_cost_parent_creach(node, new_start, goal, state):
    node.parent = new_start
    node.creach = new_start.creach + 1 # + node.distance(new_start)
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
    # Prepare the still empty *sorted* on-deck queue.
    onDeck = []
    # Setup the start state/cost to initialize the algorithm.
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

    # Show the final grid.

    # Create the path to the goal (backwards) and show.
    print("Marking path...")
    #############
    node = new_start # goal
    node.status = State.PATH
    while node != None:
        node.status = State.PATH
        original_map.colorLocation(frame, [node.row, node.col], YELLOW)
        print(node.row)
        node = node.parent
    original_map.colorLocation(frame, [goal.row, goal.col], (0.0, 0.0, 1.0))
    #############
    return

def recalculate_astar(current_position, end_position, pacman_map, original_map, frame):
    astar(current_position, end_position, pacman_map, original_map, frame)
    
    
    
# def dstar(start, goal):
#     onDeck = []
    
#     while len(onDeck) != 0:
#         point = onDeck.pop(0)
#         for neighbor in point.neighbors:
#             if isRaise:
#                 if neighbor.next_point == point:
#                     neighbor.setnextpointandupdatecost(current_point)
#                     bisort(onDeck, neighbor)
#                 else:
                    
            
            
# def isRaise(point, new_cost):
#     if point.cost > new_cost:
#         for neighbor in point.neighbors:
#             cost = point.calculate new cost
#             if cost < point.cost:
                
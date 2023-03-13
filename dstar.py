import cv2 
import numpy as np
import bisect

PROBABILITY_SCALE = 100
WALL_THRESHOLD = 0.7
GREEN = (0.0, 1.0, 0.0)

# wall_coordinates = [[2, 2], [2, 3], [4, 2], 
#                     [4, 3], [6, 2], [6, 3], 
#                     [4, 5], [2, 6], [3, 6], 
#                     [4, 6], [5, 6], [6, 6]]

class State:
    # Possible status of each state.
    WALL         = -1 
    UNKNOWN      =  0 
    ONDECKEXPAND =  1 
    ONDECKREMOVE =  5
    PROCESSED    =  2
    PATH         =  3 
    
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
    
    # Return the representation.
    def __repr__(self):
        return ("<State %d,%d, cost %f>\n" %
                (self.row, self.col, self.cost))
    
    # Define the Manhattan distance.
    def distance(self, other):
        return abs(self.row - other.row) + abs(self.col - other.col)

# pacman map where each box is a node with a cost, state, and set of neighbors
class Pacman_Map:
    def __init__(self, M, N):
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
        for m in range(self.w):
            for n in range(self.h):
                if not self.wallMap[m][n].status == State.WALL:
                    for (m1, n1) in [(m-1,n), (m+1,n), (m,n-1), (m,n+1)]:
                        if 0 < m1 < self.w and 0 < n1 < self.h:
                            if not self.wallMap[m1][n1].status == State.WALL:
                                self.wallMap[m][n].neighbors.append(self.wallMap[m1][n1])
    # restarting map                               
    def restart_map(self):
        for x in range(self.w):
            for y in range(self.h):
                self.wallMap[x][y].cost = 0
                self.wallMap[x][y].status = State.UNKNOWN

#
#   D* Algorithm
#
# Estimate the cost to go from state to goal.
def costtogo(state, goal):
    return state.distance(goal)

# initial dstar
def dstar_start(start, goal, pacman_map, original_map):
    
    # resetting the map by setting all nodes to UNKNOWN state
    pacman_map.restart_map()
    
    # creating onDeck starting with goal
    onDeck = []
    goal.parent = None
    goal.status = State.ONDECKEXPAND
    onDeck.append(goal)
    
    # finding path
    onDeck, path = process(start, goal, original_map, onDeck)
    return onDeck, path

# dstar if there is an update to the map (currently there is not)
def dstar_later(start, goal, pacman_map, original_map, old_map, onDeck, path):
    
    prob_map = original_map.probabilityMap.get_prob_map()
    num_rows = len(pacman_map.wallMap)
    num_cols = len(pacman_map.wallMap[0])
    
    # updating the costs for every node. if the node is a wall then change status
    # error is that the ondeck is being emptied
    for x in range(num_rows):
        for y in range(num_cols):
            node = get_node([x, y], pacman_map)
            # print("here")
            # print(node.cost)
            new_cost = np.exp(prob_map[x, y]*10) - np.exp(old_map[x, y]*10)# *PROBABILITY_SCALE
            node.cost += new_cost
            if node == start:
                print(np.exp(prob_map[x, y]*10) - np.exp(old_map[x, y]*10))
            # print(node.cost)
            if prob_map[x, y] > WALL_THRESHOLD:
                node.status = State.ONDECKREMOVE
            elif new_cost < 0:
                node.status = State.ONDECKEXPAND
            if node in onDeck:
                # print("here")
                onDeck.remove(node)
                bisect.insort(onDeck, node)
    # onDeck2 = []
    # for node in onDeck:
    #     onDeck.remove(node)
    #     if prob_map[node.row, node.col] > WALL_THRESHOLD:
    #         node.status = State.ONDECKREMOVE
    #     bisect.insort(onDeck2, node)
        
    # onDeck = onDeck2
    start.status = State.ONDECKREMOVE
    # start.parent = None
    bisect.insort(onDeck, start)
    onDeck, path = process(start, goal, original_map, onDeck)
    return onDeck, path
    
# taken from gunter notes
def process(start, goal, original_map, onDeck):
    
    # getting probability map 
    prob_map = original_map.probabilityMap.get_prob_map()
    a = True
    # starting loop
    while a:
    #while len(onDeck) != 0:
        node = onDeck.pop(0)
        # if node meant to expand
        if node.status == State.ONDECKEXPAND:
            for neighbor in node.neighbors:
                x = neighbor.row
                y = neighbor.col
                
                # if neighbor has not been explored yet
                if neighbor.status == State.UNKNOWN:
                    cost_of_spot = np.exp(prob_map[x, y] * 10)
                    new_to_go_cost = costtogo(neighbor, start) + cost_of_spot
                    neighbor.status = State.ONDECKEXPAND
                    neighbor = update_node_expand(node, neighbor, new_to_go_cost)
                    bisect.insort(onDeck, neighbor)
                
                # if neighbor needs to expand
                elif neighbor.status == State.ONDECKEXPAND:
                    
                    # calculate new cost
                    cost_of_spot = np.exp(prob_map[x, y] * 10)
                    new_cost = node.creach + 1 + cost_of_spot + costtogo(neighbor, start)
                    
                    # compare new cost with old cost
                    if new_cost < neighbor.cost:
                        new_to_go_cost = new_cost - (node.creach + 1)
                        neighbor = update_node_expand(node, neighbor, new_to_go_cost)
                        if neighbor in onDeck:
                            onDeck.remove(neighbor)
                        bisect.insort(onDeck, neighbor)
            
            # mark node as processed
            node.status = State.PROCESSED
            
            # if start node found, stop process
            if node == start:
                a = False
                continue
        
        # if node meant to removed
        elif node.status == State.ONDECKREMOVE:
            for neighbor in node.neighbors:
                if neighbor.parent == node:
                    status = State.ONDECKREMOVE
                    onDeck = update_node_remove(onDeck, neighbor, status)
                elif neighbor.status == State.PROCESSED:
                    status = State.ONDECKEXPAND
                    onDeck = update_node_remove(onDeck, neighbor, status)
            node.status = State.UNKNOWN
    print("Marking path...")
    node = start.parent
    node.status = State.PATH
    path = []
    while node != None:
        node.status = State.PATH
        path.append([node.row, node.col])
        node = node.parent
    original_map.highlightPath(path, GREEN)
    return onDeck, path

# calculate the cost of the path
def calculate_cost(path, pacman_map):
    cost = 0
    for x,y in path:
        cost += pacman_map.wallMap[x][y].cost 
    return cost

# getting the new pellet to go to
def get_new_pellet(pellet_locations, pellet_idx, pacman_map, start, original_map):
    
    # removing old pellet from possible locations
    old_pellet_x = pellet_locations[pellet_idx][0]
    old_pellet_y = pellet_locations[pellet_idx][1]
    pellet_locations.remove([old_pellet_x, old_pellet_y])
    
    # getting a goal
    pellet_idx = 0
    pellet_goal = get_pellet_node(pellet_locations, 0, pacman_map)
    
    # running dstart to find path and cost of path
    onDeck_new, path_new = dstar_start(start, pellet_goal, pacman_map, original_map)
    min_cost = calculate_cost(path_new, pacman_map)
    
    # iterating through all pellets to see which path has lowest cost
    for i in range(1, len(pellet_locations)):
        
        # finding path to newest pellet
        pellet_goal = get_pellet_node(pellet_locations, i, pacman_map)
        onDeck_new, path_new = dstar_start(start, pellet_goal, pacman_map, original_map)
        
        # finding cost of path and comparing
        new_cost = calculate_cost(path_new, pacman_map)
        if new_cost < min_cost:
            min_cost = new_cost
            pellet_idx = i

    return pellet_locations, pellet_idx      

# getting node of a pellet 
def get_pellet_node(pellet_locations, pellet_idx, pacman_map):
    pellet_x = pellet_locations[pellet_idx][0]
    pellet_y = pellet_locations[pellet_idx][1]
    pellet_goal = pacman_map.wallMap[pellet_x][pellet_y]
    return pellet_goal

# getting node of position on map
def get_node(location, pacman_map):
    x, y = location
    return pacman_map.wallMap[x][y]

# updating node in ONDECKEXPAND
def update_node_expand(node, neighbor, new_to_go_cost):
    neighbor.parent = node
    neighbor.creach = node.creach + 1
    neighbor.cost = neighbor.creach + new_to_go_cost
    return neighbor

# updating node in ONDECKREMOVE
def update_node_remove(onDeck, neighbor, status):
    neighbor.status = status
    if neighbor in onDeck:
        onDeck.remove(neighbor)
    bisect.insort(onDeck, neighbor)
    return onDeck

def choose_closest_pellet(start, pellet_locations, pacman_map):
    pellet_node = get_pellet_node(pellet_locations, 0, pacman_map)
    lowest_cost = costtogo(pellet_node, start)
    pellet_idx = 0
    for idx in range(len(pellet_locations)):
        pellet_node = get_pellet_node(pellet_locations, idx, pacman_map)
        new_cost = costtogo(pellet_node, start)
        if new_cost < lowest_cost:
            pellet_idx = idx
            lowest_cost = new_cost
    return pellet_idx
import cv2 
import numpy as np
from Map import Map
from dstar import Pacman_Map, dstar_start, dstar_later, get_new_pellet, get_pellet_node, get_node, choose_closest_pellet
# from astar import astar

# different positions of the pellet
pellet_locations = [[21, 20], [10, 10], [15, 19]]

# start positions of the pacman
pacman_start = (3, 4)

# index of the pellet wanted in pellet_locations
pellet_idx = 0

if __name__ == "__main__":
    
    # creating the original map
    original_map = Map(pacman_start)
    frame = original_map.generateImage()
    
    # dimentions of the map
    M = original_map.w
    N = original_map.h
    
    # creaing and initializing pacman map
    pacman_map = Pacman_Map(M, N)
    pacman_start = get_node(pacman_start, pacman_map)
    pellet_idx = choose_closest_pellet(pacman_start, pellet_locations, pacman_map)
    pellet_goal = get_pellet_node(pellet_locations, pellet_idx, pacman_map)
    
    # astar: 
    # frame = astar(pacman_start, pellet_goal, pacman_map, map, frame)
    
    # running initial dstar:
    onDeck, path = dstar_start(pacman_start, pellet_goal, pacman_map, 
                               original_map)
    
    # storing old occupancy map
    old_occup_map = original_map.probabilityMap.get_prob_map()
    
    # starting loop
    while True:
        # move is if pacman moves, change is if the occupancy map has changed
        move = False
        changed_places = []
        frame = original_map.generateImage()
        
        # moving pacman
        kp = cv2.waitKey(1)
        
        if kp == ord('w'):
            move = True
            movement = [0, 1]

        if kp == ord('a'):
            move = True
            movement = [-1, 0]
                
        if kp == ord('s'):
            move = True
            movement = [0, -1]
                
        if kp == ord('d'):
            move = True
            movement = [1, 0]
        
        # if there is a movement
        if move:
            
            # make sure that there are still pellets to collect
            if len(pellet_locations) == 0:
                break
            # print("here")
            # print(old_occup_map[5][5])
            # if valid move or if there is a change in the occupancy map
            valid_move = original_map.movePacman(movement)
            if not valid_move:
                continue
            else:
                # finds the places in the map that have changed (change to ones 
                # that are looked at from nishka)
                curr_prob_map = original_map.probabilityMap.get_prob_map()
            
                # for x,y in path:
                #     if old_occup_map[x,y] != curr_prob_map[x, y]:
                #         change = True
                #     # changed_places.append([x,y])

                curr_pacmamn_pos = get_node(original_map.pacmanLocation, 
                                            pacman_map)
                
                # if the pacman reaches a pellet then switch the pellet_location
                if curr_pacmamn_pos == pellet_goal:
                    if len(pellet_locations) == 1:
                        break
                    pellet_locations, pellet_idx = get_new_pellet(
                                                   pellet_locations, 
                                                   pellet_idx, pacman_map, 
                                                   curr_pacmamn_pos, 
                                                   original_map)
                    pellet_goal = get_pellet_node(pellet_locations, 
                                                  pellet_idx, pacman_map)
                onDeck, path = dstar_start(curr_pacmamn_pos, pellet_goal, 
                                           pacman_map, original_map)
                
                # onDeck, path = dstar_later(curr_pacmamn_pos, pellet_goal, 
                #                            pacman_map, original_map, 
                #                            old_occup_map, onDeck, path)
                
                # storing the older version of the probability map
                old_occup_map = original_map.probabilityMap.get_prob_map()
                
                # print(old_occup_map[5][5])
                pellet_idx = choose_closest_pellet(curr_pacmamn_pos, pellet_locations, pacman_map)
                pellet_goal = get_pellet_node(pellet_locations, pellet_idx, pacman_map)
                
        cv2.imshow("Map", frame)
        cv2.imshow("Occupancy Map", original_map.probabilityMap.cv_map)
        if kp & 0xFF == ord('q'):
            break 
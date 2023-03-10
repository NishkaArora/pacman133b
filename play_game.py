import cv2 
import numpy as np
from Map import Map
from dstar import Pacman_Map, State, dstar_start, dstar_later, calculate_cost
from astar import astar

 
pellet_locations = [[3, 7], [10, 10], [15, 19]]
pacman_x_start = 3
pacman_y_start = 4
pellet_idx = 0

if __name__ == "__main__":
    original_map = Map((pacman_x_start, pacman_y_start))
    M = original_map.w
    N = original_map.h
    print(M, N)
    pacman_map = Pacman_Map(M, N, (pacman_x_start, pacman_y_start), original_map)
    
    frame = original_map.generateImage()
    
    pacman_start = pacman_map.wallMap[pacman_x_start][pacman_y_start]
    pellet_goal = pacman_map.wallMap[pellet_locations[pellet_idx][0]][pellet_locations[pellet_idx][1]]
    # astar: 
    # frame = astar(pacman_start, pellet_goal, pacman_map, map, frame)
    
    # dstar:
    frame, onDeck, path = dstar_start(pacman_start, pellet_goal, pacman_map, original_map, frame, True)
    old_occup_map = original_map.probabilityMap.get_prob_map()
    older_val = old_occup_map[3, 5]
    while True:
        pellet_goal = pacman_map.wallMap[pellet_locations[pellet_idx][0]][pellet_locations[pellet_idx][1]]
        move = False
        kp = cv2.waitKey(1)
        frame = original_map.generateImage()
        if kp == ord('w'):
            move = True
            movement = [0, 1]
            #old_occup_map = original_map.probabilityMap.get_prob_map()

        if kp == ord('a'):
            move = True
            movement = [-1, 0]
            #old_occup_map = original_map.probabilityMap.get_prob_map()
                
        if kp == ord('s'):
            move = True
            movement = [0, -1]
            #old_occup_map = original_map.probabilityMap.get_prob_map()
                
        if kp == ord('d'):
            move = True
            movement = [1, 0]
            
        flag = False
        changed_places = []
        
        if move:
            for x,y in path:
                if old_occup_map[x,y] != original_map.probabilityMap.get_prob_map()[x, y]:
                    flag = True
                    changed_places.append([x,y])
                    # break
            old_occup_map = original_map.probabilityMap.get_prob_map()
            if not original_map.movePacman(movement) or flag:
                x_wanted, y_wanted = movement
                x, y = original_map.pacmanLocation
                start = pacman_map.wallMap[x][y]
                if start == pellet_goal:
                    if len(pellet_locations) == 1:
                        break
                    pellet_locations.remove([pellet_locations[pellet_idx][0], pellet_locations[pellet_idx][1]])
                    pellet_goal = pacman_map.wallMap[pellet_locations[0][0]][pellet_locations[0][1]]
                    frame_new, onDeck_new, path_new = dstar_start(start, pellet_goal, pacman_map, original_map, frame, False)
                    min_cost = calculate_cost(path_new, pacman_map)
                    pellet_idx = 0
                    for i in range(1, len(pellet_locations)):
                        pellet_goal = pacman_map.wallMap[pellet_locations[i][0]][pellet_locations[i][1]]
                        frame_new, onDeck_new, path_new = dstar_start(start, pellet_goal, pacman_map, original_map, frame, False)
                        if calculate_cost(path_new, pacman_map) < min_cost:
                            min_cost = calculate_cost(path_new, pacman_map)
                            pellet_idx = i
                            frame_new = frame
                    print(pellet_goal)
                pellet_goal = pacman_map.wallMap[pellet_locations[pellet_idx][0]][pellet_locations[pellet_idx][1]]
                frame, onDeck, path = dstar_start(start, pellet_goal, pacman_map, original_map, frame, True)
                # frame, onDeck, path = dstar_later(pacman_x_start, pacman_y_start, pacman_start, start, pellet_goal, pacman_map, original_map, old_occup_map, onDeck, frame, changed_places, path)
        cv2.imshow("Map", frame)
        cv2.imshow("Occupancy Map", original_map.probabilityMap.cv_map)
        if kp & 0xFF == ord('q'):
            break 
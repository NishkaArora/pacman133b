import cv2 
import numpy as np
from Map import Map
from dstar import Pacman_Map, State, dstar_start, dstar_later
from astar import astar

 
pacman_x_start = 3
pacman_y_start = 4
pellet_x = 20
pellet_y = 20

if __name__ == "__main__":
    original_map = Map((pacman_x_start, pacman_y_start))
    M = original_map.w
    N = original_map.h
    print(M, N)
    pacman_map = Pacman_Map(M, N, (pacman_x_start, pacman_y_start), original_map)
    
    frame = original_map.generateImage()
    
    pacman_start = pacman_map.wallMap[pacman_x_start][pacman_y_start]
    pellet_goal = pacman_map.wallMap[pellet_x][pellet_y]
    
    # astar: 
    # frame = astar(pacman_start, pellet_goal, pacman_map, map, frame)
    
    # dstar:
    frame, onDeck, path = dstar_start(pacman_start, pellet_goal, pacman_map, original_map, frame)
    old_occup_map = original_map.probabilityMap.get_prob_map()
    older_val = old_occup_map[3, 5]
    while True:
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
        if move:
            for x,y in path:
                if old_occup_map[x,y] != original_map.probabilityMap.get_prob_map()[x, y]:
                    print("here")
                    flag = True
                    break
            old_occup_map = original_map.probabilityMap.get_prob_map()
            if not original_map.movePacman(movement) or flag:
                x_wanted, y_wanted = movement
                x, y = original_map.pacmanLocation
                start = pacman_map.wallMap[x][y]
                goal = pacman_map.wallMap[pellet_x][pellet_y]
                frame, onDeck, path = dstar_start(start, pellet_goal, pacman_map, original_map, frame)
                # frame, onDeck, path = dstar_later(x + x_wanted, y + y_wanted, start, goal, pacman_map, original_map, onDeck, frame)
                print(onDeck)
        cv2.imshow("Map", frame)
        cv2.imshow("Occupancy Map", original_map.probabilityMap.cv_map)
        if kp & 0xFF == ord('q'):
            break 
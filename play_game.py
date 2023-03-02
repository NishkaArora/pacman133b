import cv2 
import numpy as np
from Map import Map
from dstar import Pacman_Map, State, dstar_start, dstar_later
from astar import astar


pacman_x_start = 3
pacman_y_start = 4
pellet_x = 1
pellet_y = 2

if __name__ == "__main__":
    original_map = Map((pacman_x_start, pacman_y_start))
    M = original_map.w
    N = original_map.h
    pacman_map = Pacman_Map(M, N, (pacman_x_start, pacman_y_start))
    
    frame = original_map.generateImage()
    
    pacman_start = pacman_map.wallMap[pacman_x_start][pacman_y_start]
    pellet_goal = pacman_map.wallMap[pellet_x][pellet_y]
    
    # astar: 
    # frame = astar(pacman_start, pellet_goal, pacman_map, map, frame)
    
    # dstar:
    
    frame, onDeck = dstar_start(pacman_start, pellet_goal, pacman_map, original_map, frame)
    
    while True:
        movement = False
        kp = cv2.waitKey(1)
        if kp == ord('w'):
            original_map.movePacman((0, 1))
            movement = True

        if kp == ord('a'):
            original_map.movePacman((-1, 0))
            movement = True
            
        if kp == ord('s'):
            original_map.movePacman((0, -1))
            movement = True
            
        if kp == ord('d'):
            original_map.movePacman((1, 0))
            movement = True
            
        if movement:
            frame = original_map.generateImage()
            x, y = original_map.pacmanLocation
            start = pacman_map.wallMap[x][y]
            goal = pacman_map.wallMap[pellet_x][pellet_y]
            # dstar:
            frame, onDeck = dstar_later(start, goal, pacman_map, original_map, onDeck, frame)
            
            # astar:
            # pacman_map.restart_map()
            # frame = astar(start, goal, pacman_map, original_map, frame)
        cv2.imshow("Map", frame)
        if kp & 0xFF == ord('q'):
            break 
import cv2 
import numpy as np
import bisect
from Map import Map
from dstar import Pacman_Map, recalculate_astar, State

if __name__ == "__main__":
    map = Map((3, 4))
    M = map.w
    N = map.h
    pacman_map = Pacman_Map(M, N, (3, 4))
    i = 0
    
    
    for m in range(M):
        for n in range(N):
            for (m1, n1) in [(m-1,n), (m+1,n), (m,n-1), (m,n+1)]:
                if 0 < m1 < M and 0 < n1 < n:
                    pacman_map.wallMap[m][n].neighbors.append(pacman_map.wallMap[m1][n1])
    frame = map.generateImage()
    while True:
        movement = False
        kp = cv2.waitKey(1)
        if kp == ord('w'):
            map.movePacman((0, 1))
            movement = True

        if kp == ord('a'):
            map.movePacman((-1, 0))
            movement = True
            
        if kp == ord('s'):
            map.movePacman((0, -1))
            movement = True
            
        if kp == ord('d'):
            map.movePacman((1, 0))
            movement = True
            
        if movement:
            pacman_map.restart_map()
            frame = map.generateImage()
            x, y = map.pacmanLocation
            recalculate_astar(pacman_map.wallMap[x][y], pacman_map.wallMap[1][2], pacman_map, map, frame)
        # map.colorLocation(frame, [1, 2], (0.0, 0.0, 1.0))
        cv2.imshow("Map", frame)

        if kp & 0xFF == ord('q'):
            break 
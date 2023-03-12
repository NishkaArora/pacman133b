def getTileColoring(newProb, isWall):
    
    # If wall, 
    if isWall:
        shading = (1 - newProb) * 0.66 * 255
        return (shading, shading, shading)
    
    else:
        shading = (1 - (newProb * 0.66)) * 255
        return (shading, shading, shading)

import cv2
import numpy as np

background = np.zeros((100, 100, 3), np.float32)
cv2.rectangle(background, (0, 0), (50, 50), (0.5 , 0.5, 0.2), -1)
cv2.imshow("Background", background)
cv2.waitKey(0)
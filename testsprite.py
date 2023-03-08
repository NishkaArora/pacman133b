import cv2 
import numpy as np

SF = 360

background = np.ones((2*SF, 2*SF, 3)) 
background[:] = (0, 0, 255)

ghostSprite = cv2.imread('pacman133b/ghost.png', 1)
gs = cv2.flip(cv2.resize(ghostSprite, (SF, SF)), 0)

print(ghostSprite.shape)

tmp = cv2.cvtColor(ghostSprite, cv2.COLOR_BGR2GRAY)
print(tmp.shape)

_, alpha = cv2.threshold(tmp, 0, 255, cv2.THRESH_BINARY)

print(alpha.shape)


background[SF: SF * 2, SF : SF * 2] = gs

def mouse_click(event, x, y, 
                flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(background[x, y])


def mouse_click2(event, x, y, 
                flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(gs[x, y])



while True:
    kp = cv2.waitKey(1)

    cv2.imshow("ghost", gs)
    cv2.imshow("bac", background)
    cv2.setMouseCallback('bac', mouse_click)
    cv2.setMouseCallback('ghost', mouse_click2)

    
    if 0xFF == ord('q'):
        break 

import numpy as np
import cv2

SF = 20

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (0, 255, 255)
RED = (0, 0, 255)

global drawing
drawing = False

w = 28
h = 36
wallMap = np.zeros((w, h))
print(wallMap.shape)

def generateImage(h, w):
    
    whiteScreen = np.zeros((h * SF, w * SF, 3))

    for x in range(w):
        for y in range(h):
            if wallMap[x,y] == 1:
                whiteScreen = colorLocation(whiteScreen, (x, y), BLACK)
            else:
                whiteScreen = colorLocation(whiteScreen, (x, y), WHITE)


    whiteScreen = cv2.flip(whiteScreen, 0)
    return whiteScreen

def colorLocation(frame, location, color):
    x, y = location
    return cv2.rectangle(frame, (x*SF, y*SF), ((x+1)*SF, (y+1)*SF), color, 3)

def mouse_click(event, x, y, 
                flags, param):
    global drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        xg, yg = int(np.floor(x / SF)), h - 1 - int(np.floor(y / SF))
        print(xg, yg)

        wallMap[xg, yg] = 1

        drawing = True 

    if event == cv2.EVENT_MOUSEMOVE and drawing:
        xg, yg = int(np.floor(x / SF)), h - 1 - int(np.floor(y / SF))
        print(xg, yg)

        wallMap[xg, yg] = 1

        drawing = True 

    if event == cv2.EVENT_LBUTTONUP:
        drawing = False

    if event == cv2.EVENT_RBUTTONDOWN:

        xg, yg = int(np.floor(x / SF)), h - 1 - int(np.floor(y / SF))
        print(xg, yg)

        wallMap[xg, yg] = 0
        drawing = False


# while True:
#     kp = cv2.waitKey(1)

#     #if kp == ord('e'):
#     #    m.colorLocation()

#     cv2.imshow("Map", generateImage(h, w))
#     cv2.setMouseCallback('Map', mouse_click)

#     if kp == ord('p'):
#         np.savetxt('data.csv', wallMap, delimiter=',')

#     if 0xFF == ord('q'):
#         break 

data = np.loadtxt('pacman133b/data.csv', delimiter=',')

s = ""

arr = "".join([("".join([" " if data[x, h - 1 - y] == 1 else "x" for x in range(w)]) + "\n") for y in range(h)])
print(arr)
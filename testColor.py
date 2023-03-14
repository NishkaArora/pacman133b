from colour import Color
import cv2 
import numpy as np

c = Color(hsl=(320/360, 1, 0.5))
gray = Color(rgb=(255/255, 255/255, 255/255))

white = np.zeros((300, 800, 3))





for p in np.linspace(0, 1, 10):
    g = gray.get_blue()
    h = c.get_hue()
    s = (p) * c.get_saturation()
    ogl = c.get_luminance()

    l = ogl + (g - ogl) * (1 - p) 

    print(h,s,l)

    a = Color(hsl=(h,s,l))

    cv2.circle(white, (100 + int(600 * p), 100), 30, (a.get_blue(), a.get_green(), a.get_red()), -1)



cv2.imshow("white", white)
cv2.waitKey(0)
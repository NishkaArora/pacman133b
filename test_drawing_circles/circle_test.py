# Bresenham's inspired circle algorithm: https://stackoverflow.com/questions/1201200/fast-algorithm-for-drawing-filled-circles
"""
Bitmap bmp = new Bitmap(200, 200);

int r = 50; // radius
int ox = 100, oy = 100; // origin

for (int x = -r; x < r ; x++)
{
    int height = (int)Math.Sqrt(r * r - x * x);

    for (int y = -height; y < height; y++)
        bmp.SetPixel(x + ox, y + oy, Color.Red);
}
"""
import numpy as np
from math import sqrt
import matplotlib.pyplot as plt

map = np.zeros((50, 50))
r = 10
cx, cy = 25, 25

rays = set()

for x in range(-r, r+1, 1): # goes from -r to r
    
    hgt = int(sqrt(r*r - x*x))
    #for y in range(-hgt, hgt, 1):
    map[cx + x, cy + hgt] = 1
    map[cx + x, cy - hgt] = 1
    map[cx+hgt, cy + x] = 1
    map[cx-hgt, cy + x] = 1

    rays.add((cx + x, cy + hgt))
    rays.add((cx + x, cy - hgt))
    rays.add((cx+hgt, cy + x))
    rays.add((cx-hgt, cy + x))
    

plt.imshow(map, cmap='hot', interpolation='nearest')
plt.show()
# -*- coding: cp1251 -*-
__Author__ = 'Gamza'
# my first "Paint"
import numpy as np
import cv2 as cv

drawing = False  # true if mouse is pressed
mode = True  # if True, draw rectangle. Press 'm' to toggle to curve
ix, iy = -1, -1
r = 100
g = 100
b = 100
brushSize = 1


# empty function for trackbars
def nothing(x):
    pass


# mouse callback function
def draw_circle(event, x, y, flags, param):
    global ix, iy, drawing, mode, r, g, b, brushSize
    if event == cv.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
    elif event == cv.EVENT_MOUSEMOVE:
        if drawing:
            if mode:
                cv.rectangle(img, (ix, iy), (x, y), (b, g, r), brushSize)
            else:
                cv.circle(img, (x, y), 1, (b, g, r), brushSize)
    elif event == cv.EVENT_LBUTTONUP:
        drawing = False
        if mode:
            cv.rectangle(img, (ix, iy), (x, y), (b, g, r), brushSize)
        else:
            cv.circle(img, (x, y), 1, (b, g, r), brushSize)


img = np.zeros((512, 512, 3), np.uint8) + 255
cv.namedWindow('image')
# mouse
cv.setMouseCallback('image', draw_circle)
# create trackbars for color change
cv.createTrackbar('R', 'image', 100, 255, nothing)
cv.createTrackbar('G', 'image', 100, 255, nothing)
cv.createTrackbar('B', 'image', 100, 255, nothing)
cv.createTrackbar('brush size', 'image', 10, 100, nothing)

while 1:
    cv.imshow('image', img)
    k = cv.waitKey(10) & 0xFF
    if k == ord('m'):
        mode = not mode
    elif k == 27:
        break
    # get current positions of four trackbars
    r = cv.getTrackbarPos('R', 'image')
    g = cv.getTrackbarPos('G', 'image')
    b = cv.getTrackbarPos('B', 'image')
    brushSize = cv.getTrackbarPos('brush size', 'image')
cv.destroyAllWindows()

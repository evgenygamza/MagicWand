# -*- coding: cp1251 -*-
__Author__ = 'Gamza'
"""First succesful magicwand usage"""
from magicwand import SelectionWindow
import cv2 as cv

# img = cv.imread("greypalau.jpg", cv.CV_LOAD_IMAGE_GRAYSCALE)
# img = cv.imread("AIA20180820_1248_0193.fits")
img = cv.imread("krasavchik.jpg")
# img = cv.imread("Palau.jpg")
window = SelectionWindow(img)
window.show()

print(f"Selection mean: {window.mean[:, 0]}.")

# -*- coding: cp1251 -*-
__Author__ = 'Gamza'

import numpy as np
import sunpy.map
# import sunpy.data.sample
import cv2 as cv

file = 'hmi.M_720s_nrt.20180820_090000_TAI.fits'
hmi = np.nan_to_num(sunpy.map.Map(file).data, nan=-999999)
treshold = 0


def fits2img(fits):
    global treshold

    r = np.copy(fits)
    r[r < -treshold] = -127
    r[abs(r) <= treshold] = 0
    r[r > treshold] *= 127 / (3 * np.std(r[r > treshold]))
    r[r >= 3 * np.std(r[r > treshold])] = 127
    r += 127
    # print(np.std(r))

    g = np.copy(fits)
    g[abs(g) <= treshold] = 0
    g[abs(g) > treshold] = -127
    g += 127
    # print(np.std(g))

    b = np.copy(-fits)
    b[abs(b) <= treshold] = 0
    b[b < -treshold] = -127
    b[b == 999999] = -127
    b[b > treshold] *= 127 / (3 * np.std(b[b > treshold]))
    b += 127
    # print(np.std(b))

    img = np.stack([b, g, r], axis=2)
    return np.rint(img).astype(np.uint8)


# fits.peek()
cv.namedWindow('hmi')
cv.createTrackbar('treshold', 'hmi', 10, 25, lambda x: None)
while 1:
    treshold = cv.getTrackbarPos('treshold', 'hmi')
    cv.imshow('hmi', fits2img(hmi))
    k = cv.waitKey(10)
    if k == 27:
        break

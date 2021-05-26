# -*- coding: cp1251 -*-
__Author__ = 'Gamza'
"""hmi viewer with MagicWand and treshold (prototype)"""

import numpy as np
import sunpy.map
import sunpy.data.sample
import cv2 as cv
import magicwand as mw
# from magicwand import SelectionWindow


class MyFuckingAwesomeWindow(mw.SelectionWindow):
    # def __init_subclass__(mw.SelectionWindow, fits):  # ne to
    def __init__(self, fits, treshold=10):
        mw.SelectionWindow.__init__(self, img=fits2img(fits, treshold), connectivity=4, tolerance=32)
        self.fits = fits
        self.treshold = treshold
        self.img = fits2img(fits, self.treshold)
        cv.createTrackbar('treshold', self.name, treshold, 25, self._treshold_callback)

    def _treshold_callback(self, pos):
        self.treshold = pos

    def _update(self):
        """Updates an image in the already drawn window."""
        # global treshold
        print('in _update: ', self.treshold)
        # treshold = cv.getTrackbarPos('treshold', 'Magic Wand Selector')  # todo nadoli?
        # viz = self.img.copy()  # fixme wrong hole
        viz = self.img.copy()
        contours = mw._find_exterior_contours(self.mask)
        viz = cv.drawContours(viz, contours, -1, color=(255,) * 3, thickness=-1)
        viz = cv.addWeighted(self.img, 0.75, viz, 0.25, 0)
        viz = cv.drawContours(viz, contours, -1, color=(255,) * 3, thickness=1)

        self.mean, self.stddev = cv.meanStdDev(self.img, mask=self.mask)
        # meanstr = "mean=({:.2f}, {:.2f}, {:.2f})".format(*self.mean[:, 0])  # fixme original code string
        # stdstr = "std=({:.2f}, {:.2f}, {:.2f})".format(*self.stddev[:, 0])  # fixme original code string
        cv.imshow(self.name, viz)
        # cv.displayStatusBar(self.name, ", ".join((meanstr, stdstr)))  # fixme original code string

    def show(self):
        """Draws a window with the supplied image."""
        # self._update()
        # global treshold
        print("Press [q] or [esc] to close the window.")
        while True:
            self.treshold = cv.getTrackbarPos('treshold', 'Magic Wand Selector')  # todo nadoli?
            self.img = fits2img(self.fits, self.treshold)
            # cv.imshow(self.name, self.img)
            self._update()
            print('in show: ', self.treshold)
            k = cv.waitKey(1000) & 0xFF  # todo nado li?
            if k in (ord("q"), ord("\x1b")):
                cv.destroyWindow(self.name)
                break


file = 'hmi.M_720s_nrt.20180820_090000_TAI.fits'
hmi = np.nan_to_num(sunpy.map.Map(file).data, nan=-999999)
# treshold = 0


# def set_treshold(x):
#     global treshold
#     treshold = x


def fits2img(fits, treshold):
    # global treshold
    print('hui: ', treshold)

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
# cv.namedWindow('hmi')
# while 1:
#     cv.imshow('hmi', img)
#     k = cv.waitKey(100)
#     if k == 27:
#         break

# window = SelectionWindow(fits2img(hmi))
# window = MyFuckingAwesomeWindow(fits2img(hmi))
window = MyFuckingAwesomeWindow(hmi)
# cv.createTrackbar('treshold', 'Magic Wand Selector', treshold, 25, lambda x: x)
# cv.createTrackbar('treshold', 'Magic Wand Selector', treshold, 25, set_treshold)
window.show()

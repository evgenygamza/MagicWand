# -*- coding: cp1251 -*-
__Author__ = 'Gamza'
"""custom MagicWand lib
"""
import numpy as np
import sunpy.map
import sunpy.data.sample
import cv2 as cv

SHIFT_KEY = cv.EVENT_FLAG_SHIFTKEY
ALT_KEY = cv.EVENT_FLAG_ALTKEY


def _find_exterior_contours(img):
    ret = cv.findContours(img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if len(ret) == 2:
        return ret[0]
    elif len(ret) == 3:
        return ret[1]
    raise Exception("Check the signature for `cv.findContours()`.")


def _fits2img(fits, treshold, resize=False):
    # global treshold

    r = np.copy(fits)
    r[r < -treshold] = -127
    r[abs(r) <= treshold] = 0
    r[r > treshold] *= 127 / (3 * np.std(r[r > treshold]))
    r[r >= 3 * np.std(r[r > treshold])] = 127
    r += 127

    g = np.copy(fits)
    g[abs(g) <= treshold] = 0
    g[abs(g) > treshold] = -127
    g += 127

    b = np.copy(-fits)
    b[abs(b) <= treshold] = 0
    b[b < -treshold] = -127
    b[b == 999999] = -127
    b[b > treshold] *= 127 / (3 * np.std(b[b > treshold]))
    b += 127

    img = np.stack([b, g, r], axis=2)
    image = np.rint(img).astype(np.uint8)

    resize = 3

    if type(resize) == int:
        # print(image.shape)
        # image = cv.resize(image, ([dimension / resize for dimension in image.shape[0:2]]))
        image = cv.resize(image, (image.shape[0] // resize, image.shape[0] // resize))
        # print(image.shape)

    return image


class SelectionWindow:
    def __init__(self, fits, name="Magic Wand Selector", connectivity=4, tolerance=32, treshold=10):
        self.name = name
        # self.img = img
        self.treshold = treshold
        self.img = _fits2img(fits, self.treshold)
        h, w = self.img.shape[:2]
        self.fits = fits
        self.mask = np.zeros((h, w), dtype=np.uint8)
        self._flood_mask = np.zeros((h + 2, w + 2), dtype=np.uint8)
        self._flood_fill_flags = (
            connectivity | cv.FLOODFILL_FIXED_RANGE | cv.FLOODFILL_MASK_ONLY | 255 << 8
        )  # 255 << 8 tells to fill with the value 255
        cv.namedWindow(self.name)
        self.tolerance = (tolerance,) * 3
        cv.createTrackbar('treshold', self.name, treshold, 25, self._treshold_callback)
        cv.createTrackbar("Tolerance", self.name, tolerance, 255, self._trackbar_callback)
        cv.setMouseCallback(self.name, self._mouse_callback)

    def _treshold_callback(self, pos):
        self.treshold = pos

    def _trackbar_callback(self, pos):
        self.tolerance = (pos,) * 3

    def _mouse_callback(self, event, x, y, flags, *userdata):

        if event != cv.EVENT_LBUTTONDOWN:
            return

        modifier = flags & (ALT_KEY + SHIFT_KEY)

        self._flood_mask[:] = 0
        cv.floodFill(
            self.img,
            self._flood_mask,
            (x, y),
            0,
            self.tolerance,
            self.tolerance,
            self._flood_fill_flags,
        )
        flood_mask = self._flood_mask[1:-1, 1:-1].copy()

        if modifier == (ALT_KEY + SHIFT_KEY):
            self.mask = cv.bitwise_and(self.mask, flood_mask)
        elif modifier == SHIFT_KEY:
            self.mask = cv.bitwise_or(self.mask, flood_mask)
        elif modifier == ALT_KEY:
            self.mask = cv.bitwise_and(self.mask, cv.bitwise_not(flood_mask))
        else:
            self.mask = flood_mask

        self._update()

    def _update(self):
        """Updates an image in the already drawn window."""
        viz = self.img.copy()
        contours = _find_exterior_contours(self.mask)
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
        print("Press [q] or [esc] to close the window.")
        while True:
            self.img = _fits2img(self.fits, self.treshold)  # todo maybe merge _fits2img and treshold callback
            self._update()
            k = cv.waitKey(10) & 0xFF
            if k in (ord("q"), ord("\x1b")):
                cv.destroyWindow(self.name)
                break


file = 'hmi.M_720s_nrt.20180820_090000_TAI.fits'
hmi = np.nan_to_num(sunpy.map.Map(file).data, nan=-999999)

window = SelectionWindow(hmi)
window.show()

# todo write '__main__'

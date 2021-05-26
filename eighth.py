# -*- coding: cp1251 -*-
__Author__ = 'Gamza'
"""custom MagicWand lib
"""
import numpy as np
import sunpy.map
import sunpy.data.sample
import cv2 as cv

# variables
SHIFT_KEY = cv.EVENT_FLAG_SHIFTKEY
ALT_KEY = cv.EVENT_FLAG_ALTKEY
# file = 'hmi.M_720s_nrt.20180820_090000_TAI.fits'
# file = '20000712_fd_M_96m_01d.2749.0006.fits'
file = '20040725_fd_M_96m_01d.4223.0008.fits'


# functions
def _find_exterior_contours(img):
    """magicWand function todo write something here"""
    ret = cv.findContours(img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if len(ret) == 2:
        return ret[0]
    elif len(ret) == 3:
        return ret[1]
    raise Exception("Check the signature for `cv.findContours()`.")


def _fits_processing(file, resize=0, nans=-999999):
    """returns 2d np.array
    """
    array = np.nan_to_num(sunpy.map.Map(file).data, nan=nans)  # todo maybe without nans

    def scale(arr, nR, nC):
        nR0 = len(arr)  # source number of rows
        nC0 = len(arr[0])  # source number of columns
        return np.asarray([[arr[int(round(nR0 * r / nR))][int(round(nC0 * c / nC))]
                            for c in range(nC)] for r in range(nR)])

    if resize:
        nR = int(round(len(array) * resize))
        nC = int(round(len(array[0]) * resize))
        array = scale(array, nR, nC)
    return array


def _arr2rgb(arr, treshold=0.5, strong=True, resize=False):
    """converts numpy array to red-and-blue color image
    :param arr:
    :param treshold:
    :param strong:
    :param resize:
    :return:
    """
    if strong:
        r = np.copy(arr)
        r[r > treshold] = 255  # positive regions
        r[abs(r) <= treshold] = 147  # neutral regions
        r[r < -treshold] = 0  # negative regions

        g = np.copy(arr)
        g[abs(g) > treshold] = 0  # positive or negative regions
        g[abs(g) <= treshold] = 147  # neutral regions

        b = np.copy(arr)
        b[b > treshold] = 0  # positive regions
        b[abs(b) <= treshold] = 147  # neutral regions
        b[b < -treshold] = 255  # negative regions
    # else:
    #     # todo todo else
    #     r = np.copy(arr)
    #     r[r < -treshold] = -127
    #     r[abs(r) <= treshold] = 0
    #     r[r > treshold] *= 127 / (3 * np.std(r[r > treshold]))
    #     r[r >= 3 * np.std(r[r > treshold])] = 127
    #     # r[abs(r) <= treshold] = 0
    #     # r[r > treshold] *= 127 / r.max()
    #     # # r[r > treshold] = 128 + (r[r > treshold] * 127 / (3 * np.std(r[r > treshold])))
    #     # r[r < -treshold] *= 127 / r.min()
    #     # # r[r < -treshold] = 0 if strong else 128 - (r[r > treshold] * 127 / (3 * np.std(r[r > treshold])))
    #     r += 128
    #
    #     g = np.copy(arr)
    #     g[abs(g) > treshold] = 128 - (g[abs(g) > treshold] * 127 / (g[abs(g) > treshold]))
    #     # g[abs(g) > treshold] = 0 if strong else 128 - (g[abs(g) > treshold] * 127 / (3 * np.std(g[g > treshold])))
    #     g[abs(g) <= treshold] = 128
    #
    #     b = np.copy(arr)
    #     b[b < -treshold] = 128 - (b[b < -treshold] * 127 / (3 * np.std(b[b < -treshold])))
    #     b[abs(b) <= treshold] = 127
    #     b[b > treshold] = 128 - (b[b > treshold] * 127 / (3 * np.std(b[b > treshold])))

    image = np.rint(np.stack([b, g, r], axis=2)).astype(np.uint8)
    if type(resize) == (int or float):
        image = cv.resize(image, (int(image.shape[0] / resize), int(image.shape[0] / resize)))
    elif type(resize) == tuple and len(resize) == 2:
        image = cv.resize(image, resize)
    return image


class SelectionWindow:
    def __init__(self, fits, name="Magic Wand Selector", connectivity=4, tolerance=32, treshold=10):
        self.name = name
        # self.img = img
        self.treshold = treshold
        self.img = _arr2rgb(fits, treshold=self.treshold)
        h, w = self.img.shape[:2]
        self.fits = fits
        self.mask = np.zeros((h, w), dtype=np.uint8)  # maybe you?
        self.flux = []
        self._flood_mask = np.zeros((h + 2, w + 2), dtype=np.uint8)
        self._flood_fill_flags = (
                connectivity | cv.FLOODFILL_FIXED_RANGE | cv.FLOODFILL_MASK_ONLY | 255 << 8
        )  # 255 << 8 tells to fill with the value 255
        cv.namedWindow(self.name)
        self.tolerance = (tolerance,) * 3
        cv.createTrackbar('treshold', self.name, treshold, 63, self._treshold_callback)
        cv.createTrackbar("Tolerance", self.name, tolerance, 255, self._trackbar_callback)
        cv.setMouseCallback(self.name, self._mouse_callback)

    def _treshold_callback(self, pos):
        self.treshold = pos

    def _trackbar_callback(self, pos):
        self.tolerance = (pos,) * 3

    def _mouse_callback(self, event, x, y, flags, *userdata):

        if event != cv.EVENT_LBUTTONDOWN:
            return
        print('lon: ', x, 'lat: ', y)
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
        flux_mask = self.fits.copy()
        # global flux
        contours = _find_exterior_contours(self.mask)
        if len(contours) != 0:
            # new_flux = [flux_mask[i[0][0]][i[0][1]] for i in contours[0]]
            new_flux = [flux_mask[i[0][1]][i[0][0]] for i in contours[0]]
            if self.flux != new_flux:
                self.flux = new_flux
                print(np.rint(sum(self.flux)))

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
            self.img = _arr2rgb(self.fits, treshold=self.treshold)  # todo maybe merge _fits2img and treshold callback
            self._update()
            k = cv.waitKey(1000) & 0xFF
            if k in (ord("q"), ord("\x1b")):
                cv.destroyWindow(self.name)
                break


# hmi = np.nan_to_num(sunpy.map.Map(file).data, nan=-999999)
# hmi0 = _fits_processing(file)
# hmi1 = _fits_processing(file, resize=0.1)
hmi2 = _fits_processing(file, nans=np.nan)
# print(_arr2rgb(hmi2))

window = SelectionWindow(hmi2)
window.show()

# todo write '__main__'

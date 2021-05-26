import numpy as np


def smooth(I):

    J = I.copy()

    J[1:-1] = (J[1:-1] // 2 + J[:-2] // 4 + J[2:] // 4)
    J[:, 1:-1] = (J[:, 1:-1] // 2 + J[:, :-2] // 4 + J[:, 2:] // 4)

    return J


#simple image scaling to (nR x nC) size
def scale(im, nR, nC):
  nR0 = len(im)     # source number of rows
  nC0 = len(im[0])  # source number of columns
  return np.asarray([[im[int(nR0 * r / nR)][int(nC0 * c / nC)]
             for c in range(nC)] for r in range(nR)])




arr = np.random.random((10, 10)) * 100
smarr = smooth(arr)
scarr = scale(arr, 15, 15)
print('ui')


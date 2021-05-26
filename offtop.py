import numpy as np


class Robot:

    def __init__(self, coords):
        self.y = coords[0]
        self.x = coords[1]
        self.theroom = np.zeros([100, 100], dtype=int)
        self.theroom[self.y, self.x] = 1
        self.pathlog = [[(self.x, self.y)]]
        # self.pathlog.append(coords)

    def move(self, movement):
        self.theroom[self.y, self.x] = 0
        # print('start point: {}, {}'.format(self.y, self.x))
        movement = [a for a in movement]
        path = []
        # print(movement)
        for item in movement:
            path.append((self.x, self.y))
            # if (item == 'n' or 'N') and self.y > 0:
            if item == 'S' and self.y > 0:
                self.y -= 1
            if item == 'N' and self.y < 99:
                self.y += 1
            if item == 'W' and self.x > 0:
                self.x -= 1
            if item == 'E' and self.x < 99:
                self.x += 1
        path.append((self.x, self.y))
        self.pathlog.append(path)
        # print('end point: {}, {}'.format(self.y, self.x))
        self.theroom[self.y, self.x] = 1
        return self.x, self.y,

    def path(self):
        return self.pathlog[-1]
        # for path in self.pathlog:
        #     return path


r = Robot((0, 0))
print('****', *r.path())
print('***', r.move('NENW'))
print('****', *r.path())

# print(r.theroom)







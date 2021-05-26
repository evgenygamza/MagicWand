# -*- coding: cp1251 -*-
__Author__ = 'Gamza'


class Hui:
    def __init__(self, days_after_shaving, days_after_bath, active_days):
        self.volosatost = 2 * days_after_shaving
        self.aromat = 3 * days_after_bath * active_days


class NemutuiHui(Hui):
    def __init__(self, a, b, c):
        Hui.__init__(self, a, b, c)
        self.tvorog = True
        self.privlekatelnost = self.volosatost * self.aromat


vasilii = NemutuiHui(2, 3, 5)
print(vasilii.aromat, vasilii.volosatost, vasilii.tvorog, vasilii.privlekatelnost)

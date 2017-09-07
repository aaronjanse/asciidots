class Pos(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "<Pos({}, {})>".format(*self)

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        else:
            raise IndexError

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        else:
            raise IndexError

    def __add__(self, other):
        return Pos(self.x + other[0], self.y + other[1])
    __radd__ = __add__

    def __neg__(self):
        return Pos(-self.x, -self.y)

    def __sub__(self, other):
        return self + -other

    def __rsub__(self, other):
        return -self + other

    def __eq__(self, other):
        return self.x == other[0] and self.y == other[1]

    @property
    def row(self):
        return self.y

    @row.setter
    def row(self, value):
        self.y = value

    @property
    def col(self):
        return self.x

    @col.setter
    def col(self, value):
        self.x = value


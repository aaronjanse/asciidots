class Pos(tuple):
    def __new__(cls, x, y=None):
        if y is None:
            return tuple.__new__(cls, x)
        return tuple.__new__(cls, (x, y))

    def __str__(self):
        return "<Pos({}, {})>".format(*self)

    def __add__(self, other):
        return Pos(self[0] + other[0], self[1] + other[1])

    __radd__ = __add__

    def __neg__(self):
        return Pos(-self[0], -self[1])

    def __sub__(self, other):
        return Pos(self[0] - other[0], self[1] - other[1])

    def __rsub__(self, other):
        return Pos(other[0] - self[0], other[1] - self[1])

    def __hash__(self):
        return super().__hash__()

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    @property
    def row(self):
        return self[1]

    @property
    def col(self):
        return self[0]

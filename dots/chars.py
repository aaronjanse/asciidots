class Char(str):
    def __init__(self, value):
        self.value = value

    def isDot(self):
        return False

    def isOper(self):
        return False

    def isCurlyOper(self):
        return False

    def isSquareOper(self):
        return False

    def isWarp(self):
        return False

    def isLibWarp(self):
        return False

    def isSingletonLibWarp(self):
        return False

    def isSingletonLibReturnWarp(self):
        return False


class DotChar(Char):
    def isDot(self):
        return True


class OperChar(Char):
    def __init__(self, value):
        super().__init__(value)

        self.func = None

    def isOper(self):
        return True

    def calc(self, x, y):
        if self.func is None:
            function_dict = {
                '+': (lambda x, y: x + y),
                '-': (lambda x, y: x - y),
                '*': (lambda x, y: x * y),
                '/': (lambda x, y: x / y),
                '÷': (lambda x, y: x / y),
                '^': (lambda x, y: x ** y),
                '%': (lambda x, y: x % y),

                'o': (lambda x, y: x | y),
                'x': (lambda x, y: x ^ y),
                '&': (lambda x, y: x & y),
                '!': (lambda x, y: x != y),

                '=': (lambda x, y: x == y),
                '≠': (lambda x, y: x != y),
                '>': (lambda x, y: x > y),
                '≥': (lambda x, y: x >= y),
                '<': (lambda x, y: x < y),
                '≤': (lambda x, y: x <= y)
            }

            self.func = function_dict[self]

        return self.func(x, y)


class CurlyOperChar(OperChar):
    def isCurlyOper(self):
        return True


class SquareOperChar(OperChar):
    def isSquareOper(self):
        return True


class WarpChar(Char):
    def __init__(self, value):
        super().__init__(value)

        self._teleporter_id = None
        self._dest_loc = None

    def isWarp(self):
        return True

    def set_id(self, teleporter_id):
        self._teleporter_id = teleporter_id

    def get_id(self):
        return self._teleporter_id

    def set_dest_loc(self, pos):
        self._dest_loc = pos

    def get_dest_loc(self):
        return self._dest_loc


class LibWarpChar(WarpChar):
    def isLibWarp(self):
        return True


# NB: Singleton refers to the library written in ascii dots, not the class itself!
class SingletonLibWarpChar(LibWarpChar):
    def isSingletonLibWarp(self):
        return True


# NB: Singleton refers to the library written in ascii dots, not the class itself!
class SingletonLibReturnWarpChar(SingletonLibWarpChar):
    def isSingletonLibReturnWarp(self):
        return True

    def set_dest_loc(self, pos):
        raise Exception("SingletonLibReturnWarpChar: cannot set destination; use the stack!")

    def get_dest_loc(self):
        raise Exception("SingletonLibReturnWarpChar: unknown destination; use the stack!")

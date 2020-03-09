from __future__ import division

class Char(str):
    def __init__(self, value):
        self.value = value

    def isdecimal(self):
        return self >= '0' and self <= '9'

    def isDot(self):
        return False

    def isTilde(self):
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
        super(OperChar, self).__init__(value)

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
                '^': (lambda x, y: x ** y),
                '%': (lambda x, y: x % y),

                'o': (lambda x, y: x | y),
                'x': (lambda x, y: x ^ y),
                '&': (lambda x, y: x & y),
                '!': (lambda x, y: x != y),

                '=': (lambda x, y: x == y),
                '>': (lambda x, y: x > y),
                'G': (lambda x, y: x >= y),
                '<': (lambda x, y: x < y),
                'L': (lambda x, y: x <= y)
            }

            unicode_substitutions = {
                '\u00F7': '/',
                '\u2260': '!',
                '\u2264': 'L',
                '\u2265': 'G'
            }

            if self in unicode_substitutions:
                raise RuntimeError('Unicode operator used. Operator "{}" should be replaced with "{}".'.format(self, unicode_substitutions[self]))

            self.func = function_dict[self]

        return self.func(x, y)


class CurlyOperChar(OperChar):
    def isCurlyOper(self):
        return True


class SquareOperChar(OperChar):
    def isSquareOper(self):
        return True

class TildeChar(Char):
    def __init__(self, value):
        assert value == "~"
        super(TildeChar, self).__init__(value)
        self.inverted = False

    def set_inverted(self, inverted):
        self.inverted = inverted

    def isTilde(self):
        return True


class WarpChar(Char):
    def __init__(self, value):
        super(WarpChar, self).__init__(value)

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


class LibInnerWarpChar(LibWarpChar):
    def isLibWarp(self):
        return True

    def set_dest_loc(self, pos):
        raise Exception(
            "SingletonLibReturnWarpChar: cannot set destination; use the stack!")

    def get_dest_loc(self):
        raise Exception(
            "SingletonLibReturnWarpChar: unknown destination; use the stack!")


class LibOuterWarpChar(LibWarpChar):
    def isLibWarp(self):
        return True


# NB: Singleton refers to the library written in ascii dots, not the class itself!
class SingletonLibWarpChar(LibWarpChar):
    def isSingletonLibWarp(self):
        return True


# NB: Singleton refers to the library written in ascii dots, not the class itself!
class SingletonLibOuterWarpChar(SingletonLibWarpChar):
    pass


# NB: Singleton refers to the library written in ascii dots, not the class itself!
class SingletonLibInnerWarpChar(LibInnerWarpChar, SingletonLibWarpChar):
    pass

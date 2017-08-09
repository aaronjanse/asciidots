def moveFirstTime(func):
    def _decorator(self, *args, **kwargs):
        # print('self is {0}'.format(self))
        # print(self.a)
        if not self.hasRun:
            self.moveParent()
            self.hasRun = True
        else:
            func(self, *args, **kwargs)
    return _decorator


class State(object):
    def __init__(self, parent):
        self.parent = parent
        self.hasRun = False

        self.isWaiting = False

    def next(self, char):
        self.parent.callbacks.on_finish()
        raise Exception("State Next Method Not Implemented!")

    def run(self, char):
        self.parent.callbacks.on_finish()
        raise Exception("State Run Method Not Implemented!")

    def setParentState(self, newState):
        self.parent.state = newState(self.parent)

    def moveParent(self, direction=None):
        if direction is None:
            direction = self.parent.dir

        self.parent.x += direction[0]
        self.parent.y += direction[1]

    # define lambda like this: lambda x, y: (your func or constant)
    def changeParentDirWithFunc(self, newDirLambda):
        self.parent.dir = list(newDirLambda(*self.parent.dir))

    def setParentDir(self, newDirX, newDirY):
        self.parent.dir = [newDirX, newDirY]

    def isParentMovingVert(self):
        return self.parent.dir[1] != 0

    def isParentMovingHoriz(self):
        return self.parent.dir[0] != 0

    def __str__(self):
        return type(self).__name__

    def isDeadState(self):
        return False

    def isTwoDotState(self):
        return False


class TravelState(State):
    def next(self, char):
        if char == ' ':
            return DeadState(self.parent)
        elif char == '~':
            return TildeState(self.parent)
        elif char == '#':
            return ValueState(self.parent)
        elif char == '@':
            return AddressState(self.parent)
        elif char == '$':
            return PrintState(self.parent)
        elif char in ('[', ']',) and self.isParentMovingVert():
            return DeadState(self.parent)
        elif char in ('{', '}',) and self.isParentMovingVert():
            return DeadState(self.parent)
        elif char.isSquareOper():
            return OperSquareState(self.parent)
        elif char.isCurlyOper():
            return OperCurlyState(self.parent)
        elif char == '-' and self.isParentMovingVert():
            return DeadState(self.parent)
        elif char == '|' and self.isParentMovingHoriz():
            return DeadState(self.parent)
        elif char == ':' and self.parent.value == 0:
            return DeadState(self.parent)
        elif char == ';' and self.parent.value == 1:
            return DeadState(self.parent)
        else:
            return self

    def run(self, char):
        if char == '\\':
            self.changeParentDirWithFunc(lambda x, y: (y, x))
        elif char == '/':
            self.changeParentDirWithFunc(lambda x, y: (-y, -x))
        elif char == '(':
            self.setParentDir(1, 0)
        elif char == ')':
            self.setParentDir(-1, 0)
        elif char == '>':
            if self.isParentMovingVert():
                self.setParentDir(1, 0)
        elif char == '<':
            if self.isParentMovingVert():
                self.setParentDir(-1, 0)
        elif char == '^':
            if self.isParentMovingHoriz():
                self.setParentDir(0, -1)
        elif char == 'v':
            if self.isParentMovingHoriz():
                self.setParentDir(0, 1)
        elif char == '*':
            for xoffset in range(-1, 1 + 1):
                for yoffset in range(-1, 1 + 1):
                    # If the abs vals of both offsets are one, skip
                    if not abs(xoffset) ^ abs(yoffset):
                        continue

                    if [-xoffset, -yoffset] == list(self.parent.dir)\
                            or [xoffset, yoffset] == list(self.parent.dir):
                        continue

                    abs_offset_x = self.parent.x + xoffset
                    abs_offset_y = self.parent.y + yoffset

                    if self.parent.world.doesLocExist(abs_offset_x, abs_offset_y)\
                            and self.parent.world.getCharAt(abs_offset_x, abs_offset_y) != ' ':

                        from .dot import Dot
                        new_dot = Dot(x=self.parent.x, y=self.parent.y, world=self.parent.world, callbacks=self.parent.callbacks, func_to_create_dots=self.parent.func_to_create_dots, func_to_get_dots=self.parent.func_to_get_dots, address=self.parent.address, value=self.parent.value, direction=[xoffset, yoffset], state=TravelState, stack=self.parent.stack[:])

                        # new_dot.state.moveParent()

                        self.parent.func_to_create_dots(new_dot)
        elif char.isSingletonLibReturnWarp():
            (self.parent.x, self.parent.y) = self.parent.stack.pop()
        elif char.isWarp():
            if char.isSingletonLibWarp():
                self.parent.stack.append((self.parent.x, self.parent.y))

            (self.parent.x, self.parent.y) = char.get_dest_loc()
        else:
            pass

        self.moveParent()


class ValueState(State):
    def __init__(self, parent):
        State.__init__(self, parent)
        self.firstDigit = True

    def next(self, char):
        if not char.isdecimal() and char != '?':
            return TravelState(self.parent)
        else:
            return self

    @moveFirstTime
    def run(self, char):
        if char.isdecimal():
            if self.firstDigit:
                self.parent.value = int(char)
                self.firstDigit = False
            else:
                self.parent.value = self.parent.value * 10 + int(char)
        elif char == '?':
            self.parent.value = int(self.parent.callbacks.get_input())

        self.moveParent()


class AddressState(State):
    def __init__(self, parent):
        State.__init__(self, parent)
        self.firstDigit = True

    def next(self, char):
        if char in ('[', ']', '{', '}'):
            if self.isParentMovingVert():
                return DeadState(self.parent)
            else:
                return self
        elif char.isSquareOper():
            return OperSquareState(self.parent, addressMode=True)
        elif char.isCurlyOper():
            return OperCurlyState(self.parent, addressMode=True)
        elif char.isdecimal() or char == '?':
            return self
        elif char == '~':
            return TildeState(self.parent, addressMode=True)
        else:
            return TravelState(self.parent)

    @moveFirstTime
    def run(self, char):
        if char.isdecimal():
            if self.firstDigit:
                self.parent.address = int(char)
                self.firstDigit = False
            else:
                self.parent.address = self.parent.address * 10 + int(char)
        elif char == '?':
            self.parent.address = int(self.parent.callbacks.get_input())
        else:
            pass

        self.moveParent()


class PrintState(State):
    def __init__(self, parent):
        State.__init__(self, parent)
        self.newline = True
        self.asciiMode = False

    def next(self, char):
        if char in ('$', '_', 'a', '#', '@',):
            return self
        elif char == ' ':
            return DeadState(self.parent)
        elif char == '"':
            return PrintDoubleQuoteState(self.parent, newline=self.newline)
        elif char == "'":
            return PrintSingleQuoteState(self.parent, newline=self.newline)
        else:
            return TravelState(self.parent)

    @moveFirstTime
    def run(self, char):
        if char == '_':
            self.newline = False
        elif char == 'a':
            self.asciiMode = True
        elif char == '#':
            data = self.parent.value

            if self.asciiMode:
                data = chr(data)

            if self.newline:
                data = str(data) + '\n'

            self.parent.callbacks.on_output(data)
        elif char == '@':
            data = self.parent.address

            if self.asciiMode:
                data = chr(data)

            if self.newline:
                data = str(data) + '\n'

            self.parent.callbacks.on_output(data)
        else:
            pass

        self.moveParent()


class PrintDoubleQuoteState(State):
    def __init__(self, parent, newline=True):
        State.__init__(self, parent)
        self.newline = newline
        self.pendingExit = False

    def next(self, char):
        if self.pendingExit:
            return TravelState(self.parent)
        else:
            return self

    @moveFirstTime
    def run(self, char):
        if char == '"':
            if self.newline:
                self.parent.callbacks.on_output('\n')

            self.pendingExit = True
        else:
            self.parent.callbacks.on_output(char)

        self.moveParent()


class PrintSingleQuoteState(State):
    def __init__(self, parent, newline=True):
        State.__init__(self, parent)
        self.newline = newline
        self.pendingExit = False

    def next(self, char):
        if self.pendingExit:
            return TravelState(self.parent)
        else:
            return self

    @moveFirstTime
    def run(self, char):
        if char == "'":
            if self.newline:
                self.parent.callbacks.on_output('\n')

            self.pendingExit = True
        else:
            self.parent.callbacks.on_output(char)

        self.moveParent()


class TwoDotState(State):
    def __init__(self, parent, isMaster, addressMode=None):
        State.__init__(self, parent)

        if addressMode is None:
            self.addressMode = False
        else:
            self.addressMode = addressMode

        self.isMaster = isMaster(self)

        self.isWaiting = True
        self.age = 0

    def isTwoDotState(self):
        return True

    def next(self, char):
        if self.isWaiting:
            return self
        else:
            return TravelState(self.parent)

    def run(self, char):
        if self.isMaster:
            # We want to find the companion dot that has been waiting the
            # longest. At the same time, if we find a dot that is also a master
            # that has been waiting longer than this, keep on waiting
            candidate_index = -1
            best_candidate_age = -1

            ready_to_operate = False

            self_x = self.parent.x
            self_y = self.parent.y

            for idx, dot in enumerate(self.parent.func_to_get_dots()):
                if dot.x == self_x and dot.y == self_y and dot.state.isTwoDotState():
                    if dot.state.isMaster:
                        if dot.state.age > self.age:
                            ready_to_operate = False
                            break
                    else:
                        age = dot.state.age
                        if age > best_candidate_age:
                            candidate_index = idx
                            ready_to_operate = True

            if ready_to_operate:
                candidate = self.parent.func_to_get_dots()[candidate_index]

                if candidate.state.addressMode:
                    candidate_par = candidate.address
                else:
                    candidate_par = candidate.value

                if self.addressMode:
                    self_par = self.parent.address
                else:
                    self_par = self.parent.value

                self.doOperation(char, self_par, candidate_par, candidate,
                                 candidate_index)

                candidate.state = DeadState(candidate)

                # FIXME: This is not a good idea...
                self.parent.state = TravelState(self.parent)

                self.moveParent()

                self.isWaiting = False
            else:
                self.isWaiting = True
        else:
            self.isWaiting = True

        self.age += 1

    def doOperation(self, candidate, candidate_idx):
        raise Exception("DoOperation not implemented!")


class OperState(TwoDotState):
    def __init__(self, parent, isMaster, addressMode=False):
        TwoDotState.__init__(self, parent, isMaster, addressMode)

    def doOperation(self, char, self_par, candidate_par, candidate,
                    candidate_idx):
        result = char.calc(self_par, candidate_par) * 1
        # NOTE: the `* 1` converts a boolean into an integer

        if self.addressMode:
            self.parent.address = result
        else:
            self.parent.value = result


class OperSquareState(OperState):
    def __init__(self, parent, addressMode=False):
        OperState.__init__(self, parent,
                           isMaster=(lambda self: self.isParentMovingVert()),
                           addressMode=addressMode)


class OperCurlyState(OperState):
    def __init__(self, parent, addressMode=False):
        OperState.__init__(self, parent,
                           isMaster=(lambda self: self.isParentMovingHoriz()),
                           addressMode=addressMode)


class TildeState(TwoDotState):
    def __init__(self, parent, addressMode=False):
        TwoDotState.__init__(self, parent,
                             isMaster=(lambda self: self.isParentMovingHoriz()),
                             addressMode=addressMode)

    def doOperation(self, char, self_par, candidate_par, candidate,
                    candidate_idx):
        if candidate_par != 0:
            self.setParentDir(0, -1)


class DeadState(State):
    def next(self, char):
        return self

    def run(self, char):
        pass

    def isDeadState(self):
        return True

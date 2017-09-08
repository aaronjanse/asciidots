from dots.constants import DIRECTIONS, RIGHT, LEFT, UP, DOWN
from dots.vector import Pos


def move_first_time(func):
    def _decorator(self, *args, **kwargs):
        # print('self is {0}'.format(self))
        # print(self.a)
        if not self.hasRun:
            self.move_parent()
            self.hasRun = True
        else:
            func(self, *args, **kwargs)

    return _decorator


class State(object):
    def __init__(self, parent):
        """
        Describe the state of a dot with functions to get to the next state ofthe state machine.

        :param dots.dot.Dot parent:
        """

        self.env = parent.env
        self.parent = parent

        self.hasRun = False
        self.isWaiting = False
        self.id_mode = False

    def next(self, char):
        self.env.io.on_finish()
        raise Exception("State Next Method Not Implemented!")

    def run(self, char):
        self.env.io.on_finish()
        raise Exception("State Run Method Not Implemented!")

    def set_parent_state(self, new_state):
        self.parent.state = new_state(self.parent)

    def move_parent(self):
        self.parent.move()

    # define lambda like this: lambda dir: (your func or constant)
    def change_parent_dir_with_func(self, newDirLambda):
        self.parent.dir = newDirLambda(self.parent.dir)

    def set_parent_direction(self, direction):
        """
        Sets the direction of the dot

        :param dots.vector.Pos direction: The new direction of the dot.
        """

        self.parent.dir = direction

    def is_moving_vert(self):
        """True if the dot is moving verticaly."""
        return self.parent.dir.y != 0

    def is_moving_horiz(self):
        """True if the dot is moving horizontally."""
        return self.parent.dir.x != 0

    def __str__(self):
        return type(self).__name__

    def is_dead(self):
        return False

    def is_two_dots(self):
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
            return IdState(self.parent)
        elif char == '$':
            return PrintState(self.parent)
        elif char in '[]' and self.is_moving_vert():
            return DeadState(self.parent)
        elif char in '{}' and self.is_moving_vert():
            return DeadState(self.parent)
        elif char.isSquareOper():
            return OperSquareState(self.parent)
        elif char.isCurlyOper():
            return OperCurlyState(self.parent)
        elif char == '-' and self.is_moving_vert():
            return DeadState(self.parent)
        elif char == '|' and self.is_moving_horiz():
            return DeadState(self.parent)
        elif char == ':' and self.parent.value == 0:
            return DeadState(self.parent)
        elif char == ';' and self.parent.value == 1:
            return DeadState(self.parent)
        else:
            return self

    def run(self, char):
        if char == '\\':
            self.change_parent_dir_with_func(lambda dir: Pos(dir.y, dir.x))
        elif char == '/':
            self.change_parent_dir_with_func(lambda dir: Pos(-dir.y, -dir.x))
        elif char == '(':
            self.set_parent_direction(RIGHT)
        elif char == ')':
            self.set_parent_direction(LEFT)
        elif char == '>':
            if self.is_moving_vert():
                self.set_parent_direction(RIGHT)
        elif char == '<':
            if self.is_moving_vert():
                self.set_parent_direction(LEFT)
        elif char == '^':
            if self.is_moving_horiz():
                self.set_parent_direction(UP)
        elif char == 'v':
            if self.is_moving_horiz():
                self.set_parent_direction(DOWN)
        elif char == '*':
            for dir in DIRECTIONS:

                if self.parent.dir in (dir, -dir):
                    continue

                next_pos = self.parent.pos + dir

                if self.env.world.does_loc_exist(next_pos) and self.env.world.get_char_at(next_pos) != ' ':
                    from .dot import Dot

                    new_dot = Dot(self.env, self.parent.pos, id_=self.parent.id,
                                  value=self.parent.value, direction=dir, state=TravelState,
                                  stack=self.parent.stack[:])

                    # new_dot.state.move_parent()
                    self.env.dots.append(new_dot)
        elif char.isSingletonLibReturnWarp():
            self.parent.pos = self.parent.stack.pop()
        elif char.isWarp():
            if char.isSingletonLibWarp():
                self.parent.stack.append(self.parent.pos)

            self.parent.pos = char.get_dest_loc()
        else:
            pass

        self.move_parent()


class ValueState(State):
    def __init__(self, parent):
        super().__init__(parent)
        self.first_digit = True

    def next(self, char):
        if not char.isdecimal() and char != '?':
            return TravelState(self.parent)
        else:
            return self

    @move_first_time
    def run(self, char):
        if char.isdecimal():
            if self.first_digit:
                self.parent.value = int(char)
                self.first_digit = False
            else:
                self.parent.value = self.parent.value * 10 + int(char)
        elif char == '?':
            self.parent.value = int(self.env.io.get_input())

        self.move_parent()


class IdState(State):
    def __init__(self, parent):
        super().__init__(parent)
        self.first_digit = True

    def next(self, char):
        if char in '[]{}':
            if self.is_moving_vert():
                return DeadState(self.parent)
            else:
                return self
        elif char.isSquareOper():
            return OperSquareState(self.parent, id_mode=True)
        elif char.isCurlyOper():
            return OperCurlyState(self.parent, id_mode=True)
        elif char.isdecimal() or char == '?':
            return self
        elif char == '~':
            return TildeState(self.parent, id_mode=True)
        else:
            return TravelState(self.parent)

    @move_first_time
    def run(self, char):
        if char.isdecimal():
            if self.first_digit:
                self.parent.id = int(char)
                self.first_digit = False
            else:
                self.parent.id = self.parent.id * 10 + int(char)
        elif char == '?':
            self.parent.id = int(self.env.io.get_input())
        else:
            pass

        self.move_parent()


class PrintState(State):
    def __init__(self, parent):
        super().__init__(parent)
        self.newline = True
        self.asciiMode = False

    def next(self, char):
        if char in '$_a#@':
            return self
        elif char == ' ':
            return DeadState(self.parent)
        elif char == '"':
            return PrintDoubleQuoteState(self.parent, newline=self.newline)
        elif char == "'":
            return PrintSingleQuoteState(self.parent, newline=self.newline)
        else:
            return TravelState(self.parent)

    @move_first_time
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

            self.env.io.on_output(data)
        elif char == '@':
            data = self.parent.id

            if self.asciiMode:
                data = chr(data)

            if self.newline:
                data = str(data) + '\n'

            self.env.io.on_output(data)
        else:
            pass

        self.move_parent()


class PrintDoubleQuoteState(State):
    def __init__(self, parent, newline=True):
        super().__init__(parent)
        self.newline = newline
        self.pendingExit = False

    def next(self, char):
        if self.pendingExit:
            return TravelState(self.parent)
        else:
            return self

    @move_first_time
    def run(self, char):
        if char == '"':
            if self.newline:
                self.env.io.on_output('\n')

            self.pendingExit = True
        else:
            self.env.io.on_output(char)

        self.move_parent()


class PrintSingleQuoteState(State):
    def __init__(self, parent, newline=True):
        super().__init__(parent)
        self.newline = newline
        self.pendingExit = False

    def next(self, char):
        if self.pendingExit:
            return TravelState(self.parent)
        else:
            return self

    @move_first_time
    def run(self, char):
        if char == "'":
            if self.newline:
                self.env.io.on_output('\n')

            self.pendingExit = True
        else:
            self.env.io.on_output(char)

        self.move_parent()


class TwoDotState(State):
    def __init__(self, parent, isMaster, id_mode=None):
        super().__init__(parent)

        if id_mode is None:
            self.id_mode = False
        else:
            self.id_mode = id_mode

        self.isMaster = isMaster(self)

        self.isWaiting = True
        self.age = 0

    def is_two_dots(self):
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

            for idx, dot in enumerate(self.env.dots):
                if dot.pos == self.parent.pos and dot.state.is_two_dots():
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
                candidate = self.env.dots[candidate_index]

                if candidate.state.id_mode:
                    candidate_par = candidate.id
                else:
                    candidate_par = candidate.value

                if self.id_mode:
                    self_par = self.parent.id
                else:
                    self_par = self.parent.value

                self.do_operation(char, self_par, candidate_par, candidate,
                                  candidate_index)

                candidate.state = DeadState(candidate)

                # FIXME: This is not a good idea...
                self.parent.state = TravelState(self.parent)

                self.move_parent()

                self.isWaiting = False
            else:
                self.isWaiting = True
        else:
            self.isWaiting = True

        self.age += 1

    def do_operation(self, *args, **kwargs):
        raise Exception("DoOperation not implemented!")


class OperState(TwoDotState):
    def __init__(self, parent, isMaster, id_mode=False):
        TwoDotState.__init__(self, parent, isMaster, id_mode)

    def do_operation(self, char, self_par, candidate_par, candidate, candidate_idx):
        result = char.calc(self_par, candidate_par) * 1
        # NOTE: the `* 1` converts a boolean into an integer

        if self.id_mode:
            self.parent.id = result
        else:
            self.parent.value = result


class OperSquareState(OperState):
    def __init__(self, parent, id_mode=False):
        OperState.__init__(self, parent,
                           isMaster=(lambda self: self.is_moving_vert()),
                           id_mode=id_mode)


class OperCurlyState(OperState):
    def __init__(self, parent, id_mode=False):
        OperState.__init__(self, parent,
                           isMaster=(lambda self: self.is_moving_horiz()),
                           id_mode=id_mode)


class TildeState(TwoDotState):
    def __init__(self, parent, id_mode=False):
        TwoDotState.__init__(self, parent,
                             isMaster=(lambda self: self.is_moving_horiz()),
                             id_mode=id_mode)

    def do_operation(self, char, self_par, candidate_par, candidate,
                     candidate_idx):
        if candidate_par != 0:
            self.set_parent_direction(UP)


class DeadState(State):
    def next(self, char):
        return self

    def run(self, char):
        pass

    def is_dead(self):
        return True

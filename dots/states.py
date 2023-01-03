from __future__ import division

from dots.constants import DIRECTIONS, RIGHT, LEFT, UP, DOWN
from dots.exceptions import DotsExit
from dots.vector import Pos
from dots.chars import SingletonLibInnerWarpChar


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


def autodetect_next_state(dot, char):
    return TravelState(dot).next(char)


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
        raise Exception("State Next Method Not Implemented!")

    def run(self, char):
        raise Exception("State Run Method Not Implemented!")

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
    # codebeat:disable[BLOCK_NESTING]
    def next(self, char):
        if char == ' ':
            return DeadState(self.parent)
        elif char == '&' and not char.isOper():
            return ExitState(self.parent)
        elif char.isTilde():
            return TildeState(self.parent)
        elif char == '#':
            return ValueState(self.parent)
        elif char == '@':
            return IdState(self.parent)
        elif char == '$':
            return PrintState(self.parent)
        elif char in '[]{}' and self.is_moving_vert():
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

    # codebeat:disable[BLOCK_NESTING]
    def run(self, char):
        if char == '\\':
            self.change_parent_dir_with_func(lambda dir: Pos(dir.y, dir.x))
        elif char == '/':
            self.change_parent_dir_with_func(lambda dir: Pos(-dir.y, -dir.x))
        elif char == '(':
            self.set_parent_direction(RIGHT)
        elif char == ')':
            self.set_parent_direction(LEFT)
        elif char == '>' and self.is_moving_vert():
            self.set_parent_direction(RIGHT)
        elif char == '<' and self.is_moving_vert():
            self.set_parent_direction(LEFT)
        elif char == '^' and self.is_moving_horiz():
            self.set_parent_direction(UP)
        elif char == 'v' and self.is_moving_horiz():
            self.set_parent_direction(DOWN)
        elif char == '*':
            for dir in DIRECTIONS:
                if self.parent.dir in (dir, -dir):
                    continue

                next_pos = self.parent.pos + dir

                if self.env.world.does_loc_exist(next_pos) and self.env.world.get_char_at(next_pos) != ' ':
                    new_dot = self.parent.copy()
                    new_dot.dir = dir
                    new_dot.move()

                    self.env.dots.append(new_dot)
        elif isinstance(char, SingletonLibInnerWarpChar):
            if len(self.parent.stack) == 0:
                raise RuntimeError('Dot tried to exit library it never entered.\nThis is likely caused by a dot spawned inside a library trying to teleport out.\n' + str(self.parent))

            self.parent.pos = self.parent.stack.pop()
        elif char.isWarp():
            if char.isSingletonLibWarp():
                self.parent.stack.append(self.parent.pos)

            char_dest_loc = char.get_dest_loc()
            if char_dest_loc is not None:
                self.parent.pos = char.get_dest_loc()
            else:
                raise RuntimeError('Warp "{}" has no destination'.format(char))

        self.move_parent()


class ValueState(State):
    def __init__(self, parent):
        super(ValueState, self).__init__(parent)
        self.first_digit = True
        self.asciiMode = False
        self.neg = False

    def next(self, char):
        if char.isdecimal() or char in 'a?':
            return self
        else:
            return autodetect_next_state(self.parent, char)

    @move_first_time
    def run(self, char):
        if char.isdecimal():
            if self.first_digit:
                self.parent.value = int(char)
                self.first_digit = False
            else:
                self.parent.value = self.parent.value * 10 + int(char)
        elif char == 'a':
            self.asciiMode = True
        elif char == '?':
            try:
                val = self.env.io.get_input(ascii_char=self.asciiMode)
                if val is None:
                    # Wait until the next tick to ask again
                    return
                if self.asciiMode:
                    self.parent.value = ord(val) if len(val) > 0 else -1
                else:
                    self.parent.value = int(val)
            except ValueError:
                self.parent.value = 0

        self.move_parent()


class IdState(State):
    def __init__(self, parent):
        super(IdState, self).__init__(parent)
        self.first_digit = True
        self.asciiMode = False
        self.setting_id = False

    def next(self, char):
        if char.isdecimal() or char in 'a?':
            return self
        elif self.setting_id:
            return autodetect_next_state(self.parent, char)
        elif char in '[]{}':
            if self.is_moving_vert():
                return DeadState(self.parent)
            else:
                return self
        elif char.isSquareOper():
            return OperSquareState(self.parent, id_mode=True)
        elif char.isCurlyOper():
            return OperCurlyState(self.parent, id_mode=True)
        elif char == '~':
            return TildeState(self.parent, id_mode=True)
        elif char == ':':
            if self.parent.id == 0:
                return DeadState(self.parent)
            else:
                return TravelState(self.parent)
        elif char == ';':
            if self.parent.id == 1:
                return DeadState(self.parent)
            else:
                return TravelState(self.parent)
        else:
            return autodetect_next_state(self.parent, char)

    @move_first_time
    def run(self, char):
        if char.isdecimal():
            self.setting_id = True
            if self.first_digit:
                self.parent.id = int(char)
                self.first_digit = False
            else:
                self.parent.id = self.parent.id * 10 + int(char)
        elif char == 'a':
            self.asciiMode = True
        elif char == '?':
            try:
                val = self.env.io.get_input(ascii_char=self.asciiMode)
                if self.asciiMode:
                    self.parent.id = ord(val) if len(val) > 0 else -1
                else:
                    self.parent.id = int(val)
            except ValueError:
                self.parent.id = 0
        else:
            pass

        self.move_parent()


class PrintState(State):
    def __init__(self, parent, newline=True):
        super(PrintState, self).__init__(parent)
        self.newline = newline
        self.asciiMode = False
        self.pendingExit = False

    def next(self, char):
        if self.pendingExit:
            return autodetect_next_state(self.parent, char)
        elif char in '$_a#@':
            return self
        elif char == ' ':
            return DeadState(self.parent)
        elif char == '"':
            return PrintDoubleQuoteState(self.parent, newline=self.newline)
        elif char == "'":
            return PrintSingleQuoteState(self.parent, newline=self.newline)
        else:
            return autodetect_next_state(self.parent, char)

    @move_first_time
    def run(self, char):
        if char == '_':
            self.newline = False
        elif char == 'a':
            self.asciiMode = True
        elif char == '#':
            data = self.parent.value
            if data % 1 == 0:
                data = int(data)

            if self.asciiMode:
                data = chr(data)

            if self.newline:
                data = str(data) + '\n'

            self.env.io.on_output(data)
            self.pendingExit = True
        elif char == '@':
            data = self.parent.id
            if data % 1 == 0:
                data = int(data)

            if self.asciiMode:
                data = chr(data)

            if self.newline:
                data = str(data) + '\n'

            self.env.io.on_output(data)
            self.pendingExit = True
        else:
            pass

        self.move_parent()


class PrintDoubleQuoteState(PrintState):
    def __init__(self, parent, newline=True):
        super(PrintDoubleQuoteState, self).__init__(parent, newline)
        self.text_buffer = ''

    def next(self, char):
        if self.pendingExit:
            return autodetect_next_state(self.parent, char)
        else:
            return self

    @move_first_time
    def run(self, char):
        if char == '"':
            if self.newline:
                self.text_buffer += '\n'

            self.env.io.on_output(self.text_buffer)

            self.pendingExit = True
        else:
            self.text_buffer += char

        self.move_parent()


class PrintSingleQuoteState(PrintState):

    def next(self, char):
        if self.pendingExit:
            return autodetect_next_state(self.parent, char)
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
        super(TwoDotState, self).__init__(parent)

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
            return autodetect_next_state(self.parent, char)

    def run(self, char):
        self.isWaiting = True

        if self.isMaster:
            # We want to find the companion dot that has been waiting the
            # longest. At the same time, if we find a dot that is also a master
            # that has been waiting longer than this, keep on waiting

            wait_here = [d for  d in self.env.dots if d.pos == self.parent.pos and d.state.is_two_dots()]
            masters_here = [d for d in wait_here if d.state.isMaster]
            other_here = [d for d in wait_here if not d.state.isMaster]

            if masters_here and other_here:
                oldest_master = max(masters_here, key=lambda d:d.state.age)
                oldest_other = max(other_here, key=lambda d:d.state.age)

                if oldest_master is self.parent:
                    candidate = oldest_other

                    if candidate.state.id_mode:
                        candidate_par = candidate.id
                    else:
                        candidate_par = candidate.value

                    if self.id_mode:
                        self_par = self.parent.id
                    else:
                        self_par = self.parent.value

                    self.do_operation(char, self_par, candidate_par, candidate)

                    candidate.state = DeadState(candidate)

                    # FIXME: This is not a good idea...
                    self.parent.state = TravelState(self.parent)
                    self.move_parent()

                    self.isWaiting = False

        self.age += 1

    def do_operation(self, *args, **kwargs):
        raise Exception("DoOperation not implemented!")


class OperState(TwoDotState):
    def __init__(self, parent, isMaster, id_mode=False):
        TwoDotState.__init__(self, parent, isMaster, id_mode)

    def do_operation(self, char, self_par, candidate_par, candidate):
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

    def do_operation(self, char, self_par, candidate_par, candidate):
        if (candidate_par != 0) ^ char.inverted:
            self.set_parent_direction(UP)


class DeadState(State):
    def next(self, char):
        return self

    def run(self, char):
        pass

    def is_dead(self):
        return True


class ExitState(State):
    def next(self, char):
        raise DotsExit

    def run(self, char):
        raise DotsExit

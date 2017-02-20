#!/usr/bin/env python

from time import sleep

from decimal import Decimal

import sys
import json
from itertools import chain

import signal

# TODO: import this only when needed (i.e. when debugging is enabled)
import os




def signal_handler(signal, frame):
        exit_progam(0)


signal.signal(signal.SIGINT, signal_handler)

# access like this: world[y][x]
# notice how y is before x
# world_raw = []
# world = []
#
# dots = []
#
# new_dots = []
#
# teleporters = []

compat_debug = '-w' in sys.argv[1:]

debug = '-d' in sys.argv[1:] or compat_debug
step_manual = debug

quick_debug = '-q' in sys.argv[1:]

debug_lines = 40
if '-l' in sys.argv[1:]:
    debug_lines = int(sys.argv[sys.argv[1:].index('-l')+2])

silent_output = '-s' in sys.argv[1:]

if '-a' in sys.argv[1:]:
    step_manual = False
    step_speed = float(sys.argv[sys.argv.index('-a') + 1])

tick_max_limit = None

if '-t' in sys.argv[1:]:
    tick_max_limit = int(sys.argv[sys.argv.index('-t') + 1])

cycle_max_limit = None

if '-c' in sys.argv[1:]:
    cycle_max_limit = int(sys.argv[sys.argv.index('-c') + 1])

if debug and not compat_debug:
    import curses
    stdscr = curses.initscr()

    curses.start_color()

    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)

    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)

    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)

    curses.noecho()

    curses.curs_set(False)

    win_program = curses.newwin(debug_lines, curses.COLS - 1, 0, 0)

    logging_pad = curses.newpad(1000, curses.COLS - 1)


logging_loc = 0
logging_x = 1


def log_output(string="", newline=True):
    if silent_output:
        return

    if debug and not compat_debug:
        global logging_loc
        global logging_x

        logging_pad.addstr(logging_loc, logging_x, str(string))
        logging_pad.refresh(logging_loc - min(logging_loc, curses.LINES -
                            debug_lines - 1), 0, debug_lines, 0,
                            curses.LINES - 1, curses.COLS - 1)

        if newline:
            logging_x = 1
            logging_loc += 1
        else:
            logging_x += len(string)
    else:
        if newline:
            print(string)
        else:
            print(string, end='')


operators = (
    '+',
    '-',
    '*',
    '/',
    '%',
    '^',
    '!',
    '&',
    'o',
    '=',
    '<',
    '>',
    '≤',
    '≥',
    '~',
    'x'
)

enc_opers_square = []
enc_opers_curly = []

dot_synonyms = []


def quit_curses():
    if debug and not compat_debug:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()

        curses.endwin()


def exit_progam(exit_code=0):
    quit_curses()

    sys.exit(exit_code)


operator_two_way_map = {}

for idx, oper in enumerate(operators):
    ch_square = chr(128 + idx)
    ch_curly = chr(128 + idx + len(operators) + 1)

    operator_two_way_map[ch_square] = oper
    operator_two_way_map[ch_curly] = oper

    operator_two_way_map[oper] = (ch_square, ch_curly,)

    enc_opers_square.append(ch_square)
    enc_opers_curly.append(ch_curly)


# see http://stackoverflow.com/a/21785167/6496271
def curses_input(stdscr, r, c, prompt_string):
    curses.echo()
    stdscr.addstr(r, c, str(prompt_string), curses.A_REVERSE)
    stdscr.refresh()
    input = ""

    while len(input) <= 0:
        input = stdscr.getstr(r + 1, c, 20)

    return input


def get_input(text):
    if debug and not compat_debug:
        return curses_input(stdscr, curses.LINES - 2, 2, text)
    else:
        if not sys.stdin.isatty():
            return input("")
        else:
            return input(text)


def render(inter_inst):

    if compat_debug:
        os.system('cls' if os.name == 'nt' else 'clear')

    d_l = []
    for idx in reversed(range(len(inter_inst.dots))):
        d = inter_inst.dots[idx]
        if not d.is_dead:
            d_l.append((d.x, d.y))

    special_char = False

    last_blank = False

    display_y = 0

    for y in range(len(inter_inst.world_raw)):
        if display_y > debug_lines-1:
            break

        if len(''.join(inter_inst.world_raw[y]).rstrip()) < 1:
            if last_blank:
                continue
            else:
                last_blank = True
        else:
            last_blank = False

        for x in range(len(inter_inst.world_raw[y])):
            char = inter_inst.world_raw[y][x]

            if compat_debug:
                char_selected = (x, y) in d_l
                if char_selected:
                    sys.stdout.write("\033[91m")

                sys.stdout.write(char)

                if char_selected:
                    sys.stdout.write("\033[0;0m")

                continue

            replaced_char = False

            if char in inter_inst.lib_alias_chars:
                char = "§"
                replaced_char = True
            elif ord(char) > 127:
                char = "◊"
                replaced_char = True

            if (x, y) in d_l:
                win_program.addstr(display_y, x, char, curses.color_pair(1))
            elif inter_inst.world[y][x] in inter_inst.teleporters:
                win_program.addstr(display_y, x, char, curses.color_pair(2))
            elif replaced_char:
                win_program.addstr(display_y, x, char, curses.color_pair(3))
            elif char in '#@~':
                win_program.addstr(display_y, x, char, curses.color_pair(4))
            else:
                win_program.addstr(display_y, x, char)

        if compat_debug:
            sys.stdout.write("\n")

        display_y += 1

    if not compat_debug:
        win_program.refresh()

    # sys.stdout.flush()


def exists(inter_inst, x, y):
    return x >= 0 and y >= 0 and y < len(inter_inst.world)and x < len(inter_inst.world[y])


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

    def next(self, char):
        quit_curses()
        raise Exception("State Next Method Not Implemented!")

    def run(self, char):
        quit_curses()
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
        elif char in enc_opers_square:
            return OperSquareState(self.parent)
        elif char in enc_opers_curly:
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
            for xoffset in range(-1, 1+1):
                for yoffset in range(-1, 1+1):
                    # If the abs vals of both offsets are one, skip
                    if not abs(xoffset) ^ abs(yoffset):
                        continue

                    if [-xoffset, -yoffset] == self.parent.dir\
                            or [xoffset, yoffset] == self.parent.dir:
                        continue

                    abs_offset_x = self.parent.x + xoffset
                    abs_offset_y = self.parent.y + yoffset

                    if exists(self.parent.inter_inst, abs_offset_x, abs_offset_y)\
                            and self.parent.inter_inst.world[abs_offset_y][abs_offset_x] != ' ':

                        pars = 'x={x}, y={y}, address={address}, value={value}, \
                                direction={dir}, state={state}, stack={stack}'\
                                .format(**self.parent.__dict__)

                        new_dot = eval('Dot(self.parent.inter_inst, '+pars+')')

                        new_dot.dir = [xoffset, yoffset]

                        new_dot.state.moveParent()

                        self.parent.inter_inst.new_dots.append(new_dot)
        elif char in self.parent.inter_inst.lib_alias_chars:
            self.parent.stack.append((self.parent.x, self.parent.y))

            dir_list = ([1, 0], [0, -1], [-1, 0], [0, 1])

            goto_idx = dir_list.index(self.parent.dir)

            dest_char = self.parent.inter_inst.lib_alias_chars[char]['goto_chars'][goto_idx]

            found = False

            for y in range(len(self.parent.inter_inst.world)):
                if self.parent.inter_inst.world[y][0] == '%':
                    continue

                for x in range(len(self.parent.inter_inst.world[y])):
                    if "``" in self.parent.inter_inst.world[y][:x]:
                        break

                    if x == self.parent.x and y == self.parent.y:
                        continue

                    cell = self.parent.inter_inst.world[y][x]

                    if cell == dest_char:
                        self.parent.x = x
                        self.parent.y = y
                        found = True
                        break

                if found:
                    break

        elif char in self.parent.inter_inst.teleporters:
            found = False

            for y in range(len(self.parent.inter_inst.world)):
                if self.parent.inter_inst.world[y][0] == '%':
                    continue

                for x in range(len(self.parent.inter_inst.world[y])):
                    if "``" in self.parent.inter_inst.world[y][:x]:
                        break

                    if x == self.parent.x and y == self.parent.y:
                        continue

                    cell = self.parent.inter_inst.world[y][x]

                    if cell == char:
                        self.parent.x = x
                        self.parent.y = y
                        found = True
                        break

                if found:
                    break
        else:
            for lib_main_alias in self.parent.inter_inst.lib_alias_chars:
                lib_gotos = self.parent.inter_inst.lib_alias_chars[lib_main_alias]['goto_chars']

                if char in lib_gotos:
                    (self.parent.x, self.parent.y) = self.parent.stack.pop()

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
            self.parent.value = int(get_input('?: '))

        self.moveParent()


class AddressState(State):
    def __init__(self, parent):
        State.__init__(self, parent)
        self.firstDigit = True

    def next(self, char):
        if char in ('[', ']', '{', '}') and self.isParentMovingVert():
            return DeadState(self.parent)
        elif char in self.parent.inter_inst.enc_opers_square:
            return OperSquareState(self.parent, addressMode=True)
        elif char in self.parent.inter_inst.enc_opers_curly:
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
            self.parent.address = int(input('?: '))
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

            self.parent.inter_inst.log_output(data, newline=self.newline)
        elif char == '@':
            data = self.parent.address

            if self.asciiMode:
                data = chr(data)

            self.inter_inst.parent.log_output(data, newline=self.newline)
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
                self.parent.inter_inst.log_output()

            self.pendingExit = True
        else:
            self.parent.inter_inst.log_output(char, newline=False)

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
                self.parent.inter_inst.log_output()

            self.pendingExit = True
        else:
            self.parent.inter_inst.log_output(char, newline=False)

        self.moveParent()


class TwoDotState(State):
    def __init__(self, parent, isMaster, addressMode=False):
        State.__init__(self, parent)

        self.addressMode = addressMode

        self.isMaster = isMaster(self)

        self.isWaiting = True
        self.age = 0

    operation_map = {
        '+': (lambda x, y: x + y),
        '-': (lambda x, y: x - y),
        '*': (lambda x, y: x * y),
        '/': (lambda x, y: x / y),
        '^': (lambda x, y: x ** y),
        'o': (lambda x, y: x | y),
        'x': (lambda x, y: x ^ y),
        '&': (lambda x, y: x & y),
        '!': (lambda x, y: x != y),
        '=': (lambda x, y: x == y),
        '>': (lambda x, y: x > y),
        '≥': (lambda x, y: x >= y),
        '<': (lambda x, y: x < y),
        '≤': (lambda x, y: x <= y),
        '%': (lambda x, y: x % y)
    }

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

            for idx, dot in enumerate(self.parent.inter_inst.dots):
                if dot.x == self.parent.x and dot.y == self.parent.y\
                        and isinstance(dot.state, TwoDotState):
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
                candidate = self.parent.inter_inst.dots[candidate_index]

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

                # print(self)

                # self.moveParent()

                self.isWaiting = False

        self.age += 1
        self.parent.breakLoop = True

        def doOperation(self, candidate, candidate_idx):
            raise Exception("DoOperation not implemented!")


class OperState(TwoDotState):
    def __init__(self, parent, isMaster, addressMode=False):
        TwoDotState.__init__(self, parent, isMaster, addressMode)

    def doOperation(self, char, self_par, candidate_par, candidate,
                    candidate_idx):
        plaintext_char = operator_two_way_map[char]
        result = self.operation_map[plaintext_char](self_par, candidate_par)

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
        # else:
            # self.setParentDir(1, 0)


class DeadState(State):
    def next(self, char):
        return self

    def run(self, char):
        pass


class Dot:
    def __init__(self, inter_inst,  x, y, address=None, value=None, direction=None,
                 state=None, stack=None):

        self.inter_inst = inter_inst

        self.breakLoop = False

        if stack is None:
            self.stack = []
        else:
            self.stack = stack

        self.x = x
        self.y = y

        if address is None:
            self.address = 0
        else:
            self.address = address

        if value is None:
            self.value = 0
        else:
            self.value = value

        self.is_dead = False

        if direction is None:
            if self.x > 0:
                if(self.inter_inst.world[self.y][self.x - 1] in ('-', '/', '\\', '>', '<')):
                    self.dir = [-1, 0]

            if self.x + 1 < len(self.inter_inst.world[self.y]):
                if(self.inter_inst.world[self.y][self.x + 1] in ('-', '/', '\\', '>', '<')):
                    self.dir = [+1, 0]

            if self.y > 0 and self.x < len(self.inter_inst.world[self.y - 1]):
                if(self.inter_inst.world[self.y - 1][self.x] in ('|', '/', '\\', '>', '<')):
                    self.dir = [0, -1]

            if self.y + 1 < len(self.inter_inst.world) and self.x < len(self.inter_inst.world[self.y + 1]):
                if(self.inter_inst.world[self.y + 1][self.x] in ('|', '/', '\\', '>', '<')):
                    self.dir = [0, +1]

            if not hasattr(self, 'dir'):
                # print("error: cannot determine dot location")
                # print(self)
                # print(self.inter_inst.world_raw)

                self.parent.inter_inst.log_output("error: dot cannot determine location...")
                self.parent.inter_inst.log_output("x: {x}, y: {y}".format(self.x, self.y))

                self.dir = [0, 0]
                self.is_dead = True
                self.state = DeadState(self)
                # exit_progam(1)
            else:
                self.x += self.dir[0]
                self.y += self.dir[1]
        else:
            self.dir = direction

        if state is None:
            self.state = TravelState(self)
        else:
            self.state = state(self)

    def __repr__(self):
        return 'Dot(x={x}, y={y}, address={address}, value={value}, \
                direction={dir}, state={state}, stack={stack})'\
                .format(**self.__dict__)

    def tick(self):
        past_locations = []
        while(True):
            if debug:
                render(self.inter_inst)

                if step_manual:
                    if not (quick_debug and len(self.stack) > 0):
                        try:
                            if compat_debug:
                                input("")
                            else:
                                stdscr.getch()
                        except SyntaxError:
                            pass
                elif step_speed != 0:
                    sleep(step_speed)

            coords = (self.x, self.y,)
            if coords in past_locations:
                return

            if not exists(self.inter_inst, self.x, self.y):
                self.is_dead = True
                return

            char = self.inter_inst.world[self.y][self.x]

            if char == '&':
                if not debug:
                    # exit_progam(0)
                    self.inter_inst.dead = True

                self.state = DeadState
                return

            self.state = self.state.next(char)

            self.state.run(char)

            if type(self.state) is DeadState:
                self.is_dead = True
                return

            if self.breakLoop:
                self.breakLoop = False
                break

class InterInstance(object):
    def __init__(self, log_func=None):
        self.dead = False

        self.raw_chars = []

        self.lib_id_counter = 0

        self.lib_alias_chars = {}

        self.program_dir = ""

        self.offset = (128 + len(operators) * 2 + 1) + 10

        self.main_lines = []

        self.libs = {}

        self.world_raw = []
        self.world = []

        self.dots = []

        self.new_dots = []

        self.teleporters = []

        self.logging_loc = 0
        self.logging_x = 1

        if log_func is None:
            self.log_output = self.log_output_default
        else:
            self.log_output = log_func

    def log_output_default(self, string="", newline=True):
        if silent_output:
            return

        if debug and not compat_debug:
            # global logging_loc
            # global logging_x

            logging_pad.addstr(self.logging_loc, self.logging_x, str(string))
            logging_pad.refresh(self.logging_loc - min(self.logging_loc, curses.LINES -
                                debug_lines - 1), 0, debug_lines, 0,
                                curses.LINES - 1, curses.COLS - 1)

            if newline:
                self.logging_x = 1
                self.logging_loc += 1
            else:
                self.logging_x += len(string)
        else:
            if newline:
                print(string)
            else:
                print(string, end='')

def find_and_process_libs(inter_inst, raw_lines, is_main, this_file_name=""):
    # global all_lib_files
    # global lib_id_counter
    # global program_dir
    # global offset
    # global lib_alias_chars
    # global main_lines
    # global libs

    include_files = []
    include_aliases = []

    lines = []

    for line in raw_lines:
        if line[:2] == '%!':
            pieces = line[2:].split()

            include_files.append(pieces[0])
            include_aliases.append(pieces[1])
        else:
            lines.append(line)

    for idx, file_name in enumerate(include_files):
        if file_name not in inter_inst.libs:
            if os.path.isfile(os.path.join(inter_inst.program_dir, file_name)):
                new_path = os.path.join(inter_inst.program_dir, file_name)
            else:
                interpreter_dir = os.path.dirname(os.path.realpath(__file__))
                new_path = os.path.join(interpreter_dir, "libs", file_name)

            with open(new_path.split('%', 1)[0], 'r') as lib_file:
                next_lines = lib_file.readlines()

            alias_char = chr(inter_inst.offset)

            inter_inst.libs[file_name] = {'id': inter_inst.lib_id_counter, 'alias': alias_char}

            # Find all the library tp chars
            tp_chars = []
            for line in next_lines:
                if line[:2] == '%+':
                    tp_chars = list(line[2:].rstrip())
                    break

            inter_inst.lib_alias_chars[alias_char] = {"file": file_name, "goto_chars": []}

            # Replace all library tp chars with special unique chars
            for idx_1, char in enumerate(tp_chars):
                replacement = chr(inter_inst.offset + idx_1 + 1)

                next_lines = [i.replace(char, replacement) for i in next_lines]

                inter_inst.lib_alias_chars[alias_char]['goto_chars'].append(replacement)

            inter_inst.libs[file_name]['lines'] = next_lines

            inter_inst.lib_id_counter += 5

            inter_inst.offset += 5
            find_and_process_libs(inter_inst, next_lines, False, this_file_name=file_name)

        # Replace all alias chars with their universal counterparts
        if is_main:
            inter_inst.main_lines = [li.replace(include_aliases[idx],
                          inter_inst.libs[file_name]['alias']) if li[0] != '%' else li
                          for li in inter_inst.main_lines]
        else:
            inter_inst.libs[this_file_name]['lines'] = [li.replace(include_aliases[idx],
                                             inter_inst.libs[file_name]['alias'])
                                             for li in
                                             inter_inst.libs[this_file_name]['lines']]

class DotsInterpreter(object):
    def __init__(self, program_lines, p_dir='.', logging_func=None):
        # global dots
        # global teleporters
        # global raw_chars
        # global main_lines
        # global program_dir
        # global world
        # global world_raw
        # global offset
        # global main_lines
        # global new_dots
        # global interpreter_instance


        # if logging_func is None:
        #     logging_func = log_output

        self.interpreter_instance = InterInstance(logging_func)

        self.interpreter_instance.program_dir = p_dir

        self.interpreter_instance.main_lines = program_lines

        find_and_process_libs(self.interpreter_instance, self.interpreter_instance.main_lines, True)

        for library_file in self.interpreter_instance.libs:
            self.interpreter_instance.main_lines.extend(self.interpreter_instance.libs[library_file]['lines'])

        lines = self.interpreter_instance.main_lines

        for line in lines:
            if line[0] == '%':
                if line[1] == '.':
                    dot_synonyms = list(line[2:].rstrip())
                elif line[1] == '$':
                    self.interpreter_instance.raw_chars = list(line[2:].rstrip())
                    self.interpreter_instance.teleporters = [chr(idx + self.interpreter_instance.offset)
                                   for idx, c in enumerate(self.interpreter_instance.raw_chars)]
                continue

            data = ' ' + line.split("``", 1)[0].rstrip() + ' '

            data = data.replace('.', '•')

            self.interpreter_instance.world_raw.append(list(data))

            data = data.replace('•', '.')
            data = data.replace('÷', '/')

            for idx, rc in enumerate(self.interpreter_instance.raw_chars):
                data = data.replace(rc, self.interpreter_instance.teleporters[idx])

            for idx, oper in enumerate(operators):
                data = data.replace("[{0}]".format(oper),
                                    "[{0}]".format(chr(128 + idx)))
                data = data.replace("{" + oper + "}", "{" + "{0}".format(
                                    chr(128 + idx + len(operators) + 1) + "}"))

            self.interpreter_instance.world.append(list(data))

        longest_line = max((len(l), i) for i, l in enumerate(self.interpreter_instance.world))[0]

        self.interpreter_instance.world = [' '*longest_line] + self.interpreter_instance.world
        self.interpreter_instance.world_raw = [' '*longest_line] + self.interpreter_instance.world_raw

        for idx, line in reversed(list(enumerate(self.interpreter_instance.world))):
            self.interpreter_instance.world[idx] += (' ' * (longest_line - len(line) + 1))
            self.interpreter_instance.world_raw[idx] += (' ' * (longest_line - len(line) + 1))

        try:
            special_dots = [[]] * len(dot_synonyms)
        except Exception:
            special_dots = []
            dot_synonyms = []

        for y in range(len(self.interpreter_instance.world)):
            if self.interpreter_instance.world[y][0] == '%':
                continue

            for x in range(len(self.interpreter_instance.world[y])):
                cell = self.interpreter_instance.world[y][x]

                if cell == '.':
                    self.interpreter_instance.dots.append(Dot(self.interpreter_instance, x, y))
                elif cell in dot_synonyms:
                    special_dots[dot_synonyms.index(cell)].append(Dot(self.interpreter_instance, x, y))

        self.interpreter_instance.dots.extend(reversed(list(chain.from_iterable(special_dots))))

        self.needsShutdown = False
        #
        # # End program
        # return 0

    def terminate(self):
        self.needsShutdown = True

    def run(self):
        tick_cnt = 0
        cycle_cnt = 0

        while len(self.interpreter_instance.dots) > 0 and not self.needsShutdown and not self.interpreter_instance.dead:
            self.interpreter_instance.new_dots = []

            dot_locations = []

            for idx in reversed(range(len(self.interpreter_instance.dots))):
                d = self.interpreter_instance.dots[idx]

                d.tick()

                if d.is_dead:
                    del self.interpreter_instance.dots[idx]
                else:
                    dot_locations.append((d.x, d.y))

                tick_cnt += 1
                if tick_max_limit is not None and tick_cnt > tick_max_limit:
                    return  # Tick limit exceeded, so return/exit

            if len(self.interpreter_instance.new_dots) > 0:
                self.interpreter_instance.dots.extend(self.interpreter_instance.new_dots)

            self.interpreter_instance.new_dots = []

            cycle_cnt += 1
            if cycle_max_limit is not None and cycle_cnt > cycle_max_limit:
                return  # Tick limit exceeded, so return/exit

            new_list = []

            for d in self.interpreter_instance.dots:
                if d not in new_list:
                    new_list.append(d)

            self.interpreter_instance.dots = new_list[:]

# def main


if __name__ == '__main__':
    try:
        file_path = sys.argv[1]

        prog_dir = os.path.dirname(os.path.abspath(file_path))

        with open(file_path, 'r') as file:
            program_lines = file.readlines()

        interpreter = DotsInterpreter(program_lines, prog_dir)

        interpreter.run()

        exit_progam(0)
    except Exception:
        quit_curses()
        raise

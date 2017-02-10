#!/usr/bin/env python

from time import sleep

from decimal import Decimal


import signal
import sys
def signal_handler(signal, frame):
        # print('You pressed Ctrl+C!')
        exit_progam(0)
signal.signal(signal.SIGINT, signal_handler)
# print('Press Ctrl+C')
# signal.pause()

import sys
import json
from itertools import chain

# TODO: import this only when needed (i.e. when debugging is enabled)
import os

# access like this: world[y][x]
# notice how y is before x
world_raw = []
world = []

dots = []

new_dots = []

teleporters = []

compat_debug = '-w' in sys.argv[1:]

debug = '-d' in sys.argv[1:] or compat_debug
step_manual = debug



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

    curses.noecho()

    curses.curs_set(False)

    win_program = curses.newwin(40, curses.COLS - 1, 0, 0)

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
        logging_pad.refresh( logging_loc-min(logging_loc, curses.LINES - 41),0, 40,0, curses.LINES - 1,curses.COLS - 1)

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
    'v',
    '=',
    '<',
    '>',
    '≤',
    '≥',
    '~',
)
operators_eval = (
    '+',
    '-',
    '*',
    '/',
    '%',
    '^',
    '!=',
    '&',
    '|',
    '==',
    '<',
    '>',
    '<=',
    '>=',
    '~',
)
enc_opers_square = []
enc_opers_curly = []

dot_synonyms = []

def exit_progam(exit_code=0):
    if debug and not compat_debug:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()

        curses.endwin()

    sys.exit(exit_code)

for idx, oper in enumerate(operators):
    enc_opers_square.append(chr(128 + idx))
    enc_opers_curly.append(chr(128 + idx + len(operators) + 1))


# see http://stackoverflow.com/a/21785167/6496271
def curses_input(stdscr, r, c, prompt_string):
    curses.echo()
    stdscr.addstr(r, c, str(prompt_string), curses.A_REVERSE)
    stdscr.refresh()
    # while True:
    #     try:
    input = ""

    while len(input) <= 0:
        input = stdscr.getstr(r + 1, c, 20)
            # break
        # except:
        #     pass


    return input  #       ^^^^  reading input at next line

def render():

    if compat_debug:
        os.system('cls' if os.name == 'nt' else 'clear')

    d_l = []
    for idx in reversed(range(len(dots))):
        d = dots[idx]
        if not d.is_dead:
            d_l.append((d.x, d.y))

    # effect = curses.color_pair(1)
    # effect = curses.A_STANDOUT

    special_char = False

    for y in range(len(world_raw)):
        if y > 40-1:
            break

        for x in range(len(world_raw[y])):
            char = world_raw[y][x]

            if compat_debug:
                char_selected = (x, y) in d_l
                if char_selected:
                    sys.stdout.write("\033[91m")

                sys.stdout.write(char)

                if char_selected:
                    sys.stdout.write("\033[0;0m")

                continue

            if char in lib_alias_chars:
                char = "§"
                # special_char = True
                # effect = curses.A_STANDOUT
            elif ord(char) > 127:
                char = "◊"
                # special_char = True
                # effect = curses.A_STANDOUT

            if (x, y) in d_l:
                # if special_char:
                #     win_program.addch(y, x, ord(char), curses.A_STANDOUT)
                # else:
                win_program.addch(y, x, ord(char), curses.color_pair(1))

                # special_char = False

                # win_program.addch(y, x, ord(char), curses.A_STANDOUT)

                # effect = curses.color_pair(1)
            else:
                win_program.addch(y, x, char)



            # sys.stdout.write(char)
            # sys.stdout.write("\033[0;0m")
        if compat_debug:
            sys.stdout.write("\n")

    if not compat_debug:
        win_program.refresh()

    # sys.stdout.flush()

def exists(x, y):
    return x >= 0 and y >= 0 and y < len(world)and x < len(world[y])


class dot:
    # @profile
    def __init__(self, _x, _y, _dir=None, _data=None):
        self.map_handlers()

        self.stack = []

        self.x = _x
        self.y = _y
        if _data is None:
            self.data = {'value': 0, 'address': 0}
        else:
            self.data = _data

        self.selected = None

        self.last_char_int = False

        self.is_dead = False

        self.is_printing = False
        self.in_quotes = False

        self.waiting = False

        self.waiting_for = 0

        if _dir is None:
            if self.x > 0:
                if(world[self.y][self.x - 1] in ('-', '/', '\\', '>', '<')):
                    self.dir = [-1, 0]

            if self.x + 1 < len(world[self.y]):
                if(world[self.y][self.x + 1] in ('-', '/', '\\', '>', '<')):
                    self.dir = [+1, 0]

            if self.y > 0 and self.x < len(world[self.y - 1]):
                if(world[self.y - 1][self.x] in ('|', '/', '\\', '>', '<')):
                    self.dir = [0, -1]

            if self.y + 1 < len(world) and self.x < len(world[self.y + 1]):
                if(world[self.y + 1][self.x] in ('|', '/', '\\', '>', '<')):
                    self.dir = [0, +1]
        else:
            self.dir = _dir

        if not hasattr(self, 'dir'):
            print("error: cannot determine dot location")
            print(self)
            print(world_raw)
            exit_progam(1)

    def __repr__(self):
        return json.dumps({'data': self.data,
                           'x': self.x,
                           'y': self.y,
                           'dir': self.dir,
                           'waiting': self.waiting,
                           'waiting_for': self.waiting_for,
                           'selected': self.selected})
    def __eq__(self, other):
        return str(self) == str(other)
    def __hash__(self):
        return hash(('data',
                     str(self.data),
                     'x',
                     self.x,
                     'y',
                     self.y,
                     'dir',
                     str(self.dir),
                     'waiting',
                     self.waiting,
                     'waiting_for',
                     self.waiting_for,
                     'selected',
                     self.selected))

    def increment_others(self):
        for d in dots:
            if d.x == self.x and d.y == self.y and d.waiting:
                d.waiting_for += 1

    def map_handlers(self):
        self.char_handler_dict = {
            '&': self.handle_and,
            '-': self.handle_dash,
            '{': self.handle_bracket,
            '}': self.handle_bracket,
            '[': self.handle_bracket,
            ']': self.handle_bracket,
            '|': self.handle_pipe,
            '+': self.handle_plus,
            ' ': self.handle_space,
            '\\': self.handle_backslash,
            '/': self.handle_forwardslash,
            '@': self.handle_atsymbol,
            '#': self.handle_poundsymbol,
            '?': self.handle_question,
            '(': self.handle_left_paren,
            ')': self.handle_right_paren,
            '>': self.handle_gt_symbol,
            '<': self.handle_lt_symbol,
            '*': self.handle_asterisk,
            '~': self.handle_tilde
        }

    def handle_printing(self, char):
        if self.in_quotes:
            if char == '"':
                log_output()
                self.in_quotes = False
                self.is_printing = False
            else:
                if char == '#':
                    log_output(self.data['value'], newline=False)
                elif char == '@':
                    log_output(self.data['address'], newline=False)
                else:
                    log_output(char, newline=False)

            return True
        else:
            if char == '#':
                log_output(self.data['value'], newline=True)
                return True
            elif char == '@':
                log_output(self.data['address'], newline=True)
                return True
            elif char == '"':
                self.in_quotes = True
                return True
            elif char == ' ':
                self.is_dead = True
                return True
            else:
                self.is_printing = False
                return False

    def handle_digit(self, number):
        if self.selected is not None:
            if self.last_char_int:
                self.data[self.selected] = self.data[self.selected] * 10 + number
            else:
                self.data[self.selected] = number

    def handle_and(self):
        if not debug:
            exit_progam(0)

        self.waiting = True
        return True

    def handle_dash(self):
        if self.dir[1] != 0:
            self.is_dead = True
            return True

        self.selected = None

        return False

    def handle_bracket(self):
        if self.dir[1] != 0:
            self.is_dead = True
            return True

        return False

    def handle_pipe(self):
        if self.dir[0] != 0:
            self.is_dead = True
            return True

        self.selected = None

        return False

    def handle_plus(self):
        self.selected = None

        return False

    def handle_space(self):
        self.is_dead = True
        return True

    def handle_backslash(self):
        self.dir = [self.dir[1], self.dir[0]]

        self.selected = None
        return False

    def handle_forwardslash(self):
        self.dir = [-self.dir[1], -self.dir[0]]

        self.selected = None
        return False

    def handle_atsymbol(self):
        self.selected = 'address'
        return False

    def handle_poundsymbol(self):
        self.selected = 'value'
        return False

    def handle_question(self):
        if self.selected is not None:
            if debug and not compat_debug:
                user_in = int(curses_input(stdscr, curses.LINES - 2, 2, "Please input an {0}: ".format(self.selected)))
                self.data[self.selected] = user_in
            else:
                self.data[self.selected] = int(input(
                        "Please input an {0}: ".format(self.selected)))

    def handle_left_paren(self):
        self.dir = [1, self.dir[1]]

        self.selected = None
        return False

    def handle_right_paren(self):
        self.dir = [-1, self.dir[1]]

        self.selected = None
        return False

    def handle_gt_symbol(self):
        if self.dir[0] == 0:
            self.dir = [1, 0]
        else:
            self.dir = self.dir[:]

        self.selected = None
        return False

    def handle_lt_symbol(self):
        if self.dir[0] == 0:
            self.dir = [-1, 0]
        else:
            self.dir = self.dir[:]

        self.selected = None
        return False

    def handle_alias_char(self, char):
        self.stack.append((self.x, self.y))

        goto_idx = ([1, 0], [0, -1], [-1, 0], [0, 1],).index(self.dir)

        # print(goto_idx)

        dest_char = lib_alias_chars[char]['goto_chars'][goto_idx]

        # print(lib_alias_chars[char]['goto_chars'])

        for y in range(len(world)):
            if world[y][0] == '%':
                continue

            for x in range(len(world[y])):
                if "''" in world[y][:x]:
                    break;

                if x == self.x and y == self.y:
                    continue

                cell = world[y][x]

                if cell == dest_char:
                    self.x = x
                    self.y = y
                    return

    def handle_asterisk(self):
        new_dots_directions = []
        original = [-self.dir[0], -self.dir[1]]
        char_list = [
            '~',
            '/',
            '\\',
            '<',
            '>',
            '+',
            '#',
            '@',
            '0',
            '1',
            '2',
            '3',
            '4',
            '5',
            '6',
            '7',
            '8',
            '9',
            '(',
            ')',
            '}',
            '{',
            '[',
            ']']

        char_list.extend(enc_opers_square)
        char_list.extend(enc_opers_curly)
        if self.x > 0:
            if(world[self.y][self.x - 1] in char_list + ['-']):
                this_dir = [-1, 0]
                if this_dir != original:
                    new_dots_directions.append(this_dir)

        if self.x + 1 < len(world[self.y]):
            if(world[self.y][self.x + 1] in char_list + ['-']):
                this_dir = [+1, 0]
                if this_dir != original:
                    new_dots_directions.append(this_dir)

        if self.y > 0:
            if(world[self.y - 1][self.x] in char_list + ['|']):
                this_dir = [0, -1]
                if this_dir != original:
                    new_dots_directions.append(this_dir)

        if self.y + 1 < len(world):
            if(world[self.y + 1][self.x] in char_list + ['|']):
                this_dir = [0, +1]
                if this_dir != original:
                    new_dots_directions.append(this_dir)

        self.dir = new_dots_directions[0]
        for i in new_dots_directions[1:]:
            d = dot(
                self.x,
                self.y,
                _dir=i[:],
                _data=self.data.copy())
            d.stack = self.stack[:]
            dots.append(d)
            d.tick()

    def handle_tilde(self):
        if self.dir[0] == 0 and self.dir[1] == 0:
            return
        elif self.dir[0] == 0 and self.dir[1] == -1:
            self.dir = [0, 0]
            self.waiting = True

            self.increment_others()

            return

        elif self.dir[0] != 0 and self.dir[1] == 0:
            self.waiting = True

            self.increment_others()

            canidate_idx = None
            canidate = None
            canidate_rank = -1

            for idx, d in enumerate(dots):
                # If this is not first in line, return
                if d.x == self.x and d.y == self.y and d.dir[
                        0] != 0 and d.dir[1] == 0 and not d.is_dead:
                    if d.waiting_for > self.waiting_for:
                        return

                # This is part of finding the matching dot that is
                # first in line
                if d.x == self.x and d.y == self.y and d.dir[
                        0] == 0 and d.dir[1] == 0 and not d.is_dead:
                    if canidate_rank == -1 or d.waiting_for > canidate_rank:
                        canidate_idx = idx

            if canidate_idx is not None:
                canidate = dots[canidate_idx]

            if canidate is not None:
                if canidate.selected is None or canidate.selected == "value":
                    canidate_par = canidate.data.copy()['value']
                else:
                    canidate_par = canidate.data.copy()['address']

                canidate.is_dead = True

                self.waiting = False
                self.waiting_for = 0

                if canidate_par == 1:
                    self.dir = [0, -1]
                else:
                    pass

            return

        else:
            print('error!')
            print(self)

    def handle_oper_square(self, char):
        if self.dir[0] == 0 and self.dir[1] == 0:
            return
        elif self.dir[0] != 0 and self.dir[1] == 0:
            self.waiting = True

            self.increment_others()

            return
        elif self.dir[0] == 0 and self.dir[1] != 0:
            self.waiting = True

            self.increment_others()

            canidate = None
            canidate_idx = None
            canidate_rank = -1

            for idx, d in enumerate(dots):
                # If this is not first in line, return
                if d.x == self.x and d.y == self.y and d.dir[
                        0] == 0 and d.dir[1] != 0 and not d.is_dead:
                    if d.waiting_for > self.waiting_for:
                        return

                # This is part of finding the matching dot that is
                # first in line
                if d.x == self.x and d.y == self.y and d.dir[
                        0] != 0 and d.dir[1] == 0 and not d.is_dead:
                    if canidate_rank == -1 or d.waiting_for > canidate_rank:
                        canidate_idx = idx + 0

            if canidate_idx is not None:
                canidate = dots[canidate_idx]

            if canidate is not None:
                if canidate.selected is None or canidate.selected == "value":
                    canidate_par = canidate.data.copy()['value']
                else:
                    canidate_par = canidate.data.copy()['address']

                # self.dir = canidate.dir[:]

                self.waiting = False

                self.waiting_for = 0

                if self.selected is None or self.selected == "value":
                    a_val = str(Decimal(self.data['value']))
                    dest = "value"
                else:
                    a_val = str(Decimal(self.data['address']))
                    dest = "address"


                a_val = a_val.rstrip('0').rstrip('.') if '.' in a_val else a_val

                b_val = str(Decimal(canidate_par))
                b_val = b_val.rstrip('0').rstrip('.') if '.' in b_val else b_val

                oper = operators_eval[enc_opers_square.index(char)]

                self.data[dest] = eval(a_val + oper + b_val) * 1  # the '* 1' converts it to an int if it is a boolean

                canidate.is_dead = True
            else:
                return

    def handle_oper_curly(self, char):
        if self.dir[0] == 0 and self.dir[1] == 0:
            return
        elif self.dir[0] == 0 and self.dir[1] != 0:
            self.waiting = True

            self.increment_others()

            return
        elif self.dir[0] != 0 and self.dir[1] == 0:
            self.waiting = True

            self.increment_others()

            canidate = None
            canidate_idx = None
            canidate_rank = -1
            for idx, d in enumerate(dots):
                # If this is not first in line, return
                if d.x == self.x and d.y == self.y and d.dir[
                        0] != 0 and d.dir[1] == 0 and not d.is_dead:
                    if d.waiting_for > self.waiting_for:
                        return

                # This is part of finding the matching dot that is
                # first in line
                if d.x == self.x and d.y == self.y and d.dir[
                        0] == 0 and d.dir[1] != 0 and not d.is_dead:
                    if canidate_rank == -1 or d.waiting_for > canidate_rank:
                        canidate_idx = idx

            if canidate_idx is not None:
                canidate = dots[canidate_idx]

            if canidate is not None:
                if canidate.selected is None or canidate.selected == "value":
                    canidate_par = canidate.data.copy()['value']
                else:
                    canidate_par = canidate.data.copy()['address']

                # self.dir = canidate.dir[:]

                self.waiting = False

                self.waiting_for = 0

                if self.selected is None or self.selected == "value":
                    a_val = str(Decimal(self.data['value']))
                    dest = "value"
                else:
                    a_val = str(Decimal(self.data['address']))
                    dest = "address"

                a_val = a_val.rstrip('0').rstrip('.') if '.' in a_val else a_val

                b_val = str(Decimal(canidate_par))
                b_val = b_val.rstrip('0').rstrip('.') if '.' in b_val else b_val

                oper = operators_eval[enc_opers_curly.index(char)]

                self.data[dest] = eval(a_val + oper + b_val) * 1  # the '* 1' converts it to an int if it is a boolean

                canidate.is_dead = True
            else:
                return

    # @profile
    def tick(self):
        past_locations = []
        while(True):
            if debug:
                render()
                if step_manual:
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

            if not self.waiting:
                self.x += self.dir[0]
                self.y += self.dir[1]
            else:
                self.waiting_for += 1

            past_locations.append(coords)

            if not exists(self.x, self.y):
                self.is_dead = True
                return

            char = world[self.y][self.x]

            if char == '$':
                self.is_printing = True
                continue

            if self.is_printing:
                if self.handle_printing(char):
                    return
                else:
                    pass

            if char == '"':
                continue

            if char.isdigit():
                self.handle_digit(int(char))
                self.last_char_int = True
                continue
            else:
                self.last_char_int = False

            if char in lib_alias_chars:
                self.handle_alias_char(char)
                # print(self.stack)
                return

            if char == ':':
                if self.data['value'] == 0:
                    self.is_dead = True
                    return

                continue

            if char == ';':
                if self.data['value'] == 1:
                    self.is_dead = True
                    return

                continue

            if char in enc_opers_square:
                self.handle_oper_square(char)
                return

            if char in enc_opers_curly:
                self.handle_oper_curly(char)
                return

            if char in teleporters:
                for y in range(len(world)):
                    if world[y][0] == '%':
                        continue

                    for x in range(len(world[y])):
                        if "''" in world[y][:x]:
                            break;

                        if x == self.x and y == self.y:
                            continue

                        cell = world[y][x]

                        if cell == char:
                            self.x = x
                            self.y = y
                            return

            for lib_main_alias in lib_alias_chars:
                lib_gotos = lib_alias_chars[lib_main_alias]['goto_chars']

                if char in lib_gotos:

                    (self.x, self.y) = self.stack.pop()
                    return

                    for y in range(len(world)):
                        if world[y][0] == '%':
                            continue

                        for x in range(len(world[y])):
                            if "''" in world[y][:x]:
                                break;

                            if x == self.x and y == self.y:
                                continue

                            cell = world[y][x]

                            if cell == lib_main_alias:
                                self.x = x
                                self.y = y
                                return

            if self.char_handler_dict[char]():
                return


raw_chars = []

lib_id_counter = 0

lib_alias_chars = {}

program_dir = ""

offset = (128 + len(operators)*2 + 1) + 1

main_lines = []

libs = {}


def find_and_process_libs(raw_lines, is_main, this_file_name=""):
    global all_lib_files
    global lib_id_counter
    global program_dir
    global offset
    global lib_alias_chars
    global main_lines

    include_files = []
    include_aliases = []

    lines = []
    for line in raw_lines:
        if line[0] == '%':
            if line[1] == '!':
                pieces = line[2:].split()

                include_files.append(pieces[0])
                include_aliases.append(pieces[1])
        else:
            lines.append(line)

    for idx, file_name in enumerate(include_files):
        if file_name not in libs:
            if os.path.isfile(os.path.join(program_dir, file_name)):
                new_path = os.path.join(program_dir, file_name)
            else:
                interpreter_dir = os.path.dirname(os.path.realpath(__file__))
                new_path = os.path.join(interpreter_dir, "libs", file_name)

            # print(file_name)

            with open(new_path.split('%', 1)[0], 'r') as lib_file:
                next_lines = lib_file.readlines()

            alias_char = chr(offset)

            libs[file_name] = {'id': lib_id_counter, 'alias': alias_char}

            # Find all the library tp chars
            tp_chars = []
            for line in next_lines:
                if line[:2] == '%+':
                    tp_chars = list(line[2:].rstrip())
                    # print('tp_chars found')
                    # print(tp_chars)
                    break

            lib_alias_chars[alias_char] = {"file": file_name, "goto_chars": []}

            # Replace all library tp chars with special unique chars
            for idx_1, char in enumerate(tp_chars):
                replacement = chr(offset+idx_1+1)

                next_lines = [li.replace(char, replacement) for li in next_lines]

                lib_alias_chars[alias_char]['goto_chars'].append(replacement)

            libs[file_name]['lines'] = next_lines

            lib_id_counter += 5

            offset += 5

            find_and_process_libs(next_lines, False, file_name)


        # Replace all alias chars with their universal counterparts
        if is_main:
            main_lines = [li.replace(include_aliases[idx], libs[file_name]['alias']) for li in main_lines]
        else:
            libs[this_file_name] = [li.replace(include_aliases[idx], libs[file_name]['alias']) for li in libs[this_file_name]]

# @profile
def main(args):
    global dots
    global teleporters
    global raw_chars
    global main_lines
    global program_dir
    global world
    global world_raw
    global offset
    global main_lines


    file_path = args[0]

    program_dir = os.path.dirname(os.path.abspath(file_path))

    with open(file_path, 'r') as file:
        main_lines = file.readlines()

    find_and_process_libs(main_lines, True)

    for library_file in libs:
        main_lines.extend(libs[library_file]['lines'])

    # print(json.dumps(lib_alias_chars))
    # print(libs)

    lines = main_lines

    for line in lines:
        if line[0] == '%':
            if line[1] == '.':
                dot_synonyms = list(line[2:].rstrip())
            elif line[1] == '$':
                raw_chars = list(line[2:].rstrip())
                teleporters = [chr(idx+offset) for idx, c in enumerate(raw_chars)]
            continue

        data = ' ' + line.split("''", 1)[0].rstrip() + ' '

        data = data.replace('.', '•')

        world_raw.append(list(data))

        data = data.replace('•', '.')
        data = data.replace('÷', '/')

        for idx, rc in enumerate(raw_chars):
            data = data.replace(rc, teleporters[idx])

        for idx, oper in enumerate(operators):
            # data = data.replace("[{0}]".format(
            #     oper), "-{0}-".format(chr(128 + idx)))
            # data = data.replace(
            #     "{" + oper + "}", "-{0}-".format(chr(128 + idx + len(operators) + 1)))
            data = data.replace("[{0}]".format(
                oper), "[{0}]".format(chr(128 + idx)))
            data = data.replace(
                "{" + oper + "}", "{" + "{0}".format(chr(128 + idx + len(operators) + 1) + "}"))

        world.append(list(data))

    longest_line = max((len(l), i) for i, l in enumerate(world))[0]

    world     = [' '*longest_line] + world
    world_raw = [' '*longest_line] + world_raw


    for idx, line in reversed(list(enumerate(world))):
        world[idx] += (' ' * (longest_line - len(line) + 1))
        world_raw[idx] += (' ' * (longest_line - len(line) + 1))

    try:
        special_dots = [[]] * len(dot_synonyms)
    except:
        special_dots = []
        dot_synonyms = []

    for y in range(len(world)):
        if world[y][0] == '%':
            continue

        for x in range(len(world[y])):
            cell = world[y][x]

            if cell == '.':
                dots.append(dot(x, y))
            elif cell in dot_synonyms:
                special_dots[dot_synonyms.index(cell)].append(dot(x, y))

    dots.extend(reversed(list(chain.from_iterable(special_dots))))

    tick_cnt = 0
    cycle_cnt = 0

    while len(dots) > 0:
        new_dots = []

        dot_locations = []


        for idx in reversed(range(len(dots))):
            d = dots[idx]

            d.tick()

            if d.is_dead:
                del dots[idx]
            else:
                dot_locations.append((d.x, d.y))

            tick_cnt += 1
            if tick_max_limit is not None and tick_cnt > tick_max_limit:
                return  # Tick limit exceeded, so return/exit

        if len(new_dots) > 0:
            dots.extend(new_dots)

        new_dots = []

        # if step_manual:
        #     try:
        #         input("")
        #     except SyntaxError:
        #         pass

        cycle_cnt += 1
        if cycle_max_limit is not None and cycle_cnt > cycle_max_limit:
            return  # Tick limit exceeded, so return/exit

        # dots = list(set(dots[:]))

        new_list = []

        for d in dots:
            if d not in new_list:
                new_list.append(d)

        dots = new_list[:]

    # End program
    return 0

if __name__ == '__main__':
    exit_progam(main(sys.argv[1:]))

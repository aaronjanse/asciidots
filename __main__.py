#!/usr/bin/env python
# coding=utf-8

import codecs
import locale
import os
import signal
import sys
import time

import click

if codecs.lookup(locale.getpreferredencoding()).name == 'ascii':
    os.environ['LANG'] = 'en_US.utf-8'

from dots.interpreter import AsciiDotsInterpreter
from dots.callbacks import IOCallbacksStorage

from dots import terminalsize

try:
    import curses
except ImportError:
    curses = 'failed to import curses; running in compatibility mode'
    print(curses)
    compat_debug_default = True
else:
    compat_debug_default = False

terminal_lines = terminalsize.get_terminal_size()[1]
default_debug_lines = int(terminal_lines * 2 / 3)

interpreter = None

debug_ = True
autostep_debug_ = False


class DefaultIOCallbacks(IOCallbacksStorage):
    """The default class to manage the input and output of a dots program."""

    def __init__(self, ticks, silent, debug, compat_debug, debug_lines, autostep_debug, output_limit):
        super().__init__()

        # if it is zero or false, we don't want to stop
        self.ticks_left = ticks if ticks else float('inf')
        self.outputs_left = output_limit if output_limit else float('inf')

        self.silent = silent
        self.debug = debug
        self.compat_debug = compat_debug
        self.debug_lines = debug_lines
        self.autostep_debug = autostep_debug

        self.compat_logging_buffer = ''
        self.compat_logging_buffer_lines = terminal_lines - debug_lines - 1

        if self.debug and not self.compat_debug:
            self.logging_loc = 0
            self.logging_x = 1

            self.stdscr = curses.initscr()

            curses.start_color()

            curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)

            curses.noecho()

            # hides the cursor
            curses.curs_set(False)

            # defining the two main parts of the screen: the view of the program
            self.win_program = curses.newwin(self.debug_lines, curses.COLS - 1, 0, 0)
            # and pad for the output of the prog
            self.logging_pad = curses.newpad(1000, curses.COLS - 1)

            def signal_handler(signal, frame):
                self.on_finish()
                sys.exit(0)

            signal.signal(signal.SIGINT, signal_handler)

            self.first_tick = True
        else:
            self.first_tick = False

    def get_input(self):
        """Get an input from the user."""
        if not self.debug or self.compat_debug:
            if not sys.stdin.isatty():
                return input('')
            else:
                return input('?: ')
        else:
            return self.curses_input(self.stdscr, curses.LINES - 3, 2, '?: ')

    def curses_input(self, stdscr, row, col, prompt_string):
        """
        Get an input string with curses.

        Row and col are the start position ot the prompt_string.
        """
        curses.echo()
        stdscr.addstr(row, col, str(prompt_string), curses.A_REVERSE)
        stdscr.addstr(row + 1, col, " " * (curses.COLS - 1))
        stdscr.refresh()
        input_val = ""

        while len(input_val) <= 0:
            input_val = stdscr.getstr(row + 1, col, 20)

        return input_val

    def on_output(self, value):
        self.outputs_left -= 1

        # maximum output reached, we quit the prog
        if self.outputs_left == 0:
            self.on_finish()
            return

        # no printing mode
        if self.silent:
            return

        if not self.debug:
            print(value, end='', flush=True)

        elif self.compat_debug:
            # we add the ouput to the buffer
            self.compat_logging_buffer += value
            # and we keep the maximum number of line to compat_logging_buffer_lines
            self.compat_logging_buffer = '\n'.join(
                self.compat_logging_buffer.split('\n')[:self.compat_logging_buffer_lines])

        else:
            # add the output string to the pad
            self.logging_pad.addstr(self.logging_loc, self.logging_x, str(value))

            self.logging_pad.refresh(self.logging_loc - min(self.logging_loc, curses.LINES - self.debug_lines - 1), 0,
                                     self.debug_lines, 0, curses.LINES - 1, curses.COLS - 1)

            # FIXME: This should count the number of newlines instead
            if str(value).endswith('\n'):
                self.logging_loc += 1
                self.logging_x = 1
            else:
                self.logging_x += len(value)

    def on_finish(self):
        """Close cleanly the I/O."""
        global interpreter  # beurk

        # we need to close curses only if it was opened :P
        if self.debug and not self.compat_debug:
            curses.nocbreak()
            self.stdscr.keypad(False)
            curses.echo()

            curses.endwin()

    def on_error(self, error_text):
        """Show the error and cleans the I/O."""
        self.on_output('error: {}'.format(error_text))

        self.on_finish()

    def on_microtick(self, dot):

        # we want to show the program
        if self.debug and not self.silent:

            d_l = []
            for idx in reversed(range(len(interpreter.get_all_dots()))):
                d = interpreter.dots[idx]
                if not d.state.isDeadState():
                    d_l.append((d.x, d.y))

            last_blank = False

            display_y = 0

            if self.compat_debug:
                if os.name == 'nt':
                    os.system('cls')  # For Windows
                else:
                    os.system('clear')  # For Linux/OS X
            else:
                self.win_program.refresh()

            for y in range(len(interpreter.world._data_array)):
                if display_y > self.debug_lines - 2:
                    break

                if len(''.join(interpreter.world._data_array[y]).rstrip()) < 1:
                    if last_blank:
                        continue
                    else:
                        last_blank = True
                else:
                    last_blank = False

                for x in range(len(interpreter.world._data_array[y])):
                    char = interpreter.world._data_array[y][x]

                    # RGYB

                    if (x, y) in d_l:
                        if self.compat_debug:
                            print('\033[0;31m' + char + '\033[0m', end='')  # Red
                        else:
                            self.win_program.addstr(display_y, x, char, curses.color_pair(1))
                    elif char.isLibWarp():
                        if self.compat_debug:
                            print('\033[0;32m' + char + '\033[0m', end='')  # Green
                        else:
                            self.win_program.addstr(display_y, x, char, curses.color_pair(2))
                    elif char.isWarp():
                        if self.compat_debug:
                            print('\033[0;33m' + char + '\033[0m', end='')  # Yellow
                        else:
                            self.win_program.addstr(display_y, x, char, curses.color_pair(3))
                    elif char in '#@~' or char.isOper():
                        if self.compat_debug:
                            print('\033[0;34m' + char + '\033[0m', end='')  # Blue
                        else:
                            self.win_program.addstr(display_y, x, char, curses.color_pair(4))
                    elif char == '\n':
                        pass
                    else:
                        if self.compat_debug:
                            print(char, end='')
                        else:
                            self.win_program.addstr(display_y, x, char)

                if self.compat_debug:
                    print()

                display_y += 1

            if self.autostep_debug:
                time.sleep(self.autostep_debug)
            else:
                if self.compat_debug:
                    input("Press enter to step...")
                else:
                    keycode = self.stdscr.getch()

                    if keycode == 3 or keycode == 26:
                        self.on_finish()
                        sys.exit(0)

        if self.compat_debug:
            print('\n' + self.compat_logging_buffer, end='', flush=True)

        if self.ticks_left == 0:
            self.on_output('QUITTING next step!\n')

            self.on_finish()
            sys.exit(0)

        self.ticks_left -= 1


@click.command()
@click.argument('filename')
@click.option('--debug', '-d', is_flag=True, help='Show the execution of the program and the course of the dots.')
@click.option('--autostep_debug', '-a', default=False, help='The time between every tick')
@click.option('--output_limit', '-o', default=0, help='Terminate the program after N outputs.')
@click.option('--ticks', '-t', default=0, help='Terminate the program after N ticks.')
@click.option('--silent', '-s', is_flag=True, help='No printing, for benchmarking.')
@click.option('--compat_debug', '-w', is_flag=True, help='Force the debug rendering without ncurses.')
@click.option('--debug_lines', '-l', default=default_debug_lines, help='The size of the debug view.')
@click.option('--run_in_parallel', '-p', is_flag=True, help='All dots move at the same time.')
def main(filename, ticks, silent, debug, compat_debug, debug_lines, autostep_debug, output_limit, run_in_parallel):
    global interpreter

    if autostep_debug is not False:
        autostep_debug = float(autostep_debug)

    compat_debug = compat_debug or compat_debug_default

    io_callbacks = DefaultIOCallbacks(ticks, silent, debug, compat_debug, debug_lines, autostep_debug, output_limit)

    program_dir = os.path.dirname(os.path.abspath(filename))

    with open(filename, 'r') as file:
        program = file.readlines()

    try:
        interpreter = AsciiDotsInterpreter(program, program_dir, io_callbacks, run_in_parallel)
        interpreter.run()
    except Exception as e:
        io_callbacks.on_finish()
        interpreter.terminate()
        raise e


if __name__ == "__main__":
    main()

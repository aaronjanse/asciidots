from dots.interpreter import AsciiDotsInterpreter
from dots.callbacks import IOCallbacksStorage

import curses
import click

import sys
import os

import time

import signal

from dots.states import DeadState

interpreter = None

debug_ = True
autostep_debug_ = False

class Default_IO_Callbacks(IOCallbacksStorage):
    def __init__(self, debug, autostep_debug, head):
        super().__init__()

        self.debug = debug
        self.autostep_debug = autostep_debug
        self.head = head

        self.output_count = 0

        if self.debug:
            self.logging_loc = 0
            self.logging_x = 1

            self.stdscr = curses.initscr()

            curses.start_color()

            curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)

            curses.noecho()

            curses.curs_set(False)

            self.debug_lines = 40

            self.win_program = curses.newwin(self.debug_lines, curses.COLS - 1, 0, 0)

            self.logging_pad = curses.newpad(1000, curses.COLS - 1)

            def signal_handler(signal, frame):
                    self.on_finish()
                    sys.exit(0)

            signal.signal(signal.SIGINT, signal_handler)

    def get_input(self):
        if not self.debug:
            if not sys.stdin.isatty():
                return input('')
            else:
                return input('?: ')
        else:
            return self.curses_input(self.stdscr, curses.LINES - 2, 2, '?: ')

    def curses_input(self, stdscr, r, c, prompt_string):
        curses.echo()
        stdscr.addstr(r, c, str(prompt_string), curses.A_REVERSE)
        stdscr.addstr(r + 1, c, " " * (curses.COLS - 1))
        stdscr.refresh()
        input = ""

        while len(input) <= 0:
            input = stdscr.getstr(r + 1, c, 20)

        return input

    def on_output(self, value):
        self.output_count += 1

        if self.head != -1 and self.output_count > self.head:
            self.on_finish()
            return

        if not self.debug:
            print(value, end='')
        else:
            self.logging_pad.addstr(self.logging_loc, self.logging_x, str(value))
            self.logging_pad.refresh(self.logging_loc - min(self.logging_loc, curses.LINES -
                                     self.debug_lines - 1), 0, self.debug_lines, 0,
                                     curses.LINES - 1, curses.COLS - 1)

            # FIXME: This should count the number of newlines instead
            if str(value).endswith('\n'):
                self.logging_loc += 1
                self.logging_x = 1
            else:
                self.logging_x += len(value)

    def on_finish(self):
        global interpreter

        if self.debug:
            curses.nocbreak()
            self.stdscr.keypad(False)
            curses.echo()

            curses.endwin()

    def on_error(self, error_text):
        print('error: {}'.format(error_text))

        self.on_finish()

    def on_microtick(self, dot):
        if self.debug:
            if self.autostep_debug is False:
                self.stdscr.getch()
            else:
                time.sleep(self.autostep_debug)

            d_l = []
            for idx in reversed(range(len(interpreter.get_all_dots()))):
                d = interpreter.dots[idx]
                if not d.state.isDeadState():
                    d_l.append((d.x, d.y))

            special_char = False

            last_blank = False

            display_y = 0

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

                    if (x, y) in d_l:
                        self.win_program.addstr(display_y, x, char, curses.color_pair(1))
                    elif char.isLibWarp():
                        self.win_program.addstr(display_y, x, char, curses.color_pair(2))
                    elif char.isWarp():
                        self.win_program.addstr(display_y, x, char, curses.color_pair(3))
                    elif char in '#@~' or char.isOper():
                        self.win_program.addstr(display_y, x, char, curses.color_pair(4))
                    else:
                        self.win_program.addstr(display_y, x, char)

                display_y += 1


@click.command()
@click.argument('filename')
@click.option('--debug', '-d', is_flag=True)
@click.option('--autostep_debug', '-a', default=False)
@click.option('--head', '-h', default=-1)
def main(filename, debug, autostep_debug, head):
    global interpreter

    if autostep_debug is not False:
        autostep_debug = float(autostep_debug)

    head = int(head)

    io_callbacks = Default_IO_Callbacks(debug, autostep_debug, head)

    file_path = sys.argv[1]

    program_dir = os.path.dirname(os.path.abspath(file_path))

    with open(file_path, 'r') as file:
        program = file.readlines()

    try:
        interpreter = AsciiDotsInterpreter(program, program_dir, io_callbacks)
        interpreter.run()
    except Exception as e:
        io_callbacks.on_finish()
        interpreter.terminate()
        raise e


if __name__ == "__main__":
    main()

from __future__ import print_function

import io
import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dots import callbacks
from dots.environment import Env
from dots.interpreter import AsciiDotsInterpreter
from dots.exceptions import DotsExit


class KeepOutputIOCallbacks(callbacks.IOCallbacksStorage):
    def __init__(self, env, input):
        super(KeepOutputIOCallbacks, self).__init__(env)

        self.output = []
        self.input = input

    def get_input(self, ascii_char=False):
        if ascii_char:
            chars_to_read = 1
            if len(self.input) == 0:
                return ""
        else:
            chars_to_read = self.input.find('\n')
            if chars_to_read == -1:
                chars_to_read = len(self.input)

        ret = self.input[:chars_to_read]
        self.input = self.input[chars_to_read:]
        print(ret, '-----', chars_to_read)
        return ret

    def on_output(self, value):
        self.output.append(value)

    def on_finish(self):
        pass

    def on_error(self, error_text):
        raise RuntimeError(error_text)

    def on_microtick(self, dot):
        "we're not printing anything at all"


def check_output(name, input='', run_in_parallel=True):
    env = Env()
    env.io = KeepOutputIOCallbacks(env, input)

    with io.open('test/' + name + '.dots', encoding='utf-8') as file:
        program = file.read()
    print(program, '---', sep='' )   
    interpreter = AsciiDotsInterpreter(env, program, 'test', run_in_parallel)
    print(interpreter.env.world.map)
    try:
        interpreter.run()
    except DotsExit:
        pass

    return env.io.output


def map_add_newline(*args):
    """
    Transforms the list to a list of strings with a newline at the end of each entry, as this is a common pattern.
    """
    
    return list(str(arg) + '\n' for arg in args)


def test_dots_count_to_100():
    out = check_output('count_to_100')
    assert out == map_add_newline(*range(1, 101))

def test_dots_use_for_in_range_library():
    out = check_output('use_for_in_range')
    assert out == map_add_newline(*range(1, 10))

def test_dots_use_wraps():
    out = check_output('warps')
    assert out == map_add_newline(3)

def test_dots_print_three():
    out = check_output('three')
    assert out == map_add_newline(3)

def test_dots_quine():
    out = check_output('quine')
    with open('test/quine.dots') as f:
        assert ''.join(out) == f.read()

def test_dots_factor():
    out = check_output('factor', '24')
    assert out == map_add_newline(1, 2, 3, 4)

    out = check_output('factor', '51')
    assert out == map_add_newline(1, 3)

def test_dots_singleton():
    out = check_output('singleton')
    assert out == map_add_newline(*range(1, 6))

    out = check_output('singleton_2')
    assert out == map_add_newline(-1, 1)

def test_dots_and():
    out = check_output('and')
    assert out == map_add_newline('Good')

def test_dots_timing():
    out = check_output('lock')
    assert out == map_add_newline(1)

def test_dots_tilde():
    out = check_output('tilde')
    assert out == map_add_newline("Y")

def test_dots_ascii_input():
    out = check_output('ascii_input', "END\n")
    assert out == map_add_newline('Success!')
        
def test_dots_filter_chars():
    out = check_output('filter_chars', "END\n")
    assert out == [0, 0, 1, 1]

def test_dots_id_mode_persistence():
    out = check_output('id_mode_persistence')
    assert out == map_add_newline("Y")

def test_dots_eof():
    out = check_output('eof', "hi\n")
    assert len(out) == 5

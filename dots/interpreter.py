import threading
from .world import World
from .dot import Dot

from .states import DeadState


class AsciiDotsInterpreter(object):
    def __init__(self, program, program_dir, io_callbacks):
        self.world = World(program, program_dir)
        self.io_callbacks = io_callbacks

        self._setup_dots()

    def run(self, run_in_separate_thread=None, make_thread_daemon=None):
        """
        Start executing the AsciiDots code

        Arguments:
        run_in_separate_thread -- If set to True, the program will be interpreted in a separate thread
        make_thread_daemon -- Controls whether a thread created by enabling in_seperate_thread will be run as daemon
        """
        if run_in_separate_thread is None:
            run_in_separate_thread = False

        if make_thread_daemon is None:
            make_thread_daemon = False

        self.needsShutdown = False

        if run_in_separate_thread:
            inter_thread = threading.Thread(target=self.run, daemon=make_thread_daemon)
            inter_thread.start()
            return

        while not self.needsShutdown and len(self.dots) > 0:
            self._dots_for_next_tick = []

            for dot in self.dots:
                dot.simulate_tick()

                if not dot.state.isDeadState():
                    self._dots_for_next_tick.append(dot)

            self.dots = self._dots_for_next_tick

        self.io_callbacks.on_finish()

    def terminate(self):
        self.needsShutdown = True

    def get_all_dots(self):
        return self.dots[:]

    def _setup_dots(self):
        dot_locations = self.world.get_coords_of_dots()

        self.dots = []
        for x, y in dot_locations:
            new_dot = Dot(x, y, world=self.world, callbacks=self.io_callbacks, func_to_create_dots=self._add_dot, func_to_get_dots=self.get_all_dots)
            self.dots.append(new_dot)

    def _add_dot(self, dot):
        self._dots_for_next_tick.append(dot)

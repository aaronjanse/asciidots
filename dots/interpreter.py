import threading

from dots.exceptions import DotsExit
from .dot import Dot
from .world import World


class AsciiDotsInterpreter(object):
    def __init__(self, env, program, program_dir, run_in_parallel):
        """
        Create a new instance of the interpreter to run the program.

        :param dots.environment.Env env: The environment for the program
        :param str program: The code of the program
        :param str program_dir: The path to the program directory
        :param bool run_in_parallel: temporarily, changes the way dots move : one by one or all at the same time
        """

        self.env = env
        self.env.interpreter = self
        self.env.world = World(env, program, program_dir)
        self.env.dots = []

        self.needs_shutdown = False

        self._setup_dots()
        self.run_in_parallel = run_in_parallel

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.terminate()
        self.env.io.on_finish()

        if isinstance(exc_tb, DotsExit):
            # we don't want the exception re-raised
            return True

    def _setup_dots(self):
        """Fill the dot list with dots from the starting points in the world."""

        self.env.dots = []
        for pos in self.env.world.get_coords_of_dots():
            new_dot = Dot(self.env, pos)

            self.env.dots.append(new_dot)

    def run(self, run_in_separate_thread=None, make_thread_daemon=None):
        """
        Start executing the AsciiDots code

        Arguments:
        run_in_separate_thread -- If set to True, the program will be interpreted in a separate thread
        make_thread_daemon -- Controls whether a thread created by enabling in_seperate_thread will be run as daemon
        """

        if run_in_separate_thread:
            inter_thread = threading.Thread(target=self.run, daemon=make_thread_daemon)
            inter_thread.start()
            return

        with self:
            while not self.needs_shutdown and len(self.env.dots) > 0 and not all(dot.state.isWaiting for dot in self.env.dots):

                if self.run_in_parallel:
                    self.parallel_tick()
                else:
                    self.async_tick()

            raise DotsExit

    def parallel_tick(self):
        """Simulate a tick in parallele mode"""

        dots = self.env.dots[:]
        for dot in dots:
            dot.next()

        for dot in dots:
            dot.run()

        for dot in dots:
            if dot.state.is_dead():
                self.env.dots.remove(dot)

        self.env.io.on_microtick(None)

    def async_tick(self):
        """Simulate a tick in async mode."""
        for dot in self.env.dots[:]:
            dot.simulate_tick(not self.run_in_parallel)

            if dot.state.is_dead():
                self.env.dots.remove(dot)

    def terminate(self):
        """The program will shut down at the next operation."""
        self.needs_shutdown = True

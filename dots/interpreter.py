import threading

from .dot import Dot
from .world import World


class AsciiDotsInterpreter(object):
    def __init__(self, env, program, program_dir, run_in_parallel):
        """
        Create a new instance of the interpreter to run the program.

        :param dots.environement.Env env: The environement for the program
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

        while not self.needs_shutdown and len(self.env.dots) > 0:
            next_tick_dots = []

            for dot in self.env.dots:
                dot.simulate_tick(not self.run_in_parallel)

                if not dot.state.is_dead():
                    next_tick_dots += dot,

            if self.run_in_parallel:
                self.env.io.on_microtick(self.env.dots[0])

            self.env.dots = next_tick_dots

        self.env.io.on_finish()

    def terminate(self):
        """The program will shut down at the next operation."""
        self.needs_shutdown = True

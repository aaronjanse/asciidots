from .states import *
import sys


class Dot:
    def __init__(self, env, x, y, id_=None, value=None, direction=None, state=None, stack=None):
        """
        The base unit of and ascii dot code : the dot.

        :param dots.environement.Env env: The environement for the program
        :param int x: the column of the dot
        :param int y: the row of the dot
        :param float id_: the id of the dot
        :param float value: its value
        :param list[int, int] direction: The direction of the dot
        :param state: Its actual state
        :param list stack:
        """

        self.x = x
        self.y = y

        self.env = env
        self.id = id_ or 0
        self.value = value or 0
        self.state = state(self) if state else TravelState(self)  # type: State
        self.dir = direction or self._calculate_direction()
        self.stack = stack or []

        self.x += self.dir[0]
        self.y += self.dir[1]

    def __repr__(self):
        return '<Dot x={x}, y={y}, id={id}, value={value}, dir={dir}, stack={stack}>'.format(**self.__dict__)

    def simulate_tick(self, run_until_waiting):
        past_locations = []

        while True:
            if run_until_waiting:
                self.env.io.on_microtick(self)

            coords = (self.x, self.y)
            if coords in past_locations:
                return

            past_locations.append(coords)

            if not self.env.world.doesLocExist(self.x, self.y):
                self.state = DeadState(self)
                return

            char = self.env.world.getCharAt(self.x, self.y)

            if char == '&':
                self.state = DeadState(self)

                self.env.io.on_finish()
                sys.exit(0)

            self.state = self.state.next(char)

            self.state.run(char)

            if self.state.is_dead():
                return

            if self.state.isWaiting:
                break

            if not run_until_waiting:
                break

    def _calculate_direction(self):

        up_loc = (UP[0] + self.x, UP[1] + self.y)
        down_loc = (DOWN[0] + self.x, DOWN[1] + self.y)
        left_loc = (LEFT[0] + self.x, LEFT[1] + self.y)
        right_loc = (RIGHT[0] + self.x, RIGHT[1] + self.y)

        for direction, location in zip([UP, DOWN], [up_loc, down_loc]):
            if self.env.world.doesLocExist(*location) and self.env.world.getCharAt(*location) == '|':
                return list(direction)

        for direction, location in zip([RIGHT, LEFT], [right_loc, left_loc]):
            if self.env.world.doesLocExist(*location) and self.env.world.getCharAt(*location) == '-':
                return list(direction)

        all_possible_directions = [UP, RIGHT, DOWN, LEFT]
        all_possible_locations = [up_loc, right_loc, down_loc, left_loc]

        valid_chars = ('\\', '/', '*', '^', 'v', '>', '<', '+')

        for direction, location in zip(all_possible_directions, all_possible_locations):
            if self.env.world.doesLocExist(*location) and self.env.world.getCharAt(*location) in valid_chars:
                return list(direction)

        # If we get here without returning, the dot can't find a direction to go!
        self.env.io.on_error("dot cannot determine location...\nx: {x}, y: {y}".format(x=self.x, y=self.y))

        self.state = DeadState(self)

        return [0, 0]

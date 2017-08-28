from .states import *
import sys

class Dot:
    def __init__(self, x, y, world, callbacks, func_to_create_dots, func_to_get_dots, id_=None, value=None, direction=None, state=None, stack=None):
        self.x = x
        self.y = y

        self.world = world

        self.callbacks = callbacks
        self.func_to_create_dots = func_to_create_dots
        self.func_to_get_dots = func_to_get_dots

        self.id = id_ or 0
        self.value = value or 0
        self.state = state(self) if state else TravelState(self)
        self.dir = direction or self._calculate_direction()
        self.stack = stack or []

        self.x += self.dir[0]
        self.y += self.dir[1]

    def __repr__(self):
        return '<Dot x={x}, y={y}, id={id}, value={value}, dir={dir}, stack={stack}>'.format(**self.__dict__)

    def simulate_tick(self, run_until_waiting):
        past_locations = []
        while(True):
            if run_until_waiting:
                self.callbacks.on_microtick(self)

            coords = (self.x, self.y,)
            if coords in past_locations:
                return

            past_locations.append(coords)

            if not self.world.doesLocExist(self.x, self.y):
                self.state = DeadState(self)
                return

            char = self.world.getCharAt(self.x, self.y)

            if char == '&':
                self.state = DeadState(self)

                self.callbacks.on_finish()
                sys.exit(0)
                return

            self.state = self.state.next(char)

            self.state.run(char)

            if self.state.is_dead_state():
                return

            if self.state.isWaiting:
                break

            if not run_until_waiting:
                break

    def _calculate_direction(self):
        up_dir = (0, -1)
        down_dir = (0, 1)
        left_dir = (-1, 0)
        right_dir = (1, 0)

        up_loc = (up_dir[0] + self.x, up_dir[1] + self.y)
        down_loc = (down_dir[0] + self.x, down_dir[1] + self.y)
        left_loc = (left_dir[0] + self.x, left_dir[1] + self.y)
        right_loc = (right_dir[0] + self.x, right_dir[1] + self.y)

        for direction, location in zip([up_dir, down_dir], [up_loc, down_loc]):
            if self.world.doesLocExist(*location) and self.world.getCharAt(*location) == '|':
                return list(direction)

        for direction, location in zip([right_dir, left_dir], [right_loc, left_loc]):
            if self.world.doesLocExist(*location) and self.world.getCharAt(*location) == '-':
                return list(direction)

        all_possible_directions = [up_dir, right_dir, down_dir, left_dir]
        all_possible_locations = [up_loc, right_loc, down_loc, left_loc]

        valid_chars = ('\\', '/', '*', '^', 'v', '>', '<', '+')

        for direction, location in zip(all_possible_directions, all_possible_locations):
            if self.world.doesLocExist(*location) and self.world.getCharAt(*location) in valid_chars:
                return list(direction)

        # If we get here without returning, the dot can't find a direction to go!
        self.callbacks.on_error("dot cannot determine location...\nx: {x}, y: {y}".format(x=self.x, y=self.y))

        self.state = DeadState(self)

        return [0, 0]

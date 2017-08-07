from .states import *


class Dot:
    def __init__(self, x, y, world, callbacks, func_to_create_dots, func_to_get_dots, address=None, value=None, direction=None, state=None, stack=None):
        self.x = x
        self.y = y

        self.world = world

        self.callbacks = callbacks
        self.func_to_create_dots = func_to_create_dots
        self.func_to_get_dots = func_to_get_dots

        if address is None:
            address = 0
        self.address = address
        if value is None:
            value = 0
        self.value = value

        if state is None:
            state = TravelState
        self.state = state(self)

        if direction is None:
            direction = self._calculate_direction()
        self.dir = direction

        if stack is None:
            stack = []
        self.stack = stack

        self.x += self.dir[0]
        self.y += self.dir[1]

    def __repr__(self):
        return '<Dot x={x}, y={y}, address={address}, value={value}, dir={dir}, stack={stack}>'.format(**self.__dict__)

    def simulate_tick(self):
        past_locations = []
        while(True):
            self.callbacks.on_microtick(self)
            # if debug:
            #     render(self.inter_inst)
            #
            #     if step_manual:
            #         if not (quick_debug and len(self.stack) > 0):
            #             try:
            #                 if compat_debug:
            #                     input("")
            #                 else:
            #                     stdscr.getch()
            #             except SyntaxError:
            #                 pass
            #     elif step_speed != 0:
            #         sleep(step_speed)

            coords = (self.x, self.y,)
            if coords in past_locations:
                return

            past_locations.append(coords)

            if not self.world.doesLocExist(self.x, self.y):
                self.state = DeadState(self)
                return

            char = self.world.getCharAt(self.x, self.y)

            if char == '&':
                self.callbacks.on_finish()

                self.state = DeadState(self)
                return

            self.state = self.state.next(char)

            self.state.run(char)

            if self.state.isDeadState():
                return

            if self.state.isWaiting:
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

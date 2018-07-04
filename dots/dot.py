import sys

from dots.exceptions import DotsExit
from .states import *


class Dot:
    def __init__(self, env, pos, id_=None, value=None, direction=None, state=None, stack=None):
        """
        The base unit of and ascii dot code : the dot.

        :param dots.environment.Env env: The environment for the program
        :param dots.vector.Pos pos: The position of the dot in the map
        :param float id_: the id of the dot
        :param float value: its value
        :param dots.vector.Pos direction: The direction of the dot
        :param state: Its actual state
        :param list stack:
        """

        self.pos = pos
        self.spawn_pos = pos

        self.env = env
        self.id = id_ or 0
        self.value = value or 0
        self.state = state(self) if state else TravelState(self)  # type: State
        self.dir = direction or self._calculate_direction()
        self.stack = stack or []

    def __repr__(self):
        return '<Dot spawn_pos={spawn_pos} pos={pos}, id={id}, value={value}, dir={dir}, stack={stack}>'.format(**self.__dict__)

    def move(self):
        """Move the dot according to its direction."""
        self.pos += self.dir

    def copy(self):
        """
        Create a copy of the dot.

        :remark: The copy doesn't share any variable (by reference) to the old one. (except env of course)
        """

        return Dot(self.env, self.pos, self.id, self.value, self.dir, type(self.state), self.stack[:])

    def simulate_tick(self, run_until_waiting):
        """
        Update the dot to its next state.

        :param bool run_until_waiting: if false, the dot will perform only one tick, else it will run untill waiting
        """

        past_locations = []

        while True:

            # we need to update the screen if we keep this dot running, nobody will ever do it otherwise
            if run_until_waiting:
                self.env.io.on_microtick(self)

            # If it was already at this location, run someone else (prevent infinite loops)
            if self.pos in past_locations:
                return
            past_locations.append(self.pos)

            # If outside the map, he dies.
            if not self.env.world.does_loc_exist(self.pos):
                self.state = DeadState(self)
                return

            char = self.env.world.get_char_at(self.pos)

            # update the dot
            self.state = self.state.next(char)
            self.state.run(char)

            if self.state.is_dead():
                return

            if not self.env.world.does_loc_exist(self.pos):
                self.state = DeadState(self)
                return

            if self.env.world.is_char_at(self.pos, ' ') and not isinstance(self.state, PrintState):
                self.state = DeadState(self)
                return

            if self.state.isWaiting:
                break

            if not run_until_waiting:
                break

    def next(self):
        """Update the state of this dot accoding to the char it is in."""
        if not self.env.world.does_loc_exist(self.pos):
            self.state = DeadState(self)
            return

        char = self.env.world.get_char_at(self.pos)
        self.state = self.state.next(char)

        if char == ' ' and not isinstance(self.state, PrintState):
            self.state = DeadState(self)

    def run(self):
        """Perform the state action on this char."""
        if not self.env.world.does_loc_exist(self.pos):
            self.state = DeadState(self)
            return

        self.state.run(self.env.world.get_char_at(self.pos))

        if not self.env.world.does_loc_exist(self.pos):
            self.state = DeadState(self)
        if self.env.world.is_char_at(self.pos, ' ') and not isinstance(self.state, PrintState):
            self.state = DeadState(self)

    def _calculate_direction(self):
        """Calculate the inial direction of a just created dot."""
        valid_chars = r'\/*^v><+'

        for direction in DIRECTIONS:
            loc = self.pos + direction

            # we have no interest in chars outside
            if not self.env.world.does_loc_exist(loc):
                continue

            if direction in (UP, DOWN) and self.env.world.get_char_at(loc) == '|':
                return direction

            if direction in (LEFT, RIGHT) and self.env.world.get_char_at(loc) == '-':
                return direction

            if self.env.world.get_char_at(loc) in valid_chars:
                return direction

        # If we get here without returning, the dot can't find a direction to go!
        self.state = DeadState(self)
        return Pos(0, 0)

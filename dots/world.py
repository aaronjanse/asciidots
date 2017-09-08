# Char inheritance works similar to the Decorator Pattern

# TODO: make the iters have a default arg of self._data_array?

import os

from dots.vector import Pos
from .chars import *


class World(object):
    def __init__(self, env, world_map, program_dir):
        """
        Create a new world to do dots races !

        :param dots.environement.Env env: The environement for the program
        :param str world_map: The string representing the world.
        :param str program_dir: The directory of the program
        """

        self.env = env
        self.env.world = self

        self.program_dir = program_dir

        self.map = self.map_from_raw(world_map)

        self._worldwide_warp_id_counter = 0
        self._setup_warps_for(self.map)

        self._import_libraries()

        self._setup_operators()

        self._connect_warps()

        self._update_class_of_dots()

    def get_coords_of_dots(self):
        """Yiels the cordinates of every dot char in the world."""
        for y, line in enumerate(self.map):
            if line[0] == '%':
                continue

            for x, char in enumerate(line):
                if char.isDot():
                    yield Pos(x, y)

    # ✓
    def get_char_at(self, pos: Pos):
        """Get the Char at the given position."""
        # NOTE: _data_array has to be accesed using y, x due to the way it is created
        return self.map[pos.row][pos.col]

    # ✓
    def does_loc_exist(self, loc: Pos):
        """True if this location exists on the map."""
        return 0 <= loc.row < len(self.map) and 0 <= loc.col < len(self.map[loc.row])

    # NOTE: Hopefully done?
    def _import_libraries(self, map=None):
        """
        Import the library for a given map.

        :param str map: The map to import libraries from. Defaults to the world map.
        """

        if map is None:
            map = self.map

        lib_filenames_for_chars = self._get_lib_files_by_alias(map)
        lib_chars = lib_filenames_for_chars.keys()

        self._update_class_of_lib_chars(map, lib_chars)

        singleton_ids = {}

        for y, line in enumerate(map):
            if line[0] == '%':
                continue

            for x, char in enumerate(line):
                if char.isLibWarp() and char.get_id() is None:
                    if char not in singleton_ids:
                        this_warp_id = self._worldwide_warp_id_counter

                        map[y][x].set_id(this_warp_id)
                        self._worldwide_warp_id_counter += 1

                        if char.isSingletonLibWarp():
                            singleton_ids[char] = this_warp_id

                        if char in lib_filenames_for_chars:
                            filename = lib_filenames_for_chars[char]

                            self._import_lib_file_with_warp_id(map, filename, this_warp_id,
                                                               is_singleton=char.isSingletonLibWarp())
                    else:
                        map[y][x].set_id(singleton_ids[char])

    # NOTE: Hopefully done?
    def _import_lib_file_with_warp_id(self, char_obj_array, filename, warp_id, is_singleton):
        path = self._get_path_of_lib_file(filename)

        with open(path, 'r') as lib_file:
            lib_code = lib_file.read()

        lib_char_obj_array = self.map_from_raw(lib_code)

        exposed_char_str = None

        for y, char_list in enumerate(lib_char_obj_array):
            line = ''.join(char_list).rstrip()

            if line[:2] == '%+':
                print(('%+ notation has become replaced by a new notation\n' +
                       'you now define a single warp char as an entry point to your code using %$\n' +
                       'for this code, it is recommended that your replace\n\n' +
                       '%+{0}{1}{2}{3}\n\n' +
                       'with\n\n' +
                       '%^X `` make sure that X doesn\'t conflict with anything\n' +
                       '%${0}{1}{2}{3}\n\n' +
                       '  {3}\n' +
                       '  |\n' +
                       '{2}-X-{0}\n' +
                       '  |\n' +
                       '  {1}\n').format(*line[2:]))

                raise Exception('obsolete code (unable to run)')
            elif line[:2] == '%^':
                exposed_char_str = line[2]  # FIXME: This only allows exposing one char!
            elif len(line) > 0 and line[0] == '%':
                continue
            else:
                for x, char in enumerate(char_list):
                    if char == exposed_char_str:
                        if is_singleton:
                            lib_char_obj_array[y][x] = SingletonLibReturnWarpChar(char)
                        else:
                            lib_char_obj_array[y][x] = LibWarpChar(char)

                        lib_char_obj_array[y][x].set_id(warp_id)

        self._setup_warps_for(lib_char_obj_array)

        # self._import_libraries(lib_char_obj_array)

        char_obj_array.extend(lib_char_obj_array)

    # ✓
    def _update_class_of_lib_chars(self, char_obj_array, lib_chars):
        is_singleton_dict = self._get_dict_of_is_singleton_for_lib_chars_in(char_obj_array)

        for y, line in enumerate(char_obj_array):
            if line[0] == '%':
                continue

            for x, char in enumerate(line):
                if char in lib_chars:
                    if is_singleton_dict[char]:
                        char_obj_array[y][x] = SingletonLibWarpChar(char)
                    else:
                        char_obj_array[y][x] = LibWarpChar(char)

    # ✓
    def _get_path_of_lib_file(self, filename):
        path_for_inside_program_dir = os.path.join(self.program_dir, filename)

        # Does it exist?
        if os.path.isfile(path_for_inside_program_dir):
            return path_for_inside_program_dir
        else:  # if not, look in the libs folder
            interpreter_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            return os.path.join(interpreter_dir, "libs", filename)

    # ✓✓
    @staticmethod
    def _get_lib_files_by_alias(map):
        """
        Get the librairy files by alias char defined.
        
        :param List[List[Char]] map: The map to import
        """

        filename_by_alias = {}

        for row in map:
            # get back the string from the Char array and remove the trailling white spaces
            line = ''.join(row).rstrip()

            # if it's an import
            if line.startswith('%!'):
                # Retrieve the filename and the alias from the line
                pieces = line[2:].split(' ')
                filename = pieces[0]
                alias = pieces[1]

                # add it to the mapping
                filename_by_alias[alias] = filename

        return filename_by_alias

    # ✓
    def _get_dict_of_is_singleton_for_lib_chars_in(self, char_obj_array):
        is_singleton_dict = {}

        for char_list in char_obj_array:
            line = ''.join(char_list).rstrip()

            if line[:2] == '%!':
                pieces = line[2:].split(' ')

                char = pieces[1]

                is_singleton_dict[char] = True

                # if len(pieces) >= 3 and pieces[2] == '&':
                #     is_singleton_dict[char] = True
                # else:
                #     is_singleton_dict[char] = False

        return is_singleton_dict

    # ✓
    def _connect_warps(self):
        for y, line in enumerate(self.map):
            if line[0] == '%':
                continue

            for x, char in enumerate(line):
                if char.isWarp() and not char.isSingletonLibReturnWarp():
                    warp_id = char.get_id()
                    companion_warp_loc = self._find_companion_warp_char_loc_of(warp_id, Pos(x, y))

                    if companion_warp_loc is not None:
                        self.map[y][x].set_dest_loc(companion_warp_loc)

    # ✓
    def _find_companion_warp_char_loc_of(self, warp_id, orig_pos: Pos):
        for y, line in enumerate(self.map):
            if line[0] == '%':
                continue

            if orig_pos.y == y:
                continue

            for x, char in enumerate(line):
                if char.isWarp() and char.get_id() == warp_id and orig_pos != (x, y):
                    return Pos(x, y)

    # ✓
    def _setup_warps_for(self, char_obj_array):
        self._correct_class_of_warp_chars_in(char_obj_array)

        # {letter: id}
        assigned_ids_for_letters = {}

        for (x, y), char in self._char_obj_array_iter_with_coords(char_obj_array):
            if char.isWarp() and char.get_id() is None:
                if char in assigned_ids_for_letters:
                    char_obj_array[y][x].set_id(assigned_ids_for_letters[char])
                else:
                    this_id = self._worldwide_warp_id_counter
                    assigned_ids_for_letters[char] = this_id
                    char.set_id(this_id)

                    self._worldwide_warp_id_counter += 1

    # ✓
    def _correct_class_of_warp_chars_in(self, char_obj_array):
        warp_list = self._get_warp_chars_list_from(char_obj_array)

        for y, line in enumerate(char_obj_array):
            for x, char in enumerate(line):
                if char in warp_list:
                    char_obj_array[y][x] = WarpChar(char)

    # TODO check if the char is inside of a ascii dots text string
    def _update_class_of_dots(self):
        for y, char_list in enumerate(self.map):
            last_was_backtick = False
            for x, char in enumerate(char_list):
                if char == '`':
                    if not last_was_backtick:
                        last_was_backtick = True
                    else:
                        break

                if char == '.':
                    self.map[y][x] = DotChar(char)

    # ✓
    def _setup_operators(self):
        for y, line in enumerate(self.map):
            for x, char in enumerate(line):
                if 0 < x < len(line) - 1:
                    if line[x - 1] == '{' and line[x + 1] == '}':
                        self.map[y][x] = CurlyOperChar(char)
                    elif line[x - 1] == '[' and line[x + 1] == ']':
                        self.map[y][x] = SquareOperChar(char)

    # ✓
    def _get_warp_chars_list_from(self, char_obj_array):
        warp_chars = []

        for char_list in char_obj_array:
            line = ''.join(char_list).rstrip()

            if line[:2] == '%$':
                string_with_chars = line[2:]
                string_with_chars = string_with_chars.rstrip()
                list_with_chars = list(string_with_chars)
                warp_chars.extend(list_with_chars)

        return warp_chars

    # ✓
    def _char_obj_array_iter(self, obj_array):
        for char_list in obj_array:
            for char in char_list:
                yield char

    # ✓
    def _char_obj_array_iter_with_coords(self, obj_array):
        for y, char_list in enumerate(obj_array):
            for x, char in enumerate(char_list):
                yield Pos(x, y), char

    # ✓✓
    @staticmethod
    def map_from_raw(raw_map: str):
        """
        Convert a code in a string to a usable map.

        This will suppress the comments and convert each chr of the string to the corresponding Char.
        Creates a 2D array accessible by map[row][col].
        :param str raw_map: The program as it is stored in files.
        """

        map = []

        # for each line
        for raw_line in raw_map.split('\n'):
            # removing the comments
            line = raw_line.partition('``')[0] + ' '
            # Convert the str to a list of Char
            line = [Char(c) for c in line]
            # add aech row to the map
            map.append(line)

        return map

#!/usr/bin/python3


import copy
import collections
from Snarl.src.util import flatten_2d_list
from Snarl.src.ITerrain import Tile, Room


class Level:
    def __init__(self, rooms, hallways, key, exit_room):
        """
        :param rooms: list of Rooms
        :param hallways: list of Hallways
        :param key: column(x), row(y) coordinate of the key
        :param exit_room: column(x), row(y) coordinate of the exit
        """
        self.__is_arguments_valid(rooms, hallways, key, exit_room)

        self.rooms = rooms
        self.hallways = hallways
        self.key = key
        self.exit_room = exit_room

    # -------------------------------- Checking Methods -------------------------------- #

    @staticmethod
    def __is_arguments_valid(rooms, hallways, key, exit_door):
        if not isinstance(rooms, list):
            raise ValueError("Rooms type is not valid. ")
        if not isinstance(hallways, list):
            raise ValueError("Hallways type is not valid. ")
        if Level.__is_rooms_overlap(rooms):
            raise ValueError("Rooms overlap. ")
        if Level.__is_hallways_overlap(hallways):
            raise ValueError("Hallways overlap. ")
        if not Level.__is_hallway_doors_match_rooms_door(rooms, hallways):
            raise ValueError("Hallways doors do not match. ")
        if Level.__is_hallways_overlap_rooms(rooms, hallways):
            raise ValueError("Hallways overlap with any rooms. ")
        if not Level.__is_exit_key_valid(rooms, exit_door, key):
            raise ValueError("Exit and key are not valid.  ")

    ###for the state test, have to allow level with no key
    @staticmethod
    def __is_exit_key_valid(rooms, exit_door, key):
        """
        check if exit_door and key position are valid, exit and key position must be located at Empty Tile

        :param rooms: list of Rooms
        :param exit_door: exit absolute position
        :param key: key absolute position
        :return: True if exit and key position are valid, False if they are invalid
        """
        if not isinstance(exit_door, tuple) or not isinstance(key, tuple):
            return False
        if len(exit_door) != 2 or len(key) != 2 or exit_door == key:
            if len(key) == 0:
                return True
            return False

        rooms_info = {}
        for room in rooms:
            rooms_info.update(room.convert_coord_to_map_dic())
        if len(key) != 0 and rooms_info.get(exit_door) == Tile.Empty and rooms_info.get(key) == Tile.Empty:
            return True
        else:
            return False

    @staticmethod
    def __is_rooms_overlap(rooms):
        """
        check if any room overlap by given list of rooms

        :param rooms: list of Rooms
        :return: True if any overlap, False if rooms are valid
        """
        rooms_list = [room for room in rooms]
        for i in range(len(rooms_list)):
            current_room = rooms_list[i]
            for j in range(i + 1, len(rooms_list)):
                other_room = rooms_list[j]
                if current_room.check_two_room_range_overlap(other_room):
                    return True
        return False

    @staticmethod
    def __is_hallway_doors_match_rooms_door(rooms, hallways):
        """
        check if hallways doors are matched

        :param rooms: a list of Rooms
        :param hallways: a list of Hallways
        :return: True if all hallways doors location match the door in the room, False if some do not match
        """
        rooms_door = flatten_2d_list([room.doors for room in rooms])
        hallways_door = flatten_2d_list([hallway.connected_rooms for hallway in hallways])
        for hallway_door in hallways_door:
            if hallway_door not in rooms_door:
                return False
        return True

    @staticmethod
    def __is_hallways_overlap(hallways):
        """
        check if hallways overlap

        :param hallways: a list of Hallways
        :return: True if any two overlap, False if no overlap
        """
        for i in range(len(hallways)):
            current_hallway = hallways[i]
            for j in range(i + 1, len(hallways)):
                other_hallway = hallways[j]
                if current_hallway.does_intersect_other(other_hallway):
                    return True
        return False

    @staticmethod
    def __is_hallways_overlap_rooms(rooms, hallways):
        """
        check if hallway overlap with room

        :param rooms: a list of Rooms
        :param hallways: a list of Hallways
        :return: True if any two overlap, False if no overlap
        """
        hallways_path = flatten_2d_list([list(hallway.convert_coord_to_map_dic().keys()) for hallway in hallways])
        rooms_range = [room.get_room_range() for room in rooms]
        for hallway_path in hallways_path:
            if any(Level.__is_coordinate_in_room_range(hallway_path, room_range) for room_range in rooms_range):
                return True
        return False

    @staticmethod
    def __is_coordinate_in_room_range(coord, room_range):
        """
        check if coordinate is inside of the room range, boundary excluded

        :param coord: coordinate, (x, y)
        :param room_range: two coordinates, (upper_left_coord, bottom_right_coord)
        :return: True if it is inside, else False
        """
        (upper_left_coord, bottom_right_coord) = room_range
        (x, y) = coord
        return upper_left_coord[0] < x < bottom_right_coord[0] and upper_left_coord[1] < y < bottom_right_coord[1]

    # -------------------------------- Getters -------------------------------- #
    def get_key_pos(self):
        return copy.deepcopy(self.key)

    def get_exit_pos(self):
        return copy.deepcopy(self.exit_room)

    def get_key_exit_pos(self) -> list:
        return [self.get_key_pos(), self.get_exit_pos()]

    def get_terrain_by_point(self, point):
        for room in self.rooms:
            if room.is_point_in(point):
                return room
        for hallway in self.hallways:
            if hallway.is_point_in(point):
                return hallway

    # -------------------------------- Main Methods -------------------------------- #

    def get_seen_tiles(self, position, seen_range) -> dict:
        """
        :param position: position
        :param seen_range: seen range
        :return: dictionary which key is position and value is the Tile type
        """
        x, y = position
        res = {}
        map_dic = self.generate_map_dic()
        for i in range(y - seen_range, y + seen_range + 1):
            for j in range(x - seen_range, x + seen_range + 1):
                res.update({(j, i): map_dic.get((j, i))})
        return res

    def get_reachable_tiles(self, character) -> set:
        position = character.get_position()
        around_range = character.get_move_range()
        move_restrict = character.get_move_restrict()
        map_dic = self.generate_map_dic()
        if position not in map_dic:
            raise ValueError("Position is not in level. ")
        else:
            res = {tuple(position)}

            for _ in range(around_range):
                for pos in list(res):
                    (x, y) = pos
                    up_pos = (x, y - 1)
                    left_pos = (x - 1, y)
                    right_pos = (x + 1, y)
                    bot_pos = (x, y + 1)
                    for possible_pos in [up_pos, left_pos, right_pos, bot_pos]:
                        current_tile = map_dic.get(possible_pos)
                        if current_tile is not None and current_tile not in move_restrict:
                            res.add(possible_pos)

            return res

    def get_reachable_terrains(self, position) -> list:
        x, y = position
        result = [(3, 3)]
        real_result = []
        seen_tiles = self.get_seen_tiles_for_player(position)
        top = seen_tiles[1][2]
        if top != 0:
            result.append((1, 2))
            top_t = seen_tiles[0][2]
            if top_t != 0:
                result.append((0, 2))
            top_l = seen_tiles[1][1]
            if top_l != 0:
                result.append((1, 1))
            top_r = seen_tiles[1][3]
            if top_r != 0:
                result.append((1, 3))

        bottom = seen_tiles[3][2]
        if bottom != 0:
            result.append((3, 2))
            bot_b = seen_tiles[4][2]
            if bot_b != 0:
                result.append((4, 2))
            bot_l = seen_tiles[3][1]
            if bot_l != 0:
                result.append((3, 1))
            bot_r = seen_tiles[3][3]
            if bot_r != 0:
                result.append((3, 3))

        left = seen_tiles[2][1]
        if left != 0:
            result.append((2, 1))
            left_l = seen_tiles[2][0]
            if left_l != 0:
                result.append((2, 0))
            left_t = seen_tiles[1][1]
            if left_t != 0:
                result.append((1, 1))
            left_b = seen_tiles[3][1]
            if left_b != 0:
                result.append((3, 1))

        right = seen_tiles[2][3]
        if right != 0:
            result.append((2, 3))
            right_r = seen_tiles[2][4]
            if right_r != 0:
                result.append((2, 4))
            right_t = seen_tiles[1][3]
            if right_t != 0:
                result.append((1, 3))
            right_b = seen_tiles[3][3]
            if right_b != 0:
                result.append((3, 3))
        result = list(set(result))
        for point in result:
            real_result.append((point[0] + x - 3, point[1] + y - 3))
        return real_result

    def get_seen_tiles_for_player(self, position) -> list:
        # TODO: not flexbile

        x, y = position
        res = [[0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0]]
        for i in range(y - 2, y + 3):
            for j in range(x - 2, x + 3):
                tile_point = (j, i)
                traversable, locations_type, neighbor_origins, tile_type = self.is_tile_traversable(tile_point)
                if tile_type == "door":
                    res[i - y + 2][j - x + 2] = 2
                elif tile_type == "floor":
                    res[i - y + 2][j - x + 2] = 1
                else:
                    pass
        return res

    def get_seen_tiles_for_adversary(self, position) -> list:
        return self.__get_all_tiles()

    def get_seen_objects_for_adversary(self, position) -> list:
        return [self.load_exit_json(), self.load_key_json()]

    def get_bot_right_position(self):
        map_coord = self.generate_map_dic().keys()
        max_col_num = max([x for x, _ in map_coord])
        max_row_num = max([y for _, y in map_coord])
        return max_col_num, max_row_num

    def __get_all_tiles(self) -> list:
        max_col_num, max_row_num = self.get_bot_right_position()

        res = [[0] * (max_col_num+1) for _ in range(max_row_num+1)]
        for i in range(max_row_num + 1):
            for j in range(max_col_num + 1):
                tile_point = (j, i)
                traversable, locations_type, neighbor_origins, tile_type = self.is_tile_traversable(tile_point)
                if tile_type == "door":
                    res[i][j] = 2
                elif tile_type == "floor":
                    res[i][j] = 1
        # print(' __get_all_tiles __get_all_tiles __get_all_tiles __get_all_tiles __get_all_tiles')
        # print(self.get_bot_right_position())
        # print(res)
        return res

    def generate_map_dic(self):
        """
        :return: generate the dictionary of the level information, including rooms and hallways
        """
        res = {}
        for room in self.rooms:
            res.update(room.convert_coord_to_map_dic())
        for hallway in self.hallways:
            res.update(hallway.convert_coord_to_map_dic())
        return res

    def generate_room_dic(self):
        res = {}
        for room in self.rooms:
            res.update(room.convert_coord_to_map_dic())
        return res

    def is_tile_traversable(self, point):
        """
        TODO
        true if the tile is traversable
        (door or “floor”, i.e., type 1 or 2 in Milestone 3’s testing task or a hallway),
        false otherwise.
        """
        traversable = False
        locations_type = "void"
        neighbor_origins = []
        tile_type = "nothing"
        # check if the given point is in any of the rooms
        for room in self.rooms:
            diction = room.convert_coord_to_map_dic()
            # print(diction)
            # check if the given point is in the room
            if point in diction.keys():
                neighbor_origins = self.find_neighbor_rooms(room)
                locations_type = "room"
                room_tile_graph = diction[point]
                if room_tile_graph == Tile.Wall:
                    traversable = False
                    tile_type = "wall"
                    break
                if room_tile_graph == Tile.Door:
                    traversable = True
                    tile_type = "door"
                    return traversable, locations_type, neighbor_origins, tile_type
                if room_tile_graph == Tile.Empty:
                    traversable = True
                    tile_type = "floor"
                    break

        for hallway in self.hallways:
            diction = hallway.convert_coord_to_map_dic()
            if point in diction.keys():
                neighbor_origins = self.find_neighbor_rooms_using_doors(hallway.connected_rooms)
                locations_type = "hallway"
                traversable = True
                tile_type = "floor"
                break

        return traversable, locations_type, neighbor_origins, tile_type

    def object_type(self, point):
        """
        Type of the object if the tile contains a key or an exit. Otherwise null.
        """
        if point == self.exit_room:
            return "exit"
        elif point == self.key:
            return "key"
        else:
            return None

    def __str__(self):
        """
        :return: a ASCII art representation of the whole level
        """
        res = ''
        map_dictionary = self.generate_map_dic()
        col_length = max([row for (row, col) in map_dictionary.keys()])
        row_length = max([col for (row, col) in map_dictionary.keys()])
        for row in range(row_length + 1):
            for col in range(col_length + 1):
                target = map_dictionary.get((col, row))
                if target is not None:
                    res += target.__str__() + ' '
                else:
                    res += '  '
            res += '\n'

        return res

    def find_neighbor_rooms(self, room):
        """
        An array of room origins that are immediately reachable from the current room or hallway
        (if the given point is in one or the other)
        """
        res = []
        for r in self.rooms:
            for other_door in r.doors:
                for this_door in room.doors:
                    connect = [this_door, other_door]
                    for hw in self.hallways:
                        if collections.Counter(connect) == collections.Counter(hw.connected_rooms):
                            res.append(r.get_upper_left_position())
        return res

    def find_neighbor_rooms_using_doors(self, doors):
        """
        For a hallway, these are the room origins which it connects
        """
        res = []
        door0 = doors[0]
        door1 = doors[1]
        for r in self.rooms:
            if door0 in r.doors:
                res.append(r.get_upper_left_position())
            if door1 in r.doors:
                res.append(r.get_upper_left_position())
        return res

    def load_key_json(self):
        return {"type": "key", "position": self.get_key_pos()}

    def load_exit_json(self):
        return {"type": "exit", "position": self.get_exit_pos()}

    def get_all_room_empty_points(self):
        result = []
        most_left, most_right, most_top, most_bottom = None, None, None, None
        for room in self.rooms:
            left_top, right_bottom = Room.get_room_range(room)
            left = left_top[0]
            top = left_top[1]
            right = right_bottom[0]
            bottom = right_bottom[1]
            if most_left == None:
                most_left = left
            else:
                most_left = min(left, most_left)
            if most_right == None:
                most_right = right
            else:
                most_right = max(right, most_right)
            if most_top == None:
                most_top = top
            else:
                most_top = min(top, most_top)
            if most_bottom == None:
                most_bottom = bottom
            else:
                most_bottom = max(bottom, most_bottom)
        for x in range(most_left, most_right + 1):
            for y in range(most_top, most_bottom + 1):
                traversable, locations_type, neighbor_origins, ti_type = self.is_tile_traversable((x, y))
                if ti_type == "floor":
                    result.append((x, y))
        return result

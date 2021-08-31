import copy
from enum import Enum
from Snarl.src.util import flatten_2d_list


class Tile(Enum):
    Wall = 'X'
    Empty = '.'
    Door = '□'

    def __str__(self):
        return str(self.value)


class ITerrain:
    def __convert_absolute_pos_to_relative(self, position):
        raise NotImplementedError()

    def is_point_in(self, position):
        raise NotImplementedError()

    def get_tile_by_point(self, point, absolute=True):
        raise NotImplementedError()

    def convert_coord_to_map_dic(self):
        raise NotImplementedError()

    def get_seen_tiles(self, position, seen_range, absolute=True):
        if not self.is_point_in(position):
            raise ValueError("Position is not in this room. ")
        else:
            res = []
            (x, y) = position if absolute else self.__convert_absolute_pos_to_relative(position)
            for row in range(y - seen_range, y + seen_range + 1):
                for col in range(x - seen_range, x + seen_range + 1):
                    res.append({(col, row): self.get_tile_by_point((col, row))})
            return res

    # def get_traversable_points(self, character):
    #     position = character.get_position()
    #     around_range = character.get_move_range()
    #     move_restrict = character.get_move_restrict()
    #
    #     if not self.is_point_in(position):
    #         raise ValueError("Position is not in this room. ")
    #     else:
    #         res = []
    #         (x, y) = position
    #         offset = 1
    #         is_inc = True
    #         for row in range(y - around_range, y + around_range + 1):
    #             for col in range(x - offset + 1, x + offset):
    #
    #                 current_tile = self.get_tile_by_point((col, row))
    #                 if current_tile is not None and current_tile not in move_restrict:
    #                     res.append((col, row))
    #             if is_inc:
    #                 offset += 1
    #             else:
    #                 offset -= 1
    #
    #             if offset > around_range:
    #                 is_inc = False
    #         return res




class Room(ITerrain):

    def __init__(self, upper_left_position, dimensions, layout, doors):
        """
        :param upper_left_position: upper left position of x, y coordinate (starting from (0, 0))
        :param dimensions: a tuple of x, y representing dimension, s.t. (3,4) means 3 * 4 (number of col, number of row)
        :param layout: 2d list of the W (wall tiles) or E (empty tiles) or D (door)
        :param doors: a list of doors position (has to be at the boundary dimensions of the room)
        """

        self.__is_arguments_valid(upper_left_position, dimensions, layout, doors)

        self.upper_left_position = upper_left_position
        self.dimensions = dimensions
        self.layout = layout
        self.doors = doors

    # -------------------------------- Checking Methods -------------------------------- #
    @staticmethod
    def __is_arguments_valid(upper_left_position, dimensions, layout, doors):
        if not Room.__is_upper_left_position_valid(upper_left_position):
            raise ValueError("Room upper left position is invalid. ")
        if not Room.__is_dimensions_position_valid(dimensions):
            raise ValueError("Room dimension is invalid. ")
        if not Room.__is_door_valid(doors, upper_left_position, dimensions):
            raise ValueError("Room door has invalid argument. ")
        if not Room.__is_layout_valid(layout, dimensions):
            raise ValueError("Room layout has invalid argument. ")
        if not isinstance(doors, list):
            raise ValueError("Room doors has invalid argument. ")

    @staticmethod
    def __is_upper_left_position_valid(upper_left_position):
        if (not isinstance(upper_left_position, tuple)) or len(upper_left_position) != 2:
            return False
        x, y = upper_left_position
        return x >= 0 and y >= 0

    @staticmethod
    def __is_dimensions_position_valid(dimensions):
        if (not isinstance(dimensions, tuple)) or len(dimensions) != 2:
            return False
        x, y = dimensions
        return x >= 1 and y >= 1

    @staticmethod
    def __is_door_valid(doors, upper_left_position, dimensions):
        for door in doors:
            if door not in Room.__get_bound_coord(upper_left_position, dimensions):
                return False
        return True

    @staticmethod
    def __is_layout_valid(layout, dimensions):
        """
        currently, the lists in the layout represent a column
        """
        (dim_x, dim_y) = dimensions
        if not isinstance(layout, list):
            return False
        if len(layout) != dim_y:
            return False
        for row in layout:
            if len(row) != dim_x:
                return False
        return True

    @staticmethod
    def __get_bound_coord(upper_left_position, dimensions):
        """

        :param upper_left_position: upper_left_position
        :param dimensions: dimensions
        :return: a list of all boundary coordinates
        """
        (temp_x, temp_y) = upper_left_position
        (dim_x, dim_y) = dimensions
        res = []
        for x in range(temp_x, temp_x + dim_x):
            if x == temp_x or x == temp_x + dim_x - 1:
                for y in range(temp_y, temp_y + dim_y):
                    res.append((x, y))
            else:
                res.append((x, temp_y))
                res.append((x, temp_y + dim_y - 1))
                continue
        return res

    # -------------------------------- Getters -------------------------------- #

    def get_upper_left_position(self):
        return copy.deepcopy(self.upper_left_position)

    def get_room_range(self):
        """
        :return: the upper_left_position and bottom_right_position
        """
        upper_left_position = copy.deepcopy(self.upper_left_position)
        bottom_right_position = (self.upper_left_position[0] + self.dimensions[0] - 1,
                                 self.upper_left_position[1] + self.dimensions[1] - 1)
        return [upper_left_position, bottom_right_position]

    def get_tile_by_point(self, point, absolute=True):
        """
        :param point: (x, y) coordinate within the whole map
        :param absolute: if point is absolute, else should convert to absolute point first
        :return: Tile in that given point, None if the point is outside of the room
        """
        point = point if absolute else self.__convert_absolute_pos_to_relative(point)
        if self.is_point_in(point):
            (upper_left_x, upper_left_y) = self.upper_left_position
            (relative_x, relative_y) = (point[0] - upper_left_x, point[1] - upper_left_y)

            return self.layout[relative_y][relative_x]
        else:
            return None

    # -------------------------------- Main Methods -------------------------------- #
    def convert_coord_to_map_dic(self):
        """
        :return: room grids information of dictionary, key is a tuple of x, y coordinate and value is a Tile
        """
        (init_x, init_y) = self.upper_left_position
        (dim_x, dim_y) = self.dimensions
        res = {}

        for row in range(dim_y):
            for col in range(dim_x):
                res[(col + init_x, row + init_y)] = self.layout[row][col]
        for door in self.doors:
            res.update({door: Tile.Door})

        return res

    def get_seen_tiles(self, position, seen_range, absolute=True):
        if not self.is_point_in(position):
            raise ValueError("Position is not in this room. ")
        else:
            res = []
            (x, y) = position if absolute else self.__convert_absolute_pos_to_relative(position)
            for row in range(y - seen_range, y + seen_range + 1):
                for col in range(x - seen_range, x + seen_range + 1):
                    res.append({(col, row): self.get_tile_by_point((col, row))})
            return res

    # def get_traversable_points(self, character):
    #     """
    #     get surrounding tiles by given character
    #
    #     :param character: a given character (move_range, position, move_requirement)
    #     :return: list of surrounding coordinate that can be reached
    #     """
    #     position = character.get_position()
    #     around_range = character.get_move_range()
    #     move_restrict = character.get_move_restrict()
    #
    #     if not self.is_point_in(position):
    #         raise ValueError("Position is not in this room. ")
    #     else:
    #         res = []
    #         (x, y) = position
    #         offset = 1
    #         is_inc = True
    #         for row in range(y - around_range, y + around_range + 1):
    #             for col in range(x - offset + 1, x + offset):
    #
    #                 current_tile = self.get_tile_by_point((col, row))
    #                 if current_tile is not None and current_tile not in move_restrict and (col, row) != position:
    #                     res.append((col, row))
    #             if is_inc:
    #                 offset += 1
    #             else:
    #                 offset -= 1
    #
    #             if offset > around_range:
    #                 is_inc = False
    #         return res

    def check_two_room_range_overlap(self, other_room):
        """
        :param other_room: compared room
        :return: True if two room overlap, False if no overlap
        """
        room_range1 = self.get_room_range()
        room_range2 = other_room.get_room_range()
        x_range1 = room_range1[0][0], room_range1[1][0]
        x_range2 = room_range2[0][0], room_range2[1][0]
        y_range1 = room_range1[0][1], room_range1[1][1]
        y_range2 = room_range2[0][1], room_range2[1][1]
        if Room.__check_overlap_1d(x_range1, x_range2) and Room.__check_overlap_1d(y_range1, y_range2):
            return True
        else:
            return False

    # -------------------------------- Helper Methods -------------------------------- #
    @staticmethod
    def __check_overlap_1d(range1, range2):
        """
        check if any range overlap

        :param range1: a tuple of size 2 representing start position and end position in 1-d
        :param range2: a tuple of size 2 representing start position and end position in 1-d
        :return: True if two range overlap, False if no range overlap (it can next to each other)
        """
        current_min, current_max = range1
        other_min, other_max = range2

        if current_min < other_min < current_max or current_min < other_max < current_max or \
                (other_min <= current_min and current_max <= other_max):
            return True
        else:
            return False

    def is_point_in(self, point):
        """
        check if a given point (x, y) is in this room
        :param point: (x, y) absolute coordinate
        :return: True if this point is in the room, False if this point is outside
        """
        (x, y) = point
        upper_left_position, bottom_right_position = self.get_room_range()
        (min_x, min_y) = upper_left_position
        (max_x, max_y) = bottom_right_position
        return min_x <= x <= max_x and min_y <= y <= max_y

    def __convert_absolute_pos_to_relative(self, position):
        if not self.is_point_in(position):
            raise ValueError("Position is not in this room. ")
        else:
            (min_x, min_y) = self.upper_left_position
            (x, y) = position
            return x - min_x, y - min_y


class Hallway(ITerrain):

    def __init__(self, connected_rooms, way_points):
        """
        :param connected_rooms: list of two coordinates that has to be the coordinate of doors
        :param way_points: list of way points that indicate how the hallway goes
        """
        self.__is_arguments_valid(connected_rooms, way_points)
        self.connected_rooms = connected_rooms
        self.way_points = way_points

    # -------------------------------- Checking Methods -------------------------------- #

    @staticmethod
    def __is_arguments_valid(connected_rooms, way_points):
        if not Hallway.__is_connected_rooms_valid(connected_rooms):
            raise ValueError("Connected rooms are invalid. ", connected_rooms)
        if not Hallway.__is_way_points_valid(connected_rooms, way_points):
            raise ValueError("Way points are invalid. ", way_points)

    @staticmethod
    def __is_connected_rooms_valid(connected_rooms):
        """
        :param connected_rooms: list of the coordinates of connected room doors, must be size of 2
        """
        if not isinstance(connected_rooms, list) or len(connected_rooms) != 2:
            return False
        return True

    @staticmethod
    def __is_way_points_valid(connected_rooms, way_points):
        """
        check way points must be horizontal or vertical to the adjacent way points or endpoints

        :param connected_rooms: list of two coordinates that has to the coordinate of doors
        :param way_points: list of way points that indicate how the hallway goes
        :return: False if way points is not valid, True if all arguments are valid
        """
        if not isinstance(way_points, list):
            return False

        res = True
        way_path = Hallway.__get_way_path(connected_rooms, way_points)
        if len(way_path) > 0:

            current_x, current_y = way_path[0]
            for i in range(1, len(way_path)):
                other_point = way_path[i]
                res = (current_x == other_point[0] or current_y == other_point[1]) and res
                current_x, current_y = other_point
        return res

    # -------------------------------- Main Methods -------------------------------- #

    def convert_coord_to_map_dic(self):
        """
        :return: hallway grids information of dictionary, key is a tuple of x, y coordinate and value is a Tile

        """
        res = {}
        way_path = Hallway.__get_way_path(self.connected_rooms, self.way_points)
        start_point = way_path[0]
        for point in way_path[1:]:
            res.update(
                {coord: Tile.Empty for coord in Hallway.__generate_all_coord_between_two_point(start_point, point)})
            start_point = point
        res.update({coord: Tile.Door for coord in self.connected_rooms})
        return res

    def get_tile_by_point(self, point, absolute=True):
        """

        :param point: (x, y) absolute coordinate within the whole map
        :param absolute: absolute is not applicable for Hallway
        :return: Tile in that given point, None if the point is outside of the room
        """
        return self.convert_coord_to_map_dic().get(point)

    def does_intersect_other(self, other_hallway):
        current_map_position = self.convert_coord_to_map_dic().keys()
        other_map_dic = other_hallway.convert_coord_to_map_dic().keys()
        for pos in current_map_position:
            if pos in other_map_dic:
                return True
        return False

    # -------------------------------- Helper Methods -------------------------------- #

    def __convert_absolute_pos_to_relative(self, position):
        raise ValueError("Hallway has to been filled in relative position. ")

    def is_point_in(self, position):
        """
        only consider if a given position is exactly inside of the hallway, not the position of the door of rooms
        :param position: given point
        :return: boolean if a point is in the given hallway (not include the connected rooms)
        """
        all_way_path = self.__get_way_path(self.connected_rooms, self.way_points)
        inner_points = [p for p in all_way_path if p not in self.connected_rooms]
        return position in inner_points

    @staticmethod
    def __get_way_path(connected_rooms, way_points):
        """
        get all way of coordinate regarding the given connected rooms and way points

        :param connected_rooms: list of two coordinates that has to the coordinate of doors
        :param way_points: list of way points that indicate how the hallway goes
        :return: a list of coordinate including the way points and the points between the way points
        """

        res = []
        from_room = connected_rooms[0]
        to_room = connected_rooms[1]

        way_points_copy = copy.deepcopy(way_points)
        way_points_copy.insert(0, from_room)
        way_points.append(to_room)

        for start_point, next_point in zip(way_points_copy, way_points):
            res.append(Hallway.__generate_all_coord_between_two_point(start_point, next_point))
        return flatten_2d_list(res)

    @staticmethod
    def __generate_all_coord_between_two_point(start_point, end_point):
        """
        two point are switch, two points must be horizontal or vertical to each other
        :param start_point: one point from start
        :param end_point: one point to the end
        :return: a list of coordinates (x, y) between two points
        """
        min_x = min(start_point[0], end_point[0])
        max_x = max(start_point[0], end_point[0])
        min_y = min(start_point[1], end_point[1])
        max_y = max(start_point[1], end_point[1])
        if Hallway.__check_two_point_horizontal(start_point, end_point):
            return [(x, start_point[1]) for x in range(min_x, max_x + 1)]
        elif Hallway.__check_two_point_vertical(start_point, end_point):
            return [(start_point[0], y) for y in range(min_y, max_y + 1)]
        else:
            raise ValueError("Points are not vertical or horizontal. \n",
                             "start_point and end_point:", start_point, end_point)

    @staticmethod
    def __check_two_point_horizontal(start_point, end_point):
        return start_point[1] == end_point[1]

    @staticmethod
    def __check_two_point_vertical(start_point, end_point):
        return start_point[0] == end_point[0]

#!/usr/bin/python3
import json
import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(os.path.split(rootPath)[0])

from Snarl.src.ITerrain import Tile, Room
from Snarl.src import util

def read_input_to_json():
    data = ''
    for line in sys.stdin:
        data += line.strip()
    try:
        expression = json.loads(data)
    except json.JSONDecodeError:
        raise ValueError("Input cannot parsed as json. ")
    # if all([s not in list(expression[0]) for s in ['type', 'origin', 'bounds', 'layout']]):
    #     raise ValueError("Input is invalid. ")
    # elif not isinstance(expression[1], list) or len(expression[1]) != 2:
    #     raise ValueError("Input is invalid. ")
    return expression


def convert_numbers_layout(origin, numbers):
    res = []
    doors = []
    x = origin[0]
    y = origin[1]
    for row in numbers:
        x = origin[0]
        row_res = []
        for num in row:
            if num == 0:
                row_res.append(Tile.Wall)
            elif num == 1:
                row_res.append(Tile.Empty)
            elif num == 2:
                row_res.append(Tile.Door)
                doors.append((x, y))
            x += 1
        res.append(row_res)
        y += 1
    return res, doors


def json_init_room(json_expression):
    if all([s not in list(json_expression) for s in ['type', 'origin', 'bounds', 'layout']]):
        raise ValueError("invalid room input. ")
    origin = (json_expression['origin'][1], json_expression['origin'][0])
    bounds = (json_expression['bounds']['columns'], json_expression['bounds']['rows'])
    layout, doors = convert_numbers_layout(origin, json_expression['layout'])
    # print("doors: ", doors)
    room = Room(origin, bounds, layout, doors)
    return room


def main():
    js = read_input_to_json()

    room = json_init_room(js[0])
    # print(room.convert_coord_to_map_dic())
    # print(Room([room], []).__str__())
    in_point = js[1]
    point = util.switch_xy_coordinate(in_point)
    room_pos = util.switch_xy_coordinate(room.get_upper_left_position())

    if room.__is_point_in_room(point):
        traversable_points = [util.switch_xy_coordinate(p) for p in room.get_traversable_points(point, 1)]
        output = ["Success: Traversable points from ", in_point, " in room at ", room_pos, " are ", traversable_points]
    else:
        output = ["Failure: Point ", in_point, " is not in room at ", room_pos]
    print(json.dumps(output))


if __name__ == '__main__':
    main()

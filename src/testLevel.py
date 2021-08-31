#!/usr/bin/python3

import json
import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(os.path.split(rootPath)[0])

import Snarl.src.util as util
from Snarl.src.Level import Level
from Snarl.src.ITerrain import Tile, Room, Hallway
from Snarl.src.testRoom import json_init_room, read_input_to_json


# {
#   "rooms": (room-list),
#   "hallways": (hall-list),
#   "objects": [ { "type": "key", "position": (point) }, 
#                { "type": "exit", "position": (point) } ]
# }

# def __init__(self, rooms, hallways, key, exit):
def json_init_level(json_expression):
    rooms = []
    hallways = []
    for r in json_expression['rooms']:
        rooms.append(json_init_room(r))
    for h in json_expression['hallways']:
        hallways.append(init_hallway(h))
    objects = json_expression['objects']
    key = ()
    exit = ()
    for o in objects:
        if o['type'] == "key":
            key = util.switch_xy_coordinate(o['position'])
        if o['type'] == "exit":
            exit = util.switch_xy_coordinate(o['position'])

    level = Level(rooms=rooms, hallways=hallways, key=key, exit_room=exit)
    return level


# def __init__(self, connected_rooms, way_points):
def init_hallway(json_expression):
    if all([s not in list(json_expression) for s in ['from', 'to', 'waypoints']]):
        raise ValueError("invalid hallway input. ")
    connectedRooms = [(json_expression['from'][1], json_expression['from'][0]),
                      (json_expression['to'][1], json_expression['to'][0])]
    waypoints = []
    for wp in json_expression['waypoints']:
        waypoints.append(util.switch_xy_coordinate(list(wp)))
    hallway = Hallway(connected_rooms=connectedRooms, way_points=waypoints)
    return hallway


def main():

    js = read_input_to_json()
    level1 = json_init_level(js[0])
    in_point = js[1]
    point = util.switch_xy_coordinate(in_point)

    # if room.is_point_in_room(point):
    #     traversable_points = [util.switch_xy_coordinate(p) for p in room.get_traversable_points(point, 1)]
    #     output = ["Success: Traversable points from ", in_point, " in room at ", room_pos, " are ", traversable_points]
    # else:
    #     output = ["Failure: Point ", in_point, " is not in room at ", room_pos]
    #     {
    #   "traversable": (boolean),
    #   "object": (maybe-object-type),
    #   "type": (room-or-hallway-or-void),
    #   "reachable": (point-list)
    # }

    # traversable, locations_type, neighbor_origins
    reachable = []
    reachable_reverse = []
    traversable_bool, point_type, reachable_reverse, tile_type = Level.is_tile_traversable(level1, point)
    obj = Level.object_type(level1, point)
    for r in reachable_reverse:
        reachable.append(util.switch_xy_coordinate(r))

    output = {
        "traversable": traversable_bool,
        "object": obj,
        "type": point_type,
        "reachable": reachable
    }
    print(json.dumps(output))


if __name__ == '__main__':
    main()

#!/usr/bin/python3
import ast
import socket
import json
import os
import sys

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(os.path.split(rootPath)[0])

from src.GameManager import GameManager
from src.RuleChecker import RuleChecker
from src.util import send_msg, receive_msg
from src.ICharacter import Player
from src.ITerrain import Tile

from Snarl.src.Remote.IClient import IClient


class ClientPlayer(IClient):

    def __init__(self, ip: str, port: int):
        super().__init__(ip, port)

    def receive_adversary_update_message(self, msg):
        raise ValueError("Player would not receive the adversary update message.")

    def display_vision(self, update_message):
        object_list = update_message["objects"]
        actor_position_list = update_message["actors"]

        p_position = update_message["position"]
        x, y = p_position
        seen_range = 2
        min_row_length = y - seen_range
        max_row_length = y + seen_range
        min_col_length = x - seen_range
        max_col_length = x + seen_range
        vision = {}
        layout_list = update_message["layout"]

        for i in range(y - seen_range, y + seen_range + 1):
            for j in range(x - seen_range, x + seen_range + 1):
                point_in_layout = (j - x + 2, i - y + 2)
                point_x, point_y = point_in_layout
                type_num = layout_list[point_y][point_x]
                res = Tile.Wall
                if type_num == 1:
                    res = Tile.Empty
                elif type_num == 2:
                    res = Tile.Door
                else:
                    pass
                vision.update({(j, i): res})
        # print(vision)

        result = ' '
        for col in range(min_col_length, max_col_length + 1):
            result += str(col).rjust(2)
        result += '\n'
        for row in range(min_row_length, max_row_length + 1):
            result += str(row).rjust(2) + ' '
            for col in range(min_col_length, max_col_length + 1):
                point = (col, row)
                object_type = self.get_object_type_by_coord_from_two_lists(point, object_list, actor_position_list)
                if [point[0], point[1]] == p_position:
                    result += '\x1b[1;31;40m' + 'P' + '\x1b[0m' + ' '
                elif object_type == 'player':
                    result += 'P' + ' '
                elif object_type == 'ghost':
                    result += 'G' + ' '
                elif object_type == 'zombie':
                    result += 'Z' + ' '
                elif object_type == 'key':
                    result += '\x1b[1;33;40m' + 'K' + '\x1b[0m' + ' '
                elif object_type == 'exit':
                    result += '\x1b[1;33;40m' + 'E' + '\x1b[0m' + ' '
                else:
                    target = vision.get(point)
                    if target is not None:
                        result += target.__str__() + ' '
                    else:
                        result += '  '
            result += '\n'

        return result

    def choose_move(self):
        print("Time to make a move!\n"
              "Enter a point, in format such as (1, 3) to make a move attempt.\n"
              "Enter None to stay. ")
        # move_input = input("Enter a point to move to:\n")
        while True:
            to_point = input('choose a move: \n')
            if to_point.strip() == 'None':
                to_point = None
                break
            else:
                try:
                    move = ast.literal_eval(to_point)
                except Exception:
                    # print(e)
                    print("Invalid. Choose a new move ...")
                    continue
                if isinstance(move, tuple) and len(move) == 2 and all(isinstance(v, int) for v in move):
                    to_point = move
                    break
        move_json = {"type": "move", "to": to_point}
        move_msg = json.dumps(move_json)
        send_msg(self.sock, move_msg)


if __name__ == '__main__':
    c = ClientPlayer("127.0.0.1", 45678)
    ClientPlayer.run(c)

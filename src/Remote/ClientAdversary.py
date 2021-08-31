#!/usr/bin/python3
import ast
import socket
import json
import os
import sys

from Snarl.src.Remote.IClient import IClient
from Snarl.src.GameManager import GameManager
from Snarl.src.RuleChecker import RuleChecker
from Snarl.src.util import send_msg, receive_msg
from Snarl.src.ICharacter import Player
from Snarl.src.ITerrain import Tile


class ClientAdversary(IClient):

    def __init__(self, ip: str, port: int):
        super().__init__(ip, port)

    def receive_player_update_message(self, msg):
        raise ValueError("Adversary would not receive the player update message.")

    def choose_move(self):
        print("Time to make a move!\n"
              "Enter a point, in format such as (1, 3) to make a move attempt.\n"
              "Enter None to stay. Only valid when adversary have no move to choose. ")
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

    def display_vision(self, update_message):
        object_list = update_message["objects"]
        actor_position_list = update_message["actors"]
        p_position = update_message["position"]
        layout_list = update_message["layout"]

        i = 0

        vision = {}
        for row in layout_list:
            j = 0
            for type_num in row:
                # point_in_layout = (j - x + 2, i - y + 2)
                # point_x, point_y = point_in_layout
                # type_num = layout_list[point_y][point_x]

                if type_num == 1:
                    res = Tile.Empty
                elif type_num == 2:
                    res = Tile.Door
                else:
                    res = Tile.Wall
                vision.update({(j, i): res})
                j += 1
            i += 1
        # print('-------------test------------')
        # print(vision)
        # for row in layout_list:
        #     print(row)
        # print(vision)
        max_col_length = len(layout_list[0])
        max_row_length = len(layout_list)
        result = ' '
        for col in range(max_col_length):
            result += str(col).rjust(2)
        result += '\n'
        for row in range(max_row_length):
            result += str(row).rjust(2) + ' '
            for col in range(max_col_length):
                point = (col, row)
                object_type = self.get_object_type_by_coord_from_two_lists(point, object_list, actor_position_list)

                if object_type == 'player':
                    result += 'P' + ' '
                elif object_type == 'ghost':
                    if [point[0], point[1]] == p_position:
                        result += '\x1b[1;34;40m' + 'G' + '\x1b[0m' + ' '
                    else:
                        result += 'G' + ' '
                elif object_type == 'zombie':
                    if [point[0], point[1]] == p_position:
                        result += '\x1b[1;32;40m' + 'Z' + '\x1b[0m' + ' '
                    else:
                        result += 'Z' + ' '
                elif object_type == 'key':
                    result += 'K' + ' '
                elif object_type == 'exit':
                    result += 'E' + ' '
                else:
                    target = vision.get(point)
                    if target is not None:
                        result += target.__str__() + ' '
                    else:
                        result += '  '
            result += '\n'

        return result


if __name__ == '__main__':
    c = ClientAdversary("127.0.0.1", 45678)
    ClientAdversary.run(c)

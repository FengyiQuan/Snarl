#!/usr/bin/python3
import json
import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(os.path.split(rootPath)[0])

import math
import argparse

from Snarl.src.testRoom import read_input_to_json
from Snarl.src.testLevel import json_init_level
from Snarl.src.GameManager import GameManager


def command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument('--levels', type=str, default='snarl.levels',
                        help="FILENAME is the name of a file containing JSON level specifications")
    parser.add_argument('--players', type=int, default=1,
                        help='where 1 <= N <= 4 is the number of players')
    parser.add_argument('--start', type=int, default=1,
                        help='where N is the level to start from')
    parser.add_argument('--observe', action='store_true',
                        help='If this option is given, the full level should be presented instead of the player view.')

    args = parser.parse_args()

    return args


def read_file_to_json(file):
    f = open('../src/levels_info/' + file, "r")
    data = ''
    for line in f.read():
        data += line.strip()
    try:

        expression = parse_input(data)
    except json.JSONDecodeError:
        raise ValueError("Input cannot parsed as json. ")
    return expression


def parse_input(expression):
    expression = expression.replace('\n', '')

    result_list = []
    work_list = []
    result = ""
    for e in expression:
        if (result.isnumeric() or result == "") and e.isnumeric():
            result += e
            continue
        elif result.isnumeric():
            result_list.append(int(result))
            result = ""
            result += e
            if e == '{':
                work_list.append('}')
            elif e == '[':
                work_list.append(']')
            elif e == '"' and work_list and work_list[-1] == '"':
                work_list.pop()
            elif e == '"':
                work_list.append('"')
            else:
                if work_list and e == work_list[-1]:
                    work_list.pop()
            continue

        if e == " " and work_list:
            result += e
            continue

        elif e == " ":
            continue

        result += e

        if e == '{':
            work_list.append('}')
        elif e == '[':
            work_list.append(']')
        elif e == '"' and work_list and work_list[-1] == '"':
            work_list.pop()
        elif e == '"':
            work_list.append('"')
        else:
            if work_list and e == work_list[-1]:
                work_list.pop()

        if not work_list:
            result_list.append(result)
            result = ""

    final = []
    for item in result_list:
        if isinstance(item, int):
            final.append(item)
        else:
            final.append(json.loads(item))
    return final


def levels_parser(file):
    js = read_file_to_json(file)
    level_num = int(js[0])
    result_level_list = []
    for n in range(1, level_num + 1):
        lvl = json_init_level(js[n])
        result_level_list.append(lvl)
    return level_num, result_level_list


# def levels_init(path):
#     f = open(path, "r")
#     level_num = f.readline()
#     levels = f.read()


def main():
    pass


if __name__ == '__main__':
    args = command_line()
    path = args.levels
    level_num, levels = levels_parser(path)
    players_num = args.players
    start = args.start
    observe = args.observe
    # for i in levels:
    #     print(i)
    # print(level_num, len(levels))
    if level_num != len(levels):
        print('.levels file has invalid natural and levels, given: natural ' + str(
            level_num) + ' ,number of levels' + str(len(levels)))
        sys.exit(1)
    if start > level_num:
        print('.levels file is not valid. start level is out of range. ')
        sys.exit(1)
    if observe and players_num != 1:
        print('invalid argument! ')
        print('--observe implies player num = 1')
        sys.exit(1)
    if not 1 <= players_num <= 4:
        print('players num: 1~4')
        sys.exit(1)
    game_manager = GameManager(None, levels, total_player_num=players_num, observer=observe)

    name_list = []
    for _ in range(players_num):
        name = input('enter player name: ')
        while name in name_list:
            print('name ' + name + ' already exist. ')
            name = input('enter new player name: ')
        else:
            name_list.append(name)
    game_manager.run_game_local_snarl(start, level_num, name_list)

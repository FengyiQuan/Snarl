#!/usr/bin/python3
import ast
import json
import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(os.path.split(rootPath)[0])

from Snarl.src.testRoom import read_input_to_json
from Snarl.src.testState import json_init_state, parse_state_to_json
from Snarl.src.GameManager import GameManager


def json_init_state_for_manager(name_list, level_js, initial_p_and_a_position_list):
    """
    parse json_expression to GameState for manager
    :param name_list: json to be parsed
    :param level_js: json to be parsed
    :param initial_p_and_a_position_list: json to be parsed
    """

    players = []
    adversaries = []
    for i in range(len(name_list)):
        name = name_list[i]
        players.append({
            "type": "player",
            "name": name,
            "position": initial_p_and_a_position_list.pop(0),
            'turn': i
        })

    for i in range(len(initial_p_and_a_position_list)):
        a_pos = initial_p_and_a_position_list[i]
        adversaries.append({
            "type": "zombie",
            "name": "a" + str(i),
            "position": a_pos,
            'turn': i
        })
    state_json = {
        "type": "state",
        "level": level_js,
        "players": players,
        "adversaries": adversaries,
        "exit-locked": True
    }

    return json_init_state(state_json)


##[ (name-list), (level), (natural), (point-list), (actor-move-list-list) ]
def main():
    js = read_input_to_json()
    if len(js) != 5:
        raise ValueError("invalid length for testManager")
    name_list = js[0]
    level_js = js[1]
    max_turn = js[2]
    initial_p_and_a_position_list = js[3]
    actor_move_list_list = js[4]

    state1 = json_init_state_for_manager(name_list=name_list, level_js=level_js,
                                         initial_p_and_a_position_list=initial_p_and_a_position_list)
    manager = GameManager(state=state1, levels=[])
    end_state, manage_trace = GameManager.run_game_for_testManager(manager, max_turn, actor_move_list_list)
    state_json = parse_state_to_json(end_state, level_js)
    output = [state_json, manage_trace]
    # print(output)
    print(json.dumps(output))
    return manager


if __name__ == '__main__':
    # print(ast.literal_eval(input()))
    js = read_input_to_json()
    if len(js) != 5:
        raise ValueError("invalid length for testManager")
    name_list = js[0]
    level_js = js[1]
    max_turn = js[2]
    initial_p_and_a_position_list = js[3]
    actor_move_list_list = js[4]

    state1 = json_init_state_for_manager(name_list=name_list, level_js=level_js,
                                         initial_p_and_a_position_list=initial_p_and_a_position_list)
    manager = GameManager(state=state1, levels=[])
    manager.run_game_local_snarl()

#!/usr/bin/python3

import json
import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(os.path.split(rootPath)[0])

import Snarl.src.util as util
from Snarl.src.Level import Level
from Snarl.src.testRoom import read_input_to_json
from Snarl.src.testLevel import json_init_level
from Snarl.src.ICharacter import ICharacter, Player, Adversary, Zombie, Ghost
from Snarl.src.GameState import GameState


# [(State), (name), (point)]
# A (State) is a JSON object with the following shape:
# { 
#   "type": "State",
#   "level": (level),
#   "players": (actor-position-list),
#   "adversaries": (actor-position-list),
#   "exit-locked": (boolean)
# }
# An (actor-position-list) is a list of (actor-position). An (actor-position) is the following object:
# {
#   "type": (actor-type),
#   "name": (string),
#   "position": (point)
# }
# An (actor-type) is one of:
# "player"
# "zombie"
# "ghost"

def json_init_state(json_expression):
    """
    parse json_expression to GameState
    :param json_expression: json to be parsed
    """
    if len(json_expression) != 5:
        raise ValueError("invalid length for init_state")

    level = json_init_level(json_expression["level"])
    Level.__str__(level)
    players = []
    adversaries = []
    exit_locked = json_expression["exit-locked"]
    for p in json_expression["players"]:
        players.append(Player(name=p["name"], position=tuple(util.switch_xy_coordinate(p["position"])), turn=p['turn']))
    for a in json_expression["adversaries"]:
        if a["type"] == "ghost":
            adversaries.append(
                Ghost(name=a["name"], position=tuple(util.switch_xy_coordinate(a["position"])), turn=a['turn']))
        elif a["type"] == "zombie":
            adversaries.append(
                Zombie(name=a["name"], position=tuple(util.switch_xy_coordinate(a["position"])), turn=a['turn']))
        else:
            raise ValueError("not implemented adversary type")

    return GameState(level=level, players=players, adversaries=adversaries, exit_locked=exit_locked)


def parse_state_to_json(state, json_level):
    players_list = []
    adversaries_list = []
    for p in GameState.get_players(state):
        if Player.get_is_alive(p):
            players_list.append({
                "type": "player",
                "name": Player.get_name(p),
                "position": util.switch_xy_coordinate(Player.get_position(p))})
    for a in GameState.get_adversaries(state):
        adversaries_list.append({
            "type": Adversary.get_type(a),
            "name": Adversary.get_name(a),
            "position": util.switch_xy_coordinate(Adversary.get_position(a))})
    output = {
        "type": "State",
        "level": json_level,
        "players": players_list,
        "adversaries": adversaries_list,
        "exit-locked": GameState.get_exit_locked(state)
    }
    return output


def main():
    js = read_input_to_json()
    if len(js) != 3:
        raise ValueError("invalid length for testState")
    json_state = js[0]
    player_name = js[1]
    to_point = tuple(util.switch_xy_coordinate(js[2]))
    state1 = json_init_state(json_state)
    to_point_output = util.switch_xy_coordinate(to_point)

    output = []
    m_achieved, m_status = GameState.move_player(state1, player_name, to_point)
    if m_status == "player does not exist in this State":
        output = ["Failure", "Player ", player_name, " is not a part of the game."]
    elif m_status == "target tile is not traversable":
        output = ["Failure", "The destination position ", to_point_output, " is invalid."]
    elif m_status == "target tile is occupied by another player":
        output = ["Failure", "The destination position ", to_point_output, " is invalid."]
    elif m_status == "player being captured by an adversary":
        state_output = parse_state_to_json(state1, json_state["level"])
        output = ["Success", "Player ", player_name, " was ejected.", state_output]
    elif m_status == "player finds the key and the exit is unlocked" or m_status == "player moves to the new position":
        state_output = parse_state_to_json(state1, json_state["level"])
        output = ["Success", state_output]
    elif m_status == "player successfully leaves the level through the exit":
        state_output = parse_state_to_json(state1, json_state["level"])
        output = ["Success", "Player ", player_name, " exited.", state_output]
    else:
        raise ValueError("invalid move status: ", m_status)

    print(json.dumps(output))


if __name__ == '__main__':
    main()

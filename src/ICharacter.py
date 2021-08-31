import ast
import copy
import json
import random

from Snarl.src.ITerrain import Tile
from Snarl.src.util import switch_xy_coordinate


class ICharacter:
    def __init__(self, name, turn, move_range, position, move_restrict, seen_range):
        self.name = name
        self.turn = turn
        self.move_range = move_range
        self.position = position
        self.move_restrict = move_restrict
        self.seen_range = seen_range

    # -------------------------------- Getters and Setters -------------------------------- #

    def get_turn(self):
        return self.turn

    def set_turn(self, turn):
        self.turn = turn

    def get_name(self):
        return copy.deepcopy(self.name)

    def get_move_restrict(self):
        return copy.deepcopy(self.move_restrict)

    def get_move_range(self):
        return self.move_range

    def get_position(self):
        return copy.deepcopy(self.position)

    def set_position(self, position):
        self.position = position

    def get_seen_range(self):
        return self.seen_range

    def get_type(self):
        return self.get_type

    def load_json_with_switch_pos(self):
        return {"type": self.get_type(), "name": self.get_name(), "position": switch_xy_coordinate(self.get_position())}

    def load_json(self):
        return {"type": self.get_type(), "name": self.get_name(), "position": self.get_position()}

    def get_vision_upper_left_bot_right(self):
        x, y = self.position
        seen_range = self.get_seen_range()
        return (x - seen_range, y - seen_range), (x + seen_range, y + seen_range)

    # -------------------------------- Main Methods -------------------------------- #
    def choose_move(self, possible_move):
        """
        choose a move and send to the manager to move the character
        :return: a coordinate to move next
        """
        print("possible move are: " + str(possible_move))

        while True:
            move_input = input('choose a move. \n')
            if move_input.strip() == 'None':
                return None
            else:
                try:
                    move = ast.literal_eval(move_input)
                except:
                    # print(e)
                    print("Invalid. Choose a new move ...")
                    continue
                if isinstance(move, tuple) and len(move) == 2 and all(isinstance(v, int) for v in move):
                    print(self.name + ' choose a move, move is ' + str(move))
                    return move


class Player(ICharacter):
    def __init__(self, name, position, turn=None, move_range=2, move_restrict=None, seen_range=4):
        """
        :param name: string representation of the player
        :param turn: num indicates the turn number, start from 0, id
        :param move_range: move_range
        :param position: position
        :param move_restrict: this is to indicate which tiles that players can not go through,
                              for example: a ghost type adversary could potentially ignore walls entirely

        :param seen_range: seen_range
        """
        move_restrict = [Tile.Wall] if move_restrict is None else move_restrict
        super().__init__(name, turn, move_range, position, move_restrict, seen_range)
        self.is_alive = True

    def __str__(self):
        return 'player name: ' + self.name + '\ncurrent position: ' + str(self.position) + '\nturn: ' + str(
            self.turn) + '\nis alive: ' + str(self.is_alive)

    # -------------------------------- Getters and Setters -------------------------------- #
    def get_is_alive(self):
        return copy.deepcopy(self.is_alive)

    def set_alive(self, alive):
        self.is_alive = alive

    def get_type(self):
        return 'player'

    # -------------------------------- Main Methods -------------------------------- #
    def receive_update(self, update_json):
        state_info = json.loads(update_json)

        self.position = state_info['location']
        self.is_alive = state_info['is_alive']
        surrounding_tiles = state_info['surrounding_tile']
        Player.print_visible(surrounding_tiles)

    @staticmethod
    def print_visible(surrounding):
        res = ''
        col_length = max([row for (row, col) in surrounding.keys()])
        row_length = max([col for (row, col) in surrounding.keys()])
        for row in range(row_length + 1):
            for col in range(col_length + 1):
                target = surrounding.get((col, row))
                if target is not None:
                    res += target + ' '
                else:
                    res += '  '
            res += '\n'

        return res


class Adversary(ICharacter):

    # -------------------------------- Getters and Setters -------------------------------- #
    def get_type(self):
        return self.get_type()

    def __str__(self):
        return self.get_type() + '\nname: ' + self.name + '\nturn: ' + str(self.turn) + '\ncurrent position: ' + str(
            self.position)

    def choose_move(self, possible_move):
        """
        choose a move and send to the manager to move the character
        :return: a coordinate to move next
        """
        if len(possible_move) == 0:
            return None
        else:
            return random.choice([move for move in possible_move if move != self.get_position()])


class RemoteZombie(Adversary):
    def __init__(self, name, position, turn=None, move_range=1, move_restrict=None, seen_range=2):
        move_restrict = [Tile.Wall, Tile.Door] if move_restrict is None else move_restrict
        super().__init__(name, turn, move_range, position, move_restrict, seen_range)

    # -------------------------------- Getters and Setters -------------------------------- #
    def get_type(self):
        return 'remote zombie'

    def choose_move(self, possible_move):
        """
        choose a move and send to the manager to move the character
        :return: a coordinate to move next
        """
        print("possible move are: " + str(possible_move))

        while True:
            move_input = input('choose a move. \n')
            if move_input.strip() == 'None':
                return None
            else:
                try:
                    move = ast.literal_eval(move_input)
                except:
                    # print(e)
                    print("Invalid. Choose a new move ...")
                    continue
                if isinstance(move, tuple) and len(move) == 2 and all(isinstance(v, int) for v in move):
                    print(self.name + ' choose a move, move is ' + str(move))
                    return move


class RemoteGhost(Adversary):
    def __init__(self, name, position, turn=None, move_range=1, move_restrict=None, seen_range=2):
        move_restrict = [] if move_restrict is None else move_restrict
        super().__init__(name, turn, move_range, position, move_restrict, seen_range)

    # -------------------------------- Getters and Setters -------------------------------- #
    def get_type(self):
        return 'remote ghost'

    def choose_move(self, possible_move):
        """
        choose a move and send to the manager to move the character
        :return: a coordinate to move next
        """
        print("possible move are: " + str(possible_move))

        while True:
            move_input = input('choose a move. \n')
            if move_input.strip() == 'None':
                return None
            else:
                try:
                    move = ast.literal_eval(move_input)
                except:
                    # print(e)
                    print("Invalid. Choose a new move ...")
                    continue
                if isinstance(move, tuple) and len(move) == 2 and all(isinstance(v, int) for v in move):
                    print(self.name + ' choose a move, move is ' + str(move))
                    return move


class Zombie(Adversary):
    def __init__(self, name, position, turn=None, move_range=1, move_restrict=None, seen_range=2):
        move_restrict = [Tile.Wall, Tile.Door] if move_restrict is None else move_restrict
        super().__init__(name, turn, move_range, position, move_restrict, seen_range)

    # -------------------------------- Getters and Setters -------------------------------- #
    def get_type(self):
        return 'zombie'


class Ghost(Adversary):
    def __init__(self, name, position, turn=None, move_range=1, move_restrict=None, seen_range=2):
        move_restrict = [] if move_restrict is None else move_restrict
        super().__init__(name, turn, move_range, position, move_restrict, seen_range)

    # -------------------------------- Getters and Setters -------------------------------- #
    def get_type(self):
        return 'ghost'

#!/usr/bin/python3

import copy
import random

# from Snarl.src.RuleChecker import RuleChecker
import sys

from Snarl.src.ITerrain import Tile
from Snarl.src.Level import Level
from Snarl.src.ICharacter import Player, Adversary, ICharacter

default_total_level_num = 5


class GameState:
    """
    GameState would contain information necessary to check validity of moves and progress the game.
    """

    def __init__(self, level=None, players=None, adversaries=None, exit_locked=True, current_level_num: int = 0,
                 total_level_num: int = default_total_level_num):
        """
        :param level: the current level
        :param players: a list of players
        :param adversaries: a list of adversaries
        :param exit_locked: if the exit is locked(key has not been picked up yet)
        """
        players = [] if players is None else players
        adversaries = [] if adversaries is None else adversaries
        self.level = level
        self.players = players
        self.adversaries = adversaries
        self.exit_locked = exit_locked
        self.current_level_num = current_level_num
        self.total_level_num = total_level_num

    def get_total_level_num(self):
        return self.total_level_num

    def set_total_level_num(self, num):
        self.total_level_num = num

    def get_current_level_num(self):
        return self.current_level_num

    def set_current_level_num(self, num):
        self.current_level_num = num

    def get_level(self):
        return copy.deepcopy(self.level)

    def set_level(self, level):
        self.level = level

    def get_exit_locked(self):
        return copy.deepcopy(self.exit_locked)

    def set_exit_locked(self, exit_locked):
        self.exit_locked = exit_locked

    # not correct
    def get_surrounding(self, player_name):
        player = self.get_player_by_name(player_name)
        player_position = player.get_position()
        player_seen_range = player.get_seen_range()
        seen_tiles = self.get_level().get_seen_tiles(player_position, player_seen_range)
        for player_position in [p.get_position() for p in self.players if p.get_name() != player_name]:
            if player_position in seen_tiles:
                seen_tiles.update({player_position: 'P'})

        for adversary_position in self.adversaries:
            if player_position in seen_tiles:
                seen_tiles.update({adversary_position: 'A'})

        key_pos = self.level.get_key_pos()
        exit_pos = self.level.get_exit_pos()
        if key_pos in seen_tiles.keys():
            seen_tiles.update({key_pos: 'K'})
        if exit_pos in seen_tiles.keys():
            seen_tiles.update({exit_pos: 'E'})
        return seen_tiles

    def get_total_characters_num(self):
        return len(self.get_players()) + len(self.get_adversaries())

    def re_assign_position(self):
        init_positions = self.__init_positions_for_character(self.get_total_characters_num())
        # print(init_positions)
        i = 0
        for player in self.players:
            position = init_positions[i]
            player.set_position(position)
            i += 1
        for adversary in self.adversaries:
            position = init_positions[i]
            adversary.set_position(position)
            i += 1

    def __init_positions_for_character(self, num) -> list:
        key_exit_location = self.get_level().get_key_exit_pos()
        # all_possible = [coord for coord in self.level.generate_map_dic().keys() if coord not in key_exit_location]
        all_possible = [coord for coord, tile in self.level.generate_room_dic().items() if
                        coord not in key_exit_location and tile != Tile.Wall and tile != Tile.Door]
        try:
            return random.sample(all_possible, num)
        except ValueError:
            print("Map is too narrow. ")
            sys.exit()

    # -------------------------------- Adversaries -------------------------------- #
    def get_adversaries(self):
        return copy.deepcopy(self.adversaries)

    def get_adversary_by_location(self, position):
        for adversary in self.adversaries:
            if Adversary.get_position(adversary) == position:
                return copy.deepcopy(adversary)

    def get_adversary_by_turn(self, turn):
        for a in self.get_adversaries():
            if a.get_turn() == turn:
                return a

    def get_adversary_by_name(self, name):
        for adversary in self.adversaries:
            if Adversary.get_name(adversary) == name:
                return adversary

    def add_adversary(self, adv):
        self.adversaries.append(adv)

    # -------------------------------- Players -------------------------------- #
    def get_players(self):
        return copy.deepcopy(self.players)

    def get_alive_players(self):
        return [p for p in self.get_players() if p.is_alive()]

    def get_player_by_turn(self, turn):
        for p in self.get_players():
            if p.get_turn() == turn:
                return p

    def get_player_by_name(self, name):
        if self.is_player_name_exist(name):
            for player in self.players:
                if player.get_name() == name:
                    return player
        else:
            raise ValueError('No name player exist. ')

    def get_player_by_location(self, position):
        for player in self.players:
            if player.get_position() == position:
                return copy.deepcopy(player)

    def add_player(self, player):
        if not self.is_player_name_exist(player.get_name()) and not self.is_adversary_name_exist(player.get_name()):
            self.players.append(player)
        else:
            raise ValueError("Name already exist. ")

    def get_player_vision(self, name) -> str:
        res = '  '
        player = self.get_player_by_name(name)
        # print(player.get_seen_range())
        vision = self.level.get_seen_tiles(player.get_position(), player.get_seen_range())
        # print(vision)
        (min_col_length, min_row_length), (max_col_length, max_row_length) = player.get_vision_upper_left_bot_right()
        # print(player.get_vision_upper_left_bot_right())

        for col in range(min_col_length, max_col_length + 1):
            res += str(col).rjust(2)
        res += '\n'
        for row in range(min_row_length, max_row_length + 1):
            res += str(row).rjust(2) + ' '
            for col in range(min_col_length, max_col_length + 1):
                point = (col, row)
                object_type = self.get_object_type_by_coord(point)
                if object_type == 'player':
                    res += 'P' + ' '
                elif object_type == 'adversary':
                    adv = self.get_adversary_by_location(point)
                    if adv.get_type() == 'ghost':
                        res += 'G' + ' '
                    elif adv.get_type() == 'zombie':
                        res += 'Z' + ' '
                    else:
                        res += 'A' + ' '
                elif object_type == 'key' and self.get_exit_locked():
                    res += 'K' + ' '
                elif object_type == 'exit':
                    res += 'E' + ' '
                else:
                    target = vision.get(point)
                    if target is not None:
                        res += target.__str__() + ' '
                    else:
                        res += '  '
            res += '\n'

        return res

    def get_objects_in_view(self, name) -> list:
        if self.is_player_name_exist(name):
            return self.__get_objects_in_player_view(name)
        elif self.is_adversary_name_exist(name):
            return self.__get_objects_in_adversary_view(name)

    def __get_objects_in_player_view(self, player_name) -> list:
        res = []
        character = self.get_player_by_name(player_name)
        (min_col_length, min_row_length), (max_col_length, max_row_length) = character.get_vision_upper_left_bot_right()

        for row in range(min_row_length, max_row_length + 1):
            for col in range(min_col_length, max_col_length + 1):
                point = (col, row)
                if point == self.get_level().get_key_pos() and self.get_exit_locked():
                    res.append(self.get_level().load_key_json())
                if point == self.get_level().get_exit_pos():
                    res.append(self.get_level().load_exit_json())
        return res

    def __get_objects_in_adversary_view(self, adv_name) -> list:
        res = []
        if self.get_exit_locked():
            res.append(self.get_level().load_key_json())
        res.append(self.get_level().load_exit_json())
        return res

    def get_actors_in_view(self, name) -> list:
        if self.is_player_name_exist(name):
            return self.__get_actors_in_player_view(name)
        elif self.is_adversary_name_exist(name):
            return self.__get_actors_in_adversary_view(name)

    def __get_actors_in_player_view(self, player_name) -> list:
        res = []
        player = self.get_player_by_name(player_name)
        (min_col_length, min_row_length), (max_col_length, max_row_length) = player.get_vision_upper_left_bot_right()

        for row in range(min_row_length, max_row_length + 1):
            for col in range(min_col_length, max_col_length + 1):
                point = (col, row)
                p = self.get_player_by_location(point)
                a = self.get_adversary_by_location(point)
                if p is not None and p.get_name() != player_name and p.get_is_alive():
                    res.append(ICharacter.load_json(p))
                if a is not None:
                    res.append(ICharacter.load_json(a))
        return res

    def __get_actors_in_adversary_view(self, adv_name) -> list:
        res = [p.load_json() for p in self.get_players() if p.get_is_alive()] + [a.load_json() for a in
                                                                                 self.get_adversaries()]
        return res

    # -------------------------------- Checker if exist -------------------------------- #
    def is_player_name_exist(self, name) -> bool:
        """
        check if the given name player exist in the State
        :param name
        """
        return name in [player.get_name() for player in self.players]

    def is_adversary_name_exist(self, name) -> bool:
        """
        check if the given name player exist in the State
        :param name
        """
        return name in [adv.get_name() for adv in self.adversaries]

    def is_player_on_point(self, point) -> bool:
        """
        check if there is a player on that point
        :param point
        """

        return point in [player.get_position() for player in self.players]

    def is_adversary_on_point(self, point) -> bool:
        """
        check if there is a adversary on that point
        :param point
        """
        return point in [adversary.get_position() for adversary in self.adversaries]

    def get_object_type_by_coord(self, coord) -> str:
        if self.is_player_on_point(coord):
            player = self.get_player_by_location(coord)
            if player.get_is_alive():
                return 'player'
        elif self.is_adversary_on_point(coord):
            return 'adversary'
        elif Level.get_exit_pos(self.level) == coord:
            return 'exit'
        elif Level.get_key_pos(self.level) == coord:
            return 'key'
        else:
            return 'none'

    def get_surrounding_objects_and_actors_for_player(self, coord):
        objects = []
        actors = []
        x, y = coord
        for i in range(y - 2, y + 3):
            for j in range(x - 2, x + 3):
                if y == i and x == j:
                    pass
                else:
                    current_point = (j, i)
                    object_type = self.get_object_type_by_coord(current_point)
                    if object_type == 'player':
                        player = self.get_player_by_location(current_point)
                        actors.append(ICharacter.load_json_with_switch_pos(player))
                    elif object_type == 'adversary':
                        adversary = self.get_adversary_by_location(current_point)
                        actors.append(ICharacter.load_json_with_switch_pos(adversary))
                    elif object_type == 'exit':
                        objects.append(Level.load_exit_json(self.level))
                    elif object_type == 'key':
                        objects.append(Level.load_key_json(self.level))
        return objects, actors

    def move_player(self, name, point):
        """
        move the player by the given name and point, followings are the circumstances:
        
        1. if the player does not exist in this State, the move is failed
        2. if the target tail is not traversable, the move is failed
        3. if there is another player in the target tail, the move is failed
        4. if the player landed on an adversary, the player should be ejected
        5. if the player touch the key while exit locked, then the exit is unlocked, and move successes
        6. if the player lands on an exit and the exit is unlocked, the player leaves!
        7. if the player lands on a traversable tile with no object, then the move is achieved
        :param name
        :param point
        """
        if not self.is_player_name_exist(name):
            move_achieved = "Failure"
            move_status = "player does not exist in this State"
        else:
            traversable, locations_type, neighbor_origins, tile_type = Level.is_tile_traversable(self.level, point)
            obj = Level.object_type(self.level, point)
            if not traversable:
                move_achieved = "Failure"
                move_status = "target tile is not traversable"
            elif self.is_player_on_point(point) and self.get_player_by_location(
                    point).get_name() != name and self.get_player_by_location(point).get_is_alive():
                move_achieved = "Failure"
                move_status = "target tile is occupied by another player"
            elif self.is_adversary_on_point(point):
                self.__kill_player_by_name(name)
                move_achieved = "Success"
                move_status = "player being captured by an adversary"
            elif obj == "key" and self.get_exit_locked():
                self.set_exit_locked(False)
                self.__move_player_by_name(name, point)
                move_achieved = "Success"
                move_status = "player finds the key and the exit is unlocked"
            elif obj == "exit" and not self.get_exit_locked():
                self.__move_player_by_name(name, point)
                move_achieved = "Success"
                move_status = "player successfully leaves the level through the exit"
            else:
                self.__move_player_by_name(name, point)
                move_achieved = "Success"
                move_status = "player moves to the new position"
        return move_achieved, move_status

    def move_adversary(self, name, point):

        if not self.is_adversary_name_exist(name):
            raise ValueError('Adversary ' + name + ' does not exist. ')
        else:
            traversable, locations_type, neighbor_origins, tile_type = Level.is_tile_traversable(self.level, point)
            # obj = Level.object_type(self.level, point)
            if not traversable:
                move_achieved = "Failure"
                move_status = "target tile is not traversable"
            elif self.is_player_on_point(point):
                player = self.get_player_by_location(point)
                move_achieved = "Success"
                if player.get_is_alive():
                    self.__kill_player_by_name(player.get_name())
                    self.__move_enemy_by_name(name, point)
                    # print(self.get_player_by_name(player.get_name()).__str__())
                    move_status = "player being captured by an adversary"
                else:
                    self.__move_enemy_by_name(name, point)
                    move_status = "adversary moves to the new position"
            else:
                self.__move_enemy_by_name(name, point)
                move_achieved = "Success"
                move_status = "adversary moves to the new position"

            return move_achieved, move_status

    def __move_player_by_name(self, name, position):
        for p in self.players:
            if Player.get_name(p) == name:
                Player.set_position(p, position)

    def __move_enemy_by_name(self, name, position):
        for a in self.adversaries:
            if Adversary.get_name(a) == name:
                Adversary.set_position(a, position)

    # def character_interact(self, character):
    #     if isinstance(character, Player):
    #         self.__player_interact(character)
    #     elif isinstance(character, Adversary):
    #         self.__enemy_interact(character)
    #
    # def __player_interact(self, player):
    #     player_location = player.get_position()
    #     player_name = player.get_name()
    #     interact_object_type = self.get_object_type_by_coord(player_location)
    #
    #     if interact_object_type == 'adversary':
    #         self.__kill_player_by_name(player_name)
    #     elif interact_object_type == 'key':
    #         self.set_exit_locked(True)
    #     else:
    #         print('do nothing')

    def __kill_player_by_name(self, name):
        for p in self.players:
            if p.get_name() == name:
                p.set_alive(False)

    def revive_all_players(self):
        for p in self.players:
            p.set_alive(True)

    # def __enemy_interact(self, adversary):
    #     adversary_location = adversary.get_position()
    #     interact_object_type = self.get_object_type_by_coord(adversary_location)
    #
    #     if interact_object_type == 'player':
    #         player_name = self.get_player_by_location(adversary_location).get_name()
    #         self.__kill_player_by_name(player_name)
    #     else:
    #         print('do nothing')

    def if_wall_teleport_for_adversary(self, point):
        """
        If the point is not a wall, this function would return the given point
        If the point is a wall, then we would select a random point in a random room in the map
        """
        traversable, locations_type, neighbor_origins, tile_type = Level.is_tile_traversable(self.level, point)
        result = point
        if tile_type == "wall":
            possible_move_list = Level.get_all_room_empty_points(self.level)
            result = random.choice(possible_move_list)
            while self.is_adversary_on_point(result):
                result = random.choice(possible_move_list)
        return result

    def __str__(self):
        """
        :return: a ASCII art representation of the whole level
        """
        res = '  '
        map_dictionary = Level.generate_map_dic(self.get_level())
        col_length = max([row for (row, col) in map_dictionary.keys()])
        row_length = max([col for (row, col) in map_dictionary.keys()])

        for col in range(col_length + 1):
            res += str(col).rjust(2)
        res += '\n'
        for row in range(row_length + 1):
            res += str(row).rjust(2) + ' '
            for col in range(col_length + 1):
                point = (col, row)
                object_type = self.get_object_type_by_coord(point)
                if object_type == 'player':
                    res += 'P' + ' '
                elif object_type == 'adversary':
                    adv = self.get_adversary_by_location(point)
                    if adv.get_type() == 'ghost':
                        res += 'G' + ' '
                    elif adv.get_type() == 'zombie':
                        res += 'Z' + ' '
                    else:
                        res += 'A' + ' '
                elif object_type == 'key' and self.get_exit_locked():
                    res += 'K' + ' '
                elif object_type == 'exit':
                    res += 'E' + ' '
                else:
                    target = map_dictionary.get(point)
                    if target is not None:
                        res += target.__str__() + ' '
                    else:
                        res += '  '
            res += '\n'

        return res

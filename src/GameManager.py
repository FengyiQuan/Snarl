#!/usr/bin/python3
import math
import os
import sys

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(os.path.split(rootPath)[0])
from Snarl.src.ICharacter import *
from Snarl.src.GameState import GameState
from Snarl.src.Level import Level
from Snarl.src.RuleChecker import RuleChecker
from Snarl.src.util import switch_xy_coordinate, print_map_score

default_total_player_num = 2
default_total_adversary_num = 4


class GameManager:
    def __init__(self, state: GameState = None, levels: list = None,
                 total_player_num: int = default_total_player_num,
                 total_adversary_num: int = default_total_adversary_num, observer=False):
        self.connections = None
        self.state = state
        self.total_player_num = total_player_num
        self.total_adversary_num = total_adversary_num
        self.all_levels = levels
        self.score_info = []  # name, exited_num, keys_found, ejected_num
        self.observer = observer

    def get_score_info(self):
        return copy.deepcopy(self.score_info)

    def print_score(self):
        res = 'Score:\n'
        self.score_info.sort(key=lambda x: x['ejected_num'], reverse=False)
        self.score_info.sort(key=lambda x: x['keys_found'], reverse=True)
        self.score_info.sort(key=lambda x: x['exited_num'], reverse=True)
        for score in self.score_info:
            res += print_map_score(score)
            res += '\n'
        print(res)
        return res

    def set_levels(self, lv):
        self.all_levels = lv

    def get_state(self):
        return copy.deepcopy(self.state)

    def get_level_by_level_num(self, index):
        return self.all_levels[index]

    def get_total_adversary_num(self):
        return self.total_adversary_num

    def set_total_adversary_num(self, num):
        self.total_adversary_num = num

    def set_total_player_num(self, num):
        self.total_player_num = num

    def get_total_characters_num(self):
        return self.total_player_num + self.total_adversary_num

    def inc_score_ejected_num(self, name):
        for one_score in self.score_info:
            if one_score['name'] == name:
                one_score['ejected_num'] += 1

    def inc_score_keys_found(self, name):
        for one_score in self.score_info:
            if one_score['name'] == name:
                one_score['keys_found'] += 1

    def inc_score_exit_reach(self, name):
        for one_score in self.score_info:
            if one_score['name'] == name:
                one_score['exited_num'] += 1

    # -------------------------------- Initialize -------------------------------- #
    def init_new_level(self, start_level: int, total_level: int):
        """

        :param start_level: start from index 1
        :param total_level:
        :return:
        """
        old_state = self.get_state()
        new_level = self.get_level_by_level_num(start_level - 1)
        if old_state is None:
            self.state = GameState(new_level)
        else:
            self.state.set_level(new_level)
        self.state.set_exit_locked(True)
        self.state.set_total_level_num(total_level)
        self.state.set_current_level_num(start_level)
        self.state.revive_all_players()

        self.state.re_assign_position()

    def init_adversaries(self, remote_adversary_list: list = None):
        self.state.adversaries.clear()

        current_level_num = self.state.get_current_level_num()
        num_zombies = math.floor(current_level_num / 2) + 1
        num_ghosts = math.floor((current_level_num - 1) / 2)
        self.set_total_adversary_num(num_zombies + num_ghosts)

        turn = 0
        for n in range(num_zombies):
            if remote_adversary_list is not None and turn < len(remote_adversary_list):
                name = remote_adversary_list[turn]
                zombie = RemoteZombie(name, None, turn)
            else:
                zombie = Zombie('zombie' + str(n), None, turn)
            self.state.add_adversary(zombie)
            turn += 1

        for n in range(num_ghosts):
            if remote_adversary_list is not None and turn + num_zombies < len(remote_adversary_list):
                name = remote_adversary_list[turn]
                ghost = RemoteGhost(name, None, turn)
            else:
                ghost = Ghost('ghost' + str(n), None, turn)
            self.state.add_adversary(ghost)
            turn += 1

    def init_score_board(self):
        """
        this should init at the end after all players initialize
        """
        player_name_list = [p.get_name() for p in self.state.get_players()]
        for p_name in player_name_list:
            self.score_info.append({'name': p_name, 'keys_found': 0, 'exited_num': 0, 'ejected_num': 0})

    def init_players(self, name_list):
        for i in range(len(name_list)):
            self.register_local_player(name_list[i], i)

    def register_local_player(self, name, turn):
        player = Player(name, None, turn=turn)
        self.state.add_player(player)

    # def register_remote_player(self, name, turn):
    #
    #     player = Client(name, None, turn=turn)
    #     self.state.add_player(player)

    # -------------------------------- Run Game -------------------------------- #

    def run_game_local_snarl(self, start_level, total_level, player_names):
        self.init_new_level(start_level, total_level)
        self.init_players(player_names)
        self.init_adversaries()
        self.state.re_assign_position()
        self.init_score_board()
        while not RuleChecker.is_game_end(self.state):
            print(
                '************************** current level : ' + str(
                    self.state.get_current_level_num()) + ' **************************')
            while not RuleChecker.is_level_end(self.state):
                self.players_turn()
                # print(not RuleChecker.is_level_end(self.state))
                self.adversaries_turn()
            if RuleChecker.is_game_end(self.state):
                break
            if RuleChecker.is_level_success(self.state) and not RuleChecker.is_the_last_level(self.state):
                print('************************** level pass **************************')
                # print(self.state.get_total_level_num())
                # print(RuleChecker.is_level_success(self.state))
                # print(not RuleChecker.is_the_last_level(self.state))
                print(
                    '************************** current level : ' + str(
                        self.state.get_current_level_num()) + ' **************************')
                current_level_num = self.state.get_current_level_num()
                self.init_new_level(current_level_num + 1, self.state.get_total_level_num())
                self.state.set_current_level_num(current_level_num + 1)
                self.init_adversaries()
                self.state.re_assign_position()

        if RuleChecker.is_game_lose(self.state):
            print('failed in level ' + str(self.state.get_current_level_num()))
        elif RuleChecker.is_game_win(self.state):
            print('Win! ')
        self.print_score()

    def players_turn(self):
        for i in range(self.total_player_num):
            player = self.state.get_player_by_turn(i)

            if player.get_is_alive():
                print('------------------------------ New Turn ------------------------------')
                print(player.__str__())
                if self.observer:
                    print(self.state.__str__())
                else:
                    print(self.state.get_player_vision(player.get_name()))
                self.attempt_player_move(player.get_name())

    def adversaries_turn(self):
        for i in range(self.total_adversary_num):
            self.move_single_adversary(i)

    def move_single_adversary(self, turn):
        adversary = self.state.get_adversary_by_turn(turn)
        possible_move = RuleChecker.get_possible_movement(self.state, adversary)
        move = adversary.choose_move(possible_move)
        # only happened when no move valid
        if move is None:
            move = adversary.get_position()

        if Adversary.get_type(adversary) == "ghost" or Adversary.get_type(adversary) == "remote ghost":
            move = self.state.if_wall_teleport_for_adversary(move)

        move_achieved, move_status = self.state.move_adversary(adversary.get_name(), move)
        if move_status == "player being captured by an adversary":
            player_name = self.get_state().get_player_by_location(move).get_name()
            self.inc_score_ejected_num(player_name)
            msg = 'Adversary ' + adversary.get_name() + ' capture a player. '
        elif move_status == "adversary moves to the new position":
            msg = 'Adversary ' + adversary.get_name() + ' move to ' + str(move) + '. '
        else:
            raise ValueError("would not go here, invalid move status: ", move_status)
        if self.observer:
            print('Adversary ' + adversary.get_type() + ' move to ' + str(move))
        print(msg)
        return msg, move_status, msg

    def attempt_player_move(self, player_name):
        player = self.state.get_player_by_name(player_name)
        game_state = self.state
        possible_move = RuleChecker.get_possible_movement(self.state, player)
        to_point = player.choose_move(possible_move)
        msg = ''
        if to_point is None:
            to_point = player.get_position()

        if not RuleChecker.validate_movement(game_state, player_name, to_point):
            msg = 'Invalid move. try again'
            print('Invalid move. try again')
            self.attempt_player_move(player_name)
        else:
            move_achieved, m_status = GameState.move_player(self.state, player_name, to_point)
            # print(m_status)
            if m_status == "player being captured by an adversary":
                msg = 'Player ' + player_name + ' was expelled. '
                self.inc_score_ejected_num(player_name)
            # valid move, key found
            elif m_status == "player finds the key and the exit is unlocked":
                msg = 'Player ' + player_name + ' found the key. '
                self.inc_score_keys_found(player_name)
            # valid move, exit found
            elif m_status == "player successfully leaves the level through the exit":
                msg = 'Player ' + player_name + ' exited. '
                self.inc_score_exit_reach(player_name)
            # valid move, move to a new tile with no objects on
            elif m_status == "player moves to the new position":
                msg = 'Player ' + player_name + ' move to ' + str(to_point) + '. '
            else:
                raise ValueError("would not go here, invalid move status: ", m_status)
            print(msg)
        return msg

    # -------------------------------- Only for Testing -------------------------------- #
    """
    method for running game, to pass our requirements for testManager
    """

    def run_game_for_testManager(self, max_turn, actor_move_list_list):
        manage_trace = []
        game_state = self.get_state()
        game_level = GameState.get_level(game_state)
        state_players = self.state.players
        for p in state_players:
            update_trace_entry = self.load_json_player_update_trace_entry(p, game_level)
            manage_trace.append(update_trace_entry)
        for _ in range(max_turn):
            # If an input stream is exhausted at the end of a turn, that turn is the last one in the trace
            for al in actor_move_list_list:
                if not al:
                    return self.get_state(), manage_trace
            for n in range(len(state_players)):
                pl = state_players[n]
                if pl.get_is_alive() == True:
                    al = actor_move_list_list[n]
                    # for p, al in zip(state_players, actor_move_list_list):
                    manage_trace_list, rest_action_list = self.attempt_player_moves(pl, al)
                    actor_move_list_list[n] = rest_action_list
                    manage_trace += manage_trace_list
                    # the level is over
                    if RuleChecker.is_game_lose(self.get_state()):
                        return self.get_state(), manage_trace
        return self.get_state(), manage_trace

    """
    method for attempting one move for one specific player
    
    1. If a player's move resulted in them exiting or being expelled, 
    they don't get an update after that move
    2. If the moves are exhausted while the turn is already in progress, the behavior is undefined.
    """

    def attempt_player_moves(self, player, action_list):
        manage_trace_list = []
        rest_action_list = copy.deepcopy(action_list)
        action_count = 0
        game_state = self.get_state()
        game_level = GameState.get_level(game_state)
        position = player.position
        name = Player.get_name(player)
        reachabel_terrains = Level.get_reachable_terrains(game_level, position)
        for action in action_list:
            action_count += 1
            # when it is a skipped move, set the to point to player location
            to_point = position
            if action["to"] is not None:
                to_point = tuple(switch_xy_coordinate(action["to"]))
            ###invalid move because the to point is too far
            if not RuleChecker.validate_movement(game_state, player.get_name(), to_point):
                manage_trace_list.append(self.load_json_player_move(player, action, "Invalid"))
            else:
                move_achieved, m_status = GameState.move_player(self.state, name, to_point)

                if m_status == "target tile is not traversable":
                    manage_trace_list.append(self.load_json_player_move(player, action, "Invalid"))
                    print("not tra")
                # invalid move because it would hit another player
                elif m_status == "target tile is occupied by another player":
                    manage_trace_list.append(self.load_json_player_move(player, action, "Invalid"))
                # valid move, ejected
                elif m_status == "player being captured by an adversary":
                    manage_trace_list.append(self.load_json_player_move(player, action, "Eject"))
                    manage_trace_list += self.load_json_all_player_update_trace_entry()
                    break
                # valid move, key found
                elif m_status == "player finds the key and the exit is unlocked":
                    manage_trace_list.append(self.load_json_player_move(player, action, "Key"))
                    manage_trace_list += self.load_json_all_player_update_trace_entry()
                    break
                # valid move, exit found
                elif m_status == "player successfully leaves the level through the exit":
                    manage_trace_list.append(self.load_json_player_move(player, action, "Exit"))
                    manage_trace_list += self.load_json_all_player_update_trace_entry()
                    break
                # valid move, move to a new tile with no objects on
                elif m_status == "player moves to the new position":
                    manage_trace_list.append(self.load_json_player_move(player, action, "OK"))
                    manage_trace_list += self.load_json_all_player_update_trace_entry()
                    break
                else:
                    raise ValueError("invalid move status: ", m_status)
        return manage_trace_list, rest_action_list[action_count:]

    @staticmethod
    def load_json_player_move(player, action, status):
        return [Player.get_name(player), action, status]

    """
    method for load json for player update trace entry
    """

    def load_json_all_player_update_trace_entry(self):
        all_update_trace_entry = []
        game_state = self.state
        level = GameState.get_level(game_state)
        players = GameState.get_players(game_state)
        for p in players:
            if Player.get_is_alive(p):
                all_update_trace_entry.append(self.load_json_player_update_trace_entry(p, level))
        return all_update_trace_entry

    """
    method for load json for player update trace entry
    """

    def load_json_player_update_trace_entry(self, player, level):
        p_position = Player.get_position(player)
        player_update_json = self.load_json_player_update(level, p_position)
        return [Player.get_name(player), player_update_json]

    """
    method for load json for player update
    """

    def load_json_player_update(self, level, player_position):
        objects, actors = GameState.get_surrounding_objects_and_actors_for_player(self.state, player_position)
        return {
            "type": "player-update",
            "layout": Level.get_seen_tiles_for_player(level, player_position),
            "position": switch_xy_coordinate(player_position),
            "objects": objects,
            "actors": actors
        }

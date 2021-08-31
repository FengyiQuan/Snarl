import ast
import copy
import socket
import json
import sys
import time

from Snarl.src.GameManager import GameManager
from Snarl.src.GameState import GameState
from Snarl.src.RuleChecker import RuleChecker
from Snarl.src.util import send_msg, receive_msg


class Server:
    def __init__(self, ip: str, port: int, min_clients: int = 1, max_clients: int = 4, max_remote_adversary: int = 2,
                 reg_timeout: int = 60, observer: bool = False, manager: GameManager = None):

        self.min_clients = min_clients
        self.max_clients = max_clients
        self.max_remote_adversary = max_remote_adversary
        self.reg_timeout = reg_timeout
        self.observer = observer

        self.sock = None
        self.init_sock(ip, port)
        self.player_sockets = {}
        self.adversary_sockets = {}
        self.remote_zombie_list = []
        self.remote_ghost_list = []  # no use

        self.manager = manager

        self.who_find_key = None
        self.who_exits = []
        self.who_ejects = []
        self.setting = {'remote players': True, 'remote adversary': False}  # TODO: not supported remote adversary

    def enable_remote_adversary(self):
        self.setting.update({'remote adversary': True})

    def enable_remote_player(self):
        self.setting.update({'remote players': True})

    def clear_record(self):
        self.who_find_key = None
        self.who_exits = []
        self.who_ejects = []

    def get_player_name_list(self) -> list:
        return [p.get_name() for p in self.manager.get_state().get_players()]

    def get_adversary_name_list(self) -> list:
        return [a.get_name() for a in self.manager.get_state().get_adversaries()]

    def adversaries_turn(self):
        for i in range(self.manager.get_total_adversary_num()):
            adversary = self.manager.state.get_adversary_by_turn(i)
            print(adversary.load_json())

            if self.observer:
                print('------------------------------ New Turn ------------------------------')
                print(self.manager.state.__str__())
            # else:
            #     print(self.state.get_player_vision(player.get_name()))
            try:
                if adversary.get_type() == 'remote ghost' or adversary.get_type() == 'remote zombie':
                    self.attempt_remote_adversary_move(adversary.get_name())
                else:  ## local adversary situation
                    _, move_status, msg = self.manager.move_single_adversary(i)
                    if move_status == "player being captured by an adversary":
                        self.send_player_update_message(msg)
                    elif move_status == "adversary moves to the new position":
                        self.send_adversary_update_message(msg)

            except Exception:
                print("Someone disconnected. Game end.")
                self.send_adversary_update_message("Player " + adversary.get_name() + " disconnected. ")
                sys.exit()

        self.send_player_update_message()

    def players_turn(self):
        if self.setting.get('remote player'):
            self.remote_players_turn()
        else:
            self.manager.players_turn()

    def remote_players_turn(self):
        for i in range(self.manager.total_player_num):
            player = self.manager.state.get_player_by_turn(i)

            if player.get_is_alive():
                if self.observer:
                    print('------------------------------ New Turn ------------------------------')
                    print(self.manager.state.__str__())
                # else:
                #     print(self.state.get_player_vision(player.get_name()))
                try:
                    self.attempt_player_move(player.get_name())
                except:
                    print("Someone disconnected. Game end.")
                    self.send_player_update_message("Player " + player.get_name() + " disconnected. ")
                    sys.exit()

    def get_remote_adversary_list(self):
        res = copy.deepcopy(self.remote_zombie_list)
        res.append(self.remote_ghost_list)
        return copy.deepcopy(self.remote_zombie_list)

    def run(self, total_level):

        self.manager.init_new_level(1, total_level)
        self.register_players()

        self.manager.set_total_player_num(len(self.player_sockets))
        self.register_remote_adversary()

        self.manager.init_adversaries(remote_adversary_list=self.get_remote_adversary_list())
        self.manager.state.re_assign_position()
        self.manager.init_score_board()
        player_name_list = self.get_player_name_list()
        adversary_name_list = self.get_adversary_name_list()
        while not RuleChecker.is_game_end(self.manager.state):
            self.clear_record()
            self.send_start_level(level_num=self.manager.get_state().get_current_level_num(),
                                  player_name_list=player_name_list,
                                  adversary_name_list=adversary_name_list)
            self.send_player_update_message("start a level! Good luck! ")
            self.send_adversary_update_message("start a level! Good luck! ")
            if self.observer:
                print(
                    '************************** current level : ' + str(
                        self.manager.state.get_current_level_num()) + ' **************************')
            while not RuleChecker.is_level_end(self.manager.state):
                if self.observer:
                    print(self.manager.state.__str__())
                self.remote_players_turn()
                if RuleChecker.is_level_end(self.manager.state):
                    break
                self.adversaries_turn()
                # if RuleChecker.is_level_end(self.__manager.state):
                #     break
            self.send_end_level()
            if RuleChecker.is_game_end(self.manager.state):
                break
                # players pass the level
            if RuleChecker.is_level_success(self.manager.state) and not RuleChecker.is_the_last_level(
                    self.manager.state):
                if self.observer:
                    print('************************** level pass **************************')

                current_level_num = self.manager.state.get_current_level_num()
                self.manager.init_new_level(current_level_num + 1, self.manager.state.get_total_level_num())
                # self.__manager.state.set_current_level_num(current_level_num + 1)
                self.manager.init_adversaries(remote_adversary_list=self.get_remote_adversary_list())
                self.manager.state.re_assign_position()

        if RuleChecker.is_game_lose(self.manager.state):
            self.send_end_game(self.manager.get_score_info(), False)
            print('Failed in level ' + str(self.manager.state.get_current_level_num()))
        elif RuleChecker.is_game_win(self.manager.state):
            self.send_end_game(self.manager.get_score_info(), True)
            print('Win! ')

    def get_player_connection(self, name) -> socket.SocketType:
        for player_name, conn in self.player_sockets.items():
            if player_name == name:
                return conn

    def get_adv_connection(self, name) -> socket.SocketType:
        for adversary_name, conn in self.adversary_sockets.items():
            if adversary_name == name:
                return conn

    def attempt_remote_adversary_move(self, adversary_name):
        adversary = self.manager.state.get_adversary_by_name(adversary_name)
        game_state = self.manager.state
        possible_move = RuleChecker.get_possible_movement(self.manager.state, adversary)
        conn = self.get_adv_connection(adversary_name)

        to_point = self.wait_for_a_move(conn, possible_move)

        if to_point is None:
            to_point = adversary.get_position()

        while not RuleChecker.validate_movement(game_state, adversary_name, to_point):
            print('Invalid move! ')
            send_msg(conn, 'Invalid')
            time.sleep(1)
            to_point = self.wait_for_a_move(conn, possible_move)
        move_achieved, m_status = GameState.move_adversary(self.manager.state, adversary_name, to_point)
        # print(m_status)

        # valid move, key found
        if m_status == "player being captured by an adversary":
            self.send_move_result(conn, "Capture")
            player_name = self.manager.get_state().get_player_by_location(to_point).get_name()
            self.manager.inc_score_ejected_num(player_name)
            msg = 'Adversary ' + adversary_name + ' capture a player. '
            self.send_player_update_message('Player ' + player_name + ' was expelled. ')

        # valid move, move to a new tile with no objects on
        elif m_status == "adversary moves to the new position":
            self.send_move_result(conn, "OK")
            msg = 'Adversary ' + adversary_name + ' move to ' + str(to_point) + '. '
        else:
            print("would not go here, invalid move status: ", m_status)
            raise ValueError("would not go here, invalid move status: ", m_status)

        # layout = self.__manager.get_state().get_level().get_seen_tiles_for_player(player.get_position())
        # objects = self.__manager.get_state().get_objects_in_view(player_name)
        # actors = self.__manager.get_state().get_actors_in_view(player_name)
        # position = self.__manager.state.get_player_by_name(player_name).get_position()
        if self.observer:
            print(msg)
        time.sleep(1)
        self.send_adversary_update_message(msg)

    def attempt_player_move(self, player_name):
        player = self.manager.state.get_player_by_name(player_name)
        # print(player.__str__())
        game_state = self.manager.state
        possible_move = RuleChecker.get_possible_movement(self.manager.state, player)
        conn = self.get_player_connection(player_name)

        to_point = self.wait_for_a_move(conn, possible_move)

        while not RuleChecker.validate_movement(game_state, player_name, to_point):
            print('Invalid move! ')
            send_msg(conn, 'Invalid')
            time.sleep(1)
            to_point = self.wait_for_a_move(conn, possible_move)

        if to_point is None:
            to_point = player.get_position()

        move_achieved, m_status = GameState.move_player(self.manager.state, player_name, to_point)
        # print(m_status)
        if m_status == "player being captured by an adversary":
            self.send_move_result(conn, "Eject")
            msg = 'Player ' + player_name + ' was expelled. '
            self.manager.inc_score_ejected_num(player_name)
            self.who_ejects.append(player_name)
        # valid move, key found
        elif m_status == "player finds the key and the exit is unlocked":
            self.send_move_result(conn, "Key")
            msg = 'Player ' + player_name + ' found the key. '
            self.manager.inc_score_keys_found(player_name)
            self.who_find_key = player_name

            player_on_exit = self.manager.get_state().get_player_by_location(
                self.manager.get_state().get_level().get_exit_pos())
            if player_on_exit is not None:
                name = player_on_exit.get_name()
                self.who_exits.append(name)
                self.manager.inc_score_exit_reach(name)


        # valid move, exit found
        elif m_status == "player successfully leaves the level through the exit":
            self.send_move_result(conn, "Exit")
            msg = 'Player ' + player_name + ' exited. '
            self.manager.inc_score_exit_reach(player_name)
            self.who_exits.append(player_name)
        # valid move, move to a new tile with no objects on
        elif m_status == "player moves to the new position":
            self.send_move_result(conn, "OK")
            msg = 'Player ' + player_name + ' move to ' + str(to_point) + '. '
        else:
            raise ValueError("would not go here, invalid move status: ", m_status)

        # layout = self.__manager.get_state().get_level().get_seen_tiles_for_player(player.get_position())
        # objects = self.__manager.get_state().get_objects_in_view(player_name)
        # actors = self.__manager.get_state().get_actors_in_view(player_name)
        # position = self.__manager.state.get_player_by_name(player_name).get_position()
        if self.observer:
            print(msg)
        time.sleep(1)
        self.send_player_update_message(msg)

    def init_sock(self, ip: str, port: int):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((ip, port))
        self.sock.listen(self.max_clients + self.max_remote_adversary)
        self.sock.settimeout(self.reg_timeout)

    def register_players(self):
        try:
            self.wait_for_players(self.min_clients, 0)
        except socket.timeout:
            raise ValueError("Game should have at least " + str(self.min_clients) + " players to start. Having " +
                             str(len(self.player_sockets)))
        try:
            self.wait_for_players(self.max_clients - self.min_clients, 1)
        except socket.timeout:
            print('No additional players. ')

    def register_remote_adversary(self):
        try:
            self.wait_for_adversaries()
        except socket.timeout:
            raise ValueError("Game should have at least " + str(self.min_clients) + " players to start. Having " +
                             str(len(self.player_sockets)))

    def wait_for_adversaries(self):
        for i in range(self.max_remote_adversary):
            conn, addr = self.sock.accept()
            print('client ip: ' + addr[0] + 'client port: ' + str(addr[1]))
            self.send_welcome(conn)
            time.sleep(1)

            while True:
                try:
                    name = self.ask_for_name(conn)
                    self.remote_zombie_list.append(name)
                    self.adversary_sockets.update({name: conn})
                    break
                except ValueError:
                    continue

    def ask_for_name(self, conn) -> str:
        while True:
            send_msg(conn, 'name')

            name = receive_msg(conn)
            if name and name.isalpha() and ' ' not in name and name not in self.player_sockets.keys() and \
                    name not in self.adversary_sockets.keys():
                return name

    def wait_for_players(self, count, turn):
        for i in range(turn, count + turn):
            conn, addr = self.sock.accept()
            print('client ip: ' + addr[0] + 'client port: ' + str(addr[1]))
            self.send_welcome(conn)
            time.sleep(1)

            while True:
                try:
                    name = self.ask_for_name(conn)
                    self.manager.register_local_player(name, i)
                    self.player_sockets.update({name: conn})
                    break
                except ValueError:
                    continue

    def wait_for_a_move(self, conn, possible_move) -> [tuple, None]:
        send_msg(conn, 'move')
        # send_msg(conn, "possible move are: " + str(possible_move) + '\nPlease enter a move. (absolute position)')
        msg = json.loads(receive_msg(conn))

        try:
            # print(msg)

            move = self.deal_response_type(msg)
            print(move)
            if move is None:
                return move

        except AssertionError or ValueError:

            return self.wait_for_a_move(conn, possible_move)
        if isinstance(move, tuple) and len(move) == 2 and all(isinstance(v, int) for v in move):
            return move

    def deal_response_type(self, msg):

        # assert msg['type']
        msg_type = msg['type']
        if msg_type == 'move':
            # assert msg['to']
            if msg['to'] is None:
                move = None
            else:
                move = tuple(msg['to'])

            return move
        else:
            raise ValueError('Response does not supported. ')

    def send_move_result(self, conn, result: str):
        """
        "OK", meaning “the move was valid, nothing happened”
        "Key", meaning “the move was valid, player collected the key”
        "Exit", meaning “the move was valid, player exited”
        "Eject", meaning “the move was valid, player was ejected”
        "Invalid", meaning “the move was invalid”
        "Capture", meaning “the move was valid, adversary captured a player”
        :return:
        """
        if result == 'Invalid':
            msg = 'Invalid move. try again:'
            send_msg(conn, msg)
        send_msg(conn, result)

    @staticmethod
    def get_server_info():
        return 'Erenon'

    def send_welcome(self, conn):
        server_info = self.get_server_info()
        msg = {"type": "welcome", "info": server_info}
        print(json.dumps(msg))
        send_msg(conn, json.dumps(msg))

    def send_start_level(self, level_num, player_name_list, adversary_name_list):
        msg = {"type": "start-level", "level": level_num, "players": player_name_list,
               "adversaries": adversary_name_list}
        for _, conn in self.player_sockets.items():
            send_msg(conn, json.dumps(msg))
        for _, conn in self.adversary_sockets.items():
            send_msg(conn, json.dumps(msg))

    def send_player_update_message(self, message=None):
        """
        message are the following:
                                "Player <name> <event>.", where <event> is one of
                                    "moved"
                                    "found the key"
                                    "was expelled"
                                    "exited"
                                    "disconnected"
        :param message: specified above
        """
        for player_name, conn in self.player_sockets.items():
            player = self.manager.get_state().get_player_by_name(player_name)
            tile_layout = self.manager.get_state().get_level().get_seen_tiles_for_player(player.get_position())
            object_list = self.manager.get_state().get_objects_in_view(player_name)
            actors = self.manager.get_state().get_actors_in_view(player_name)
            position = self.manager.state.get_player_by_name(player_name).get_position()
            msg = {"type": "player-update", "layout": tile_layout, "position": position, "objects": object_list,
                   "actors": actors, "message": message}
            try:
                send_msg(conn, json.dumps(msg))
            except ValueError as e:
                print(e)
                print("Someone disconnected. Game end.")
                sys.exit()

    def send_adversary_update_message(self, message=None):
        """
        message are the following:
                                "Adversary <name> <event>.", where <event> is one of
                                    "moved"
                                    "capture a player"
                                    "disconnected"
        :param message: specified above
        """
        for adversary_name, conn in self.adversary_sockets.items():
            adversary = self.manager.get_state().get_adversary_by_name(adversary_name)
            if adversary is None:
                break
            tile_layout = self.manager.get_state().get_level().get_seen_tiles_for_adversary(adversary.get_position())
            object_list = self.manager.get_state().get_objects_in_view(adversary_name)
            actors = self.manager.get_state().get_actors_in_view(adversary_name)
            position = self.manager.state.get_adversary_by_name(adversary_name).get_position()
            msg = {"type": "adversary-update", "layout": tile_layout, "position": position, "objects": object_list,
                   "actors": actors, "message": message}
            try:
                send_msg(conn, json.dumps(msg))
            except Exception as e:
                print(e)
                print("Someone disconnected. Game end.")
                sys.exit()

    def send_end_level(self):

        msg = {"type": "end-level", "key": self.who_find_key, "exits": self.who_exits, "ejects": self.who_ejects}

        for _, conn in self.player_sockets.items():
            send_msg(conn, json.dumps(msg))
        for _, conn in self.adversary_sockets.items():
            send_msg(conn, json.dumps(msg))

    def send_end_game(self, scores, is_win):

        for _, conn in self.player_sockets.items():
            msg = {"type": "end-game", "scores": self.build_score_list(scores), "game-won": is_win}
            send_msg(conn, json.dumps(msg))
            conn.close()
        for _, conn in self.adversary_sockets.items():
            msg = {"type": "end-game", "scores": self.build_score_list(scores), "game-won": not is_win}
            send_msg(conn, json.dumps(msg))
            conn.close()

    @staticmethod
    def build_score_list(scores):
        score_list = []
        for score in scores:
            one_score = {"type": "player-score", "name": score['name'], "exits": score['exited_num'],
                         "ejects": score['ejected_num'], "keys": score['keys_found']}
            score_list.append(one_score)
        return score_list

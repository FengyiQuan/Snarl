import ast
import copy
import socket
import json
import sys
import time

from Snarl.src.GameManager import GameManager
from Snarl.src.RuleChecker import RuleChecker
from Snarl.src.util import send_msg, receive_msg
from Snarl.src.Remote.Server import Server


class MultiServer(Server):
    def __init__(self, ip: str, port: int, min_clients: int = 1, max_clients: int = 4, max_remote_adversary: int = 2,
                 reg_timeout: int = 60, observer: bool = False, manager: GameManager = None):

        super().__init__(ip, port, min_clients, max_clients, max_remote_adversary, reg_timeout, observer, manager)

        # self.sock = None
        # self.init_sock(ip, port)
        # self.player_sockets = {}
        # self.adversary_sockets = {}
        # self.remote_zombie_list = []
        # self.remote_ghost_list = []  # no use

        self.__new_manager = copy.deepcopy(manager)

        # self.who_find_key = None
        # self.who_exits = []
        # self.who_ejects = []
        #
        # self.setting = {'remote players': True, 'remote adversary': False}  # TODO: not supported remote adversary

        self.all_scores_board = []

    def run(self, total_level):
        self.player_sockets = {}
        self.adversary_sockets = {}
        self.remote_zombie_list = []
        self.manager = copy.deepcopy(self.__new_manager)

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


    def send_end_game(self, scores, is_win):
        self.add_scores_to_scores_board(scores)
        for _, conn in self.player_sockets.items():
            msg1 = {"type": "scores_board", "scores": self.__build_scores_board(self.all_scores_board),
                    "game-won": is_win}
            send_msg(conn, json.dumps(msg1))
            time.sleep(1)
            msg2 = {"type": "end-game", "scores": self.build_score_list(scores), "game-won": is_win}
            send_msg(conn, json.dumps(msg2))
            conn.close()
        for _, conn in self.adversary_sockets.items():
            msg = {"type": "end-game", "scores": self.build_score_list(scores), "game-won": not is_win}
            send_msg(conn, json.dumps(msg))
            conn.close()

    def add_scores_to_scores_board(self, scores):
        for one_score in scores:
            name_in_board = False
            for one_score_board in self.all_scores_board:
                if one_score['name'] == one_score_board['name']:
                    one_score_board['exited_num'] += one_score['exited_num']
                    one_score_board['ejected_num'] += one_score['ejected_num']
                    one_score_board['keys_found'] += one_score['keys_found']
                    name_in_board = True
                    break
            if not name_in_board:
                self.all_scores_board.append(one_score)


    @staticmethod
    def __build_scores_board(scores):
        score_list = []
        for score in scores:
            one_score = {score['name']: {"exits": score['exited_num'],
                                         "ejects": score['ejected_num'], "keys": score['keys_found']}}
            score_list.append(one_score)
        return score_list

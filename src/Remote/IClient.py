import json
import socket
import sys

from Snarl.src.util import send_msg, receive_msg


class IClient:
    def __init__(self, ip: str, port: int):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((ip, port))
        except socket.error:
            print("connect to server failed")

    def display_vision(self, msg):
        raise NotImplementedError()

    def choose_move(self):
        raise NotImplementedError()

    def register_name(self):

        while True:
            name = input('Enter your name:')
            if name and name.isalpha() and ' ' not in name:
                send_msg(self.sock, name)
                break
            else:
                print('invalid name. try again. ')

    def run(self):
        while True:
            # self.deal_response_type()
            try:
                self.deal_response_type()
            except Exception as e:
                print(e)
                print("Someone disconnected or game ended by admin. Game end.")
                sys.exit()

    def deal_response_type(self):
        """

        "OK", meaning “the move was valid, nothing happened”
        "Key", meaning “the move was valid, player collected the key”
        "Exit", meaning “the move was valid, player exited”
        "Eject", meaning “the move was valid, player was ejected”
        "Invalid", meaning “the move was invalid”
        """
        msg_raw = receive_msg(self.sock)
        move_result_string = ["OK", "Key", "Exit", "Eject", "Invalid", "Capture"]

        if msg_raw == "name":
            self.register_name()
        elif msg_raw == "move":
            self.choose_move()
        elif msg_raw in move_result_string:
            if msg_raw == "Invalid":
                print("invalid move. please try to move to another point. ")
            else:
                print("move succeed. ")
        else:
            # try:
            msg = json.loads(msg_raw)
            # except Exception:
            #     print(msg_raw)
            #     raise ValueError("invalid message sent by server", msg_raw)
            assert msg['type']
            msg_type = msg['type']
            print(msg_type)
            if msg_type == 'welcome':
                self.receive_welcome_msg(msg)
            elif msg_type == 'start-level':
                self.receive_start_level_msg(msg)
            elif msg_type == 'player-update':
                self.receive_player_update_message(msg)

            elif msg_type == 'adversary-update':
                self.receive_adversary_update_message(msg)
            elif msg_type == 'end-level':
                self.receive_end_level_message(msg)
            elif msg_type == 'scores_board':
                self.receive_scores_board_message(msg)
            elif msg_type == 'end-game':
                self.receive_end_game_message(msg)
            else:
                raise ValueError('Response does not supported. ')

    def receive_welcome_msg(self, msg):
        welcome_info = msg["info"]
        print("welcome message:", welcome_info)

    def receive_start_level_msg(self, msg):
        level_num = msg["level"]
        players = msg["players"]
        adversary = msg["adversaries"]
        print("level_number: " + str(level_num) + "\nplayers: " + str(players) + "adversaries: " + str(adversary))

    def receive_player_update_message(self, msg):
        player_vision = self.display_vision(msg)
        print("player_view_updated:\n", player_vision)
        print("event happened: ", msg["message"])

    def receive_adversary_update_message(self, msg):
        adversary_vision = self.display_vision(msg)
        print("adversary_view_updated:\n", adversary_vision)
        print("event happened: ", msg["message"])

    def receive_end_level_message(self, msg):
        name = msg["key"]
        exits_list = msg["exits"]
        ejects_list = msg["ejects"]
        print("level ended.\n", name, "found key.\n", exits_list, "exits.\n", ejects_list, "ejects.\n")

    def receive_end_game_message(self, msg):
        score_list = msg["scores"]
        print("Game ended.\n", "Scores_lists:\n", score_list)
        self.sock.close()
        sys.exit()

    def receive_scores_board_message(self, msg):
        score_list = msg["scores"]
        score_list_str = json.dumps(score_list)
        print('\x1b[1;33;40m' + 'Scores_board:' + '\x1b[0m' + score_list_str)

    def get_object_type_by_coord_from_two_lists(self, point, object_list, actor_position_list):
        key_position = None
        exit_position = None
        for obj in object_list:
            if obj["type"] == "key":
                key_position = tuple(obj["position"])
            elif obj["type"] == "exit":
                exit_position = tuple(obj["position"])
            else:
                raise ValueError("invalid object")
        player_positions = []
        zombie_positions = []
        ghost_positions = []
        for actor in actor_position_list:
            if actor["type"] == "player":
                player_positions.append(tuple(actor["position"]))
            elif actor["type"] == "zombie":
                zombie_positions.append(tuple(actor["position"]))
            elif actor["type"] == "remote zombie":
                zombie_positions.append(tuple(actor["position"]))
            elif actor["type"] == "ghost":
                ghost_positions.append(tuple(actor["position"]))
            elif actor["type"] == "remote ghost":
                ghost_positions.append(tuple(actor["position"]))
            else:
                raise ValueError("invalid actor")

        if point in player_positions:
            result = "player"
        elif point in ghost_positions:
            result = "ghost"
        elif point in zombie_positions:
            result = "zombie"
        elif point == key_position:
            result = "key"
        elif point == exit_position:
            result = "exit"

        else:
            result = None
        return result

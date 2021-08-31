#!/usr/bin/python3
from Snarl.src.ICharacter import Player, Adversary


class RuleChecker:
    @staticmethod
    def validate_movement(game_state, name, position):
        if game_state.is_player_name_exist(name):
            player = game_state.get_player_by_name(name)
            moves = RuleChecker.get_possible_movement(game_state, player)
            return position in moves
        if game_state.is_adversary_name_exist(name):
            adversary = game_state.get_adversary_by_name(name)
            return position in RuleChecker.get_possible_movement(game_state, adversary)

    @staticmethod
    def get_possible_movement(game_state, character) -> list:
        """
        get all possible movement by given player in the game State
        :param game_state: current game State that includes the game level information
        :param character: can be player or adversary
        :return: a list of coordinate which character is able to move to
        """

        level = game_state.get_level()  # the layout of the current map
        character_name = character.get_name()

        reachable_tile_character_can_reach = level.get_reachable_tiles(character)
        players_pos = [c.get_position() for c in game_state.get_players() if c.get_is_alive()]
        adversaries_pos = [c.get_position() for c in game_state.get_adversaries()]
        if isinstance(character, Player):
            reachable_tile_character_can_reach = [tile for tile in reachable_tile_character_can_reach if
                                                  tile not in players_pos]
            reachable_tile_character_can_reach.append(None)
        if isinstance(character, Adversary):
            reachable_tile_character_can_reach = [tile for tile in reachable_tile_character_can_reach if
                                                  tile not in adversaries_pos]
            if len(reachable_tile_character_can_reach) == 0:
                reachable_tile_character_can_reach.append(None)

        # players_and_adversaries = game_state.get_players() + game_state.get_adversaries()
        # players_and_adversaries_pos = [c.get_position() for c in players_and_adversaries if
        #                                c.get_name() != character_name]

        # reachable_tile_character_can_reach = [tile for tile in reachable_tile_character_can_reach if
        #                                       tile not in players_and_adversaries_pos]
        return reachable_tile_character_can_reach

    @staticmethod
    def is_game_end(game_state):
        return RuleChecker.is_game_lose(game_state) or RuleChecker.is_game_win(game_state)

    @staticmethod
    def is_game_lose(game_state):
        # return any([not player.is_alive() for player in game_state.get_players()])
        result = True
        for p in game_state.get_players():
            if p.get_is_alive():
                result = False
        return result

    @staticmethod
    def is_game_win(game_state):
        """
        :param game_state: game_state
        :return: True if game is win (players reach the final exit successfully)
        """
        is_final_level = (game_state.get_current_level_num() == game_state.get_total_level_num())
        return is_final_level and RuleChecker.is_level_success(game_state)

    @staticmethod
    def is_level_success(game_state):
        """
         :param game_state: game_state
         :return: True if any players reach the open exit successfully in current level
         """
        exit_pos = game_state.get_level().get_exit_pos()
        players_position = [player.get_position() for player in game_state.get_players()]
        adversary_position = [ad.get_position() for ad in game_state.get_adversaries()]
        any_player_exit = any([pos for pos in players_position if pos == exit_pos])
        no_adversary_at_exit = not any([pos for pos in adversary_position if pos == exit_pos])
        is_door_open = not game_state.get_exit_locked()

        return is_door_open and any_player_exit and no_adversary_at_exit

    @staticmethod
    def is_level_end(game_state):
        return RuleChecker.is_level_success(game_state) or RuleChecker.is_game_end(game_state)

    @staticmethod
    def is_only_one_players_remain(game_state):
        return len([player for player in game_state.get_players() if player.is_alive()]) == 1

    @staticmethod
    def is_the_last_level(game_state):
        return game_state.get_current_level_num() == game_state.get_total_level_num()

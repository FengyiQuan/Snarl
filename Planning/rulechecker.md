### Rule Checker
For Rule Checker component, it validates the movements and interactions from players and adversaries as well as 
determine the end of a level versus the end of the game. Below lists the functions we consider necessary for this 
interface.

`def validate_movement(game_state, character, position)` check if a movement to a given position is valid which means
this movement is in the possible movements that a character might perform  
`def get_possible_movement(game_state, character)` get a list of possible position that a character can reach based on 
its moving ability and some special rules  
`def character_interact(character, game_state)` return a new game state after interaction happened, character can be 
either players or enemy  
`def player_interact(player, game_state)` helper function that only concern about players interaction  
`def enemy_interact(player, interact_object, game_state)` helper function that only concern about players interaction  
`def is_game_end(game_state)` check if game is end either lose or win  
`def is_game_lose(game_state)` check if all players eliminated  
`def is_game_win(game_state)` check if game is win (players reach the final exit successfully)  
`def is_level_success(game_state)` check if any players reach the open exit successfully in current level  

We decided to add `move_range`, `move_requirement` fields to each characters to extend the flexibility to handle if some
new characters added either new player type or new adversary type.  
`move_range` is the ability how far a character can reach  
`move_requirement` is the restriction that character can move, for example, normal players move_requirement should be 
non-wall and a ghost type adversary could potentially ignore walls entirely should be none.

To make sure that every necessary methods are implemented, we create a `ICharacter` and a `IObject` interface to manage
the common methods. These interface and class are placed under src/.
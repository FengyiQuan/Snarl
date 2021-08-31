### Player
For Player component, it represents the interests of the human behind the keyboard in the game. A Player needs to 
receive updates from the Game Manager at appropriate moments. When it’s the Player’s turn, it needs to communicate 
the chosen action to the Game Manager.

#### Fields for Player
`id` unique id that indicate the player order  
`name` players name  
`position` absolute position in the given level  
`moving_ability` maximum range that a player can reach   
`sight_range` maximum range that a player can see  
`move_requirement`  moving requirement, such that player cannot go through the wall
`is_alive` if a player is alive

Below lists the functions we consider necessary for this interface.  
`move(self, position)` move to a given position, send move request to the server 
`register(self, server, name)` register on the game, the server will send the unique id and other necessary information 
back  

We don't have interact function in Player class since interaction can be done at server level, the player only concern
to make a move. Player can choose a list of possible moves that 2 grid units away in any cardinal or diagonal direction.
Once they send the move request to the server, the server will check if it is a valid move. If not, the server will wait
and resend the request that ask the player to choose a valid move.
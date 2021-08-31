### Game Manager
For Game Manager, it accepts players to the game and starts a game with a single level, which will be provided.

Below lists the functions we consider necessary for this interface.  
`init_level(self)` initialize the level  
`init_player(self)` send player information back to the sender (player)  
`send_seen_grid_to_player(self, player_id, state)` send list of grid information (coordinate and tile type) to the given player  
`send_position_to_player(self, player_id, state)` send the current position (absolute coordinate) to the given player  
### interface state manager
***
State manager is the interface that components are using for communicating information with the snarl state.<br>
It is used for actors to acquire necessary information (like view), as well as perform actions and movements.<br>
Below lists the functions we consider necessary for this interface.<br>
***
generate a random level <br>
`generate_level()` <br>

take in the number of players in this game <br>
initialize players, set their alive status to true, and put them into random locations <br>
`init_players(number)` <br>

take in the number of adversaries in this game <br>
initialize adversaries, and set their locations <br>
`init_adversaries(number)` <br>

return boolean, representing if key has been picked up by any player.<br>
`keyPicked()`<br>

take the player id.<br>
return location by the given player id.<br>
`getPlayerLocation(playerID)`<br>

take the player id.<br>
return boolean representing if the player is alive.<br>
`playerAlive(playerID)`<br>

take the player id and the move order.<br>
return boolean representing if the move is valid.<br>
`validPlayerMove(playerID, move)`<br>

take the player id and the move order.<br>
update the state according to the move.<br>
`playerMove(playerID, move)`<br>

take the adversary id and the move order.<br>
return boolean representing if the move is valid.<br>
`validAdversaryMove(advID, move)`<br>

take the adversary id and the move order.<br>
update the state according to the move.<br>
`adversary(advID, move)`<br>

take the player ID.<br>
return the surrounding view of the player(could be represented in a dictionary).<br>
`surroundingView(playerID)`<br>

return the snarl level.<br>
`allView()`<br>
***

### Snarl State:
***
Snarl state would contain information necessary to check validity of moves and progress the game.<br>
Below is the fields that we consider necessary to store all information.<br>
***
`snarl_level` the current level layout<br>
`door_location` door location<br>
`key_location` key location<br>
`players_id` all players id<br>
`players_alive` dictionary that key is the player id, while the value is boolean representing if player is alive<br>
`players_location` dictionary that key is the player id, while the value is some data representation representing players locations<br>
`players_order` dictionary that key is the player id, while the value is number representing players order.<br>
`adversaries_id` all adversaries
`adversaries_locations` the locations of the adversaries<br>
`isLose` boolean if a game is lose<br> 
`isWin` boolean if a game is win<br>
`connection` connection to communicate within players<br>
`ifKeyPicked` if the key has been picked up<br>
***

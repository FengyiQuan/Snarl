### interface observable
***
Observable interface allows delivery of game information, such as the view of the level, number of alive players, number of rooms, etc.<br>
Functions in this interface demonstrates what information we think could come handy for testing and debugging purpose.<br>
More functions could be added in in future iterations.<br>
***
TODO: what arguments to take in?<br>
update the information in observer classes. The information that goint to feed in is TBD.<br>
`update(???)` <br>

return the visual view of current snarl level, with objects and characters.<br>
`allView()`<br>

take in the id of a player.<br>
return the visual view of a certain player, since a player could only see view around the player.<br>
`playerView(playerID)`<br>

return the number of terrains, represented in a dictionary with the key being terrain type(currently only room and hallway), and the value being number.<br>
`allTerrainsNumber()`<br>

return the location for each player, represented in a dictionary with the key being playerID, and the value being location.<br>
`allPlayersLocation()`<br>

return the location for each adversary, represented in a dictionary with the key being adversaryID, and the value being location.<br>
`allAdversariesLocation()`<br>

return the type for each adversary, represented in a dictionary with the key being adversaryID, and the value being types.<br>
`allAdversariesType()`<br>

return the status for each player, represented in a dictionary with the key being playerID, and the value being status(in-game, exited, expelled).<br>
`allPlayersStatus()`<br>

return the status for key, with true representing key has been picked, false representing key has not been picked.<br>
`keyPicked()`<br>

return the status for exit, with true representing door has been opened, false representing door has not been opened.<br>
`exitOpened()`<br>

return the status for the game of current level, with true representing level has finished, false representing door has not finished.<br>
`levelEnded()`<br>
***


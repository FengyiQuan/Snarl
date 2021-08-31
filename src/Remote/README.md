### README for option1: Multiserver game
1. run `./snarlServer1` first, you can specify the number of remote player.<br>
2. to connect to server as player, you need to run `./snarlClient1`<br>
3. when connect as players, you must run specified number of players(snarlClient), or have to wait to timeout first.<br>
4. each time a socket connect to server, it will ask a name from you.<br>
5. then, please follow the instructions along within the game process<br>
6. when one game ends the client will receive leaderboard(scores_board) and close the client socket. The server socket will pop of instructions for input. If you type "exit" and hit enter, the server will shutdown, if type anything other than "exit" and hit enter, the server will continue listening for other connections for other players to join in the next game<br>

### Important:
1. our coordinate is reverse from what instructor gived us. For example, the first number is x, the second number is y. <br>

### set up process
1. run server, run client

### README for option3: Remote Adversaries
1. run snarlServer3 first, you can specify the number of remote player and remote adversary.
2. to connect to server as player, you need to run `./snarlClient`
3. to connect to server as adversary, you need to run `./snarlClientAdversary`
4. above two could create the different instance of the client type. They are almost the same, rather than behavior of 
handling message type.
5. when connect as players, you must run specified number of players(snarlClient), or have to wait to timeout first.
6. then running connection as adversary, you can connect to server as much as the number you specified. but it will not 
all used since the first level could be only one zombie, and the rest of socket gonna wait until new level required more
number of adversaries.
7. To initialize the adversary every time a level started, it will first fulfill the socket into zombie. If sockets have
remaining, it will become remote ghost. 
7. each time a socket connect to server, it will ask a name from you.
8. then, please follow the instructions along within the game process
9. to better see what's going on on the server side, please add observe flag.
10. the users controlled character would be colored and some other would printed in different color to have a better 
appearance.
11. when register adversaries, cannot use zombie/ghost + number format, it reserved for local adversary only!!!
12. 



### Important:
1. player cannot see the adversary move (should not receive adversary update message)
2. adversary would see the whole board
3. adversary cannot enter None to stay at position (must move to another point)
4. receive end message should differ
5. adversary would not receive players update
6. adversary type would assign to users every time a level start 


### set up process
1. run server, run player client, run adversary client
2. cannot run adversary client first!!!
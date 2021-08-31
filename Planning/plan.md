### Part2 milestones for the project
- Milestone1, research and discover: discuss and make sure to satisfy the specifications for the project through piazza, office hours, and partner meetings
- Milestone2, complete the roadmap for design: complete our design for components, network, etc. Create UML diagrams and memo documents
- Milestone3, implement functions: We would implement components and their functions first. Test out the correctness of functions. Create an easy user interface to demonstrate its functionality and test it out
- Milestone4, add networks: then we separate components, and create network connections between players and server(adversary and map). Test out programs through different computers
- Milestone5, design user interface: research and design user-friendly user interface. Testing the user interface
***

### Explanations for UML
1.	Each player initializes connections to the server, which is made of two components: map and automated adversaries, then the server would initialize each player’s location in the map and send to each player, the game begins
3.	During the game, if it comes to one player’s turn, the player would send movement request in turn to the server component(map).
4.	After each player finishes their turn, the map components in the server would give information to adversary, and adversary would make decisions through the given information and let map components know how adversary would move. 
5.	For each time a player/an adversary makes a move, map component would receive that information and generate new map state based on the movement; the new state(available part for specific player, which may be different from one another) would be sent to each of the player. Only when all player finishes their move, the map state would be sent to automated adversaries component for the AI to make movement.

***
The overall design is the following:

### Player: 
***
A character that player can control to move and interact with certain stuff.   
`name` a unique string to represent a certain players  
`location` the location of the player  
`isSurvived` boolean whether this character is alive  
`isSuccessful` boolean whether this character is escape successfully  
`isActed` boolean whether this character complete this round 

`Player` should support the following operations:
```
    # move a player
    move(self, movement)
    # interact with the object in its location
    interact(self, object)

```
Player knows the surrounding tiles information and layout in order to choose a correct location to move. They should 
need to know whether some players have found the key and the door is open. They also need to know the other players 
view which includes others location and visible tiles to plan for the next move together.

### Interaction (Function class)
***
Interaction is all possible interactions that players or enemy can perform.

```
    # interaction that a player can perform
      If the object is a key, the key is removed from the level and the exit is unlocked. If that object is a locked 
      exit, nothing happens. If that object is an unlocked exit, the player leaves the dungeon, represented by the 
      avatar being removed from the level.
    player_interact(player, object, state)
    
    # interaction that a enemy can perform
      If that object is a player, the player is expelled from the game
    enemy_interact(player, object, state)
```
Interaction needs to know the whole game state and which two are going to interact. All fields are passed in as params.

### Grids:
Grids define the whole dungeon map. It represents as a 2d list. Each element can contains an object which locates in
this grid. Object can be `wall`, `hallway`, `room`.

### GameState
***
GameState defines the state space, start state, goal state, successor function.  
`grids` a whole layout of game dungeon map  
`door_location` door location  
`key_location` key location  
`players` all players in the game  
`enemies` all enemies in the game  
`isLose` boolean if a game is lose  
`isWin` boolean if a game is win  
`connection` connection to communicate within players  
`level` level information  

`GameState` should support the following operations:
```
    # get the start state
    def getStartState(self) 

    # check if the game should finished, finished when lose or win
    def isGoalState(self, state)
    
    # get the surronding tiles by given the current tiles and range
    def getSuccessor(self, currentLocation, range)
    
    # return the object by the given location
    def getObject(self, location)
```
GameState should know all information related to games in order to make everything works, including grids layout, all
players and enemies location, door and key location and level information.

### Enemy
***
A Enemy is an automated adversary to against players. When it interact with a player, the player will be expelled from 
the game.  
`location` the location of the player

`Enemy` should support the following operations:
```
    # move a player
    move(self, movement)
```
Enemy knows the whole dungeon level and layout they occupy in order to chase the player.

### Door
***
The door that is a exit for players. If it is locked, players can not go through it.  
`location` the location of the player  
`isLocked` boolean if it is locked  

`Door` should support the following operations:
```
    # get the door location
    getLocation(self)
    # get the boolean if it is locked
    isLocked(self)
```
Door needs to know if players find the key.


### Key:
The key that can open the door.  
`location` the location of the player

`Key` should support the following operations:
```
    # get the key location
    getLocation(self)
```


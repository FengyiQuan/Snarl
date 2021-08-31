move_achieved: bool  
move_status: str (no practical usage, only for generating information)  
is_alive: bool  
location: (_, _) tuple  
surrounding_tile: map-like string that indicate the surrounding area (key is coordinate, value is 'one char indicate object') 


It should be have a type field to indicate what type of the message has been send to players. once player received, it
know how to deal with the certain message type 
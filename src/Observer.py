#!/usr/bin/python3


import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(os.path.split(rootPath)[0])

import copy
from abc import ABC, abstractmethod
from Snarl.src.GameState import GameState

class Observable(ABC):
 
    def render(self):
        pass

    def update(self):
        pass
 
class Observer(Observable):
 
    def __init__(self, game_state):
        self.game_state = game_state

    
    def render(self):
        print(GameState.__str__(self.game_state))


    def update(self, game_state):
        self.game_state = game_state
# ActionHistory.py

from enum import Enum, unique
from ActionSuccess import *

# Enumeration for layer types
class ActionType(Enum):
    MOVE_FORWARD    = 0
    MOVE_BACKWARD   = 1
    ROTATE_CW       = 2
    ROTATE_CCW      = 3
    PICKUP          = 4
    PUT             = 5
    DROP            = 6 
    OPEN            = 7
    CLOSE           = 8
    ACTIVATE        = 9
    DEACTIVATE      = 10
    TALK            = 11
    EAT             = 12
    READ            = 13
    USE             = 14

# Stores the action history for one agent
class ActionHistory:
    # Constructor
    def __init__(self, world):
        self.history = []
        self.world = world

    # Add an action to the history
    def add(self, actionType:ActionType, arg1, arg2, result:ActionSuccess):
        packed = {
            'actionType': actionType,
            'arg1': arg1,
            'arg2': arg2,            
            'success': result.success,
            'step': self.world.getStepCounter(),
            'result': result
        }

        return self.history.append(packed)

    def getLastAction(self):
        if (len(self.history) > 0):
            return self.history[-1]
        else:
            return None

    # Only returns the last action if it happened on the last step.  Otherwise, None
    def getLastStepAction(self):
        if (len(self.history) > 0):
            if (self.history[-1]['step'] == self.world.getStepCounter()):
                return self.history[-1]
        return None


    
    def __str__(self):
        strOut = ""
        for action in self.history:
            strOut += str(action) + "\n"
        return strOut

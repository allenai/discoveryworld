# ActionHistory.py

from enum import Enum, unique
from ActionSuccess import *
from ObjectModel import Object

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
    DISCOVERY_FEED_GET_UPDATES = 15
    DISCOVERY_FEED_GET_ARTICLES = 16
    DISCOVERY_FEED_GET_POST_BY_ID = 17
    DISCOVERY_FEED_CREATE_UPDATE = 18
    DISCOVERY_FEED_CREATE_ARTICLE = 19

# Returns a dictionary of action descriptions
def getActionDescriptions():
    actionDescriptions = {
        ActionType.MOVE_FORWARD.name:   {"arguments": [], "desc": "move forward 1 step"}, 
        ActionType.MOVE_BACKWARD.name:  {"arguments": [], "desc": "move backward 1 step"}, 
        ActionType.ROTATE_CCW.name:     {"arguments": [], "desc": "move counter-clockwise 90 degrees"}, 
        ActionType.ROTATE_CW.name:      {"arguments": [], "desc": "move clockwise 90 degrees"}, 
        ActionType.PICKUP.name:         {"arguments": ["arg1"], "desc": "pick up an object (arg1)"},
        ActionType.DROP.name:           {"arguments": ["arg1"], "desc": "drop an object (arg1)"},
        ActionType.PUT.name:            {"arguments": ["arg1", "arg2"], "desc": "put an object (arg1) in/on another object (arg2)"},
        ActionType.OPEN.name:           {"arguments": ["arg1"], "desc": "open an object (arg1)"},
        ActionType.CLOSE.name:          {"arguments": ["arg1"], "desc": "close an object (arg1)"},
        ActionType.ACTIVATE.name:       {"arguments": ["arg1"], "desc": "activate an object (arg1)"},
        ActionType.DEACTIVATE.name:     {"arguments": ["arg1"], "desc": "deactivate an object (arg1)"},
        ActionType.TALK.name:           {"arguments": ["arg1"], "desc": "talk to another agent (arg1)"},
        ActionType.EAT.name:            {"arguments": ["arg1"], "desc": "eat an object (arg1)"},
        ActionType.READ.name:           {"arguments": ["arg1"], "desc": "read an object (arg1)"},
        ActionType.USE.name:            {"arguments": ["arg1", "arg2"], "desc": "use an object (arg1) on another object (arg2)"},

        ActionType.DISCOVERY_FEED_GET_UPDATES.name:     {"arguments": [], "desc": "read the latest status updates on discovery feed"},
        ActionType.DISCOVERY_FEED_GET_ARTICLES.name:    {"arguments": [], "desc": "read the latest scientific articles on discovery feed"},
        ActionType.DISCOVERY_FEED_GET_POST_BY_ID.name:  {"arguments": ["arg1"], "desc": "read a specific post on discovery feed (arg1)"},
        ActionType.DISCOVERY_FEED_CREATE_UPDATE.name:   {"arguments": ["arg1"], "desc": "create a status update on discovery feed (arg1)"},
        ActionType.DISCOVERY_FEED_CREATE_ARTICLE.name:  {"arguments": ["arg1"], "desc": "create a scientific article on discovery feed (arg1)"}
    }
    return actionDescriptions

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


    # Export the action history to a list that can be converted to JSON
    def exportToJSONAbleList(self):
        out = []
        for action in self.history:            
            packed = {
                'actionType': action['actionType'].name,
                'arg1': None,
                'arg2': None,
                'success': action['success'],
                'step': action['step']
                #'result': not saved here
            }
            if (action['arg1'] != None):
                # Check type -- if it's an Object, then we need to pack it differently
                if (isinstance(action['arg1'], Object)):
                    packed['arg1'] = {"objUUID": action['arg1'].uuid}
                else:
                    # It's not an Object, so just pack it directly
                    packed['arg1'] = action['arg1'] 
                #packed['arg1'] = {"objUUID": action['arg1'].uuid}
            if (action['arg2'] != None):                
                # Check type -- if it's an Object, then we need to pack it differently
                if (isinstance(action['arg2'], Object)):
                    packed['arg2'] = {"objUUID": action['arg2'].uuid}
                else:
                    # It's not an Object, so just pack it directly
                    packed['arg2'] = action['arg2'] 
                #packed['arg2'] = {"objUUID": action['arg2'].uuid}

            out.append(packed)

        return out
    
    def __str__(self):
        strOut = ""
        for action in self.history:
            strOut += str(action) + "\n"
        return strOut

# KnowledgeScorer.py

from enum import Enum, unique

# # Enumeration for layer types
# class ActionType(Enum):
#     MOVE_FORWARD    = 0
#     MOVE_BACKWARD   = 1
#     ROTATE_CW       = 2
#     ROTATE_CCW      = 3
#     PICKUP          = 4
#     PUT             = 5
#     DROP            = 6 
#     OPEN            = 7
#     CLOSE           = 8
#     ACTIVATE        = 9
#     DEACTIVATE      = 10
#     TALK            = 11
#     EAT             = 12
#     READ            = 13
#     USE             = 14

# Enumeration for property operators
class PropertyOperator(Enum):
    EQUALS = 0
    LESS_THAN = 1
    GREATER_THAN = 2
    LESS_THAN_OR_EQUAL = 3
    GREATER_THAN_OR_EQUAL = 4
    NOT_EQUAL = 5
    CONTAINS_LIST = 6                   # e.g. ["red", "green", "blue"]


# Storage class for an object reference, which may or may not include additional property filtering/scoping.
class ObjectReference():
    def __init__(self):
        # Keep track of any errors
        self.errors = []

        # Can refer to a specific object (by UUID), an object by name ('name'), or a class of objects (by 'type')
        self.objectUUID = None
        self.objectName = None
        self.objectType = None

        # Can scope the reference to objects with specific properties
        self.properties = {}

    


# Storage class for an object-operator-property combination (e.g. 'color', 'equals', 'red')
class ObjectProperty():
    def __init__(self, propertyName:str, propertyOperator:str, propertyValue:str):
        # Keep track of any errors
        self.errors = []

        # Parse
        self.propertyName = propertyName
        self.propertyOperator = self._parsePropertyOperator(propertyOperator)
        self.propertyValue = propertyValue

        # Validate (TODO, make this more robust)
        self.isValid = True if (len(self.errors) == 0) else False

    # Convert form a string representation of the Enum to the Enum
    def _parsePropertyOperator(self, strIn:str):
        # Sanitize the input
        strIn = strIn.strip().upper()

        if (strIn == "EQUALS"):
            return PropertyOperator.EQUALS
        elif (strIn == "LESS_THAN"):
            return PropertyOperator.LESS_THAN
        elif (strIn == "GREATER_THAN"):
            return PropertyOperator.GREATER_THAN
        elif (strIn == "LESS_THAN_OR_EQUAL"):
            return PropertyOperator.LESS_THAN_OR_EQUAL
        elif (strIn == "GREATER_THAN_OR_EQUAL"):
            return PropertyOperator.GREATER_THAN_OR_EQUAL
        elif (strIn == "NOT_EQUAL"):
            return PropertyOperator.NOT_EQUAL
        elif (strIn == "CONTAINS_LIST"):
            return PropertyOperator.CONTAINS_LIST
        else:
            #raise ValueError("Unknown property operator: " + strIn)
            self.errors.append ("Unknown property operator: " + strIn)
            return None




# Stores the action history for one agent
class KnowledgeRecorder:
    # Constructor
    def __init__(self, world):
        
        # Different types of scientific knowledge
        self.measurements = []
        self.hypotheses = []
        self.hypothesisConfirmReject = []
        self.laws = []
        self.theories = []
        self.models = []

        self.world = world

    # Add an action to the history
    # def add(self, actionType:ActionType, arg1, arg2, result:ActionSuccess):
    #     packed = {
    #         'actionType': actionType,
    #         'arg1': arg1,
    #         'arg2': arg2,            
    #         'success': result.success,
    #         'step': self.world.getStepCounter(),
    #         'result': result
    #     }

    #     return self.history.append(packed)

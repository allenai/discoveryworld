# ActionSuccess.py
from enum import Enum, unique

# Enumeration to define different types of action results (success, completion, failure)
class ActionResult(Enum):
    SUCCESS     = 0
    COMPLETED   = 1
    SUSPEND     = 2
    FAILURE     = 3
    INVALID     = 4
    

# Enumeration to define message importance
class MessageImportance(Enum):
    LOW         = 0
    NORMAL      = 1
    HIGH        = 2
    


# Storage class for the result of an action
class ActionSuccess:
    # Constructor
    def __init__(self, success, message, importance = MessageImportance.NORMAL):
        self.success = success
        self.message = message
        self.importance = importance
        self.data = {}
    
    # String method
    def __str__(self):
        return "ActionSuccess(" + str(self.success) + ", " + str(self.importance) + ", " + str(self.message) + ")"



# Storage class for the result of a "use with" action
class UseWithSuccess(ActionSuccess):
    # Constructor
    def __init__(self, success, message, generatedItems = [], importance = MessageImportance.NORMAL):
        ActionSuccess.__init__(self, success, message, importance)
        self.data['generatedItems'] = generatedItems


    
    # String method
    def __str__(self):
        return "UseWithSuccess(" + str(self.success) + ", " + str(self.importance) + ", " + str(self.message) + ", " + str(self.item) + ")"


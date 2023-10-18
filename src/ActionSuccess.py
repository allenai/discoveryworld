# ActionSuccess.py
from enum import Enum, unique

# Storage class for the result of an action
class ActionSuccess:
    # Constructor
    def __init__(self, success, message):
        self.success = success
        self.message = message
    
    # String method
    def __str__(self):
        return "ActionSuccess(" + str(self.success) + ", " + str(self.message) + ")"



# Enumeration to define different types of action results (success, completion, failure)
class ActionResult(Enum):
    SUCCESS = 0
    COMPLETED = 1
    FAILURE = 2
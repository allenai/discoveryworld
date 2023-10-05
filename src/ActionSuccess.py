# ActionSuccess.py

# Storage class for the result of an action
class ActionSuccess:
    # Constructor
    def __init__(self, success, message):
        self.success = success
        self.message = message
    
    # String method
    def __str__(self):
        return "ActionSuccess(" + str(self.success) + ", " + str(self.message) + ")"
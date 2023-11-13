# KnowledgeScorer.py

from enum import Enum, unique
import json

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
    def __init__(self, dictIn:str): # objectUUID:str, objectName:str, objectType:str, properties:dict):
        # Keep track of any errors
        self.errors = []

        # Can refer to a specific object (by UUID), an object by name ('name'), or a class of objects (by 'type')
        self.objectUUID = None
        self.objectName = None
        self.objectType = None

        # Parse object UUID, name, or type from the dictionary (but, should have only one)
        refCount = 0
        if ('objectUUID' in dictIn):
            self.objectUUID = dictIn['objectUUID']
            refCount += 1
        if ('objectName' in dictIn):
            self.objectName = dictIn['objectName']
            refCount += 1            
        if ('objectType' in dictIn):
            self.objectType = dictIn['objectType']
            refCount += 1
        # Check that only one of these is set
        if (refCount > 1):
            self.errors.append("Object reference can only have one of 'objectUUID', 'objectName', or 'objectType'")
        elif (refCount == 0):
            self.errors.append("Object reference must have one of 'objectUUID', 'objectName', or 'objectType'")


        # Parse properties (which are called 'scope' in the JSON dictionary)
        self.properties = {}
        if ('scope' in dictIn):
            propListToParse = dictIn['scope']
            for propToParse in propListToParse:
                prop = ObjectProperty(propToParse)
                if (prop.isValid):
                    self.properties[prop.propertyName] = prop
                else:
                    self.errors.append("Unable to parse property: " + str(propToParse))

        # Validate (TODO, make this more robust)
        self.isValid = True if (len(self.errors) == 0) else False


    # String method
    def __str__(self):
        strOut = "ObjectReference("
        if (self.objectUUID is not None):
            strOut += "UUID: " + self.objectUUID + ", "
        if (self.objectName is not None):
            strOut += "Name: " + self.objectName + ", "
        if (self.objectType is not None):
            strOut += "Type: " + self.objectType + ", "
        if (len(self.properties) > 0):
            strOut += "Properties: "
            for propName in sorted(self.properties.keys()):
                strOut += "'" + propName + "': " + str(self.properties[propName]) + ", "
        strOut += ")"
        return strOut


# Storage class for an object-operator-property combination (e.g. 'color', 'equals', 'red')
class ObjectProperty():
    def __init__(self, dictIn:dict):
        # Keep track of any errors
        self.errors = []

        # Parse
        self.propertyName = _parseDictValue(dictIn, 'propertyName', self.errors)             
        propertyOperatorStr = _parseDictValue(dictIn, 'propertyOperator', self.errors)                
        self.propertyOperator = _parsePropertyOperator(propertyOperatorStr, self.errors)
        self.propertyValue = _parseDictValue(dictIn, 'propertyValue', self.errors)        
        
        # Validate (TODO, make this more robust)
        self.isValid = True if (len(self.errors) == 0) else False


    # String method
    def __str__(self):
        return "(" + str(self.propertyName) + ", " + str(self.propertyOperator) + ", " + str(self.propertyValue) + ")"


# Storage class for a measurement, which contains an object reference, and a property
class Measurement():
    def __init__(self, dictIn:dict):
        # Keep track of any errors
        self.errors = []

        # Parse

        # Field 1: Object reference
        objReference = _parseDictValue(dictIn, 'object', self.errors)
        self.objectReference = ObjectReference(objReference)
        self.errors += self.objectReference.errors

        # Field 2: Property
        property = _parseDictValue(dictIn, 'property', self.errors)
        self.propertyMeasurement = ObjectProperty(property)
        self.errors += self.propertyMeasurement.errors

        # Validate (TODO, make this more robust)
        self.isValid = True if (len(self.errors) == 0) else False


    # String method
    def __str__(self):
        return "Measurement(" + str(self.objectReference) + ", PropertyMeasurement: " + str(self.propertyMeasurement) + ")"



#
#   Helper functions
#
def _parseDictValue(dictIn:dict, fieldName:str, errors:list):    
    if (fieldName in dictIn):
        return dictIn[fieldName]
    else:
        errors.append("Missing field in property: " + fieldName)
        return None

# Convert form a string representation of the Enum to the Enum
def _parsePropertyOperator(strIn:str, errors:list):    
    if (strIn == None):
        errors.append("Missing property operator")
        return None

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
        errors.append ("Unknown property operator: " + strIn)
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





# 
#   Tests
#

if __name__ == "__main__":
    # Test ObjectReference
    print("Testing ObjectReference")

    # JSON string
    #jsonStr = """{"objectUUID": "1234"}"""
    jsonStr = """{"objectUUID": "1234", "scope":[{"propertyName":"color", "propertyOperator":"equals", "propertyValue":"red"}, {"propertyName":"size", "propertyOperator":"less_than", "propertyValue":5}]}"""
    jsonStr = """
    {
        "object": {"objectUUID": "1234", "scope":[{"propertyName":"color", "propertyOperator":"equals", "propertyValue":"red"}, {"propertyName":"size", "propertyOperator":"less_than", "propertyValue":5}]},
        "property": {"propertyName":"color", "propertyOperator":"equals", "propertyValue":"blue"}
    }
        """    
    # Convert to a dictionary
    dictIn = json.loads(jsonStr)
    
    # Create an ObjectReference
    #objRef = ObjectReference(dictIn)
    #print(objRef.errors)
    #print(objRef)

    # Create a Measurement
    measurement = Measurement(dictIn)
    print(measurement.errors)
    print(measurement)
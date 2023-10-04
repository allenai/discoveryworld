from enum import Enum, unique

# Enumeration for layer types
class Layer(Enum):
    WORLD = 0
    BUILDING = 1
    FURNITURE = 2
    OBJECTS = 3
    AGENT = 4

# Pathfinding.py

from Layer import Layer
from enum import Enum, unique

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder



class Pathfinder():
    # Constructor
    def __init__(self):
        pass

    # Find a path
    def findPathNextStep(self, world, startX, startY, endX, endY):

        # Step 1: Construct a cost grid representing the world, where each cell contains whether it's passable or not
        costGrid = []
        for y in range(world.sizeY):
            costGrid.append([])
            for x in range(world.sizeX):

                # By default, moving to the next cell has a base cost of 1
                passableScore = 1

                # Check if the cell is passable
                allObjs = world.getObjectsAt(x, y)

                # Check if any of the objects are impassable
                for object in allObjs:
                    if (not object.attributes["isPassable"]):
                        # Check to see if the object is a door, and therefore potentially passable
                        if (object.attributes["isPassage"]):
                            # Potentially passable, with a cost
                            passableScore = 20
                        else:
                            # Not passable (score of -1)
                            passableScore = -1

                        break
                # If this tile has any agents in it, increase its traversal cost
                if (passableScore > 0):
                    if (len(world.grid[x][y]["layers"][Layer.AGENT]) > 0):
                        passableScore += 10


                # Store the passability score
                costGrid[y].append(passableScore)

        # Step 2: Find a path using A*
        print("Finding path from (" + str(startX) + ", " + str(startY) + ") to (" + str(endX) + ", " + str(endY) + ")")
        
        # Use A* library to find a path
        grid = Grid(matrix=costGrid)

        start = grid.node(startX, startY)
        end = grid.node(endX, endY)

        finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
        path, runs = finder.find_path(start, end, grid)

        #print('operations:', runs, 'path length:', len(path))
        #print(grid.grid_str(path=path, start=start, end=end))

        # Get the next step in the path
        if (len(path) > 1):
            nextX = path[1].x
            nextY = path[1].y
            return (True, nextX, nextY)
        else:
            return (False, -1, -1)
        
        
    #
    #   Autopilot Functions
    #

    # Run the next step of a given autopilot action. 
    # Arguments:
    #   autopilotAction: The action to run
    #   agent: The agent running the action
    #   world: The world the agent is in
    # Returns:
    #   success: True (action running successfully) or False (action completed)
    def actionInterpreter(autopilotAction, agent, world):
        # First, figure out which type of action we're running
        actionType = autopilotAction.actionType
        # Then, run the appropriate function
        if (actionType == AutopilotActionType.GOTO_XY):
            return Pathfinder.runGotoXY(autopilotAction.args)
        elif (actionType == AutopilotActionType.PICKUP_OBJ):
            return Pathfinder.runPickupObj(autopilotAction.args)
        elif (actionType == AutopilotActionType.PLACE_OBJ_IN_CONTAINER):
            return Pathfinder.runPlaceObjInContainer(autopilotAction.args)
        elif (actionType == AutopilotActionType.WANDER):
            return Pathfinder.runWander(autopilotAction.args)
        elif (actionType == AutopilotActionType.WAIT):
            return Pathfinder.runWait(autopilotAction.args)
        else:
            print("ERROR: Invalid autopilot action type: " + str(actionType))
            return False
    

    def runGotoXY(args:dict):
        pass

    def runPickupObj(args:dict):
        pass

    def runPlaceObjInContainer(args:dict):
        pass

    def runWander(args:dict):
        pass

    def runWait(args:dict):
        pass

        





# Storage class for autopilot action
class AutopilotAction():
    # Constructor
    # ActionType is an enumeration (AutopilotActionType)
    # actionArguments are specific to each type of action
    def __init__(self, actionType, actionArguments:dict):
        self.actionType = actionType
        self.args = {}
    
    # String representation
    def __str__(self):
        return "AutopilotAction: " + str(self.actionType) + " (args: " + str(self.args) + ")"


# Specific action types
class AutopilotAction_GotoXY(AutopilotAction):
    # Constructor
    def __init__(self, x, y):
        self.actionType = AutopilotActionType.GOTO_XY
        self.args['destinationX'] = x
        self.args['destinationY'] = y

class AutopilotAction_PickupObj(AutopilotAction):
    # Constructor
    def __init__(self, objectToPickUp):
        self.actionType = AutopilotActionType.PICKUP_OBJ
        self.args['objectToPickUp'] = objectToPickUp

class AutopilotAction_PlaceObjInContainer(AutopilotAction):
    # Constructor
    def __init__(self, objectToPlace, container):
        self.actionType = AutopilotActionType.PLACE_OBJ_IN_CONTAINER
        self.args['objectToPlace'] = objectToPlace
        self.args['container'] = container

class AutopilotAction_Wander(AutopilotAction):
    # Constructor
    def __init__(self):
        self.actionType = AutopilotActionType.WANDER

class AutopilotAction_Wait(AutopilotAction):
    # Constructor
    def __init__(self):
        self.actionType = AutopilotActionType.WAIT


# Enumeration for types of autopilot actions
class AutopilotActionType(Enum):
    GOTO_XY                 = 0
    PICKUP_OBJ              = 1
    PLACE_OBJ_IN_CONTAINER  = 2
    WANDER                  = 3
    WAIT                    = 4
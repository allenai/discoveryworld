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
            return Pathfinder.runGotoXY(autopilotAction.args, agent, world)
        elif (actionType == AutopilotActionType.PICKUP_OBJ):
            return Pathfinder.runPickupObj(autopilotAction.args, agent, world)
        elif (actionType == AutopilotActionType.PLACE_OBJ_IN_CONTAINER):
            return Pathfinder.runPlaceObjInContainer(autopilotAction.args, agent, world)
        elif (actionType == AutopilotActionType.WANDER):
            return Pathfinder.runWander(autopilotAction.args, agent, world)
        elif (actionType == AutopilotActionType.WAIT):
            return Pathfinder.runWait(autopilotAction.args, agent, world)
        else:
            print("ERROR: Invalid autopilot action type: " + str(actionType))
            return False
    

    def runGotoXY(args:dict, agent, world):
        # First, check if we're already at the destination
        agentLocation = agent.getWorldLocation()
        if (agentLocation[0] == args['destinationX']) and (agentLocation[1] == args['destinationY']):
            # We're already there
            return True

        # Otherwise, find the next step in the path
        success = Pathfinder._doNPCAutonavigation(agent, world, args['destinationX'], args['destinationY'])
        print("runGotoXY: _doNPCAutonavigation returned: " + str(success))

        return success
        

    def runPickupObj(args:dict, agent, world):
        pass

    def runPlaceObjInContainer(args:dict, agent, world):
        pass

    def runWander(args:dict, agent, world):
        pass

    def runWait(args:dict, agent, world):
        pass

        

    #
    #   Helper functions
    #
    #
    #   NPC Auto-navigation
    #   
    def _doNPCAutonavigation(self, agent, world, destinationX, destinationY):
        pathSuccess, nextX, nextY = self.findPathNextStep(world, agent.attributes["gridX"], agent.attributes["gridY"], destinationX, destinationY)
        
        if (not pathSuccess):
            print("_doNPCAutonavigation: No path found to goal location.  Exiting. (agent: " + agent.name + ")")
            return False

        if ("doorNeedsToBeClosed" in agent.attributes) and (agent.attributes["doorNeedsToBeClosed"] != None) and (agent.attributes["movesSinceDoorOpen"] == 1):
            # We recently opened a door -- close it
            print("AGENT: CLOSING DOOR")
            doorToClose = agent.attributes["doorNeedsToBeClosed"]
            agent.actionOpenClose(doorToClose, "close")
            agent.attributes["doorNeedsToBeClosed"] = None
            agent.attributes["movesSinceDoorOpen"] = 0
        else:
            # Calculate deltas
            deltaX = nextX - agent.attributes["gridX"]
            deltaY = nextY - agent.attributes["gridY"]

            # First, check to see if we're facing the correct direction.  If not, start rotating in that direction.
            desiredDirection = agent.convertXYDeltasToDirection(deltaX, deltaY)
            if (desiredDirection != agent.attributes["faceDirection"]):
                # We're not facing the correct direction -- rotate
                print("AGENT: ROTATING TO FACE DIRECTION (curDirection: " + agent.attributes["faceDirection"] + ", desiredDirection: " + desiredDirection + ")")
                rotateSuccess = agent.rotateToFaceDirection(desiredDirection)
                print(rotateSuccess)
                return True

            # First, check to see if the next step has a barrier (like a door) that needs to be opened
            allObjs = world.getObjectsAt(nextX, nextY)
            # Get a list of objects that are not passable (isPassable == False)
            allObjsNotPassable = [obj for obj in allObjs if (obj.attributes["isPassable"] == False)]
            
            # If there are no impassable objects, then move the agent one step in the forward direction
            if (len(allObjsNotPassable) == 0):
                # Move agent one step in the forward direction
                #moveSuccess = self.actionMoveAgent(deltaX, deltaY)
                print("AGENT: MOVING FORWARD")
                moveSuccess = agent.actionMoveAgentForwardBackward(direction=+1)
                agent.attributes["movesSinceDoorOpen"] += 1
            else:
                print("AGENT: TRYING TO OPEN IMPASSABLE OBJECT")
                # There's one or more impassable objects -- try to open them.
                for obj in allObjsNotPassable:
                    # Check to see if the object is openable
                    if (obj.attributes["isOpenable"]):
                        # Open the object
                        agent.actionOpenClose(obj, "open")
                        agent.attributes["doorNeedsToBeClosed"] = obj
                        agent.attributes["movesSinceDoorOpen"] = 0
                        # Break out of the loop
                        break

        return True




# Storage class for autopilot action
class AutopilotAction():
    # Constructor
    # ActionType is an enumeration (AutopilotActionType)
    # actionArguments are specific to each type of action
    def __init__(self, actionType, actionArguments:dict, priority=0):
        self.actionType = actionType
        self.args = actionArguments
        self.priority = priority       # Priority of this action (higher priority actions will be executed first)
    
    # String representation
    def __str__(self):
        return "AutopilotAction: " + str(self.actionType) + " (args: " + str(self.args) + ")"


# Specific action types
class AutopilotAction_GotoXY(AutopilotAction):
    # Constructor
    def __init__(self, x, y, priority=2):
        self.actionType = AutopilotActionType.GOTO_XY
        self.args['destinationX'] = x
        self.args['destinationY'] = y
        self.priority = priority

class AutopilotAction_PickupObj(AutopilotAction):
    # Constructor
    def __init__(self, objectToPickUp, priority=4):
        self.actionType = AutopilotActionType.PICKUP_OBJ
        self.args['objectToPickUp'] = objectToPickUp
        self.priority = priority

class AutopilotAction_PlaceObjInContainer(AutopilotAction):
    # Constructor
    def __init__(self, objectToPlace, container, priority=3):
        self.actionType = AutopilotActionType.PLACE_OBJ_IN_CONTAINER
        self.args['objectToPlace'] = objectToPlace
        self.args['container'] = container
        self.priority = priority

class AutopilotAction_Wander(AutopilotAction):
    # Constructor
    def __init__(self, priority=1):
        self.actionType = AutopilotActionType.WANDER
        self.priority = priority

class AutopilotAction_Wait(AutopilotAction):
    # Constructor
    def __init__(self, priority=0):
        self.actionType = AutopilotActionType.WAIT
        self.priority = priority


# Enumeration for types of autopilot actions
class AutopilotActionType(Enum):
    GOTO_XY                 = 0
    PICKUP_OBJ              = 1
    PLACE_OBJ_IN_CONTAINER  = 2
    WANDER                  = 3
    WAIT                    = 4
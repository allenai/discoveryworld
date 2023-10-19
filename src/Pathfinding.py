# Pathfinding.py

from Layer import Layer
from ActionSuccess import *
from enum import Enum, unique

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder



class Pathfinder():
    # Constructor
    def __init__(self):
        pass

    # Find a path
    # Returns the next step to take on the path, as well as the total length of the path.
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
            return (True, nextX, nextY, len(path))
        else:
            return (False, -1, -1, -1)
        
        
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
    def actionInterpreter(self, autopilotAction, agent, world):
        # First, figure out which type of action we're running
        actionType = autopilotAction.actionType
        # Then, run the appropriate function
        if (actionType == AutopilotActionType.GOTO_XY):
            return self.runGotoXY(autopilotAction.args, agent, world)
        elif (actionType == AutopilotActionType.PICKUP_OBJ):
            return self.runPickupObj(autopilotAction.args, agent, world)
        elif (actionType == AutopilotActionType.PLACE_OBJ_IN_CONTAINER):
            return self.runPlaceObjInContainer(autopilotAction.args, agent, world)
        elif (actionType == AutopilotActionType.WANDER):
            return self.runWander(autopilotAction.args, agent, world)
        elif (actionType == AutopilotActionType.WAIT):
            return self.runWait(autopilotAction.args, agent, world)
        else:
            print("ERROR: Invalid autopilot action type: " + str(actionType))
            return ActionResult.INVALID
    

    def runGotoXY(self, args:dict, agent, world):
        # First, check if we're already at the destination
        agentLocation = agent.getWorldLocation()
        if (agentLocation[0] == args['destinationX']) and (agentLocation[1] == args['destinationY']):
            # We're already there
            return ActionResult.COMPLETED

        # Otherwise, find the next step in the path
        result = self._doNPCAutonavigation(agent, world, args['destinationX'], args['destinationY'], besideIsOK=True)
        print("runGotoXY: _doNPCAutonavigation returned: " + str(result))

        return result
        

    def runPickupObj(self, args:dict, agent, world):
        # First, get the object's world location
        objectToPickUp = args['objectToPickUp']
        objLocation = objectToPickUp.getWorldLocation()

        # Check if we are directly left, right, up, or down from the object
        agentLocation = agent.getWorldLocation()
        isBeside, besideDir = self._isAgentDirectlyAdjacentToDestination(agentLocation[0], agentLocation[1], objLocation[0], objLocation[1])

        if (isBeside):
            print("runPickupObj: We are beside the object (it is to our " + str(besideDir) + ")")

            # We're directly beside the object.  Is the agent facing the object?
            if (agent.attributes["faceDirection"] != besideDir):
                # We're not facing the object.  Rotate.
                print("runPickupObj: We're not facing the object.  Rotating to face it.")
                success = agent.rotateToFaceDirection(besideDir)
                return ActionResult.SUCCESS
            else:
                # We're facing the object.  Check to see if we can pick it up (i.e. if it's accessible, or in a closed container)
                print("runPickupObj: We're facing the object.  Checking if we can pick it up.")
                objectContainerIfClosed = objectToPickUp.getOutermostClosedContainer()
                if (objectContainerIfClosed != None):
                    # The object is in a closed container.  Open the container.
                    print("runPickupObj: The object is in a closed container (" + objectContainerIfClosed.name + ").  Opening the container.")
                    success = agent.actionOpenContainer(objectContainerIfClosed)
                    print("runPickupObj: actionOpenContainer returned: " + str(success))
                    return ActionResult.SUCCESS

                # If we reach here, the object is accessible and we can pick it up.  Pick it up.
                success = agent.actionPickUp(objectToPickUp)
                
                # TODO: Check for success
                return ActionResult.COMPLETED

        else:
            # We're not close enough to pick up the object. Navigate to it.
            result = self._doNPCAutonavigation(agent, world, objLocation[0], objLocation[1], besideIsOK=True)
            print("runPickupObj: _doNPCAutonavigation returned: " + str(result))

            return result


    def runPlaceObjInContainer(self, args:dict, agent, world):
        # self.args['objectToPlace'] = objectToPlace
        # self.args['container'] = container

        # First, get the container's world location
        objectToPlace = args['objectToPlace']
        container = args['container']
        containerLocation = container.getWorldLocation()

        # TODO: Check if we have the object in our inventory.  If not, something unexpected has happened, so return an error.

        # Check if we are directly left, right, up, or down from the container
        agentLocation = agent.getWorldLocation()
        isBeside, besideDir = self._isAgentDirectlyAdjacentToDestination(agentLocation[0], agentLocation[1], containerLocation[0], containerLocation[1])

        if (isBeside):
            print("runPlaceObjInContainer: We are beside the container (it is to our " + str(besideDir) + ")")

            # We're directly beside the object.  Is the agent facing the object?
            if (agent.attributes["faceDirection"] != besideDir):
                # We're not facing the object.  Rotate.
                print("runPlaceObjInContainer: We're not facing the container.  Rotating to face it.")
                success = agent.rotateToFaceDirection(besideDir)
                return ActionResult.SUCCESS
            else:
                # We're facing the container.  If it needs to be opened, open it.
                print("runPlaceObjInContainer: We're facing the container.  Checking if we need to open it.")
                objectContainerIfClosed = container.getOutermostClosedContainer(includeSelf=True)
                if (objectContainerIfClosed != None):
                    # The object is in a closed container.  Open the container.
                    print("runPlaceObjInContainer: The following container is closed and needs to be opened (" + objectContainerIfClosed.name + ").  Opening the container.")
                    success = agent.actionOpenContainer(objectContainerIfClosed)
                    print("runPlaceObjInContainer: actionOpenContainer returned: " + str(success))
                    return ActionResult.SUCCESS

                # If we reach here, the object is accessible and we can put it in/on the container.  Move it to the container.
                print("runPlaceObjInContainer: Putting object (" + objectToPlace.name + ") in container (" + container.name + ")")
                success = agent.actionPut(objToPut=objectToPlace, newContainer=container)
                print("runPlaceObjInContainer: actionPut returned: " + str(success))
                
                # TODO: Check for success
                return ActionResult.COMPLETED

        else:
            # We're not close enough to pick up the object. Navigate to it.
            result = self._doNPCAutonavigation(agent, world, containerLocation[0], containerLocation[1], besideIsOK=True)
            print("runPlaceObjInContainer: _doNPCAutonavigation returned: " + str(result))

            return result


    def runWander(self, args:dict, agent, world):
        pass

    def runWait(self, args:dict, agent, world):
        pass

        

    #
    #   Helper functions
    #

    #
    #   NPC Auto-navigation
    #   
    #  This function is used by the NPC to automatically navigate to a given location.
    #  Arguments:
    #   - agent: The agent that is navigating
    #   - world: The world object
    #   - destinationX: The X coordinate of the destination
    #   - destinationY: The Y coordinate of the destination
    #   - besideIsOK: If the agent can't reach the destination, is it OK to reach a location directly N/E/S/W from it?
    def _doNPCAutonavigation(self, agent, world, destinationX, destinationY, besideIsOK=False):

        pathSuccess, nextX, nextY, pathLength = self.findPathNextStep(world, agent.attributes["gridX"], agent.attributes["gridY"], destinationX, destinationY)
        # Back-off strategy: If 'besideIsOK=True', try to find a path to a location directly N/E/S/W from the destination
        if (not pathSuccess) and besideIsOK:
            pathLength = 999999
            # North
            _pathSuccess, _nextX, _nextY, _pathLength = self.findPathNextStep(world, agent.attributes["gridX"], agent.attributes["gridY"], destinationX, destinationY-1)
            if (_pathSuccess) and (_pathLength < pathLength):
                pathSuccess = _pathSuccess
                nextX = _nextX
                nextY = _nextY
                pathLength = _pathLength

            # East
            _pathSuccess, _nextX, _nextY, _pathLength = self.findPathNextStep(world, agent.attributes["gridX"], agent.attributes["gridY"], destinationX+1, destinationY)
            if (_pathSuccess) and (_pathLength < pathLength):
                pathSuccess = _pathSuccess
                nextX = _nextX
                nextY = _nextY
                pathLength = _pathLength
            
            # South
            _pathSuccess, _nextX, _nextY, _pathLength = self.findPathNextStep(world, agent.attributes["gridX"], agent.attributes["gridY"], destinationX, destinationY+1)
            if (_pathSuccess) and (_pathLength < pathLength):
                pathSuccess = _pathSuccess
                nextX = _nextX
                nextY = _nextY
                pathLength = _pathLength

            # West
            _pathSuccess, _nextX, _nextY, _pathLength = self.findPathNextStep(world, agent.attributes["gridX"], agent.attributes["gridY"], destinationX-1, destinationY)
            if (_pathSuccess) and (_pathLength < pathLength):
                pathSuccess = _pathSuccess
                nextX = _nextX
                nextY = _nextY
                pathLength = _pathLength

        
        if (not pathSuccess):
            print("_doNPCAutonavigation: No path found to goal location.  Exiting. (agent: " + agent.name + ")")
            return ActionResult.FAILURE

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
                return ActionResult.SUCCESS

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

        return ActionResult.SUCCESS

    # Check to see if the agent is directly north, east, south, or west from the destination
    # Returns (True, "north"/"east"/"south"/"west") if the agent is directly adjacent to the destination
    # Returns (False, None) if the agent is not directly adjacent to the destination
    def _isAgentDirectlyAdjacentToDestination(self, queryX, queryY, destinationX, destinationY):
        # Check north
        if (queryX == destinationX) and (queryY == destinationY + 1):
            return (True, "north")
        # Check east
        if (queryX == destinationX + 1) and (queryY == destinationY):
            return (True, "east")
        # Check south
        if (queryX == destinationX) and (queryY == destinationY - 1):
            return (True, "south")
        # Check west
        if (queryX == destinationX - 1) and (queryY == destinationY):
            return (True, "west")

        # Default return
        return (False, None)




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
        return "AutopilotAction: " + str(self.actionType) + " (args: " + str(self.args) + ", priority: " + str(self.priority) + ")"


# Specific action types
class AutopilotAction_GotoXY(AutopilotAction):
    # Constructor
    def __init__(self, x, y, priority=2):
        self.actionType = AutopilotActionType.GOTO_XY
        self.args = {}
        self.args['destinationX'] = x
        self.args['destinationY'] = y
        self.priority = priority

class AutopilotAction_PickupObj(AutopilotAction):
    # Constructor
    def __init__(self, objectToPickUp, priority=4):
        self.actionType = AutopilotActionType.PICKUP_OBJ
        self.args = {}
        self.args['objectToPickUp'] = objectToPickUp
        self.priority = priority

class AutopilotAction_PlaceObjInContainer(AutopilotAction):
    # Constructor
    def __init__(self, objectToPlace, container, priority=3):
        self.actionType = AutopilotActionType.PLACE_OBJ_IN_CONTAINER
        self.args = {}
        self.args['objectToPlace'] = objectToPlace
        self.args['container'] = container
        self.priority = priority

class AutopilotAction_Wander(AutopilotAction):
    # Constructor
    def __init__(self, priority=1):
        self.actionType = AutopilotActionType.WANDER
        self.args = {}
        self.priority = priority

class AutopilotAction_Wait(AutopilotAction):
    # Constructor
    def __init__(self, priority=0):
        self.actionType = AutopilotActionType.WAIT
        self.args = {}
        self.priority = priority


# Enumeration for types of autopilot actions
class AutopilotActionType(Enum):
    GOTO_XY                 = 0
    PICKUP_OBJ              = 1
    PLACE_OBJ_IN_CONTAINER  = 2
    WANDER                  = 3
    WAIT                    = 4


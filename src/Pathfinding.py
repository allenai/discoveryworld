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
            result = self.runGotoXY(autopilotAction.args, agent, world)
        elif (actionType == AutopilotActionType.PICKUP_OBJ):
            result = self.runPickupObj(autopilotAction.args, agent, world)
        elif (actionType == AutopilotActionType.PLACE_OBJ_IN_CONTAINER):
            result = self.runPlaceObjInContainer(autopilotAction.args, agent, world)
        elif (actionType == AutopilotActionType.FIND_OBJS_AREA_PLACE):
            result = self.runFindObjsInAreaThenPlace(autopilotAction, autopilotAction.args, agent, world)
        elif (actionType == AutopilotActionType.WANDER):
            result = self.runWander(autopilotAction.args, agent, world)
        elif (actionType == AutopilotActionType.WAIT):
            result = self.runWait(autopilotAction.args, agent, world)
        elif (actionType == AutopilotActionType.EAT_OBJ_IN_INVENTORY):
            result = self.runEat(autopilotAction.args, agent, world)
        else:
            print("ERROR: Invalid autopilot action type: " + str(actionType))
            return ActionResult.INVALID

        # Check if there's a callback in the args
        if ("callback" in autopilotAction.args) and (autopilotAction.args["callback"] != None):
            # Run the callback
            print("Running callback")            
            # Append 'result' to existing parameters in callback
            callbackArgs = []
            if ("callbackArgs" in autopilotAction.args):
                # Copy existing params
                callbackArgs = autopilotAction.args["callbackArgs"]
            # Append result
            callbackArgs.append(result)
            # Run callback
            autopilotAction.args["callback"](callbackArgs)                                    
        
        return result

    

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
        

    # Eat an object in the agent's inventory
    def runEat(self, args:dict, agent, world):
        # First, check that the object to eat is in the agent's inventory
        objectNamesOrTypesToEat = args['objectNamesOrTypesToEat']

        # Check if an object with an appropriate name/type is in the agent's inventory
        agentInventory = agent.getAllContainedObjectsRecursive(respectContainerStatus=True)
        objectToEat = None        
        for invObj in agentInventory:
            # Check if this object matches the name or type
            if (invObj.name in objectNamesOrTypesToEat) or (invObj.objectType in objectNamesOrTypesToEat):
                # Found the object
                objectToEat = invObj
                break

        if (objectToEat == None):
            # Object meeting name/type requirements not found in inventory.
            print("runEat: Object with that name or type (" + objectNamesOrTypesToEat.name + " not found in agent's inventory.")
            return ActionResult.FAILURE

        # Perform the action
        result = agent.actionEat(objectToEat)

        # Check the result
        if (result.success == False):
            # Action failed
            print("runEat: Action failed (" + result.message + ")")
            return ActionResult.FAILURE

        # Action succeeded
        return ActionResult.COMPLETED
     

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
            if (agent.attributes["faceDirection"] != besideDir) and (besideDir != "identical"):
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


    # Helper: Find the first object meeting a given type within a specified area
    def _findFirstObjectOfType(self, args:dict, agent, world):
        startX = args['x']
        startY = args['y']
        endX = args['x'] + args['width']
        endY = args['y'] + args['height']
        objectTypes = args['objectTypes']

        excludeObjectsOnAgent = args['excludeObjectsOnAgent']

        agentInventory = []
        if (excludeObjectsOnAgent):
            agentInventory = agent.getAllContainedObjectsRecursive(respectContainerStatus=False)

        for tileX in range(startX, endX):
            for tileY in range(startY, endY):
                objectsAtTile = world.getObjectsAt(tileX, tileY, respectContainerStatus=True)
                for obj in objectsAtTile:
                    if (obj.type in objectTypes):
                        # We found an object that matches one of the types we're looking for.  Place it in the container.
                        # But, first check that the object isn't in the agents inventory (if we're supposed to exclude objects on the agent)
                        if (excludeObjectsOnAgent):
                            if (obj not in agentInventory):
                                return obj
                        else:
                            return obj
        
        # If we reach here, we didn't find any objects of the specified type
        return None
                


    def runFindObjsInAreaThenPlace(self, originalAction, args:dict, agent, world):
        # Step 1: Find if there's an object in the area that matches the object type(s) we're looking for (if not, we're done)
        nextObj = self._findFirstObjectOfType(args, agent, world)

        print("##### runFindObjsInAreaThenPlace: Found object: " + str(nextObj))
        # If there are no objects to find, we're done
        if (nextObj == None):            
            return ActionResult.COMPLETED

        #self.args['maxToTake'] = maxToTake                              # The maximum number of objects meeting the criteria to take
        #self.args['numTaken'] = 0
        # If the 'maxToTake' parameter is set (i.e. > 0), and we've already taken that many objects, we're done
        if ('maxToTake' in args):
            print("###### runFindObjsInAreaThenPlace: Already taken " + str(args['numTaken']) + " objects, and maxToTake is " + str(args['maxToTake']) + ".  Checking if we're done.")
            if (args['maxToTake'] > 0):
                if ('numTaken' in args):
                    if (args['numTaken'] >= args['maxToTake']):
                        print("###### runFindObjsInAreaThenPlace: Already taken " + str(args['numTaken']) + " objects, and maxToTake is " + str(args['maxToTake']) + ".  Action completed.")
                        return ActionResult.COMPLETED

        # Step 2: If we reach here, we found an object -- place it in the container        
        container = args['container']
        priority = args['priority']

        # Pop on a 'placeObjInContainer' action, with a higher priority
        thingToPickup = nextObj
        whereToPlace = container
        actionPick = AutopilotAction_PickupObj(thingToPickup, priority=priority+1)
        #actionPlace = AutopilotAction_PlaceObjInContainer(thingToPickup, whereToPlace, priority=priority+1)        
        # Provide a callback to PickupObj that increments the 'numTaken' parameter
        def callbackPickupObj(callbackArgs):
            action = callbackArgs[0]
            result = callbackArgs[1]
            if (result == ActionResult.COMPLETED):                
                if ('numTaken' in action.args):
                    action.args['numTaken'] += 1
                else:
                    action.args['numTaken'] = 1
                
                print("##### runFindObjsInAreaThenPlace: CALLBACK Incremented numTaken to " + str(action.args['numTaken']))

        #actionPlace = AutopilotAction_PlaceObjInContainer(thingToPickup, whereToPlace, priority=priority+1, callback=callbackPickupObj(self))
        # Above doesn't work because the callback is called with an additional 'result' parameter, which is the result of the action that just completed.
        # e.g. autopilotAction.args["callback"](result)
        # Instead, we'll change the call to this:
        actionPlace = AutopilotAction_PlaceObjInContainer(thingToPickup, whereToPlace, priority=priority+1, callback=callbackPickupObj, callbackArgs=[originalAction])
            

        agent.addAutopilotActionToQueue( actionPick )
        agent.addAutopilotActionToQueue( actionPlace )
        print("##### Added action to queue " + str(actionPick) )
        print("##### Added action to queue " + str(actionPlace) )
        # Suspend the current action, so the 'placeObjInContainer' action can run
        return ActionResult.SUSPEND





    def runPlaceObjInContainer(self, args:dict, agent, world):
        # self.args['objectToPlace'] = objectToPlace
        # self.args['container'] = container

        # First, get the container's world location
        objectToPlace = args['objectToPlace']
        container = args['container']
        containerLocation = container.getWorldLocation()

        # Check if we have the object in our inventory.  If not, something unexpected has happened, so return an error.
        agentInventory = agent.getAllContainedObjectsRecursive(respectContainerStatus=True)        
        # TODO: Handle case where the object is in a closed container, and we need to open the container to get it
        if (objectToPlace not in agentInventory):
            print("runPlaceObjInContainer: ERROR: I can't seem to find the object I need to place (" + objectToPlace.name + ") in the agent inventory. Stopping place action.")
            return ActionResult.ERROR


        # Check if we are directly left, right, up, or down from the container
        agentLocation = agent.getWorldLocation()
        isBeside, besideDir = self._isAgentDirectlyAdjacentToDestination(agentLocation[0], agentLocation[1], containerLocation[0], containerLocation[1])
        print ("## runPlaceObjInContainer: Agent is at (" + str(agentLocation[0]) + ", " + str(agentLocation[1]) + ")")
        print ("## runPlaceObjInContainer: Container is at (" + str(containerLocation[0]) + ", " + str(containerLocation[1]) + ")")

        if (isBeside):
            print("runPlaceObjInContainer: We are beside the container (it is to our " + str(besideDir) + ")")

            # We're directly beside the object.  Is the agent facing the object?
            if (agent.attributes["faceDirection"] != besideDir) and (besideDir != "identical"):
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
        # Check to see if the locations are identical
        if (queryX == destinationX) and (queryY == destinationY):
            return (True, "identical")

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
        self.args['priority'] = priority      # Priority of this action (higher priority actions will be executed first)
    
    # Priority property getter
    @property
    def priority(self):
        return self.args.get('priority', 0)
    
    # Priority property setter
    @priority.setter
    def priority(self, value):
        self.args['priority'] = value

    # Timestamp
    @property
    def timestamp(self):
        return self.args.get('timestamp', 0)

    # Timestamp property setter
    @timestamp.setter
    def timestamp(self, value):
        self.args['timestamp'] = value

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
        self.args['priority'] = priority                

class AutopilotAction_PickupObj(AutopilotAction):
    # Constructor
    def __init__(self, objectToPickUp, callback=None, callbackArgs=None, priority=4):
        self.actionType = AutopilotActionType.PICKUP_OBJ
        self.args = {}
        self.args['objectToPickUp'] = objectToPickUp
        self.args['priority'] = priority                
        self.args['callback'] = callback
        self.args['callbackArgs'] = callbackArgs

class AutopilotAction_PlaceObjInContainer(AutopilotAction):
    # Constructor
    def __init__(self, objectToPlace, container, callback=None, callbackArgs=None, priority=3):
        self.actionType = AutopilotActionType.PLACE_OBJ_IN_CONTAINER
        self.args = {}
        self.args['objectToPlace'] = objectToPlace
        self.args['container'] = container
        self.args['priority'] = priority
        self.args['callback'] = callback            
        self.args['callbackArgs'] = callbackArgs

class AutopilotAction_PickupObjectsInArea(AutopilotAction):
    # Constructor
    def __init__(self, x, y, width, height, objectTypes:list, container, excludeObjectsOnAgent=True, maxToTake=-1, priority=4):
        self.actionType = AutopilotActionType.FIND_OBJS_AREA_PLACE
        self.args = {}
        self.args['x'] = x
        self.args['y'] = y
        self.args['width'] = width
        self.args['height'] = height
        self.args['objectTypes'] = objectTypes
        self.args['container'] = container
        self.args['excludeObjectsOnAgent'] = excludeObjectsOnAgent      # If True, will not look for objects on the agent if/when the agent is in the area
        self.args['maxToTake'] = maxToTake                              # The maximum number of objects meeting the criteria to take
        self.args['numTaken'] = 0
        self.args['priority'] = priority                


class AutopilotAction_EatObjectInInventory(AutopilotAction):
    # Constructor
    def __init__(self, objectNamesOrTypesToEat, callback=None, callbackArgs=None, priority=3):
        self.actionType = AutopilotActionType.EAT_OBJ_IN_INVENTORY
        self.args = {}
        self.args['objectNamesOrTypesToEat'] = objectNamesOrTypesToEat        
        self.args['priority'] = priority
        self.args['callback'] = callback            
        self.args['callbackArgs'] = callbackArgs

class AutopilotAction_Wander(AutopilotAction):
    # Constructor
    def __init__(self, priority=1):
        self.actionType = AutopilotActionType.WANDER
        self.args = {}
        self.args['priority'] = priority                

class AutopilotAction_Wait(AutopilotAction):
    # Constructor
    def __init__(self, priority=0):
        self.actionType = AutopilotActionType.WAIT
        self.args = {}
        self.args['priority'] = priority                


# Enumeration for types of autopilot actions
class AutopilotActionType(Enum):
    GOTO_XY                 = 0
    PICKUP_OBJ              = 1
    PLACE_OBJ_IN_CONTAINER  = 2
    WANDER                  = 3
    WAIT                    = 4
    FIND_OBJS_AREA_PLACE    = 5
    EAT_OBJ_IN_INVENTORY    = 6


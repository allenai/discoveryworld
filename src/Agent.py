# Agent.py

import SpriteLibrary
import random
from ObjectModel import *
from Layer import * 
from ActionSuccess import *
from Pathfinding import *
from ActionHistory import *
from KnowledgeScorer import KnowledgeScorer

import time

#
#   Agent (controlled by a user or model)
#
class Agent(Object):
    # Constructor
    def __init__(self, world, objectType="agent", objectName="agent", defaultSpriteName="character18_agent_facing_south"):
        # Default sprite name
        Object.__init__(self, world, objectType, objectName, defaultSpriteName = "character18_agent_facing_south")
    
        # Rendering
        self.attributes["faceDirection"] = "south"        
        self.spriteCharacterPrefix = "character18_"                 # Prefix for the sprite character name (e.g. "character18_")

        # Agent action history
        self.actionHistory = ActionHistory(self.world)

        # Agent knowledge scorer
        self.knowledgeScorer = KnowledgeScorer(self.world)

        # Autopilot action queue and pathfinder
        self.autopilotActionQueue = []                              # Queue of autopilot actions        
        self.pathfinder = Pathfinder()
        self.actionTimestampCounter = 0                             # Counter for the timestamp of the last action

        # Default attributes
        self.attributes["isMovable"] = False                       # Can it be moved?

        # Agent is a container for its inventory
        # Container attributes
        self.attributes['isContainer'] = True                      # Is it a container?
        self.attributes['isOpenable'] = False                      # Can be opened
        self.attributes['isOpenContainer'] = True                 # If it's a container, then is it open?
        self.attributes['containerPrefix'] = "in"                  # Container prefix (e.g. "in" or "on")            
        self.attributes['contentsVisible2D'] = False               # If it is a container, do we render the contents in the 2D representation, or is that already handled (e.g. for pots/jars, that render generic contents if they contain any objects)

        # Dialog attributes
        self.attributes['isDialogable'] = True                     # Can it be dialoged with?
        self.attributes['inDialogWith'] = None                     # Who is it in dialog with at this current moment?
        self.dialogTree = None                                     # Dialog tree for this agent

        # Door opening/closing for NPCs
        self.attributes["doorNeedsToBeClosed"] = None              # Whether a door was recently opened that needs to be closed
        self.attributes["movesSinceDoorOpen"] = 0                  # How many moves have happened since the door was opened

        # Signals (largely for NPCs)
        self.attributes["states"] = set()                          # External signals that the agent has received

        # Health attributes
        self.attributes["poisonedCounter"] = -1                    # Poisoned counter (if >= 0, then the agent is poisoned)
        self.attributes['isPoisoned'] = False                      # Is the agent currently poisoned?

        # Object visibility for agents (i.e. the last object(s) they interacted with)
        self.attributes["objectToShow"] = None                     # The object to show the agent carrying
        
        # Alive/dead
        self.attributes["isLiving"] = True                          # Is the agent alive?

    #   
    #   Accessors/helpers
    #
    
    # Get the grid location (x, y) that the agent is facing
    def getWorldLocationAgentIsFacing(self):
        # Get the current location
        x = self.attributes["gridX"]
        y = self.attributes["gridY"]

        # Get the direction the agent is facing
        faceDirection = self.attributes["faceDirection"]

        # Get the new location
        if (faceDirection == "north"):
            y -= 1
        elif (faceDirection == "south"):
            y += 1
        elif (faceDirection == "east"):
            x += 1
        elif (faceDirection == "west"):
            x -= 1

        # Return the new location
        return (x, y)

    #
    #   States
    #

    # Add a state to this agent
    def addState(self, stateName):
        self.attributes['states'].add(stateName)

    # Savely remov a state (fails gracefully if the state doesn't exist)    
    def removeState(self, stateName):
        if (stateName in self.attributes['states']):
            self.attributes['states'].remove(stateName)
            return True
        else:
            return False

    # 
    #   Get inventory    
    #

    # Helper to get inventory
    def getInventory(self):
        return self.getAllContainedObjectsRecursive(respectContainerStatus=True)

    # Get all objects in the world tile that the agent is facing
    def getObjectsAgentFacing(self, respectContainerStatus=True):
        # Find a usable item at the location the agent is facing
        facingLocation = self.getWorldLocationAgentIsFacing()
        # Bound checking
        if (self.world.isWithinBounds(facingLocation[0], facingLocation[1]) == False):
            return []

        # Get objects at location
        objs = self.world.getObjectsAt(facingLocation[0], facingLocation[1], respectContainerStatus=respectContainerStatus)                    

        # Return the objects
        return objs


    #
    #   Tick
    #
        
    # Tick
    def tick(self):
        print("")
        # # Randomly move agent
        # if (random.random() < 0.1):
        #     # Randomly move the agent
        #     deltaX = random.randint(-1, 1)
        #     deltaY = random.randint(-1, 1)
        #     self.actionMoveAgent(deltaX, deltaY)

        # Call superclass
        Object.tick(self)

        # Check if the agent is poisoned
        POISON_DURATION = 100
        POISON_INCUBATION_PERIOD = 50
        if (self.attributes['poisonedCounter'] != -1):
            # Decrement the poisoned counter
            self.attributes['poisonedCounter'] -= 1

            # Poisoning is initially silent, and only starts to affect the agent when the poisonedCounter reaches -50. 
            if (self.attributes['poisonedCounter'] < -POISON_INCUBATION_PERIOD):
                self.attributes['poisonedCounter'] = POISON_DURATION     # Duration of poison
                self.attributes['isPoisoned'] = True
                self.actionDiscoveryFeedMakeUpdatePost("I'm not feeling well.", signals=[])

            elif (self.attributes['poisonedCounter'] > -1):
                # Poisoned and actively affecting the agent
                self.addState('poisoned')
                print("Agent " + self.name + ": I don't feel very well!")
        else:
            # Remove state of 'poisoned' from the agent
            if ('poisoned' in self.attributes['states']):
                self.removeState('poisoned')
            if (self.attributes['isPoisoned'] == True):
                self.actionDiscoveryFeedMakeUpdatePost("I'm feeling better.", signals=[])
                self.attributes['isPoisoned'] = False
            



    #
    #   Actions
    #

    # Attempt to move the agent in a particular direction.  deltaX and deltaY are in world coordinates, and should nominally be (-1, 0, 1)
    # TODO: DEPRECATED
    # def actionMoveAgent(self, deltaX:int, deltaY:int):
    #     # Get the current location
    #     newX = self.attributes["gridX"] + deltaX
    #     newY = self.attributes["gridY"] + deltaY

    #     # Update the last direction the agent was facing (we do this even if the move wasn't valid, to give some visual feedback to the user)
    #     if (deltaX < 0):
    #         self.attributes["faceDirection"] = "west"
    #     elif (deltaX > 0):
    #         self.attributes["faceDirection"] = "east"
    #     elif (deltaY < 0):
    #         self.attributes["faceDirection"] = "north"
    #     elif (deltaY > 0):
    #         self.attributes["faceDirection"] = "south"
    #     else:
    #         # This should generally not happen -- the agent is not moving.  Still, default to south.
    #         self.attributes["faceDirection"] = "south"

    #     # Invalidate the sprite name
    #     self.needsSpriteNameUpdate = True

    #     # Check if the new location is valid
    #     # Check 1: Is the new location within the bounds of the world?        
    #     if (newX < 0 or newX >= self.world.sizeX or newY < 0 or newY >= self.world.sizeY):
    #         # Invalid location
    #         return ActionSuccess(False, "That would take me beyond the edge of the world.")

    #     # Check 2: Check if the new location is passable
    #     isPassable, blockingObject = self.world.isPassable(newX, newY)
    #     if (not isPassable):            
    #         return ActionSuccess(False, "I can't move there. There is something in the way (" + blockingObject.name + ").")

    #     # If we reach here, the new location is valid. Update the agent's location to the new location
    #     self.world.removeObject(self)                           # First, remove the object from it's current location in the world grid
    #     self.world.addObject(newX, newY, Layer.AGENT, self)     # Then, add the object to the new location in the world grid

    #     return ActionSuccess(True, "I moved to (" + str(newX) + ", " + str(newY) + ").")

    # Rotate the direction the agent is facing
    # Direction: +1 = clockwise, -1 = counterclockwise
    def actionRotateAgentFacingDirection(self, direction=+1):
        # Get the current direction
        currentDirection = self.attributes["faceDirection"]

        # Get the new direction
        if (direction == +1):
            if (currentDirection == "north"):
                newDirection = "east"
            elif (currentDirection == "east"):
                newDirection = "south"
            elif (currentDirection == "south"):
                newDirection = "west"
            elif (currentDirection == "west"):
                newDirection = "north"
        elif (direction == -1):
            if (currentDirection == "north"):
                newDirection = "west"
            elif (currentDirection == "east"):
                newDirection = "north"
            elif (currentDirection == "south"):
                newDirection = "east"
            elif (currentDirection == "west"):
                newDirection = "south"

        # Update the direction
        self.attributes["faceDirection"] = newDirection

        # Invalidate the sprite name
        self.needsSpriteNameUpdate = True

        # Result
        result = ActionSuccess(True, "I rotated to face " + newDirection + ".")
        actionType = ActionType.ROTATE_CW if (direction == +1) else ActionType.ROTATE_CCW
        self.actionHistory.add(actionType=actionType, arg1=None, arg2=None, result=result)
        return result

    # Move forward (or backward) in the direction the agent is facing
    # Direction: +1 = forward, -1 = backward
    def actionMoveAgentForwardBackward(self, direction=+1):
        actionType = ActionType.MOVE_FORWARD if (direction == +1) else ActionType.MOVE_BACKWARD
        # Get the current direction
        currentDirection = self.attributes["faceDirection"]        

        # Get the new location
        if (direction == +1):
            if (currentDirection == "north"):
                newX = self.attributes["gridX"]
                newY = self.attributes["gridY"] - 1
            elif (currentDirection == "east"):
                newX = self.attributes["gridX"] + 1
                newY = self.attributes["gridY"]
            elif (currentDirection == "south"):
                newX = self.attributes["gridX"]
                newY = self.attributes["gridY"] + 1
            elif (currentDirection == "west"):
                newX = self.attributes["gridX"] - 1
                newY = self.attributes["gridY"]
        elif (direction == -1):
            if (currentDirection == "north"):
                newX = self.attributes["gridX"]
                newY = self.attributes["gridY"] + 1
            elif (currentDirection == "east"):
                newX = self.attributes["gridX"] - 1
                newY = self.attributes["gridY"]
            elif (currentDirection == "south"):
                newX = self.attributes["gridX"]
                newY = self.attributes["gridY"] - 1
            elif (currentDirection == "west"):
                newX = self.attributes["gridX"] + 1
                newY = self.attributes["gridY"]
        
        # Check if the new location is valid
        # Check 1: Is the new location within the bounds of the world?
        if (newX < 0 or newX >= self.world.sizeX or newY < 0 or newY >= self.world.sizeY):
            # Invalid location
            result = ActionSuccess(False, "That would take me beyond the edge of the world.")
            self.actionHistory.add(actionType=actionType, arg1=None, arg2=None, result=result)
            return result
        
        # Check 2: Check if the new location is passable
        isPassable, blockingObject = self.world.isPassable(newX, newY)
        if (not isPassable):
            result = ActionSuccess(False, "I can't move there. There is something in the way (" + blockingObject.name + ").")
            self.actionHistory.add(actionType=actionType, arg1=None, arg2=None, result=result)
            return result


        # If we reach here, the new location is valid. Update the agent's location to the new location
        self.world.removeObject(self)                           # First, remove the object from it's current location in the world grid
        self.world.addObject(newX, newY, Layer.AGENT, self)     # Then, add the object to the new location in the world grid

        # Invalidate sprite name
        self.needsSpriteNameUpdate = True

        result = ActionSuccess(True, "I moved to (" + str(newX) + ", " + str(newY) + ").")
        self.actionHistory.add(actionType=actionType, arg1=None, arg2=None, result=result)
        return result




    # Pick up an object, and add it to the agent's inventory
    def actionPickUp(self, objToPickUp):
        # First, check if the object is movable
        if (not objToPickUp.attributes["isMovable"]):
            # Object is not movable
            result = ActionSuccess(False, "That object (" + objToPickUp.name + ") is not movable.")
            self.actionHistory.add(actionType=ActionType.PICKUP, arg1=objToPickUp, arg2=None, result=result)
            return result

        # Next, check if the object is within reach (i.e. +/- 1 grid location)
        distX = abs(objToPickUp.attributes["gridX"] - self.attributes["gridX"])
        distY = abs(objToPickUp.attributes["gridY"] - self.attributes["gridY"])
        if (distX > 1 or distY > 1):
            # Object is not within reach
            result = ActionSuccess(False, "That object (" + objToPickUp.name + ") is not within reach. I can only pick up objects that are within +/- 1 grid location.")            
            self.actionHistory.add(actionType=ActionType.PICKUP, arg1=objToPickUp, arg2=None, result=result)
            return result

        # If we reach here, the object is movable and within reach.  Pick it up.
        objToPickUp.invalidateSpritesThisWorldTile()            # Invalidate the sprites at the object's current location
        self.world.removeObject(objToPickUp)                    # Remove the object from the world
        self.addObject(objToPickUp)                             # Add the object to the agent's inventory

        # Update to show the agent holding the object it just picked up
        self.updateLastInteractedObject([objToPickUp])

        result = ActionSuccess(True, "I picked up the " + objToPickUp.name + ".")
        self.actionHistory.add(actionType=ActionType.PICKUP, arg1=objToPickUp, arg2=None, result=result)
        return result



    # Drop an object from the agent's inventory at the agent's current location
    def actionDrop(self, objToDrop):
        # First, check if the object is in the agent's inventory
        objectsInInventory = self.getAllContainedObjectsRecursive(respectContainerStatus=True)
        print("OBJECTS IN INVENTORY: " + str(objectsInInventory))
        if (not objToDrop in objectsInInventory):
            # Object is not in the agent's inventory
            result = ActionSuccess(False, "That object (" + objToDrop.name + ") is not in my inventory.")
            self.actionHistory.add(actionType=ActionType.DROP, arg1=objToDrop, arg2=None, result=result)
            return result

        # Next, drop the object at the agent's current location.
        # (Note: adding the item to a specific location should remove it from the agent's inventory)
        self.world.addObject(self.attributes["gridX"], self.attributes["gridY"], Layer.OBJECTS, objToDrop)

        # Invalidate the sprites at the object's new location
        objToDrop.invalidateSpritesThisWorldTile()

        result = ActionSuccess(True, "I dropped the " + objToDrop.name + ".")
        self.actionHistory.add(actionType=ActionType.DROP, arg1=objToDrop, arg2=None, result=result)
        return result


    def actionPut(self, objToPut, newContainer):
        # First, check if the object is in the agent's inventory
        objectsInInventory = self.getAllContainedObjectsRecursive(respectContainerStatus=True)
        if (not objToPut in objectsInInventory):
            # Object is not in the agent's inventory
            result = ActionSuccess(False, "That object (" + objToPut.name + ") is not in my inventory.")
            self.actionHistory.add(actionType=ActionType.PUT, arg1=objToPut, arg2=newContainer, result=result)
            return result

        # Next, check if the new container is within reach (i.e. +/- 1 grid location)
        distX = abs(newContainer.attributes["gridX"] - self.attributes["gridX"])
        distY = abs(newContainer.attributes["gridY"] - self.attributes["gridY"])
        if (distX > 1 or distY > 1):
            # Container is not within reach
            result = ActionSuccess(False, "That container (" + newContainer.name + ") is not within reach. I can only put objects into containers that are within +/- 1 grid location.")
            self.actionHistory.add(actionType=ActionType.PUT, arg1=objToPut, arg2=newContainer, result=result)
            return result

        # Next, check to see if the container is a container
        if (not newContainer.attributes["isContainer"]):
            # Container is not a container            
            result = ActionSuccess(False, "That object (" + newContainer.name + ") is not a container.")
            self.actionHistory.add(actionType=ActionType.PUT, arg1=objToPut, arg2=newContainer, result=result)
            return result

        # Next, check to see if the container is open
        if (not newContainer.attributes["isOpenContainer"]):
            # Container is not open
            result = ActionSuccess(False, "That container (" + newContainer.name + ") is not open.")
            self.actionHistory.add(actionType=ActionType.PUT, arg1=objToPut, arg2=newContainer, result=result)
            return result


        # If we reach here, the object is in the agent's inventory, the container is within reach, and the container is open.
        # Put the object into the container.
        if (objToPut.parentContainer != None):
            objToPut.parentContainer.invalidateSpritesThisWorldTile()
        newContainer.addObject(objToPut)
        objToPut.invalidateSpritesThisWorldTile()
        newContainer.invalidateSpritesThisWorldTile()

        # Update to show the agent holding the container it put something in (if the container is in its inventory)
        self.updateLastInteractedObject([newContainer])

        result = ActionSuccess(True, "I put the " + objToPut.name + " into the " + newContainer.name + ".")
        self.actionHistory.add(actionType=ActionType.PUT, arg1=objToPut, arg2=newContainer, result=result)
        return result


    # Open or close an object
    # 'whichAction' should be "open" or "close"
    def actionOpenClose(self, objToOpenOrClose, whichAction="open"):
        actionType = ActionType.OPEN if whichAction == "open" else ActionType.CLOSE
        # First, check if the object is within reach (i.e. +/- 1 grid location)
        distX = abs(objToOpenOrClose.attributes["gridX"] - self.attributes["gridX"])
        distY = abs(objToOpenOrClose.attributes["gridY"] - self.attributes["gridY"])
        if (distX > 1 or distY > 1):
            # Object is not within reach
            result = ActionSuccess(False, "That object (" + objToOpenOrClose.name + ") is not within reach. I can only open/close objects that are within +/- 1 grid location.")
            self.actionHistory.add(actionType=actionType, arg1=objToOpenOrClose, arg2=None, result=result)
            return result

        # Next, check if the object is openable
        if (not objToOpenOrClose.attributes["isOpenable"]):
            # Object is not openable
            result = ActionSuccess(False, "That object (" + objToOpenOrClose.name + ") is not openable/closeable.")
            self.actionHistory.add(actionType=actionType, arg1=objToOpenOrClose, arg2=None, result=result)
            return result
        
        # Next, check to see whether we're dealing with a container or a passage
        if (objToOpenOrClose.attributes["isContainer"]):
            # Open a container
            # Next, check if the object is already in the desired state
            if (whichAction == "open" and objToOpenOrClose.attributes["isOpenContainer"]):
                # Object is already open
                result = ActionSuccess(False, "That object (" + objToOpenOrClose.name + ") is already open.")
                self.actionHistory.add(actionType=actionType, arg1=objToOpenOrClose, arg2=None, result=result)
                return result

            elif (whichAction == "close" and not objToOpenOrClose.attributes["isOpenContainer"]):
                # Object is already closed
                result = ActionSuccess(False, "That object (" + objToOpenOrClose.name + ") is already closed.")
                self.actionHistory.add(actionType=actionType, arg1=objToOpenOrClose, arg2=None, result=result)
                return result

            # If we reach here, the object is within reach and is openable.  Open/close it.
            if (whichAction == "open"):
                objToOpenOrClose.attributes["isOpenContainer"] = True
                objToOpenOrClose.invalidateSpritesThisWorldTile()
                self.updateLastInteractedObject([objToOpenOrClose])
                result = ActionSuccess(True, "I opened the " + objToOpenOrClose.name + ".")
                self.actionHistory.add(actionType=actionType, arg1=objToOpenOrClose, arg2=None, result=result)
                return result

            else:
                objToOpenOrClose.attributes["isOpenContainer"] = False
                objToOpenOrClose.invalidateSpritesThisWorldTile()
                self.updateLastInteractedObject([objToOpenOrClose])
                result = ActionSuccess(True, "I closed the " + objToOpenOrClose.name + ".")
                self.actionHistory.add(actionType=actionType, arg1=objToOpenOrClose, arg2=None, result=result)
                return result


        elif (objToOpenOrClose.attributes["isPassage"]):
            # Open a passage
            # Next, check if the object is already in the desired state
            if (whichAction == "open" and objToOpenOrClose.attributes["isOpenPassage"]):
                # Object is already open
                result = ActionSuccess(False, "That object (" + objToOpenOrClose.name + ") is already open.")
                self.actionHistory.add(actionType=actionType, arg1=objToOpenOrClose, arg2=None, result=result)
                return result

            elif (whichAction == "close" and not objToOpenOrClose.attributes["isOpenPassage"]):
                # Object is already closed
                result = ActionSuccess(False, "That object (" + objToOpenOrClose.name + ") is already closed.")
                self.actionHistory.add(actionType=actionType, arg1=objToOpenOrClose, arg2=None, result=result)
                return result

            # If we reach here, the object is within reach and is openable.  Open/close it.
            if (whichAction == "open"):
                objToOpenOrClose.attributes["isOpenPassage"] = True
                objToOpenOrClose.invalidateSpritesThisWorldTile()
                result = ActionSuccess(True, "I opened the " + objToOpenOrClose.name + ".")
                self.actionHistory.add(actionType=actionType, arg1=objToOpenOrClose, arg2=None, result=result)
                return result

            else:
                objToOpenOrClose.attributes["isOpenPassage"] = False
                objToOpenOrClose.invalidateSpritesThisWorldTile()
                result = ActionSuccess(True, "I closed the " + objToOpenOrClose.name + ".")
                self.actionHistory.add(actionType=actionType, arg1=objToOpenOrClose, arg2=None, result=result)
                return result



    # Activate/Deactivate an object
    # 'whichAction' should be "activate" or "deactivate"
    def actionActivateDeactivate(self, objToActivateOrDeactivate, whichAction="activate"):
        actionType = ActionType.ACTIVATE if whichAction == "activate" else ActionType.DEACTIVATE
        # First, check if the object is within reach (i.e. +/- 1 grid location)
        distX = abs(objToActivateOrDeactivate.attributes["gridX"] - self.attributes["gridX"])
        distY = abs(objToActivateOrDeactivate.attributes["gridY"] - self.attributes["gridY"])
        if (distX > 1 or distY > 1):
            # Object is not within reach
            result = ActionSuccess(False, "That object (" + objToActivateOrDeactivate.name + ") is not within reach. I can only activate/deactivate objects that are within +/- 1 grid location.")
            self.actionHistory.add(actionType=actionType, arg1=objToActivateOrDeactivate, arg2=None, result=result)
            return result

        # Next, check if the object is activatable
        if (not objToActivateOrDeactivate.attributes["isActivatable"]):
            # Object is not activatable
            result = ActionSuccess(False, "That object (" + objToActivateOrDeactivate.name + ") is not activatable/deactivatable.")
            self.actionHistory.add(actionType=actionType, arg1=objToActivateOrDeactivate, arg2=None, result=result)
            return result
                
        # Next, check if the object is already in the desired state
        if (whichAction == "activate" and objToActivateOrDeactivate.attributes["isActivated"]):
            # Object is already activated
            result = ActionSuccess(False, "That object (" + objToActivateOrDeactivate.name + ") is already activated.")
            self.actionHistory.add(actionType=actionType, arg1=objToActivateOrDeactivate, arg2=None, result=result)
            return result

        elif (whichAction == "deactivate" and not objToActivateOrDeactivate.attributes["isActivated"]):
            # Object is already deactivated
            result = ActionSuccess(False, "That object (" + objToActivateOrDeactivate.name + ") is already deactivated.")
            self.actionHistory.add(actionType=actionType, arg1=objToActivateOrDeactivate, arg2=None, result=result)
            return result
        
        # If we reach here, the object is within reach and is activatable.  Activate/deactivate it.
        if (whichAction == "activate"):
            objToActivateOrDeactivate.attributes["isActivated"] = True
            objToActivateOrDeactivate.invalidateSpritesThisWorldTile()
            self.updateLastInteractedObject([objToActivateOrDeactivate])
            result = ActionSuccess(True, "I activated the " + objToActivateOrDeactivate.name + ".")
            self.actionHistory.add(actionType=actionType, arg1=objToActivateOrDeactivate, arg2=None, result=result)
            return result

        else:
            objToActivateOrDeactivate.attributes["isActivated"] = False
            objToActivateOrDeactivate.invalidateSpritesThisWorldTile()
            self.updateLastInteractedObject([objToActivateOrDeactivate])
            result = ActionSuccess(True, "I deactivated the " + objToActivateOrDeactivate.name + ".")
            self.actionHistory.add(actionType=actionType, arg1=objToActivateOrDeactivate, arg2=None, result=result)
            return result

            

    # Eat an object
    def actionEat(self, objToEat):
        # First, check if the object is edible
        if (not objToEat.attributes["isEdible"]):
            # Object is not movable
            result = ActionSuccess(False, "That object (" + objToEat.name + ") is not edible.")
            self.actionHistory.add(actionType=ActionType.EAT, arg1=objToEat, arg2=None, result=result)
            return result

        # Next, check if the object is within reach (i.e. +/- 1 grid location)
        distX = abs(objToEat.attributes["gridX"] - self.attributes["gridX"])
        distY = abs(objToEat.attributes["gridY"] - self.attributes["gridY"])
        if (distX > 1 or distY > 1):
            # Object is not within reach
            result = ActionSuccess(False, "That object (" + objToEat.name + ") is not within reach. I can only eat objects that are within +/- 1 grid location.")
            self.actionHistory.add(actionType=ActionType.EAT, arg1=objToEat, arg2=None, result=result)
            return result

        # If we reach here, the object is edible and within reach.  Eat it.
        objToEat.invalidateSpritesThisWorldTile()            # Invalidate the sprites at the object's current location
        print("EATEN OBJECT PARENT CONTAINER: " + str(objToEat.parentContainer))    
        self.world.removeObject(objToEat)                    # Remove the object from the world
        print("EATEN OBJECT PARENT CONTAINER: " + str(objToEat.parentContainer))

        # When the agent eats something, it eats all of that object's contained objects (and, parts). 
        # First, collect all the parts that are being consumed
        allObjs = objToEat.getAllContainedObjectsRecursive(respectContainerStatus=False)
        allObjs.append(objToEat)
        objsAndParts = []
        for obj in allObjs:            
            objsAndParts.append(obj)
            objParts = obj.parts
            for part in objParts:
                objsAndParts.append(part)
                allPartContents = part.getAllContainedObjectsRecursive(respectContainerStatus=False)
                # add to objAndParts
                objsAndParts.extend(allPartContents)
        
        # Process any of the attributes of the objects being eaten
        for eatenObj in objsAndParts:
            print("## Eating object: " + eatenObj.name + " with attributes: " + str(eatenObj.attributes))
            # If the object is poisonous, set the poisonedCounter randomly to (-2, -20)
            if (eatenObj.attributes["isPoisonous"] == True):
                print("DEBUG: POISONED! (from " + eatenObj.name + ")")
                self.attributes["poisonedCounter"] = random.randint(-20, -2)
        
        result = ActionSuccess(True, "I ate the " + objToEat.name + ".")
        self.actionHistory.add(actionType=ActionType.EAT, arg1=objToEat, arg2=None, result=result)
        return result



    # Read an object
    def actionRead(self, objToRead):
        # First, check if the object to read is within reach (i.e. +/- 1 grid location)
        distX = abs(objToRead.attributes["gridX"] - self.attributes["gridX"])
        distY = abs(objToRead.attributes["gridY"] - self.attributes["gridY"])
        if (distX > 1 or distY > 1):
            # Object is not within reach
            result = ActionSuccess(False, "That object (" + objToRead.name + ") is not within reach. I can only read objects that are within +/- 1 grid location.")
            self.actionHistory.add(actionType=ActionType.READ, arg1=objToRead, arg2=None, result=result)
            return result
            
        # Next, check if the object to read is readable
        if (not objToRead.attributes["isReadable"]):
            # Object is not readable
            result = ActionSuccess(False, "That object (" + objToRead.name + ") is not readable.")
            self.actionHistory.add(actionType=ActionType.READ, arg1=objToRead, arg2=None, result=result)
            return result

        # If we reach here, the object is within reach and is readable.  Read it.
        # Check if the object is blank (i.e. document length is zero)
        if (len(objToRead.attributes["document"].strip()) == 0):
            # Object is blank
            result = ActionSuccess(False, "The " + objToRead.name + " appears blank. There is nothing to read.", MessageImportance.HIGH)
            self.actionHistory.add(actionType=ActionType.READ, arg1=objToRead, arg2=None, result=result)
            return result

        else:
            # Object is not blank
            self.updateLastInteractedObject([objToRead])
            result = ActionSuccess(True, "The " + objToRead.name + " reads:\n" + objToRead.attributes["document"], MessageImportance.HIGH)
            self.actionHistory.add(actionType=ActionType.READ, arg1=objToRead, arg2=None, result=result)
            return result



    # Use an object on another object
    def actionUse(self, objToUse, objToUseOn):
        # First, check if the object to use is within reach (i.e. +/- 1 grid location)
        distX = abs(objToUse.attributes["gridX"] - self.attributes["gridX"])
        distY = abs(objToUse.attributes["gridY"] - self.attributes["gridY"])
        if (distX > 1 or distY > 1):
            # Object is not within reach
            result = ActionSuccess(False, "That object (" + objToUse.name + ") is not within reach. I can only use objects that are within +/- 1 grid location.")
            self.actionHistory.add(actionType=ActionType.USE, arg1=objToUse, arg2=objToUseOn, result=result)        
            return result

        # Next, check if the object to use is usable
        if (not objToUse.attributes["isUsable"]):
            # Object is not usable
            result = ActionSuccess(False, "That object (" + objToUse.name + ") is not usable.")
            self.actionHistory.add(actionType=ActionType.USE, arg1=objToUse, arg2=objToUseOn, result=result)        
            return result

        # Next, check if the patient object is within reach (i.e. +/- 1 grid location)
        distX = abs(objToUseOn.attributes["gridX"] - self.attributes["gridX"])
        distY = abs(objToUseOn.attributes["gridY"] - self.attributes["gridY"])
        if (distX > 1 or distY > 1):
            # Object is not within reach
            result = ActionSuccess(False, "That object (" + objToUseOn.name + ") is not within reach. I can only use objects on other objects that are within +/- 1 grid location.")
            self.actionHistory.add(actionType=ActionType.USE, arg1=objToUse, arg2=objToUseOn, result=result)        
            return result

        # If we reach here, the object is usable, and both the device and patient object are within reach. Use it. 
        result = objToUse.actionUseWith(objToUseOn)

        # If there is a .generatedItems populated in this result, then process it            
        if ('generatedItems' in result.data):
            for item in result.data['generatedItems']:
                self.addObject(item)

        # Invalidate the sprites of all objects at these locations. 
        objToUse.invalidateSpritesThisWorldTile()
        objToUseOn.invalidateSpritesThisWorldTile()

        self.updateLastInteractedObject([objToUse, objToUseOn])

        # Return result
        self.actionHistory.add(actionType=ActionType.USE, arg1=objToUse, arg2=objToUseOn, result=result)        
        return result


    #
    #   DiscoveryFeed actions
    #

    # Get the most recent updates from the discovery feed
    def actionDiscoveryFeedGetPosts(self, startFromID=0):
        numPostsToRetrieve = 5 # Number of posts to retrieve
        postDelimiter = "---\n"
        allPosts = self.world.discoveryFeed.getPosts()                
        lastPosts = []
        notificationStr = ""
        if (startFromID <= 0):
            # Just get the last N posts
            lastPosts = allPosts[-numPostsToRetrieve:]
            notificationStr = "Showing the most recent " + str(len(lastPosts)) + " posts."
        else:
            # Get the last N posts starting from the specified ID.  Posts are sorted in ascending order. 
            postLocation = -1
            for post in allPosts:
                if (post["postID"] >= startFromID):
                    postLocation = allPosts.index(post)
                    break
            if (postLocation >= 0):
                postEnd = postLocation + numPostsToRetrieve
                if (postEnd > len(allPosts)):
                    postEnd = len(allPosts)
                
                lastPosts = allPosts[postLocation:postEnd]

                notificationStr = "Showing the most recent " + str(len(lastPosts)) + " posts starting from post ID " + str(startFromID) + "."
            else:
                # Just get the last N posts
                lastPosts = allPosts[-numPostsToRetrieve:]
                notificationStr = "Failed to find update posts with ID " + str(startFromID) + ", showing the most recent " + str(len(lastPosts)) + " posts."


        # Create a string to display the posts        
        postStrings = []
        for post in lastPosts:
            postStr = "Post " + str(post["postID"]) + "\nPosted by " + post["author"] + " on Step " + str(post["step"]) + ":\n"
            postStr += post["content"] + "\n"
            postStrings.append(postStr)

        # Final string
        outStr = "DiscoveryFeed (Update Posts)\n"
        outStr += "DiscoveryFeed contains " + str(len(allPosts)) + " update posts.\n"
        #outStr += "Last " + str(len(postStrings)) + " posts found:\n\n"
        outStr += notificationStr + "\n\n"
        outStr += postDelimiter.join(postStrings)

        # Generate result
        result = ActionSuccess(True, outStr, importance=MessageImportance.HIGH)        
        # Add to action history
        self.actionHistory.add(actionType=ActionType.DISCOVERY_FEED_GET_UPDATES, arg1=None, arg2=None, result=result)
        return result
    
    # Get the most recent updates from the discovery feed
    def actionDiscoveryFeedGetArticleTitles(self, startFromID=0):
        numArticlesToRetrieve = 5 # Number of posts to retrieve
        postDelimiter = "---\n"
        allArticles = self.world.discoveryFeed.getArticles()        
        
        lastArticles = []
        notificationStr = ""
        if (startFromID <= 0):
            # Just get the last N posts
            lastArticles = allArticles[-numArticlesToRetrieve:]
            notificationStr = "Showing the most recent " + str(len(lastArticles)) + " articles."
        else:
            # Get the last N posts starting from the specified ID.  Posts are sorted in ascending order. 
            postLocation = -1
            for post in allArticles:
                if (post["postID"] >= startFromID):
                    postLocation = allArticles.index(post)
                    break
            if (postLocation >= 0):
                postEnd = postLocation + numArticlesToRetrieve
                if (postEnd > len(allArticles)):
                    postEnd = len(allArticles)
                
                lastArticles = allArticles[postLocation:postEnd]

                notificationStr = "Showing the most recent " + str(len(lastArticles)) + " articles starting from document ID " + str(startFromID) + "."
            else:
                # Just get the last N posts
                lastArticles = allArticles[-numArticlesToRetrieve:]
                notificationStr = "Failed to find articles with ID " + str(startFromID) + ", showing the most recent " + str(len(lastArticles)) + " articles."


        # Create a string to display the posts        
        postStrings = []
        for post in lastArticles:
            postStr = "Article " + str(post["postID"]) + " Title: " + post["title"] + "\n"
            postStr += "Submitted by " + post["author"] + " on Step " + str(post["step"]) + "\n"
            #postStr += post["content"] + "\n"
            postStrings.append(postStr)

        # Final string
        outStr = "DiscoveryFeed (Article Index)\n"
        outStr += "DiscoveryFeed contains " + str(len(allArticles)) + " articles.\n"
        outStr += notificationStr
        outStr += " Articles can be retrieved by their ID. Here are their titles:\n\n"
        outStr += postDelimiter.join(postStrings)

        # Generate result
        result = ActionSuccess(True, outStr, importance=MessageImportance.HIGH)        
        # Add to action history
        self.actionHistory.add(actionType=ActionType.DISCOVERY_FEED_GET_ARTICLES, arg1=None, arg2=None, result=result)
        return result

    # Get the most recent updates from the discovery feed
    def actionDiscoveryFeedGetByID(self, postID):
        outStr = "DiscoveryFeed (Search)\n"
        outStr += "Search results for DiscoveryFeed document ID " + str(postID) + ":\n\n"

        post = self.world.discoveryFeed.getPostByID(postID)
        if (post == None):
            outStr += "No post found with ID " + str(postID) + "\n"
            result = ActionSuccess(False, outStr, importance=MessageImportance.HIGH)
            self.actionHistory.add(actionType=ActionType.DISCOVERY_FEED_GET_POST_BY_ID, arg1=postID, arg2=None, result=result)
            return result
        
        postStr = ""
        if (post["type"] == "update"):
            postStr = "Post " + str(post["postID"]) + "\nPosted by " + post["author"] + " on Step " + str(post["step"]) + ":\n"
            postStr += post["content"] + "\n"
        elif (post["type"] == "article"):
            postStr = "Article " + str(post["postID"]) + ": " + post["title"] + "\n"
            postStr += "Submitted by " + post["author"] + " on Step " + str(post["step"]) + "\n\n"
            postStr += post["content"] + "\n"
        else:
            #raise ValueError("Unknown post type: " + str(post["type"]))
            result = ActionSuccess(False, "Unknown post type: " + str(post["type"]) + "\n" + str(post), importance=MessageImportance.HIGH)

        outStr += postStr

        # Generate result
        result = ActionSuccess(True, outStr, importance=MessageImportance.HIGH)        
        # Add to action history
        self.actionHistory.add(actionType=ActionType.DISCOVERY_FEED_GET_POST_BY_ID, arg1=postID, arg2=None, result=result)
        return result
            
    # Make a post
    def actionDiscoveryFeedMakeUpdatePost(self, contentStr, signals:list=[]):
        # Create the post
        postID = self.world.discoveryFeed.addUpdatePost(self.world.step, self.name, contentStr, signals)

        post = self.world.discoveryFeed.getPostByID(postID)
        outStr = "DiscoveryFeed (Create Update Post)\n"
        outStr += "I made an update post with ID " + str(postID) + ":\n\n"
        postStr = "Post " + str(post["postID"]) + "\nPosted by " + post["author"] + " on Step " + str(post["step"]) + ":\n"
        postStr += post["content"] + "\n"
        outStr += postStr

        # Generate result
        result = ActionSuccess(True, outStr, importance=MessageImportance.HIGH)        

        # Add to action history
        self.actionHistory.add(actionType=ActionType.DISCOVERY_FEED_CREATE_UPDATE, arg1=post, arg2=None, result=result)
        return result
    
    # Make an article
    def actionDiscoveryFeedMakeArticle(self, titleStr, contentStr):
        # Create the article
        postID = self.world.discoveryFeed.addArticle(self.world.step, self.name, titleStr, contentStr)

        post = self.world.discoveryFeed.getPostByID(postID)
        outStr = "DiscoveryFeed (Create Article)\n"
        outStr += "I made an article with ID " + str(postID) + ":\n\n"
        postStr = "Article " + str(post["postID"]) + ": " + post["title"] + "\n"
        postStr += "Submitted by " + post["author"] + " on Step " + str(post["step"]) + "\n\n"
        postStr += post["content"] + "\n"
        outStr += postStr

        # Generate result
        result = ActionSuccess(True, outStr, importance=MessageImportance.HIGH)        

        # Add to action history
        self.actionHistory.add(actionType=ActionType.DISCOVERY_FEED_CREATE_ARTICLE, arg1=post, arg2=None, result=result)
        return result
        

    #
    #   Autopilot helpers
    #

    # Incrementally rotate (one rotation at a time) to face the given direction
    # Returns 'True' if a rotation action took place, and 'False' if the agent is already facing the desired direction
    def rotateToFaceDirection(self, directionToFace):
        # Get the current direction the agent is facing
        curDirection = self.attributes["faceDirection"]

        if (directionToFace == "identical"):
            return ActionSuccess(False, "That object is at the same location that I am, so there is no need to rotate.")

        # Check to make sure 'directionToFace' is a valid direction
        if (directionToFace not in ["north", "east", "south", "west"]):
            raise ValueError("Invalid directionToFace: " + str(directionToFace) + " (must be 'north', 'east', 'south', or 'west')")

        # If the agent is already facing the desired direction, return False
        if (curDirection == directionToFace):
            return ActionSuccess(False, "I am already facing in the requested direction (" + directionToFace + ").")

        # Otherwise, rotate the agent one rotation at a time
        # Clockwise: +1, Counter-clockwise: -1
        # This look-up table describes the next movement that the agent should take, in order to ultimately rotate to the desired direction
        movementLUT = {
            "north:east": +1,
            "north:west": -1,
            "north:south": +1,
            "east:south": +1,
            "east:north": -1,
            "east:west": +1,
            "south:west": +1,
            "south:east": -1,
            "south:north": +1,
            "west:north": +1,
            "west:south": -1,
            "west:east": +1,
        }

        # Get the next movement to take
        nextMovement = movementLUT[curDirection + ":" + directionToFace]
        # Take the action
        self.actionRotateAgentFacingDirection(nextMovement)
        
        return ActionSuccess(True, "I am rotating towards facing the requested direction (" + directionToFace + ").")

    # Convert x/y deltas (e.g. (0, -1 ) to a direction (e.g. "north", "east")
    def convertXYDeltasToDirection(self, deltaX, deltaY):
        if (deltaX == 0) and (deltaY == +1):
            return "south"
        elif (deltaX == 0) and (deltaY == -1):
            return "north"
        elif (deltaX == +1) and (deltaY == 0):
            return "east"
        elif (deltaX == -1) and (deltaY == 0):
            return "west"
        else:
            raise ValueError("Invalid deltaX/deltaY: " + str(deltaX) + ", " + str(deltaY) + " (must be (0, +1), (0, -1), (+1, 0), or (-1, 0))")


    #
    #   Autopilot: Adding actions to the queue
    #
    def addAutopilotActionToQueue(self, action):
        # Add a timestamp to the action 
        action.timestamp = self.actionTimestampCounter

        # Add the action to the queue
        self.autopilotActionQueue.append(action)

        # Increment the timestamp
        self.actionTimestampCounter += 1

        # Sort the autopilot action queue by priority (highest priority first).  Sort by two fields: first priority, then time added to queue 'timestamp')
        #  Note: The 'timestamp' field is used to break ties in priority
        self.autopilotActionQueue.sort(key=lambda x: (x.priority, -x.timestamp), reverse=True)                        
        

    # Display the autopilot queue (for debugging)
    def displayAutopilotQueueStr(self):
        outStr = "Autopilot Action Queue:\n"

        for idx, action in enumerate(self.autopilotActionQueue):            
            outStr += "  #" + str(idx) + " (priority " + str(action.priority) + "): " + str(action) + "\n"

        return outStr



    #
    #   Dialog Actions
    #
    def setDialogTree(self, dialogTree):
        self.dialogTree = dialogTree

    def setInDialogWith(self, agent):
        self.attributes['inDialogWith'] = agent

    def setNotInDialog(self):
        self.attributes['inDialogWith'] = None

    # Is this agent currently in dialog?
    def isInDialog(self):
        return ('inDialogWith' in self.attributes) and (self.attributes['inDialogWith'] != None)        

    def getAgentInDialogWith(self):
        return self.attributes['inDialogWith']

    # Exit whatever dialog we're in 
    def exitDialog(self):
        # If we're in dialog, then exit it
        if (self.isInDialog()):
            self.attributes['inDialogWith'].dialogTree.endDialog()
        self.setNotInDialog()
                

        

    # If 'dialogStrToSay' is None, then it will stop the dialog with 'agentToTalkTo'
    def actionDialog(self, agentToTalkTo, dialogStrToSay=None):
        # Check if dialogable
        if ('isDialogable' in agentToTalkTo.attributes) and (agentToTalkTo.attributes["isDialogable"] == False):
            return ActionSuccess(False, "You can't talk to that (" + agentToTalkTo.name + ").")

        # Make sure the agent to talk to has a dialog tree
        if (agentToTalkTo.dialogTree == None):
            return ActionSuccess(False, "That agent (" + agentToTalkTo.name + ") has no dialog tree set.")

        # Otherwise, start the dialog

        # First, check if we're currently talking to that agent/in the middle of a dialog
        if (agentToTalkTo.dialogTree.getAgentTalkingTo() == self):
            # Check if te action is to stop the dialog
            if (dialogStrToSay == None):
                # Stop the dialog
                agentToTalkTo.dialogTree.endDialog()
                self.setNotInDialog()
                return ActionSuccess(True, "Finished talking to " + str(agentToTalkTo.name) + ".")

            # We're currently in the middle of a dialog -- send the dialogStrToSay. 
            success = agentToTalkTo.dialogTree.say(thingToSay=dialogStrToSay, agentEngaging=self)
            if (success == False):
                self.setNotInDialog()
                return ActionSuccess(False, "Something went wrong in the dialog -- the response was unexpected.")

            # Get the NPC's response, and our possible next dialog options
            npcResponse, nextDialogOptions = agentToTalkTo.dialogTree.getCurrentDialog()

            # Return the NPC's response
            self.setInDialogWith(agentToTalkTo)
            return DialogSuccess(True, "We are talking.  You said: " + str(dialogStrToSay) + "\n\n" + str(agentToTalkTo.name) + " said: " + str(npcResponse), nextDialogOptions)

        else: 
            # We're not currently talking to the agent.  Try to initiate conversation.
            if (agentToTalkTo.dialogTree.isBusy() == True):
                # The NPC is busy talking to another agent
                self.setNotInDialog()
                return ActionSuccess(False, "That agent (" + agentToTalkTo.name + ") is busy talking to (" + str(agentToTalkTo.dialogTree.getAgentTalkingTo().name) + ").")
            else:
                # Check if te action is to stop the dialog
                if (dialogStrToSay == None):
                    # Stop the dialog
                    agentToTalkTo.dialogTree.endDialog()
                    self.setNotInDialog()
                    return ActionSuccess(True, "Finished talking to " + str(agentToTalkTo.name) + ".")

                # The agent is not busy, initiate conversation
                agentToTalkTo.dialogTree.initiateDialog(self)

                # Get the NPC's response, and our possible next dialog options
                npcResponse, nextDialogOptions = agentToTalkTo.dialogTree.getCurrentDialog()

                # Return the NPC's response
                self.setInDialogWith(agentToTalkTo)
                return DialogSuccess(True, "We are talking.  You said: " + str(dialogStrToSay) + "\n\n" + str(agentToTalkTo.name) + " said: " + str(npcResponse), nextDialogOptions)
            

        # Return a dialog placeholder
        #return ActionSuccess(True, "We are talking.  You said: " + str(dialogStrToSay), MessageImportance.HIGH)
                

    #
    # Sprite
    #

    # This function updates what object the agent should be shown "holding". 
    # It takes a list of objects (nominally from the last action the agent took), and will pick one that the agent is currently carying. 
    # If the agent is not carrying any, then it will set 'objectToShow' to None.
    # If the agent is carrying more than one, it will show the first one it finds. 
    def updateLastInteractedObject(self, objList:list):
        self.attributes["objectToShow"] = None                     # The object to show the agent carrying
        
        # Filter the list of objects to show only those that are in the agent's inventory
        accessibleInventoryObjects = self.getAllContainedObjectsRecursive(respectContainerStatus=True)
        
        filteredInInventory = []
        for obj in objList:
            if (obj in accessibleInventoryObjects):
                filteredInInventory.append(obj)

        # If there are no objects in the list, then we're done
        if (len(filteredInInventory) == 0):
            return

        # Otherwise, take the first object
        self.attributes["objectToShow"] = filteredInInventory[0]


    def clearLastInteractedObject(self):
        self.attributes["objectToShow"] = None
        

    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return

        # Change the sprite based on the direction the agent is facing
        if (self.attributes["faceDirection"] == "north"):
            self.curSpriteName = self.spriteCharacterPrefix + "agent_facing_north"
        elif (self.attributes["faceDirection"] == "south"):
            self.curSpriteName = self.spriteCharacterPrefix + "agent_facing_south"
        elif (self.attributes["faceDirection"] == "east"):
            self.curSpriteName = self.spriteCharacterPrefix + "agent_facing_east"
        elif (self.attributes["faceDirection"] == "west"):
            self.curSpriteName = self.spriteCharacterPrefix + "agent_facing_west"
        else:
            # Unknown direction -- this should never happen.  Default to south.
            self.curSpriteName = self.spriteCharacterPrefix + "agent_facing_south"

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName




#
#   Non-player character (controlled by the simulation)
#
class NPC(Agent):
    # Constructor
    def __init__(self, world, name):
        # Default sprite name
        Agent.__init__(self, world, "agent", name, defaultSpriteName = "character17_agent_facing_south")
        #Object.__init__(self, world, "agent", name, defaultSpriteName = "character17_agent_facing_south")
    
        # Rendering
        self.attributes["faceDirection"] = "south"        
        self.spriteCharacterPrefix = "character17_"

        # Default attributes
        self.attributes["isMovable"] = False                       # Can it be moved?

        # Agent is a container for its inventory
        # Container attributes
        self.attributes['isContainer'] = True                      # Is it a container?
        self.attributes['isOpenable'] = False                      # Can be opened
        self.attributes['isOpenContainer'] = True                 # If it's a container, then is it open?
        self.attributes['containerPrefix'] = "in"                  # Container prefix (e.g. "in" or "on")            
    
        # Dialog attributes
        self.attributes['isDialogable'] = True                     # Can it be dialoged with?

        # NPC States
        self.attributes['dialogAgentsSpokenWith'] = []             # List of dialog agents that this NPC has spoken with

        # Pathfinder
        self.pathfinder = Pathfinder()

    #
    #   Dialog Actions
    #
    # def actionDialog(self, agentDoingTalking, dialogStrToSay):

    #     # Step 1: Check if the agent has already spoken with this NPC
    #     if (agentDoingTalking.name in self.attributes['dialogAgentsSpokenWith']):
    #         # Agent has already spoken with this NPC
    #         return "I've already spoken with you."

    #     # Add the agent to the list of agents that this NPC has spoken with
    #     self.attributes['dialogAgentsSpokenWith'].append(agentDoingTalking.name)

    #     # If we reach here, the agent has not spoken with this NPC yet
    #     return "Hello, " + agentDoingTalking.name + ".  I am " + self.name + ".  Nice to meet you."


    #
    #   NPC Auto-navigation
    #   
    def _doNPCAutonavigation(self):
        # Check to see if there's a goal location attribute
        if ("goalLocation" not in self.attributes):
            print("_doNPCAutonavigation: No goal location attribute found.  Exiting. (agent: " + self.name + ")")
            return False
            #self.attributes["goalLocation"] = (10, 10)

        pathSuccess, nextX, nextY, pathLength = self.pathfinder.findPathNextStep(self.world, self.attributes["gridX"], self.attributes["gridY"], self.attributes["goalLocation"][0], self.attributes["goalLocation"][1])
        
        if (not pathSuccess):
            print("_doNPCAutonavigation: No path found to goal location.  Exiting. (agent: " + self.name + ")")
            return False

        if ("doorNeedsToBeClosed" in self.attributes) and (self.attributes["doorNeedsToBeClosed"] != None) and (self.attributes["movesSinceDoorOpen"] == 1):
            # We recently opened a door -- close it
            print("AGENT: CLOSING DOOR")
            doorToClose = self.attributes["doorNeedsToBeClosed"]
            self.actionOpenClose(doorToClose, "close")
            self.attributes["doorNeedsToBeClosed"] = None
            self.attributes["movesSinceDoorOpen"] = 0
        else:
            # Calculate deltas
            deltaX = nextX - self.attributes["gridX"]
            deltaY = nextY - self.attributes["gridY"]

            # First, check to see if we're facing the correct direction.  If not, start rotating in that direction.
            desiredDirection = self.convertXYDeltasToDirection(deltaX, deltaY)
            if (desiredDirection != self.attributes["faceDirection"]):
                # We're not facing the correct direction -- rotate
                print("AGENT: ROTATING TO FACE DIRECTION (curDirection: " + self.attributes["faceDirection"] + ", desiredDirection: " + desiredDirection + ")")
                rotateSuccess = self.rotateToFaceDirection(desiredDirection)
                print(rotateSuccess)
                return True

            # First, check to see if the next step has a barrier (like a door) that needs to be opened
            allObjs = self.world.getObjectsAt(nextX, nextY)
            # Get a list of objects that are not passable (isPassable == False)
            allObjsNotPassable = [obj for obj in allObjs if (obj.attributes["isPassable"] == False)]
            
            # If there are no impassable objects, then move the agent one step in the forward direction
            if (len(allObjsNotPassable) == 0):
                # Move agent one step in the forward direction
                #moveSuccess = self.actionMoveAgent(deltaX, deltaY)
                print("AGENT: MOVING FORWARD")
                moveSuccess = self.actionMoveAgentForwardBackward(direction=+1)
                self.attributes["movesSinceDoorOpen"] += 1
            else:
                print("AGENT: TRYING TO OPEN IMPASSABLE OBJECT")
                # There's one or more impassable objects -- try to open them.
                for obj in allObjsNotPassable:
                    # Check to see if the object is openable
                    if (obj.attributes["isOpenable"]):
                        # Open the object
                        self.actionOpenClose(obj, "open")
                        self.attributes["doorNeedsToBeClosed"] = obj
                        self.attributes["movesSinceDoorOpen"] = 0
                        # Break out of the loop
                        break

        return True
        
        # else:
        #     # No success -- means either (a) we're already in the goal location, or (b) there's no path to the goal location
        #     # In either case, we'll just pick a new goal location
        #     print("Finding new goal location")
        #     #time.sleep(1)
        #     self.attributes["goalLocation"] = (random.randint(0, self.world.sizeX - 1), random.randint(0, self.world.sizeY - 1))



#
#   Non-player character (controlled by the simulation)
#
class NPCChef(NPC):
    # Constructor
    def __init__(self, world, name):
        # Default sprite name
        Agent.__init__(self, world, "agent", name, defaultSpriteName = "character17_agent_facing_south", tables=None, pot=None)
    
        # Rendering
        self.attributes["faceDirection"] = "south"        
        self.spriteCharacterPrefix = "character17_"



    #
    #   Dialog Actions
    #
    # def actionDialog(self, agentDoingTalking, dialogStrToSay):

    #     # Step 1: Check if the agent has already spoken with this NPC
    #     if (agentDoingTalking.name in self.attributes['dialogAgentsSpokenWith']):
    #         # Agent has already spoken with this NPC
    #         return "I've already spoken with you."

    #     # Add the agent to the list of agents that this NPC has spoken with
    #     self.attributes['dialogAgentsSpokenWith'].append(agentDoingTalking.name)

    #     # If we reach here, the agent has not spoken with this NPC yet
    #     return "Hello, " + agentDoingTalking.name + ".  I am " + self.name + ".  Nice to meet you."


    #
    #   Tick
    #
        
    # Tick
    def tick(self):
        # # Randomly move agent
        # if (random.random() < 0.1):
        #     # Randomly move the agent
        #     deltaX = random.randint(-1, 1)
        #     deltaY = random.randint(-1, 1)
        #     self.actionMoveAgent(deltaX, deltaY)

        # Stop if the object has already had tick() called this update -- this might have happened if the object moved locations in this current update cycle.
        if (self.tickCompleted):
            return

        # Debug
        print("NPC States (name: " + self.name + "): " + str(self.attributes['states']))

        # Call superclass
        NPC.tick(self)

        # Sprite modifier updates
        if ("poisoned" in self.attributes['states']):
            self.curSpriteModifiers.add("placeholder_sick")


        # Interpret any external states
        if ("poisoned" in self.attributes['states']):
            # If the agent is poisoned, then head for the infirmary
            # Remove the "wandering" state
            if ("wandering" in self.attributes['states']):
                self.removeState("wandering")
            # Head to the infirmary
            self.attributes["goalLocation"] = (23, 7)   # Infirmary entrance

        elif ("moveToInitialLocation" in self.attributes['states']):
            # Move to the starting location
            self.attributes["goalLocation"] = (20, 21)
        elif ("moveToPutPotPack" in self.attributes['states']):
            # Move to the starting location
            self.attributes["goalLocation"] = (21, 21)    
        elif ("putPotBack" in self.attributes['states']):
            # Get pot from inventory
            pot = self.attributes["foodContainer"]
            # Drop pot
            successDrop = self.actionDrop(pot)
            # Remove "putPotBack" from external signals
            self.removeState("putPotBack")
            # Add "moveToInitialLocation" to state
            self.addState("moveToInitialLocation")
            # Remove 'foodContainer' attribute
            del self.attributes['foodContainer']


        elif ("serveDinner" in self.attributes['states']):
            # Remove the "waiting" state
            if ("waiting" in self.attributes['states']):
                self.removeState("waiting")
            # Head to the cafeteria kitchen, beside the table with the pot
            self.attributes["goalLocation"] = (21, 21)
            # remove "eatSignal" from external signals
            self.removeState("serveDinner")
            # Add "movingToCafeteria" to external signals
            self.addState("pickupFoodFromCafeteria")

        elif ("takePotFromCafeteria" in self.attributes['states']):
            # Look directly in front of the agent for something edible
            # Get the location in front of the agent
            (facingX, facingY) = self.getWorldLocationAgentIsFacing()
            # Get all objects at that world location
            objectsInFrontOfAgent = self.world.getObjectsAt(facingX, facingY)
            # Print names of objects in front of agent
            print("Objects in front of agent: " + str([x.name for x in objectsInFrontOfAgent]))

            # Loop through all objects at that location, looking for the pot
            potObjects = [x for x in objectsInFrontOfAgent if x.type == 'pot']
            # Print names of edible objects in front of agent
            print("Pot objects in front of agent: " + str([x.name for x in potObjects]))

            if (len(potObjects) > 0):
                print("I want to take the " + potObjects[0].name)
                # Take the first edible object
                potObject = potObjects[0]
                # Take the object
                successTake = self.actionPickUp(potObject)
                print("TAKE: " + str(successTake))

                # Remove "takeFoodFromCafeteria" from external signals
                self.removeState("takePotFromCafeteria")
                # Add "eating" to external signals
                self.addState("serveFood")
                self.addState("moveToSpot1")

                # Set which object to eat
                self.attributes["foodContainer"] = potObject

        elif ("serveFood" in self.attributes['states']):
            # Moving to spots
            if ("moveToSpot1" in self.attributes['states']):
                self.attributes["goalLocation"] = (21, 22)      # Move to spot 1
            elif ("moveToSpot2" in self.attributes['states']):
                self.attributes["goalLocation"] = (22, 22)      # Move to spot 2
            elif ("moveToSpot3" in self.attributes['states']):
                self.attributes["goalLocation"] = (23, 22)      # Move to spot 3
            elif ("moveToSpot4" in self.attributes['states']):
                self.attributes["goalLocation"] = (24, 22)      # Move to spot 4
            elif ("moveToSpot5" in self.attributes['states']):
                self.attributes["goalLocation"] = (25, 22)      # Move to spot 5

            # Putting food at spots
            elif ("putFoodAtSpot1" in self.attributes['states']):
                # Take the food out of the container
                containerObjects = self.attributes["foodContainer"].contents
                if (len(containerObjects) > 0):
                    foodObject = self.attributes["foodContainer"].contents[0]
                    # Put the food at the spot
                    successDrop = self.actionDrop(foodObject)
                    # Move to next spot
                    self.removeState("putFoodAtSpot1")
                    self.addState("moveToSpot2")
                else:
                    print("NO FOOD IN CONTAINER!")
            elif ("putFoodAtSpot2" in self.attributes['states']):
                # Take the food out of the container
                containerObjects = self.attributes["foodContainer"].contents
                if (len(containerObjects) > 0):
                    foodObject = self.attributes["foodContainer"].contents[0]
                    # Put the food at the spot
                    successDrop = self.actionDrop(foodObject)
                    # Move to next spot
                    self.removeState("putFoodAtSpot2")
                    self.addState("moveToSpot3")
                else:
                    print("NO FOOD IN CONTAINER!")
            elif ("putFoodAtSpot3" in self.attributes['states']):
                # Take the food out of the container
                containerObjects = self.attributes["foodContainer"].contents
                if (len(containerObjects) > 0):
                    foodObject = self.attributes["foodContainer"].contents[0]
                    # Put the food at the spot
                    successDrop = self.actionDrop(foodObject)
                    # Move to next spot
                    self.removeState("putFoodAtSpot3")
                    self.addState("moveToSpot4")
                else:
                    print("NO FOOD IN CONTAINER!")
            elif ("putFoodAtSpot4" in self.attributes['states']):
                # Take the food out of the container
                containerObjects = self.attributes["foodContainer"].contents
                if (len(containerObjects) > 0):
                    foodObject = self.attributes["foodContainer"].contents[0]
                    # Put the food at the spot
                    successDrop = self.actionDrop(foodObject)
                    # Move to next spot
                    self.removeState("putFoodAtSpot4")
                    self.addState("moveToSpot5")
                else:
                    print("NO FOOD IN CONTAINER!")
            elif ("putFoodAtSpot5" in self.attributes['states']):
                # Take the food out of the container
                containerObjects = self.attributes["foodContainer"].contents
                if (len(containerObjects) > 0):
                    foodObject = self.attributes["foodContainer"].contents[0]
                    # Put the food at the spot
                    successDrop = self.actionDrop(foodObject)
                    # Move to next spot
                    self.removeState("putFoodAtSpot5")
                    self.addState("moveToPutPotPack")
                else:
                    print("NO FOOD IN CONTAINER!")
    






        # elif ("eating" in self.attributes['states']):
        #     # Eat the food in the inventory
        #     if ("objectToEat" not in self.attributes):
        #         # Error -- no object to eat is listed, shouldn't be here
        #         print("Error: No object to eat is listed, shouldn't be here")
        #     else:
        #         objectToEat = self.attributes["objectToEat"]
        #         # Eat the object
        #         successEat = self.actionEat(objectToEat)
        #         print(successEat)

        #         # Remove "eating" from external signals
        #         self.removeState("eating")
        #         # Add "wandering" to external signals
        #         self.addState("wandering")
        #         # Remove "objectToEat" attribute
        #         del self.attributes["objectToEat"]

        else:
            # Default behavior, if no other behaviors are present, is to wander
            if ("waiting" not in self.attributes['states']):
                self.addState("waiting")


        # Pathfinding/Auto-navigation        
        if ("goalLocation" in self.attributes):
            success = self._doNPCAutonavigation()
            if (not success):
                # If we're in the "pickupFoodFromCafeteria" state, check to see if we're already in the goal location
                if ("pickupFoodFromCafeteria" in self.attributes['states']):
                    if (self.attributes["gridX"] == self.attributes["goalLocation"][0]) and (self.attributes["gridY"] == self.attributes["goalLocation"][1]):
                        # We're in the kitchen at the pot -- pick it up
                        self.removeState("pickupFoodFromCafeteria")
                        self.addState("takePotFromCafeteria")
                        # Remove the goal location
                        del self.attributes["goalLocation"]
                elif ("moveToInitialLocation" in self.attributes['states']):
                    # Check to see if we've moved to the initial location
                    if (self.attributes["gridX"] == self.attributes["goalLocation"][0]) and (self.attributes["gridY"] == self.attributes["goalLocation"][1]):
                        # We're in the kitchen at the pot -- pick it up
                        self.removeState("moveToInitialLocation")
                        self.addState("TODO")
                        # Remove the goal location
                        del self.attributes["goalLocation"]
                elif ("moveToPutPotPack" in self.attributes['states']):
                    # Check to see if we've moved to the initial location
                    if (self.attributes["gridX"] == self.attributes["goalLocation"][0]) and (self.attributes["gridY"] == self.attributes["goalLocation"][1]):
                        # We're in the kitchen at the pot -- pick it up
                        self.removeState("moveToPutPotPack")
                        self.addState("putPotBack")
                        # Remove the goal location
                        del self.attributes["goalLocation"]

                elif ("serveFood" in self.attributes['states']):
                    if (self.attributes["gridX"] == self.attributes["goalLocation"][0]) and (self.attributes["gridY"] == self.attributes["goalLocation"][1]):
                        # We're in the kitchen at the pot -- pick it up
                        #self.removeState("serveFood")
                        if ("moveToSpot1" in self.attributes['states']):
                            self.removeState("moveToSpot1")
                            self.addState("putFoodAtSpot1")
                            del self.attributes["goalLocation"]
                        elif ("moveToSpot2" in self.attributes['states']):
                            self.removeState("moveToSpot2")
                            self.addState("putFoodAtSpot2")
                            del self.attributes["goalLocation"]
                        elif ("moveToSpot3" in self.attributes['states']):
                            self.removeState("moveToSpot3")
                            self.addState("putFoodAtSpot3")
                            del self.attributes["goalLocation"]
                        elif ("moveToSpot4" in self.attributes['states']):
                            self.removeState("moveToSpot4")
                            self.addState("putFoodAtSpot4")
                            del self.attributes["goalLocation"]
                        elif ("moveToSpot5" in self.attributes['states']):
                            self.removeState("moveToSpot5")
                            self.addState("putFoodAtSpot5")
                            del self.attributes["goalLocation"]


                elif ("wandering" in self.attributes['states']):
                    self.attributes["goalLocation"] = (random.randint(0, self.world.sizeX - 1), random.randint(0, self.world.sizeY - 1))   


                # We failed to find a path to the goal location -- pick a new goal location
                #self.attributes["goalLocation"] = (random.randint(0, self.world.sizeX - 1), random.randint(0, self.world.sizeY - 1))
        else:
            if ("wandering" in self.attributes['states']):
                self.attributes["goalLocation"] = (random.randint(0, self.world.sizeX - 1), random.randint(0, self.world.sizeY - 1))

        # DEBUG: End of tick -- display the agent's current state
        print("NPC States (name: " + self.name + "): " + str(self.attributes))



#
#   Non-player character (controlled by the simulation)
#
class NPCColonist(NPC):
    # Constructor
    def __init__(self, world, name):
        # Default sprite name
        Agent.__init__(self, world, "agent", name, defaultSpriteName = "character16_agent_facing_south")
    
        # Rendering
        self.attributes["faceDirection"] = "south"        
        self.spriteCharacterPrefix = "character16_"

        # Default attributes
        self.attributes["isMovable"] = False                       # Can it be moved?

        # Agent is a container for its inventory
        # Container attributes
        self.attributes['isContainer'] = True                      # Is it a container?
        self.attributes['isOpenable'] = False                      # Can be opened
        self.attributes['isOpenContainer'] = True                 # If it's a container, then is it open?
        self.attributes['containerPrefix'] = "in"                  # Container prefix (e.g. "in" or "on")            
    
        # Dialog attributes
        self.attributes['isDialogable'] = True                     # Can it be dialoged with?

        # NPC States
        self.attributes['dialogAgentsSpokenWith'] = []             # List of dialog agents that this NPC has spoken with

        # Pathfinder
        self.pathfinder = Pathfinder()


    #
    #   Dialog Actions
    #
    # def actionDialog(self, agentDoingTalking, dialogStrToSay):

    #     # Step 1: Check if the agent has already spoken with this NPC
    #     if (agentDoingTalking.name in self.attributes['dialogAgentsSpokenWith']):
    #         # Agent has already spoken with this NPC
    #         return "I've already spoken with you."

    #     # Add the agent to the list of agents that this NPC has spoken with
    #     self.attributes['dialogAgentsSpokenWith'].append(agentDoingTalking.name)

    #     # If we reach here, the agent has not spoken with this NPC yet
    #     return "Hello, " + agentDoingTalking.name + ".  I am " + self.name + ".  Nice to meet you."    

    
    #
    #   Tick
    #
        
    # Tick
    def tick(self):
        # # Randomly move agent
        # if (random.random() < 0.1):
        #     # Randomly move the agent
        #     deltaX = random.randint(-1, 1)
        #     deltaY = random.randint(-1, 1)
        #     self.actionMoveAgent(deltaX, deltaY)

        # Stop if the object has already had tick() called this update -- this might have happened if the object moved locations in this current update cycle.
        if (self.tickCompleted):
            return

        # Debug
        print("NPC States (name: " + self.name + "): " + str(self.attributes['states']))

        # Call superclass
        NPC.tick(self)

        # Sprite modifier updates
        if ("poisoned" in self.attributes['states']):
            self.curSpriteModifiers.add("placeholder_sick")


        # Interpret any external states
        if ("poisoned" in self.attributes['states']):
            # If the agent is poisoned, then head for the infirmary
            # Remove the "wandering" state
            if ("wandering" in self.attributes['states']):
                self.removeState("wandering")
            # Head to the infirmary
            self.attributes["goalLocation"] = (23, 7)   # Infirmary entrance


        elif ("eatSignal" in self.attributes['states']):
            # Remove the "wandering" state
            if ("wandering" in self.attributes['states']):
                self.removeState("wandering")
            # Head to the cafeteria
            self.attributes["goalLocation"] = (23, 23)
            # remove "eatSignal" from external signals
            self.removeState("eatSignal")
            # Add "movingToCafeteria" to external signals
            self.addState("movingToCafeteria")

        elif ("takeFoodFromCafeteria" in self.attributes['states']):
            # Look directly in front of the agent for something edible
            # Get the location in front of the agent
            (facingX, facingY) = self.getWorldLocationAgentIsFacing()
            # Get all objects at that world location
            objectsInFrontOfAgent = self.world.getObjectsAt(facingX, facingY)
            # Print names of objects in front of agent
            print("Objects in front of agent: " + str([x.name for x in objectsInFrontOfAgent]))

            # Loop through all objects at that location, looking for edible objects
            edibleObjects = [x for x in objectsInFrontOfAgent if x.attributes['isEdible']]
            # Print names of edible objects in front of agent
            print("Edible objects in front of agent: " + str([x.name for x in edibleObjects]))

            if (len(edibleObjects) > 0):
                print("I want to take the " + edibleObjects[0].name)
                # Take the first edible object
                edibleObject = edibleObjects[0]
                # Take the object
                successTake = self.actionPickUp(edibleObject)
                print(successTake)

                # Remove "takeFoodFromCafeteria" from external signals
                self.removeState("takeFoodFromCafeteria")
                # Add "eating" to external signals
                self.addState("eating")

                # Set which object to eat
                self.attributes["objectToEat"] = edibleObject

        elif ("eating" in self.attributes['states']):
            # Eat the food in the inventory
            if ("objectToEat" not in self.attributes):
                # Error -- no object to eat is listed, shouldn't be here
                print("Error: No object to eat is listed, shouldn't be here")
            else:
                objectToEat = self.attributes["objectToEat"]
                # Eat the object
                successEat = self.actionEat(objectToEat)
                print(successEat)

                # Remove "eating" from external signals
                self.removeState("eating")
                # Add "wandering" to external signals
                self.addState("wandering")
                # Remove "objectToEat" attribute
                del self.attributes["objectToEat"]

        else:
            # Default behavior, if no other behaviors are present, is to wander
            if ("wandering" not in self.attributes['states']):
                self.addState("wandering")


        # Pathfinding/Auto-navigation        
        if ("goalLocation" in self.attributes):
            success = self._doNPCAutonavigation()
            if (not success):
                # If we're in the "movingToCafeteria" state, check to see if we're already in the goal location
                if ("movingToCafeteria" in self.attributes['states']):
                    if (self.attributes["gridX"] == self.attributes["goalLocation"][0]) and (self.attributes["gridY"] == self.attributes["goalLocation"][1]):
                        # We're in the cafeteria -- eat!
                        self.removeState("movingToCafeteria")
                        self.addState("takeFoodFromCafeteria")
                        # Remove the goal location
                        del self.attributes["goalLocation"]

                elif ("wandering" in self.attributes['states']):
                    self.attributes["goalLocation"] = (random.randint(0, self.world.sizeX - 1), random.randint(0, self.world.sizeY - 1))   


                # We failed to find a path to the goal location -- pick a new goal location
                #self.attributes["goalLocation"] = (random.randint(0, self.world.sizeX - 1), random.randint(0, self.world.sizeY - 1))
        else:
            if ("wandering" in self.attributes['states']):
                self.attributes["goalLocation"] = (random.randint(0, self.world.sizeX - 1), random.randint(0, self.world.sizeY - 1))

        # DEBUG: End of tick -- display the agent's current state
        print("NPC States (name: " + self.name + "): " + str(self.attributes))



#
#   Non-player character (controlled by the simulation)
#
class NPCColonist1(NPC):
    # Constructor
    def __init__(self, world, name, thingsToPickup=None, whereToPlace=None):        ## DEBUG: thingToPickUp is a placeholder
        # Default sprite name
        Agent.__init__(self, world, "agent", name, defaultSpriteName = "character15_agent_facing_south")
    
        # Rendering
        self.attributes["faceDirection"] = "south"        
        self.spriteCharacterPrefix = "character15_"

        # Below is the original farm behavior (picking up mushrooms and taking them to the kitchen)
        # # Add a default action into the action queue 
        # if (thingsToPickup is not None):
        #     for thingToPickup in thingsToPickup:
        #         self.autopilotActionQueue.append( AutopilotAction_PickupObj(thingToPickup) )
        #         self.autopilotActionQueue.append( AutopilotAction_PlaceObjInContainer(thingToPickup, whereToPlace) )

        #     # Then, move to the farm
        #     self.autopilotActionQueue.append( AutopilotAction_GotoXY(x=10, y=16) )
        # else:
        #     self.autopilotActionQueue.append( AutopilotAction_GotoXY(x=1, y=1) )

        # Test of the new action
        #class AutopilotAction_PickupObjectsInArea(AutopilotAction):
        #def __init__(self, x, y, width, height, objectTypes:list, container, priority=4):
        fieldX = 10
        fieldY = 13
        fieldWidth = 6
        fieldHeight = 5
        objectTypes = ["mushroom"]
        container = whereToPlace
        self.addAutopilotActionToQueue( AutopilotAction_PickupObjectsInArea(fieldX, fieldY, fieldWidth, fieldHeight, objectTypes, container) )

        

    #
    #   Dialog Actions
    #
    # def actionDialog(self, agentDoingTalking, dialogStrToSay):

    #     # Step 1: Check if the agent has already spoken with this NPC
    #     if (agentDoingTalking.name in self.attributes['dialogAgentsSpokenWith']):
    #         # Agent has already spoken with this NPC
    #         return "I've already spoken with you."

    #     # Add the agent to the list of agents that this NPC has spoken with
    #     self.attributes['dialogAgentsSpokenWith'].append(agentDoingTalking.name)

    #     # If we reach here, the agent has not spoken with this NPC yet
    #     return "Hello, " + agentDoingTalking.name + ".  I am " + self.name + ".  Nice to meet you."    

    
    #
    #   Tick
    #
        
    # Tick
    def tick(self):
        # # Randomly move agent
        # if (random.random() < 0.1):
        #     # Randomly move the agent
        #     deltaX = random.randint(-1, 1)
        #     deltaY = random.randint(-1, 1)
        #     self.actionMoveAgent(deltaX, deltaY)

        # Stop if the object has already had tick() called this update -- this might have happened if the object moved locations in this current update cycle.
        if (self.tickCompleted):
            return

        # Debug
        print("NPC States (name: " + self.name + "): " + str(self.attributes['states']))

        # Call superclass
        NPC.tick(self)

        # Sprite modifier updates
        if ("poisoned" in self.attributes['states']):
            self.curSpriteModifiers.add("placeholder_sick")


        # Interpret any external states
        if ("poisoned" in self.attributes['states']):
            # If the agent is poisoned, then head for the infirmary
            # Remove the "wandering" state
            if ("wandering" in self.attributes['states']):
                self.removeState("wandering")
            # Head to the infirmary
            self.attributes["goalLocation"] = (23, 7)   # Infirmary entrance


        elif ("eatSignal" in self.attributes['states']):
            # TODO: Add the action sequence to go to the cafeteria and eat
            pass

    
        # Call the NPC's action interpreter
        #self.autopilotActionQueue = []                              # Queue of autopilot actions
        #self.pathfinder = Pathfinder()

        # Display autopilot action queue (debug)
        print(self.displayAutopilotQueueStr())

        # Get the NPC's current autopilot action
        if (len(self.autopilotActionQueue) > 0):            
            # Get the current autopilot action
            curAutopilotAction = self.autopilotActionQueue[0]
            # Call the action interpreter to run it
            print("(Agent: " + self.name + "): Calling action interpreter with action: " + str(curAutopilotAction))
            result = self.pathfinder.actionInterpreter(curAutopilotAction, agent=self, world=self.world)
            print("(Agent: " + self.name + "): Result of calling action interpreter: " + str(result))

            # If the result is "COMPLETED", then remove the action from the queue
            if (result == ActionResult.COMPLETED):
                self.autopilotActionQueue.remove(curAutopilotAction)
                print("(Agent: " + self.name + "): Action completed.  Removed from queue.")
            # If the result is "FAILURE", then remove the action from the queue
            elif (result == ActionResult.FAILURE):
                self.autopilotActionQueue.remove(curAutopilotAction)
                print("(Agent: " + self.name + "): Action failed.  Removed from queue.")
            # If the result is "INVALID", then remove the action from the queue
            elif (result == ActionResult.INVALID):
                self.autopilotActionQueue.remove(curAutopilotAction)
                print("(Agent: " + self.name + "): Action invalid.  Removed from queue.")
            
            # If the result is "success", then do nothing -- the action is still in progress.



class NPCChef1(NPC):
    # Constructor
    def __init__(self, world, name, tables=None, pot=None):
        # Default sprite name
        Agent.__init__(self, world, "agent", name, defaultSpriteName = "character17_agent_facing_south")

        ## DEBUG
        self.pot = pot
        self.tables = tables

        # Rendering
        self.attributes["faceDirection"] = "south"        
        self.spriteCharacterPrefix = "character15_"

        # # Add a default action into the action queue 
        # if (tables is not None) and (pot is not None):
        #     self.potParentContainer = pot.parentContainer

        #     # First, pick up the pot
        #     self.autopilotActionQueue.append( AutopilotAction_PickupObj(pot) )
        #     # Since the rest is dependent upon the pot's contents at pick-up time, the rest of the actions are added in tick()

    #
    #   Dialog Actions
    #
    # def actionDialog(self, agentDoingTalking, dialogStrToSay):

    #     # Step 1: Check if the agent has already spoken with this NPC
    #     if (agentDoingTalking.name in self.attributes['dialogAgentsSpokenWith']):
    #         # Agent has already spoken with this NPC
    #         return "I've already spoken with you."

    #     # Add the agent to the list of agents that this NPC has spoken with
    #     self.attributes['dialogAgentsSpokenWith'].append(agentDoingTalking.name)

    #     # If we reach here, the agent has not spoken with this NPC yet
    #     return "Hello, " + agentDoingTalking.name + ".  I am " + self.name + ".  Nice to meet you."    

    
    #
    #   Tick
    #
        
    # Tick
    def tick(self):
        # # Randomly move agent
        # if (random.random() < 0.1):
        #     # Randomly move the agent
        #     deltaX = random.randint(-1, 1)
        #     deltaY = random.randint(-1, 1)
        #     self.actionMoveAgent(deltaX, deltaY)

        # Stop if the object has already had tick() called this update -- this might have happened if the object moved locations in this current update cycle.
        if (self.tickCompleted):
            return

        # Debug
        print("NPC States (name: " + self.name + "): " + str(self.attributes['states']))

        # Call superclass
        NPC.tick(self)

        # Sprite modifier updates
        if ("poisoned" in self.attributes['states']):
            self.curSpriteModifiers.add("placeholder_sick")


        # Interpret any external states
        if ("poisoned" in self.attributes['states']):
            # If the agent is poisoned, then head for the infirmary
            # Remove the "wandering" state
            if ("wandering" in self.attributes['states']):
                self.removeState("wandering")
            # Head to the infirmary
            self.attributes["goalLocation"] = (23, 7)   # Infirmary entrance


        elif ("eatSignal" in self.attributes['states']):
            # TODO: Add the action sequence to go to the cafeteria and eat
            pass

    
        # Call the NPC's action interpreter
        #self.autopilotActionQueue = []                              # Queue of autopilot actions
        #self.pathfinder = Pathfinder()

        elif ("collectSignal" in self.attributes['states']):
            # Collect the mushrooms from the field
            # First, remove the collect signal
            self.removeState("collectSignal")

            self.actionDiscoveryFeedMakeUpdatePost("I'm going to the farm to collect mushrooms.", signals=[])

            # First, pick up the pot
            potContainer = self.pot.parentContainer
            self.addAutopilotActionToQueue( AutopilotAction_PickupObj(self.pot, priority=5) )

            # Then, pick up the mushrooms
            fieldX = 10
            fieldY = 13
            fieldWidth = 6
            fieldHeight = 5
            objectTypes = ["mushroom"]
            container = self.pot
            self.addAutopilotActionToQueue( AutopilotAction_PickupObjectsInArea(fieldX, fieldY, fieldWidth, fieldHeight, objectTypes, container, priority=5) )

            # Then, put the pot back down
            self.addAutopilotActionToQueue( AutopilotAction_PlaceObjInContainer(self.pot, potContainer, priority=5) )

            # Send a note to the discovery feed signifying the task is completed
            self.addAutopilotActionToQueue( AutopilotAction_PostDiscoveryFeedUpdate(contentStr="I'm going back to the cafeteria from the farm.", signals=[], priority=5) )

            # Then, travel back to your starting location
            self.addAutopilotActionToQueue( AutopilotAction_GotoXY(x=20, y=21, priority=5) )

        
        elif ("serveSignal" in self.attributes['states']):
            # Serve the food
            # First, remove the serve signal
            self.removeState("serveSignal")

            self.actionDiscoveryFeedMakeUpdatePost("I'm going to serve food in the cafeteria.", signals=[])

            # First, pick up the pot
            potContainer = self.pot.parentContainer
            self.addAutopilotActionToQueue( AutopilotAction_PickupObj(self.pot, priority=5) )

            # Then, for each edible item in the pot (up to 5), place it on a table
            potContents = self.pot.contents
            edibleContents = [x for x in potContents if x.attributes['isEdible']]
            for i in range(0, min(5, len(edibleContents))):
                self.addAutopilotActionToQueue( AutopilotAction_PlaceObjInContainer(edibleContents[i], self.tables[i], priority=5) )
            
            # Then, put the pot back down on the original table
            self.addAutopilotActionToQueue( AutopilotAction_PlaceObjInContainer(self.pot, potContainer, priority=5) )

            # Then, travel back to your starting location
            self.addAutopilotActionToQueue( AutopilotAction_GotoXY(x=20, y=21, priority=5) )                        


        # Run the autopilot action queue

        # Display autopilot action queue (debug)
        print(self.displayAutopilotQueueStr())

        # Get the NPC's current autopilot action
        if (len(self.autopilotActionQueue) > 0):
            # Get the current autopilot action
            curAutopilotAction = self.autopilotActionQueue[0]
            # Call the action interpreter to run it
            print("(Agent: " + self.name + "): Calling action interpreter with action: " + str(curAutopilotAction))
            result = self.pathfinder.actionInterpreter(curAutopilotAction, agent=self, world=self.world)
            print("(Agent: " + self.name + "): Result of calling action interpreter: " + str(result))

            # If the result is "COMPLETED", then remove the action from the queue
            if (result == ActionResult.COMPLETED):
                self.autopilotActionQueue.remove(curAutopilotAction)
                print("(Agent: " + self.name + "): Action completed.  Removed from queue.")
            # If the result is "FAILURE", then remove the action from the queue
            elif (result == ActionResult.FAILURE):
                self.autopilotActionQueue.remove(curAutopilotAction)
                print("(Agent: " + self.name + "): Action failed.  Removed from queue.")
            # If the result is "INVALID", then remove the action from the queue
            elif (result == ActionResult.INVALID):
                self.autopilotActionQueue.remove(curAutopilotAction)
                print("(Agent: " + self.name + "): Action invalid.  Removed from queue.")
            
            # If the result is "success", then do nothing -- the action is still in progress.
        # DEBUG: End of tick -- display the agent's current state
        print("NPC States (name: " + self.name + "): " + str(self.attributes))
        print("--------------------\n")



class NPCColonistAuto2(NPC):
    # Constructor
    def __init__(self, world, name):
        # Default sprite name
        Agent.__init__(self, world, "agent", name, defaultSpriteName = "character17_agent_facing_south")

        # Rendering
        self.attributes["faceDirection"] = "south"        
        self.spriteCharacterPrefix = "character17_"

        # # Add a default action into the action queue 
        # if (tables is not None) and (pot is not None):
        #     self.potParentContainer = pot.parentContainer

        #     # First, pick up the pot
        #     self.autopilotActionQueue.append( AutopilotAction_PickupObj(pot) )
        #     # Since the rest is dependent upon the pot's contents at pick-up time, the rest of the actions are added in tick()

        # Add default action (wandering), which has a low priority
        self.addAutopilotActionToQueue( AutopilotAction_Wander() )

    #
    #   Dialog Actions
    #
    # def actionDialog(self, agentDoingTalking, dialogStrToSay):

    #     # Step 1: Check if the agent has already spoken with this NPC
    #     if (agentDoingTalking.name in self.attributes['dialogAgentsSpokenWith']):
    #         # Agent has already spoken with this NPC
    #         return "I've already spoken with you."

    #     # Add the agent to the list of agents that this NPC has spoken with
    #     self.attributes['dialogAgentsSpokenWith'].append(agentDoingTalking.name)

    #     # If we reach here, the agent has not spoken with this NPC yet
    #     return "Hello, " + agentDoingTalking.name + ".  I am " + self.name + ".  Nice to meet you."    

    
    #
    #   Tick
    #
        
    # Tick
    def tick(self):
        # # Randomly move agent
        # if (random.random() < 0.1):
        #     # Randomly move the agent
        #     deltaX = random.randint(-1, 1)
        #     deltaY = random.randint(-1, 1)
        #     self.actionMoveAgent(deltaX, deltaY)

        # Stop if the object has already had tick() called this update -- this might have happened if the object moved locations in this current update cycle.
        if (self.tickCompleted):
            return

        # Debug
        print("NPC States (name: " + self.name + "): " + str(self.attributes['states']))

        # Call superclass
        NPC.tick(self)

        # Sprite modifier updates
        if ("poisoned" in self.attributes['states']):
            self.curSpriteModifiers.add("placeholder_sick")


        # Interpret any external states
        if ("poisoned" in self.attributes['states']):
            # If the agent is poisoned, then head for the infirmary

            # Add GOTO action to the autopilot queue
            self.addAutopilotActionToQueue( AutopilotAction_GotoXY(x=23, y=7, priority=100) )


        #elif ("eatSignal" in self.attributes['states']):
        #    # TODO: Add the action sequence to go to the cafeteria and eat
        #    pass

    
        # Call the NPC's action interpreter
        #self.autopilotActionQueue = []                              # Queue of autopilot actions
        #self.pathfinder = Pathfinder()

        elif ("eatSignal" in self.attributes['states']) or (("eatSignal_" + self.name) in self.attributes['states']):
            # Collect a single mushroom from the cafeteria tables

            # First, remove the collect signal
            self.removeState("eatSignal")
            self.removeState("eatSignal_" + self.name)

            self.actionDiscoveryFeedMakeUpdatePost("Heading to the cafeteria for some food.", signals=[])

            # First, record the agent's starting location
            agentStartingLocation = self.getWorldLocation()

            # First, travel to the cafeteria 
            self.addAutopilotActionToQueue( AutopilotAction_GotoXY(x=23, y=25, priority=5) )            

            # Then, pick up one mushroom
            fieldX = 21
            fieldY = 23
            fieldWidth = 5
            fieldHeight = 1
            objectTypes = ["mushroom"]
            container = self
            self.addAutopilotActionToQueue( AutopilotAction_PickupObjectsInArea(fieldX, fieldY, fieldWidth, fieldHeight, objectTypes, container, maxToTake=1, priority=5) )

            # Then, eat the object
            # Find the object in the agent's inventory            
            self.addAutopilotActionToQueue( AutopilotAction_EatObjectInInventory(objectNamesOrTypesToEat=["mushroom"], priority=5) )

            # Then, travel back to your starting location
            self.addAutopilotActionToQueue( AutopilotAction_GotoXY(x=agentStartingLocation[0], y=agentStartingLocation[1], priority=5) )            



        # Run the autopilot action queue

        # Display autopilot action queue (debug)
        print(self.displayAutopilotQueueStr())

        # Get the NPC's current autopilot action
        if (len(self.autopilotActionQueue) > 0):
            # Get the current autopilot action
            curAutopilotAction = self.autopilotActionQueue[0]
            # Call the action interpreter to run it
            print("(Agent: " + self.name + "): Calling action interpreter with action: " + str(curAutopilotAction))
            result = self.pathfinder.actionInterpreter(curAutopilotAction, agent=self, world=self.world)
            print("(Agent: " + self.name + "): Result of calling action interpreter: " + str(result))

            # If the result is "COMPLETED", then remove the action from the queue
            if (result == ActionResult.COMPLETED):
                self.autopilotActionQueue.remove(curAutopilotAction)
                print("(Agent: " + self.name + "): Action completed.  Removed from queue.")
            # If the result is "FAILURE", then remove the action from the queue
            elif (result == ActionResult.FAILURE):
                self.autopilotActionQueue.remove(curAutopilotAction)
                print("(Agent: " + self.name + "): Action failed.  Removed from queue.")
            # If the result is "INVALID", then remove the action from the queue
            elif (result == ActionResult.INVALID):
                self.autopilotActionQueue.remove(curAutopilotAction)
                print("(Agent: " + self.name + "): Action invalid.  Removed from queue.")
            
            # If the result is "success", then do nothing -- the action is still in progress.

        # DEBUG: End of tick -- display the agent's current state
        print("NPC States (name: " + self.name + "): " + str(self.attributes))

        print("--------------------\n")



class NPCFarmer1(NPC):
    # Constructor
    def __init__(self, world, name, tables=None, pot=None):
        # Default sprite name
        Agent.__init__(self, world, "agent", name, defaultSpriteName = "character17_agent_facing_south")

        ## DEBUG
        self.pot = pot
        self.tables = tables

        # Rendering
        self.attributes["faceDirection"] = "south"        
        self.spriteCharacterPrefix = "character15_"

        # # Add a default action into the action queue 
        # if (tables is not None) and (pot is not None):
        #     self.potParentContainer = pot.parentContainer

        #     # First, pick up the pot
        #     self.autopilotActionQueue.append( AutopilotAction_PickupObj(pot) )
        #     # Since the rest is dependent upon the pot's contents at pick-up time, the rest of the actions are added in tick()

    #
    #   Dialog Actions
    #
    # def actionDialog(self, agentDoingTalking, dialogStrToSay):

    #     # Step 1: Check if the agent has already spoken with this NPC
    #     if (agentDoingTalking.name in self.attributes['dialogAgentsSpokenWith']):
    #         # Agent has already spoken with this NPC
    #         return "I've already spoken with you."

    #     # Add the agent to the list of agents that this NPC has spoken with
    #     self.attributes['dialogAgentsSpokenWith'].append(agentDoingTalking.name)

    #     # If we reach here, the agent has not spoken with this NPC yet
    #     return "Hello, " + agentDoingTalking.name + ".  I am " + self.name + ".  Nice to meet you."    

    
    #
    #   Tick
    #
        
    # Tick
    def tick(self):
        # # Randomly move agent
        # if (random.random() < 0.1):
        #     # Randomly move the agent
        #     deltaX = random.randint(-1, 1)
        #     deltaY = random.randint(-1, 1)
        #     self.actionMoveAgent(deltaX, deltaY)

        # Stop if the object has already had tick() called this update -- this might have happened if the object moved locations in this current update cycle.
        if (self.tickCompleted):
            return

        # Debug
        print("NPC States (name: " + self.name + "): " + str(self.attributes['states']))

        # Call superclass
        NPC.tick(self)

        # Sprite modifier updates
        if ("poisoned" in self.attributes['states']):
            self.curSpriteModifiers.add("placeholder_sick")


        # Interpret any external states
        if ("poisoned" in self.attributes['states']):
            # If the agent is poisoned, then head for the infirmary
            # Remove the "wandering" state
            if ("wandering" in self.attributes['states']):
                self.removeState("wandering")
            # Head to the infirmary
            self.attributes["goalLocation"] = (23, 7)   # Infirmary entrance


        elif ("eatSignal" in self.attributes['states']):
            # TODO: Add the action sequence to go to the cafeteria and eat
            pass

    
        # Call the NPC's action interpreter
        #self.autopilotActionQueue = []                              # Queue of autopilot actions
        #self.pathfinder = Pathfinder()

        elif ("plantSignal" in self.attributes['states']):
            # Collect the mushrooms from the field
            # First, remove the collect signal
            self.removeState("plantSignal")

            numSeedsToPlant = 5
            self.actionDiscoveryFeedMakeUpdatePost("I'm going to try to plant some seeds.", signals=[])

            # First, pick up a shovel
            farmX = 10
            farmY = 8
            farmWidth = 6
            farmHeight = 5+5
            objectTypes = ["shovel"]
            container = self            
            self.addAutopilotActionToQueue( AutopilotAction_PickupObjectsInArea(farmX, farmY, farmWidth, farmHeight, objectTypes, container, maxToTake=1, priority=5) )
            #self.addAutopilotActionToQueue( AutopilotAction_PickupObj(self.pot, priority=5) )

            # Then, pick up some seeds
            objectTypes = ["seed"]
            self.addAutopilotActionToQueue( AutopilotAction_PickupObjectsInArea(farmX, farmY, farmWidth, farmHeight, objectTypes, container, maxToTake=numSeedsToPlant, priority=5) )

            # Then, pick 5 unoccupied spots in the field 
            # Then, go to each spot, dig the hole, plant the seed, and put dirt back in the hole
            tileTypesToFind = ["soil"]
            allowedContentTypes = ["dirt"]    
            for i in range(numSeedsToPlant):
                self.addAutopilotActionToQueue( AutopilotAction_LocateBlankTileInArea(farmX, farmY, farmWidth, farmHeight, tileTypesToFind, allowedContentTypes, priority=5) )
                self.addAutopilotActionToQueue( AutoPilotAction_BuryInFrontOfAgent(objectNamesOrTypesToDig=["soil"], objectNamesOrTypesToBury=["seed"], priority=5) )            

            # Then, return any remaining seeds to the container
            # TODO

            # Then, put the shovel back down
            self.addAutopilotActionToQueue( AutopilotAction_DropObjAtLocation(objectToPlace=None, dropX=12, dropY=9, objectNamesOrTypes=["shovel"], priority=5) )



            # Then, travel back to your starting location

            # fieldX = 10
            # fieldY = 13
            # fieldWidth = 6
            # fieldHeight = 5
            # objectTypes = ["mushroom"]
            # container = self.pot
            # self.addAutopilotActionToQueue( AutopilotAction_PickupObjectsInArea(fieldX, fieldY, fieldWidth, fieldHeight, objectTypes, container, priority=5) )

            # # Then, put the pot back down
            # self.addAutopilotActionToQueue( AutopilotAction_PlaceObjInContainer(self.pot, potContainer, priority=5) )

            # Then, travel back to your starting location
            self.addAutopilotActionToQueue( AutopilotAction_GotoXY(x=11, y=12, finalDirection="south", priority=5) )

        
        elif ("serveSignal" in self.attributes['states']):
            # # Serve the food
            # # First, remove the serve signal
            # self.removeState("serveSignal")

            # # First, pick up the pot
            # potContainer = self.pot.parentContainer
            # self.addAutopilotActionToQueue( AutopilotAction_PickupObj(self.pot, priority=5) )

            # # Then, for each edible item in the pot (up to 5), place it on a table
            # potContents = self.pot.contents
            # edibleContents = [x for x in potContents if x.attributes['isEdible']]
            # for i in range(0, min(5, len(edibleContents))):
            #     self.addAutopilotActionToQueue( AutopilotAction_PlaceObjInContainer(edibleContents[i], self.tables[i], priority=5) )
            
            # # Then, put the pot back down on the original table
            # self.addAutopilotActionToQueue( AutopilotAction_PlaceObjInContainer(self.pot, potContainer, priority=5) )

            # # Then, travel back to your starting location
            # self.addAutopilotActionToQueue( AutopilotAction_GotoXY(x=20, y=21, priority=5) )
            pass

        # Run the autopilot action queue

        # Display autopilot action queue (debug)
        print(self.displayAutopilotQueueStr())

        # Get the NPC's current autopilot action
        if (len(self.autopilotActionQueue) > 0):
            # Get the current autopilot action
            curAutopilotAction = self.autopilotActionQueue[0]
            # Call the action interpreter to run it
            print("(Agent: " + self.name + "): Calling action interpreter with action: " + str(curAutopilotAction))
            result = self.pathfinder.actionInterpreter(curAutopilotAction, agent=self, world=self.world)
            print("(Agent: " + self.name + "): Result of calling action interpreter: " + str(result))

            # If the result is "COMPLETED", then remove the action from the queue
            if (result == ActionResult.COMPLETED):
                self.autopilotActionQueue.remove(curAutopilotAction)
                print("(Agent: " + self.name + "): Action completed.  Removed from queue.")
            # If the result is "FAILURE", then remove the action from the queue
            elif (result == ActionResult.FAILURE):
                self.autopilotActionQueue.remove(curAutopilotAction)
                print("(Agent: " + self.name + "): Action failed.  Removed from queue.")
            # If the result is "INVALID", then remove the action from the queue
            elif (result == ActionResult.INVALID):
                self.autopilotActionQueue.remove(curAutopilotAction)
                print("(Agent: " + self.name + "): Action invalid.  Removed from queue.")
            
            # If the result is "success", then do nothing -- the action is still in progress.
        # DEBUG: End of tick -- display the agent's current state
        print("NPC States (name: " + self.name + "): " + str(self.attributes))
        print("--------------------\n")



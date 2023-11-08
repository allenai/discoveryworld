# Agent.py

import SpriteLibrary
import random
from ObjectModel import *
from Layer import * 
from ActionSuccess import *
from Pathfinding import *

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

        # Dialog attributes
        self.attributes['isDialogable'] = True                     # Can it be dialoged with?

        # Door opening/closing for NPCs
        self.attributes["doorNeedsToBeClosed"] = None              # Whether a door was recently opened that needs to be closed
        self.attributes["movesSinceDoorOpen"] = 0                  # How many moves have happened since the door was opened

        # Signals (largely for NPCs)
        self.attributes["states"] = set()                          # External signals that the agent has received

        # Health attributes
        self.attributes["poisonedCounter"] = -1                    # Poisoned counter (if >= 0, then the agent is poisoned)
        

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
            elif (self.attributes['poisonedCounter'] > -1):
                # Poisoned and actively affecting the agent
                self.attributes['states'].add('poisoned')
                print("Agent " + self.name + ": I don't feel very well!")
        else:
            # Remove state of 'poisoned' from the agent
            if ('poisoned' in self.attributes['states']):
                self.attributes['states'].remove('poisoned')



    #
    #   Actions
    #

    # Attempt to move the agent in a particular direction.  deltaX and deltaY are in world coordinates, and should nominally be (-1, 0, 1)
    def actionMoveAgent(self, deltaX:int, deltaY:int):
        # Get the current location
        newX = self.attributes["gridX"] + deltaX
        newY = self.attributes["gridY"] + deltaY

        # Update the last direction the agent was facing (we do this even if the move wasn't valid, to give some visual feedback to the user)
        if (deltaX < 0):
            self.attributes["faceDirection"] = "west"
        elif (deltaX > 0):
            self.attributes["faceDirection"] = "east"
        elif (deltaY < 0):
            self.attributes["faceDirection"] = "north"
        elif (deltaY > 0):
            self.attributes["faceDirection"] = "south"
        else:
            # This should generally not happen -- the agent is not moving.  Still, default to south.
            self.attributes["faceDirection"] = "south"

        # Invalidate the sprite name
        self.needsSpriteNameUpdate = True

        # Check if the new location is valid
        # Check 1: Is the new location within the bounds of the world?        
        if (newX < 0 or newX >= self.world.sizeX or newY < 0 or newY >= self.world.sizeY):
            # Invalid location
            return ActionSuccess(False, "That would take me beyond the edge of the world.")

        # Check 2: Check if the new location is passable
        isPassable, blockingObject = self.world.isPassable(newX, newY)
        if (not isPassable):            
            return ActionSuccess(False, "I can't move there. There is something in the way (" + blockingObject.name + ").")

        # If we reach here, the new location is valid. Update the agent's location to the new location
        self.world.removeObject(self)                           # First, remove the object from it's current location in the world grid
        self.world.addObject(newX, newY, Layer.AGENT, self)     # Then, add the object to the new location in the world grid

        return ActionSuccess(True, "I moved to (" + str(newX) + ", " + str(newY) + ").")

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

        return ActionSuccess(True, "I rotated to face " + newDirection + ".")

    # Move forward (or backward) in the direction the agent is facing
    # Direction: +1 = forward, -1 = backward
    def actionMoveAgentForwardBackward(self, direction=+1):
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
            return ActionSuccess(False, "That would take me beyond the edge of the world.")
        
        # Check 2: Check if the new location is passable
        isPassable, blockingObject = self.world.isPassable(newX, newY)
        if (not isPassable):
            return ActionSuccess(False, "I can't move there. There is something in the way (" + blockingObject.name + ").")

        # If we reach here, the new location is valid. Update the agent's location to the new location
        self.world.removeObject(self)                           # First, remove the object from it's current location in the world grid
        self.world.addObject(newX, newY, Layer.AGENT, self)     # Then, add the object to the new location in the world grid

        # Invalidate sprite name
        self.needsSpriteNameUpdate = True

        return ActionSuccess(True, "I moved to (" + str(newX) + ", " + str(newY) + ").")



    # Pick up an object, and add it to the agent's inventory
    def actionPickUp(self, objToPickUp):
        # First, check if the object is movable
        if (not objToPickUp.attributes["isMovable"]):
            # Object is not movable
            return ActionSuccess(False, "That object (" + objToPickUp.name + ") is not movable.")

        # Next, check if the object is within reach (i.e. +/- 1 grid location)
        distX = abs(objToPickUp.attributes["gridX"] - self.attributes["gridX"])
        distY = abs(objToPickUp.attributes["gridY"] - self.attributes["gridY"])
        if (distX > 1 or distY > 1):
            # Object is not within reach
            return ActionSuccess(False, "That object (" + objToPickUp.name + ") is not within reach. I can only pick up objects that are within +/- 1 grid location.")


        # If we reach here, the object is movable and within reach.  Pick it up.
        objToPickUp.invalidateSpritesThisWorldTile()            # Invalidate the sprites at the object's current location
        self.world.removeObject(objToPickUp)                    # Remove the object from the world
        self.addObject(objToPickUp)                             # Add the object to the agent's inventory

        return ActionSuccess(True, "I picked up the " + objToPickUp.name + ".")


    # Drop an object from the agent's inventory at the agent's current location
    def actionDrop(self, objToDrop):
        # First, check if the object is in the agent's inventory
        objectsInInventory = self.getAllContainedObjectsRecursive(respectContainerStatus=True)
        print("OBJECTS IN INVENTORY: " + str(objectsInInventory))
        if (not objToDrop in objectsInInventory):
            # Object is not in the agent's inventory
            return ActionSuccess(False, "That object (" + objToDrop.name + ") is not in my inventory.")

        # Next, drop the object at the agent's current location.
        # (Note: adding the item to a specific location should remove it from the agent's inventory)
        self.world.addObject(self.attributes["gridX"], self.attributes["gridY"], Layer.OBJECTS, objToDrop)

        # Invalidate the sprites at the object's new location
        objToDrop.invalidateSpritesThisWorldTile()

        return ActionSuccess(True, "I dropped the " + objToDrop.name + ".")

    def actionPut(self, objToPut, newContainer):
        # First, check if the object is in the agent's inventory
        objectsInInventory = self.getAllContainedObjectsRecursive(respectContainerStatus=True)
        if (not objToPut in objectsInInventory):
            # Object is not in the agent's inventory
            return ActionSuccess(False, "That object (" + objToPut.name + ") is not in my inventory.")

        # Next, check if the new container is within reach (i.e. +/- 1 grid location)
        distX = abs(newContainer.attributes["gridX"] - self.attributes["gridX"])
        distY = abs(newContainer.attributes["gridY"] - self.attributes["gridY"])
        if (distX > 1 or distY > 1):
            # Container is not within reach
            return ActionSuccess(False, "That container (" + newContainer.name + ") is not within reach. I can only put objects into containers that are within +/- 1 grid location.")

        # Next, check to see if the container is a container
        if (not newContainer.attributes["isContainer"]):
            # Container is not a container
            return ActionSuccess(False, "That object (" + newContainer.name + ") is not a container.")

        # Next, check to see if the container is open
        if (not newContainer.attributes["isOpenContainer"]):
            # Container is not open
            return ActionSuccess(False, "That container (" + newContainer.name + ") is not open.")

        # If we reach here, the object is in the agent's inventory, the container is within reach, and the container is open.
        # Put the object into the container.
        if (objToPut.parentContainer != None):
            objToPut.parentContainer.invalidateSpritesThisWorldTile()
        newContainer.addObject(objToPut)
        objToPut.invalidateSpritesThisWorldTile()
        newContainer.invalidateSpritesThisWorldTile()

        return ActionSuccess(True, "I put the " + objToPut.name + " into the " + newContainer.name + ".")

    # Open or close an object
    # 'whichAction' should be "open" or "close"
    def actionOpenClose(self, objToOpenOrClose, whichAction="open"):
        # First, check if the object is within reach (i.e. +/- 1 grid location)
        distX = abs(objToOpenOrClose.attributes["gridX"] - self.attributes["gridX"])
        distY = abs(objToOpenOrClose.attributes["gridY"] - self.attributes["gridY"])
        if (distX > 1 or distY > 1):
            # Object is not within reach
            return ActionSuccess(False, "That object (" + objToOpenOrClose.name + ") is not within reach. I can only open/close objects that are within +/- 1 grid location.")

        # Next, check if the object is openable
        if (not objToOpenOrClose.attributes["isOpenable"]):
            # Object is not openable
            return ActionSuccess(False, "That object (" + objToOpenOrClose.name + ") is not openable/closeable.")
        
        # Next, check to see whether we're dealing with a container or a passage
        if (objToOpenOrClose.attributes["isContainer"]):
            # Open a container
            # Next, check if the object is already in the desired state
            if (whichAction == "open" and objToOpenOrClose.attributes["isOpenContainer"]):
                # Object is already open
                return ActionSuccess(False, "That object (" + objToOpenOrClose.name + ") is already open.")
            elif (whichAction == "close" and not objToOpenOrClose.attributes["isOpenContainer"]):
                # Object is already closed
                return ActionSuccess(False, "That object (" + objToOpenOrClose.name + ") is already closed.")

            # If we reach here, the object is within reach and is openable.  Open/close it.
            if (whichAction == "open"):
                objToOpenOrClose.attributes["isOpenContainer"] = True
                objToOpenOrClose.invalidateSpritesThisWorldTile()
                return ActionSuccess(True, "I opened the " + objToOpenOrClose.name + ".")
            else:
                objToOpenOrClose.attributes["isOpenContainer"] = False
                objToOpenOrClose.invalidateSpritesThisWorldTile()
                return ActionSuccess(True, "I closed the " + objToOpenOrClose.name + ".")

        elif (objToOpenOrClose.attributes["isPassage"]):
            # Open a passage
            # Next, check if the object is already in the desired state
            if (whichAction == "open" and objToOpenOrClose.attributes["isOpenPassage"]):
                # Object is already open
                return ActionSuccess(False, "That object (" + objToOpenOrClose.name + ") is already open.")
            elif (whichAction == "close" and not objToOpenOrClose.attributes["isOpenPassage"]):
                # Object is already closed
                return ActionSuccess(False, "That object (" + objToOpenOrClose.name + ") is already closed.")

            # If we reach here, the object is within reach and is openable.  Open/close it.
            if (whichAction == "open"):
                objToOpenOrClose.attributes["isOpenPassage"] = True
                objToOpenOrClose.invalidateSpritesThisWorldTile()
                return ActionSuccess(True, "I opened the " + objToOpenOrClose.name + ".")
            else:
                objToOpenOrClose.attributes["isOpenPassage"] = False
                objToOpenOrClose.invalidateSpritesThisWorldTile()
                return ActionSuccess(True, "I closed the " + objToOpenOrClose.name + ".")


    # Activate/Deactivate an object
    # 'whichAction' should be "activate" or "deactivate"
    def actionActivateDeactivate(self, objToActivateOrDeactivate, whichAction="activate"):
        # First, check if the object is within reach (i.e. +/- 1 grid location)
        distX = abs(objToActivateOrDeactivate.attributes["gridX"] - self.attributes["gridX"])
        distY = abs(objToActivateOrDeactivate.attributes["gridY"] - self.attributes["gridY"])
        if (distX > 1 or distY > 1):
            # Object is not within reach
            return ActionSuccess(False, "That object (" + objToActivateOrDeactivate.name + ") is not within reach. I can only activate/deactivate objects that are within +/- 1 grid location.")

        # Next, check if the object is activatable
        if (not objToActivateOrDeactivate.attributes["isActivatable"]):
            # Object is not activatable
            return ActionSuccess(False, "That object (" + objToActivateOrDeactivate.name + ") is not activatable/deactivatable.")
                
        # Next, check if the object is already in the desired state
        if (whichAction == "activate" and objToActivateOrDeactivate.attributes["isActivated"]):
            # Object is already activated
            return ActionSuccess(False, "That object (" + objToActivateOrDeactivate.name + ") is already activated.")
        elif (whichAction == "deactivate" and not objToActivateOrDeactivate.attributes["isActivated"]):
            # Object is already deactivated
            return ActionSuccess(False, "That object (" + objToActivateOrDeactivate.name + ") is already deactivated.")
        
        # If we reach here, the object is within reach and is activatable.  Activate/deactivate it.
        if (whichAction == "activate"):
            objToActivateOrDeactivate.attributes["isActivated"] = True
            objToActivateOrDeactivate.invalidateSpritesThisWorldTile()
            return ActionSuccess(True, "I activated the " + objToActivateOrDeactivate.name + ".")
        else:
            objToActivateOrDeactivate.attributes["isActivated"] = False
            objToActivateOrDeactivate.invalidateSpritesThisWorldTile()
            return ActionSuccess(True, "I deactivated the " + objToActivateOrDeactivate.name + ".")
            

    # Eat an object
    def actionEat(self, objToEat):
        # First, check if the object is edible
        if (not objToEat.attributes["isEdible"]):
            # Object is not movable
            return ActionSuccess(False, "That object (" + objToEat.name + ") is not edible.")

        # Next, check if the object is within reach (i.e. +/- 1 grid location)
        distX = abs(objToEat.attributes["gridX"] - self.attributes["gridX"])
        distY = abs(objToEat.attributes["gridY"] - self.attributes["gridY"])
        if (distX > 1 or distY > 1):
            # Object is not within reach
            return ActionSuccess(False, "That object (" + objToEat.name + ") is not within reach. I can only eat objects that are within +/- 1 grid location.")


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
        


        return ActionSuccess(True, "I ate the " + objToEat.name + ".")


    # Read an object
    def actionRead(self, objToRead):
        # First, check if the object to read is within reach (i.e. +/- 1 grid location)
        distX = abs(objToRead.attributes["gridX"] - self.attributes["gridX"])
        distY = abs(objToRead.attributes["gridY"] - self.attributes["gridY"])
        if (distX > 1 or distY > 1):
            # Object is not within reach
            return ActionSuccess(False, "That object (" + objToRead.name + ") is not within reach. I can only read objects that are within +/- 1 grid location.")

        # Next, check if the object to read is readable
        if (not objToRead.attributes["isReadable"]):
            # Object is not readable
            return ActionSuccess(False, "That object (" + objToRead.name + ") is not readable.")

        # If we reach here, the object is within reach and is readable.  Read it.
        # Check if the object is blank (i.e. document length is zero)
        if (len(objToRead.attributes["document"].strip()) == 0):
            # Object is blank
            return ActionSuccess(False, "The " + objToRead.name + " appears blank. There is nothing to read.", MessageImportance.HIGH)
        else:
            # Object is not blank
            return ActionSuccess(True, "The " + objToRead.name + " reads:\n" + objToRead.attributes["document"], MessageImportance.HIGH)


    # Use an object on another object
    def actionUse(self, objToUse, objToUseOn):
        # First, check if the object to use is within reach (i.e. +/- 1 grid location)
        distX = abs(objToUse.attributes["gridX"] - self.attributes["gridX"])
        distY = abs(objToUse.attributes["gridY"] - self.attributes["gridY"])
        if (distX > 1 or distY > 1):
            # Object is not within reach
            return ActionSuccess(False, "That object (" + objToUse.name + ") is not within reach. I can only use objects that are within +/- 1 grid location.")

        # Next, check if the object to use is usable
        if (not objToUse.attributes["isUsable"]):
            # Object is not usable
            return ActionSuccess(False, "That object (" + objToUse.name + ") is not usable.")

        # Next, check if the patient object is within reach (i.e. +/- 1 grid location)
        distX = abs(objToUseOn.attributes["gridX"] - self.attributes["gridX"])
        distY = abs(objToUseOn.attributes["gridY"] - self.attributes["gridY"])
        if (distX > 1 or distY > 1):
            # Object is not within reach
            return ActionSuccess(False, "That object (" + objToUseOn.name + ") is not within reach. I can only use objects on other objects that are within +/- 1 grid location.")

        # If we reach here, the object is usable, and both the device and patient object are within reach. Use it. 
        result = objToUse.actionUseWith(objToUseOn)

        # If there is a .generatedItems populated in this result, then process it            
        if ('generatedItems' in result.data):
            for item in result.data['generatedItems']:
                self.addObject(item)


        # Invalidate the sprites of all objects at these locations. 
        objToUse.invalidateSpritesThisWorldTile()
        objToUseOn.invalidateSpritesThisWorldTile()

        # Return result
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
    def actionDialog(self, agentDoingTalking, dialogStrToSay):
        return "Dialog placeholder"

    #
    # Sprite
    #

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
    def actionDialog(self, agentDoingTalking, dialogStrToSay):

        # Step 1: Check if the agent has already spoken with this NPC
        if (agentDoingTalking.name in self.attributes['dialogAgentsSpokenWith']):
            # Agent has already spoken with this NPC
            return "I've already spoken with you."

        # Add the agent to the list of agents that this NPC has spoken with
        self.attributes['dialogAgentsSpokenWith'].append(agentDoingTalking.name)

        # If we reach here, the agent has not spoken with this NPC yet
        return "Hello, " + agentDoingTalking.name + ".  I am " + self.name + ".  Nice to meet you."


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
    def actionDialog(self, agentDoingTalking, dialogStrToSay):

        # Step 1: Check if the agent has already spoken with this NPC
        if (agentDoingTalking.name in self.attributes['dialogAgentsSpokenWith']):
            # Agent has already spoken with this NPC
            return "I've already spoken with you."

        # Add the agent to the list of agents that this NPC has spoken with
        self.attributes['dialogAgentsSpokenWith'].append(agentDoingTalking.name)

        # If we reach here, the agent has not spoken with this NPC yet
        return "Hello, " + agentDoingTalking.name + ".  I am " + self.name + ".  Nice to meet you."


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
                self.attributes['states'].remove("wandering")
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
            self.attributes['states'].remove("putPotBack")
            # Add "moveToInitialLocation" to state
            self.attributes['states'].add("moveToInitialLocation")
            # Remove 'foodContainer' attribute
            del self.attributes['foodContainer']


        elif ("serveDinner" in self.attributes['states']):
            # Remove the "waiting" state
            if ("waiting" in self.attributes['states']):
                self.attributes['states'].remove("waiting")
            # Head to the cafeteria kitchen, beside the table with the pot
            self.attributes["goalLocation"] = (21, 21)
            # remove "eatSignal" from external signals
            self.attributes['states'].remove("serveDinner")
            # Add "movingToCafeteria" to external signals
            self.attributes['states'].add("pickupFoodFromCafeteria")

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
                self.attributes['states'].remove("takePotFromCafeteria")
                # Add "eating" to external signals
                self.attributes['states'].add("serveFood")
                self.attributes['states'].add("moveToSpot1")

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
                    self.attributes['states'].remove("putFoodAtSpot1")
                    self.attributes['states'].add("moveToSpot2")
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
                    self.attributes['states'].remove("putFoodAtSpot2")
                    self.attributes['states'].add("moveToSpot3")
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
                    self.attributes['states'].remove("putFoodAtSpot3")
                    self.attributes['states'].add("moveToSpot4")
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
                    self.attributes['states'].remove("putFoodAtSpot4")
                    self.attributes['states'].add("moveToSpot5")
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
                    self.attributes['states'].remove("putFoodAtSpot5")
                    self.attributes['states'].add("moveToPutPotPack")
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
        #         self.attributes['states'].remove("eating")
        #         # Add "wandering" to external signals
        #         self.attributes['states'].add("wandering")
        #         # Remove "objectToEat" attribute
        #         del self.attributes["objectToEat"]

        else:
            # Default behavior, if no other behaviors are present, is to wander
            if ("waiting" not in self.attributes['states']):
                self.attributes['states'].add("waiting")


        # Pathfinding/Auto-navigation        
        if ("goalLocation" in self.attributes):
            success = self._doNPCAutonavigation()
            if (not success):
                # If we're in the "pickupFoodFromCafeteria" state, check to see if we're already in the goal location
                if ("pickupFoodFromCafeteria" in self.attributes['states']):
                    if (self.attributes["gridX"] == self.attributes["goalLocation"][0]) and (self.attributes["gridY"] == self.attributes["goalLocation"][1]):
                        # We're in the kitchen at the pot -- pick it up
                        self.attributes['states'].remove("pickupFoodFromCafeteria")
                        self.attributes['states'].add("takePotFromCafeteria")
                        # Remove the goal location
                        del self.attributes["goalLocation"]
                elif ("moveToInitialLocation" in self.attributes['states']):
                    # Check to see if we've moved to the initial location
                    if (self.attributes["gridX"] == self.attributes["goalLocation"][0]) and (self.attributes["gridY"] == self.attributes["goalLocation"][1]):
                        # We're in the kitchen at the pot -- pick it up
                        self.attributes['states'].remove("moveToInitialLocation")
                        self.attributes['states'].add("TODO")
                        # Remove the goal location
                        del self.attributes["goalLocation"]
                elif ("moveToPutPotPack" in self.attributes['states']):
                    # Check to see if we've moved to the initial location
                    if (self.attributes["gridX"] == self.attributes["goalLocation"][0]) and (self.attributes["gridY"] == self.attributes["goalLocation"][1]):
                        # We're in the kitchen at the pot -- pick it up
                        self.attributes['states'].remove("moveToPutPotPack")
                        self.attributes['states'].add("putPotBack")
                        # Remove the goal location
                        del self.attributes["goalLocation"]

                elif ("serveFood" in self.attributes['states']):
                    if (self.attributes["gridX"] == self.attributes["goalLocation"][0]) and (self.attributes["gridY"] == self.attributes["goalLocation"][1]):
                        # We're in the kitchen at the pot -- pick it up
                        #self.attributes['states'].remove("serveFood")
                        if ("moveToSpot1" in self.attributes['states']):
                            self.attributes['states'].remove("moveToSpot1")
                            self.attributes['states'].add("putFoodAtSpot1")
                            del self.attributes["goalLocation"]
                        elif ("moveToSpot2" in self.attributes['states']):
                            self.attributes['states'].remove("moveToSpot2")
                            self.attributes['states'].add("putFoodAtSpot2")
                            del self.attributes["goalLocation"]
                        elif ("moveToSpot3" in self.attributes['states']):
                            self.attributes['states'].remove("moveToSpot3")
                            self.attributes['states'].add("putFoodAtSpot3")
                            del self.attributes["goalLocation"]
                        elif ("moveToSpot4" in self.attributes['states']):
                            self.attributes['states'].remove("moveToSpot4")
                            self.attributes['states'].add("putFoodAtSpot4")
                            del self.attributes["goalLocation"]
                        elif ("moveToSpot5" in self.attributes['states']):
                            self.attributes['states'].remove("moveToSpot5")
                            self.attributes['states'].add("putFoodAtSpot5")
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
    def actionDialog(self, agentDoingTalking, dialogStrToSay):

        # Step 1: Check if the agent has already spoken with this NPC
        if (agentDoingTalking.name in self.attributes['dialogAgentsSpokenWith']):
            # Agent has already spoken with this NPC
            return "I've already spoken with you."

        # Add the agent to the list of agents that this NPC has spoken with
        self.attributes['dialogAgentsSpokenWith'].append(agentDoingTalking.name)

        # If we reach here, the agent has not spoken with this NPC yet
        return "Hello, " + agentDoingTalking.name + ".  I am " + self.name + ".  Nice to meet you."    

    
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
                self.attributes['states'].remove("wandering")
            # Head to the infirmary
            self.attributes["goalLocation"] = (23, 7)   # Infirmary entrance


        elif ("eatSignal" in self.attributes['states']):
            # Remove the "wandering" state
            if ("wandering" in self.attributes['states']):
                self.attributes['states'].remove("wandering")
            # Head to the cafeteria
            self.attributes["goalLocation"] = (23, 24)
            # remove "eatSignal" from external signals
            self.attributes['states'].remove("eatSignal")
            # Add "movingToCafeteria" to external signals
            self.attributes['states'].add("movingToCafeteria")

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
                self.attributes['states'].remove("takeFoodFromCafeteria")
                # Add "eating" to external signals
                self.attributes['states'].add("eating")

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
                self.attributes['states'].remove("eating")
                # Add "wandering" to external signals
                self.attributes['states'].add("wandering")
                # Remove "objectToEat" attribute
                del self.attributes["objectToEat"]

        else:
            # Default behavior, if no other behaviors are present, is to wander
            if ("wandering" not in self.attributes['states']):
                self.attributes['states'].add("wandering")


        # Pathfinding/Auto-navigation        
        if ("goalLocation" in self.attributes):
            success = self._doNPCAutonavigation()
            if (not success):
                # If we're in the "movingToCafeteria" state, check to see if we're already in the goal location
                if ("movingToCafeteria" in self.attributes['states']):
                    if (self.attributes["gridX"] == self.attributes["goalLocation"][0]) and (self.attributes["gridY"] == self.attributes["goalLocation"][1]):
                        # We're in the cafeteria -- eat!
                        self.attributes['states'].remove("movingToCafeteria")
                        self.attributes['states'].add("takeFoodFromCafeteria")
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
    def actionDialog(self, agentDoingTalking, dialogStrToSay):

        # Step 1: Check if the agent has already spoken with this NPC
        if (agentDoingTalking.name in self.attributes['dialogAgentsSpokenWith']):
            # Agent has already spoken with this NPC
            return "I've already spoken with you."

        # Add the agent to the list of agents that this NPC has spoken with
        self.attributes['dialogAgentsSpokenWith'].append(agentDoingTalking.name)

        # If we reach here, the agent has not spoken with this NPC yet
        return "Hello, " + agentDoingTalking.name + ".  I am " + self.name + ".  Nice to meet you."    

    
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
                self.attributes['states'].remove("wandering")
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
    def actionDialog(self, agentDoingTalking, dialogStrToSay):

        # Step 1: Check if the agent has already spoken with this NPC
        if (agentDoingTalking.name in self.attributes['dialogAgentsSpokenWith']):
            # Agent has already spoken with this NPC
            return "I've already spoken with you."

        # Add the agent to the list of agents that this NPC has spoken with
        self.attributes['dialogAgentsSpokenWith'].append(agentDoingTalking.name)

        # If we reach here, the agent has not spoken with this NPC yet
        return "Hello, " + agentDoingTalking.name + ".  I am " + self.name + ".  Nice to meet you."    

    
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
                self.attributes['states'].remove("wandering")
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
            self.attributes['states'].remove("collectSignal")

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

            # Then, travel back to your starting location
            self.addAutopilotActionToQueue( AutopilotAction_GotoXY(x=20, y=21, priority=5) )

        
        elif ("serveSignal" in self.attributes['states']):
            # Serve the food
            # First, remove the serve signal
            self.attributes['states'].remove("serveSignal")

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
    def actionDialog(self, agentDoingTalking, dialogStrToSay):

        # Step 1: Check if the agent has already spoken with this NPC
        if (agentDoingTalking.name in self.attributes['dialogAgentsSpokenWith']):
            # Agent has already spoken with this NPC
            return "I've already spoken with you."

        # Add the agent to the list of agents that this NPC has spoken with
        self.attributes['dialogAgentsSpokenWith'].append(agentDoingTalking.name)

        # If we reach here, the agent has not spoken with this NPC yet
        return "Hello, " + agentDoingTalking.name + ".  I am " + self.name + ".  Nice to meet you."    

    
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

        elif ("eatSignal" in self.attributes['states']):
            # Collect a single mushroom from the cafeteria tables

            # First, remove the collect signal
            self.attributes['states'].remove("eatSignal")

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
    def actionDialog(self, agentDoingTalking, dialogStrToSay):

        # Step 1: Check if the agent has already spoken with this NPC
        if (agentDoingTalking.name in self.attributes['dialogAgentsSpokenWith']):
            # Agent has already spoken with this NPC
            return "I've already spoken with you."

        # Add the agent to the list of agents that this NPC has spoken with
        self.attributes['dialogAgentsSpokenWith'].append(agentDoingTalking.name)

        # If we reach here, the agent has not spoken with this NPC yet
        return "Hello, " + agentDoingTalking.name + ".  I am " + self.name + ".  Nice to meet you."    

    
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
                self.attributes['states'].remove("wandering")
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
            self.attributes['states'].remove("plantSignal")

            numSeedsToPlant = 5

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
            # self.attributes['states'].remove("serveSignal")

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



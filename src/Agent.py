# Agent.py

import SpriteLibrary
import random
from ObjectModel import *
from Layer import * 
from ActionSuccess import *

#
#   Agent (controlled by a user or model)
#
class Agent(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "agent", "agent", defaultSpriteName = "character18_agent_facing_south")
    
        # Rendering
        self.attributes["faceDirection"] = "south"        
        self.spriteCharacterPrefix = "character18_"                 # Prefix for the sprite character name (e.g. "character18_")

        # Default attributes
        self.attributes["isMovable"] = False                       # Can it be moved?

        # Agent is a container for its inventory
        # Container attributes
        self.attributes['isContainer'] = True                      # Is it a container?
        self.attributes['isOpenable'] = False                      # Can be opened
        self.attributes['isOpenContainer'] = False                 # If it's a container, then is it open?
        self.attributes['containerPrefix'] = "in"                  # Container prefix (e.g. "in" or "on")            


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

        # Call superclass
        Object.tick(self)



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
            return ActionSuccess(False, "That is too far to move in a single step.  I can only move one step north, south, east, or west at a time.")

        # Check 2: Check if the new location is passable
        isPassable, blockingObject = self.world.isPassable(newX, newY)
        if (not isPassable):            
            return ActionSuccess(False, "I can't move there. There is something in the way (" + blockingObject.name + ").")

        # If we reach here, the new location is valid. Update the agent's location to the new location
        self.world.removeObject(self)                           # First, remove the object from it's current location in the world grid
        self.world.addObject(newX, newY, Layer.AGENT, self)     # Then, add the object to the new location in the world grid

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
        if (not objToDrop in self.contents):
            # Object is not in the agent's inventory
            return ActionSuccess(False, "That object (" + objToDrop.name + ") is not in my inventory.")

        # Next, drop the object at the agent's current location.
        # (Note: adding the item to a specific location should remove it from the agent's inventory)
        self.world.addObject(self.attributes["gridX"], self.attributes["gridY"], Layer.OBJECTS, objToDrop)

    def actionPut(self, objToPut, newContainer):
        # First, check if the object is in the agent's inventory
        if (not objToPut in self.contents):
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
        Object.__init__(self, world, "agent", name, defaultSpriteName = "character17_agent_facing_south")
    
        # Rendering
        self.attributes["faceDirection"] = "south"        
        self.spriteCharacterPrefix = "character17_"

        # Default attributes
        self.attributes["isMovable"] = False                       # Can it be moved?

        # Agent is a container for its inventory
        # Container attributes
        self.attributes['isContainer'] = True                      # Is it a container?
        self.attributes['isOpenable'] = False                      # Can be opened
        self.attributes['isOpenContainer'] = False                 # If it's a container, then is it open?
        self.attributes['containerPrefix'] = "in"                  # Container prefix (e.g. "in" or "on")            
    

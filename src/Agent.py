# Agent.py

import SpriteLibrary
import random
from ObjectModel import *
from Layer import * 


#
#   Object: Fence
#
class Agent(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "agent", "agent", defaultSpriteName = "character18_agent_facing_south")
    
        # Rendering
        self.attributes["faceDirection"] = "south"        

        # Agent is a container for its inventory
        # Container attributes
        self.attributes['isContainer'] = True                      # Is it a container?
        self.attributes['isOpenable'] = False                      # Can be opened
        self.attributes['isOpenContainer'] = False                 # If it's a container, then is it open?
        self.attributes['containerPrefix'] = "in"                  # Container prefix (e.g. "in" or "on")            



    # Attempt to move the agent in a particular direction.  deltaX and deltaY are in world coordinates, and should nominally be (-1, 0, 1)
    def moveAgent(self, deltaX:int, deltaY:int):
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
            return False

        # Check 2: Check if the new location is passable
        if (not self.world.isPassable(newX, newY)):            
            return False

        # If we reach here, the new location is valid. Update the agent's location to the new location
        self.world.removeObject(self)                           # First, remove the object from it's current location in the world grid
        self.world.addObject(newX, newY, Layer.AGENT, self)     # Then, add the object to the new location in the world grid


        return True
        
        

    def tick(self):
        # # Randomly move agent
        # if (random.random() < 0.1):
        #     # Randomly move the agent
        #     deltaX = random.randint(-1, 1)
        #     deltaY = random.randint(-1, 1)
        #     self.moveAgent(deltaX, deltaY)

        # Call superclass
        Object.tick(self)



    # Sprite
    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return

        # Change the sprite based on the direction the agent is facing
        if (self.attributes["faceDirection"] == "north"):
            self.curSpriteName = "character18_agent_facing_north"
        elif (self.attributes["faceDirection"] == "south"):
            self.curSpriteName = "character18_agent_facing_south"
        elif (self.attributes["faceDirection"] == "east"):
            self.curSpriteName = "character18_agent_facing_east"
        elif (self.attributes["faceDirection"] == "west"):
            self.curSpriteName = "character18_agent_facing_west"
        else:
            # Unknown direction -- this should never happen.  Default to south.
            self.curSpriteName = "character18_agent_facing_south"

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName
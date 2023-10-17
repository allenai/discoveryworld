# ObjectModel.py

import SpriteLibrary
import random

# Storage class for a single object
class Object:

    # Constructor
    def __init__(self, world, objectType, objectName, defaultSpriteName):
        self.type = objectType
        self.name = objectName
        self.defaultSpriteName = defaultSpriteName

        # Whether the agent has had tick() called already this past update
        self.tickCompleted = False

        # Whether the sprite name needs to be recalculated
        # By default this is off (i.e. static sprites).
        # If your object changes sprites based on status, then you should set this to True,
        # especially in tick() whenever the object changes state.
        self.needsSpriteNameUpdate = False

        # Name of the current and last sprite names
        self.curSpriteName = None
        self.lastSpriteName = None
        self.tempLastSpriteName = None      # Used to store what the next 'lastSpriteName' will be -- updated when the backbuffer flips

        # World back-reference
        self.world = world

        # Properties/attributes
        self.attributes = {}

        # Default attributes
        self.attributes["isMovable"] = True                         # Can it be moved?
        self.attributes["isPassable"] = True                        # Can an agent walk over this?

        # Contents (for containers)
        self.parentContainer = None                                 # Back-reference for the container that this object is in
        self.attributes['isContainer'] = False                      # Is it a container?
        self.attributes['isOpenable'] = False                       # If it's a container, can you open/close it?
        self.attributes['isOpenContainer'] = False                  # If it's a container, then is it open?
        self.attributes['containerPrefix'] = ""                     # Container prefix (e.g. "in" or "on")            
        self.attributes['isOpen'] = False                           # Closed by default
        self.contents = []                                          # Contents of the container (other objects)

        # Passage (for dynamic passages like doors, that can be opened/closed)
        self.attributes['isPassage'] = False                        # Is this a passage?

        # Device (is activable)
        self.attributes['isActivatable'] = False                      # Is this a device? (more specifically, can it be activated/deactivated?)
        self.attributes['isActivated'] = False                      # Is this device currently activated?

        # Dialog attributes
        self.attributes['isDialogable'] = False                     # Can it be dialoged with?


        # Force a first infer-sprite-name
        # NOTE: Moved to a global update (since other objects that the sprite depends on may not be populated yet when it is created)
        self.firstInit = True

    #
    # World location
    #

    # This should always be called whenever the object is moved, to ensure that the world location is always up-to-date
    def setWorldLocation(self, gridX, gridY):
        self.attributes["gridX"] = gridX
        self.attributes["gridY"] = gridY

    def getWorldLocation(self):
        # Get the world location of the object
        return (self.attributes["gridX"], self.attributes["gridY"])

    # Remove from world location -- this is analagous to the removeObject() method for containers, but removes the object from the world tile.
    def removeFromWorldLocation(self):
        # Remove this object from its world location
        self.world.removeObjectFromTile(self)

    #
    #   Container Semantics
    #

    # Add an object (obj) to this container
    def addObject(self, obj, force=False):
        # Remove the object from its previous container
        obj.removeSelfFromContainer()

        # Add an object to this container        
        self.contents.append(obj)
        obj.parentContainer = self

    # Remove an object from this container
    def removeObject(self, obj):
        # Remove an object from this container
        if (obj in self.contents):
            self.contents.remove(obj)
            obj.parentContainer = None
            return True
        else:
            return False

    # Remove the current object from whatever container it's currently in
    def removeSelfFromContainer(self):
        # Remove this object from its container
        if (self.parentContainer != None):
            return self.parentContainer.removeObject(self)

    # Get all contained objects
    def getAllContainedObjectsRecursive(self, respectContainerStatus=False):
        # Get all contained objects, recursively
        out = []
        # If this is a container, and it's open, then add the contents
        if (not respectContainerStatus) or (respectContainerStatus and self.attributes['isOpenContainer']):
            for obj in self.contents:
                # Add self
                out.append(obj)
                # Add children
                out.extend(obj.getAllContainedObjectsRecursive(respectContainerStatus))
        # Return
        return out



    #
    #   Update/Tick
    #
    def tick(self):
        # Update the object

        # Stop if the object has already had tick() called this update -- this might have happened if the object moved locations in this current update cycle.
        if (self.tickCompleted):
            return

        # Infer current name
        if (self.firstInit):
            self.firstInit = False
            self.inferSpriteName(force=True)
        else:
            self.inferSpriteName()


        # Set that the tick has been completed on this object
        self.tickCompleted = True

        # Also call tick on all contained objects
        for obj in self.contents:
            # First, update the grid location of the contained objects to be the same as the container
            obj.setWorldLocation(self.attributes["gridX"], self.attributes["gridY"])
            # Next, call tick()
            obj.tick()

        
        

    #
    #   Sprite
    #

    # Invalidate the sprite name for this object, and all objects it contains/that contain it.
    # This will force them to update their sprites on the next tick.
    def invalidateSpritesThisWorldTile(self):
        # Step 1: Get the names of all objects at this world tile
        allObjs = self.world.getObjectsAt(self.attributes["gridX"], self.attributes["gridY"])

        # Step 2: Invalidate the sprite names for all objects at this world tile, plus all objects contained by those objects
        for obj in allObjs:
            obj.needsSpriteNameUpdate = True
            for containedObj in obj.getAllContainedObjectsRecursive():
                containedObj.needsSpriteNameUpdate = True        


    def inferSpriteName(self, force:bool=False):
        # Infer the sprite name from the current state of the object
        # This should be called whenever the object is moved, or something else changes
        if (self.needsSpriteNameUpdate):
            # Placeholder for inferring sprite name based on attributes
            self.curSpriteName = self.defaultSpriteName
            pass
        else:
            self.curSpriteName = self.defaultSpriteName


    # TODO: Add world as context?
    def getSpriteName(self):
        # Get the current sprite name, in response to the current state of the object

        # Default: return the default sprite name
        return self.curSpriteName
    
    # Should be run once per frame, after the rendering for every tile is finished, after the backbuffer flips.
    def updateLastSpriteName(self):
        # Update the last sprite name
        self.lastSpriteName = self.tempLastSpriteName

    # TODO: Rendering for objects with contents (e.g. containers with things on/in them)
    def getSpriteNamesWithContents(self):
        # Get the sprite name, including the contents of the object
        # This is used for rendering objects that contain other objects (e.g. containers)

        # First, get the name of the current object itself
        spriteList = [self.getSpriteName()]

        # Then, add the name of any visible contents
        # First, check if this is a container (and it's open)
        if (self.attributes['isContainer'] and self.attributes['isOpenContainer']):
            # If so, then add the contents
            for obj in self.contents:
                # Add the sprite name of the object
                spriteNameObj = obj.getSpriteName()
                #print("Object name: " + obj.name + "  sprite name: " + str(spriteNameObj))
                if (spriteNameObj != None):
                    spriteList.append(spriteNameObj)                

        # Return the sprite list
        return spriteList


#
#   Object: Grass
#
class Grass(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "grass", "grass", defaultSpriteName = "forest1_grass")

        self.attributes["isMovable"] = False                       # Can it be moved?
    
    def tick(self):
        # Call superclass
        Object.tick(self)


#
#   Object: Wall
#
class Wall(Object):
    # Constructor
    def __init__(self, world):
        # Note: Change the default sprite name to something obviously incorrect so it is obvious when it's not inferring properly. 
        Object.__init__(self, world, "wall", "wall", defaultSpriteName = "house2_wall_t")

        self.attributes["isMovable"] = False                       # Can it be moved?
        self.attributes["isPassable"] = False                      # Agen't can't walk over this

        # Rendering attribute (wall direction, "tl", "tr", "bl", "br", "l", "r", "t", "b")     
        self.wallShape = ""

        
    def tick(self):
        # TODO: Invalidate sprite name if this or neighbouring walls change
        if (False):
            self.needsSpriteNameUpdate = True


        # Call superclass
        Object.tick(self)

    # Helper function to get the neighbouring walls
    def _hasWall(self, x, y):
        # Check to see if there is a wall at the given location
        # First, get objects at a given location
        objects = self.world.getObjectsAt(x, y)
        # Then, check to see if any of them are walls
        for object in objects:
            if (object.type == "wall"):
                return (True, object.wallShape)
            elif (object.type == "door"):
                return (True, "")
        # If we get here, there are no walls
        return (False, "")
    
    # Helper function to get the neighbouring walls
    def _hasFloor(self, x, y):
        # Check to see if there is a wall at the given location
        # First, get objects at a given location
        objects = self.world.getObjectsAt(x, y)
        # Then, check to see if any of them are walls
        for object in objects:
            if object.type == "floor":
                return True
        # If we get here, there are no walls
        return False

    # Sprite
    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return

        # Check to see what the neighbouring walls are
        hasWallNorth, wallShapeNorth = self._hasWall(self.attributes["gridX"], self.attributes["gridY"] - 1)
        hasWallSouth, wallShapeSouth = self._hasWall(self.attributes["gridX"], self.attributes["gridY"] + 1)
        hasWallWest, wallShapeWest = self._hasWall(self.attributes["gridX"] - 1, self.attributes["gridY"])
        hasWallEast, wallShapeEast = self._hasWall(self.attributes["gridX"] + 1, self.attributes["gridY"])

        # Check to see if there is neighbouring floor
        hasFloorNorth = self._hasFloor(self.attributes["gridX"], self.attributes["gridY"] - 1)
        hasFloorSouth = self._hasFloor(self.attributes["gridX"], self.attributes["gridY"] + 1)
        hasFloorWest = self._hasFloor(self.attributes["gridX"] - 1, self.attributes["gridY"])
        hasFloorEast = self._hasFloor(self.attributes["gridX"] + 1, self.attributes["gridY"])        

        isInterior = (hasFloorNorth and hasFloorSouth) or (hasFloorWest and hasFloorEast)

        # Corners
        # First, 4 corners
        if (hasWallNorth and hasWallEast and hasWallSouth and hasWallWest):
            # 4-way
            self.curSpriteName = "house2_wall_int_4way"
            self.wallShape = "4way"

        # Next, 3 corners
        elif (hasWallNorth and hasWallSouth and hasWallEast):
            # 3-way, up/down/right
            self.curSpriteName = "house2_wall_int_tbr"
            self.wallShape = "tbr"
        elif (hasWallNorth and hasWallSouth and hasWallWest):
            # 3-way, up/down/left
            self.curSpriteName = "house2_wall_int_tbl"
            self.wallShape = "tbl"
        elif (hasWallEast and hasWallWest and hasWallNorth):
            # 3-way, left/right/up
            self.curSpriteName = "house2_wall_int_lrt"
            self.wallShape = "lrt"
        elif (hasWallEast and hasWallWest and hasWallSouth):
            # 3-way, left/right/down
            self.curSpriteName = "house2_wall_int_lrb"
            self.wallShape = "lrb"

        # Next, Corners (NE, NW, SE, SW)
        elif (hasWallSouth and hasWallEast):
            self.curSpriteName = "house2_wall_tl"
            self.wallShape = "tl"
        elif (hasWallSouth and hasWallWest):
            self.curSpriteName = "house2_wall_tr"
            self.wallShape = "tr"
        elif (hasWallNorth and hasWallEast):
            self.curSpriteName = "house2_wall_bl"
            self.wallShape = "bl"
        elif (hasWallNorth and hasWallWest):
            self.curSpriteName = "house2_wall_br"
            self.wallShape = "br"
        
        # Next, edges (interior)
        elif (isInterior):
            # If a wall north or south, then it's a vertical wall            
            if (hasWallNorth or hasWallSouth):
                if (hasWallNorth and hasWallSouth):
                    self.curSpriteName = "house2_wall_int_tb"
                    self.wallShape = "v"
                elif (hasWallNorth):
                    self.curSpriteName = "house2_wall_int_tb_opening_t"
                    self.wallShape = "v"
                elif (hasWallSouth):
                    self.curSpriteName = "house2_wall_int_tb_opening_b"
                    self.wallShape = "v"
            # If a wall east or west, then it's a horizontal wall
            elif (hasWallEast or hasWallWest):
                if (hasWallEast and hasWallWest):
                    self.curSpriteName = "house2_wall_int_lr"
                    self.wallShape = "h"
                elif (hasWallEast):
                    self.curSpriteName = "house2_wall_int_lr_opening_l"
                    self.wallShape = "h"
                elif (hasWallWest):
                    self.curSpriteName = "house2_wall_int_lr_opening_r"
                    self.wallShape = "h"
                
        # Next, edges (exterior)
        # First, check to see if there is a wall to the north or south
        elif (hasWallNorth or hasWallSouth):
            # Check to see if there is a floor to the east or west
            if (hasFloorEast):
                self.curSpriteName = "house2_wall_l"
                self.wallShape = "l"
            elif (hasFloorWest):
                self.curSpriteName = "house2_wall_r"
                self.wallShape = "r"
        
        # Next, check to see if there is a wall to the east or west
        elif (hasWallEast or hasWallWest):
            # Check to see if there is a floor to the north or south
            if (hasFloorNorth):
                self.curSpriteName = "house2_wall_t"
                self.wallShape = "t"
            elif (hasFloorSouth):
                self.curSpriteName = "house2_wall_b"
                self.wallShape = "b"                
                
        else:
            # Catch-all -- possibly a wall with no neighbours?
            print("Unknown wall shape!")
            self.curSpriteName = self.defaultSpriteName
            self.curSpriteName = "house2_wall_t"
            self.wallShape = "single"


        # If we reach here and still don't know the wall shape, then we'll note that it should be checked again the next tick
        if (self.wallShape == ""):
            self.needsSpriteNameUpdate = True

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName

#
#   Object: Floor
#
class Floor(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "floor", "floor", defaultSpriteName = "house2_floor")

        # Default attributes
        self.attributes["isMovable"] = False                       # Can it be moved?

        # Material type?

    def tick(self):
        # TODO: Invalidate sprite name if this or neighbouring walls change
        if (False):
            self.needsSpriteNameUpdate = True

        # TODO

        # Call superclass
        Object.tick(self)

    # Sprite
    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return

        # Static -- just use the default sprite name
        self.curSpriteName = self.defaultSpriteName

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName

#
#   Object: BackWall
#
# class WallHorizontal(Object):
#     # Constructor
#     def __init__(self, world):
#         # Default sprite name
#         Object.__init__(self, world, "back wall", "back wall", defaultSpriteName = "house2_wall_horiz")
#
#     def tick(self):
#         # Call superclass
#         Object.tick(self)

#
#   Object: Door
#
class Door(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "door", "door", defaultSpriteName = "house2_door_closed")

        # Default attributes
        self.attributes["isMovable"] = False                       # Can it be moved?        

        # Open/Close attribute (similar to container, but not a container)
        self.attributes['isPassage'] = True                       # Is this a passage?
        self.attributes['isOpenable'] = True                      # Can be opened
        self.attributes['isOpenPassage'] = False                  # If it's a passage, then is it open?
        



    def tick(self):
        # TODO: Invalidate sprite name if this or neighbouring walls change
        if (False):
            self.needsSpriteNameUpdate = True

        # TODO
        # Randomly open/close the door
        #if (random.randint(0, 100) < 5):
        #    self.attributes["isOpenPassage"] = not self.attributes["isOpenPassage"]
        #    self.needsSpriteNameUpdate = True

        # If the door is open, the object is passable.  If closed, impassable.
        if (self.attributes["isOpenPassage"]):
            self.attributes["isPassable"] = True
        else:
            self.attributes["isPassable"] = False

        # Call superclass
        Object.tick(self)

    # Sprite
    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return

        # If the door is open, then we need to use the open sprite
        if (self.attributes["isOpenPassage"]):
            self.curSpriteName = "house2_door_open"
        else:
            self.curSpriteName = "house2_door_closed"

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName

#
#   Object: Sign
#
class Sign(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "sign", "sign", defaultSpriteName = "village1_sign_nowriting")

        # Default attributes
        self.attributes["isMovable"] = False                       # Can it be moved?
        self.attributes["isPassable"] = False                      # Agen't can't walk over this object     
        self.attributes["document"] = "This is a sign."

    def tick(self):
        # TODO: Invalidate sprite name if this or neighbouring walls change
        if (False):
            self.needsSpriteNameUpdate = True

        # Call superclass
        Object.tick(self)

    def setText(self, text:str):
        self.attributes["document"] = text.strip()
        self.needsSpriteNameUpdate = True

    # Sprite
    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return

        # If the stove is open, then we need to use the open sprite
        if (len(self.attributes["document"]) > 0):
            self.curSpriteName = "village1_sign_writing"
        else:
            self.curSpriteName = "village1_sign_nowriting"

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName

        # After one run, we don't need to update the sprite name again unless something changes
        self.needsSpriteNameUpdate = False


#
#   Object: Sign (Village, large)
#
### TODO: CURRENTLY DOES NOT HANDLE THAT ITS A MULTI-TILE OBJECT
class SignVillage(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "sign (village)", "sign (village)", defaultSpriteName = "village1_sign_village")

        # Default attributes
        self.attributes["isMovable"] = False                       # Can it be moved?
        self.attributes["isPassable"] = False                      # Agen't can't walk over this
        self.attributes["document"] = "This is a sign."

    def tick(self):
        # TODO: Invalidate sprite name if this or neighbouring walls change
        if (False):
            self.needsSpriteNameUpdate = True

        # Call superclass
        Object.tick(self)

    def setText(self, text:str):
        self.attributes["document"] = text.strip()
        self.needsSpriteNameUpdate = True

    # Sprite
    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return

        # Static sprite -- always the same (currently)
        self.curSpriteName = self.defaultSpriteName

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName

        # After one run, we don't need to update the sprite name again unless something changes
        self.needsSpriteNameUpdate = False



#
#   Object: Stove
#
class Stove(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "stove", "stove", defaultSpriteName = "house1_stove_off")

        # Default attributes
        self.attributes["isMovable"] = False                       # Can it be moved?
        self.attributes["isPassable"] = False                      # Agen't can't walk over this

        # Container attributes
        self.attributes['isContainer'] = True                      # Is it a container?
        self.attributes['isOpenable'] = True                       # Can be opened
        self.attributes['isOpenContainer'] = False                 # If it's a container, then is it open?
        self.attributes['containerPrefix'] = "in"                  # Container prefix (e.g. "in" or "on")            

        # Device (is activable)
        self.attributes['isActivatable'] = True                       # Is this a device? (more specifically, can it be activated/deactivated?)
        self.attributes['isActivated'] = False                      # Is this device currently activated?


    def tick(self):
        # TODO: Invalidate sprite name if this or neighbouring walls change
        if (False):
            self.needsSpriteNameUpdate = True

        # TODO

        # Call superclass
        Object.tick(self)

    # Sprite
    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return

        # If the stove is open, then we need to use the open sprite
        if (self.attributes["isOpenContainer"]):
            self.curSpriteName = "house1_stove_open"
        else:
            if (self.attributes["isActivated"]):
                self.curSpriteName = "house1_stove_on"
            else:
                self.curSpriteName = "house1_stove_off"

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName


#
#   Object: Sink
#
class Sink(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "stove", "stove", defaultSpriteName = "house1_sink_off")

        # Default attributes
        self.attributes["isMovable"] = False                       # Can it be moved?
        self.attributes["isPassable"] = False                      # Agen't can't walk over this        

        # Container attributes
        self.attributes['isContainer'] = True                      # Is it a container?
        self.attributes['isOpenable'] = False                      # Always open
        self.attributes['isOpenContainer'] = True                  # If it's a container, then is it open?
        self.attributes['containerPrefix'] = "in"                  # Container prefix (e.g. "in" or "on")

        # Device (is activable)
        self.attributes['isActivatable'] = True                     # Is this a device? (more specifically, can it be activated/deactivated?)
        self.attributes['isActivated'] = False                      # Is this device currently activated?



    def tick(self):
        # TODO: Invalidate sprite name if this or neighbouring walls change
        if (False):
            self.needsSpriteNameUpdate = True

        # TODO
        # Randomly turn on/off
        #if (random.randint(0, 100) < 5):
        #    self.attributes["isActivated"] = not self.attributes["isActivated"]
        #    self.needsSpriteNameUpdate = True

        # Call superclass
        Object.tick(self)

    # Sprite
    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return

        # If the stove is open, then we need to use the open sprite
        if (self.attributes["isActivated"]):
            self.curSpriteName = "house1_sink_on"
        else:
            self.curSpriteName = "house1_sink_off"

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName


#
#   Object: Fridge
#
class Fridge(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "fridge", "fridge", defaultSpriteName = "house1_fridge_closed")

        # Default attributes
        self.attributes["isMovable"] = False                       # Can it be moved?
        self.attributes["isPassable"] = False                      # Agen't can't walk over this

        # Container attributes
        self.attributes['isContainer'] = True                      # Is it a container?
        self.attributes['isOpenable'] = True                       # Can be opened
        self.attributes['isOpenContainer'] = False                  # If it's a container, then is it open?
        self.attributes['containerPrefix'] = "in"                  # Container prefix (e.g. "in" or "on")            

        # Device (is activable)
        self.attributes['isActivatable'] = True                      # Is this a device? (more specifically, can it be activated/deactivated?)
        self.attributes['isActivated'] = True                      # Is this device currently activated?



    def tick(self):
        # TODO: Invalidate sprite name if this or neighbouring walls change
        if (False):
            self.needsSpriteNameUpdate = True

        # TODO

        # Call superclass
        Object.tick(self)

    # Sprite
    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return

        self.curSpriteName = self.defaultSpriteName

        # TODO: If the fridge is open, then we need to use the open sprite
        if (self.attributes["isOpenContainer"]):
            self.curSpriteName = "house1_fridge_open"
        else:
            self.curSpriteName = "house1_fridge_closed"

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName


#
#   Object: Table
#
class Table(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "table", "table", defaultSpriteName = "house1_table")

        self.attributes["isMovable"] = False                       # Can it be moved?
        self.attributes["isPassable"] = False                      # Agen't can't walk over this

        # Container
        self.attributes['isContainer'] = True                      # Is it a container?
        self.attributes['isOpenable'] = False                      # Can not be opened (things are stored on the table surface)
        self.attributes['isOpenContainer'] = True                  # If it's a container, then is it open?
        self.attributes['containerPrefix'] = "on"                  # Container prefix (e.g. "in" or "on")            

    def tick(self):
        # Call superclass
        Object.tick(self)    

#
#   Object: Table (Bedside)
#
class TableBedside(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "table", "table", defaultSpriteName = "house1_table_bedside")

        self.attributes["isMovable"] = False                       # Can it be moved?
        self.attributes["isPassable"] = False                      # Agen't can't walk over this

        # Container
        self.attributes['isContainer'] = True                      # Is it a container?
        self.attributes['isOpenable'] = True                       # Can be opened
        self.attributes['isOpenContainer'] = True                  # If it's a container, then is it open?
        self.attributes['containerPrefix'] = "in"                  # Container prefix (e.g. "in" or "on")            

    def tick(self):
        # Call superclass
        Object.tick(self)    

#
#   Object: Chair
#
class Chair(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "chair", "chair", defaultSpriteName = "house1_chair_l")

        self.attributes["isMovable"] = False                       # Can it be moved?
        self.attributes["isPassable"] = False                      # Agen't can't walk over this

        # Container attributes
        self.attributes['isContainer'] = True                      # Is it a container?
        self.attributes['isOpenable'] = False                      # Always open
        self.attributes['isOpenContainer'] = True                  # If it's a container, then is it open?
        self.attributes['containerPrefix'] = "on"                  # Container prefix (e.g. "in" or "on")

        # Rendering attributes
        self.curDirection = "west"

    def tick(self):
        # TODO: Invalidate sprite name if this or neighbouring walls change
        if (False):
            self.needsSpriteNameUpdate = True

        # Call superclass
        Object.tick(self)


    # Sprite helper: Look to see if there's a table nearby
    def _hasTable(self, x, y):
        # Check to see if there is a wall at the given location
        # First, get objects at a given location
        objects = self.world.getObjectsAt(x, y)
        # Then, check to see if any of them are walls
        for object in objects:
            if object.type == "table":
                return True
        # If we get here, there are no walls
        return False

    # Sprite
    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return

        # Check to see if there is a table north, east, south, or west of us
        hasTableNorth = self._hasTable(self.attributes["gridX"], self.attributes["gridY"] - 1)
        hasTableSouth = self._hasTable(self.attributes["gridX"], self.attributes["gridY"] + 1)
        hasTableEast = self._hasTable(self.attributes["gridX"] + 1, self.attributes["gridY"])
        hasTableWest = self._hasTable(self.attributes["gridX"] - 1, self.attributes["gridY"])

        # If we have a table to the north, then we need to use the north sprite
        if (hasTableNorth):
            self.curSpriteName = "house1_chair_u"
            self.curDirection = "north"
        elif (hasTableSouth):
            self.curSpriteName = "house1_chair_d"
            self.curDirection = "south"
        elif (hasTableEast):
            self.curSpriteName = "house1_chair_r"
            self.curDirection = "east"
        elif (hasTableWest):
            self.curSpriteName = "house1_chair_l"
            self.curDirection = "west"
        else:
            # If we get here, then we have no table nearby
            self.curSpriteName = "house1_chair_l"
            self.curDirection = "west"

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName


#
#   Object: Bed
#
class Bed(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "bed", "bed", defaultSpriteName = "house1_bed_ud")
        #Object.__init__(self, world, "bed", "bed", defaultSpriteName = "house1_bed_lr")

        self.attributes["isMovable"] = False                       # Can it be moved?
        self.attributes["isPassable"] = False                      # Agen't can't walk over this

        # Container
        self.attributes['isContainer'] = True                      # Is it a container?
        self.attributes['isOpenContainer'] = True                  # If it's a container, then is it open?
        self.attributes['containerPrefix'] = "on"                  # Container prefix (e.g. "in" or "on")            


    def tick(self):
        # Call superclass
        Object.tick(self)    



#
#   Object: Microscope
#
class Microscope(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "microscope", "microscope", defaultSpriteName = "placeholder_microscope")

        # Default attributes
        pass        
        

    def tick(self):
        # TODO: Invalidate sprite name if this or neighbouring walls change
        if (False):
            self.needsSpriteNameUpdate = True

        # TODO

        # Call superclass
        Object.tick(self)

    # Sprite
    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return

        self.curSpriteName = self.defaultSpriteName

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName


#
#   Object: Statue
#
class Statue(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "statue", "statue", defaultSpriteName = "statue_statue1")
    
        self.attributes["isMovable"] = False                       # Can it be moved?
        self.attributes["isPassable"] = False                      # Agen't can't walk over this

    def tick(self):
        # Call superclass
        Object.tick(self)


#
#   Object: Path
#
class Path(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "path", "path", defaultSpriteName = "forest1_path_c")

        self.attributes["isMovable"] = False                       # Can it be moved?

    
    def tick(self):
        # Call superclass
        Object.tick(self)

    # Check if a tile already contains a "path"
    def _hasObj(self, x, y, type):
        objects = self.world.getObjectsAt(x, y)
        # Then, check to see if any of them are walls
        for object in objects:
            if (object.type == type):
                return True
        return False        

    # Sprite
    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return

        # Check to see if the neighbouring tiles have paths
        hasPathNorth = self._hasObj(self.attributes["gridX"], self.attributes["gridY"] - 1, "path")
        hasPathSouth = self._hasObj(self.attributes["gridX"], self.attributes["gridY"] + 1, "path")
        hasPathWest = self._hasObj(self.attributes["gridX"] - 1, self.attributes["gridY"], "path")
        hasPathEast = self._hasObj(self.attributes["gridX"] + 1, self.attributes["gridY"], "path")
        
        # 4 positives
        if (hasPathNorth and hasPathSouth and hasPathEast and hasPathWest):
            self.curSpriteName = "forest1_path_c"

        # 3 positives
        elif (hasPathNorth and hasPathSouth and hasPathEast):
            self.curSpriteName = "forest1_path_l"
        elif (hasPathNorth and hasPathSouth and hasPathWest):
            self.curSpriteName = "forest1_path_r"
        elif (hasPathEast and hasPathWest and hasPathNorth):
            self.curSpriteName = "forest1_path_b"
        elif (hasPathEast and hasPathWest and hasPathSouth):
            self.curSpriteName = "forest1_path_t"

        # 2 positives (up/down or left/right)
        elif (hasPathNorth and hasPathSouth):
            self.curSpriteName = "forest1_path_lr"
        elif (hasPathEast and hasPathWest):
            self.curSpriteName = "forest1_path_tb"

        # 2 positives (top/left or top/right or bottom/left or bottom/right)
        elif (hasPathNorth and hasPathWest):
            self.curSpriteName = "forest1_path_br"
        elif (hasPathNorth and hasPathEast):
            self.curSpriteName = "forest1_path_bl"
        elif (hasPathSouth and hasPathWest):
            self.curSpriteName = "forest1_path_tr"
        elif (hasPathSouth and hasPathEast):
            self.curSpriteName = "forest1_path_tl"

        # 1 positive (north/east/south/west)
        elif (hasPathNorth):
            self.curSpriteName = "forest1_path_1way_t"
        elif (hasPathEast):
            self.curSpriteName = "forest1_path_1way_r"
        elif (hasPathSouth):
            self.curSpriteName = "forest1_path_1way_b"
        elif (hasPathWest):
            self.curSpriteName = "forest1_path_1way_l"

        else:
            # If we get here, then we have no path nearby (north/east/south/west)
            self.curSpriteName = "forest1_path_single"

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName

#
#   Object: SoilTile
#
class SoilTile(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "soil", "soil", defaultSpriteName = "forest1_soil_c")
    
        self.attributes["isMovable"] = False                       # Can it be moved?

    def tick(self):
        # Call superclass
        Object.tick(self)

    # Check if a tile already contains a "path"
    def _hasObj(self, x, y, type):
        objects = self.world.getObjectsAt(x, y)
        # Then, check to see if any of them are walls
        for object in objects:
            if (object.type == type):
                return True
        return False        

    # Sprite
    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return

        # Check to see if the neighbouring tiles have paths
        hasPathNorth = self._hasObj(self.attributes["gridX"], self.attributes["gridY"] - 1, "soil")
        hasPathSouth = self._hasObj(self.attributes["gridX"], self.attributes["gridY"] + 1, "soil")
        hasPathWest = self._hasObj(self.attributes["gridX"] - 1, self.attributes["gridY"], "soil")
        hasPathEast = self._hasObj(self.attributes["gridX"] + 1, self.attributes["gridY"], "soil")
        
        # 4 positives
        if (hasPathNorth and hasPathSouth and hasPathEast and hasPathWest):
            self.curSpriteName = "forest1_soil_c"

        # 3 positives
        elif (hasPathNorth and hasPathSouth and hasPathEast):
            self.curSpriteName = "forest1_soil_l"
        elif (hasPathNorth and hasPathSouth and hasPathWest):
            self.curSpriteName = "forest1_soil_r"
        elif (hasPathEast and hasPathWest and hasPathNorth):
            self.curSpriteName = "forest1_soil_b"
        elif (hasPathEast and hasPathWest and hasPathSouth):
            self.curSpriteName = "forest1_soil_t"

        # 2 positives (top/left or top/right or bottom/left or bottom/right)
        elif (hasPathNorth and hasPathWest):
            self.curSpriteName = "forest1_soil_br"
        elif (hasPathNorth and hasPathEast):
            self.curSpriteName = "forest1_soil_bl"
        elif (hasPathSouth and hasPathWest):
            self.curSpriteName = "forest1_soil_tr"
        elif (hasPathSouth and hasPathEast):
            self.curSpriteName = "forest1_soil_tl"

        else:
            # If we get here, then we have no path nearby (north/east/south/west)
            self.curSpriteName = "forest1_soil_single"

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName


#
#   Object: Fence
#
class Fence(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "fence", "fence", defaultSpriteName = "village1_fence_single")
    
        self.attributes["isMovable"] = False                       # Can it be moved?
        self.attributes["isPassable"] = False                      # Agen't can't walk over this


    def tick(self):
        # Call superclass
        Object.tick(self)

    # Check if a tile already contains a "path"
    def _hasObj(self, x, y, type):
        objects = self.world.getObjectsAt(x, y)
        # Then, check to see if any of them are walls
        for object in objects:
            if (object.type == type):
                return True
        return False        

    # Sprite
    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return

        # Check to see if the neighbouring tiles have paths        
        hasFenceNorth = self._hasObj(self.attributes["gridX"], self.attributes["gridY"] - 1, "fence")
        hasFenceSouth = self._hasObj(self.attributes["gridX"], self.attributes["gridY"] + 1, "fence")
        hasFenceWest = self._hasObj(self.attributes["gridX"] - 1, self.attributes["gridY"], "fence")
        hasFenceEast = self._hasObj(self.attributes["gridX"] + 1, self.attributes["gridY"], "fence")
        
        # 4 positives (should never happen unless something is wonky -- just in case, place a single fence)
        if (hasFenceNorth and hasFenceSouth and hasFenceEast and hasFenceWest):
            self.curSpriteName = "village1_fence_single"

        # 3 positives
        # elif (hasFenceNorth and hasFenceSouth and hasFenceEast):
        #     self.curSpriteName = "village1_fence_l"
        # elif (hasFenceNorth and hasFenceSouth and hasFenceWest):
        #     self.curSpriteName = "village1_fence_r"
        # elif (hasFenceEast and hasFenceWest and hasFenceNorth):
        #     self.curSpriteName = "village1_fence_b"
        # elif (hasFenceEast and hasFenceWest and hasFenceSouth):
        #     self.curSpriteName = "village1_fence_t"

        # 2 positives (up/down or left/right)
        elif (hasFenceNorth and hasFenceSouth):
            self.curSpriteName = "village1_fence_l"
        elif (hasFenceEast and hasFenceWest):
            self.curSpriteName = "village1_fence_t"

        # 2 positives (top/left or top/right or bottom/left or bottom/right)
        elif (hasFenceNorth and hasFenceWest):
            self.curSpriteName = "village1_fence_br"
        elif (hasFenceNorth and hasFenceEast):
            self.curSpriteName = "village1_fence_bl"
        elif (hasFenceSouth and hasFenceWest):
            self.curSpriteName = "village1_fence_tr"
        elif (hasFenceSouth and hasFenceEast):
            self.curSpriteName = "village1_fence_tl"

        # 1 positive (north/east/south/west)
        elif (hasFenceNorth):
            self.curSpriteName = "village1_fence_1way_t"
        elif (hasFenceEast):
            self.curSpriteName = "village1_fence_1way_r"
        elif (hasFenceSouth):
            self.curSpriteName = "village1_fence_1way_b"
        elif (hasFenceWest):
            self.curSpriteName = "village1_fence_1way_l"

        else:
            # If we get here, then we have no path nearby (north/east/south/west)
            self.curSpriteName = "village1_fence_single"

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName


#
#   Object: PlantGeneric
#
### A placeholder for a plant
class PlantGeneric(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "plant (generic)", "plant (generic)", defaultSpriteName = "forest1_plant1")
    
    def tick(self):
        # Call superclass
        Object.tick(self)


#
#   Object: Mushroom
#
class Mushroom(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "mushroom", "mushroom", defaultSpriteName = "forest1_mushroom_pink")

        #self.attributes["color"] = "pink"                           # Color of the mushroom (valid: "yellow", "pink", "red", "green")
        # Randomly choose a color
        self.attributes["color"] = random.choice(["yellow", "pink", "red", "green"])

    
    def tick(self):
        # Call superclass
        Object.tick(self)

    # Sprite
    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return
        
        # Infer sprite based on color
        if (self.attributes["color"] == "yellow"):
            self.curSpriteName = "forest1_mushroom_yellow"
        elif (self.attributes["color"] == "pink"):
            self.curSpriteName = "forest1_mushroom_pink"
        elif (self.attributes["color"] == "red"):
            self.curSpriteName = "forest1_mushroom_red"
        elif (self.attributes["color"] == "green"):
            self.curSpriteName = "forest1_mushroom_green"
        else:
            # Throw warning, default to pink
            print("WARNING: Mushroom color not recognized (" + str(self.attributes["color"]) + "). Defaulting to pink.")
            self.curSpriteName = "forest1_mushroom_pink"            

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName


#
#   Object: Pot (container)
#
class Pot(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "pot", "pot", defaultSpriteName = "placeholder_pot")

        self.attributes["isMovable"] = True                       # Can it be moved?
        self.attributes["isPassable"] = True                      # Agen't can't walk over this

        # Container
        self.attributes['isContainer'] = True                      # Is it a container?
        self.attributes['isOpenable'] = False                      # Can not be opened (things are stored in the open pot)
        self.attributes['isOpenContainer'] = True                  # If it's a container, then is it open?
        self.attributes['containerPrefix'] = "in"                  # Container prefix (e.g. "in" or "on")            

    def tick(self):
        # Call superclass
        Object.tick(self)    

#
#   Object: Pot (container)
#
class FlowerPot(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "pot", "pot", defaultSpriteName = "generated_flowerpot")

        self.attributes["isMovable"] = True                       # Can it be moved?
        self.attributes["isPassable"] = True                      # Agen't can't walk over this

        # Container
        self.attributes['isContainer'] = True                      # Is it a container?
        self.attributes['isOpenable'] = False                      # Can not be opened (things are stored in the open pot)
        self.attributes['isOpenContainer'] = True                  # If it's a container, then is it open?
        self.attributes['containerPrefix'] = "in"                  # Container prefix (e.g. "in" or "on")            

    def tick(self):
        # Call superclass
        Object.tick(self)    

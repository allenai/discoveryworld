# ObjectModel.py

import SpriteLibrary
from Layer import Layer
from ActionSuccess import *
from ScienceHelpers import *
import random
import json
import copy


# Storage class for a single object
class Object:

    # Constructor
    def __init__(self, world, objectType, objectName, defaultSpriteName):
        self.type = objectType
        self.name = objectName
        self.defaultSpriteName = defaultSpriteName
        self.uuid = world.uuidGenerator.generateUUID()          # Generate a unique integer to represent this object

        # Whether the agent has had tick() called already this past update
        self.tickCompleted = False

        # Whether the sprite name needs to be recalculated
        # By default this is off (i.e. static sprites).
        # If your object changes sprites based on status, then you should set this to True,
        # especially in tick() whenever the object changes state.
        self.needsSpriteNameUpdate = False

        # Name of the current and last sprite names
        self.curSpriteName = None
        self.curSpriteModifiers = set()
        self.lastSpriteName = None
        self.tempLastSpriteName = None      # Used to store what the next 'lastSpriteName' will be -- updated when the backbuffer flips

        # World back-reference
        self.world = world

        # Properties/attributes
        self.attributes = {}

        # Initial world location (undefined)
        if ("gridX" not in self.attributes):
            self.attributes["gridX"] = -1   
        if ("gridY" not in self.attributes):
            self.attributes["gridY"] = -1

        # Agent action history (if applicable)
        self.actionHistory = None

        # Default attributes
        self.attributes["isMovable"] = True                         # Can it be moved?
        self.attributes["isPassable"] = True                        # Can an agent walk over this?

        # Materials
        self.attributes["materials"] = []                           # List of materials that this object is made of

        # Contents (for containers)
        self.parentContainer = None                                 # Back-reference for the container that this object is in
        self.attributes['isContainer'] = False                      # Is it a container?
        self.attributes['isOpenable'] = False                       # If it's a container, can you open/close it?
        self.attributes['isOpenContainer'] = False                  # If it's a container, then is it open?
        self.attributes['containerPrefix'] = ""                     # Container prefix (e.g. "in" or "on")            
        self.attributes['isOpen'] = False                           # Closed by default
        self.attributes['contentsVisible2D'] = True                 # If it is a container, do we render the contents in the 2D representation, or is that already handled (e.g. for pots/jars, that render generic contents if they contain any objects)
        self.contents = []                                          # Contents of the container (other objects)

        # Parts (for composite objects -- similar to containers)
        self.parts = []                                             # List of parts that this object is made of

        # Whether the object has a hole in it (e.g. a hole in the ground), that allows objects to be contained inside it.
        self.attributes['hasHole'] = False                          # Does it have a hole?

        # Passage (for dynamic passages like doors, that can be opened/closed)
        self.attributes['isPassage'] = False                        # Is this a passage?

        # Device (is activable)
        self.attributes['isActivatable'] = False                    # Is this a device? (more specifically, can it be activated/deactivated?)
        self.attributes['isActivated'] = False                      # Is this device currently activated?
        self.attributes['isUsable'] = False                         # Can this device be used with another object? (e.g. specifically through the 'use' action)

        # Dialog attributes
        self.attributes['isDialogable'] = False                     # Can it be dialoged with?

        # Food attributes
        self.attributes['isEdible'] = False                         # Can it be eaten?

        # Poison/health attributes
        self.attributes['isPoisonous'] = False                     # Is it poisonous?

        # Can it be used with a shovel (e.g. dug up?).  The function is called useWithShovelResult().
        self.attributes['isShovelable'] = False                    # Can it be shoveled?

        # Readable
        self.attributes['isReadable'] = False                      # Can it be read?
        self.attributes['document'] = ""                           # Any text to read

        # Temperature
        self.attributes['temperatureC'] = 20                       # The default object temeprature, in Celsius
        self.attributes['heatSourceMaxTemp'] = 0                   # If it is a heat source, then this is the maximum temperature that it can reach
        self.attributes['coolSourceMinTemp'] = 0                   # If it is a cool source, then this is the minimum temperature that it can reach

        # Alive
        self.attributes['isLiving'] = False                         # Is it alive?

        # Modifier text, if the object is viewed under a microscope. This is a list of strings, which are displayed in the microscope view.
        self.attributes['microscopeModifierText'] = []


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

        # Recursively update the world location of all contained objects and parts
        for obj in self.contents:
            obj.setWorldLocation(gridX, gridY)

        for obj in self.parts:
            obj.setWorldLocation(gridX, gridY)

    def getWorldLocation(self):
        # Get the world location of the object
        return (self.attributes["gridX"], self.attributes["gridY"])

    # Remove from world location -- this is analagous to the removeObject() method for containers, but removes the object from the world tile.
    def removeFromWorldLocation(self):
        # TODO: Depricated? use self.world.removeObject(obj) instead?

        # Remove this object from its world location
        self.world.removeObjectFromTile(self)

    #
    #   Material Property Initialization
    #
    def initializeMaterialProperties(self, materialIndexDict):
        # If the object has special material requirements (like randomly choosing from a number of different materials), then this function should be overridden. 
        # Otherwise, it can be left blank.
        pass

    #
    #   Container Semantics
    #

    # Add an object (obj) to this container
    def addObject(self, obj, force=False):
        # Remove the object from its previous container
        obj.removeSelfFromContainer()

        # Add an object to this container        
        self.contents.append(obj)
        # Set the parent container
        obj.parentContainer = self        


    # Add an object (obj) as a part of this object
    def addPart(self, obj):
        # Remove the object from its previous container
        obj.removeSelfFromContainer()

        # Add an object as part (using parentContainer as a backreference to whole)
        self.parts.append(obj)
        obj.parentContainer = self

    # Remove an object from this container
    def removeObject(self, obj):
        # Remove an object from this container
        if (obj in self.contents):
            self.contents.remove(obj)
            obj.parentContainer = None
            return True
        elif (obj in self.parts):
            self.parts.remove(obj)
            obj.parentContainer = None
            return True
        else:
            return False

    # Remove the current object from whatever container it's currently in
    def removeSelfFromContainer(self):
        # Remove this object from its container
        if (self.parentContainer != None):
            return self.parentContainer.removeObject(self)

    # Replace self with another object (obj) in the container that it's currently in
    # Largely intended for objects that change into completely different objects. 
    def replaceSelfWithObject(self, obj):
        # Replace self with another object in the container that it's currently in
        if (self.parentContainer != None):
            # Get the index of self in the parent container
            idx = self.parentContainer.contents.index(self)
            parentContainerCopy = self.parentContainer
            # Remove self from the parent container
            self.parentContainer.removeObject(self)
            # Add the new object at the same index
            parentContainerCopy.contents.insert(idx, obj)
            # Set the parent container
            obj.parentContainer = parentContainerCopy


    # Get all contained objects
    def getAllContainedObjectsRecursive(self, respectContainerStatus=False):
        # Get all contained objects, recursively
        out = []
        #print("getAllContainedObjectsRecursive: " + self.name + " (" + str(self.attributes['isOpenContainer']) + ") ." )
        # If this is a container, and it's open, then add the contents        
        if (not respectContainerStatus) or (respectContainerStatus and self.attributes['isOpenContainer']):
            for obj in self.contents:
                # Add self
                out.append(obj)
                # Add children
                out.extend(obj.getAllContainedObjectsRecursive(respectContainerStatus))

        # Return
        return out

    # Get one or more objects of a specific type. 
    # maxMatches specifies the maximum number of objects to return (all returns are a list)
    # recursive specifies whether to look recursively through all contained objects (True), or just the immediate contents (False)
    # respectContainerStatus specifies whether to respect the container status (e.g. if it's closed, then don't return anything, or recurse into it)
    def getContainedObjectByType(self, objType, maxMatches=1, recursive=False, respectContainerStatus=False):
        # Get an object of a specific type
        out = []

        # If not recursive, then just look at the immediate contents. 
        if (not recursive):
            if (not respectContainerStatus) or (respectContainerStatus and self.attributes['isOpenContainer']):
                for obj in self.contents:
                    # If this is the type we're looking for, then add it
                    if (obj.type == objType):
                        out.append(obj)
                        if (len(out) >= maxMatches):
                            break
            
        else: 
            # Recursive 
            # If this is a container, and it's open, then add the contents
            allObjs = self.getAllContainedObjectsRecursive(respectContainerStatus)
            for obj in allObjs:
                # If this is the type we're looking for, then add it
                if (obj.type == objType):
                    out.append(obj)
                    if (len(out) >= maxMatches):
                        break
        # Return
        return out

    # Get all contained objects and parts, do not respect containers (this is typically used for dumping the objects to a file)
    def getAllContainedObjectsAndParts(self, includeContents=True, includeParts=True):
        # TODO: Fix this so it doesn't require the list(set()) hack (which prevents the duplicates, but is slow)
        out = []
        # Add self
        out.append(self)

        if (includeContents):
            for obj in self.contents:
                # Add self
                out.append(obj)
                # Add children
                out.extend(obj.getAllContainedObjectsAndParts(includeContents, includeParts))

        if (includeParts):
            for obj in self.parts:
                # Add self
                out.append(obj)
                # Add children
                out.extend(obj.getAllContainedObjectsAndParts(includeContents, includeParts))

        # Return
        return list(set(out))

    # Get outermost closed container (if this object is contained in a closed container).
    # Essentially answers the question: "What is the next container that I'd have to open to (eventually) get at this object?"
    # Returns None if there is no closed container.
    def getOutermostClosedContainer(self, includeSelf=False):
        lastContainer = None
        lastParent = self.parentContainer

        # If 'includeSelf' is true, and this object is a closed container, then add it as the initial last container
        if (includeSelf):
            if (self.attributes['isContainer'] == True) and (self.attributes['isOpenContainer'] == False):
                lastContainer = self

        # Iterate through all parents, looking for the last closed container
        while (lastParent != None):
            if (lastParent.attributes['isOpenContainer'] == False):
                lastContainer = lastParent
            lastParent = lastParent.parentContainer

        # Return the last container
        return lastContainer


    #
    #   Actions (use with)
    #
    def actionUseWith(self, patientObj):
        # Use this object on the patient object
        return ActionSuccess(False, "I'm not sure how to use the " + self.name + " with the " + patientObj.name + ".")        

    # Specific use-with actions
    def useWithShovelResult():
        # Use this object with a shovel
        return None


    #
    #   Update/Tick
    #
    def tick(self):
        # Update the object

        # Stop if the object has already had tick() called this update -- this might have happened if the object moved locations in this current update cycle.
        if (self.tickCompleted):
            return

        # Remove all current sprite modifiers (these are regenerated every tick)
        self.curSpriteModifiers = set()

        # Infer current name
        if (self.firstInit):
            self.firstInit = False
            self.inferSpriteName(force=True)
        else:
            self.inferSpriteName()

        # Remove the list of object description modifiers, which should be regenerated every tick. 
        self.attributes['microscopeModifierText'] = []

        # Set that the tick has been completed on this object
        self.tickCompleted = True

        # Also call tick on all contained objects
        for obj in self.contents:
            # First, update the grid location of the contained objects to be the same as the container
            obj.setWorldLocation(self.attributes["gridX"], self.attributes["gridY"])
            # Next, call tick()
            obj.tick()
        # And all parts
        for obj in self.parts:
            # First, update the grid location of the contained objects to be the same as the container
            obj.setWorldLocation(self.attributes["gridX"], self.attributes["gridY"])
            # Next, call tick()
            obj.tick()


    #
    #   Text Observations
    #
    def getTextDescription(self):
        # Get a text description of this object
        return self.name 
    

    def getTextObservationMicroscopic(self):
        # Get a text description of this object, under a microscope
        # TODO: Check object size (normal, microscopic, nanoscopic?)

        microscopeDescriptionStr = ""

        # First, describe the object itself
        partNames = [part.name for part in self.parts]
        if (len(partNames) > 0):
            microscopeDescriptionStr = "Observing the " + self.name + ", you see the following parts: " + ", ".join(partNames) + ". \n"
            
        # Describe the materials            
        materials = self.attributes['materials']
        if (len(materials) == 0):
            microscopeDescriptionStr += "Observing the " + self.name + ", you don't observe anything particularly noteworthy."
        else:
            microscopeDescriptionStr += "Observing the " + self.name + ", you see the following: "
            materialDescs = []
            for material in materials:
                materialDescs.append(material['microscopeDesc'])                
            microscopeDescriptionStr += ", ".join(materialDescs) + ".\n"

        # Add any specific attributes to be mentioned. 
        if (len(self.attributes['microscopeModifierText']) > 0):
            microscopeDescriptionStr += " ".join(self.attributes['microscopeModifierText']) + "\n"

        # Then, recursively describe all the parts. 
        for part in self.parts:
            microscopeDescriptionStr += part.getTextObservationMicroscopic()

        # Return
        return microscopeDescriptionStr

        

    #
    #   Sprite
    #

    # Invalidate the sprite name for this object, and all objects it contains/that contain it.
    # This will force them to update their sprites on the next tick.
    def invalidateSpritesThisWorldTile(self):
        print("##### INVALIDATING SPRITES FOR " + self.name + " #####")
        print("#### LOCATION: " + str(self.attributes["gridX"]) + ", " + str(self.attributes["gridY"]) + " ####")
        # Step 1: Get the names of all objects (and any objects they contain) at this world tile
        allObjs = self.world.getObjectsAt(self.attributes["gridX"], self.attributes["gridY"], respectContainerStatus=False)
        print("#### OBJECTS: " + str(allObjs) + " ####")
        # Step 2: Invalidate the sprite names for all objects at this world tile
        for obj in allObjs:
            obj.needsSpriteNameUpdate = True
            #for containedObj in obj.getAllContainedObjectsRecursive():
            #    containedObj.needsSpriteNameUpdate = True        


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

        # Check if this sprite is invalidated and needs to be updated
        if (self.needsSpriteNameUpdate):
            # If so, then update it
            self.inferSpriteName()
            self.needsSpriteNameUpdate = False

        # First, get the name of the current object itself
        spriteNameOrNames = self.getSpriteName()        
        spriteList = []#[self.getSpriteName()]
        if (isinstance(spriteNameOrNames, list)):
            spriteList.extend(spriteNameOrNames)
        else:
            spriteList.append(spriteNameOrNames)            
        
        # Add any sprite modifiers
        spriteList.extend(self.curSpriteModifiers)

        # Then, add the name of any visible contents
        # First, check if this is a container (and it's open)
        if (self.attributes['isContainer'] and self.attributes['isOpenContainer']):
            # Make sure that the sprites for the contents should be displayed, and that this isn't handled by the sprite function rendering different sprites for full vs empty objects
            if (self.attributes['contentsVisible2D']):
                # If so, then add the contents
                for obj in self.contents:
                    # Check if this sprite is invalidated and needs to be updated
                    if (obj.needsSpriteNameUpdate):
                        # If so, then update it
                        obj.inferSpriteName()
                        obj.needsSpriteNameUpdate = False

                    # Add the sprite name of the object
                    spriteNameObj = obj.getSpriteName()
                    #print("Object name: " + obj.name + "  sprite name: " + str(spriteNameObj))
                    if (spriteNameObj != None):
                        spriteList.append(spriteNameObj) 
                        # Add any sprite modifiers
                        spriteList.extend(obj.curSpriteModifiers)

            # If the object has the 'objectToShow' attribute, like for agents showing the last object they interacted with, then add that object's sprite name
            if ('objectToShow' in self.attributes) and (self.attributes['objectToShow'] != None):
                # Get the object to show
                obj = self.attributes['objectToShow']                

                # Make sure that object's parent container is this object, otherwise discontinue
                if (obj.parentContainer == self):
                    # Check if this sprite is invalidated and needs to be updated
                    if (obj.needsSpriteNameUpdate):
                        # If so, then update it
                        obj.inferSpriteName()
                        obj.needsSpriteNameUpdate = False
                    # Add the sprite name of the object
                    spriteNameObj = obj.getSpriteName()
                    if (spriteNameObj != None):
                        spriteList.append(spriteNameObj) 
                        # Add any sprite modifiers
                        spriteList.extend(obj.curSpriteModifiers)


        # Return the sprite list
        return spriteList


    #
    #   Serialize to JSON (for saving histories, but potentially lossy -- not all object member variables are saved)    
    #
    def to_dict(self):
        # Serialize to a dictionary suitable for saving to JSON
        # Note: This is lossy, and does not save all member variables
        packed = {
            "uuid": self.uuid,
            "name": self.name,
            "type": self.type,
            "contents": [],
            "parts": [],
            "attributes": {},
            "actionHistory": None,
            "spriteNames": self.getSpriteNamesWithContents()
        }

        # Serialize contents
        for obj in self.contents:
            packed["contents"].append( {"objUUID": obj.uuid} )

        # Serialize parts
        for obj in self.parts:
            packed["parts"].append( {"objUUID": obj.uuid} )

        # Serialize attributes
        for key in self.attributes:
            value = self.attributes[key]
            # Skip any non-primitive types (but allow lists and dicts)
            if (type(value) != str) and (type(value) != int) and (type(value) != float) and (type(value) != bool) and (type(value) != list) and (type(value) != dict):                
                continue            
            packed["attributes"][key] = value            
        

        # Serialize action history, if applicable        
        if (self.actionHistory != None):
            packed["actionHistory"] = self.actionHistory.exportToJSONAbleList()                        

        return packed



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
#   Object: Cave Wall
#
# TODO: Most of the interior wall parts of this code are disabled -- so they can either be removed, or the sprite sheet can be modified to include interior walls.
class CaveWall(Object):
    
    # Constructor
    def __init__(self, world):
        # Note: Change the default sprite name to something obviously incorrect so it is obvious when it's not inferring properly. 
        Object.__init__(self, world, "wall", "cave wall", defaultSpriteName = "cave1_wall_t")

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


    # def getSpriteName(self):
    #     # Get the current sprite name, in response to the current state of the object
    #     # Normally this just returns the current sprite name, but for these cave walls (that are partially transparent), we're going to add a background object -- the cave floor. 
    #     caveFloor = "cave1_floor"
    #     return [caveFloor, self.curSpriteName]


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

        #isInterior = (hasFloorNorth and hasFloorSouth) or (hasFloorWest and hasFloorEast)
        isInterior = False

        # Corners
        # First, 4 corners
        if (hasWallNorth and hasWallEast and hasWallSouth and hasWallWest):
            # 4-way
            self.curSpriteName = "cave1_wall_int_4way"
            self.wallShape = "4way"

        # Next, 3 corners
        elif (hasWallNorth and hasWallSouth and hasWallEast):
            # 3-way, up/down/right
            self.curSpriteName = "cave1_wall_int_tbr"
            self.wallShape = "tbr"
        elif (hasWallNorth and hasWallSouth and hasWallWest):
            # 3-way, up/down/left
            self.curSpriteName = "cave1_wall_int_tbl"
            self.wallShape = "tbl"
        elif (hasWallEast and hasWallWest and hasWallNorth):
            # 3-way, left/right/up
            self.curSpriteName = "cave1_wall_int_lrt"
            self.wallShape = "lrt"
        elif (hasWallEast and hasWallWest and hasWallSouth):
            # 3-way, left/right/down
            self.curSpriteName = "cave1_wall_int_lrb"
            self.wallShape = "lrb"

        # Next, Corners (NE, NW, SE, SW)
        elif (hasWallSouth and hasWallEast):
            self.curSpriteName = "cave1_wall_tl"
            self.wallShape = "tl"
        elif (hasWallSouth and hasWallWest):
            self.curSpriteName = "cave1_wall_tr"
            self.wallShape = "tr"
        elif (hasWallNorth and hasWallEast):
            self.curSpriteName = "cave1_wall_bl"
            self.wallShape = "bl"
        elif (hasWallNorth and hasWallWest):
            self.curSpriteName = "cave1_wall_br"
            self.wallShape = "br"
        
        # Next, edges (interior)
        elif (isInterior):
            # If a wall north or south, then it's a vertical wall            
            if (hasWallNorth or hasWallSouth):
                if (hasWallNorth and hasWallSouth):
                    self.curSpriteName = "cave1_wall_int_tb"
                    self.wallShape = "v"
                elif (hasWallNorth):
                    self.curSpriteName = "cave1_wall_int_tb_opening_t"
                    self.wallShape = "v"
                elif (hasWallSouth):
                    self.curSpriteName = "cave1_wall_int_tb_opening_b"
                    self.wallShape = "v"
            # If a wall east or west, then it's a horizontal wall
            elif (hasWallEast or hasWallWest):
                if (hasWallEast and hasWallWest):
                    self.curSpriteName = "cave1_wall_int_lr"
                    self.wallShape = "h"
                elif (hasWallEast):
                    self.curSpriteName = "cave1_wall_int_lr_opening_l"
                    self.wallShape = "h"
                elif (hasWallWest):
                    self.curSpriteName = "cave1_wall_int_lr_opening_r"
                    self.wallShape = "h"
                
        # Next, edges (exterior)
        # First, check to see if there is a wall to the north or south
        elif (hasWallNorth or hasWallSouth):
            # Check to see if there is a floor to the east or west
            if (hasFloorEast):
                self.curSpriteName = "cave1_wall_l"
                self.wallShape = "l"
            elif (hasFloorWest):
                self.curSpriteName = "cave1_wall_r"
                self.wallShape = "r"
        
        # Next, check to see if there is a wall to the east or west
        elif (hasWallEast or hasWallWest):
            # Check to see if there is a floor to the north or south
            if (hasFloorNorth):
                self.curSpriteName = "cave1_wall_t"
                self.wallShape = "t"
            elif (hasFloorSouth):                
                self.curSpriteName = "cave1_wall_b"
                self.wallShape = "b"                
                
        else:
            # Catch-all -- possibly a wall with no neighbours?
            print("Unknown wall shape!")
            self.curSpriteName = self.defaultSpriteName
            self.curSpriteName = "cave1_wall_t"
            self.wallShape = "single"


        # If we reach here and still don't know the wall shape, then we'll note that it should be checked again the next tick
        if (self.wallShape == ""):
            self.needsSpriteNameUpdate = True

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName


#
#   Object: Floor
#
class CaveFloor(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "floor", "cave floor", defaultSpriteName = "cave1_rock_floor")

        # Default attributes
        self.attributes["isMovable"] = False                       # Can it be moved?

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

        self.attributes['isReadable'] = True                       # Can it be read?
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

        # Heating        
        self.attributes['heatSourceMaxTemp'] = 350                   # If it is a heat source, then this is the maximum temperature that it can reach        


    def tick(self):
        # TODO: Invalidate sprite name if this or neighbouring walls change
        if (False):
            self.needsSpriteNameUpdate = True
        
        # If the stove is on, then all of its contents gets heated towards its maximum heating temperature
        if (self.attributes["isActivated"]):            
            # Get a list of all the contents (recursive, with parts)
            contentsAndParts = self.getAllContainedObjectsAndParts(includeContents=True, includeParts=True)
            # Heat them
            heatObjects(contentsAndParts, finalTemperature = self.attributes['heatSourceMaxTemp'])            


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
            if (self.attributes["isActivated"]):
                self.curSpriteName = "house1_stove_on_open"
            else:
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
        Object.__init__(self, world, "sink", "sink", defaultSpriteName = "house1_sink_off")

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

        # Heating
        self.attributes['coolSourceMinTemp'] = -4                    # If it is a cool source, then this is the minimum temperature that it can reach


    def tick(self):
        # TODO: Invalidate sprite name if this or neighbouring walls change
        if (False):
            self.needsSpriteNameUpdate = True
        
        # If the fridge is on, then all of its contents gets cooled towards its minimum cooling temperature
        if (self.attributes["isActivated"]):            
            # Get a list of all the contents (recursive, with parts)
            contentsAndParts = self.getAllContainedObjectsAndParts(includeContents=True, includeParts=True)
            # Heat them
            coolObjects(contentsAndParts, finalTemperature = self.attributes['coolSourceMinTemp'])            


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
        Object.__init__(self, world, "microscope", "microscope", defaultSpriteName = "instruments_microscope")

        # Default attributes

        self.attributes['isUsable'] = True                       # Can this device be used with another object? (e.g. specifically through the 'use' action)

        pass        
        

    #
    #   Actions (use with)
    #
    def actionUseWith(self, patientObj):
        # Use this object on the patient object
        microscopeDescriptionStr = "You use the microscope to view the " + patientObj.name + ".\n"
        # Get the description of the object as observed under a microscope
        microscopeDescriptionStr += patientObj.getTextObservationMicroscopic()
        # Return the action response
        return ActionSuccess(True, microscopeDescriptionStr, importance=MessageImportance.HIGH)        

    #
    #   Tick
    #
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
#   Object: Spectrometer
#
class Spectrometer(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "spectrometer", "spectrometer", defaultSpriteName = "instruments_spectrometer")

        # Default attributes

        self.attributes['isUsable'] = True                       # Can this device be used with another object? (e.g. specifically through the 'use' action)

        pass        
        

    #
    #   Actions (use with)
    #
    def actionUseWith(self, patientObj):
        # Use this object on the patient object
        useDescriptionStr = "You use the spectrometer to view the " + patientObj.name + ".\n"

        # Get the patient object, and all its parts
        # def getAllContainedObjectsAndParts(self, includeContents=True, includeParts=True):
        patientObjAndParts = patientObj.getAllContainedObjectsAndParts(includeContents=False, includeParts=True)
        # Collect the materials of the object and its parts
        patientMaterials = []
        for patientObjOrPart in patientObjAndParts:
            if ("materials" in patientObjOrPart.attributes):
                patientMaterials.extend(patientObjOrPart.attributes["materials"])

        # Get the spectra of the materials
        spectra = []
        for patientMaterial in patientMaterials:
            if ("spectrum" in patientMaterial):
                spectra.append(patientMaterial["spectrum"])

        # If there are no spectra, say the results are inconclusive. 
        if (len(spectra) == 0):
            useDescriptionStr += "The results are inconclusive.\n"
            return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)

        # Calculate the spectrum (as emission)
        # First, check the length of the spectra, and create a new spectrum of that length
        spectrumLength = len(spectra[0])
        spectrum = [0] * spectrumLength
        # Then, add the spectra together
        for spectrumToAdd in spectra:
            for i in range(spectrumLength):
                # Check that it's within the bounds of the spectrum
                if (i < len(spectrumToAdd)):
                    spectrum[i] += spectrumToAdd[i]

        # Then, report the spectrum
        useDescriptionStr += "The results are as follows:\n"
        for i in range(spectrumLength):
            #useDescriptionStr += "Channel 1: " + str(spectrum[i]) + "\n"
            # report to 1 decimal place(s)
            useDescriptionStr += "- Channel " + str(i+1) + ": " + "{:.2f}".format(spectrum[i]) + "\n"

        return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)        

    #
    #   Tick
    #
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
#   Object: Thermometer
#
class Thermometer(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "thermometer", "thermometer", defaultSpriteName = "instruments_thermometer")

        # Default attributes

        self.attributes['isUsable'] = True                       # Can this device be used with another object? (e.g. specifically through the 'use' action)

        pass        
        

    #
    #   Actions (use with)
    #
    def actionUseWith(self, patientObj):
        # Use this object on the patient object
        useDescriptionStr = "You use the thermometer to measure the temperature of the " + patientObj.name + ".\n"

        # Get the patient object's temperature
        patientTemperature = patientObj.attributes["temperatureC"]
        if (patientTemperature == None):
            useDescriptionStr += "The results are inconclusive.\n"
            return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)
        
        # Report the temperature (to 1 decimal place(s)
        useDescriptionStr += "The thermometer reports a temperature of " + "{:.1f}".format(patientTemperature) + " degrees Celsius.\n"
        
        return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)        

    #
    #   Tick
    #
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
#   Object: PH Meter
#
class PHMeter(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "PH meter", "PH meter", defaultSpriteName = "instruments_ph_meter")

        # Default attributes

        self.attributes['isUsable'] = True                       # Can this device be used with another object? (e.g. specifically through the 'use' action)

        pass        
        

    #
    #   Actions (use with)
    #
    def actionUseWith(self, patientObj):
        # Use this object on the patient object
        useDescriptionStr = "You use the PH meter to investigate the " + patientObj.name + ".\n"

        # Get the patient object, and all its parts
        # def getAllContainedObjectsAndParts(self, includeContents=True, includeParts=True):
        patientObjAndParts = patientObj.getAllContainedObjectsAndParts(includeContents=False, includeParts=True)
        # Collect the materials of the object and its parts
        patientMaterials = []
        for patientObjOrPart in patientObjAndParts:
            if ("materials" in patientObjOrPart.attributes):
                patientMaterials.extend(patientObjOrPart.attributes["materials"])

        # Get the spectra of the materials
        phs = []
        for patientMaterial in patientMaterials:
            if ("ph" in patientMaterial):
                phs.append(patientMaterial["ph"])

        # If there are no spectra, say the results are inconclusive. 
        if (len(phs) == 0):
            useDescriptionStr += "The results are inconclusive.\n"
            return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)

        # Calculate the spectrum (as emission)
        # First, check the length of the spectra, and create a new spectrum of that length

        # Calculate the average PH of the materials (NOTE: this is not physically accurate)
        averagePH = sum(phs) / len(phs)

        # Report the PH (to 1 decimal place(s)
        useDescriptionStr += "The PH meter reports a PH of " + "{:.1f}".format(averagePH) + ".\n"

        return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)        

    #
    #   Tick
    #
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
#   Object: NPK Meter
#
class NPKMeter(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "NPK field test", "NPK field test", defaultSpriteName = "instruments_npk_fieldtest")

        # Default attributes

        self.attributes['isUsable'] = True                       # Can this device be used with another object? (e.g. specifically through the 'use' action)

        pass        
        

    #
    #   Actions (use with)
    #
    def actionUseWith(self, patientObj):
        # Use this object on the patient object
        useDescriptionStr = "You use the NPK field test to investigate the " + patientObj.name + ".\n"

        npk = getNPKContent(patientObj)
        totalNitrogen = npk["nitrogen"]        
        totalPhosphorus = npk["phosphorus"]
        totalPotassium = npk["potassium"]

        # If any numbers are greater than 10, then clip the results to 10
        MAX_READING = 10
        if (totalNitrogen > MAX_READING):
            totalNitrogen = MAX_READING
        if (totalPhosphorus > MAX_READING):
            totalPhosphorus = MAX_READING
        if (totalPotassium > MAX_READING):
            totalPotassium = MAX_READING

        # Report the PH (to 1 decimal place(s)
        useDescriptionStr += "The test ranges from 0 (no presence detected) to 10 (the maximum value of the test has been exceeded). \n"
        useDescriptionStr += "The screen on the field test reports the following numbers: \n"
        useDescriptionStr += " Nitrogen: " + "{:.1f}".format(totalNitrogen) + "\n"
        useDescriptionStr += " Phosphorus: " + "{:.1f}".format(totalPhosphorus) + "\n"
        useDescriptionStr += " Potassium: " + "{:.1f}".format(totalPotassium) + "\n"

        return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)        

    #
    #   Tick
    #
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
#   Object: Sampler
#
class Sampler(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "sampler", "sampler", defaultSpriteName = "instruments_sampler")

        # Default attributes

        self.attributes['isUsable'] = True                       # Can this device be used with another object? (e.g. specifically through the 'use' action)

        pass        
        

    #
    #   Actions (use with)
    #
    def actionUseWith(self, patientObj):
        # Use this object on the patient object
        useDescriptionStr = "You use the sampler to take a sample of the " + patientObj.name + ".\n The sample has been placed in your inventory.\n"

        # Create a sample of the patient
        sample = Sample(self.world, patientObj)
        petriDish = PetriDish(self.world)
        petriDish.addObject(sample)
        
        # Place the sample in the same parent container as the sampler. 
        self.parentContainer.addObject(petriDish)

        return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)        

    #
    #   Tick
    #
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
#   Object: Radiation Meter
#
class RadiationMeter(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "radiation meter", "radiation meter", defaultSpriteName = "instruments_radiation_meter")

        # Default attributes

        self.attributes['isUsable'] = True                       # Can this device be used with another object? (e.g. specifically through the 'use' action)

        pass        
        

    #
    #   Actions (use with)
    #
    def actionUseWith(self, patientObj):        
        # Use this object on the patient object        
        useDescriptionStr = "You use the radiation meter to investigate the " + patientObj.name + ".\n"

        # Get the patient object, and all its parts
        # def getAllContainedObjectsAndParts(self, includeContents=True, includeParts=True):
        patientObjAndParts = patientObj.getAllContainedObjectsAndParts(includeContents=False, includeParts=True)
        # Collect the materials of the object and its parts
        patientMaterials = []
        for patientObjOrPart in patientObjAndParts:
            if ("materials" in patientObjOrPart.attributes):
                patientMaterials.extend(patientObjOrPart.attributes["materials"])

        # Get the radiation levels of each material
        radiationLevels = []
        for patientMaterial in patientMaterials:
            if ("radiationusvh" in patientMaterial):
                radiationLevels.append(patientMaterial["radiationusvh"])

        # If there are radiation levels, say the results are inconclusive.
        # TODO: Just use background rate, then?
        if (len(radiationLevels) == 0):
            radiationLevels = [0]
            #useDescriptionStr += "The results are inconclusive.\n"
            #return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)

        # Calculate the radiation level of this object (sum of all radiation levels of each material)
        radiationLevelMicroSeivertsPerHour = sum(radiationLevels)
        # Add a random amount of background radiation, drawn from the current background radiation rate.  First, generate a number between 0-avgRadiationBackgroundLevelUSVH
        backgroundRadiation = random.random() * self.world.parameters["avgRadiationBackgroundLevelUSVH"]
        # Add the background radiation to the radiation level
        radiationLevelMicroSeivertsPerHour += backgroundRadiation

        # Also add the radiation from any objects near this location, using the inverse square law. 
        backgroundNearLocation = getRadiationLevelAroundLocation(self.world, self.attributes["gridX"], self.attributes["gridY"], excludeObject=patientObj, windowSize=5)
        radiationLevelMicroSeivertsPerHour += backgroundNearLocation

        # TODO: Also add the radiation from any other objects near this location.
                
        # Report the radiation level (to 2 decimal place(s)
        useDescriptionStr += "The radiation meter reports a level of " + "{:.2f}".format(radiationLevelMicroSeivertsPerHour) + " micro Seiverts per hour.\n"
        useDescriptionStr += "DEBUG:\n Background radiation: " + "{:.2f}".format(backgroundRadiation) + " micro Seiverts per hour.\n"
        useDescriptionStr += "DEBUG:\n Background near location: " + "{:.2f}".format(backgroundNearLocation) + " micro Seiverts per hour.\n"

        return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)
    #
    #   Tick
    #
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
#   Object: Petri Dish (container)
#
class PetriDish(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "petri dish", "petri dish", defaultSpriteName = "instruments_petri_dish_empty")

        self.attributes["isMovable"] = True                       # Can it be moved?
        self.attributes["isPassable"] = True                      # Agen't can't walk over this

        # Container
        self.attributes['isContainer'] = True                      # Is it a container?
        self.attributes['isOpenable'] = False                      # Can not be opened (things are stored in the open pot)
        self.attributes['isOpenContainer'] = True                  # If it's a container, then is it open?
        self.attributes['containerPrefix'] = "in"                  # Container prefix (e.g. "in" or "on")            
        self.attributes['contentsVisible2D'] = False               # If it is a container, do we render the contents in the 2D representation, or is that already handled (e.g. for pots/jars, that render generic contents if they contain any objects)

    def tick(self):
        # Call superclass
        Object.tick(self)    

    # Sprite
    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return
        # Infer sprite based on whether empty/non-empty
        if (len(self.contents) == 0):
            self.curSpriteName = "instruments_petri_dish_empty"
        else:
            self.curSpriteName = "instruments_petri_dish_full"

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName


#
#   Object: Sample
#   A Sample is a special type of object that clones the attributes of another parent object, but not its contents. 
class Sample(Object):
    # Constructor
    def __init__(self, world, parentObject):
        # Default sprite name
        Object.__init__(self, world, "sample", "sample of " + parentObject.name, defaultSpriteName = "instruments_sample")

        # Materials
        # Deep copy the materials from the parent object
        self.attributes["materials"] = copy.deepcopy(parentObject.attributes["materials"])

        # Parts (for composite objects -- similar to containers)
        self.parts = []                                            
        # For each part in the parent object, create a new part in this object
        for parentPart in parentObject.parts:
            # Create a new part, and add it to this object
            newPart = Sample(self.world, parentPart)
            self.parts.append(newPart)

        # Poison/health attributes
        self.attributes['isPoisonous'] = parentObject.attributes['isPoisonous'] if ('isPoisonous' in parentObject.attributes) else False
        self.attributes['temperatureC'] = parentObject.attributes['temperatureC'] if ('temperatureC' in parentObject.attributes) else 20.0

        # Remove the parent object's contents
        self.contents = []



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

    # Add readable text (e.g. for a plaque on the statue)
    def addReadableText(self, text):
        self.attributes["isReadable"] = True
        self.attributes['document'] = text

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
        self.attributes['isShovelable'] = True                     # Can it be shoveled?

        # By default, it contains Dirt, which can be removed by shovelling
        dirt = self.world.createObject("Dirt")
        self.addObject(dirt, force=True)
        

    #def __init__(self, success, message, generatedItem = None, importance = MessageImportance.NORMAL):
    def useWithShovelResult(self):
        # First, check to see if the object already has a hole -- if so, it can't be shovelled. 
        if (self.attributes["hasHole"]):
            return UseWithSuccess(False, "There is already a hole here.")

        # Otherwise, we can dig a hole
        #self.attributes["hasHole"] = True

        # Generate 'dirt' object. 
        #generatedObjects = [self.world.createObject("Dirt")]
        # Find 'dirt' object contained in this object        
        generatedObjects = []
        dirtList = self.getContainedObjectByType("dirt", maxMatches=1, recursive=False, respectContainerStatus=False)
        if (len(dirtList) == 0):
            # No dirt found -- this shouldn't happen
            return UseWithSuccess(False, "Error: No dirt found in soil tile. This should never happen.")
        else:
            # Dirt found -- remove it from the soil tile, and add it to the list of generated objects
            dirt = dirtList[0]
            self.removeObject(dirt)
            generatedObjects.append(dirt)


        # Return success
        return UseWithSuccess(True, "You dig a hole in the soil, creating a hole and dirt.", generatedObjects)
        

    def tick(self):
        # Call superclass
        Object.tick(self)

        # Check to see if this object contains dirt (in which case, the 'hasHole' attribute should be False)
        hasDirt = False
        for obj in self.contents:
            if (obj.type == "dirt"):
                hasDirt = True
                break
        if (hasDirt):
            self.attributes["hasHole"] = False
        else:
            self.attributes["hasHole"] = True


        # Check to see if the object has a hole (and if so, change the name, and add the sprite modifier)
        if (self.attributes["hasHole"]):
            # Add the sprite modifier
            self.curSpriteModifiers.add("placeholder_hole")            
            # Change the name of the object to "hole"
            if (self.name != "hole"):
                self.name = "hole"
                # If so, then we need to update the sprite name
                self.needsSpriteNameUpdate = True

            # Allow the object to be a container, and be open
            self.attributes["isContainer"] = True
            self.attributes["isOpenContainer"] = True
        else:
            # No sprite modifier needed (they are cleared each tick automatically)
            # Change the name of the object to "soil"
            if (self.name != "soil"):
                self.name = "soil"
                self.needsSpriteNameUpdate = True

            # Object is not a container, and not open
            self.attributes["isContainer"] = False
            self.attributes["isOpenContainer"] = False


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
    def __init__(self, world, color:str=""):
        # Default sprite name
        Object.__init__(self, world, "mushroom", "mushroom", defaultSpriteName = "forest1_mushroom_pink")

        #self.attributes["color"] = "pink"                           # Color of the mushroom (valid: "yellow", "pink", "red", "green")
        # Randomly choose a color
        if (color == ""):
            self.attributes["color"] = random.choice(["yellow", "pink", "red", "green"])
        else:
            self.attributes["color"] = color

        # Food attributes
        self.attributes['isEdible'] = True                         # Can it be eaten?

        # Poison/health attributes
        self.attributes['isPoisonous'] = False                     # Is it poisonous?
        # Make red mushrooms poisonous
        #if (self.attributes["color"] == "red"):
        #    self.attributes['isPoisonous'] = True
        
    
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
    #   Text Observations
    #
    def getTextDescription(self):
        # Get a text description of this object
        return self.attributes["color"] + " " + self.name 


#
#   Object: Mold
#
class Mold(Object):
    # Constructor
    def __init__(self, world, color:str=""):
        # Default sprite name
        Object.__init__(self, world, "mold", "mold", defaultSpriteName = "forest1_mushroom_pink")

        self.attributes['isLiving'] = True                         # Is it alive?
        # Most properties populated from the external spreadsheet
            
    def tick(self):
        # Call superclass
        Object.tick(self)

        # Check to make sure this living thing is not subjected to extreme temperatures that may kill it
        livingTemperatureRangeCheck(self)

        # If it's dead, then it's no longer poisonous
        if (self.attributes['isLiving'] == False):
            self.attributes['isPoisonous'] = False
            # Make a note of this in the microscope modifier text.
            ## TODO: This should be refactored -- perhaps only do it in response to a 'generateMicroscopeDesc' string? (i.e. only when the player looks at it)
            self.attributes['microscopeModifierText'].append("This mold appears dead.")




#
#   Object: Pot (container)
#
class Pot(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "pot", "pot", defaultSpriteName = "placeholder_pot_empty")

        self.attributes["isMovable"] = True                       # Can it be moved?
        self.attributes["isPassable"] = True                      # Agen't can't walk over this

        # Container
        self.attributes['isContainer'] = True                      # Is it a container?
        self.attributes['isOpenable'] = False                      # Can not be opened (things are stored in the open pot)
        self.attributes['isOpenContainer'] = True                  # If it's a container, then is it open?
        self.attributes['containerPrefix'] = "in"                  # Container prefix (e.g. "in" or "on")            
        self.attributes['contentsVisible2D'] = False               # If it is a container, do we render the contents in the 2D representation, or is that already handled (e.g. for pots/jars, that render generic contents if they contain any objects)        

    def tick(self):
        # Call superclass
        Object.tick(self)    

    # Sprite
    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return
        # Infer sprite based on whether empty/non-empty
        if (len(self.contents) == 0):
            self.curSpriteName = "placeholder_pot_empty"
        elif (len(self.contents) == 1):
            self.curSpriteName = "placeholder_pot_full1"
        elif (len(self.contents) == 2):
            self.curSpriteName = "placeholder_pot_full2"
        else:
            self.curSpriteName = "placeholder_pot_full3"

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName


#
#   Object: Jar (container)
#
class Jar(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "jar", "jar", defaultSpriteName = "placeholder_jar_empty")

        self.attributes["isMovable"] = True                       # Can it be moved?
        self.attributes["isPassable"] = True                      # Agen't can't walk over this

        # Container
        self.attributes['isContainer'] = True                      # Is it a container?
        self.attributes['isOpenable'] = False                      # Can not be opened (things are stored in the open pot)
        self.attributes['isOpenContainer'] = True                  # If it's a container, then is it open?
        self.attributes['containerPrefix'] = "in"                  # Container prefix (e.g. "in" or "on")            
        self.attributes['contentsVisible2D'] = False               # If it is a container, do we render the contents in the 2D representation, or is that already handled (e.g. for pots/jars, that render generic contents if they contain any objects)

        # Auto fill
        self.autoFillCheckForObjectName = None
        self.autoFillFillObjectName = None
        self.lastAddedCount = 0
        self.replenishTime = 5

    # If we want this object to autofill (i.e. perpetually fill with a supply of an object), set it here. 
    def setAutoFill(self, checkObjectName:str, fillObjectName:str, minCount:int, replenishTime:int=8):
        self.autoFillCheckForObjectName = checkObjectName
        self.autoFillFillObjectName = fillObjectName
        self.autoFillMinCount = minCount
        self.replenishTime = replenishTime
        self.lastAddedCount = 0
        


    def tick(self):
        # Call superclass
        Object.tick(self)    

        # Auto fill
        #if (self.autoFillObjectName != None and self.autoFillMinCount != None):
        if (self.autoFillCheckForObjectName != None) and (self.autoFillFillObjectName != None) and (self.autoFillMinCount != None):
            # Count how much of the object is contained within the root level of the contents
            count = 0
            for obj in self.contents:
                if (obj.name == self.autoFillCheckForObjectName):
                    count += 1
            
            # Fill up to the minimum count
            if (count < self.autoFillMinCount):
                # Check to see if the last added count is zero
                if (self.lastAddedCount <= 0):
                    # Add one more
                    objToAdd = self.world.createObject(self.autoFillFillObjectName)
                    self.addObject(objToAdd, force=True)
                    # Tick the object to update its sprite
                    objToAdd.tick()                    
                    # Invalidate object sprite
                    self.needsSpriteNameUpdate = True
                    # Tick 
                    self.lastAddedCount = self.replenishTime     # Wait a few ticks before adding the next one
                else:
                    self.lastAddedCount -= 1




    # Sprite
    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return
        # Infer sprite based on whether empty/non-empty
        if (len(self.contents) == 0):
            self.curSpriteName = "placeholder_jar_empty"
        elif (len(self.contents) == 1):
            self.curSpriteName = "placeholder_jar_full1"
        elif (len(self.contents) == 2):
            self.curSpriteName = "placeholder_jar_full2"
        else:
            self.curSpriteName = "placeholder_jar_full3"

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName



#
#   Object: Shovel (tool)
#
class Shovel(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "shovel", "shovel", defaultSpriteName = "placeholder_shovel")

        self.attributes["isMovable"] = True                       # Can it be moved?
        self.attributes["isPassable"] = True                      # Agen't can't walk over this

        self.attributes["isUsable"] = True                        # Can it be used?

    #
    #   Actions (use with)
    #
    def actionUseWith(self, patientObj):
        # Use this object on the patient object

        # Check if the patient object has the 'isShovelable' attribute
        if (not patientObj.attributes["isShovelable"]):
            # Can't use the shovel on this object
            return ActionSuccess(False, "You can't use the shovel on that.")

        
        # Run the 'useWithShovelResult' function on the patient object
        result = patientObj.useWithShovelResult()

        # Return the result
        return result


    def tick(self):
        # Call superclass
        Object.tick(self)    


#
#   Object: Seed (placeholder object -- plants should probably have their own sprite class)
#
class Seed(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "seed", "seed", defaultSpriteName = "placeholder_seed")

        self.attributes["isMovable"] = True                       # Can it be moved?
        self.attributes["isPassable"] = True                      # Agen't can't walk over this

        self.attributes["sproutTime"] = -1                        # How many ticks until the seed sprouts?

    def tick(self):
        # Call superclass
        Object.tick(self)    

        # Check if the conditions for the seed to grow have been met
        # Condition 1: Check that the seed is contained in a 'SoilTile' object
        inSoilTile = False
        hasHole = False
        if (self.parentContainer is not None):
            #print("*** Parent Container Attributes: " + str(self.parentContainer.attributes))
            if (self.parentContainer.type == "soil"):
                inSoilTile = True

        # Condition 2: Also check that the hole is filled                        
        if (self.parentContainer is not None):
            if (self.parentContainer.attributes['hasHole'] == True):
                hasHole = True

        # Debug information
        #print("*** Seed: inSoilTile = " + str(inSoilTile) + ", hasHole = " + str(hasHole) + ", sproutTime: " + str(self.attributes["sproutTime"]))

        # If the conditions have been met, continue the growth process
        if (inSoilTile and not hasHole):
            # Perform action based on sprout time
            if (self.attributes["sproutTime"] == 0):
                #print("Turn into plant")
                # Turn into plant
                plant = None
                # Randomly choose one of 4 plants to turn into
                rand = random.randint(0, 3)
                if (rand == 0):
                    plant = self.world.createObject("mushroom1")
                elif (rand == 1):
                    plant = self.world.createObject("mushroom2")
                elif (rand == 2):
                    plant = self.world.createObject("mushroom3")
                elif (rand == 3):
                    plant = self.world.createObject("mushroom4")
                
                # Replace self with the plant
                #self.replaceSelfWithObject(plant)
                # Return, since this object is no longer valid
                # Add the plant to the same world location as the soil tile
                #self.world.addObjectToLocation(plant, self.parentContainer.parentContainer)
                #def addObject(self, x, y, layer, object:Object):
                seedLocation = self.getWorldLocation()
                self.world.addObject(seedLocation[0], seedLocation[1], Layer.OBJECTS, plant)

                # Remove self
                self.world.removeObject(self)

                return

            elif (self.attributes["sproutTime"] == -1):                
                #print("Random sprout time")
                # Sprout time was not set -- so this is the first time the conditions have been met. Set sprout time to a random value between 10 and 20 ticks
                self.attributes["sproutTime"] = random.randint(10, 20)
            else:
                #print("Decrement sprout time")
                # If the sprout time has already been set, then decrement it
                # How fast the plant grows is determined by the quality of its soil. The better the soil, the faster it grows.
                # Soil quality is determined by NPK content. The higher the NPK content, the better the soil.  Use the ScienceHelper.getNPKContent() to calculate this. 
                npk = getNPKContent(self.parentContainer)
                sumNPK = npk["nitrogen"] + npk["phosphorus"] + npk["potassium"]
                # NPK is nominally between 0-10, but most of the soil in DiscoveryWorld has starting values between 1-4 for each.  Call the nominal max growth rate at 5.  5*3 = 15, so divide by 15 to get a growth rate. 
                growthRate = sumNPK / 30.0
                # Randomly generate a number, and see if that number is less than the growth rate. If it is, then the plant grows.
                randGrowth = random.random()
                if (randGrowth < growthRate):
                    self.attributes["sproutTime"] -= 1
                else:
                    # Plant did not grow this cycle
                    pass
                    

        
#
#   Object: Fertilizer Pellet
#
class FertilizerPellet(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "fertilizer", "fertilizer", defaultSpriteName = "instruments_fertilizer_pellet")

        self.attributes["isMovable"] = True                       # Can it be moved?
        self.attributes["isPassable"] = True                      # Agen't can't walk over this

        self.attributes["absorbTime"] = 8                         # How many ticks until it absorbs into the soil?

    def tick(self):
        # Call superclass
        Object.tick(self)    

        # Check if the conditions for the seed to grow have been met
        # Condition 1: Check if the fertilizer pellet is contained within soil
        nearDirt = None

        # Check if parent container is soil with dirt in it
        if (self.parentContainer is not None):            
            if (self.parentContainer.type == "soil"):
                # Get any contained dirt
                parentContinerObjs = self.parentContainer.contents
                for obj in parentContinerObjs:
                    if (obj.type == "dirt"):
                        nearDirt = obj
                        break

        # OR, check if the fertilizer pellet is in no container, but is on the same tile as dirt. 
        if (self.parentContainer is None) and (nearDirt is None):
            # Get the tile that this object is on            
            objectsAtTile = self.world.getObjectsAt(self.attributes["gridX"], self.attributes["gridY"])
            for object in objectsAtTile:
                if (object.type == "dirt"):
                    nearDirt = object
                    break

        # If the conditions have been met, continue the absorption process
        if (nearDirt is not None):
            self.attributes["absorbTime"] -= 1

            # If the absorb time is 0, then absorb into the soil
            if (self.attributes["absorbTime"] == 0):
                #print("Absorb into soil")

                # Increase the N/P/K of the dirt material by one
                found = False
                for material in nearDirt.attributes["materials"]:
                    if (material["MaterialName"] == "soil"):
                        material["nitrogen"] += 1
                        material["phosphorus"] += 1
                        material["potassium"] += 1
                        break
                        
                # Remove the fertilizer pellet from the world
                self.world.removeObject(self)
                return


#
#   Object: Fertilizer Bag (container, infinite)
#
class FertilizerBag(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "fertilizer bag", "fertilizer bag", defaultSpriteName = "instruments_fertilizer_bag")

        self.attributes["isMovable"] = True                       # Can it be moved?
        self.attributes["isPassable"] = True                      # Agen't can't walk over this

        # Container
        self.attributes['isContainer'] = True                      # Is it a container?
        self.attributes['isOpenable'] = False                      # Can not be opened (things are stored in the open pot)
        self.attributes['isOpenContainer'] = True                  # If it's a container, then is it open?
        self.attributes['containerPrefix'] = "in"                  # Container prefix (e.g. "in" or "on")            
        self.attributes['contentsVisible2D'] = False               # If it is a container, do we render the contents in the 2D representation, or is that already handled (e.g. for pots/jars, that render generic contents if they contain any objects)

    def tick(self):
        # Call superclass
        Object.tick(self)    

        # If the bag contains less than 3 fertilizer pellets, then add enough to make 3
        numFertilizerPellets = 0
        for obj in self.contents:
            if (obj.type == "fertilizer"):
                numFertilizerPellets += 1

        if (numFertilizerPellets < 3):
            # Add enough fertilizer pellets to make 3
            for i in range(3 - numFertilizerPellets):
                fertilizerPellet = self.world.createObject("FertilizerPellet")
                self.addObject(fertilizerPellet, force=True)
                fertilizerPellet.tick()


    # Sprite
    # Updates the current sprite name based on the current state of the object
    # def inferSpriteName(self, force:bool=False):
    #     if (not self.needsSpriteNameUpdate and not force):
    #         # No need to update the sprite name
    #         return

    #     # This will be the next last sprite name (when we flip the backbuffer)
    #     self.tempLastSpriteName = self.curSpriteName



# #
# #   Object: Hole (placeholder)
# #
# class Hole(Object):
#     # Constructor
#     def __init__(self, world):
#         # Default sprite name
#         Object.__init__(self, world, "hole", "hole", defaultSpriteName = "placeholder_hole")

#         self.attributes["isMovable"] = False                       # Can it be moved?
#         self.attributes["isPassable"] = True                      # Agen't can't walk over this

#     def tick(self):
#         # Call superclass
#         Object.tick(self)    


#
#   Object: Dirt Pile (placeholder)
#
class Dirt(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "dirt", "dirt", defaultSpriteName = "placeholder_dirt_pile")

        self.attributes["isMovable"] = True                       # Can it be moved?
        self.attributes["isPassable"] = True                      # Agen't can't walk over this

    #
    #   Material Property Initialization
    #
    def initializeMaterialProperties(self, materialIndexDict):
        # Randomly choose the material type ("soil_good", "soil_medium", "soil_poor")
        soilTypes = ["soil_good", "soil_medium", "soil_poor"]
        # Randomly choose one
        randIdx = random.randint(0, len(soilTypes) - 1)
        randMaterialName = soilTypes[randIdx]
        # Set the material type        
        if (randMaterialName in materialIndexDict):
            material = materialIndexDict[randMaterialName]            
            self.attributes["materials"].append( copy.deepcopy(material) )
        else:
            print("Error: Material '" + randMaterialName + "' not found in materialIndexDict")
            print("Material Index Dict: " + str(materialIndexDict))
            exit(1)
                        
        pass


    def tick(self):
        # Call superclass
        Object.tick(self) 


#
#   Object: Flower (container)      # (TODO? This one is just a decorative placeholder?)
#
class FlowerPot(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "flowerpot", "flowerpot", defaultSpriteName = "generated_flowerpot")

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
#   Object: Radioactive Check Source
#


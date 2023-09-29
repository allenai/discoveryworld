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

    #
    #   Update/Tick
    #
    def tick(self):
        # Update the object
        
        # Infer current name
        if (self.firstInit):
            self.firstInit = False
            self.inferSpriteName(force=True)
        else:
            self.inferSpriteName()

        

    #
    #   Sprite
    #

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

#
#   Object: Grass
#
class Grass(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "grass", "grass", defaultSpriteName = "forest1_grass")
    
    def tick(self):
        # Call superclass
        Object.tick(self)


#
#   Object: Wall
#
class Wall(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "wall", "wall", defaultSpriteName = "house1_test1")

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
            if object.type == "wall":
                return (True, object.wallShape)
        # If we get here, there are no walls
        return (False, "")

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

        # Corners
        if (hasWallSouth and hasWallEast):
            self.curSpriteName = "house1_wall_tl"
            self.wallShape = "tl"
        elif (hasWallSouth and hasWallWest):
            self.curSpriteName = "house1_wall_tr"
            self.wallShape = "tr"
        elif (hasWallNorth and hasWallEast):
            self.curSpriteName = "house1_wall_bl"
            self.wallShape = "bl"
        elif (hasWallNorth and hasWallWest):
            self.curSpriteName = "house1_wall_br"
            self.wallShape = "br"
        # Edges
        elif (hasWallNorth or hasWallSouth):
            # Check to see what kind of wall the immediate north wall is
            if (wallShapeNorth == "tl" or wallShapeNorth == "l"):
                self.curSpriteName = "house1_wall_l"
                self.wallShape = "l"
            elif (wallShapeNorth == "tr" or wallShapeNorth == "r"):
                self.curSpriteName = "house1_wall_r"
                self.wallShape = "r"
            else:
                # Unknown?
                print("Unknown!")
                self.curSpriteName = self.defaultSpriteName
                #pass

        elif (hasWallEast or hasWallWest):
            # Check to see what kind of wall the immediate east wall is
            if (wallShapeEast == "tr" or wallShapeEast == "t"):
                self.curSpriteName = "house1_wall_t"
                self.wallShape = "t"
            elif (wallShapeEast == "br" or wallShapeEast == "b"):
                self.curSpriteName = "house1_wall_b"
                self.wallShape = "b"
            else:
                #print("Can't find at location (" + str(self.attributes["gridX"]) + ", " + str(self.attributes["gridY"]) + ")")
                # Have to traverse further -- keep going east until we (a) stop finding walls, or (b) find a wall that has self.wallShape populated
                if (hasWallWest):
                    #print("Can't find at location (" + str(self.attributes["gridX"]) + ", " + str(self.attributes["gridY"]) + ")")
                    # Keep going west until we find a wall that has self.wallShape populated (or, hit the edge of the grid)
                    for i in range(self.attributes["gridX"] - 1, -1, -1):
                        hasWallWest, wallShapeWest = self._hasWall(i, self.attributes["gridY"])
                        #print("WEST: Checking (" + str(i) + ", " + str(self.attributes["gridY"]) + ")" + " hasWallWest: " + str(hasWallWest) + " wallShapeWest: " + str(wallShapeWest))
                        if (hasWallWest and wallShapeWest != ""):
                            # Found a wall that has self.wallShape populated
                            if (wallShapeWest == "tl" or wallShapeWest == "t"):
                                self.curSpriteName = "house1_wall_t"
                                self.wallShape = "t"
                            elif (wallShapeWest == "bl" or wallShapeWest == "b"):
                                self.curSpriteName = "house1_wall_b"
                                self.wallShape = "b"
                            break
                        elif (not hasWallWest):
                            # No longer within the building -- this should not happen. Default to "t"
                            #print ("No longer within building!")
                            self.curSpriteName = self.defaultSpriteName
                            self.wallShape = ""
                            break

                elif (hasWallEast):
                    # Keep going east until we find a wall that has self.wallShape populated (or, hit the edge of the grid)
                    for i in range(self.attributes["gridX"] + 1, self.world.sizeX):
                        #hasWallEast, wallShapeEast = self._hasWall(i, self.attributes["gridY"])
                        print("EAST: Checking (" + str(i) + ", " + str(self.attributes["gridY"]) + ")" + " hasWallEast: " + str(hasWallEast) + " wallShapeEast: " + str(wallShapeEast))
                        if (hasWallEast and wallShapeEast != ""):
                            # Found a wall that has self.wallShape populated
                            if (wallShapeEast == "tr" or wallShapeEast == "t"):
                                self.curSpriteName = "house1_wall_t"
                                self.wallShape = "t"
                            elif (wallShapeEast == "br" or wallShapeEast == "b"):
                                self.curSpriteName = "house1_wall_b"
                                self.wallShape = "b"
                            break
                        elif (not hasWallEast):
                            # No longer within the building -- this should not happen. Default to "t"
                            #print ("No longer within building!")
                            self.curSpriteName = self.defaultSpriteName
                            self.wallShape = ""
                            break


                else:
                    # Unknown?  Lone wall?
                    print("Unknown! (EW) " + wallShapeEast + " " + wallShapeWest)
                    self.curSpriteName = self.defaultSpriteName
                #pass

                # Show result:
                #print("Result at location (" + str(self.attributes["gridX"]) + ", " + str(self.attributes["gridY"]) + ") is: " + str(self.curSpriteName) + " " + str(self.wallShape))

            
        # Else:
        else:
            self.curSpriteName = self.defaultSpriteName

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName

        
#
#   Object: Stove
#
class Stove(Object):
    # Constructor
    def __init__(self, world):
        defaultSpriteName = "stove_off"
        Object.__init__(self, world, "stove", "stove", defaultSpriteName = "house1_stove_off")

        # Default attributes
        self.attributes["activated"] = False
        self.attributes["open"] = False

        

    def tick(self):
        # TODO: Invalidate sprite name if this or neighbouring walls change
        if (False):
            self.needsSpriteNameUpdate = True

        # TODO

        # Randomly turn on/off
        if (random.randint(0, 100) < 5):
            self.attributes["activated"] = not self.attributes["activated"]
            self.needsSpriteNameUpdate = True
        
        # Randomly open/close
        if (random.randint(0, 100) < 5):
            self.attributes["open"] = not self.attributes["open"]
            self.needsSpriteNameUpdate = True
        


        # Call superclass
        Object.tick(self)

    # Sprite
    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return

        # If the stove is open, then we need to use the open sprite
        if (self.attributes["open"]):
            self.curSpriteName = "house1_stove_open"
        else:
            if (self.attributes["activated"]):
                self.curSpriteName = "house1_stove_on"
            else:
                self.curSpriteName = "house1_stove_off"

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName

# World.py

import SpriteLibrary
from Layer import Layer
from ObjectModel import Object


# Storage class for the world (including the full environment grid)
class World:
    # Constructor
    def __init__(self, assetPath, filenameSpriteIndex):
        # World size (in tiles)
        self.sizeX = 32
        self.sizeY = 32

        # Load sprites
        self.spriteLibrary = SpriteLibrary.SpriteLibrary(assetPath, filenameSpriteIndex)

        # Initialize grid
        self.grid = [[self.mkBlankGridTile() for x in range(self.sizeX)] for y in range(self.sizeY)]

        # Load world data
        # TODO


    #
    #   Grid
    #

    # Create a blank grid tile
    def mkBlankGridTile(self):
        gridTile = {
            "layers": {}
        }

        for layer in Layer:
            gridTile["layers"][layer] = []

        return gridTile


    # Add an object to the world
    def addObject(self, x, y, layer, object:Object):
        # Bound checking: Make sure the object is within the world bounds
        #if x < 0 or x >= self.sizeX or y < 0 or y >= self.sizeY:
        if (self.isWithinBounds(x, y) == False):
            print("Error: Object out of bounds: " + str(x) + ", " + str(y))
            return False


        # Remove the object from its current container
        object.removeSelfFromContainer()
        
        # Set the object's position
        object.setWorldLocation(x, y)

        # World, building, and furniture layers are overwrite layers (i.e. they can hold only a single object)
        # if layer == Layer.WORLD or layer == Layer.BUILDING or layer == Layer.FURNITURE:
        #     self.grid[x][y]["layers"][layer] = []
        #     self.grid[x][y]["layers"][layer].append(object)
        # # Objects layer is an additive layer (i.e. it can hold multiple objects)
        # elif layer == Layer.OBJECTS:
        #     self.grid[x][y]["layers"][layer].append(object)
        # # Player layer is a special layer that can only hold a single object
        # elif layer == Layer.AGENT:
        #     self.grid[x][y]["layers"][layer] = []
        #     self.grid[x][y]["layers"][layer].append(object)

        # All layers can hold multiple objects (prevents objects suddenly disappearing when a new object is moved to the same world location)
        if (layer == Layer.WORLD) or (layer == Layer.BUILDING) or (layer == Layer.FURNITURE) or (layer == Layer.OBJECTS) or (layer == Layer.AGENT):
           self.grid[x][y]["layers"][layer].append(object) 
        else:
            print("Error: Invalid layer: " + str(layer))
            return False


    # Get all objects at a given position
    def getObjectsAt(self, x, y, respectContainerStatus=False):
        # Bound checking: Make sure the object is within the world bounds
        if x < 0 or x >= self.sizeX or y < 0 or y >= self.sizeY:
            print("Error: Object out of bounds: " + str(x) + ", " + str(y))
            return []

        #print("\t\t\tGetting objects at (" + str(x) + ", " + str(y) + ")")
        # Get the objects
        objects = []
        for layer in Layer:            
            #objects += self.grid[x][y]["layers"][layer]
            objsToAdd = self.grid[x][y]["layers"][layer]
            if (len(objsToAdd) > 0):
                #print("\t\t\t\tLayer: " + str(layer) + " (" + str(len(objsToAdd)) + " objects)") 
                for obj in objsToAdd:
                    objects.append(obj)
                    contents = obj.getAllContainedObjectsRecursive(respectContainerStatus=respectContainerStatus)
                    if (len(contents) > 0):
                        #print("Contents of " + obj.name + ": " + str(contents))
                        objects += contents
                    
                    

            #objects += objsToAdd


            #for obj in self.grid[x][y]["layers"][layer]:
            #    objects += obj.getAllContainedObjectsRecursive(respectContainerStatus=True)

        return objects

    # Remove an object from the world
    def removeObject(self, object:Object):
        # First, get the object's position (stored internally in that object)
        objX, objY = object.getWorldLocation()
        # Then, set the object's position to -1 (i.e. not in the world)
        object.setWorldLocation(-1, -1)

        # Remove the object from the world
        if (objX >= 0) and (objY >= 0):
            for layer in Layer:
                if object in self.grid[objX][objY]["layers"][layer]:
                    self.grid[objX][objY]["layers"][layer].remove(object)
                    return True
        
        # If we reach here, something went wrong -- the object could not be removed from the world.
        print("WARNING: Object could not be removed from the world (" + object.name + ") at (" + str(objX) + ", " + str(objY) + ")")
        return False


    #
    #   Traversability
    #
    
    # Check if a tile is passable
    # Returns (bool, obj) where:
    #  - bool is true if the tile is passable, and obj is the first impassable object encountered at that location. 
    #  - If the tile is passable, obj is None.
    def isPassable(self, x, y):
        # Bound checking: Make sure the object is within the world bounds
        if x < 0 or x >= self.sizeX or y < 0 or y >= self.sizeY:
            #print("Error: Object out of bounds: " + str(x) + ", " + str(y))
            return False

        # Check if the tile is passable
        # Collect all the objects across all layers
        allObjs = self.getObjectsAt(x, y)
        # Check if any of the objects are impassable
        for object in allObjs:
            if (not object.attributes["isPassable"]):
                return (False, object)

        # If we reach here, the tile is passable
        return (True, None)


    #
    #   Bound Checking
    #

    # Returns true if the specified position is within the world grid bounds
    def isWithinBounds(self, x, y):
        return (x >= 0) and (x < self.sizeX) and (y >= 0) and (y < self.sizeY)

    #
    #   World update
    #
    def tick(self):
        # Update all objects in the world

        # First, reset whether each object has had its tick() function called this tick
        for x in range(self.sizeX):
            for y in range(self.sizeY):
                for layer in Layer:
                    for object in self.grid[x][y]["layers"][layer]:
                        object.tickCompleted = False


        # Then, call tick() on each object in the world
        for x in range(self.sizeX):
            for y in range(self.sizeY):
                for layer in Layer:
                    for object in self.grid[x][y]["layers"][layer]:
                        object.tick()


    #
    #   Rendering
    #   
    def render(self, window, cameraX, cameraY):
        #world.spriteLibrary.displaySprite("house1_house_corner_tl", window, 0, 0)
        # Render the world
        for y in range(self.sizeY):
            for x in range(self.sizeX):

                # print("Rendering: " + str(x) + ", " + str(y))
                # for layer in self.grid[x][y]["layers"].values():
                #     for object in layer:
                #         # print object and sprite names
                #         print("\t" + object.name + " (" + str(object.getSpriteNamesWithContents()) + ")")

                # Render the world layer
                for object in self.grid[x][y]["layers"][Layer.WORLD]:
                    #print("Rendering: " + object.name)
                    #self.spriteLibrary.renderSprite(window, object.getSpriteName(), x * 32 - cameraX, y * 32 - cameraY)
                    for spriteName in object.getSpriteNamesWithContents():
                        self.spriteLibrary.renderSprite(window, spriteName, x * 32 - cameraX, y * 32 - cameraY)

                # Render the building layer
                for object in self.grid[x][y]["layers"][Layer.BUILDING]:
                    #print("Rendering: " + object.name)
                    #self.spriteLibrary.renderSprite(window, object.getSpriteName(), x * 32 - cameraX, y * 32 - cameraY)
                    for spriteName in object.getSpriteNamesWithContents():
                        self.spriteLibrary.renderSprite(window, spriteName, x * 32 - cameraX, y * 32 - cameraY)

                # Render the furniture layer
                for object in self.grid[x][y]["layers"][Layer.FURNITURE]:
                    #print("Rendering: " + object.name)
                    #self.spriteLibrary.renderSprite(window, object.getSpriteName(), x * 32 - cameraX, y * 32 - cameraY)
                    for spriteName in object.getSpriteNamesWithContents():
                        self.spriteLibrary.renderSprite(window, spriteName, x * 32 - cameraX, y * 32 - cameraY)

                # Render the objects layer
                for object in self.grid[x][y]["layers"][Layer.OBJECTS]:
                    #print("Rendering: " + object.name)
                    #self.spriteLibrary.renderSprite(window, object.getSpriteName(), x * 32 - cameraX, y * 32 - cameraY)
                    for spriteName in object.getSpriteNamesWithContents():
                        self.spriteLibrary.renderSprite(window, spriteName, x * 32 - cameraX, y * 32 - cameraY)

                # Render the player layer
                for object in self.grid[x][y]["layers"][Layer.AGENT]:
                    #print("Rendering: " + object.name)
                    #self.spriteLibrary.renderSprite(window, object.getSpriteName(), x * 32 - cameraX, y * 32 - cameraY)
                    for spriteName in object.getSpriteNamesWithContents():
                        self.spriteLibrary.renderSprite(window, spriteName, x * 32 - cameraX, y * 32 - cameraY)



    #
    #   Pathfinding
    #   

    # Get the next step in the path from one location to another
    #def getNextStep(self, fromLocation, toLocation):

    


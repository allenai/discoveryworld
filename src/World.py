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
        if x < 0 or x >= self.sizeX or y < 0 or y >= self.sizeY:
            print("Error: Object out of bounds: " + str(x) + ", " + str(y))
            return

        # Set the object's position
        object.setWorldLocation(x, y)

        # World, building, and furniture layers are overwrite layers (i.e. they can hold only a single object)
        if layer == Layer.WORLD or layer == Layer.BUILDING or layer == Layer.FURNITURE:
            self.grid[x][y]["layers"][layer] = []
            self.grid[x][y]["layers"][layer].append(object)
        # Objects layer is an additive layer (i.e. it can hold multiple objects)
        elif layer == Layer.OBJECTS:
            self.grid[x][y]["layers"][layer].append(object)
        # Player layer is a special layer that can only hold a single object
        elif layer == Layer.PLAYER:
            self.grid[x][y]["layers"][layer] = []
            self.grid[x][y]["layers"][layer].append(object)
        else:
            print("Error: Invalid layer: " + str(layer))


    # Get all objects at a given position
    def getObjectsAt(self, x, y):
        # Bound checking: Make sure the object is within the world bounds
        if x < 0 or x >= self.sizeX or y < 0 or y >= self.sizeY:
            print("Error: Object out of bounds: " + str(x) + ", " + str(y))
            return []

        # Get the objects
        objects = []
        for layer in Layer:
            objects += self.grid[x][y]["layers"][layer]

        return objects


    #
    #   World update
    #
    def tick(self):
        # Update all objects in the world
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
                for object in self.grid[x][y]["layers"][Layer.PLAYER]:
                    #print("Rendering: " + object.name)
                    #self.spriteLibrary.renderSprite(window, object.getSpriteName(), x * 32 - cameraX, y * 32 - cameraY)
                    for spriteName in object.getSpriteNamesWithContents():
                        self.spriteLibrary.renderSprite(window, spriteName, x * 32 - cameraX, y * 32 - cameraY)


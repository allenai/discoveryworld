# World.py

import SpriteLibrary
from Layer import Layer


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
    def addObject(self, x, y, layer, object):
        # Bound checking: Make sure the object is within the world bounds
        if x < 0 or x >= self.sizeX or y < 0 or y >= self.sizeY:
            print("Error: Object out of bounds: " + str(x) + ", " + str(y))
            return

        # World, building, and furniture layers are overwrite layers (i.e. they can hold only a single object)
        if layer == Layer.WORLD or layer == Layer.BUILDING or layer == Layer.FURNITURE:
            self.grid[y][x]["layers"][layer] = []
            self.grid[y][x]["layers"][layer].append(object)
        # Objects layer is an additive layer (i.e. it can hold multiple objects)
        elif layer == Layer.OBJECTS:
            self.grid[y][x]["layers"][layer].append(object)
        # Player layer is a special layer that can only hold a single object
        elif layer == Layer.PLAYER:
            self.grid[y][x]["layers"][layer] = []
            self.grid[y][x]["layers"][layer].append(object)
        else:
            print("Error: Invalid layer: " + str(layer))


    #
    #   Rendering
    #   
    def render(self, window, cameraX, cameraY):
        # Render the world
        for y in range(self.sizeY):
            for x in range(self.sizeX):
                # Render the world layer
                for object in self.grid[y][x]["layers"][Layer.WORLD]:
                    self.spriteLibrary.renderSprite(window, object["spriteName"], x * 32 - cameraX, y * 32 - cameraY)

                # Render the building layer
                for object in self.grid[y][x]["layers"][Layer.BUILDING]:
                    self.spriteLibrary.renderSprite(window, object["spriteName"], x * 32 - cameraX, y * 32 - cameraY)

                # Render the furniture layer
                for object in self.grid[y][x]["layers"][Layer.FURNITURE]:
                    self.spriteLibrary.renderSprite(window, object["spriteName"], x * 32 - cameraX, y * 32 - cameraY)

                # Render the objects layer
                for object in self.grid[y][x]["layers"][Layer.OBJECTS]:
                    self.spriteLibrary.renderSprite(window, object["spriteName"], x * 32 - cameraX, y * 32 - cameraY)

                # Render the player layer
                for object in self.grid[y][x]["layers"][Layer.PLAYER]:
                    self.spriteLibrary.renderSprite(window, object["spriteName"], x * 32 - cameraX, y * 32 - cameraY)

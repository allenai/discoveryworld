# BuildingMaker

import SpriteLibrary
from World import World
from Layer import Layer
from ObjectModel import *

class BuildingMaker:
    # Constructor
    def __init__(self, spriteLibrary):
        self.spriteLibrary = spriteLibrary

    #
    #   Object Maker
    #
    def mkObject(objectType, objectName, spriteName):
        object = {
            "type": objectType,
            "name": objectName,
            "spriteName": spriteName,
        }

        return object

    #
    #   Grass
    #
    
    # Fill the world with a base layer of grass
    def mkGrassFill(self, world):
        # Fill the world with grass
        for y in range(world.sizeY):
            for x in range(world.sizeX):
                world.addObject(x, y, Layer.WORLD, Grass(world))


    #
    #   Houses
    #
    def mkBuildingOneRoom(self, world, x, y, width, height, signText = "Default Sign Text", includeDoor=True):
        # Walls
        # Sprite names: ['house1_house_corner_b', 'house1_house_corner_bl', 'house1_house_corner_br', 'house1_house_corner_l', 'house1_house_corner_r', 'house1_house_corner_t', 'house1_house_corner_tl', 'house1_house_corner_tr']
        # Check that it has a minimum size (e.g. at least 4x4)
        if width < 4 or height < 4:
            print("Error: House is too small: " + str(width) + ", " + str(height))
            return

        # Top-left corner
        world.addObject(x, y, Layer.BUILDING, Wall(world))
        # Top-right corner
        world.addObject(x + width - 1, y, Layer.BUILDING, Wall(world))
        # Bottom-left corner
        world.addObject(x, y + height - 1, Layer.BUILDING, Wall(world))
        # Bottom-right corner
        world.addObject(x + width - 1, y + height - 1, Layer.BUILDING, Wall(world))
        # Top wall
        for i in range(1, width - 1):
            world.addObject(x + i, y, Layer.BUILDING, Wall(world))
        # Bottom wall
        for i in range(1, width - 1):
            # The middle of the bottom wall should be a door
            if (i == int(width / 2) and includeDoor):
                world.addObject(x + i, y + height - 1, Layer.BUILDING, Floor(world))
                world.addObject(x + i, y + height - 1, Layer.FURNITURE, Door(world))
            else:
                world.addObject(x + i, y + height - 1, Layer.BUILDING, Wall(world))
        # Left wall
        for i in range(1, height - 1):
            world.addObject(x, y + i, Layer.BUILDING, Wall(world))
        # Right wall
        for i in range(1, height - 1):
            world.addObject(x + width - 1, y + i, Layer.BUILDING, Wall(world))
        # Floor
        for i in range(1, width - 1):
            for j in range(1, height - 1):
                world.addObject(x + i, y + j, Layer.BUILDING, Floor(world))
        # Sign infront of the door
        if (len(signText) > 0):
            sign = Sign(world)
            sign.setText(signText)
            world.addObject(x + int(width / 2)-1, y + height, Layer.FURNITURE, sign)
    

    def mkBuildingDivided(self, world, x, y, width, height, dividerX, apertureX, dividerY, apertureY, doorX=0, signText = "Default Sign Text"):
        # Walls
        # Sprite names: ['house1_house_corner_b', 'house1_house_corner_bl', 'house1_house_corner_br', 'house1_house_corner_l', 'house1_house_corner_r', 'house1_house_corner_t', 'house1_house_corner_tl', 'house1_house_corner_tr']
        # Check that it has a minimum size (e.g. at least 4x4)
        if width < 4 or height < 4:
            print("Error: House is too small: " + str(width) + ", " + str(height))
            return

        # Calculate the real door-X, if not populated (by placing it in the middle)
        if doorX == 0:
            doorX = int(width / 2)

        # Top-left corner
        world.addObject(x, y, Layer.BUILDING, Wall(world))
        # Top-right corner
        world.addObject(x + width - 1, y, Layer.BUILDING, Wall(world))
        # Bottom-left corner
        world.addObject(x, y + height - 1, Layer.BUILDING, Wall(world))
        # Bottom-right corner
        world.addObject(x + width - 1, y + height - 1, Layer.BUILDING, Wall(world))
        # Top wall
        for i in range(1, width - 1):
            world.addObject(x + i, y, Layer.BUILDING, Wall(world))
        # Bottom wall
        for i in range(1, width - 1):
            # The middle of the bottom wall should be a door
            if i == doorX:
                #world.addObject(x + i, y + height - 1, Layer.BUILDING, Door(world))
                world.addObject(x + i, y + height - 1, Layer.BUILDING, Floor(world))
                world.addObject(x + i, y + height - 1, Layer.FURNITURE, Door(world))
            else:
                world.addObject(x + i, y + height - 1, Layer.BUILDING, Wall(world))
        # Left wall
        for i in range(1, height - 1):
            world.addObject(x, y + i, Layer.BUILDING, Wall(world))
        # Right wall
        for i in range(1, height - 1):
            world.addObject(x + width - 1, y + i, Layer.BUILDING, Wall(world))
        # Floor
        for i in range(1, width - 1):
            for j in range(1, height - 1):
                world.addObject(x + i, y + j, Layer.BUILDING, Floor(world))

        if (dividerX > 0):
            # Add an interior wall to divide the room
            for i in range(1, height - 1):
                # Add a hole in the middle
                if i == apertureX:
                    #world.addObject(x + dividerX, y + i, Layer.BUILDING, Floor(world))
                    pass
                else:                
                    world.addObject(x + dividerX, y + i, Layer.BUILDING, Wall(world))

        # Add an interior wall to divide the room
        if (dividerY > 0):
            for i in range(1, width - 1):
                # Add a hole in the middle
                if i == apertureY:
                    #world.addObject(x + i, y + dividerY, Layer.BUILDING, Floor(world))
                    pass
                else:
                    world.addObject(x + i, y + dividerY, Layer.BUILDING, Wall(world))

            
        # Sign infront of the door
        if (len(signText) > 0):
            sign = Sign(world)
            sign.setText(signText)
            world.addObject(x + doorX-1, y + height, Layer.FURNITURE, sign)
    

    ### TODO: WORK IN PROGRESS
    def mkBuildingLDivided(self, world, x, y, width, height, dividerX, signText = "Default Sign Text"):
        smallRoomOnBottom = False
        # Makes an L-shaped building. 
        # Nominally, this is just two square buildings, with a hole in the wall between them.

        # The size of the first building is (width - dividerX) x height
        # The size of the second building is (dividerX) x (height/2)
        # The second building is placed at (x + width - dividerX, y + height/2)

        # First building (bigger)
        self.mkBuildingOneRoom(world, x, y, width - dividerX, height, signText, includeDoor=True)
        # Second building (smaller)
        if (smallRoomOnBottom):
            self.mkBuildingOneRoom(world, x + width - dividerX, y + int(height/2), dividerX, int(height/2), signText="", includeDoor=False)
        else:
            self.mkBuildingOneRoom(world, x + width - dividerX, y + 1 + int(height/2), dividerX, int(height/2), signText="", includeDoor=False)
        # Add a hole in the wall between the two buildings
        for i in range(1, int(height/2)):
            world.addObject(x + width - dividerX, y + i + int(height/2), Layer.BUILDING, Floor(world))



    # Make table and chairs
    def mkTableAndChairs(self, world, x, y, chairsPresent = ["n", "s", "e", "w"]):
        # Table
        world.addObject(x, y, Layer.FURNITURE, Table(world))
        # Chairs
        if "n" in chairsPresent:
            world.addObject(x, y - 1, Layer.FURNITURE, Chair(world))
        if "s" in chairsPresent:            
            world.addObject(x, y + 1, Layer.FURNITURE, Chair(world))
        if "w" in chairsPresent:
            world.addObject(x - 1, y, Layer.FURNITURE, Chair(world))
        if "e" in chairsPresent:
            world.addObject(x + 1, y, Layer.FURNITURE, Chair(world))

    
# BuildingMaker

from discoveryworld.objects import *
from discoveryworld.Layer import Layer


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
                world.addObject(x, y, Layer.WORLD, world.createObject("Grass"))


    #
    #   Houses
    #
    def mkBuildingOneRoom(self, world, x, y, width, height, signText = "Default Sign Text", includeDoor=True, doorKeyID = 0):
        # Walls
        # Sprite names: ['house1_house_corner_b', 'house1_house_corner_bl', 'house1_house_corner_br', 'house1_house_corner_l', 'house1_house_corner_r', 'house1_house_corner_t', 'house1_house_corner_tl', 'house1_house_corner_tr']
        # Check that it has a minimum size (e.g. at least 4x4)
        if width < 4 or height < 4:
            print("Error: House is too small: " + str(width) + ", " + str(height))
            return

        # Top-left corner
        world.addObject(x, y, Layer.BUILDING, world.createObject("Wall"))
        # Top-right corner
        world.addObject(x + width - 1, y, Layer.BUILDING, world.createObject("Wall"))
        # Bottom-left corner
        world.addObject(x, y + height - 1, Layer.BUILDING, world.createObject("Wall"))
        # Bottom-right corner
        world.addObject(x + width - 1, y + height - 1, Layer.BUILDING, world.createObject("Wall"))
        # Top wall
        for i in range(1, width - 1):
            world.addObject(x + i, y, Layer.BUILDING, world.createObject("Wall"))
        # Bottom wall
        for i in range(1, width - 1):
            # The middle of the bottom wall should be a door
            if (i == int(width / 2) and includeDoor):
                world.addObject(x + i, y + height - 1, Layer.BUILDING, world.createObject("Floor"))
                door = world.createObject("Door")
                if (doorKeyID > 0):
                    door.setKeyID(doorKeyID)
                world.addObject(x + i, y + height - 1, Layer.FURNITURE, door)
            else:
                world.addObject(x + i, y + height - 1, Layer.BUILDING, world.createObject("Wall"))
        # Left wall
        for i in range(1, height - 1):
            world.addObject(x, y + i, Layer.BUILDING, world.createObject("Wall"))
        # Right wall
        for i in range(1, height - 1):
            world.addObject(x + width - 1, y + i, Layer.BUILDING, world.createObject("Wall"))
        # Floor
        for i in range(1, width - 1):
            for j in range(1, height - 1):
                world.addObject(x + i, y + j, Layer.BUILDING, world.createObject("Floor"))
        # Sign infront of the door
        if (len(signText) > 0):
            sign = world.createObject("Sign")
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
        world.addObject(x, y, Layer.BUILDING, world.createObject("Wall"))
        # Top-right corner
        world.addObject(x + width - 1, y, Layer.BUILDING, world.createObject("Wall"))
        # Bottom-left corner
        world.addObject(x, y + height - 1, Layer.BUILDING, world.createObject("Wall"))
        # Bottom-right corner
        world.addObject(x + width - 1, y + height - 1, Layer.BUILDING, world.createObject("Wall"))
        # Top wall
        for i in range(1, width - 1):
            world.addObject(x + i, y, Layer.BUILDING, world.createObject("Wall"))
        # Bottom wall
        for i in range(1, width - 1):
            # The middle of the bottom wall should be a door
            if i == doorX:
                #world.addObject(x + i, y + height - 1, Layer.BUILDING, world.createObject("Door"))
                world.addObject(x + i, y + height - 1, Layer.BUILDING, world.createObject("Floor"))
                world.addObject(x + i, y + height - 1, Layer.FURNITURE, world.createObject("Door"))
            else:
                world.addObject(x + i, y + height - 1, Layer.BUILDING, world.createObject("Wall"))
        # Left wall
        for i in range(1, height - 1):
            world.addObject(x, y + i, Layer.BUILDING, world.createObject("Wall"))
        # Right wall
        for i in range(1, height - 1):
            world.addObject(x + width - 1, y + i, Layer.BUILDING, world.createObject("Wall"))
        # Floor
        for i in range(1, width - 1):
            for j in range(1, height - 1):
                world.addObject(x + i, y + j, Layer.BUILDING, world.createObject("Floor"))

        if (dividerX > 0):
            # Add an interior wall to divide the room
            for i in range(1, height - 1):
                # Add a hole in the middle
                if i == apertureX:
                    #world.addObject(x + dividerX, y + i, Layer.BUILDING, world.createObject("Floor"))
                    pass
                else:
                    world.addObject(x + dividerX, y + i, Layer.BUILDING, world.createObject("Wall"))

        # Add an interior wall to divide the room
        if (dividerY > 0):
            for i in range(1, width - 1):
                # Add a hole in the middle
                if i == apertureY:
                    #world.addObject(x + i, y + dividerY, Layer.BUILDING, world.createObject("Floor"))
                    pass
                else:
                    world.addObject(x + i, y + dividerY, Layer.BUILDING, world.createObject("Wall"))


        # Sign infront of the door
        if (len(signText) > 0):
            sign = world.createObject("Sign")
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
            world.addObject(x + width - dividerX, y + i + int(height/2), Layer.BUILDING, world.createObject("Floor"))



    # Make table and chairs
    def mkTableAndChairs(self, world, x, y, chairsPresent = ["n", "s", "e", "w"]):
        # Table
        world.addObject(x, y, Layer.FURNITURE, world.createObject("Table"))
        # Chairs
        if "n" in chairsPresent:
            world.addObject(x, y - 1, Layer.FURNITURE, world.createObject("Chair"))
        if "s" in chairsPresent:
            world.addObject(x, y + 1, Layer.FURNITURE, world.createObject("Chair"))
        if "w" in chairsPresent:
            world.addObject(x - 1, y, Layer.FURNITURE, world.createObject("Chair"))
        if "e" in chairsPresent:
            world.addObject(x + 1, y, Layer.FURNITURE, world.createObject("Chair"))



    #
    #   Caves
    #
    #
    #   Houses
    #
    def mkCaveOneRoom(self, world, x, y, width, height, signText = "Default Sign Text"):
        includeDoor = True

        # Walls
        # Sprite names: ['house1_house_corner_b', 'house1_house_corner_bl', 'house1_house_corner_br', 'house1_house_corner_l', 'house1_house_corner_r', 'house1_house_corner_t', 'house1_house_corner_tl', 'house1_house_corner_tr']
        # Check that it has a minimum size (e.g. at least 4x4)
        if width < 4 or height < 4:
            print("Error: Cave is too small: " + str(width) + ", " + str(height))
            return

        # Floor
        for i in range(0, width):
            for j in range(0, height):
                world.addObject(x + i, y + j, Layer.WORLD, world.createObject("CaveFloor"))

        # Top-left corner
        world.addObject(x, y, Layer.BUILDING, world.createObject("CaveWall"))
        # Top-right corner
        world.addObject(x + width - 1, y, Layer.BUILDING, world.createObject("CaveWall"))
        # Bottom-left corner
        world.addObject(x, y + height - 1, Layer.BUILDING, world.createObject("CaveWall"))
        # Bottom-right corner
        world.addObject(x + width - 1, y + height - 1, Layer.BUILDING, world.createObject("CaveWall"))
        # Top wall
        for i in range(1, width - 1):
            world.addObject(x + i, y, Layer.BUILDING, world.createObject("CaveWall"))
        # Bottom wall
        for i in range(1, width - 1):
            # The middle of the bottom wall should be a door
            if (i == int(width / 2) and includeDoor):
                world.addObject(x + i, y + height - 1, Layer.BUILDING, world.createObject("CaveFloor"))
                #world.addObject(x + i, y + height - 1, Layer.FURNITURE, world.createObject("Door"))
            else:
                world.addObject(x + i, y + height - 1, Layer.BUILDING, world.createObject("CaveWall"))
        # Left wall
        for i in range(1, height - 1):
            world.addObject(x, y + i, Layer.BUILDING, world.createObject("CaveWall"))
        # Right wall
        for i in range(1, height - 1):
            world.addObject(x + width - 1, y + i, Layer.BUILDING, world.createObject("CaveWall"))
        # Sign infront of the door
        if (len(signText) > 0):
            sign = world.createObject("Sign")
            sign.setText(signText)
            world.addObject(x + int(width / 2)-1, y + height, Layer.FURNITURE, sign)

# BuildingMaker

import SpriteLibrary
from World import World
from Layer import Layer

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
    #   Houses
    #
    def mkHouse(self, world, x, y, width, height):
        # Walls
        # Sprite names: ['house1_house_corner_b', 'house1_house_corner_bl', 'house1_house_corner_br', 'house1_house_corner_l', 'house1_house_corner_r', 'house1_house_corner_t', 'house1_house_corner_tl', 'house1_house_corner_tr']
        # Check that it has a minimum size (e.g. at least 4x4)
        if width < 4 or height < 4:
            print("Error: House is too small: " + str(width) + ", " + str(height))
            return

        # Top-left corner
        world.addObject(x, y, Layer.BUILDING, BuildingMaker.mkObject("wall", "wall", "house1_house_corner_tl"))
        # Top-right corner
        world.addObject(x + width - 1, y, Layer.BUILDING, BuildingMaker.mkObject("wall", "wall", "house1_house_corner_tr"))
        # Bottom-left corner
        world.addObject(x, y + height - 1, Layer.BUILDING, BuildingMaker.mkObject("wall", "wall", "house1_house_corner_bl"))
        # Bottom-right corner
        world.addObject(x + width - 1, y + height - 1, Layer.BUILDING, BuildingMaker.mkObject("wall", "wall", "house1_house_corner_br"))
        # Top wall
        for i in range(1, width - 1):
            world.addObject(x + i, y, Layer.BUILDING, BuildingMaker.mkObject("wall", "wall", "house1_house_corner_t"))
            # Also needs the 'house1_house_backwall' sprite along the back
            world.addObject(x + i, y+1, Layer.BUILDING, BuildingMaker.mkObject("wall", "wall", "house1_house_backwall"))

        # Bottom wall
        for i in range(1, width - 1):
            world.addObject(x + i, y + height - 1, Layer.BUILDING, BuildingMaker.mkObject("wall", "wall", "house1_house_corner_b"))
        # Left wall
        for i in range(1, height - 1):
            world.addObject(x, y + i, Layer.BUILDING, BuildingMaker.mkObject("wall", "wall", "house1_house_corner_l"))
        # Right wall
        for i in range(1, height - 1):
            world.addObject(x + width - 1, y + i, Layer.BUILDING, BuildingMaker.mkObject("wall", "wall", "house1_house_corner_r"))
        # Floor
        for i in range(1, width - 1):
            for j in range(2, height - 1):
                world.addObject(x + i, y + j, Layer.BUILDING, BuildingMaker.mkObject("floor", "floor", "house1_house_floor"))

        # Door
        # TODO

    # Make table and chairs
    def mkTableAndChairs(self, world, x, y, chairsPresent = ["u", "d", "l", "r"]):
        # Table
        world.addObject(x, y, Layer.FURNITURE, BuildingMaker.mkObject("table", "table", "house1_table"))
        # Chairs
        if "u" in chairsPresent:
            world.addObject(x, y - 1, Layer.FURNITURE, BuildingMaker.mkObject("chair", "chair", "house1_chair_d"))
        if "d" in chairsPresent:            
            world.addObject(x, y + 1, Layer.FURNITURE, BuildingMaker.mkObject("chair", "chair", "house1_chair_u"))
        if "l" in chairsPresent:
            world.addObject(x - 1, y, Layer.FURNITURE, BuildingMaker.mkObject("chair", "chair", "house1_chair_r"))
        if "r" in chairsPresent:
            world.addObject(x + 1, y, Layer.FURNITURE, BuildingMaker.mkObject("chair", "chair", "house1_chair_l"))

    
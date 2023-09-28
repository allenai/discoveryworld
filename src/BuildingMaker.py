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
            for j in range(1, height - 1):
                world.addObject(x + i, y + j, Layer.BUILDING, BuildingMaker.mkObject("floor", "floor", "house1_house_floor"))

        # Door
        # TODO

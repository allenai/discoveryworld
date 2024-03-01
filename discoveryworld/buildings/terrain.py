
from discoveryworld.buildings import Layer


def mkGrassFill(world):
    """ Fill the world with a base layer of grass. """

    for y in range(world.sizeY):
        for x in range(world.sizeX):
            world.addObject(x, y, Layer.WORLD, world.createObject("Grass"))


def mkTownSquare(x, y, world):
    # Add statue
    statue = world.createObject("Statue")
    statue.addReadableText("A statue of the colony founder.")
    world.addObject(x+1, y+1, Layer.OBJECTS, statue)

    # Create a square that's made out of "Path" tiles
    for i in range(0, 3):
        for j in range(0, 3):
            if (not world.hasObj(x+i, y+j, "path")):
                world.addObject(x+i, y+j, Layer.WORLD, world.createObject("Path"))



# Path making
def mkPathX(x, y, lengthX, world):
    for i in range(0, lengthX):
        if (not world.hasObj(x+i, y, "path")):
            world.addObject(x+i, y, Layer.WORLD, world.createObject("Path"))


def mkPathY(x, y, lengthY, world):
    for i in range(0, lengthY):
        if (not world.hasObj(x, y+i, "path")):
            world.addObject(x, y+i, Layer.WORLD, world.createObject("Path"))


# Fence making
def mkFenceX(x, y, lengthX, world):
    for i in range(0, lengthX):
        if (not world.hasObj(x+i, y, "fence")):
            world.addObject(x+i, y, Layer.BUILDING, world.createObject("Fence"))


def mkFenceY(x, y, lengthY, world):
    for i in range(0, lengthY):
        if (not world.hasObj(x, y+i, "fence")):
            world.addObject(x, y+i, Layer.BUILDING, world.createObject("Fence"))

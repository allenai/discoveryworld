import random

from discoveryworld.Layer import Layer
from discoveryworld.buildings.house import mkBuildingOneRoom


def mkFarm(x, y, world, rng=None):
    rng = rng or random.Random()

    # Create a small building
    houseSizeX = 4
    houseSizeY = 4
    mkBuildingOneRoom(world, x=x+1, y=y, width=houseSizeX, height=houseSizeY, signText="Farm")

    # Add a table in the farm house
    seedTable = world.createObject("Table")
    seedJar = world.createObject("Jar")
    seedJar.setAutoFill(checkObjectName="seed", fillObjectName="Seed", minCount=5)
    seedJar.name = "seed jar"
    #seedJar.addObject(Seed(world, "red"))

    # Add 5 seeds to the jar
    #for i in range(5):
    #    seedJar.addObject( world.createObject("Seed") )

    seedTable.addObject(seedJar)
    world.addObject(x+3, y+1, Layer.FURNITURE, seedTable)

    # Add a shovel in the farm house
    shovel = world.createObject("Shovel")
    world.addObject(x+2, y+1, Layer.FURNITURE, shovel)

    # Add a bag of fertilizer
    fertilizer = world.createObject("FertilizerBag")
    world.addObject(x+2, y+2, Layer.FURNITURE, fertilizer)

    # Add a seed just outside the farm house
    #world.addObject(x+1, y+houseSizeY+2, Layer.OBJECTS, world.createObject("Seed"))

    # Create a soil plot
    soilPlotSizeX = 6
    soilPlotSizeY = 5
    for i in range(0, soilPlotSizeX):
        for j in range(0, soilPlotSizeY):
            if (not world.hasObj(x+i, y+j + houseSizeX + 1, "soil")):
                soilTile = world.createObject("SoilTile")
                # Randomly set the 'hasHole' attribute to True for some of the soil tiles
                #if (random.randint(0, 2) == 0):
                #    soilTile.attributes['hasHole'] = True

                # # Randomly add seeds to some of the soil tiles
                # if (random.randint(0, 2) == 0):
                #     soilTile.addObject(world.createObject("Seed"), force=True)

                world.addObject(x+i, y+j + houseSizeX + 1, Layer.WORLD, soilTile)

    # Add a hole in one soil plot at the top left
    #world.addObject(x+1, y+houseSizeY+1, Layer.OBJECTS, world.createObject("Hole"))
    # Add dirt beside the hole
    #world.addObject(x, y+houseSizeY+1, Layer.OBJECTS, world.createObject("Dirt"))

    # Randomly add a number of Mushrooms to the soil
    numMushroomsToAdd = 5
    numMushroomsAdded = 0
    attempts = 0
    mushroomsAdded = []
    while (numMushroomsAdded < numMushroomsToAdd):
        # Pick a random location
        randX = rng.randint(x, x+soilPlotSizeX-1)
        randY = rng.randint(y+houseSizeY+1, y+houseSizeY+soilPlotSizeY-1)

        # If there isn't already a mushroom there, add one
        if (not world.hasObj(randX, randY, "mushroom")):
            # Add a mushroom
            mushroomTypes = ["mushroom1", "mushroom2", "mushroom3", "mushroom4"]
            # Randomly pick a mushroom type
            mushroomType = mushroomTypes[rng.randint(0, len(mushroomTypes)-1)]
            mushroom = world.createObject(mushroomType)
            #mushroom = world.createObject("Mushroom")

            world.addObject(randX, randY, Layer.OBJECTS, mushroom)
            mushroomsAdded.append(mushroom)
            numMushroomsAdded += 1

        attempts += 1
        if (attempts > 100):
            print("ERROR: Couldn't add all mushrooms to farm.  Exiting to prevent infinite loop.")
            break


    # add a fertilizer pellet
    #world.addObject(x, y+4, Layer.OBJECTS, world.createObject("FertilizerPellet"))
    #world.addObject(x-1, y+4, Layer.OBJECTS, world.createObject("FertilizerPellet"))
    #world.addObject(x-2, y+4, Layer.OBJECTS, world.createObject("FertilizerPellet"))


    ## Debug, gives references to mushrooms added for agents to pick up
    return mushroomsAdded
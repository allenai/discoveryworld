import random

from discoveryworld.Agent import Agent
from discoveryworld.DialogTree import DialogMaker
from discoveryworld.Layer import Layer
from discoveryworld.buildings.colony import mkStorageShed
from discoveryworld.buildings.terrain import mkGrassFill, mkPathX


def makeScenarioStorageShed(world, numUserAgents=1, rng=None):
    scoringInfo = {}
    scoringInfo["criticalHypotheses"] = []
    rng = rng or random.Random()
    DOOR_KEY_ID = 123

    # Set a limit for the number of user agents
    MAX_NUM_AGENTS = 1
    if (numUserAgents > MAX_NUM_AGENTS):
        numUserAgents = MAX_NUM_AGENTS

    # Populate with structures/objects
    # Fill with grass
    mkGrassFill(world)
    # Randomly place a few plants (plant1, plant2, plant3)
    for i in range(0, 10):
        randY = rng.randint(0, world.sizeY - 1)
        randX = rng.randint(0, world.sizeX - 1)

    # Buildings
    mkStorageShed(15, 10, world, DOOR_KEY_ID, scoringInfo)

    # Paths
    mkPathX(17, 15, 15, world)       # Town square to farm

    # Add some plants
    world.addObject(15, 1, Layer.OBJECTS, world.createObject("PlantGeneric"))

    plantCount = 0
    minPlants = 15
    while (plantCount < minPlants):
        # Pick a random location
        randX = rng.randint(0, world.sizeX - 1)
        randY = rng.randint(0, world.sizeY - 1)

        # Check to see if there are any objects other than grass there
        objs = world.getObjectsAt(randX, randY)
        # Get types of objects
        objTypes = [obj.type for obj in objs]
        # Check to see that there is grass here
        if ("grass" in objTypes):
            # Check that there is not other things here
            if (len(objTypes) == 1):
                # Add a plant
                world.addObject(randX, randY, Layer.OBJECTS, world.createObject("PlantGeneric"))
                plantCount += 1


    # DialogMaker
    dialogMaker = DialogMaker()

    # Add some number of user agents
    for userAgentIdx in range(0, numUserAgents):
        userAgent = Agent(world)
        # TODO: Add starting tools for agent
        # TODO: ADD KEY

        # Add the agent to a specfic location
        #world.addObject(14+userAgentIdx, 14, Layer.AGENT, userAgent)      # In farm field
        world.addObject(18+userAgentIdx, 12, Layer.AGENT, userAgent)      # Near farm
        # Register the agent with the World so we can keep track of it
        world.addAgent(userAgent)


    # Add teleport locations to world
    # world.addTeleportLocation("shed", 12, 13)

    return scoringInfo
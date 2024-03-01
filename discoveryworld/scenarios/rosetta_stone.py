

import random
from discoveryworld.Agent import Agent
from discoveryworld.Layer import Layer
from discoveryworld.buildings.colony import mkKeyShop, mkPaintShop
from discoveryworld.buildings.terrain import mkFenceX, mkFenceY, mkGrassFill, mkPathX, mkPathY, mkTownSquare


def makeScenarioRosettaStone(world, numUserAgents=1, rng=None):
    # Make the Rosetta Stone scenario
    rng = rng or random.Random()

    # Set a limit for the number of user agents
    MAX_NUM_AGENTS = 5
    if (numUserAgents > MAX_NUM_AGENTS):
        numUserAgents = MAX_NUM_AGENTS

    # Populate with structures/objects
    # Fill with grass
    mkGrassFill(world)
    # Randomly place a few plants (plant1, plant2, plant3)
    for i in range(0, 10):
        randX = rng.randint(0, world.sizeX - 1)
        randY = rng.randint(0, world.sizeY - 1)

    # Buildings
    #mkHouse(4, 4, world, buildingMaker)

    mkKeyShop(9, 21, world)
    mkPaintShop(19, 21, world)

    # tables, pot = mkCafeteria(19, 20, world, buildingMaker)

    mkTownSquare(16, 18, world)

    #mushroomsAdded = mkFarm(10, 8, world, buildingMaker)

    # Paths
    mkPathY(17, 1, 30, world)       # Top/bottom, through town square

    mkPathX(10, 28, 15, world)       # Bottom, along cafeteria/science lab

    mkPathX(17, 19, 15, world)       # Town square to barracks

    mkPathX(17, 10, 10, world)       # Town square to infirmary

    mkPathX(1, 19, 16, world)       # Town square to farm

    # Fences
    # Top-left corner
    mkFenceY(6, 2, 16, world)
    mkFenceX(6, 2, 10, world)

    # Bottom-left corner
    mkFenceY(6, 21, 8, world)
    mkFenceX(6, 29, 10, world)

    # Bottom-right corner
    mkFenceX(19, 29, 10, world)
    mkFenceY(28, 21, 8, world)

    # Top-right corner
    mkFenceX(19, 2, 10, world)
    mkFenceY(28, 2, 16, world)


    # Add big village sign
    world.addObject(16, 2, Layer.BUILDING, world.createObject("SignVillage"))
    world.addObject(16, 29, Layer.BUILDING, world.createObject("SignVillage"))

    # Add some plants
    world.addObject(15, 1, Layer.OBJECTS, world.createObject("PlantGeneric"))

    # plantCount = 0
    # minPlants = 15
    # while (plantCount < minPlants):
    #     # Pick a random location
    #     randX = random.randint(0, world.sizeX - 1)
    #     randY = random.randint(0, world.sizeY - 1)

    #     # Check to see if there are any objects other than grass there
    #     objs = world.getObjectsAt(randX, randY)
    #     # Get types of objects
    #     objTypes = [obj.type for obj in objs]
    #     # Check to see that there is grass here
    #     if ("grass" in objTypes):
    #         # Check that there is not other things here
    #         if (len(objTypes) == 1):
    #             # Add a plant
    #             world.addObject(randX, randY, Layer.OBJECTS, world.createObject("PlantGeneric"))
    #             plantCount += 1


    # # DialogMaker
    # dialogMaker = DialogMaker()

    # Add some number of user agents
    for userAgentIdx in range(0, numUserAgents):
        userAgent = Agent(world)
        # TODO: Add starting tools for agent
        userAgent.addObject(world.createObject("Shovel"))
        userAgent.addObject(world.createObject("Seed"))
        # Add the agent to a specfic location
        #world.addObject(14+userAgentIdx, 14, Layer.AGENT, userAgent)      # In farm field
        world.addObject(12+userAgentIdx, 18, Layer.AGENT, userAgent)      # Near farm
        # Register the agent with the World so we can keep track of it
        world.addAgent(userAgent)


    # Add teleport locations to world
    world.addTeleportLocation("key shop", 10, 24)
    world.addTeleportLocation("paint shop", 20, 23)
    world.addTeleportLocation("town square", 16, 18)

    # currentAgent = Agent(world)
    # #world.addObject(5, 8, Layer.AGENT, currentAgent)      # Near cave
    # #world.addObject(10, 10, Layer.AGENT, currentAgent)      # Near farm
    # #world.addObject(20, 22, Layer.AGENT, currentAgent)     # In cafeteria
    # #world.addObject(10, 24, Layer.AGENT, currentAgent)     # In science lab
    # # Add tools for agent
    # currentAgent.addObject(world.createObject("Shovel"))
    # currentAgent.addObject(world.createObject("Seed"))
    # world.addAgent(currentAgent)

    # Add an NPC
    #npcColonist = NPCColonist(world, "Example NPC")
    #world.addObject(18, 25, Layer.AGENT, npcColonist)
    #world.addAgent(npcColonist)

    # # Add the NPC Chef
    # npcChef = NPCChef1(world, "Chef", tables=tables, pot=pot)
    # world.addObject(20, 21, Layer.AGENT, npcChef)
    # dialogMaker.mkDialogChef(npcChef)
    # world.addAgent(npcChef)

    # # Add the NPC Farmer
    # npcFarmer = NPCFarmer1(world, "Farmer", mushroomsAdded)
    # world.addObject(11, 12, Layer.AGENT, npcFarmer)
    # dialogMaker.mkDialogFarmer(npcFarmer)
    # world.addAgent(npcFarmer)


    # # Add another NPC colonist
    # #npcColonist1 = NPCColonist1(world, "Colonist 1", thingToPickup=None)
    # ##npcColonist1 = NPCColonist1(world, "Colonist 1", thingsToPickup=mushroomsAdded, whereToPlace=pot)
    # ##world.addObject(18, 20, Layer.AGENT, npcColonist1)

    # # Add another NPC colonist
    # npcColonists = []
    # for i in range(0, 5):
    #     colonist = NPCColonistAuto2(world, "Colonist " + str(i))
    #     dialogMaker.mkDialogColonist(colonist)
    #     world.addObject(13+i, 19, Layer.AGENT, colonist)
    #     world.addAgent(colonist)

    #     npcColonists.append(colonist)
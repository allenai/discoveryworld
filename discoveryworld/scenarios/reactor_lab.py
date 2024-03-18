# reactor_lab.py

import random
from discoveryworld.Agent import Agent, NPCChef1, NPCColonistAuto2, NPCFarmer1
from discoveryworld.DialogTree import DialogMaker
from discoveryworld.Layer import Layer
from discoveryworld.buildings.cave import mkCave
from discoveryworld.buildings.colony import mkBarracks, mkCafeteria, mkInfirmary, mkScienceLab
from discoveryworld.buildings.farm import mkFarm

from discoveryworld.buildings.terrain import mkFenceX, mkFenceY, mkGrassFill, mkPathX, mkPathY, mkSignVillage, mkTownSquare

from discoveryworld.buildings.house import mkBuildingDivided, mkBuildingOneRoom, mkTableAndChairs


# Helper to create a reactor
def mkGenerator(x, y, world, linkedObjects, reactorLength=3):
    # Left side
    world.addObject(x, y, Layer.OBJECTS, world.createObject("GeneratorSideLeft"))
    # Right side
    world.addObject(x+reactorLength, y, Layer.OBJECTS, world.createObject("GeneratorSideRight"))
    # Middle
    for i in range(1, reactorLength):
        reactorCenterPiece = world.createObject("GeneratorCenter")
        # Add the linked objects, so the reactor activates when they activate
        reactorCenterPiece.addLinkedObjectsActivationState(linkedObjects)

        world.addObject(x+i, y, Layer.OBJECTS, reactorCenterPiece)


#
#   Reactor Lab Building
#

def mkReactorLab(x, y, world):
    # Create a building (science lab)
    #buildingMaker.mkBuildingOneRoom(world, x=x, y=y, width=5, height=5)
    mkBuildingDivided(world, x=x, y=y, width=13, height=6, dividerX=6, apertureX=3, dividerY=0, apertureY=0, doorX=3, signText="Quantum Reactor Lab")

    # Add 5 instruments on 5 tables
    instruments = []
    instruments.append( world.createObject("Microscope") )
    instruments.append( world.createObject("Spectrometer") )
    instruments.append( world.createObject("RadiationMeter") )
    instruments.append( world.createObject("Thermometer") )
    instruments.append( world.createObject("Densitometer") )

    # Shuffle
    random.shuffle(instruments)

    # Add the tables and an instrument to each
    for i in range(0, 5):
        bench = world.createObject("Table")
        bench.addObject( instruments[i] )
        world.addObject(x+1+i, y+1, Layer.FURNITURE, bench)


    # Reactor portion
    quantumCrystals = []
    for i in range(0, 4):
        quantumCrystal = world.createObject("QuantumCrystal")
        quantumCrystal.attributes['density'] = random.uniform(0.5, 1.5)
        quantumCrystals.append(quantumCrystal)


    # Shuffle
    random.shuffle(quantumCrystals)
    # Give the crystals a number
    for i in range(0, 4):
        quantumCrystals[i].name = "quantum crystal " + str(i+1)

    # Add the tables and a quantum crystal reactor to each
    crystalReactors = []
    for i in range(0, 4):
        reactorBench = world.createObject("Table")
        reactor = world.createObject("CrystalReactor")
        reactor.setReactorNum(i+1)
        crystalReactors.append(reactor)
        reactorBench.addObject( reactor )
        # TODO: Set first 2 reactors to appropriate state
        if (i < 2):
            # Add a crystal to the contents of this reactor
            reactor.addObject( quantumCrystals[i] )

            # TODO: Set the reactor to the appropriate frequency

        world.addObject(x+8+i, y+2, Layer.FURNITURE, reactorBench)


    # Put the other 2 quantum crystals on tables on the other side of the room
    for i in range(0, 2):
        bench = world.createObject("Table")
        bench.addObject( quantumCrystals[i+2] )
        world.addObject(x+4+i, y+4, Layer.FURNITURE, bench)


    # Add the generator
    mkGenerator(x+8, y+1, world, linkedObjects = crystalReactors, reactorLength=3)



    # Add a radioactive check source
    #world.addObject(x+6, y+1, Layer.OBJECTS, world.createObject("radioactivechecksource"))

    # Add NPK meter
    #world.addObject(x+5, y+4, Layer.OBJECTS, world.createObject("NPKMeter"))




#
#   Reactor Lab Scenario
#
def makeScenarioReactorLab(world, numUserAgents=1, rng=None):
    rng = rng or random.Random()

    # Set a limit for the number of user agents
    MAX_NUM_AGENTS = 3
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
    #mkHouse(4, 4, world)

    mkReactorLab(10, 15, world)

    # Paths
    #mkPathY(17, 1, 30, world)       # Top/bottom, through town square
    #mkPathX(10, 28, 15, world)       # Bottom, along cafeteria/science lab


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
    mkSignVillage(16, 2, world)
    mkSignVillage(16, 29, world)

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
        userAgent.addObject(world.createObject("Shovel"))
        userAgent.addObject(world.createObject("Seed"))
        # Add the agent to a specfic location
        #world.addObject(14+userAgentIdx, 14, Layer.AGENT, userAgent)      # In farm field
        world.addObject(12+userAgentIdx, 18, Layer.AGENT, userAgent)      # Near farm
        # Register the agent with the World so we can keep track of it
        world.addAgent(userAgent)


    # Add teleport locations to world
    # TODO
    #world.addTeleportLocation("science lab", 10, 24)

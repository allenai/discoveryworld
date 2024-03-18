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


# Make random properties of a quantum crystal
def mkCrystalProperties(quantumCrystalIn, rng, keyDimension:int=0, slope:float=100.0, offset:float=100):
        # Resonance Frequency of the crystal (a set property for a given crystal)
        #quantumCrystalIn.attributes['resonanceFreq'] = 5000                    # The resonance frequency of the crystal
        precision = 2   # Number of decimal places to round to

        # Quantities that the crystal depends on
        quantumCrystalIn.attributes['density'] = round(rng.uniform(10.0, 70.0), precision)          # The density of the crystal (in g/cm^3)
        quantumCrystalIn.attributes['temperatureC'] = round(rng.uniform(10.0, 50.0), precision)    # The temperature of the crystal (in degrees C)
        quantumCrystalIn.attributes['quantumSize'] = round(rng.uniform(10.0, 70.0), precision)   # The quantum size of the crystal (in nm)
        # Add a faux material, with a given radiation and spectrum
        fauxMaterial = {}
        fauxMaterial['radiationusvh'] = round(rng.uniform(10.0, 50.0), precision)       # The radiation of the crystal (in mSv)
        spectrum = []
        for i in range(0, 5):
            channelValue = round(rng.uniform(10.0, 70.0), precision)
            spectrum.append(channelValue)
        fauxMaterial['spectrum'] = spectrum            # The spectrum of the crystal (on 5 spectral channels)
        fauxMaterial['microscopeDesc'] = "The quantum gap of this crystal appears to be " + str(quantumCrystalIn.attributes['quantumSize']) + " nm"  # The description of the crystal under a microscope
        quantumCrystalIn.attributes['materials'].append(fauxMaterial)

        # Pick one dimension (density, temperature, quantumSize, radiation, or spectrum) to be the "key" dimension.  Dimensions are numbered (0, 1, 2, 3, 4)
        keyValue = 0
        if (keyDimension == 0):
            keyValue = quantumCrystalIn.attributes['density']
        elif (keyDimension == 1):
            keyValue = quantumCrystalIn.attributes['temperatureC']
        elif (keyDimension == 2):
            keyValue = quantumCrystalIn.attributes['quantumSize']
        elif (keyDimension == 3):
            keyValue = fauxMaterial['radiationusvh']
        elif (keyDimension == 4):
            keyValue = fauxMaterial['spectrum'][4]
        else:
            print("Error: mkCrystalProperties(): keyDimension must be between 0 and 4")

        # The value of 'resonanceFreq' will be a linear function of the keyValue, with the specified slope and offset
        resonanceFreq = (slope * keyValue) + offset
        # resonanceFreq should be an integer
        resonanceFreq = int(resonanceFreq)
        quantumCrystalIn.attributes['resonanceFreq'] = resonanceFreq

        # Return
        return quantumCrystalIn


#
#   Reactor Lab Building
#

def mkReactorLab(x, y, world, rng, randomSeed, scoringInfo):
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

    scoringInfo['instruments'] = instruments

    # Shuffle
    rng.shuffle(instruments)

    # Add the tables and an instrument to each
    for i in range(0, 5):
        bench = world.createObject("Table")
        bench.addObject( instruments[i] )
        world.addObject(x+1+i, y+1, Layer.FURNITURE, bench)


    # Reactor portion
    quantumCrystals = []
    #keyDimension = rng.randint(0, 4)        # Which dimension (temperature, density, quantum size, radiation, spectrum) will be the "key" dimension that the resonance frequency depends on
    keyDimension = randomSeed % 5            # Makes sure that random seeds 1-5 cycle through all available dimensions
    randomSlope = int(rng.uniform(90, 110))
    randomOffset = int(rng.uniform(90, 110))

    for i in range(0, 4):
        quantumCrystal = world.createObject("QuantumCrystal")
        #quantumCrystal.attributes['density'] = random.uniform(0.5, 1.5)
        # Make random quantum crystal values
        quantumCrystal = mkCrystalProperties(quantumCrystal, rng=rng, keyDimension=keyDimension, slope=randomSlope, offset=randomOffset)
        quantumCrystals.append(quantumCrystal)

    scoringInfo['quantumCrystals'] = quantumCrystals

    # Shuffle
    rng.shuffle(quantumCrystals)
    # Give the crystals a number
    for i in range(0, 4):
        quantumCrystals[i].name = "quantum crystal " + str(i+1)
        #print("Quantum Crystal " + str(i+1) + " resonance frequency: " + str(quantumCrystals[i].attributes['resonanceFreq']) + " Hz")
    #import time
    #time.sleep(10)
    #exit(1)

    # Add the tables and a quantum crystal reactor to each
    crystalReactors = []
    scoringInfo['reactorsToChange'] = []
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
            # Set the reactor to the appropriate frequency
            reactor.attributes['resonanceFreq'] = quantumCrystals[i].attributes['resonanceFreq']
        else:
            scoringInfo['reactorsToChange'].append(reactor)

        # Note the default resonance frequency
        reactor.attributes['resonanceFreqDefault'] = quantumCrystals[i].attributes['resonanceFreq']
        # Add the reactor to the bench
        world.addObject(x+8+i, y+2, Layer.FURNITURE, reactorBench)

    scoringInfo['reactors'] = crystalReactors

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
def makeScenarioReactorLab(world, numUserAgents=1):
    scoringInfo = {}
    scoringInfo["criticalHypotheses"] = []

    # Set a limit for the number of user agents
    MAX_NUM_AGENTS = 3
    if (numUserAgents > MAX_NUM_AGENTS):
        numUserAgents = MAX_NUM_AGENTS

    # Populate with structures/objects

    # Fill with grass
    mkGrassFill(world)
    # Randomly place a few plants (plant1, plant2, plant3)
    for i in range(0, 10):
        randX = world.rng.randint(0, world.sizeX - 1)
        randY = world.rng.randint(0, world.sizeY - 1)


    # Buildings
    #mkHouse(4, 4, world)

    mkReactorLab(10, 15, world, rng=world.rng, randomSeed=world.randomSeed, scoringInfo=scoringInfo)

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
        randX = world.rng.randint(0, world.sizeX - 1)
        randY = world.rng.randint(0, world.sizeY - 1)

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
        #userAgent.addObject(world.createObject("Shovel"))
        #userAgent.addObject(world.createObject("Seed"))
        # Add the agent to a specfic location
        #world.addObject(14+userAgentIdx, 14, Layer.AGENT, userAgent)      # In farm field
        world.addObject(12+userAgentIdx, 18, Layer.AGENT, userAgent)      # Near farm
        # Register the agent with the World so we can keep track of it
        world.addAgent(userAgent)


    # Add teleport locations to world
    # TODO
    world.addTeleportLocation("science lab", 14, 18)
    world.addTeleportLocation("reactor lab", 20, 18)

    # Return scoring info
    return scoringInfo

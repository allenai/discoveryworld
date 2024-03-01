
import random

import numpy as np
from discoveryworld.Agent import Agent
from discoveryworld.DialogTree import DialogMaker
from discoveryworld.Layer import Layer

from discoveryworld.buildings import mkGrassFill
from discoveryworld.buildings.archaeology import mkDigSite, mkDigSiteWithObj


def makeScenarioArchaeologicalDig(world, numUserAgents=1, rng=None):
    rng = rng or random.Random()
    numDigSites = 3

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

    # Possible artifact ages (in years). Ranges from 100k to 1 million years old, with even numbers.
    artifactAges = [150000, 230000, 370000, 410000, 500000, 675000, 725000, 890000, 930000, 1000000]
    # Shuffle the artifact ages
    rng.shuffle(artifactAges)
    # Trim to the first numDigSites
    artifactAges = artifactAges[:numDigSites]

    # List dig site locations
    digSiteLocations = [(10, 10), (20, 13), (12, 18)]

    # Add 3 dig sites
    for digSiteIdx, digSiteLocation in enumerate(digSiteLocations):
        mkDigSite(digSiteLocation[0], digSiteLocation[1], world, rng, digSiteIdx+1, artifactAges[digSiteIdx])

    # Add a table at the start of the dig site
    instrumentTable = world.createObject("Table")
    world.addObject(15, 15, Layer.FURNITURE, instrumentTable)
    # Add a radiocarbon meter to the table
    instrumentTable.addObject( world.createObject("RadioCarbonMeter") )


    # Add a shovel at the start of the dig site
    shovel = world.createObject("Shovel")
    world.addObject(14, 15, Layer.FURNITURE, shovel)

    # Add a flag at the start of the dig site
    flag = world.createObject("Flag")
    world.addObject(14, 16, Layer.FURNITURE, flag)

    # Add some random holes
    minHoles = 1
    holeCount = 0
    while (holeCount < minHoles):
        # Pick a random locatio between 10-20
        randX = rng.randint(10, 20)
        randY = rng.randint(10, 20)

        # Check to see if there are any objects other than grass there
        objs = world.getObjectsAt(randX, randY)
        # Get types of objects
        objTypes = [obj.type for obj in objs]
        # Check to see that there is grass here
        if ("grass" in objTypes):
            # Check that there is not other things here
            if (len(objTypes) == 1):
                # Add a hole
                soilTile = world.createObject("SoilTile")
                #soilTile.attributes['hasHole'] = True
                # Remove all soil tile contents (i.e. the dirt) -- this has the effect of making a hole
                for obj in soilTile.contents:
                    soilTile.removeObject(obj)

                world.addObject(randX, randY, Layer.BUILDING, soilTile)
                holeCount += 1


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
        # Add the agent to a specfic location
        world.addObject(13+userAgentIdx, 14, Layer.AGENT, userAgent)      # Near center of dig site
        # Register the agent with the World so we can keep track of it
        world.addAgent(userAgent)


    # Add teleport locations to world
    world.addTeleportLocation("base camp", 13, 14)
    for digSiteIdx, digSiteLocation in enumerate(digSiteLocations):
        world.addTeleportLocation("dig site " + str(digSiteIdx+1), digSiteLocation[0]-1, digSiteLocation[1]+1)



#
# Make the archeological dig scenario
#
def makeScenarioArchaeologicalDigGenericRadioisotope(world, numUserAgents=1, rng=None):
    rng = rng or random.Random()
    numDigSites = 3

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

    # Possible artifact ages (in years). Ranges from 100k to 1 million years old, with even numbers.
    #artifactAges = [150000, 230000, 370000, 410000, 500000, 675000, 725000, 890000, 930000, 1000000]
    # Shuffle the artifact ages
    #rng.shuffle(artifactAges)
    # Trim to the first numDigSites
    #artifactAges = artifactAges[:numDigSites]

    # List dig site locations
    #seedSiteLocations = [(10, 10), (20, 13), (12, 18)]
    #experimentalSiteLocations = [(16, 8), (18, 18), (8, 15)]
    digSiteLocations = [(10, 10), (20, 13), (12, 18)] + [(16, 8), (18, 18), (8, 15)]
    # Shuffle
    rng.shuffle(digSiteLocations)

    #"ArtifactStoneHammer": ArtifactStoneHammer,
    #"ArtifactBrassChisel": ArtifactBrassChisel,
    #"ArtifactIronTongs": ArtifactIronTongs,
    knownArtifactAges = [10000, 4000, 1000]
    oldArtifactAge = rng.choice([40000, 35000, 30000, 20000])
    mediumArtifactAge = rng.choice([5000, 4000, 3000, 2000])
    youngArtifactAge = rng.choice([1700, 1500, 1200])

    print("oldArtifactAge: " + str(oldArtifactAge))
    print("mediumArtifactAge: " + str(mediumArtifactAge))
    print("youngArtifactAge: " + str(youngArtifactAge))

    # Make up 4 faux radioisotope values.  For the real one, it should strongly correlate with the age of the artifact.  For the others, the correlation should be very weak.
    # The real one should be the first one.
    realRadioisotopeValues = knownArtifactAges + [oldArtifactAge, mediumArtifactAge, youngArtifactAge]
    # divide each value by 50,000
    realRadioisotopeValues = [val/50000 for val in realRadioisotopeValues]
    # Add some noise (+/- 0.01) to each value
    realRadioisotopeValues = [val + rng.uniform(-0.01, 0.01) for val in realRadioisotopeValues]
    # Round to 3 decimal places
    realRadioisotopeValues = [round(val, 3) for val in realRadioisotopeValues]

    # Use numpy to calculate the correlation between the real radioisotope values and the artifact ages
    correlation = np.corrcoef(knownArtifactAges + [oldArtifactAge, mediumArtifactAge, youngArtifactAge], realRadioisotopeValues)
    #print ("Ages: " + str(knownArtifactAges + [oldArtifactAge, mediumArtifactAge, youngArtifactAge]))
    #print ("Real radioisotope values: " + str(realRadioisotopeValues))
    #print ("Correlation: " + str(correlation[0][1]))

    # For the other radioisotope values, just make them random, between 0 and 1

    # Make a fake radioisotope value that has a weak correlation with the artifact ages
    done = False
    fakeRadioisotope1Values = []
    while (not done):
        fakeRadioisotope1Values = [rng.uniform(0, 1) for i in range(0, len(realRadioisotopeValues))]
        # Round to 3 decimal places
        fakeRadioisotope1Values = [round(val, 3) for val in fakeRadioisotope1Values]
        correlation = np.corrcoef(knownArtifactAges, fakeRadioisotope1Values[:len(knownArtifactAges)])
        if (abs(correlation[0][1]) < 0.1):
            done = True
    #print("Fake radioisotope 1 values: " + str(fakeRadioisotope1Values))
    #print("Correlation: " + str(correlation[0][1]))

    done = False
    fakeRadioisotope2Values = []
    while (not done):
        fakeRadioisotope2Values = [rng.uniform(0, 1) for i in range(0, len(realRadioisotopeValues))]
        # Round to 3 decimal places
        fakeRadioisotope2Values = [round(val, 3) for val in fakeRadioisotope2Values]
        correlation = np.corrcoef(knownArtifactAges, fakeRadioisotope2Values[:len(knownArtifactAges)])
        if (abs(correlation[0][1]) < 0.1):
            done = True
    #print("Fake radioisotope 2 values: " + str(fakeRadioisotope2Values))
    #print("Correlation: " + str(correlation[0][1]))

    done = False
    fakeRadioisotope3Values = []
    while (not done):
        fakeRadioisotope3Values = [rng.uniform(0, 1) for i in range(0, len(realRadioisotopeValues))]
        # Round to 3 decimal places
        fakeRadioisotope3Values = [round(val, 3) for val in fakeRadioisotope3Values]
        correlation = np.corrcoef(knownArtifactAges + [oldArtifactAge, mediumArtifactAge, youngArtifactAge], fakeRadioisotope3Values)
        if (abs(correlation[0][1]) < 0.1):
            done = True
    #print("Fake radioisotope 3 values: " + str(fakeRadioisotope3Values))
    #print("Correlation: " + str(correlation[0][1]))
    #exit(1)

    # Figure out which channel (1, 2, 3, or 4) should be the "real" one
    channelShift = rng.choice([0, 1, 2, 3])

    # Assign the radioisotope values to the artifacts
    seedOldArtifact = world.createObject("ArtifactStoneHammer")
    radioisotopeValues = [realRadioisotopeValues[0], fakeRadioisotope1Values[0], fakeRadioisotope2Values[0], fakeRadioisotope3Values[0]]
    radioisotopeValues = radioisotopeValues[-channelShift:] + radioisotopeValues[:-channelShift]        # Shift the list so that the real radioisotope value is in the real channel
    seedOldArtifact.attributes["radioisotopeValues"] = radioisotopeValues
    seedOldArtifact.attributes["radiocarbonAge"] = knownArtifactAges[0]

    seedMediumArtifact = world.createObject("ArtifactBrassChisel")
    radioisotopeValues = [realRadioisotopeValues[1], fakeRadioisotope1Values[1], fakeRadioisotope2Values[1], fakeRadioisotope3Values[1]]
    radioisotopeValues = radioisotopeValues[-channelShift:] + radioisotopeValues[:-channelShift]        # Shift the list so that the real radioisotope value is in the real channel
    seedMediumArtifact.attributes["radioisotopeValues"] = radioisotopeValues
    seedMediumArtifact.attributes["radiocarbonAge"] = knownArtifactAges[1]

    seedYoungArtifact = world.createObject("ArtifactIronTongs")
    radioisotopeValues = [realRadioisotopeValues[2], fakeRadioisotope1Values[2], fakeRadioisotope2Values[2], fakeRadioisotope3Values[2]]
    radioisotopeValues = radioisotopeValues[-channelShift:] + radioisotopeValues[:-channelShift]        # Shift the list so that the real radioisotope value is in the real channel
    seedYoungArtifact.attributes["radioisotopeValues"] = radioisotopeValues
    seedYoungArtifact.attributes["radiocarbonAge"] = knownArtifactAges[2]

    # Now the 3 unknown artifacts
    unknownArtifacts = []
    unknownArtifactAges = [oldArtifactAge, mediumArtifactAge, youngArtifactAge]
    for i in range(0, 3):
        unknownArtifact = world.createObject("AncientArtifact")
        radioisotopeValues = [realRadioisotopeValues[3+i], fakeRadioisotope1Values[3+i], fakeRadioisotope2Values[3+i], fakeRadioisotope3Values[3+i]]
        radioisotopeValues = radioisotopeValues[-channelShift:] + radioisotopeValues[:-channelShift]        # Shift the list so that the real radioisotope value is in the real channel
        unknownArtifact.attributes["radioisotopeValues"] = radioisotopeValues
        unknownArtifact.attributes["radiocarbonAge"] = unknownArtifactAges[i]
        unknownArtifacts.append(unknownArtifact)

    # Shuffle the order of the unknown artifacts
    rng.shuffle(unknownArtifacts)

    # Shuffle the order of the seed artifacts
    seedArtifacts = [seedOldArtifact, seedMediumArtifact, seedYoungArtifact]
    rng.shuffle(seedArtifacts)


    # Add dig sites
    for digSiteIdx, digSiteLocation in enumerate(digSiteLocations):
        if (digSiteIdx < 3):
            # Seed artifact
            artifact = seedArtifacts[digSiteIdx]
            mkDigSiteWithObj(digSiteLocation[0], digSiteLocation[1], world, rng, digSiteIdx+1, artifact, artifactExposed=True)
        else:
            # Unknown artifact
            artifact = unknownArtifacts[digSiteIdx-3]
            mkDigSiteWithObj(digSiteLocation[0], digSiteLocation[1], world, rng, digSiteIdx+1, artifact, artifactExposed=False)
            #self.mkDigSite(digSiteLocation[0], digSiteLocation[1], world, rng, digSiteIdx+1, artifactAges[digSiteIdx])


    # Add a table at the start of the dig site
    instrumentTable = world.createObject("Table")
    world.addObject(15, 15, Layer.FURNITURE, instrumentTable)
    # Add a radiocarbon meter to the table
    instrumentTable.addObject( world.createObject("RadioisotopeMeter") )


    # Add a shovel at the start of the dig site
    shovel = world.createObject("Shovel")
    world.addObject(14, 15, Layer.FURNITURE, shovel)

    # Add a flag at the start of the dig site
    flag = world.createObject("Flag")
    world.addObject(14, 16, Layer.FURNITURE, flag)

    # Add some random holes
    minHoles = 1
    holeCount = 0
    while (holeCount < minHoles):
        # Pick a random locatio between 10-20
        randX = rng.randint(10, 20)
        randY = rng.randint(10, 20)

        # Check to see if there are any objects other than grass there
        objs = world.getObjectsAt(randX, randY)
        # Get types of objects
        objTypes = [obj.type for obj in objs]
        # Check to see that there is grass here
        if ("grass" in objTypes):
            # Check that there is not other things here
            if (len(objTypes) == 1):
                # Add a hole
                soilTile = world.createObject("SoilTile")
                #soilTile.attributes['hasHole'] = True
                # Remove all soil tile contents (i.e. the dirt) -- this has the effect of making a hole
                for obj in soilTile.contents:
                    soilTile.removeObject(obj)

                world.addObject(randX, randY, Layer.BUILDING, soilTile)
                holeCount += 1


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
        # Add the agent to a specfic location
        world.addObject(13+userAgentIdx, 14, Layer.AGENT, userAgent)      # Near center of dig site
        # Register the agent with the World so we can keep track of it
        world.addAgent(userAgent)


    # Add teleport locations to world
    world.addTeleportLocation("base camp", 13, 14)
    for digSiteIdx, digSiteLocation in enumerate(digSiteLocations):
        world.addTeleportLocation("dig site " + str(digSiteIdx+1), digSiteLocation[0]-1, digSiteLocation[1]+1)

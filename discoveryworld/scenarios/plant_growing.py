import random
from discoveryworld.Agent import Agent
from discoveryworld.DialogTree import DialogMaker

from discoveryworld.Layer import Layer
from discoveryworld.buildings.soil_research import mkRandomSoilNutrientsWithSetValues, mkSoilFieldControlled, mkSoilResearchBuilding
from discoveryworld.buildings.terrain import mkFenceX, mkFenceY, mkGrassFill, mkPathX, mkPathY, mkTallTree

from discoveryworld.objects import *



def mapSeedToObjectName(nutrientName, nutrientValue):
    # List of seed types
    #seedTypes = ["SeedNutrientsPot1", "SeedNutrientsPot2", "SeedNutrientsPot3", "SeedNutrientsTit1", "SeedNutrientsTit2", "SeedNutrientsTit3", "SeedNutrientsLit1", "SeedNutrientsLit2", "SeedNutrientsLit3", "SeedNutrientsTho1", "SeedNutrientsTho2", "SeedNutrientsTho3", "SeedNutrientsBar1", "SeedNutrientsBar2", "SeedNutrientsBar3"]
    if (nutrientName == "potassium"):
        return "SeedNutrientPot" + str(nutrientValue)
    elif (nutrientName == "titanium"):
        return "SeedNutrientTit" + str(nutrientValue)
    elif (nutrientName == "lithium"):
        return "SeedNutrientLit" + str(nutrientValue)
    elif (nutrientName == "thorium"):
        return "SeedNutrientTho" + str(nutrientValue)
    elif (nutrientName == "barium"):
        return "SeedNutrientBar" + str(nutrientValue)

    print("ERROR: mapSeedToObjectName: nutrientName not recognized: " + nutrientName)
    return None


def makeScenarioPlantGrowing(world, numUserAgents=1):
    scoringInfo = {}
    scoringInfo["criticalHypotheses"] = []
    numPlantSites = 3

    # Randomly choose what value is helpful for growing plants
    possibleNutrients = ["potassium", "titanium", "lithium", "thorium", "barium"]
    possibleValues = [1, 2, 3]
    possibleValuesStrLUT = {1: "low", 2: "medium", 3: "high"}
    whichNutrientPositive = world.rng.choice(possibleNutrients)
    whichValuePositive = world.rng.choice(possibleValues)
    whichSeedName = mapSeedToObjectName(whichNutrientPositive, whichValuePositive)

    # Set a limit for the number of user agents
    MAX_NUM_AGENTS = 5
    if (numUserAgents > MAX_NUM_AGENTS):
        numUserAgents = MAX_NUM_AGENTS

    # Populate with structures/objects

    # Fill with grass
    mkGrassFill(world)

    # Soil research building
    mkSoilResearchBuilding(12, 8, world, whichSeedName)
    world.addTeleportLocation("Storage Building", 12+3, 8+2)

    # Primary pilot field area
    pilotFieldStartX = 6
    pilotFieldStartY = 14
    pilotFieldSizeX = 4
    pilotFieldSizeY = 3
    pilotSoilTiles = []
    for i in range(0, pilotFieldSizeX):
        for j in range(0, pilotFieldSizeY):
            soilTile = world.createObject("SoilTile")
            # Randomize nutrient levels in this soil tile
            soilTile.attributes["soilNutrients"] = mkRandomSoilNutrientsWithSetValues(setValuesDict={}, rng=world.rng)
            world.addObject(pilotFieldStartX+i, pilotFieldStartY+j, Layer.BUILDING, soilTile)
            # TODO: Add plants, etc.
            pilotSoilTiles.append(soilTile)


    # Randomly set 3 of the tiles to have positive examples of the required soil nutrients, and 3 to have negative examples
    # Positive (first 3)
    world.rng.shuffle(pilotSoilTiles)
    for i in range(0, 3):
        setValueDict = {}
        setValueDict[whichNutrientPositive] = whichValuePositive
        pilotSoilTiles[i].attributes["soilNutrients"] = mkRandomSoilNutrientsWithSetValues(setValuesDict=setValueDict, rng=world.rng)

    # Add hypothesis
    hypothesisStr = "If a seed is placed in soil with a '" + whichNutrientPositive + "' nutrient level of '" + str(possibleValuesStrLUT[whichValuePositive]) + "', then it will successfully grow into a plant."
    scoringInfo["criticalHypotheses"].append(hypothesisStr)

    # Negative (next 3)
    for i in range(3, 6):
        soilTile = pilotSoilTiles[i]
        setValueDict = {}
        # Select a random negative value for the nutrient (by negative, we mean not the positive value)
        setValueDict[whichNutrientPositive] = world.rng.choice(possibleValues)
        while (setValueDict[whichNutrientPositive] == whichValuePositive):
            setValueDict[whichNutrientPositive] = world.rng.choice(possibleValues)
        soilTile.attributes["soilNutrients"] = mkRandomSoilNutrientsWithSetValues(setValuesDict=setValueDict, rng=world.rng)

    # Note the pilot field soil tiles, for scoring
    scoringInfo["pilotFieldSoilTiles"] = pilotSoilTiles

    # Add seeds to the pilot field
    scoringInfo["startingSeeds"] = []
    for soilTile in pilotSoilTiles:
        seed = world.createObject(whichSeedName)
        soilTile.addObject(seed)
        scoringInfo["startingSeeds"].append(seed)

    # Sign for the pilot field
    sign = world.createObject("Sign")
    sign.setText("Pilot Field")
    world.addObject(pilotFieldStartX, pilotFieldStartY+pilotFieldSizeY, Layer.FURNITURE, sign)
    world.addTeleportLocation("Pilot Field", pilotFieldStartX, pilotFieldStartY+pilotFieldSizeY-1)

    # Make 3 test fields
    testFieldStartX = 12
    testFieldStartY = 15

    for i in range(0, numPlantSites):
        x = testFieldStartX + i*5
        y = testFieldStartY
        mkSoilFieldControlled(x, y, world, i+1)
        world.addTeleportLocation("Experimental Field #" + str(i+1), x, y+1)


    # Make path along fields
    mkPathX(6, 18, 18, world)
    # Make path to research building
    mkPathY(15, 12, 12, world)

    # Make fence around entire research station + fields
    mkFenceX(4, 6, 22, world)      # Top
    mkFenceY(4, 6, 14, world)      # Left
    mkFenceY(25, 6, 15, world)     # Right
    mkFenceX(4, 20, 10, world)     # Bottom (left)
    mkFenceX(17, 20, 9, world)     # Bottom (right)

    # Sign for the whole research facility
    sign = world.createObject("Sign")
    sign.setText("Botanical Research Facility")
    world.addObject(13, 21, Layer.FURNITURE, sign)

    # Add big trees to either side of the research facility
    mkTallTree(11, 10, world)
    mkTallTree(9, 10, world)
    mkTallTree(7, 10, world)

    mkTallTree(18, 10, world)
    mkTallTree(20, 10, world)
    mkTallTree(22, 10, world)

    mkTallTree(12, 21, world)
    mkTallTree(18, 21, world)


    # Randomly place a few decorative plants
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
        # Add the agent to a specfic location
        world.addObject(13+userAgentIdx, 14, Layer.AGENT, userAgent)      # Near center of dig site
        # Register the agent with the World so we can keep track of it
        world.addAgent(userAgent)


    # Should tick the environment 10 times, to make sure the pilot seeds grow and are ready for the user to view.
    for i in range(0, 10):
        world.tick()


    # Keep track of starting plants that have grown
    scoringInfo["startingPlants"] = []
    # Get all objects in the world
    allObjects = world.getAllWorldObjects()
    for obj in allObjects:
        # If the object is an instance of the "Mushroom" class, then add it to the list of starting mushrooms
        if (isinstance(obj, Mushroom)):
            scoringInfo["startingPlants"].append(obj)
        if (isinstance(obj, SoilNutrientMeter)):
            scoringInfo["soilNutrientMeter"] = obj
        if (isinstance(obj, Shovel)):
            scoringInfo["shovel"] = obj
        if (isinstance(obj, Jar)):
            scoringInfo["jar"] = obj            # Seed jar

    # Return the helpful info for scoring
    return scoringInfo
# ScenarioMaker.py


from ObjectMaker import ObjectMaker
from World import World
from Layer import Layer
from BuildingMaker import BuildingMaker
from Agent import *
from DialogTree import DialogMaker


class ScenarioMaker:
    # Constructor
    # Random is a reference to an existing random number generator, already setup with a specific seed
    def __init__(self, random):
        self.random = random


    #
    #   Functions to help build specific buildings or other structures
    #
    def mkHouse(self, x, y, world, buildingMaker):
        # Create a building (house)
        buildingMaker.mkBuildingOneRoom(world, x=x+0, y=x+0, width=7, height=7)
        #buildingMaker.mkTableAndChairs(world, x=6, y=9, chairsPresent=["n", "s", "e", "w"])
        buildingMaker.mkTableAndChairs(world, x=x+1, y=y+4, chairsPresent=["n", "s", "", ""])

        world.addObject(x+1, y+1, Layer.FURNITURE, world.createObject("Fridge"))
        world.addObject(x+2, y+1, Layer.FURNITURE, world.createObject("Sink"))
        world.addObject(x+3, y+1, Layer.FURNITURE, world.createObject("Stove"))

        world.addObject(x+5, y+1, Layer.FURNITURE, world.createObject("Bed"))


    def mkBarracks(self, x, y, world, buildingMaker):
        # Create a building (barracks)
        #buildingMaker.mkBuildingOneRoom(world, x=x, y=y, width=5, height=5)
        #buildingMaker.mkBuildingOneRoom(world, x=x, y=y, width=12, height=5)
        buildingMaker.mkBuildingDivided(world, x=x, y=y, width=8, height=7, dividerX=0, apertureX=0, dividerY=3, apertureY=1, doorX=3, signText="Barracks")


        # Add 3 beds and bedside tables (back wall)
        world.addObject(x+2, y+1, Layer.FURNITURE, world.createObject("Bed"))
        world.addObject(x+3, y+1, Layer.FURNITURE, world.createObject("TableBedside"))
        world.addObject(x+5, y+1, Layer.FURNITURE, world.createObject("Bed"))
        world.addObject(x+6, y+1, Layer.FURNITURE, world.createObject("TableBedside"))
        #world.addObject(x+8, y+1, Layer.FURNITURE, Bed(world))
        #world.addObject(x+9, y+1, Layer.FURNITURE, TableBedside(world))

        # Add 3 beds and bedside tables (middle wall)
        world.addObject(x+2, y+4, Layer.FURNITURE, world.createObject("Bed"))
        world.addObject(x+3, y+4, Layer.FURNITURE, world.createObject("TableBedside"))
        world.addObject(x+5, y+4, Layer.FURNITURE, world.createObject("Bed"))
        world.addObject(x+6, y+4, Layer.FURNITURE, world.createObject("TableBedside"))
        #world.addObject(x+8, y+4, Layer.FURNITURE, Bed(world))
        #world.addObject(x+9, y+4, Layer.FURNITURE, TableBedside(world))


        # Add a bed
        #world.addObject(x+1, y+1, Layer.FURNITURE, Bed(world))

        # Add a bedside table
        #world.addObject(x+2, y+1, Layer.FURNITURE, TableBedside(world))

    def mkInfirmary(self, x, y, world, buildingMaker):
        # Create a building (barracks)
        buildingMaker.mkBuildingOneRoom(world, x=x, y=y, width=8, height=5)

        # Add 4 beds
        world.addObject(x+1, y+1, Layer.FURNITURE, world.createObject("Bed"))
        world.addObject(x+3, y+1, Layer.FURNITURE, world.createObject("Bed"))
        #world.addObject(x+5, y+1, Layer.FURNITURE, Bed(world))
        #world.addObject(x+7, y+1, Layer.FURNITURE, Bed(world))

        # Table
        world.addObject(x+5, y+1, Layer.FURNITURE, world.createObject("Table"))
        # Fridge
        world.addObject(x+6, y+1, Layer.FURNITURE, world.createObject("Fridge"))

    def mkCafeteria(self, x, y, world, buildingMaker):
        # Create an L-shaped building (cafeteria)
        #buildingMaker.mkBuildingLDivided(world, x=x, y=y, width=10, height=8, dividerX=5)
        # Create a divided building (cafeteria)
        #buildingMaker.mkBuildingDivided(world, x=x, y=y, width=8, height=7, dividerX=0, apertureX=0, dividerY=3, apertureY=1, doorX=3, signText="Cafeteria")
        buildingMaker.mkBuildingOneRoom(world, x=x, y=y, width=8, height=7, signText="Cafeteria")

        # Front (eating area)
        # Table and chairs
        #buildingMaker.mkTableAndChairs(world, x=x+7, y=y+5, chairsPresent=["n", "s", "e", "w"])
        buildingMaker.mkTableAndChairs(world, x=x+2, y=y+5, chairsPresent=["", "", "e", "w"])

        # Counter
        tables = []
        for i in range(5):
            tableToAdd = world.createObject("Table")
            #if (i == 2):
            #    tableToAdd.addObject(Mushroom(world, "red"))
            #tableToAdd.addObject(world.createObject("mushroom3"))
            #tableToAdd.addObject(world.createObject("mushroom1"))
            # Randomly choose between mushroom1 and mushroom2
            if (self.random.random() < 0.5):
                tableToAdd.addObject(world.createObject("mushroom1"))
            else:
                tableToAdd.addObject(world.createObject("mushroom2"))

            world.addObject(x+i+2, y+3, Layer.FURNITURE, tableToAdd)
            tables.append(tableToAdd)

        #world.addObject(x+2, y+5, Layer.FURNITURE, Table(world))

        # Back (kitchen)
        pot = world.createObject("Pot")
        # add 5 mushrooms to pot
        #for i in range(5):
        #    pot.addObject(Mushroom(world))
        # Put the pot on a table
        kitchenPrepTable = world.createObject("Table")
        kitchenPrepTable.addObject(pot)
        world.addObject(x+3, y+1, Layer.FURNITURE, kitchenPrepTable)
        world.addObject(x+4, y+1, Layer.FURNITURE, world.createObject("Fridge"))
        world.addObject(x+5, y+1, Layer.FURNITURE, world.createObject("Sink"))
        world.addObject(x+6, y+1, Layer.FURNITURE, world.createObject("Stove"))

        # Front (decorations)
        flowerpot = world.createObject("FlowerPot")
        flowerTable = world.createObject("Table")
        flowerTable.addObject(flowerpot)
        world.addObject(x+6, y+5, Layer.FURNITURE, flowerTable)

        ## debug
        return tables, pot


    def mkScienceLab(self, x, y, world, buildingMaker):
        # Create a building (science lab)
        #buildingMaker.mkBuildingOneRoom(world, x=x, y=y, width=5, height=5)
        buildingMaker.mkBuildingDivided(world, x=x, y=y, width=8, height=6, dividerX=5, apertureX=3, dividerY=0, apertureY=0, doorX=3, signText="Science Lab")

        bench1 = world.createObject("Table")
        world.addObject(x+1, y+1, Layer.FURNITURE, bench1)
        bench1.addObject( world.createObject("Microscope") )

        bench2 = world.createObject("Table")
        world.addObject(x+2, y+1, Layer.FURNITURE, bench2)
        bench2.addObject( world.createObject("Spectrometer") )

        bench3 = world.createObject("Table")
        world.addObject(x+3, y+1, Layer.FURNITURE, bench3)
        bench3.addObject( world.createObject("PHMeter") )

        bench4 = world.createObject("Table")
        world.addObject(x+4, y+1, Layer.FURNITURE, bench4)
        bench4.addObject( world.createObject("RadiationMeter") )


        # Add sampler and sample containers (Petri dishes)
        bench5 = world.createObject("Table")
        world.addObject(x+1, y+4, Layer.FURNITURE, bench5)
        bench5.addObject( world.createObject("Sampler") )

        bench6 = world.createObject("Table")
        world.addObject(x+1, y+3, Layer.FURNITURE, bench6)
        bench6.addObject( world.createObject("PetriDish") )


        bench7 = world.createObject("Table")
        world.addObject(x+4, y+4, Layer.FURNITURE, bench7)
        bench7.addObject( world.createObject("Thermometer") )


        # Add a red mushroom and a pink mushroom
        world.addObject(x+3, y+3, Layer.OBJECTS, world.createObject("mushroom1"))
        world.addObject(x+4, y+3, Layer.OBJECTS, world.createObject("mushroom2"))

        # Add a radioactive check source
        world.addObject(x+6, y+1, Layer.OBJECTS, world.createObject("radioactivechecksource"))

        # Add NPK meter
        world.addObject(x+6, y+4, Layer.OBJECTS, world.createObject("NPKMeter"))



    # Check if a tile already contains a "path"
    def _hasObj(self, x, y, world, objType):
        objects = world.getObjectsAt(x, y)
        # Then, check to see if any of them are walls
        for object in objects:
            if (object.type == objType):
                return True
        return False


    def mkTownSquare(self, x, y, world, buildingMaker):
        # Add statue
        statue = world.createObject("Statue")
        statue.addReadableText("A statue of the colony founder.")
        world.addObject(x+1, y+1, Layer.OBJECTS, statue)

        # Create a square that's made out of "Path" tiles
        for i in range(0, 3):
            for j in range(0, 3):
                if (not self._hasObj(x+i, y+j, world, "path")):
                    world.addObject(x+i, y+j, Layer.WORLD, world.createObject("Path"))


    def mkFarm(self, x, y, world, buildingMaker):
        # Create a small building
        houseSizeX = 4
        houseSizeY = 4
        buildingMaker.mkBuildingOneRoom(world, x=x+1, y=y, width=houseSizeX, height=houseSizeY, signText="Farm")

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
                if (not self._hasObj(x+i, y+j + houseSizeX + 1, world, "soil")):
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
            randX = self.random.randint(x, x+soilPlotSizeX-1)
            randY = self.random.randint(y+houseSizeY+1, y+houseSizeY+soilPlotSizeY-1)

            # If there isn't already a mushroom there, add one
            if (not self._hasObj(randX, randY, world, "mushroom")):
                # Add a mushroom
                mushroomTypes = ["mushroom1", "mushroom2", "mushroom3", "mushroom4"]
                # Randomly pick a mushroom type
                mushroomType = mushroomTypes[self.random.randint(0, len(mushroomTypes)-1)]
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


    # Cave
    def mkCave(self, x, y, world, buildingMaker):
        # Make the cave
        buildingMaker.mkCaveOneRoom(world, x, y, 6, 5, signText="Cave")

        # Add some rocks
        world.addObject(x+1, y+1, Layer.OBJECTS, world.createObject("rock_lg"))
        world.addObject(x+4, y+1, Layer.OBJECTS, world.createObject("rock_med"))
        world.addObject(x+4, y+2, Layer.OBJECTS, world.createObject("rock_lg"))
        world.addObject(x+4, y+3, Layer.OBJECTS, world.createObject("rock_sm"))
        world.addObject(x+3, y+1, Layer.OBJECTS, world.createObject("rock_sm"))

        world.addObject(x+1, y+2, Layer.OBJECTS, world.createObject("rock_glowing"))
        world.addObject(x+2, y+1, Layer.OBJECTS, world.createObject("rock_glowing"))





    # Path making
    def mkPathX(self, x, y, lengthX, world):
        for i in range(0, lengthX):
            if (not self._hasObj(x+i, y, world, "path")):
                world.addObject(x+i, y, Layer.WORLD, world.createObject("Path"))

    def mkPathY(self, x, y, lengthY, world):
        for i in range(0, lengthY):
            if (not self._hasObj(x, y+i, world, "path")):
                world.addObject(x, y+i, Layer.WORLD, world.createObject("Path"))

    # Fence making
    def mkFenceX(self, x, y, lengthX, world):
        for i in range(0, lengthX):
            if (not self._hasObj(x+i, y, world, "fence")):
                world.addObject(x+i, y, Layer.BUILDING, world.createObject("Fence"))

    def mkFenceY(self, x, y, lengthY, world):
        for i in range(0, lengthY):
            if (not self._hasObj(x, y+i, world, "fence")):
                world.addObject(x, y+i, Layer.BUILDING, world.createObject("Fence"))




    # Archeology Dig Site
    def mkDigSite(self, x, y, world, buildingMaker, r, digSiteNum, artifactAge):
        minSize = 2
        # Randomly make size of archeology dig site (x-y each between 1-2)
        totalLocations = 0
        while (totalLocations < minSize):       # Keep trying until we get a big enough dig site (at least 2 squares)
            digSiteSizeX = r.randint(1, 2)
            digSiteSizeY = r.randint(1, 2)
            totalLocations = digSiteSizeX * digSiteSizeY
        locationOfArtifact = r.randint(0, totalLocations-1)

        # Make the dig site soil (with one hole containing an artifact)
        count = 0       # Counter for where to place the artifact
        for i in range(0, digSiteSizeX):
            for j in range(0, digSiteSizeY):
                soilTile = world.createObject("SoilTile")
                # Randomly set the 'hasHole' attribute to True for some of the soil tiles
                #if (random.randint(0, 2) == 0):
                #    soilTile.attributes['hasHole'] = True

                # Randomly add an artifact to one of the soil tiles
                if (count == locationOfArtifact):
                    # Add an artifact
                    artifact = world.createObject("AncientArtifact")
                    # Add the age
                    artifact.attributes['radiocarbonAge'] = artifactAge
                    # Add the artifact to the hole
                    soilTile.addObject(artifact, force=True)

                # Add soil tile to world
                world.addObject(x+i, y+j+1, Layer.BUILDING, soilTile)

                count += 1


        # Add a sign to the dig site
        sign = world.createObject("Sign")
        sign.setText("Dig Site " + str(digSiteNum))
        world.addObject(x, y, Layer.FURNITURE, sign)



    # Archeology Dig Site
    def mkDigSiteWithObj(self, x, y, world, buildingMaker, r, digSiteNum, artifactObj, artifactExposed=False):
        minSize = 2
        # Randomly make size of archeology dig site (x-y each between 1-2)
        totalLocations = 0
        while (totalLocations < minSize):       # Keep trying until we get a big enough dig site (at least 2 squares)
            digSiteSizeX = r.randint(1, 2)
            digSiteSizeY = r.randint(1, 2)
            totalLocations = digSiteSizeX * digSiteSizeY
        locationOfArtifact = r.randint(0, totalLocations-1)

        # Make the dig site soil (with one hole containing an artifact)
        count = 0       # Counter for where to place the artifact
        for i in range(0, digSiteSizeX):
            for j in range(0, digSiteSizeY):
                soilTile = world.createObject("SoilTile")
                # Randomly set the 'hasHole' attribute to True for some of the soil tiles
                #if (random.randint(0, 2) == 0):
                #    soilTile.attributes['hasHole'] = True

                # Randomly add an artifact to one of the soil tiles
                if (count == locationOfArtifact):
                    # If 'artifactExposed' is True, then remove the soil from the hole
                    if (artifactExposed):
                        for obj in soilTile.contents:
                            soilTile.removeObject(obj)

                    # Add the artifact to the hole
                    soilTile.addObject(artifactObj, force=True)

                # Add soil tile to world
                world.addObject(x+i, y+j+1, Layer.BUILDING, soilTile)

                count += 1


        # Add a sign to the dig site
        sign = world.createObject("Sign")
        sign.setText("Dig Site " + str(digSiteNum))
        world.addObject(x, y, Layer.FURNITURE, sign)




    #
    #   Functions to build specific scenarios
    #


    # Make the town scenario
    def makeScenarioTown(self, world, numUserAgents=1):
        # Set a limit for the number of user agents
        MAX_NUM_AGENTS = 5
        if (numUserAgents > MAX_NUM_AGENTS):
            numUserAgents = MAX_NUM_AGENTS

        # Populate with structures/objects
        buildingMaker = BuildingMaker(world)

        # Fill with grass
        buildingMaker.mkGrassFill(world)
        # Randomly place a few plants (plant1, plant2, plant3)
        for i in range(0, 10):
            randX = self.random.randint(0, world.sizeX - 1)
            randY = self.random.randint(0, world.sizeY - 1)
            ## world.addObject(randX, randY, Layer.OBJECTS, BuildingMaker.mkObject("plant", "plant", "forest1_plant" + str(i % 3 + 1)))


        # Buildings
        #mkHouse(4, 4, world, buildingMaker)

        self.mkScienceLab(8, 21, world, buildingMaker)

        self.mkInfirmary(19, 4, world, buildingMaker)

        self.mkBarracks(19, 11, world, buildingMaker)

        tables, pot = self.mkCafeteria(19, 20, world, buildingMaker)

        self.mkTownSquare(16, 18, world, buildingMaker)

        ## TODO: Add Farm?
        mushroomsAdded = self.mkFarm(10, 8, world, buildingMaker)

        # Cave
        self.mkCave(0, 0, world, buildingMaker)


        # Paths
        self.mkPathY(17, 1, 30, world)       # Top/bottom, through town square

        self.mkPathX(10, 28, 15, world)       # Bottom, along cafeteria/science lab

        self.mkPathX(17, 19, 15, world)       # Town square to barracks

        self.mkPathX(17, 10, 10, world)       # Town square to infirmary

        self.mkPathX(1, 19, 16, world)       # Town square to farm

        # Fences
        # Top-left corner
        self.mkFenceY(6, 2, 16, world)
        self.mkFenceX(6, 2, 10, world)

        # Bottom-left corner
        self.mkFenceY(6, 21, 8, world)
        self.mkFenceX(6, 29, 10, world)

        # Bottom-right corner
        self.mkFenceX(19, 29, 10, world)
        self.mkFenceY(28, 21, 8, world)

        # Top-right corner
        self.mkFenceX(19, 2, 10, world)
        self.mkFenceY(28, 2, 16, world)


        # Add big village sign
        world.addObject(16, 2, Layer.BUILDING, world.createObject("SignVillage"))
        world.addObject(16, 29, Layer.BUILDING, world.createObject("SignVillage"))

        # Add some plants
        world.addObject(15, 1, Layer.OBJECTS, world.createObject("PlantGeneric"))

        plantCount = 0
        minPlants = 15
        while (plantCount < minPlants):
            # Pick a random location
            randX = self.random.randint(0, world.sizeX - 1)
            randY = self.random.randint(0, world.sizeY - 1)

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
        world.addTeleportLocation("science lab", 10, 24)
        world.addTeleportLocation("cafeteria", 20, 23)
        world.addTeleportLocation("farm", 12, 13)
        world.addTeleportLocation("cave", 5, 8)
        world.addTeleportLocation("farmers field", 18, 25)
        world.addTeleportLocation("town square", 16, 18)
        world.addTeleportLocation("barracks", 18, 11)
        world.addTeleportLocation("infirmary", 22, 7)

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

        # Add the NPC Chef
        npcChef = NPCChef1(world, "Chef", tables=tables, pot=pot)
        world.addObject(20, 21, Layer.AGENT, npcChef)
        dialogMaker.mkDialogChef(npcChef)
        world.addAgent(npcChef)

        # Add the NPC Farmer
        npcFarmer = NPCFarmer1(world, "Farmer", mushroomsAdded)
        world.addObject(11, 12, Layer.AGENT, npcFarmer)
        dialogMaker.mkDialogFarmer(npcFarmer)
        world.addAgent(npcFarmer)


        # Add another NPC colonist
        #npcColonist1 = NPCColonist1(world, "Colonist 1", thingToPickup=None)
        ##npcColonist1 = NPCColonist1(world, "Colonist 1", thingsToPickup=mushroomsAdded, whereToPlace=pot)
        ##world.addObject(18, 20, Layer.AGENT, npcColonist1)

        # Add another NPC colonist
        npcColonists = []
        for i in range(0, 5):
            colonist = NPCColonistAuto2(world, "Colonist " + str(i))
            dialogMaker.mkDialogColonist(colonist)
            world.addObject(13+i, 19, Layer.AGENT, colonist)
            world.addAgent(colonist)

            npcColonists.append(colonist)



    #
    #   Storage shed scenario
    #
    def mkStorageShed(self, x, y, world, buildingMaker, DOOR_KEY_ID):
        # Create a small building
        houseSizeX = 7
        houseSizeY = 4
        buildingMaker.mkBuildingOneRoom(world, x=x+1, y=y, width=houseSizeX, height=houseSizeY, signText="Storage Shed", includeDoor=True, doorKeyID = DOOR_KEY_ID)

        # Add a table in the farm house
        compoundTable1 = world.createObject("Table")
        compoundTable2 = world.createObject("Table")
        compoundTable3 = world.createObject("Table")
        compoundTable4 = world.createObject("Table")
        compoundTable5 = world.createObject("Table")

        # Create chemical dispensers
        dispenser1 = world.createObject("ChemicalDispenser")
        dispenser2 = world.createObject("ChemicalDispenser")
        dispenser3 = world.createObject("ChemicalDispenser")
        dispenser1.name = "Dispenser (Substance A)"
        dispenser2.name = "Dispenser (Substance B)"
        dispenser3.name = "Dispenser (Substance C)"

        # Fill with chemicals
        #dispenser1.setAutoFill(checkObjectName="seed", fillObjectName="Seed", minCount=5)
        dispenser1.setAutoFill(checkObjectName="Substance A", fillObjectName="SubstanceA", minCount=1, replenishTime=0)
        dispenser2.setAutoFill(checkObjectName="Substance B", fillObjectName="SubstanceB", minCount=1, replenishTime=0)
        dispenser3.setAutoFill(checkObjectName="Substance C", fillObjectName="SubstanceC", minCount=1, replenishTime=0)

        # Add dispensers to tables
        compoundTable2.addObject(dispenser1)
        compoundTable3.addObject(dispenser2)
        compoundTable4.addObject(dispenser3)

        # Add bottle cleaner
        BottleCleaner = world.createObject("BottleCleaner")
        compoundTable5.addObject(BottleCleaner)

        # Add tables to world
        world.addObject(x+2, y+1, Layer.FURNITURE, compoundTable1)
        world.addObject(x+3, y+1, Layer.FURNITURE, compoundTable2)
        world.addObject(x+4, y+1, Layer.FURNITURE, compoundTable3)
        world.addObject(x+5, y+1, Layer.FURNITURE, compoundTable4)
        world.addObject(x+6, y+1, Layer.FURNITURE, compoundTable5)

        mixingJar = world.createObject("Jar")
        # Add to first table
        compoundTable1.addObject(mixingJar)

        # Add substance
        #substance1 = world.createObject("TestSubstance")
        #substance2 = world.createObject("PurpleSubstance")
        #mixingJar.addObject(substance1)
        #mixingJar.addObject(substance2)

        #substanceCleaner = world.createObject("substanceCleaner")
        #mixingJar.addObject(substanceCleaner)

        # Add rusty key
        rustyKey = world.createObject("Key")
        rustyKey.setKeyID(DOOR_KEY_ID)
        world.addObject(x+2, y+2, Layer.OBJECTS, rustyKey)



#        seedJar.setAutoFill(checkObjectName="seed", fillObjectName="Seed", minCount=5)
#        seedJar.name = "seed jar"
        #seedJar.addObject(Seed(world, "red"))

        # Add 5 seeds to the jar
        #for i in range(5):
        #    seedJar.addObject( world.createObject("Seed") )

#        seedTable.addObject(seedJar)
#        world.addObject(x+3, y+1, Layer.FURNITURE, seedTable)

        # Add a shovel in the farm house
        #shovel = world.createObject("Shovel")
        #world.addObject(x+2, y+1, Layer.FURNITURE, shovel)

        # Add a bag of fertilizer
        #fertilizer = world.createObject("FertilizerBag")
        #world.addObject(x+2, y+2, Layer.FURNITURE, fertilizer)



    # Make the town scenario
    def makeScenarioStorageShed(self, world, numUserAgents=1):
        DOOR_KEY_ID = 123

        # Set a limit for the number of user agents
        MAX_NUM_AGENTS = 1
        if (numUserAgents > MAX_NUM_AGENTS):
            numUserAgents = MAX_NUM_AGENTS

        # Populate with structures/objects
        buildingMaker = BuildingMaker(world)

        # Fill with grass
        buildingMaker.mkGrassFill(world)
        # Randomly place a few plants (plant1, plant2, plant3)
        for i in range(0, 10):
            randX = self.random.randint(0, world.sizeX - 1)
            randY = self.random.randint(0, world.sizeY - 1)
            ## world.addObject(randX, randY, Layer.OBJECTS, BuildingMaker.mkObject("plant", "plant", "forest1_plant" + str(i % 3 + 1)))

        # Buildings
        self.mkStorageShed(15, 10, world, buildingMaker, DOOR_KEY_ID)

        # Paths
        self.mkPathX(17, 15, 15, world)       # Town square to farm

        # Add some plants
        world.addObject(15, 1, Layer.OBJECTS, world.createObject("PlantGeneric"))

        plantCount = 0
        minPlants = 15
        while (plantCount < minPlants):
            # Pick a random location
            randX = self.random.randint(0, world.sizeX - 1)
            randY = self.random.randint(0, world.sizeY - 1)

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



    #
    #   Storage shed scenario
    #
    def mkStorageShed(self, x, y, world, buildingMaker, DOOR_KEY_ID):
        # Create a small building
        houseSizeX = 7
        houseSizeY = 4
        buildingMaker.mkBuildingOneRoom(world, x=x+1, y=y, width=houseSizeX, height=houseSizeY, signText="Storage Shed", includeDoor=True, doorKeyID = DOOR_KEY_ID)

        # Add a table in the farm house
        compoundTable1 = world.createObject("Table")
        compoundTable2 = world.createObject("Table")
        compoundTable3 = world.createObject("Table")
        compoundTable4 = world.createObject("Table")
        compoundTable5 = world.createObject("Table")

        # Create chemical dispensers
        dispenser1 = world.createObject("ChemicalDispenser")
        dispenser2 = world.createObject("ChemicalDispenser")
        dispenser3 = world.createObject("ChemicalDispenser")
        dispenser1.name = "Dispenser (Substance A)"
        dispenser2.name = "Dispenser (Substance B)"
        dispenser3.name = "Dispenser (Substance C)"

        # Fill with chemicals
        #dispenser1.setAutoFill(checkObjectName="seed", fillObjectName="Seed", minCount=5)
        dispenser1.setAutoFill(checkObjectName="Substance A", fillObjectName="SubstanceA", minCount=1, replenishTime=0)
        dispenser2.setAutoFill(checkObjectName="Substance B", fillObjectName="SubstanceB", minCount=1, replenishTime=0)
        dispenser3.setAutoFill(checkObjectName="Substance C", fillObjectName="SubstanceC", minCount=1, replenishTime=0)

        # Add dispensers to tables
        compoundTable2.addObject(dispenser1)
        compoundTable3.addObject(dispenser2)
        compoundTable4.addObject(dispenser3)

        # Add bottle cleaner
        BottleCleaner = world.createObject("BottleCleaner")
        compoundTable5.addObject(BottleCleaner)

        # Add tables to world
        world.addObject(x+2, y+1, Layer.FURNITURE, compoundTable1)
        world.addObject(x+3, y+1, Layer.FURNITURE, compoundTable2)
        world.addObject(x+4, y+1, Layer.FURNITURE, compoundTable3)
        world.addObject(x+5, y+1, Layer.FURNITURE, compoundTable4)
        world.addObject(x+6, y+1, Layer.FURNITURE, compoundTable5)

        mixingJar = world.createObject("Jar")
        # Add to first table
        compoundTable1.addObject(mixingJar)

        # Add substance
        #substance1 = world.createObject("TestSubstance")
        #substance2 = world.createObject("PurpleSubstance")
        #mixingJar.addObject(substance1)
        #mixingJar.addObject(substance2)

        #substanceCleaner = world.createObject("substanceCleaner")
        #mixingJar.addObject(substanceCleaner)

        # Add rusty key
        rustyKey = world.createObject("Key")
        rustyKey.setKeyID(DOOR_KEY_ID)
        world.addObject(x+2, y+2, Layer.OBJECTS, rustyKey)



#        seedJar.setAutoFill(checkObjectName="seed", fillObjectName="Seed", minCount=5)
#        seedJar.name = "seed jar"
        #seedJar.addObject(Seed(world, "red"))

        # Add 5 seeds to the jar
        #for i in range(5):
        #    seedJar.addObject( world.createObject("Seed") )

#        seedTable.addObject(seedJar)
#        world.addObject(x+3, y+1, Layer.FURNITURE, seedTable)

        # Add a shovel in the farm house
        #shovel = world.createObject("Shovel")
        #world.addObject(x+2, y+1, Layer.FURNITURE, shovel)

        # Add a bag of fertilizer
        #fertilizer = world.createObject("FertilizerBag")
        #world.addObject(x+2, y+2, Layer.FURNITURE, fertilizer)






    #
    # Make the archeological dig scenario
    #
    def makeScenarioArchaeologicalDig(self, world, numUserAgents=1):
        numDigSites = 3

        # Set a limit for the number of user agents
        MAX_NUM_AGENTS = 5
        if (numUserAgents > MAX_NUM_AGENTS):
            numUserAgents = MAX_NUM_AGENTS

        # Populate with structures/objects
        buildingMaker = BuildingMaker(world)

        # Fill with grass
        buildingMaker.mkGrassFill(world)
        # Randomly place a few plants (plant1, plant2, plant3)
        for i in range(0, 10):
            randX = self.random.randint(0, world.sizeX - 1)
            randY = self.random.randint(0, world.sizeY - 1)
            ## world.addObject(randX, randY, Layer.OBJECTS, BuildingMaker.mkObject("plant", "plant", "forest1_plant" + str(i % 3 + 1)))

        # Possible artifact ages (in years). Ranges from 100k to 1 million years old, with even numbers.
        artifactAges = [150000, 230000, 370000, 410000, 500000, 675000, 725000, 890000, 930000, 1000000]
        # Shuffle the artifact ages
        self.random.shuffle(artifactAges)
        # Trim to the first numDigSites
        artifactAges = artifactAges[:numDigSites]

        # List dig site locations
        digSiteLocations = [(10, 10), (20, 13), (12, 18)]

        # Add 3 dig sites
        for digSiteIdx, digSiteLocation in enumerate(digSiteLocations):
            self.mkDigSite(digSiteLocation[0], digSiteLocation[1], world, buildingMaker, self.random, digSiteIdx+1, artifactAges[digSiteIdx])

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
            randX = self.random.randint(10, 20)
            randY = self.random.randint(10, 20)

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
            randX = self.random.randint(0, world.sizeX - 1)
            randY = self.random.randint(0, world.sizeY - 1)

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
    def makeScenarioArchaeologicalDigGenericRadioisotope(self, world, numUserAgents=1):
        numDigSites = 3

        # Set a limit for the number of user agents
        MAX_NUM_AGENTS = 5
        if (numUserAgents > MAX_NUM_AGENTS):
            numUserAgents = MAX_NUM_AGENTS

        # Populate with structures/objects
        buildingMaker = BuildingMaker(world)

        # Fill with grass
        buildingMaker.mkGrassFill(world)
        # Randomly place a few plants (plant1, plant2, plant3)
        for i in range(0, 10):
            randX = self.random.randint(0, world.sizeX - 1)
            randY = self.random.randint(0, world.sizeY - 1)
            ## world.addObject(randX, randY, Layer.OBJECTS, BuildingMaker.mkObject("plant", "plant", "forest1_plant" + str(i % 3 + 1)))

        # Possible artifact ages (in years). Ranges from 100k to 1 million years old, with even numbers.
        #artifactAges = [150000, 230000, 370000, 410000, 500000, 675000, 725000, 890000, 930000, 1000000]
        # Shuffle the artifact ages
        #self.random.shuffle(artifactAges)
        # Trim to the first numDigSites
        #artifactAges = artifactAges[:numDigSites]

        # List dig site locations
        #seedSiteLocations = [(10, 10), (20, 13), (12, 18)]
        #experimentalSiteLocations = [(16, 8), (18, 18), (8, 15)]
        digSiteLocations = [(10, 10), (20, 13), (12, 18)] + [(16, 8), (18, 18), (8, 15)]
        # Shuffle
        self.random.shuffle(digSiteLocations)

        #"ArtifactStoneHammer": ArtifactStoneHammer,
        #"ArtifactBrassChisel": ArtifactBrassChisel,
        #"ArtifactIronTongs": ArtifactIronTongs,
        knownArtifactAges = [10000, 4000, 1000]
        oldArtifactAge = self.random.choice([40000, 35000, 30000, 20000])
        mediumArtifactAge = self.random.choice([5000, 4000, 3000, 2000])
        youngArtifactAge = self.random.choice([1700, 1500, 1200])

        print("oldArtifactAge: " + str(oldArtifactAge))
        print("mediumArtifactAge: " + str(mediumArtifactAge))
        print("youngArtifactAge: " + str(youngArtifactAge))

        # Make up 4 faux radioisotope values.  For the real one, it should strongly correlate with the age of the artifact.  For the others, the correlation should be very weak.
        # The real one should be the first one.
        realRadioisotopeValues = knownArtifactAges + [oldArtifactAge, mediumArtifactAge, youngArtifactAge]
        # divide each value by 50,000
        realRadioisotopeValues = [val/50000 for val in realRadioisotopeValues]
        # Add some noise (+/- 0.01) to each value
        realRadioisotopeValues = [val + self.random.uniform(-0.01, 0.01) for val in realRadioisotopeValues]
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
            fakeRadioisotope1Values = [self.random.uniform(0, 1) for i in range(0, len(realRadioisotopeValues))]
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
            fakeRadioisotope2Values = [self.random.uniform(0, 1) for i in range(0, len(realRadioisotopeValues))]
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
            fakeRadioisotope3Values = [self.random.uniform(0, 1) for i in range(0, len(realRadioisotopeValues))]
            # Round to 3 decimal places
            fakeRadioisotope3Values = [round(val, 3) for val in fakeRadioisotope3Values]
            correlation = np.corrcoef(knownArtifactAges + [oldArtifactAge, mediumArtifactAge, youngArtifactAge], fakeRadioisotope3Values)
            if (abs(correlation[0][1]) < 0.1):
                done = True
        #print("Fake radioisotope 3 values: " + str(fakeRadioisotope3Values))
        #print("Correlation: " + str(correlation[0][1]))
        #exit(1)

        # Figure out which channel (1, 2, 3, or 4) should be the "real" one
        channelShift = self.random.choice([0, 1, 2, 3])

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
        self.random.shuffle(unknownArtifacts)

        # Shuffle the order of the seed artifacts
        seedArtifacts = [seedOldArtifact, seedMediumArtifact, seedYoungArtifact]
        self.random.shuffle(seedArtifacts)


        # Add dig sites
        for digSiteIdx, digSiteLocation in enumerate(digSiteLocations):
            if (digSiteIdx < 3):
                # Seed artifact
                artifact = seedArtifacts[digSiteIdx]
                self.mkDigSiteWithObj(digSiteLocation[0], digSiteLocation[1], world, buildingMaker, self.random, digSiteIdx+1, artifact, artifactExposed=True)
            else:
                # Unknown artifact
                artifact = unknownArtifacts[digSiteIdx-3]
                self.mkDigSiteWithObj(digSiteLocation[0], digSiteLocation[1], world, buildingMaker, self.random, digSiteIdx+1, artifact, artifactExposed=False)
                #self.mkDigSite(digSiteLocation[0], digSiteLocation[1], world, buildingMaker, self.random, digSiteIdx+1, artifactAges[digSiteIdx])


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
            randX = self.random.randint(10, 20)
            randY = self.random.randint(10, 20)

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
            randX = self.random.randint(0, world.sizeX - 1)
            randY = self.random.randint(0, world.sizeY - 1)

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
    #   Helpers for soil research scenario
    #

    # Make a field of soil that can be controlled by a soil nutrient manager
    def mkSoilFieldControlled(self, x, y, world, buildingMaker, fieldNumber, width=2, height=2, ):

        # Create the field
        for i in range(0, width):
            for j in range(0, height):
                soilTile = world.createObject("SoilTile")
                # Set a baseline soil nutrient level
                nutrientLevels = self.packSoilNutrients(potassium=1, titanium=1, lithium=1, thorium=2, barium=1)
                soilTile.attributes["soilNutrients"] = nutrientLevels

                world.addObject(x+i, y+j, Layer.BUILDING, soilTile)

        # Add a soil nutrient manager
        # TODO

        # Add a sign saying what field this is
        sign = world.createObject("Sign")        
        sign.setText("Soil Field #" + str(fieldNumber))
        world.addObject(x, y+2, Layer.FURNITURE, sign)        

        # Add the soil controller
        soilController = world.createObject("SoilController")
        # TODO: Set the soil that this field controls

        # Put the soil controller on a table
        soilControllerTable = world.createObject("Table")
        soilControllerTable.addObject(soilController)
        world.addObject(x+1, y+2, Layer.FURNITURE, soilControllerTable)



    def mkSoilResearchBuilding(self, x, y, world, buildingMaker):
        # Create a small building
        houseSizeX = 4
        houseSizeY = 4
        buildingMaker.mkBuildingOneRoom(world, x=x+1, y=y, width=houseSizeX, height=houseSizeY, signText="Soil Research Facility")

        # Add a seed jar
        seedJar = world.createObject("Jar")
        #seedJar.setAutoFill(checkObjectName="seed", fillObjectName="Seed", minCount=5)        
        seedJar.setAutoFill(checkObjectName="seed", fillObjectName="SeedRequiringNutrients", minCount=5)
        seedJar.name = "seed jar"        

        # Table for seed jar
        seedTable = world.createObject("Table")
        seedTable.addObject(seedJar)
        world.addObject(x+3, y+1, Layer.FURNITURE, seedTable)

        # Add a soil nutrient meter
        soilMeter = world.createObject("SoilNutrientMeter")
        # Table for soil meter
        soilMeterTable = world.createObject("Table")
        soilMeterTable.addObject(soilMeter)
        world.addObject(x+2, y+1, Layer.FURNITURE, soilMeterTable)

        # Add a shovel in the farm house
        shovel = world.createObject("Shovel")
        world.addObject(x+2, y+2, Layer.FURNITURE, shovel)



    # Packing soil nutrients (potassium, titanium, lithium, thorium, barium)
    def packSoilNutrients(self, potassium, titanium, lithium, thorium, barium):
        packed = {
            "potassium": potassium,
            "titanium": titanium,
            "lithium": lithium,
            "thorium": thorium,
            "barium": barium            
        }
        return packed
    
    def packSoilNutrientsList(self, nutrients:list):
        packed = {
            "potassium": nutrients[0],
            "titanium": nutrients[1],
            "lithium": nutrients[2],
            "thorium": nutrients[3],
            "barium": nutrients[4]            
        }
        return packed


    #
    # Make the plant growing scenario
    #
    def makeScenarioPlantGrowing(self, world, numUserAgents=1):
        numPlantSites = 3

        # Set a limit for the number of user agents
        MAX_NUM_AGENTS = 5
        if (numUserAgents > MAX_NUM_AGENTS):
            numUserAgents = MAX_NUM_AGENTS

        # Populate with structures/objects
        buildingMaker = BuildingMaker(world)

        # Fill with grass
        buildingMaker.mkGrassFill(world)

        # Soil research building
        self.mkSoilResearchBuilding(12, 8, world, buildingMaker)

        # Primary pilot field area
        pilotFieldStartX = 6
        pilotFieldStartY = 14
        pilotFieldSizeX = 4
        pilotFieldSizeY = 3
        for i in range(0, pilotFieldSizeX):
            for j in range(0, pilotFieldSizeY):
                world.addObject(pilotFieldStartX+i, pilotFieldStartY+j, Layer.BUILDING, world.createObject("SoilTile"))
                # TODO: Add plants, etc. 

        # Sign for the pilot field                
        sign = world.createObject("Sign")        
        sign.setText("Pilot Field")
        world.addObject(pilotFieldStartX, pilotFieldStartY+pilotFieldSizeY, Layer.FURNITURE, sign)        


        # Make 3 test fields
        testFieldStartX = 12
        testFieldStartY = 15

        for i in range(0, numPlantSites):
            self.mkSoilFieldControlled(testFieldStartX + i*5, testFieldStartY, world, buildingMaker, i+1)


        # Make path along fields
        self.mkPathX(6, 18, 18, world)
        # Make path to research building
        self.mkPathY(15, 12, 12, world)

        # Make fence around entire research station + fields
        self.mkFenceX(4, 6, 22, world)      # Top
        self.mkFenceY(4, 6, 14, world)      # Left
        self.mkFenceY(25, 6, 15, world)     # Right
        self.mkFenceX(4, 20, 10, world)     # Bottom (left)
        self.mkFenceX(17, 20, 9, world)     # Bottom (right)

        # Sign for the whole research facility
        sign = world.createObject("Sign")        
        sign.setText("Botanical Research Facility")
        world.addObject(13, 21, Layer.FURNITURE, sign)        

        # Add big trees to either side of the research facility        
        world.addObject(11, 10, Layer.OBJECTS, world.createObject("PlantTreeBig"))
        world.addObject(9, 10, Layer.OBJECTS, world.createObject("PlantTreeBig"))
        world.addObject(7, 10, Layer.OBJECTS, world.createObject("PlantTreeBig"))

        world.addObject(18, 10, Layer.OBJECTS, world.createObject("PlantTreeBig"))
        world.addObject(20, 10, Layer.OBJECTS, world.createObject("PlantTreeBig"))
        world.addObject(22, 10, Layer.OBJECTS, world.createObject("PlantTreeBig"))


        # Randomly place a few decorative plants
        plantCount = 0
        minPlants = 15
        while (plantCount < minPlants):
            # Pick a random location
            randX = self.random.randint(0, world.sizeX - 1)
            randY = self.random.randint(0, world.sizeY - 1)

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
        #world.addTeleportLocation("base camp", 13, 14)
        #for digSiteIdx, digSiteLocation in enumerate(digSiteLocations):
        #    world.addTeleportLocation("dig site " + str(digSiteIdx+1), digSiteLocation[0]-1, digSiteLocation[1]+1)

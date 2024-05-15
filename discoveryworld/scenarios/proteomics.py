import random
from discoveryworld.Agent import Agent, NPC
from discoveryworld.DialogTree import DialogMaker

from discoveryworld.Layer import Layer
from discoveryworld.buildings.soil_research import mkRandomSoilNutrientsWithSetValues, mkSoilFieldControlled, mkSoilResearchBuilding
from discoveryworld.buildings.house import mkBuildingOneRoom
from discoveryworld.buildings.terrain import mkFenceX, mkFenceY, mkGrassFill, mkPathX, mkPathY, mkTallTree
# import mkBuildingOneRoom
from discoveryworld.objects import *
from discoveryworld.Pathfinding import *




def mkProteomicsResearchBuilding(x, y, world):
    # Create a small building
    houseSizeX = 4
    houseSizeY = 4
    mkBuildingOneRoom(world, x=x+1, y=y, width=houseSizeX, height=houseSizeY, signText="Research Building")

    # Add a seed jar
    #seedJar = world.createObject("Jar")
    #seedJar.setAutoFill(checkObjectName="seed", fillObjectName="Seed", minCount=5)
    #seedJar.setAutoFill(checkObjectName="seed", fillObjectName=whichSeedName, minCount=1, replenishTime=0)
    #seedJar.name = "seed jar"

    # Table for seed jar
    seedTable = world.createObject("Table")
    #seedTable.addObject(seedJar)
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


def makeScenarioProteomics(world, numUserAgents=1):
    scoringInfo = {}
    scoringInfo["criticalHypotheses"] = []

    # Example of using the world RNG
    whichNutrientPositive = world.rng.choice([1, 2, 3])

    # Set a limit for the number of user agents
    MAX_NUM_AGENTS = 5
    if (numUserAgents > MAX_NUM_AGENTS):
        numUserAgents = MAX_NUM_AGENTS

    # Populate with structures/objects

    # Fill with grass
    mkGrassFill(world)

    # Soil research building
    #mkProteomicsResearchBuilding(12, 12, world)
    world.addTeleportLocation("Research Building", 12+3, 12+2)
 

    # Make path along fields
    #mkPathX(10, 18, 10, world)
    #mkPathX(10, 17, 10, world)
    # Make path to research building
    #mkPathY(15, 12, 12, world)

    # Bottom
    mkFenceX(9, 19, 5, world)     # Bottom (left)
    mkFenceX(17, 19, 5, world)     # Bottom (right)
    # Top
    mkFenceX(9, 9, 5, world)     # Top (left)
    mkFenceX(17, 9, 5, world)     # Top (right)
    # Left
    mkFenceY(9, 9, 4, world)     # Left (top)
    mkFenceY(9, 16, 3, world)     # Left (bottom)
    # Right
    mkFenceY(21, 9, 4, world)     # Right (top)
    mkFenceY(21, 16, 3, world)     # Right (bottom)


    # Sign for the whole research facility
    sign = world.createObject("Sign")
    sign.setText("Proteomics Research Facility")
    world.addObject(13, 20, Layer.FURNITURE, sign)


    statueLocations = [(12, 12), (12, 16), (18, 12), (18, 16), (15, 14)]

    for statueLocation in statueLocations:
        # Add a plot of path under the statue
        for i in range(-1, 2):
            for j in range(-1, 2):
                world.addObject(statueLocation[0]+i, statueLocation[1]+j, Layer.BUILDING, world.createObject("Path"))
        world.addObject(statueLocation[0], statueLocation[1], Layer.FURNITURE, world.createObject("Statue"))



    # Add big trees to either side of the research facility
    #mkTallTree(12, 10, world)
    #mkTallTree(9, 10, world)
    #mkTallTree(7, 10, world)

    #mkTallTree(18, 10, world)
    #mkTallTree(20, 10, world)
    #mkTallTree(22, 10, world)

    # Trees at bottom entrance
    mkTallTree(12, 20, world)
    mkTallTree(18, 20, world)
    # Trees at top entrance
    mkTallTree(12, 8, world)
    mkTallTree(18, 8, world)
    # Trees at left entrance
    mkTallTree(8, 12, world)
    mkTallTree(8, 16, world)
    # Trees at right entrance
    mkTallTree(22, 12, world)
    mkTallTree(22, 16, world)

    # Trees at 4 corners
    mkTallTree(10, 10, world)
    mkTallTree(10, 18, world)
    mkTallTree(20, 10, world)
    mkTallTree(20, 18, world)


    # Animal locations are nominally 4 along the top, 4 along the bottom, and 2 along the sides. 
    animalLocations = [(4, 4), (12, 4), (20, 4), (28, 4)]   # top
    animalLocations += [(4, 28), (12, 28), (20, 28), (28, 28)]   # bottom
    animalLocations += [(4, 12), (4, 20), (28, 12), (28, 20)]   # sides
    random.shuffle(animalLocations)

    animals = []
    for i in range(0, 10):
        animals.append(NPCMovingAnimal(world, "Animal" + str(i), preferredX=animalLocations[i][0], preferredY=animalLocations[i][1], homeX=animalLocations[i][0], homeY=animalLocations[i][1]))
        world.addObject(animalLocations[i][0], animalLocations[i][1], Layer.AGENT, animals[i])
        world.addAgent(animals[i])


    # Randomly place trees near the animal locations, but not directly on them.
    for location in animalLocations:
        treesPlaced = 0
        while (treesPlaced < 2):
            # Pick a random location
            randX = world.rng.randint(location[0]-3, location[0]+3)
            randY = world.rng.randint(location[1]-3, location[1]+3)

            # Make sure the location is within the world bounds
            if (randX < 0):
                randX = 0
            if (randX >= world.sizeX):
                randX = world.sizeX - 1
            if (randY < 0):
                randY = 0
            if (randY >= world.sizeY):
                randY = world.sizeY - 1

            # Make sure the location isn't the same as the animal location
            if ((randX == location[0]) and (randY == location[1])):
                continue

            # Place a tree
            mkTallTree(randX, randY, world)
            treesPlaced += 1

    # # Add NPC animals
    # for i in range(0, 5):
    #     # Add a random animal
    #     animal = NPCMovingAnimal(world, "Animal" + str(i))
    #     world.addObject(15+i, 15, Layer.AGENT, animal)
    #     # Add the animal to the list of agents
    #     world.addAgent(animal)

    # Randomly place a few decorative plants
    plantCount = 0
    minPlants = 25
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


    # Add some small plants (randomly placed)
    plantCount = 0
    minPlants = 15
    while (plantCount < minPlants):
        # Pick a random location
        randX = world.rng.randint(2, world.sizeX - 2)
        randY = world.rng.randint(2, world.sizeY - 2)

        # Check to see if there are any objects other than grass there
        objs = world.getObjectsAt(randX, randY)
        # Get types of objects
        objTypes = [obj.type for obj in objs]
        # Check to see that there is grass here
        if ("grass" in objTypes):
            # Check that there is not other things here
            if (len(objTypes) == 1):
                # Add a plant
                world.addObject(randX, randY, Layer.OBJECTS, world.createObject("PlantRandomSmall"))
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



# NPC
class NPCMovingAnimal(NPC):
    #def __init__(self, world, name):
    def __init__(self, world, name, preferredX=15, preferredY=15, homeX=15, homeY=15):
        # Default sprite name
        super().__init__(world, name, defaultSpriteName="character32_agent_facing_east")

        # Randomly pick a sprite

        # Rendering
        self.attributes["faceDirection"] = "east"
        #self.spriteCharacterPrefix = "character32_"
        # Randomly pick a sprite
        #spriteChoices = ["character32_", "character17_", "character16_", "character35_", "character9_"]
        spriteChoices = ["enemy01_04_", "enemy06_04_", "enemy10_02_", "enemy11_01_", "enemy14_03_", "enemy16_03_"]
        self.spriteCharacterPrefix = random.choice(spriteChoices)

        # Default attributes
        self.attributes["isMovable"] = False                       # Elder cannot be picked.
        self.attributes['isContainer'] = True                      # Elder's inventory is a container.
        self.attributes['isOpenable'] = False                      # Can't be opened
        self.attributes['isOpenContainer'] = False                 # Prevent other players from accessing its inventory.
        self.attributes['containerPrefix'] = "on"                  # Container prefix (e.g. "in" or "on")

        # Dialog attributes
        self.attributes['isDialogable'] = True                    # Can it be dialoged with?

        # NPC States
        self.attributes['dialogAgentsSpokenWith'] = []             # List of dialog agents that this NPC has spoken with

        self.pathfinder = Pathfinder()

        # Add default action (wandering), which has a low priority
        self.addAutopilotActionToQueue( AutopilotAction_Wander(preferredX=preferredX, preferredY=preferredY) )

        # Store this agent's home location
        self.attributes['homeX'] = homeX
        self.attributes['homeY'] = homeY

    # Tick
    def tick(self):
        # Stop if the object has already had tick() called this update -- this might have happened if the object moved locations in this current update cycle.
        if (self.tickCompleted):
            return

        # Debug
        print("*** NPC States (name: " + self.name + "): " + str(self.attributes['states']))

        # Call superclass
        NPC.tick(self)

        # Check for specific states
        if (("goHome_" + self.name) in self.attributes['states']):
            # Remove state
            self.attributes['states'].remove("goHome_" + self.name)
            # Clear all actions in the autopilot action queue
            self.clearAutopilotActionQueue()
            # Move to a specific location
            homeX = self.attributes['homeX']
            homeY = self.attributes['homeY']
            self.addAutopilotActionToQueue( AutopilotAction_GotoXY(x=homeX, y=homeY, priority=100) )

        # Display autopilot action queue (debug)
        print(self.displayAutopilotQueueStr())

        # Get the NPC's current autopilot action
        if (len(self.autopilotActionQueue) > 0) and (self.attributes['inDialogWith'] == None):
            # Get the current autopilot action
            curAutopilotAction = self.autopilotActionQueue[0]
            # Call the action interpreter to run it
            #print("(Agent: " + self.name + "): Calling action interpreter with action: " + str(curAutopilotAction))
            result = self.pathfinder.actionInterpreter(curAutopilotAction, agent=self, world=self.world)
            #print("(Agent: " + self.name + "): Result of calling action interpreter: " + str(result))

            # If the result is "COMPLETED", then remove the action from the queue
            if (result == ActionResult.COMPLETED):
                self.autopilotActionQueue.remove(curAutopilotAction)
                #print("(Agent: " + self.name + "): Action completed.  Removed from queue.")
            # If the result is "FAILURE", then remove the action from the queue
            elif (result == ActionResult.FAILURE):
                self.autopilotActionQueue.remove(curAutopilotAction)
                #print("(Agent: " + self.name + "): Action failed.  Removed from queue.")
            # If the result is "INVALID", then remove the action from the queue
            elif (result == ActionResult.INVALID):
                self.autopilotActionQueue.remove(curAutopilotAction)
                #print("(Agent: " + self.name + "): Action invalid.  Removed from queue.")


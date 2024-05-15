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


# Generate data for the clustering task
def generate_clustering_data(clusterSeed, numDimensions, numInliers, numOutliers):
    rng = random.Random(clusterSeed)
    if numDimensions not in [1, 2, 3, 4]:
        raise ValueError("Dimensions must be between 1 and 4.")
    
    # Generate a random center within the unit space for the inliers
    #center = np.random.rand(numDimensions)
    inliers = None
    outliers = None
    attempts0 = 0
    while (inliers == None or outliers == None):
        center = [rng.uniform(0.2, 0.8), rng.uniform(0.2, 0.8)]
        #print("Center is ", center)

        # Function to generate points in a sphere around a center
        def generate_points(n, radius, center):
            points = []
            attempts = 0
            while (len(points) < n):
                # Randomly generate an angle
                angle = rng.uniform(0, 2 * np.pi)
                # Generate a point (x1, y1), from center (x0, y0) and radius r
                x1 = center[0] + radius * math.cos(angle)
                y1 = center[1] + radius * math.sin(angle)

                #print("Generated point: ", (x1, y1))
                # Check the points are within the (0-1) space
                if (x1 >= 0 and x1 <= 1) and (y1 >= 0 and y1 <= 1):
                    points.append([x1, y1])

                attempts += 1
                if (attempts > 1000):
                    return None
            return points
        
        # Generate inliers and outliers
        inliers = generate_points(numInliers, 0.1, center)
        outliers = generate_points(numOutliers, 0.5, center)

        attempts0 += 1
        if (attempts0 > 1000):
            print("Failed to generate random numbers for clustering data.  The parameters provided may be invalid or impossible/improbable to generate data for.")
            return None, None
    
    return inliers, outliers

import matplotlib.pyplot as plt

def plot_data(inliers, outliers):
    import matplotlib.pyplot as plt

    # Plot inliers
    #plt.scatter(inliers[:, 0], inliers[:, 1], c='blue', label='Inliers', edgecolors='w')
    plt.scatter([x[0] for x in inliers], [x[1] for x in inliers], c='blue', label='Inliers', edgecolors='w')
    
    # Plot outliers
    #plt.scatter(outliers[:, 0], outliers[:, 1], c='red', label='Outliers', marker='x', edgecolors='w')
    plt.scatter([x[0] for x in outliers], [x[1] for x in outliers], c='red', label='Outliers', marker='x', edgecolors='w')
    
    plt.xlabel('Dimension 1')
    plt.ylabel('Dimension 2')
    plt.title('Clustering Data Visualization')
    # Make the range 0-1 on both axes
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.legend()
    plt.grid(True)
    plt.show()

# Example usage
# rng = random.Random(0)
# inliers, outliers = generate_clustering_data(rng, numDimensions=2, numInliers=4, numOutliers=1)
# print("Inliers:\n", inliers)
# print("Outliers:\n", outliers)
# plot_data(inliers, outliers)
# exit(1)

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

    # The index of the correct animal for this scenario
    answerAnimalIdx = world.randomSeed % 5
    # names of the animals (indexed correctly -- e.g. animal index 0 is called a "spheroid", animal index 1 is called a "echojelly", etc.)
    animalNames = ["spheroid", "echojelly", "vortisquid", "animaplant", "prismatic beast"]
    answerAnimalName = animalNames[answerAnimalIdx]

    scoringInfo["criticalHypotheses"].append("The " + answerAnimalName + " has proteomics values that appear to be outliers compared to the other animals.")

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
    scoringInfo["statues"] = []
    scoringInfo["correctStatue"] = None
    for idx, statueLocation in enumerate(statueLocations):
        # Add a plot of path under the statue
        for i in range(-1, 2):
            for j in range(-1, 2):
                world.addObject(statueLocation[0]+i, statueLocation[1]+j, Layer.BUILDING, world.createObject("Path"))
        statue = world.createObject("Statue")
        statue.name = "statue of a " + animalNames[idx]
        world.addObject(statueLocation[0], statueLocation[1], Layer.FURNITURE, statue)

        # Scoring info
        if (idx == answerAnimalIdx):
            scoringInfo["correctStatue"] = statue
        scoringInfo["statues"].append(statue)

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


    # Add a table near the sign
    table = world.createObject("Table")
    world.addObject(14, 19, Layer.FURNITURE, table)
    # Add a meter to the table
    meter = world.createObject("ProteomicsMeter")
    table.addObject(meter)
    scoringInfo["meter"] = meter

    # Add a flag under the table
    flag = world.createObject("Flag")
    world.addObject(14, 20, Layer.FURNITURE, flag)
    scoringInfo["flag"] = flag


    # Animal locations are nominally 4 along the top, 4 along the bottom, and 2 along the sides. 
    animalLocations = [(4, 4), (12, 4), (20, 4), (28, 4)]   # top
    animalLocations += [(4, 28), (12, 28), (20, 28), (28, 28)]   # bottom
    animalLocations += [(4, 12), (4, 20), (28, 12), (28, 20)]   # sides
    random.shuffle(animalLocations)


    # Generate proteomics values
    numDimensions = 2
    numInliers = 5
    numOutliers = 1
    inliers, outliers = generate_clustering_data(world.randomSeed, numDimensions, numInliers, numOutliers)

    # Print the inliers and outliers
    # print("Inliers: ") 
    # for inlier in inliers:
    #     print(inlier)
    # print("Outliers: ")
    # for outlier in outliers:
    #     print(outlier)
    
    # # Plot the data
    # plot_data(inliers, outliers)
    #exit(1)

    inlierProteomicsValues = []
    for inlier in inliers:
        inlierValues = {}
        for i in range(0, numDimensions):
            inlierValues["Protein " + chr(ord('A') + i)] = inlier[i]
        inlierProteomicsValues.append(inlierValues)

    outlierProteomicsValues = []
    for outlier in outliers:
        outlierValues = {}
        for i in range(0, numDimensions):
            outlierValues["Protein " + chr(ord('A') + i)] = outlier[i]
        outlierProteomicsValues.append(outlierValues)

    # Generate animals
    animals = []
    for i in range(0, 10):
        animalIdx = i % 5
        proteomicsValues = None
        if (animalIdx == answerAnimalIdx):
            proteomicsValues = copy.deepcopy(outlierProteomicsValues[0])
        else:
            proteomicsValues = copy.deepcopy(inlierProteomicsValues[animalIdx])
            
        animal = mkAnimal(animalIdx, world, animalLocations[i][0], animalLocations[i][1], proteomicsValues=proteomicsValues)
        world.addObject(animalLocations[i][0], animalLocations[i][1], Layer.AGENT, animal)
        world.addAgent(animal)
        animals.append(animal)

        # Store all the references to each of the 5 animal types
        if ("animal" + str(animalIdx) not in scoringInfo):
            scoringInfo["animal" + str(animalIdx)] = []
        scoringInfo["animal" + str(animalIdx)].append(animal)


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
    def __init__(self, world, name, preferredX=15, preferredY=15, spriteCharacterPrefix="character32_"):
        # Default sprite name
        #super().__init__(world, name, defaultSpriteName="character32_agent_facing_east")
        super().__init__(world, name, defaultSpriteName=spriteCharacterPrefix + "agent_facing_east")

        # Randomly pick a sprite

        # Rendering
        self.attributes["faceDirection"] = "east"
        #self.spriteCharacterPrefix = "character32_"
        # Randomly pick a sprite
        #spriteChoices = ["character32_", "character17_", "character16_", "character35_", "character9_"]
        #spriteChoices = ["enemy01_04_", "enemy06_04_", "enemy10_02_", "enemy11_01_", "enemy14_03_", "enemy16_03_"]
        #self.spriteCharacterPrefix = random.choice(spriteChoices)
        self.spriteCharacterPrefix = spriteCharacterPrefix

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
        #self.attributes['homeX'] = homeX
        #self.attributes['homeY'] = homeY

    # Tick
    def tick(self):
        # Stop if the object has already had tick() called this update -- this might have happened if the object moved locations in this current update cycle.
        if (self.tickCompleted):
            return

        # Debug
        print("*** NPC States (name: " + self.name + "): " + str(self.attributes['states']))

        # Call superclass
        NPC.tick(self)

        # # Check for specific states
        # if (("goHome_" + self.name) in self.attributes['states']):
        #     # Remove state
        #     self.attributes['states'].remove("goHome_" + self.name)
        #     # Clear all actions in the autopilot action queue
        #     self.clearAutopilotActionQueue()
        #     # Move to a specific location
        #     homeX = self.attributes['homeX']
        #     homeY = self.attributes['homeY']
        #     self.addAutopilotActionToQueue( AutopilotAction_GotoXY(x=homeX, y=homeY, priority=100) )

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


# Generator for a specific animal
def mkAnimal(animalIdx:int, world, preferredX:int, preferredY:int, proteomicsValues=None):
    if (animalIdx == 0):
        return NPCAnimal1(world, preferredX, preferredY, proteomicsValues)
    elif (animalIdx == 1):
        return NPCAnimal2(world, preferredX, preferredY, proteomicsValues)
    elif (animalIdx == 2):
        return NPCAnimal3(world, preferredX, preferredY, proteomicsValues)
    elif (animalIdx == 3):
        return NPCAnimal4(world, preferredX, preferredY, proteomicsValues)
    elif (animalIdx == 4):
        return NPCAnimal5(world, preferredX, preferredY, proteomicsValues)
    else:
        return None


class NPCAnimal1(NPCMovingAnimal):
    def __init__(self, world, preferredX, preferredY, proteomicsValues):
        name = "spheroid"
        spriteCharacterPrefix = "enemy01_04_"
        NPCMovingAnimal.__init__(self, world, name, preferredX=preferredX, preferredY=preferredY, spriteCharacterPrefix=spriteCharacterPrefix)
        self.attributes["proteomicsValues"] = proteomicsValues

class NPCAnimal2(NPCMovingAnimal):
    def __init__(self, world, preferredX, preferredY, proteomicsValues):
        name = "echojelly"
        spriteCharacterPrefix = "enemy06_04_"
        NPCMovingAnimal.__init__(self, world, name, preferredX=preferredX, preferredY=preferredY, spriteCharacterPrefix=spriteCharacterPrefix)
        self.attributes["proteomicsValues"] = proteomicsValues

class NPCAnimal3(NPCMovingAnimal):
    def __init__(self, world, preferredX, preferredY, proteomicsValues):
        name = "vortisquid"
        spriteCharacterPrefix = "enemy10_02_"
        NPCMovingAnimal.__init__(self, world, name, preferredX=preferredX, preferredY=preferredY, spriteCharacterPrefix=spriteCharacterPrefix)
        self.attributes["proteomicsValues"] = proteomicsValues

class NPCAnimal4(NPCMovingAnimal):
    def __init__(self, world, preferredX, preferredY, proteomicsValues):
        name = "animaplant"
        spriteCharacterPrefix = "enemy11_01_"
        NPCMovingAnimal.__init__(self, world, name, preferredX=preferredX, preferredY=preferredY, spriteCharacterPrefix=spriteCharacterPrefix)
        self.attributes["proteomicsValues"] = proteomicsValues

class NPCAnimal5(NPCMovingAnimal):
    def __init__(self, world, preferredX, preferredY, proteomicsValues):
        name = "prismatic beast"
        spriteCharacterPrefix = "enemy16_03_"
        NPCMovingAnimal.__init__(self, world, name, preferredX=preferredX, preferredY=preferredY, spriteCharacterPrefix=spriteCharacterPrefix)
        self.attributes["proteomicsValues"] = proteomicsValues

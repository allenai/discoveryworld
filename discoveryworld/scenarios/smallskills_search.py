import random

from discoveryworld.Agent import NPC, Agent
from discoveryworld.DialogTree import DialogMaker
from discoveryworld.Layer import Layer
from discoveryworld.Pathfinding import Pathfinder
from discoveryworld.buildings.colony import mkStorageShed, mkStorageShedChallenge
from discoveryworld.buildings.terrain import mkGrassFill, mkPathX, mkTallTree
from discoveryworld.buildings.house import mkBuildingDivided, mkBuildingOneRoom, mkTableAndChairs
from discoveryworld.DialogTree import DialogTree, DialogNode
from discoveryworld.TaskScorer import Task, ScorecardElement

def mkRoomKitchen(world, startX, startY, numDevices=4):
    # Add a fridge, stove, and sink
    deviceNames = ["Fridge", "Stove", "Sink", "Table"]
    devices = []
    for deviceName in deviceNames:
        device = world.createObject(deviceName)
        devices.append(device)
        if (deviceName == "Table"):
            # Randomly add an object to the table
            if (random.randint(0, 1) == 0):
                device.addObject(world.createObject("Mushroom"))
    random.shuffle(devices)

    # Add to the top
    count = 0
    for device in devices:
        world.addObject(startX + 1 + count, startY, Layer.OBJECTS, device)
        count += 1
        if (count >= numDevices):
            break

    # Add a table and chairs
    chairsPresent = []
    if (world.rng.randint(0, 1) == 0):
        chairsPresent.append("n")
    if (world.rng.randint(0, 1) == 0):
        chairsPresent.append("s")
    if (world.rng.randint(0, 1) == 0):
        chairsPresent.append("e")
    if (world.rng.randint(0, 1) == 0):
        chairsPresent.append("w")
    mainTable = mkTableAndChairs(world, startX+2, startY+3, chairsPresent=chairsPresent)
    randomObjects = []
    randomObjects.append(world.createObject("Mushroom"))
    randomObjects.append(world.createObject("FlowerPot"))
    randomObjects.append(world.createObject("Seed"))
    randomObjects.append(world.createObject("Coin"))
    randomObjects.append(world.createObject("Key"))
    randomObjects.append(world.createObject("ColoredFlower", "red"))
    randomObjects.append(world.createObject("ColoredFlower", "blue"))
    if (world.rng.randint(0, 5) != 0):
        mainTable.addObject(random.choice(randomObjects))


def mkRoomBedroom(world, startX, startY):
    objectNamesToAdd = ["Bed", "TableBedside"]
    objectsToAdd = [world.createObject(objectName) for objectName in objectNamesToAdd]
    random.shuffle(objectsToAdd)
    count = 0
    for obj in objectsToAdd:
        world.addObject(startX + 1 + count, startY, Layer.OBJECTS, obj)
        if (obj.name == "table"):
            # Randomly add an object to the table
            if (random.randint(0, 5) != 0):
                randomObjects = []
                randomObjects.append(world.createObject("Mushroom"))
                randomObjects.append(world.createObject("FlowerPot"))
                randomObjects.append(world.createObject("Seed"))
                randomObjects.append(world.createObject("Coin"))
                randomObjects.append(world.createObject("Key"))
                randomObjects.append(world.createObject("ColoredFlower", "red"))
                randomObjects.append(world.createObject("ColoredFlower", "blue"))
                obj.addObject(random.choice(randomObjects))

        count += 1

    # Add a chair
    if (world.rng.randint(0, 1) == 0):
        world.addObject(startX + world.rng.randint(0, 3), startY + 3, Layer.OBJECTS, world.createObject("Chair"))


def mkRoomScienceLab(world, startX, startY):
    # Add a microscope, spectrometer, and petri dish
    deviceNames = ["Microscope", "Spectrometer", "PetriDish"]
    devices = []
    for deviceName in deviceNames:
        device = world.createObject(deviceName)
        devices.append(device)
    random.shuffle(devices)

    # Add to the top
    count = 0
    for device in devices:
        table = world.createObject("Table")
        table.addObject(device)
        world.addObject(startX + 1 + count, startY, Layer.OBJECTS, table)
        count += 1

    # Add a table and chairs
    chairsPresent = []
    if (world.rng.randint(0, 1) == 0):
        chairsPresent.append("n")
    if (world.rng.randint(0, 1) == 0):
        chairsPresent.append("s")
    if (world.rng.randint(0, 1) == 0):
        chairsPresent.append("e")
    if (world.rng.randint(0, 1) == 0):
        chairsPresent.append("w")
    mainTable = mkTableAndChairs(world, startX+2, startY+3, chairsPresent=chairsPresent)
    randomObjects = []
    randomObjects.append(world.createObject("Mushroom"))
    randomObjects.append(world.createObject("FlowerPot"))
    randomObjects.append(world.createObject("Seed"))
    randomObjects.append(world.createObject("Coin"))
    randomObjects.append(world.createObject("Key"))
    randomObjects.append(world.createObject("ColoredFlower", "red"))
    randomObjects.append(world.createObject("ColoredFlower", "blue"))
    if (world.rng.randint(0, 5) != 0):
        mainTable.addObject(random.choice(randomObjects))

# Test whether an agent can successfully complete a scenario that just involves traversing a dialog tree
def makeScenarioSearchTest(world, numUserAgents=1):
    scoringInfo = {}
    scoringInfo["criticalHypotheses"] = []

    # Set a limit for the number of user agents
    MAX_NUM_AGENTS = 1
    if (numUserAgents > MAX_NUM_AGENTS):
        numUserAgents = MAX_NUM_AGENTS

    # Populate with structures/objects
    # Fill with grass
    mkGrassFill(world)

    # Buildings
    startX = 10
    startY = 10
    width = 13
    height = 15
    mkBuildingOneRoom(world, x=startX, y=startY, width=width, height=height, signText="House", includeDoor=True, doorKeyID = 0)

    locations = {}

    roomStartLocations = []
    roomStartLocations.append((startX, startY+1))
    roomStartLocations.append((startX+7, startY+1))
    roomStartLocations.append((startX, startY+9))
    roomStartLocations.append((startX+8, startY+9))

    random.shuffle(roomStartLocations)

    # Add a kitchen
    numKitchenDevices = 4
    if (roomStartLocations[0][1] >= startY+9):
        numKitchenDevices = 3   # Make a smaller kitchen if it's on the bottom
    mkRoomKitchen(world, roomStartLocations[0][0], roomStartLocations[0][1], numDevices=numKitchenDevices)
    locations["kitchen"] = {"x": roomStartLocations[0][0], "y": roomStartLocations[0][1], "width": 5, "height": 5}

    # Add a bedroom
    mkRoomBedroom(world, roomStartLocations[1][0], roomStartLocations[1][1])
    locations["bedroom"] = {"x": roomStartLocations[1][0], "y": roomStartLocations[1][1], "width": 5, "height": 5}

    # Add a science lab
    mkRoomScienceLab(world, roomStartLocations[2][0], roomStartLocations[2][1])
    locations["science lab"] = {"x": roomStartLocations[2][0], "y": roomStartLocations[2][1], "width": 5, "height": 5}

    # Empty room
    locations["empty room"] = {"x": roomStartLocations[3][0], "y": roomStartLocations[3][1], "width": 5, "height": 5}

    # Add a small farmers field out back
    fieldLocationX = startX + random.randint(0, width-2)
    fieldLocationY = startY - random.randint(5, 7)
    for i in range(0, 3):
        for j in range(0, 3):
            # Add soil tile
            world.addObject(fieldLocationX + i, fieldLocationY + j, Layer.WORLD, world.createObject("SoilTile"))
            if (random.randint(0, 2) == 0):
                world.addObject(fieldLocationX + i, fieldLocationY + j, Layer.OBJECTS, world.createObject("PlantGeneric"))
    locations["soil plot"] = {"x": fieldLocationX, "y": fieldLocationY, "width": 3, "height": 3}

    scoringInfo["locations"] = locations

    # Pick a random task location
    taskLocation = random.choice(list(locations.keys()))
    scoringInfo["taskLocation"] = taskLocation
    # Store the valid rectangle for the task location
    taskLocationRect = locations[taskLocation]
    scoringInfo["taskLocationRect"] = {
        "startX": taskLocationRect["x"],
        "startY": taskLocationRect["y"],
        "endX": taskLocationRect["x"] + taskLocationRect["width"],
        "endY": taskLocationRect["y"] + taskLocationRect["height"]
    }

    # Add a hallway
    for i in range(1, width - 1):
        if (i != 5) and (i != 6) and (i != 7):
            world.addObject(startX + i, startY + 6, Layer.BUILDING, world.createObject("Wall"))
            world.addObject(startX + i, startY + 8, Layer.BUILDING, world.createObject("Wall"))
    for i in range(1, height - 1):
        if (i != 5) and (i != 6) and (i != 7) and (i != 8) and (i != 9):
            world.addObject(startX + 5, startY + i, Layer.BUILDING, world.createObject("Wall"))
            world.addObject(startX + 7, startY + i, Layer.BUILDING, world.createObject("Wall"))

    # Replace back wall with a door
    doorLocationX = startX + 6
    doorLocationY = startY
    objsAtLocation = world.getObjectsAt(doorLocationX, doorLocationY)
    wallsAtLocation = [obj for obj in objsAtLocation if obj.type == "wall"]
    for wall in wallsAtLocation:
        world.removeObject(wall)
    door = world.createObject("Door")
    world.addObject(doorLocationX, doorLocationY, Layer.FURNITURE, door)


    # Randomly place the flag somewhere on the map
    flag = world.createObject("Flag")
    scoringInfo["flag"] = flag
    flagPlaced = False
    while (flagPlaced == False):
        # Randomly pick a location
        randX = random.randint(startX-4, startX+width+3)
        randY = random.randint(startY-3, startY+height+3)

        # Check to see if there are any objects there
        objs = world.getObjectsAt(randX, randY)
        # Check to see if the location is unpassable
        if (world.isPassable(randX, randY) == False):
            continue
        # Check to see if there are any walls or doors there
        objTypes = [obj.type for obj in objs]
        if ("wall" in objTypes) or ("door" in objTypes):
            continue

        # Place the object
        world.addObject(randX, randY, Layer.OBJECTS, flag)
        flagPlaced = True
        scoringInfo["flagLocation"] = {"x": randX, "y": randY}
        scoringInfo["criticalHypotheses"].append("The flag is located at ({}, {}).".format(randX, randY))



    # Add some number of user agents
    for userAgentIdx in range(0, numUserAgents):
        userAgent = Agent(world)
        # Add the agent to a specfic location
        world.addObject(startX+(width//2)+userAgentIdx, startY+height, Layer.AGENT, userAgent)
        #world.addObject(startX + 10, startY+5, Layer.AGENT, userAgent)      # DEBUG
        # Register the agent with the World so we can keep track of it
        world.addAgent(userAgent)




    # Small decorations
    #mkTallTree(14, 12, world)
    #mkTallTree(13, 17, world)
    #mkTallTree(22, 18, world)
    #mkTallTree(23, 14, world)
    #mkTallTree(18, 7, world)
    #mkTallTree(22, 8, world)
    #mkTallTree(17, 8, world)
    mkTallTree(startX+(width//2)+userAgentIdx-2, startY+height, world)
    mkTallTree(startX+(width//2)+userAgentIdx+2, startY+height, world)

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

    # Add teleport locations to world
    world.addTeleportLocation("initial location", startX+(width//2), startY+height)


    return scoringInfo



#
#   Task Scoring
#

class SmallSkillsSearchTask(Task):

    def __init__(self, world, scoringInfo):
        self.flag = scoringInfo["flag"]

        taskDescription = "Your task is to find the flag (located somewhere in the environment) and pick it up."

        super().__init__("SmallSkillsSearchTask", taskDescription, world, scoringInfo)

        # Scorecard elements (TODO)
        self.scorecardPick = ScorecardElement("Find the Flag", "Have the flag in your inventory.", maxScore=1)
        self.scoreCard.append(self.scorecardPick)

        # Add hypotheses from scoringInfo
        self.criticalHypotheses = scoringInfo["criticalHypotheses"]

        # Update max score based on the scorecard elements.
        self.maxScore = sum(element.maxScore for element in self.scoreCard)

    # Task setup: Add any necessary objects to the world to perform the task.
    def taskSetup(self):
        pass

    def updateTick(self):
        if self.completed:
            return  # Do not update the score if the task is already marked as completed

        # Check to see if the object is in the agent's inventory
        if (not self.scorecardPick.completed):
            # Get the object's parent container
            parentContainer = self.flag.parentContainer
            if (parentContainer != None):
                if (parentContainer.attributes["isAgent"] == True):
                    self.scorecardPick.updateScore(1, True, associatedUUIDs=[self.flag.uuid], associatedNotes=f"Agent has picked up the object (UUID: {self.flag.uuid}).")

        failure = False

        # Update score
        self.score = sum(element.score for element in self.scoreCard)

        # Check whether the task is complete
        # Here, the task is complete if all the objects have been collected and returned to the elder.
        if (failure == True):
            # Failure
            self.completed = True
            self.completedSuccessfully = False
        elif (self.score == self.maxScore):
            # Win
            self.completed = True
            self.completedSuccessfully = True
        else:
            # Still playing
            self.completed = False
            self.completedSuccessfully = False

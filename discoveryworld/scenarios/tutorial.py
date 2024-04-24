

from discoveryworld.Agent import NPC, Agent
from discoveryworld.DialogTree import DialogMaker
from discoveryworld.Layer import Layer
from discoveryworld.Pathfinding import Pathfinder
from discoveryworld.buildings.colony import mkGeneralStore, mkKeyShop, mkSchool
from discoveryworld.buildings.farm import mkMushroomAndFlowerFarm
from discoveryworld.buildings.house import mkBuildingOneRoom, mkTableAndChairs
from discoveryworld.buildings.terrain import mkFenceX, mkFenceY, mkGrassFill, mkPathX, mkPathY, mkSignVillage, mkTownSquare

from termcolor import colored


class NPCElder(NPC):
    def __init__(self, world, name, pot, key):
        # Default sprite name
        super().__init__(world, name, defaultSpriteName="character9_agent_facing_east")

        # Rendering
        self.attributes["faceDirection"] = "east"
        self.spriteCharacterPrefix = "character9_"

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

        self.pot = pot
        self.key = key

    def tick(self):
        # Stop if the object has already had tick() called this update -- this might have happened if the object moved locations in this current update cycle.
        if (self.tickCompleted):
            return

        # Debug
        print(f"NPCElder (id: {self.name}): {self.attributes['states']}")
        super().tick()

        # Interpret any external states
        if self.pot in self.contents:
            self.addState("hasPot")
            # Check if temperature of pot is below 0C
            if self.pot.attributes['temperatureC'] < 0:
                self.addState("potIsCold")
            else:
                self.addState("potIsWarm")

        if "giveBack" in self.attributes['states']:
            self.removeState("giveBack")
            self.removeState("hasPot")
            self.removeState("potIsCold")
            self.actionDrop(self.pot)

        if "giveKey" in self.attributes['states']:
            self.removeState("giveKey")
            self.actionDrop(self.key)
            self.addState("keyGiven")

        print(f"NPCElder (id: {self.name}): {self.attributes}")

def mkTutorialHouse(x, y, world):
    # Create a building (house)
    mkBuildingOneRoom(world, x=x, y=y, width=10, height=7, doorKeyID=42)

    OBJECTS = {
        "B": ("Bed", {}, Layer.FURNITURE),
        "N": ("TableBedside", {}, Layer.FURNITURE),
        "D": ("Table", {}, Layer.FURNITURE),
        "-": ("Wall", {}, Layer.BUILDING),
        "|": ("Wall", {}, Layer.BUILDING),
        "v": ("Door", {}, Layer.FURNITURE),
        "F": ("Fridge", {}, Layer.FURNITURE),
        "T": ("Table", {}, Layer.FURNITURE),
        "S": ("Stove", {}, Layer.FURNITURE),
        "s": ("Sink", {}, Layer.FURNITURE),
    }
    layout = [
        "##########",
        "#FTSs|NBN#",
        "#....|...#",
        "#-v----v-#",
        "#........#",
        "#.t......#",
        "##########",
    ]
    fridge = None
    for i, row in enumerate(layout):
        for j, o in enumerate(row):
            if o in OBJECTS.keys():
                cls, kwargs, layer = OBJECTS[o]
                obj = world.createObject(cls, **kwargs)
                world.addObject(x+j, y+i, layer, obj)

                if o == "F":
                    fridge = obj

            elif o == "t":
                mkTableAndChairs(world, x+j, y+i, chairsPresent=["e", "w", "", ""])

    # Make a pot and put mushroms in it
    pot = world.createObject("Pot")
    pot.addObject(world.createObject("Mushroom"))
    pot.addObject(world.createObject("Mushroom"))

    # # Set temperature of pot and its contents to 4C.
    # pot.attributes['temperatureC'] = 4
    # for obj in pot.contents:
    #     obj.attributes['temperatureC'] = 4

    # Add pot to fridge
    fridge.addObject(pot)
    return pot


def makeScenarioTutorial(world, numUserAgents=1, difficulty="easy"):

    # TODO:
    # [X] Drop the initial temperature of the meal
    # [X] Using the Stove should increase the temperature of objects in it.
    # [ ] Bringing back the meal to the elder should teach the "put X in Y" aka give.
    # [ ] Should talk to the elder once the meal has been given to him.
    # [ ] Elder should give a key to the user after that.
    # [ ] Unlock the door "use key on door".
    # [ ] Detect the player has left the house and end the scenario.

    scoringInfo = {}
    scoringInfo["criticalHypotheses"] = []

    # Make the Rosetta Stone scenario
    rng = world.rng

    # Set a limit for the number of user agents
    MAX_NUM_AGENTS = 1
    if (numUserAgents > MAX_NUM_AGENTS):
        raise ValueError("Tutorial scenario supports only a single agent at the moment.")

    # Populate with structures/objects
    # Fill with grass
    mkGrassFill(world)

    mkMushroomAndFlowerFarm(20, 3, world)

    # Buildings
    mkKeyShop(9, 21, world)
    pot = mkTutorialHouse(18, 20, world)
    mkGeneralStore(7, 4, world)
    mkSchool(19, 7, world)


    mkTownSquare(16, 18, world)

    # Paths
    mkPathY(17, 1, 30, world)       # Top/bottom, through town square
    mkPathX(12, 28, 12, world)      # Bottom, along key and paint shops.
    mkPathX(17, 19, 15, world)      # To the east
    mkPathX(1, 19, 16, world)       # To the west
    mkPathY(11, 18, 1, world)       # To general store.
    mkPathY(23, 18, 1, world)       # To school.
    mkPathY(23, 27, 1, world)       # To paint shop.
    mkPathY(12, 27, 1, world)       # To key shop.

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
    userAgent = Agent(world)
    # Add the agent to a specfic location
    #world.addObject(25, 22, Layer.AGENT, userAgent)      # In the bedroom
    world.addObject(20, 24, Layer.AGENT, userAgent)      # Next to the elder.

    # Register the agent with the World so we can keep track of it
    world.addAgent(userAgent)

    # Add teleport locations to world
    world.addTeleportLocation("key shop", 12, 24)
    world.addTeleportLocation("paint shop", 22, 24)
    world.addTeleportLocation("town square", 16, 18)
    world.addTeleportLocation("general store", 11, 10)
    world.addTeleportLocation("school", 23, 10)

    # Create key to front door and give it to elder.
    key = world.createObject("Key", isRusted=False)
    key.setKeyID(42)

    elder = NPCElder(world, "Elder", pot=pot, key=key)
    world.addObject(19, 24, Layer.AGENT, elder)
    world.addAgent(elder)
    dialogMaker.mkDialogElderTutorial(elder)
    elder.addObject(key)

    scoringInfo["elder"] = elder

    return scoringInfo
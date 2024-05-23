# reactor_lab.py

import random

import numpy as np
from discoveryworld.Agent import NPC, Agent, NPCDevice
from discoveryworld.DialogTree import DialogMaker, DialogNode, DialogTree
from discoveryworld.Layer import Layer
from discoveryworld.TaskScorer import ScorecardElement, Task
from discoveryworld.buildings.colony import mkRocket

from discoveryworld.buildings.terrain import mkPathX, mkPathY, mkSandFill, mkSignVillage

from discoveryworld.objects.Terrain import LaunchPad, Sand, SandPath


ROCKET_FORMULAS = """
   /\                 -= Rocketry Cheat Sheet =-
  /  \\
 /____\  Formulas:
 |    |    - Escape velocity: v = sqrt(2 * G * M / R)
 | D  |    - Orbital speed: O_v = sqrt(G * M / (R + h))
 | i  |    - Orbital period: O_T = 2 * pi * sqrt((R + h)^3 / (G * M))
 | s  |    - Gravitational acceleration: g = G * M / R^2
 | c  |    - Pendulum period: T = 2 * pi * sqrt(L / g)
 |----|    - Centripetal acceleration: a = v^2 / R
 | o  |    - Centripetal force: F = m * v^2 / R
 | v  |    - Thrust-to-weight ratio: TWR = F / (m * g)
 | e  |    - Specific impulse: Isp = F / (m_dot * g)
 | r  |    - Rocket equation: delta_v = Isp * g * ln(m0 / m1)
 | y  |
 |----|  Constants & variables:
 |  W |    - G: gravitational constant (6.67430e-11 N m^2 / kg^2)
 |  o |    - M: mass of planet (kg)
 |  r |    - R: radius of planet (m)
 |  l |    - h: height above planet (m)
 |  d |    - g: acceleration due to gravity (m/s^2)     _____
 |____|    - v: velocity (m/s)                      ,-:` \;',`'-,
/|    |\   - T: period (s)                        .'-;_,;  ':-;_,'.
 ||  ||    - L: length of pendulum (m)           /;   '/    ,  _`.-\\
 ||  ||    - F: force (N)                       | '`. (`     /` ` \`|
 ||  ||    - a: acceleration (m/s^2)            |:.  `\`-.   \_   / |
/_|__|_\   - m_dot: mass flow rate (kg/s)       |     (   `,  .`\ ;'|
 ||||||    - m0: initial mass of rocket (kg)     \     | .'     `-'/
 /||||\    - m1: final mass of rocket (kg)        `.   ;/        .'
  /||\     - delta_v: change in velocity (m/s)      `'-.______.-'
"""


PLANETS = [
    "Earth",
    "the Moon",
    "Mars",
    "Io",
    "Europa",
    "Mercury",
    "Venus",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
    "Ganymede",
]

# According to https://en.wikipedia.org/wiki/List_of_Solar_System_objects_by_size
PLANET_RADII = {
    "Mercury": 2439.4,
    "Venus": 6052,
    "Earth": 6371,
    "Mars": 3389.5,
    "Jupiter": 69911,
    "Saturn": 58232,
    "Uranus": 25362,
    "Neptune": 24622,
    "Pluto": 1188.3,
    "the Moon": 1737.5,
    "Io": 1821.6,
    "Europa": 1560.8,
    "Ganymede": 2634.1,
}

PLANET_MASSES = {
    "Mercury": 330.11e21,
    "Venus": 4867.4e21,
    "Earth": 5972.4e21,
    "Mars": 641.71e21,
    "Jupiter": 1898187e21,
    "Saturn": 568317e21,
    "Uranus": 86813e21,
    "Neptune": 102413e21,
    "Pluto": 13.03e21,
    "the Moon": 73.46e21,
    "Io": 89.32e21,
    "Europa": 48.00e21,
    "Ganymede": 148.2e21,
}


def mkControlRoom(world, x, y):
    layout = [
        "#######",
        "#p#m  #",
        "# #tTt#",
        "#     #",
        "####ds#",
    ]
    bounds = (x, y, x+len(layout[0]), y+len(layout))

    pendulum = world.createObject("Pendulum")
    launchTerminal = LaunchTerminal(world) #world.createObject("LaunchTerminal")
    for j, row in enumerate(layout):
        for i, char in enumerate(row):
            if char == "#":
                world.addObject(x+i, y+j, Layer.BUILDING, world.createObject("Wall"))
            elif char == ".":
                pass
            else:
                world.addObject(x+i, y+j, Layer.BUILDING, world.createObject("Floor"))

            if char == "d": # Add door and floor
                door = world.createObject("Door")
                world.addObject(x+i, y+j, Layer.FURNITURE, door)
            elif char == "s":  # Add wall and sign
                world.addObject(x+i, y+j, Layer.BUILDING, world.createObject("Wall"))
                sign = world.createObject("Sign", variant=1)
                sign.setText("Control Room")
                world.addObject(x+i, y+j, Layer.FURNITURE, sign)
            elif char == "T":  # Add table and chairs and computer
                table = world.createObject("Table")
                world.addObject(x+i, y+j, Layer.FURNITURE, table)
                table.addObject(launchTerminal)
            elif char == "t":  # Add table and chairs
                world.addObject(x+i, y+j, Layer.FURNITURE, world.createObject("Table"))
            elif char == "m":  # Add monitor
                world.addObject(x+i, y+j, Layer.OBJECTS, world.createObject("LaunchMonitor", part="bl"))
                world.addObject(x+i+1, y+j, Layer.OBJECTS, world.createObject("LaunchMonitor", part="b"))
                world.addObject(x+i+2, y+j, Layer.OBJECTS, world.createObject("LaunchMonitor", part="br"))
                world.addObject(x+i, y+j-1, Layer.OBJECTS, world.createObject("LaunchMonitor", part="tl"))
                world.addObject(x+i+1, y+j-1, Layer.OBJECTS, world.createObject("LaunchMonitor", part="t"))
                world.addObject(x+i+2, y+j-1, Layer.OBJECTS, world.createObject("LaunchMonitor", part="tr"))
            elif char == "p":  # Add pendulum
                world.addObject(x+i, y+j, Layer.OBJECTS, pendulum)

    return pendulum, launchTerminal, bounds


def mkThrustTestingGround(world, x, y):
    layout = [
        "sABC   ",
        "#######T",
    ]

    for j, row in enumerate(layout):
        for i, char in enumerate(row):
            if char in ("A", "B", "C"):
                world.addObject(x+i, y+j-2, Layer.AIR, world.createObject("FuelTank", variant=char, part="t"))
                world.addObject(x+i, y+j-1, Layer.AIR, world.createObject("FuelTank", variant=char, part="c"))
                world.addObject(x+i, y+j, Layer.FURNITURE, world.createObject("FuelTank", variant=char, part="b"))

            elif char == "s":
                sign = world.createObject("Sign")
                sign.setText("Propellant Tanks")
                world.addObject(x+i, y+j, Layer.OBJECTS, sign)

            elif char == "T":
                pass # TODO


def mkLaunchPad(world, x, y, width, height):
    # Check that it has a minimum size.
    if width < 3 or height < 3:
        print(f"Error: Launch pad is too small: {width} x {height}")
        return

    # Top-left corner
    world.addObject(x, y, Layer.BUILDING, world.createObject("LaunchPad", variant="tl"))
    # Top-right corner
    world.addObject(x + width - 1, y, Layer.BUILDING, world.createObject("LaunchPad", variant="tr"))
    # Bottom-left corner
    world.addObject(x, y + height - 1, Layer.BUILDING, world.createObject("LaunchPad", variant="bl"))
    # Bottom-right corner
    world.addObject(x + width - 1, y + height - 1, Layer.BUILDING, world.createObject("LaunchPad", variant="br"))
    # Top border
    for i in range(1, width - 1):
        world.addObject(x + i, y, Layer.BUILDING, world.createObject("LaunchPad", variant="tc"))

    # Bottom wall
    for i in range(1, width - 1):
        world.addObject(x + i, y + height - 1, Layer.BUILDING, world.createObject("LaunchPad", variant="bc"))

    # Left wall
    for i in range(1, height - 1):
        world.addObject(x, y + i, Layer.BUILDING, world.createObject("LaunchPad", variant="lc"))

    # Right wall
    for i in range(1, height - 1):
        world.addObject(x + width - 1, y + i, Layer.BUILDING, world.createObject("LaunchPad", variant="rc"))

    # Floor
    for i in range(1, width - 1):
        for j in range(1, height - 1):
            world.addObject(x + i, y + j, Layer.BUILDING, world.createObject("LaunchPad", variant="cc"))

    bounds = (x+1, y+1, x + width - 2, y + height - 2)
    return bounds



def makeScenarioNotRocketScience(world, numUserAgents=1, difficulty="easy"):
    scoringInfo = {}
    scoringInfo["criticalHypotheses"] = []

    scoringInfo["difficulty"] = difficulty

    planet = "X"
    if difficulty == "easy":
        planet = PLANETS[world.randomSeed % len(PLANETS)]
        scoringInfo["criticalHypotheses"].append(f"The planet's caracteristics are very similar to {planet}.")

    scoringInfo["planet"] = planet

    # Critical values for the scenario.
    # Planet radius
    planetRadius = world.rng.randint(400, 10000)  # (km)
    if difficulty == "easy":
        planetRadius = PLANET_RADII[planet]  # (km)

    worldHeight = (world.sizeY-1) / 1000  # (km)
    diffAngle = (360 * worldHeight) / (2*planetRadius*np.pi)  # (degrees)
    startAngle = world.rng.randint(2, 5) + (world.rng.random() - 0.5) * diffAngle * 15  # (degrees)
    print(f"DiffAngle: {diffAngle} {startAngle}")

    scoringInfo["planetRadius"] = planetRadius
    scoringInfo["criticalHypotheses"].append(f"Planet radius is {planetRadius} km.")

    # Planet mass
    GRAVITATIONAL_CONSTANT = 6.67430e-11  # (N m^2 / kg^2)
    MIN_PLANET_MASS = 1e23  # kg
    MAX_PLANET_MASS = 1e25  # kg
    planetMass = MIN_PLANET_MASS + world.rng.random() * (MAX_PLANET_MASS - MIN_PLANET_MASS)  # (kg)
    if difficulty == "easy":
        planetMass = PLANET_MASSES[planet]  # (kg)

    scoringInfo["planetMass"] = planetMass
    scoringInfo["criticalHypotheses"].append(f"Planet mass is {planetMass} kg.")

    # Planet gravity
    planetGravity = GRAVITATIONAL_CONSTANT * planetMass / (planetRadius * 1000) ** 2  # (m/s^2)
    scoringInfo["planetGravity"] = planetGravity
    scoringInfo["criticalHypotheses"].append(f"Planet gravity is {planetGravity} m/s^2.")

    # 1-meter pendulum period
    pendulumLength = 1  # (m)
    scoringInfo["pendulumLength"] = pendulumLength
    scoringInfo["criticalHypotheses"].append(f"The pendulum's length is {pendulumLength}m.")
    pendulumPeriod = 2 * np.pi * np.sqrt(pendulumLength / planetGravity)  # (s)
    scoringInfo["pendulumPeriod"] = pendulumPeriod
    scoringInfo["criticalHypotheses"].append(f"The pendulum's period is {pendulumPeriod} ticks.")

    # Target orbit height
    orbitHeight = world.rng.randint(100, 10000)  # (km)
    if difficulty == "easy":
        orbitHeight = 400  # e.g. ISS (km)

    scoringInfo["orbitHeight"] = orbitHeight
    scoringInfo["criticalHypotheses"].append(f"Target orbit height is {scoringInfo['orbitHeight']} km.")

    # Target orbital speed
    orbitSpeed = np.sqrt(GRAVITATIONAL_CONSTANT * planetMass / ((planetRadius + scoringInfo["orbitHeight"])*1000))  # m/s
    scoringInfo["orbitSpeed"] = orbitSpeed
    scoringInfo["criticalHypotheses"].append(f"Target orbit speed is {scoringInfo['orbitSpeed']} m/s.")

    # Set a limit for the number of user agents
    MAX_NUM_AGENTS = 3
    if (numUserAgents > MAX_NUM_AGENTS):
        numUserAgents = MAX_NUM_AGENTS

    # Populate with structures/objects

    # Fill with sand
    mkSandFill(world)

    # Buildings
    # Launchpad
    mkLaunchPad(world, 13, 0, 7, 5)
    mkRocket(world, 16, 2)

    # Rocket Control Operations
    pendulum, launchTerminal, controlRoomBounds = mkControlRoom(world, 7, 20)
    pendulum.setLength(scoringInfo["pendulumLength"])
    pendulum.oscillationPeriod = scoringInfo["pendulumPeriod"]
    launchTerminal.attributes["orbitHeight"] = scoringInfo["orbitHeight"]
    launchTerminal.attributes["targetOrbitSpeed"] = scoringInfo["orbitSpeed"]
    scoringInfo["launchTerminal"] = launchTerminal

    # Load cell test ground
    mkThrustTestingGround(world, 22, 24)

    # Paths
    mkPathX(9, 25, 6, world, type="SandPath")
    mkPathX(18, 25, 13, world, type="SandPath")
    mkPathY(15, 4, 28, world, type="SandPath")
    mkPathY(16, 4, 28, world, type="SandPath")
    mkPathY(17, 4, 28, world, type="SandPath")

    # Add big village sign
    mkSignVillage(15, 27, world)

    # Add some plants
    plantCount = 0
    minPlants = 7
    while (plantCount < minPlants):
        # Pick a random location
        randX = world.rng.randint(0, world.sizeX - 1)
        randY = world.rng.randint(0, world.sizeY - 1)

        # Check to see if there are any objects other than grass there
        objs = world.getObjectsAt(randX, randY)
        # Get types of objects
        objTypes = set(obj.type for obj in objs)

        # Check to see that there is only sand here
        if objTypes == {"sand"}:
            world.addObject(randX, randY, Layer.OBJECTS, world.createObject("Cactus", part="bottom"))
            world.addObject(randX, randY-1, Layer.AIR, world.createObject("Cactus", part="top"))

            plantCount += 1

    plantCount = 0
    minPlants = 7
    while (plantCount < minPlants):
        # Pick a random location
        randX = world.rng.randint(1, world.sizeX - 2)
        randY = world.rng.randint(1, world.sizeY - 2)

        # Check to see if there are any objects other than grass there
        objs = world.getObjectsAt(randX, randY) + world.getObjectsAt(randX+1, randY)

        # Get types of objects
        objTypes = set(obj.type for obj in objs)

        # Check to see that there is only sand here
        if objTypes == {"sand"}:
            world.addObject(randX, randY, Layer.OBJECTS, world.createObject("BigCactus", side="left", part="bottom"))
            world.addObject(randX, randY-1, Layer.AIR, world.createObject("BigCactus", side="left", part="top"))
            world.addObject(randX+1, randY, Layer.OBJECTS, world.createObject("BigCactus", side="right", part="bottom"))
            world.addObject(randX+1, randY-1, Layer.AIR, world.createObject("BigCactus", side="right", part="top"))

            plantCount += 1

    # Assign light angle to each Sand tile. # TODO: also to path and launchpad
    for y in range(world.sizeY):
        lightAngle = np.round((startAngle + diffAngle * (y / (world.sizeY-1))) * 1e3, 5)  # (millidegrees)
        # print(f"Light angle at row {y} is {lightAngle} degrees.")

        for x in range(world.sizeX):
            if x >= controlRoomBounds[0] and x <= controlRoomBounds[2] and y >= controlRoomBounds[1] and y <= controlRoomBounds[3]:
                continue

            for obj in world.getObjectsAt(x, y):
                # Check if the object is Sand.
                if isinstance(obj, (Sand, SandPath, LaunchPad)):
                    obj.attributes["lightAngle"] = lightAngle

    # Add dialog to objects.
    mkDialogLaunchTerminal(launchTerminal)

    # Add some number of user agents
    for userAgentIdx in range(0, numUserAgents):
        userAgent = Agent(world)
        # TODO: Add starting tools for agent
        # Create tools
        speed_square = world.createObject("SpeedSquare")
        userAgent.addObject(speed_square)

        rocketry_book = world.createObject("RocketryBook")
        rocketry_book.attributes["document"] = ROCKET_FORMULAS
        userAgent.addObject(rocketry_book)

        #userAgent.addObject(world.createObject("RocketryBook"))
        # Add the agent to a specfic location
        # world.addObject(16+userAgentIdx, 3, Layer.AGENT, userAgent)    # Near rocket
        world.addObject(11+userAgentIdx, 23, Layer.AGENT, userAgent)   # In control room
        # Register the agent with the World so we can keep track of it
        world.addAgent(userAgent)

    # Add teleport locations to world
    # TODO
    world.addTeleportLocation("control room", 11, 23)
    world.addTeleportLocation("rocket", 16, 3)
    world.addTeleportLocation("northern observation post", 6, 1)  # TODO: make sure there's not cactus here
    world.addTeleportLocation("southern observation post", 6, 31)  # TODO: make sure there's not cactus here

    # Add signs at observation locations
    signNorth = world.createObject("Sign")
    signNorth.setText("This sign is exactly 30 meters north of the southern sign.")
    world.addObject(5, 1, Layer.OBJECTS, signNorth)
    signSouth = world.createObject("Sign")
    signSouth.setText("This sign is exactly 30 meters south of the northern sign.")
    world.addObject(5, 31, Layer.OBJECTS, signSouth)


    # Compute expected approximations for the scenario made the players.
    worldHeight = ((world.sizeY-1) - 0) #/ 1000  # (km)
    sandTileAt00 = [obj for obj in world.getObjectsAt(0, 0) if obj.type == "sand"][0]
    sandTileAt0N = [obj for obj in world.getObjectsAt(0, world.sizeY-1) if obj.type == "sand"][0]
    approxDiffLightAngle = abs(sandTileAt0N.attributes["lightAngle"] - sandTileAt00.attributes["lightAngle"])  # (millidegrees)
    approxDiffLightAngle = approxDiffLightAngle / 1e3  # (degrees)

    approxPlanetRadius = (360*worldHeight) / (approxDiffLightAngle * 2 * np.pi)  # (m)
    approxPlanetRadius = approxPlanetRadius / 1e3  # (km)

    #print(sandTileAt00.attributes["lightAngle"] , sandTileAt0N.attributes["lightAngle"] )
    #print(f"{diffAngle} vs. {approxDiffLightAngle}")
    print(f"Approximation error for DiffAngle: {abs(approxDiffLightAngle - diffAngle)}")

    print(f"{planetRadius} vs. {approxPlanetRadius}")
    print(f"Approximation error for PlanetRadius: {abs(approxPlanetRadius - planetRadius)}")

    # 1-meter pendulum period
    nbTicks = 50
    # nbOscillations = ticks // pendulumPeriod
    nbOscillations = np.round(nbTicks / pendulumPeriod, 3)  # TODO: needs to match the code in the Pendulum object

    # approximage the period of a 1-meter pendulum
    approxPendulumPeriod = nbTicks / nbOscillations

    # approximate g from the period of a 1-meter pendulum
    g = 4 * np.pi ** 2 * pendulumLength / pendulumPeriod ** 2
    approxG = 4 * np.pi ** 2 * pendulumLength / approxPendulumPeriod ** 2

    print(f"Approximation error for PendulumPeriod: {abs(approxPendulumPeriod - pendulumPeriod)}")
    print(f"Approximation error for g with pendulum: {abs(approxG - g)}")
    print(f"Approximation error for g: {abs(approxG - planetGravity)}")

    approxOrbitSpeed = np.sqrt((approxG * (approxPlanetRadius*1e3)**2) / ((approxPlanetRadius + orbitHeight)*1e3))  # m/s
    print(f"Approximation error for OrbitSpeed: {abs(approxOrbitSpeed - orbitSpeed)}")
    print(f"{orbitSpeed} vs. {approxOrbitSpeed}")

    assert abs(approxOrbitSpeed - orbitSpeed) < 1, f"Approximation error for OrbitSpeed: {abs(approxOrbitSpeed - orbitSpeed)}"
    assert orbitSpeed >= 0, f"OrbitSpeed is {orbitSpeed}"
    assert orbitSpeed <= 25000, f"OrbitSpeed is {orbitSpeed}"

    # Return scoring info
    return scoringInfo


class NotRocketScienceTask(Task):

    def __init__(self, world, scoringInfo):
        orbitHeight = scoringInfo["orbitHeight"]
        taskDescription = "You are at the new Launch Site on Planet X. "
        taskDescription += f"To better monitor the weather patterns, you were tasked to send a new probe on orbit at {orbitHeight} kilometers from the ground. "
        taskDescription += "You were told to simply punch in the target orbital speed needed for such an altitude in the launch terminal and the system will take care of the rest. "
        taskDescription += "There is only one rocket, and this is a very important mission, so we better get it right the first time! "

        if scoringInfo["difficulty"] == "challenge":
            taskDescription += "Upon arriving at the launch site, you realized the rocket hasn't been fueled yet. "
            taskDescription += "You will need to figure what type of propellant to use and how much to put in the rocket. "

        if scoringInfo["difficulty"] == "easy":
            taskDescription += f"Thankfully, you know the planet's characteristics, such as its mass and radius, are exactly the same as {scoringInfo['planet']}. "

        taskDescription += "Good thing, you brought with you your faithful rocketry book!\n"
        taskDescription += "Some helpful notes: \n"
        taskDescription += "  1. The grid cells on Planet X are 1-meter square.\n"
        taskDescription += "  2. You can assume air resistance is neglible.\n"
        taskDescription += "  3. Pay attention to the units in the formulas.\n"
        taskDescription += "  4. The formulas are simplifications and may not be 100% accurate.\n"
        taskDescription += "  5. Keep as much decimal places in your calculations.\n"
        if (scoringInfo["difficulty"] != "easy"):
            taskDescription += "  6. There are two observation posts to the north and south, that you may find useful.\n"

        #taskDescription += "\nWhile you brought your faithful rocketry book, it was designed for Earth. "
        #taskDescription += "You might need to adjust some values for Planet X."

        super().__init__("NotRocketScienceTask", taskDescription, world, scoringInfo)
        self.score = 0
        self.maxScore = 3

        # Scorecard elements
        self.scorecardVisitControlRoom = ScorecardElement("Visit control room", "The agent has visited the control room.", maxScore=1)
        self.scoreCard.append(self.scorecardVisitControlRoom)

        self.scorecardMeasureLightAngle = ScorecardElement("Measure light angle", "The agent has measured light angle at two locations.", maxScore=2)
        self.scoreCard.append(self.scorecardMeasureLightAngle)

        self.scorecardActivatePendulum = ScorecardElement("Activate pendulum", "Pendulum was activated.", maxScore=1)
        self.scoreCard.append(self.scorecardActivatePendulum)

        self.scorecardReadoutPendulum = ScorecardElement("Observe pendulum", "The agent has read the pendulum.", maxScore=1)
        self.scoreCard.append(self.scorecardReadoutPendulum)

        self.scorecardUseLaunchTerminal = ScorecardElement("Use launch terminal", "The agent has seen the launch terminal interface.", maxScore=1)
        self.scoreCard.append(self.scorecardUseLaunchTerminal)

        self.scorecardEnterOrbitVelocity = ScorecardElement("Enter correct orbit velocity", "The agent has entered the correct target orbital velocity.", maxScore=1)
        self.scoreCard.append(self.scorecardEnterOrbitVelocity)

        # Add hypotheses from scoringInfo
        self.criticalHypotheses = scoringInfo["criticalHypotheses"]

        # Update max score based on the scorecard elements.
        self.maxScore = sum(element.maxScore for element in self.scoreCard)

    # Update the task progress
    def updateTick(self):
        if self.completed:
            return  # Do not update the score if the task is already marked as completed

        launchTerminal = self.scoringInfo["launchTerminal"]
        if not self.scorecardEnterOrbitVelocity.completed and "launchConfirmed" in launchTerminal.attributes["states"]:
            wiggleRoom = 2    # Allow 2 m/s of wiggle room in getting the value correct
            associatedNotes = []
            associatedUUIDs = []
            if abs(launchTerminal.attributes['orbitSpeed'] - launchTerminal.attributes['targetOrbitSpeed']) < wiggleRoom:
                associatedUUIDs.append((launchTerminal.uuid,))
                associatedNotes.append(f"{launchTerminal.name} (UUID: {launchTerminal.uuid}) has correct orbital velocity {launchTerminal.attributes['orbitSpeed']}.")
                self.scorecardEnterOrbitVelocity.updateScore(1, True, associatedUUIDs, associatedNotes)
            else:
                associatedUUIDs.append((launchTerminal.uuid,))
                associatedNotes.append(f"{launchTerminal.name} (UUID: {launchTerminal.uuid}) has incorrect orbital velocity {launchTerminal.attributes['orbitSpeed']}.")
                self.scorecardEnterOrbitVelocity.updateScore(0, True, associatedUUIDs, associatedNotes)

        # Update score
        self.score = sum(element.score for element in self.scoreCard)

        # Check whether the task is complete
        # Here, the task is complete if the right target orbital velocity has been entered in the launch terminal.
        self.completed = False
        self.completedSuccessfully = False
        if self.scorecardEnterOrbitVelocity.completed:
            self.completed = True
            self.completedSuccessfully = (self.scorecardEnterOrbitVelocity.score == 1)


class LaunchTerminal(NPCDevice):
    def __init__(self, world):
        Agent.__init__(self, world, "computer", "computer", defaultSpriteName="instruments_spectrometer")

        self.spriteCharacterPrefix = ""         # Disable the character prefix for this object (just use the default sprite)

        self.attributes["orbitSpeed"] = 0
        self.attributes["manualMaterialNames"] = ["Metal"]

    def checkOrbitSpeed(self):
        # Make sure the orbital speed is within bounds
        if (self.attributes['orbitSpeed'] < 0):
            self.attributes['orbitSpeed'] = 0
        elif (self.attributes['orbitSpeed'] > 25000):
            self.attributes['orbitSpeed'] = 25000

    def confirmLaunch(self):
        self.addState("launchConfirmed")

    def tick(self):
        self.checkOrbitSpeed()
        super().tick()

    def inferSpriteName(self, force:bool=False):
        # This will be the next last sprite name (when we flip the backbuffer)
        self.curSpriteName = "instruments_spectrometer"
        self.tempLastSpriteName = self.curSpriteName


def mkDialogLaunchTerminal(launchTerminal):
    tree = DialogTree(launchTerminal)

    rootNode = DialogNode("rootNode", "-= Launch Terminal - Main menu =-\n\nOrbital velocity currently set to {orbitSpeed} m/s.", statesToAdd = [], statesToRemove = [])
    rootNode.addDialogOption("Change target orbital velocity.", "setOrbitVelocityNode")
    rootNode.addDialogOption("Start countdown!", "startCountdownNode")
    rootNode.addDialogOption("Exit", "endNode")
    tree.addNode(rootNode)
    tree.setRoot(rootNode.name)

    startCountdownNode = DialogNode("startCountdownNode", "-= Launch Terminal - Start Rocket Launch Countdown? =-\n\nOrbital velocity currently set to {orbitSpeed} m/s.\n(Once you confirmed, there's no coming back.)")
    startCountdownNode.addDialogOption("Confirm", "endNode", callback=launchTerminal.confirmLaunch)
    startCountdownNode.addDialogOption("Cancel", "rootNode")
    tree.addNode(startCountdownNode)

    setOrbitVelocityNode = DialogNode("setOrbitVelocityNode", "-= Launch Terminal - Setting Orbital Velocity =-\n\nOrbital velocity currently set to {orbitSpeed} m/s.\n(Must be between 0 and 10,000 m/s).", statesToAdd = [], statesToRemove = [])

    # Increase target velocity
    setOrbitVelocityNode.addDialogOption("Increase target velocity by 1000 m/s", "setOrbitVelocityNode", floatVariablesToModify={"orbitSpeed": 1000}, minMaxRange={"orbitSpeed": {"min": 0, "max": 25000}}, callback=launchTerminal.checkOrbitSpeed)
    setOrbitVelocityNode.addDialogOption("Increase target velocity by 100 m/s", "setOrbitVelocityNode", floatVariablesToModify={"orbitSpeed": 100}, minMaxRange={"orbitSpeed": {"min": 0, "max": 25000}}, callback=launchTerminal.checkOrbitSpeed)
    setOrbitVelocityNode.addDialogOption("Increase target velocity by 10 m/s", "setOrbitVelocityNode", floatVariablesToModify={"orbitSpeed": 10}, minMaxRange={"orbitSpeed": {"min": 0, "max": 25000}}, callback=launchTerminal.checkOrbitSpeed)
    setOrbitVelocityNode.addDialogOption("Increase target velocity by 1 m/s", "setOrbitVelocityNode", floatVariablesToModify={"orbitSpeed": 1}, minMaxRange={"orbitSpeed": {"min": 0, "max": 25000}}, callback=launchTerminal.checkOrbitSpeed)
    # Decrease target velocity
    setOrbitVelocityNode.addDialogOption("Decrease target velocity by 1000 m/s", "setOrbitVelocityNode", floatVariablesToModify={"orbitSpeed": -1000}, minMaxRange={"orbitSpeed": {"min": 0, "max": 25000}}, callback=launchTerminal.checkOrbitSpeed)
    setOrbitVelocityNode.addDialogOption("Decrease target velocity by 100 m/s", "setOrbitVelocityNode", floatVariablesToModify={"orbitSpeed": -100}, minMaxRange={"orbitSpeed": {"min": 0, "max": 25000}}, callback=launchTerminal.checkOrbitSpeed)
    setOrbitVelocityNode.addDialogOption("Decrease target velocity by 10 m/s", "setOrbitVelocityNode", floatVariablesToModify={"orbitSpeed": -10}, minMaxRange={"orbitSpeed": {"min": 0, "max": 25000}}, callback=launchTerminal.checkOrbitSpeed)
    setOrbitVelocityNode.addDialogOption("Decrease target velocity by 1 m/s", "setOrbitVelocityNode", floatVariablesToModify={"orbitSpeed": -1}, minMaxRange={"orbitSpeed": {"min": 0, "max": 25000}}, callback=launchTerminal.checkOrbitSpeed)

    setOrbitVelocityNode.addDialogOption("[Back]", "rootNode")
    tree.addNode(setOrbitVelocityNode)

    # OK node
    endNodeOK = DialogNode("endNode", "Exiting launch terminal.", statesToAdd = [], statesToRemove = [])
    tree.addNode(endNodeOK)

    # Store dialog tree in agent
    launchTerminal.setDialogTree(tree)
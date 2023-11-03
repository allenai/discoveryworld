
import pygame
import os
import json
import random
import time
import subprocess

# Sprite library
import SpriteLibrary
from ObjectMaker import ObjectMaker
from World import World
from Layer import Layer
from BuildingMaker import BuildingMaker
from ObjectModel import *
from Agent import *
from ActionSuccess import *



def mkHouse(x, y, world, buildingMaker):
    # Create a building (house)
    buildingMaker.mkBuildingOneRoom(world, x=x+0, y=x+0, width=7, height=7)
    #buildingMaker.mkTableAndChairs(world, x=6, y=9, chairsPresent=["n", "s", "e", "w"])
    buildingMaker.mkTableAndChairs(world, x=x+1, y=y+4, chairsPresent=["n", "s", "", ""])

    world.addObject(x+1, y+1, Layer.FURNITURE, world.createObject("Fridge"))    
    world.addObject(x+2, y+1, Layer.FURNITURE, world.createObject("Sink"))
    world.addObject(x+3, y+1, Layer.FURNITURE, world.createObject("Stove"))

    world.addObject(x+5, y+1, Layer.FURNITURE, world.createObject("Bed"))


def mkBarracks(x, y, world, buildingMaker):
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

def mkInfirmary(x, y, world, buildingMaker):
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
    
def mkCafeteria(x, y, world, buildingMaker):
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
        world.addObject(x+i+2, y+3, Layer.FURNITURE, tableToAdd)
        tables.append(tableToAdd)

    #world.addObject(x+2, y+5, Layer.FURNITURE, Table(world))

    # Back (kitchen)
    pot = Pot(world)
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


def mkScienceLab(x, y, world, buildingMaker):
    # Create a building (science lab)
    #buildingMaker.mkBuildingOneRoom(world, x=x, y=y, width=5, height=5)
    buildingMaker.mkBuildingDivided(world, x=x, y=y, width=8, height=6, dividerX=5, apertureX=3, dividerY=0, apertureY=0, doorX=3, signText="Science Lab")
    bench1 = world.createObject("Table")
    world.addObject(x+1, y+1, Layer.FURNITURE, bench1)
    bench1.addObject( world.createObject("Microscope") )


# Check if a tile already contains a "path"
def _hasObj(x, y, world, objType):
    objects = world.getObjectsAt(x, y)
    # Then, check to see if any of them are walls
    for object in objects:
        if (object.type == objType):
            return True
    return False


def mkTownSquare(x, y, world, buildingMaker):
    # Add statue
    world.addObject(x+1, y+1, Layer.OBJECTS, world.createObject("Statue"))
    
    # Create a square that's made out of "Path" tiles
    for i in range(0, 3):
        for j in range(0, 3):
            if (not _hasObj(x+i, y+j, world, "path")):                
                world.addObject(x+i, y+j, Layer.WORLD, world.createObject("Path"))


def mkFarm(x, y, world, buildingMaker):
    # Create a small building
    houseSizeX = 4
    houseSizeY = 4
    buildingMaker.mkBuildingOneRoom(world, x=x+1, y=y, width=houseSizeX, height=houseSizeY, signText="Farm")

    # Add a table in the farm house
    seedTable = world.createObject("Table")
    seedJar = world.createObject("Jar")
    #seedJar.addObject(Seed(world, "red"))

    # Add 5 seeds to the jar
    for i in range(5):
        seedJar.addObject( world.createObject("Seed") )

    seedTable.addObject(seedJar)
    world.addObject(x+3, y+1, Layer.FURNITURE, seedTable)

    # Add a shovel in the farm house
    shovel = world.createObject("Shovel")
    world.addObject(x+2, y+1, Layer.FURNITURE, shovel)

    # Add a seed just outside the farm house
    world.addObject(x+1, y+houseSizeY+2, Layer.OBJECTS, world.createObject("Seed"))

    # Create a soil plot
    soilPlotSizeX = 6
    soilPlotSizeY = 5
    for i in range(0, soilPlotSizeX):
        for j in range(0, soilPlotSizeY):
            if (not _hasObj(x+i, y+j + houseSizeX + 1, world, "soil")):
                world.addObject(x+i, y+j + houseSizeX + 1, Layer.WORLD, world.createObject("SoilTile"))

    # Add a hole in one soil plot at the top left
    world.addObject(x+1, y+houseSizeY+1, Layer.OBJECTS, world.createObject("Hole"))
    # Add dirt beside the hole
    world.addObject(x, y+houseSizeY+1, Layer.OBJECTS, world.createObject("Dirt"))


    # Randomly add a number of Mushrooms to the soil
    numMushroomsToAdd = 5
    numMushroomsAdded = 0
    attempts = 0
    mushroomsAdded = []
    while (numMushroomsAdded < numMushroomsToAdd):    
        # Pick a random location
        randX = random.randint(x, x+soilPlotSizeX-1)
        randY = random.randint(y+houseSizeY+1, y+houseSizeY+soilPlotSizeY-1)

        # If there isn't already a mushroom there, add one
        if (not _hasObj(randX, randY, world, "mushroom")):
            # Add a mushroom 
            mushroomTypes = ["mushroom1", "mushroom2", "mushroom3", "mushroom4"]
            # Randomly pick a mushroom type
            mushroomType = mushroomTypes[random.randint(0, len(mushroomTypes)-1)]
            mushroom = world.createObject(mushroomType)
            #mushroom = world.createObject("Mushroom")

            world.addObject(randX, randY, Layer.OBJECTS, mushroom)
            mushroomsAdded.append(mushroom)
            numMushroomsAdded += 1

        attempts += 1
        if (attempts > 100):
            print("ERROR: Couldn't add all mushrooms to farm.  Exiting to prevent infinite loop.")
            break

    ## Debug, gives references to mushrooms added for agents to pick up
    return mushroomsAdded
    



# Path making
def mkPathX(x, y, lengthX, world):
    for i in range(0, lengthX):
        if (not _hasObj(x+i, y, world, "path")):
            world.addObject(x+i, y, Layer.WORLD, world.createObject("Path"))

def mkPathY(x, y, lengthY, world):
    for i in range(0, lengthY):
        if (not _hasObj(x, y+i, world, "path")):
            world.addObject(x, y+i, Layer.WORLD, world.createObject("Path"))

# Fence making
def mkFenceX(x, y, lengthX, world):
    for i in range(0, lengthX):
        if (not _hasObj(x+i, y, world, "fence")):
            world.addObject(x+i, y, Layer.BUILDING, world.createObject("Fence"))

def mkFenceY(x, y, lengthY, world):
    for i in range(0, lengthY):
        if (not _hasObj(x, y+i, world, "fence")):
            world.addObject(x, y+i, Layer.BUILDING, world.createObject("Fence"))




def main():
    print("Initializing...")


    # 32 pixels/tile * 32 tiles = 1024 pixels

    # Game parameters
    gameParams = {
        "height": 1024,
        "width": 1024,
        "fps": 60,
        "name": "DiscoveryWorld"
    }

    # Open window
    #window = pygame.display.set_mode((gameParams["width"], gameParams["height"]))
    # Open window (should open in top left corner)
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50,50)
    window = pygame.display.set_mode((gameParams["width"], gameParams["height"]))
    pygame.display.set_caption(gameParams["name"])
    
    clock = pygame.time.Clock()

    # Initialize font renderer
    pygame.font.init()

    # Intialize world
    world = World(assetPath = "assets", filenameSpriteIndex = "spriteIndex.json", dataPath = "data/", filenameObjectData = "objects.tsv", filenameMaterialData="materials.tsv")
    print ("All sprite names: ")
    print (world.spriteLibrary.getSpriteNames())

    

    # Populate with structures/objects
    buildingMaker = BuildingMaker(world)

    # Fill with grass
    buildingMaker.mkGrassFill(world)
    # Randomly place a few plants (plant1, plant2, plant3)
    for i in range(0, 10):
        randX = random.randint(0, world.sizeX - 1)
        randY = random.randint(0, world.sizeY - 1)
        ## world.addObject(randX, randY, Layer.OBJECTS, BuildingMaker.mkObject("plant", "plant", "forest1_plant" + str(i % 3 + 1)))


    # Buildings
    #mkHouse(4, 4, world, buildingMaker)
    
    mkScienceLab(8, 21, world, buildingMaker)


    mkInfirmary(19, 4, world, buildingMaker)

    mkBarracks(19, 11, world, buildingMaker)
    
    tables, pot = mkCafeteria(19, 20, world, buildingMaker)

    mkTownSquare(16, 18, world, buildingMaker)

    ## TODO: Add Farm?
    mushroomsAdded = mkFarm(10, 8, world, buildingMaker)

    # Paths
    mkPathY(17, 1, 30, world)       # Top/bottom, through town square

    mkPathX(10, 28, 15, world)       # Bottom, along cafeteria/science lab

    mkPathX(17, 19, 15, world)       # Town square to barracks

    mkPathX(17, 10, 10, world)       # Town square to infirmary

    mkPathX(1, 19, 16, world)       # Town square to farm

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
    world.addObject(16, 2, Layer.BUILDING, world.createObject("SignVillage"))
    world.addObject(16, 29, Layer.BUILDING, world.createObject("SignVillage"))

    # Add some plants
    world.addObject(15, 1, Layer.OBJECTS, world.createObject("PlantGeneric"))

    plantCount = 0
    minPlants = 15
    while (plantCount < minPlants):
        # Pick a random location
        randX = random.randint(0, world.sizeX - 1)
        randY = random.randint(0, world.sizeY - 1)

        # Check to see if there are any objects other than grass there
        objs = world.getObjectsAt(randX, randY)
        # Get types of objects
        objTypes = [obj.type for obj in objs]
        # Check to see that there is grass here
        if ("grass" in objTypes):
            # Check that there is not other things here
            if (len(objTypes) == 1):
                # Add a plant
                world.addObject(randX, randY, Layer.OBJECTS, PlantGeneric(world))
                plantCount += 1                


    # Add an agent
    currentAgent = Agent(world)
    world.addObject(10, 10, Layer.AGENT, currentAgent)

    # Add an NPC
    npcColonist = NPCColonist(world, "Example NPC")
    world.addObject(18, 25, Layer.AGENT, npcColonist)

    # Add the NPC Chef
    npcChef = NPCChef1(world, "Chef", tables=tables, pot=pot)
    world.addObject(20, 21, Layer.AGENT, npcChef)

    # Add another NPC colonist
    #npcColonist1 = NPCColonist1(world, "Colonist 1", thingToPickup=None)
    ##npcColonist1 = NPCColonist1(world, "Colonist 1", thingsToPickup=mushroomsAdded, whereToPlace=pot)
    ##world.addObject(18, 20, Layer.AGENT, npcColonist1)

    # Add another NPC colonist
    npcColonists = []
    for i in range(0, 5):
        npcColonists.append(NPCColonistAuto2(world, "Colonist " + str(i)))
        world.addObject(13+i, 20, Layer.AGENT, npcColonists[i])

    # Initial world tick
    world.tick()


    # Create a directory "/video" for storing video frames
    VIDEO_DIR = "video"
    FRAME_DIR = "video/frames"
    if (not os.path.exists(VIDEO_DIR)):
        os.mkdir(VIDEO_DIR)
    if (not os.path.exists(FRAME_DIR)):
        os.mkdir(FRAME_DIR)
    # Empty the frames directory
    for filename in os.listdir(FRAME_DIR):
        os.remove(FRAME_DIR + "/" + filename)
    

    # Main rendering loop
    running = True
    frames = 0
    autoRunCycles = 0
    lastMove = time.time()        # Time of last move (in seconds since start of game)
    while running:        
        #print("Frame: " + str(frames))
        curTime = time.time()

        clock.tick(gameParams["fps"])

        # Check for a quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Check for keyboard input
        keys = pygame.key.get_pressed()

        # Signify whether the agent has done their move this turn
        doNextTurn = False

        # Escape -- quits the game
        if (keys[pygame.K_ESCAPE]):
            running = False    

        # # Arrow keys -- move agent (directly up/down/left/right)
        # elif (keys[pygame.K_UP]):
        #     # Move agent north
        #     success = currentAgent.actionMoveAgent(0, -1)            
        #     lastMove = curTime
        #     print(success)
        #     doNextTurn = True

        # elif (keys[pygame.K_DOWN]):
        #     # Move agent south
        #     success = currentAgent.actionMoveAgent(0, 1)
        #     lastMove = curTime
        #     print(success)
        #     doNextTurn = True

        # elif (keys[pygame.K_LEFT]):
        #     # Move agent west
        #     success = currentAgent.actionMoveAgent(-1, 0)
        #     lastMove = curTime
        #     print(success)
        #     doNextTurn = True

        # elif (keys[pygame.K_RIGHT]):
        #     # Move agent east
        #     success = currentAgent.actionMoveAgent(1, 0)
        #     lastMove = curTime
        #     print(success)
        #     doNextTurn = True

        # Arrow keys -- move agent.  Left/right rotate agent clockwise/counterclockwise, up/down move agent forward/backward
        elif (keys[pygame.K_UP]):
            # Move agent forward
            success = currentAgent.actionMoveAgentForwardBackward(direction=+1)
            print(success)
            doNextTurn = True
        elif (keys[pygame.K_DOWN]):
            # Move agent backwards
            success = currentAgent.actionMoveAgentForwardBackward(direction=-1)
            print(success)
            doNextTurn = True
        elif (keys[pygame.K_LEFT]):
            # Rotate agent counterclockwise
            success = currentAgent.actionRotateAgentFacingDirection(direction=-1)
            print(success)
            doNextTurn = True
        elif (keys[pygame.K_RIGHT]):
            # Rotate agent clockwise
            success = currentAgent.actionRotateAgentFacingDirection(direction=+1)
            print(success)
            doNextTurn = True

        elif (keys[pygame.K_SPACE]):
            # Pick-up object in front of agent
            facingLocation = currentAgent.getWorldLocationAgentIsFacing()
            # Bound checking
            if (world.isWithinBounds(facingLocation[0], facingLocation[1])):
                # Get objects at location
                objs = world.getObjectsAt(facingLocation[0], facingLocation[1])  
                # Expand the list of objects by adding objects that are contained by those objects
                objs1 = [obj for obj in objs for obj in obj.getAllContainedObjectsRecursive(respectContainerStatus=True)]
                # Add this expanded list to the original list of objects at this location
                objs.extend(objs1)

                # Filter by objects that are movable
                movableObjs = [obj for obj in objs if (obj.attributes['isMovable'] == True)]

                # Check to see if there is a movable object here
                if (len(movableObjs) > 0):
                    # Pick up the first movable object
                    objToPickUp = movableObjs[0]
                    success = currentAgent.actionPickUp(objToPickUp)
                    print(success)

            lastMove = curTime
            doNextTurn = True

        elif (keys[pygame.K_d]):
            # Drop an inventory item at the agents current location

            # First, pick an item from the inventory (i.e. the first item)
            if (len(currentAgent.contents) > 0):
                itemToDrop = currentAgent.contents[0]
                success = currentAgent.actionDrop(itemToDrop)
                print(success)

            lastMove = curTime
            doNextTurn = True

        elif (keys[pygame.K_p]):
            # Put an inventory item in a specific container
            
            # First, pick an item from the inventory (i.e. the first item)
            if (len(currentAgent.contents) > 0):
                itemToPut = currentAgent.contents[0]
            
                # Find a container at the location the agent is facing
                facingLocation = currentAgent.getWorldLocationAgentIsFacing()
                # Bound checking
                if (world.isWithinBounds(facingLocation[0], facingLocation[1])):
                    # Get objects at location
                    objs = world.getObjectsAt(facingLocation[0], facingLocation[1])                    
                    # Filter by objects that are containers
                    containerObjs = [obj for obj in objs if (obj.attributes['isContainer'] == True)]

                    # Check to see if there is a container here
                    if (len(containerObjs) > 0):
                        # Put the item in the first container
                        success = currentAgent.actionPut(itemToPut, containerObjs[0])
                        print(success)
                        
            lastMove = curTime
            doNextTurn = True

        elif (keys[pygame.K_o]):
            # Open a container or passage in front of the agent

            # Find a container at the location the agent is facing
            facingLocation = currentAgent.getWorldLocationAgentIsFacing()
            # Bound checking
            if (world.isWithinBounds(facingLocation[0], facingLocation[1])):
                # Get objects at location
                objs = world.getObjectsAt(facingLocation[0], facingLocation[1])                    
                # Filter by objects that are containers OR passages
                openableObjs = [obj for obj in objs if (obj.attributes['isContainer'] == True or obj.attributes['isPassage'] == True)]

                # Check to see if there is an openable object here
                if (len(openableObjs) > 0):
                    # Try to open the first one
                    success = currentAgent.actionOpenClose(openableObjs[0], "open")
                    print(success)

            lastMove = curTime
            doNextTurn = True

        elif (keys[pygame.K_c]):
            # Close a container or passage in front of the agent

            # Find a container at the location the agent is facing
            facingLocation = currentAgent.getWorldLocationAgentIsFacing()
            # Bound checking
            if (world.isWithinBounds(facingLocation[0], facingLocation[1])):
                # Get objects at location
                objs = world.getObjectsAt(facingLocation[0], facingLocation[1])                    
                # Filter by objects that are containers OR passages
                openableObjs = [obj for obj in objs if (obj.attributes['isContainer'] == True or obj.attributes['isPassage'] == True)]

                # Check to see if there is an openable object here
                if (len(openableObjs) > 0):
                    # Try to open the first one
                    success = currentAgent.actionOpenClose(openableObjs[0], "close")
                    print(success)

            doNextTurn = True


        elif (keys[pygame.K_a]):
            # Activate an object in front of the agent

            # Find an activatable object at the location the agent is facing
            facingLocation = currentAgent.getWorldLocationAgentIsFacing()
            # Bound checking
            if (world.isWithinBounds(facingLocation[0], facingLocation[1])):
                # Get objects at location
                objs = world.getObjectsAt(facingLocation[0], facingLocation[1])                    
                # Filter by objects that are activatable
                activatableObjs = [obj for obj in objs if (obj.attributes['isActivatable'] == True)]

                # Check to see if there is an activatable object here
                if (len(activatableObjs) > 0):
                    # Try to activate the first one
                    success = currentAgent.actionActivateDeactivate(activatableObjs[0], "activate")
                    print(success)

            lastMove = curTime
            doNextTurn = True
        
        # For some read K_d doesn't work. 
        # Should be D key here
        elif (keys[pygame.K_s]):            
            # Deactivate an object in front of the agent
            
            # Find an activatable object at the location the agent is facing
            facingLocation = currentAgent.getWorldLocationAgentIsFacing()
            # Bound checking
            if (world.isWithinBounds(facingLocation[0], facingLocation[1])):
                # Get objects at location
                objs = world.getObjectsAt(facingLocation[0], facingLocation[1])                    
                # Filter by objects that are activatable
                activatableObjs = [obj for obj in objs if (obj.attributes['isActivatable'] == True)]

                # Check to see if there is an activatable object here
                if (len(activatableObjs) > 0):
                    # Try to activate the first one
                    success = currentAgent.actionActivateDeactivate(activatableObjs[0], "deactivate")
                    print(success)

            lastMove = curTime
            doNextTurn = True

        # Dialog/talk action
        elif (keys[pygame.K_t]):
            # Talk to an agent in front of the agent

            # Find an agent at the location the agent is facing
            facingLocation = currentAgent.getWorldLocationAgentIsFacing()
            # Bound checking
            if (world.isWithinBounds(facingLocation[0], facingLocation[1])):
                # Get objects at location
                objs = world.getObjectsAt(facingLocation[0], facingLocation[1])                    
                # Filter by objects that are agents (i.e. dialogable)
                agentObjs = [obj for obj in objs if (obj.attributes['isDialogable'] == True)]

                # Check to see if there is an agent here
                if (len(agentObjs) > 0):
                    # Try to talk to the first one
                    agentToTalkTo = agentObjs[0]
                    print("Dialog event:")
                    success = agentToTalkTo.actionDialog(agentDoingTalking = currentAgent, dialogStrToSay = "Hello!")
                    print(success)
                    #time.sleep(1)

                    doNextTurn = True

        # Eat action
        elif (keys[pygame.K_e]):
            # Eat an item in front of the agent

            # Find an edible item at the location the agent is facing
            facingLocation = currentAgent.getWorldLocationAgentIsFacing()
            # Bound checking
            if (world.isWithinBounds(facingLocation[0], facingLocation[1])):
                # Get objects at location
                objs = world.getObjectsAt(facingLocation[0], facingLocation[1])                    
                # Filter by objects that are edible
                edibleObjs = [obj for obj in objs if (obj.attributes['isEdible'] == True)]

                # Check to see if there is an edible object here
                if (len(edibleObjs) > 0):
                    # Try to eat the first one
                    success = currentAgent.actionEat(edibleObjs[0])
                    print(success)

                    doNextTurn = True

        # Use action
        elif (keys[pygame.K_u]):
            # Use one item with another item.

            # Find a usable item at the location the agent is facing
            facingLocation = currentAgent.getWorldLocationAgentIsFacing()
            # Bound checking
            if (world.isWithinBounds(facingLocation[0], facingLocation[1])):
                # Get objects at location
                objs = world.getObjectsAt(facingLocation[0], facingLocation[1])                    
                # Filter by objects that are usable
                usableObjs = [obj for obj in objs if (obj.attributes['isUsable'] == True)]

                # Check to see if there is a usable object here
                if (len(usableObjs) > 0):
                    
                    # The patient object will be the first item in the inventory. 
                    if (len(currentAgent.contents) > 0):
                        patientObj = currentAgent.contents[0]

                        # Try to use the first one
                        success = currentAgent.actionUse(usableObjs[0], patientObj)
                        print(success)
                        
                    else: 
                        print("No items in inventory to use.")
                else:
                    print("No usable objects found in front of the agent.")

                doNextTurn = True


        
        # Manual state adjustment
        elif (keys[pygame.K_1]):
            # Change the colonist NPC external signal
            print("Sending 'eatSignal' to colonist NPC")
            for npcColonist in npcColonists:
                npcColonist.attributes['states'].add("eatSignal")

            doNextTurn = True
        
        elif (keys[pygame.K_2]):
            # Change the Chef NPC external signal
            print("Sending 'collectSignal' to chef NPC")
            npcChef.attributes['states'].add("collectSignal")

            doNextTurn = True

        elif (keys[pygame.K_3]):
            # Change the Chef NPC external signal
            print("Sending 'serveSignal' to chef NPC")
            npcChef.attributes['states'].add("serveSignal")

            doNextTurn = True


        # Manual "wait"
        elif (keys[pygame.K_w]):
            # Wait a turn
            print("Waiting (taking no action this turn)...")
            doNextTurn = True
        
        # Manual "run for 100 cycles"
        elif (keys[pygame.K_0]):
            # Run for 100 cycles
            autoRunCycles = 100
            print("Setting autorun cycles to 100...")
            doNextTurn = True

        # Manual "run for 500 cycles"
        elif (keys[pygame.K_9]):
            # Run for 100 cycles
            autoRunCycles = 500
            print("Setting autorun cycles to 500...")
            doNextTurn = True



        # Fill the window with black
        window.fill((0, 0, 0))

        # Update the world
        # If the agent has taken their turn, then update the world
        exportFrame = False
        if (doNextTurn) or (autoRunCycles > 0):
            world.tick()
            frames += 1
            print("")
            if (autoRunCycles > 0):
                print("Step: " + str(frames) + " (autorun)")
            else:
                print("Step: " + str(frames))
            #time.sleep(0.25)
            time.sleep(0.10)

            if (autoRunCycles > 0):
                autoRunCycles -= 1

            exportFrame = True



        # Render the world
        #world.render(window, cameraX=0, cameraY=0)

        # Render a viewport centered on the agent
        # def renderViewport(self, window, worldStartX, worldStartY, sizeTilesX, sizeTilesY, offsetX, offsetY):
        # Step 1: Get the agent's location
        agentLocation = currentAgent.getWorldLocation()
        # Step 2: Define the viewport size (in tiles)
        viewportSizeX = 32
        viewportSizeY = 32
        # Step 3: Determine the worldStartX and worldStartY coordinates
        worldStartX = agentLocation[0] - int(viewportSizeX / 2)
        worldStartY = agentLocation[1] - int(viewportSizeY / 2)
        # Step 4: Render the viewport
        world.renderViewport(window, worldStartX, worldStartY, viewportSizeX, viewportSizeY, 0, 0)



        # Save the screen frame to a file
        if (exportFrame):
            frameFilename = FRAME_DIR + "/frame_" + str(frames) + ".png"
            pygame.image.save(window, frameFilename)


        # Display the sprite
        #world.spriteLibrary.renderSprite(window, "house1_wall1", 100, 100)

        # Flip the backbuffer
        pygame.display.flip()
        #frames += 1
        
        #time.sleep(1)        

    # If we get here, the game loop is over.
    # Convert the frames to a video
    print("Converting frames to video...")
    # Call FFMPEG (forces overwrite)
    #subprocess.call(["./ffmpeg", "-y", "-framerate", "10", "-i", FRAME_DIR + "/frame_%d.png", "-c:v", "libx264", "-profile:v", "high", "-crf", "20", "-pix_fmt", "yuv420p", "output.mp4"])
    subprocess.call(["ffmpeg", "-y", "-framerate", "10", "-i", FRAME_DIR + "/frame_%d.png", "-c:v", "libx264", "-profile:v", "high", "-crf", "20", "-pix_fmt", "yuv420p", "output.mp4"])


# Main
if __name__ == "__main__":
    # Main function
    main()

    
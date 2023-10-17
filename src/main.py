
import pygame
import os
import json
import random
import time

# Sprite library
import SpriteLibrary
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

    world.addObject(x+1, y+1, Layer.FURNITURE, Fridge(world))    
    world.addObject(x+2, y+1, Layer.FURNITURE, Sink(world))
    world.addObject(x+3, y+1, Layer.FURNITURE, Stove(world))

    world.addObject(x+5, y+1, Layer.FURNITURE, Bed(world))


def mkBarracks(x, y, world, buildingMaker):
    # Create a building (barracks)
    #buildingMaker.mkBuildingOneRoom(world, x=x, y=y, width=5, height=5)
    #buildingMaker.mkBuildingOneRoom(world, x=x, y=y, width=12, height=5)
    buildingMaker.mkBuildingDivided(world, x=x, y=y, width=8, height=7, dividerX=0, apertureX=0, dividerY=3, apertureY=1, doorX=3, signText="Barracks")


    # Add 3 beds and bedside tables (back wall)
    world.addObject(x+2, y+1, Layer.FURNITURE, Bed(world))
    world.addObject(x+3, y+1, Layer.FURNITURE, TableBedside(world))
    world.addObject(x+5, y+1, Layer.FURNITURE, Bed(world))
    world.addObject(x+6, y+1, Layer.FURNITURE, TableBedside(world))
    #world.addObject(x+8, y+1, Layer.FURNITURE, Bed(world))
    #world.addObject(x+9, y+1, Layer.FURNITURE, TableBedside(world))

    # Add 3 beds and bedside tables (middle wall)
    world.addObject(x+2, y+4, Layer.FURNITURE, Bed(world))
    world.addObject(x+3, y+4, Layer.FURNITURE, TableBedside(world))
    world.addObject(x+5, y+4, Layer.FURNITURE, Bed(world))
    world.addObject(x+6, y+4, Layer.FURNITURE, TableBedside(world))
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
    world.addObject(x+1, y+1, Layer.FURNITURE, Bed(world))
    world.addObject(x+3, y+1, Layer.FURNITURE, Bed(world))
    #world.addObject(x+5, y+1, Layer.FURNITURE, Bed(world))
    #world.addObject(x+7, y+1, Layer.FURNITURE, Bed(world))

    # Table
    world.addObject(x+5, y+1, Layer.FURNITURE, Table(world))    
    # Fridge
    world.addObject(x+6, y+1, Layer.FURNITURE, Fridge(world))    
    
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
    world.addObject(x+2, y+3, Layer.FURNITURE, Table(world))
    world.addObject(x+3, y+3, Layer.FURNITURE, Table(world))
    mushroom = Mushroom(world)
    table1 = Table(world)
    table1.addObject(mushroom)
    world.addObject(x+4, y+3, Layer.FURNITURE, table1)
    world.addObject(x+5, y+3, Layer.FURNITURE, Table(world))
    world.addObject(x+6, y+3, Layer.FURNITURE, Table(world))

    #world.addObject(x+2, y+5, Layer.FURNITURE, Table(world))

    # Back (kitchen)
    pot = Pot(world)
    kitchenPrepTable = Table(world)
    kitchenPrepTable.addObject(pot)
    world.addObject(x+3, y+1, Layer.FURNITURE, kitchenPrepTable)
    world.addObject(x+4, y+1, Layer.FURNITURE, Fridge(world))    
    world.addObject(x+5, y+1, Layer.FURNITURE, Sink(world))
    world.addObject(x+6, y+1, Layer.FURNITURE, Stove(world))

    # Front (decorations)
    flowerpot = FlowerPot(world)
    flowerTable = Table(world)
    flowerTable.addObject(flowerpot)
    world.addObject(x+6, y+5, Layer.FURNITURE, flowerTable)




def mkScienceLab(x, y, world, buildingMaker):
    # Create a building (science lab)
    #buildingMaker.mkBuildingOneRoom(world, x=x, y=y, width=5, height=5)
    buildingMaker.mkBuildingDivided(world, x=x, y=y, width=8, height=6, dividerX=5, apertureX=3, dividerY=0, apertureY=0, doorX=3, signText="Science Lab")
    bench1 = Table(world)
    world.addObject(x+1, y+1, Layer.FURNITURE, bench1)
    bench1.addObject( Microscope(world) )


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
    world.addObject(x+1, y+1, Layer.OBJECTS, Statue(world))
    
    # Create a square that's made out of "Path" tiles
    for i in range(0, 3):
        for j in range(0, 3):
            if (not _hasObj(x+i, y+j, world, "path")):                
                world.addObject(x+i, y+j, Layer.WORLD, Path(world))


def mkFarm(x, y, world, buildingMaker):
    # Create a small building
    houseSizeX = 4
    houseSizeY = 4
    buildingMaker.mkBuildingOneRoom(world, x=x+1, y=y, width=houseSizeX, height=houseSizeY, signText="Farm")


    # Create a soil plot
    soilPlotSizeX = 6
    soilPlotSizeY = 5
    for i in range(0, soilPlotSizeX):
        for j in range(0, soilPlotSizeY):
            if (not _hasObj(x+i, y+j + houseSizeX + 1, world, "soil")):
                world.addObject(x+i, y+j + houseSizeX + 1, Layer.WORLD, SoilTile(world))

    # Randomly add a number of Mushrooms to the soil
    numMushroomsToAdd = 5
    numMushroomsAdded = 0
    attempts = 0
    while (numMushroomsAdded < numMushroomsToAdd):    
        # Pick a random location
        randX = random.randint(x, x+soilPlotSizeX-1)
        randY = random.randint(y+houseSizeY+1, y+houseSizeY+soilPlotSizeY-1)

        # If there isn't already a mushroom there, add one
        if (not _hasObj(randX, randY, world, "mushroom")):
            world.addObject(randX, randY, Layer.OBJECTS, Mushroom(world))
            numMushroomsAdded += 1

        attempts += 1
        if (attempts > 100):
            print("ERROR: Couldn't add all mushrooms to farm.  Exiting to prevent infinite loop.")
            break



# Path making
def mkPathX(x, y, lengthX, world):
    for i in range(0, lengthX):
        if (not _hasObj(x+i, y, world, "path")):
            world.addObject(x+i, y, Layer.WORLD, Path(world))

def mkPathY(x, y, lengthY, world):
    for i in range(0, lengthY):
        if (not _hasObj(x, y+i, world, "path")):
            world.addObject(x, y+i, Layer.WORLD, Path(world))

# Fence making
def mkFenceX(x, y, lengthX, world):
    for i in range(0, lengthX):
        if (not _hasObj(x+i, y, world, "fence")):
            world.addObject(x+i, y, Layer.BUILDING, Fence(world))

def mkFenceY(x, y, lengthY, world):
    for i in range(0, lengthY):
        if (not _hasObj(x, y+i, world, "fence")):
            world.addObject(x, y+i, Layer.BUILDING, Fence(world))




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

    # Intialize world
    world = World(assetPath = "assets", filenameSpriteIndex = "spriteIndex.json")
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
    
    mkCafeteria(19, 20, world, buildingMaker)

    mkTownSquare(16, 18, world, buildingMaker)

    ## TODO: Add Farm?
    mkFarm(10, 8, world, buildingMaker)

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
    world.addObject(16, 2, Layer.BUILDING, SignVillage(world))
    world.addObject(16, 29, Layer.BUILDING, SignVillage(world))

    # Add some plants
    world.addObject(15, 1, Layer.OBJECTS, PlantGeneric(world))

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
    npcChef = NPCChef(world, "Chef")
    world.addObject(20, 21, Layer.AGENT, npcChef)


    # Initial world tick
    world.tick()


    # Main rendering loop
    running = True
    frames = 0
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

        # Arrow keys -- move agent
        elif (keys[pygame.K_UP]):
            # Move agent north
            success = currentAgent.actionMoveAgent(0, -1)            
            lastMove = curTime
            print(success)
            doNextTurn = True

        elif (keys[pygame.K_DOWN]):
            # Move agent south
            success = currentAgent.actionMoveAgent(0, 1)
            lastMove = curTime
            print(success)
            doNextTurn = True

        elif (keys[pygame.K_LEFT]):
            # Move agent west
            success = currentAgent.actionMoveAgent(-1, 0)
            lastMove = curTime
            print(success)
            doNextTurn = True

        elif (keys[pygame.K_RIGHT]):
            # Move agent east
            success = currentAgent.actionMoveAgent(1, 0)
            lastMove = curTime
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
        elif (keys[pygame.K_d]):            
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

        
        # Manual state adjustment
        elif (keys[pygame.K_1]):
            # Change the colonist NPC external signal
            print("Sending 'eatSignal' to colonist NPC")
            npcColonist.attributes['states'].append("eatSignal")

            doNextTurn = True




        # Fill the window with black
        window.fill((0, 0, 0))

        # Update the world
        # If the agent has taken their turn, then update the world
        if (doNextTurn):
            world.tick()
            frames += 1
            print("Step: " + str(frames))
            time.sleep(0.25)



        # Render the world
        world.render(window, cameraX=0, cameraY=0)


        # Display the sprite
        #world.spriteLibrary.renderSprite(window, "house1_wall1", 100, 100)

        # Flip the backbuffer
        pygame.display.flip()
        #frames += 1
        
        #time.sleep(1)



# Main
if __name__ == "__main__":
    # Main function
    main()
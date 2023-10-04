
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
    buildingMaker.mkBuildingDivided(world, x=x, y=y, width=8, height=7, dividerX=0, apertureX=0, dividerY=3, apertureY=1, doorX=3, signText="Cafeteria")

    # Front (eating area)
    # Table and chairs
    #buildingMaker.mkTableAndChairs(world, x=x+7, y=y+5, chairsPresent=["n", "s", "e", "w"])
    buildingMaker.mkTableAndChairs(world, x=x+5, y=y+4, chairsPresent=["", "", "e", "w"])

    # Counter
    world.addObject(x+2, y+4, Layer.FURNITURE, Table(world))
    #world.addObject(x+2, y+5, Layer.FURNITURE, Table(world))

    # Back (kitchen)
    world.addObject(x+3, y+1, Layer.FURNITURE, Table(world))
    world.addObject(x+4, y+1, Layer.FURNITURE, Fridge(world))    
    world.addObject(x+5, y+1, Layer.FURNITURE, Sink(world))
    world.addObject(x+6, y+1, Layer.FURNITURE, Stove(world))




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
    buildingMaker.mkBuildingOneRoom(world, x=x+1, y=y, width=4, height=4, signText="Farm")

    # Create a soil plot
    for i in range(0, 6):
        for j in range(0, 5):
            if (not _hasObj(x+i, y+j + 5, world, "soil")):
                world.addObject(x+i, y+j + 5, Layer.WORLD, SoilTile(world))


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


    # Main rendering loop
    running = True
    frames = 0
    while running:
        print("Frame: " + str(frames))

        clock.tick(gameParams["fps"])

        # Check for a quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the window with black
        window.fill((0, 0, 0))

        # Update the world
        world.tick()

        # Render the world
        world.render(window, cameraX=0, cameraY=0)


        # Display the sprite
        #world.spriteLibrary.renderSprite(window, "house1_wall1", 100, 100)
        #world.spriteLibrary.renderSprite(window, "house1_bed", 50, 100)
        #world.spriteLibrary.renderSprite(window, "house1_bed_lr", 50, 100)

        # Flip the backbuffer
        pygame.display.flip()
        frames += 1
        
        #time.sleep(1)



# Main
if __name__ == "__main__":
    # Main function
    main()
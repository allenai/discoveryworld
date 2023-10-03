
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
    buildingMaker.mkBuildingDivided(world, x=x, y=y, width=12, height=7, dividerX=0, apertureX=0, dividerY=3, apertureY=1, doorX=3, signText="Barracks")


    # Add 3 beds and bedside tables (back wall)
    world.addObject(x+2, y+1, Layer.FURNITURE, Bed(world))
    world.addObject(x+3, y+1, Layer.FURNITURE, TableBedside(world))
    world.addObject(x+5, y+1, Layer.FURNITURE, Bed(world))
    world.addObject(x+6, y+1, Layer.FURNITURE, TableBedside(world))
    world.addObject(x+8, y+1, Layer.FURNITURE, Bed(world))
    world.addObject(x+9, y+1, Layer.FURNITURE, TableBedside(world))

    # Add 3 beds and bedside tables (middle wall)
    world.addObject(x+2, y+4, Layer.FURNITURE, Bed(world))
    world.addObject(x+3, y+4, Layer.FURNITURE, TableBedside(world))
    world.addObject(x+5, y+4, Layer.FURNITURE, Bed(world))
    world.addObject(x+6, y+4, Layer.FURNITURE, TableBedside(world))
    world.addObject(x+8, y+4, Layer.FURNITURE, Bed(world))
    world.addObject(x+9, y+4, Layer.FURNITURE, TableBedside(world))


    # Add a bed
    #world.addObject(x+1, y+1, Layer.FURNITURE, Bed(world))

    # Add a bedside table
    #world.addObject(x+2, y+1, Layer.FURNITURE, TableBedside(world))

def mkInfirmary(x, y, world, buildingMaker):
    # Create a building (barracks)
    buildingMaker.mkBuildingOneRoom(world, x=x, y=y, width=12, height=5)

    # Add 4 beds
    world.addObject(x+1, y+1, Layer.FURNITURE, Bed(world))
    world.addObject(x+3, y+1, Layer.FURNITURE, Bed(world))
    world.addObject(x+5, y+1, Layer.FURNITURE, Bed(world))
    world.addObject(x+7, y+1, Layer.FURNITURE, Bed(world))

    # Table
    world.addObject(x+9, y+1, Layer.FURNITURE, Table(world))    
    # Fridge
    world.addObject(x+10, y+1, Layer.FURNITURE, Fridge(world))    
    
def mkCafeteria(x, y, world, buildingMaker):
    # Create an L-shaped building (cafeteria)
    #buildingMaker.mkBuildingLDivided(world, x=x, y=y, width=10, height=8, dividerX=5)
    # Create a divided building (cafeteria)
    buildingMaker.mkBuildingDivided(world, x=x, y=y, width=10, height=10, dividerX=0, apertureX=0, dividerY=3, apertureY=1, doorX=3, signText="Cafeteria")

    # Front (eating area)
    # Table and chairs
    buildingMaker.mkTableAndChairs(world, x=x+7, y=y+5, chairsPresent=["n", "s", "e", "w"])
    buildingMaker.mkTableAndChairs(world, x=x+7, y=y+8, chairsPresent=["", "", "e", "w"])

    # Counter
    world.addObject(x+2, y+4, Layer.FURNITURE, Table(world))
    world.addObject(x+2, y+5, Layer.FURNITURE, Table(world))

    # Back (kitchen)
    world.addObject(x+3, y+1, Layer.FURNITURE, Table(world))
    world.addObject(x+5, y+1, Layer.FURNITURE, Fridge(world))    
    world.addObject(x+6, y+1, Layer.FURNITURE, Sink(world))
    world.addObject(x+7, y+1, Layer.FURNITURE, Stove(world))




def mkScienceLab(x, y, world, buildingMaker):
    # Create a building (science lab)
    #buildingMaker.mkBuildingOneRoom(world, x=x, y=y, width=5, height=5)
    buildingMaker.mkBuildingDivided(world, x=x, y=y, width=8, height=8, dividerX=5, apertureX=5, dividerY=0, apertureY=0, doorX=3, signText="Science Lab")
    bench1 = Table(world)
    world.addObject(x+1, y+1, Layer.FURNITURE, bench1)
    bench1.addObject( Microscope(world) )


def mkTownSquare(x, y, world, buildingMaker):
    # Add statue

    world.addObject(x+1, y+1, Layer.OBJECTS, Statue(world))



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
    mkHouse(4, 4, world, buildingMaker)
    
    mkScienceLab(5, 20, world, buildingMaker)


    mkInfirmary(20, 2, world, buildingMaker)

    mkBarracks(20, 10, world, buildingMaker)
    
    mkCafeteria(20, 20, world, buildingMaker)

    mkTownSquare(10, 10, world, buildingMaker)



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
        world.spriteLibrary.renderSprite(window, "house1_bed_lr", 50, 100)

        # Flip the backbuffer
        pygame.display.flip()
        frames += 1
        
        #time.sleep(1)



# Main
if __name__ == "__main__":
    # Main function
    main()
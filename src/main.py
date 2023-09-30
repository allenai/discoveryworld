
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



def main():
    print("Initializing...")

    # Game parameters
    gameParams = {
        "height": 600,
        "width": 800,
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

    # Create a building
    buildingMaker.mkHouse(world, x=4, y=4, width=8, height=8)
    buildingMaker.mkTableAndChairs(world, x=6, y=9, chairsPresent=["n", "s", "e", "w"])

    world.addObject(6, 6, Layer.FURNITURE, Stove(world))
    world.addObject(7, 6, Layer.FURNITURE, Sink(world))
    world.addObject(8, 6, Layer.FURNITURE, Fridge(world))

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
        world.spriteLibrary.renderSprite(window, "house1_wall2", 50, 100)

        # Flip the backbuffer
        pygame.display.flip()
        frames += 1
        
        #time.sleep(1)



# Main
if __name__ == "__main__":
    # Main function
    main()
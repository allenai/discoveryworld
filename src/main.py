
import pygame
import os
import json

# Sprite library
import SpriteLibrary
from World import World
from Layer import Layer
from BuildingMaker import BuildingMaker


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
    window = pygame.display.set_mode((gameParams["width"], gameParams["height"]))
    pygame.display.set_caption(gameParams["name"])

    clock = pygame.time.Clock()

    # Intialize world
    world = World(assetPath = "assets", filenameSpriteIndex = "spriteIndex.json")
    print ("All sprite names: ")
    print (world.spriteLibrary.getSpriteNames())

    # Create a building
    buildingMaker = BuildingMaker(world)
    buildingMaker.mkHouse(world, x=4, y=4, width=8, height=8)
    buildingMaker.mkTableAndChairs(world, x=6, y=9, chairsPresent=["u", "d", "l", "r"])

    world.addObject(6, 6, Layer.FURNITURE, BuildingMaker.mkObject("stove", "stove", "house1_stove_on"))
    world.addObject(7, 6, Layer.FURNITURE, BuildingMaker.mkObject("sink", "sink", "house1_sink_filled"))

    # Main rendering loop
    running = True

    while running:
        clock.tick(gameParams["fps"])

        # Check for a quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the window with black
        window.fill((0, 0, 0))

        # Display the sprite
        #world.spriteLibrary.displaySprite("house1_house_corner_tl", window, 0, 0)

        # Render the world
        world.render(window, cameraX=0, cameraY=0)

        # Flip the backbuffer
        pygame.display.flip()




# Main
if __name__ == "__main__":
    # Main function
    main()

import pygame
import os
import json

# Sprite library
import SpriteLibrary
from World import World
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
    buildingMaker.mkHouse(world, x=4, y=4, width=5, height=5)

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

        # Insert drawing code here
        # This is just a test that puts a red square in the middle of the screen
        pygame.draw.rect(window, (255, 0, 0), (gameParams["width"] / 2 - 25, gameParams["height"] / 2 - 25, 50, 50))        

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

import pygame
import os
import json

# Sprite library
import SpriteLibrary



class World:
    # Constructor
    def __init__(self, assetPath, filenameSpriteIndex):
        # Load sprites
        self.spriteLibrary = SpriteLibrary.SpriteLibrary(assetPath, filenameSpriteIndex)

        # Load world data
        # TODO




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

        # Flip the backbuffer
        pygame.display.flip()




# Main
if __name__ == "__main__":
    # Main function
    main()
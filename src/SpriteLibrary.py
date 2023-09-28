# Sprite Library class
# Keeps a library of sprites loaded in from a number of spritesheets
# Each sprite has a name associated with it (e.g. "table1_left", "grass1_center", "player1_right", etc). 
# The name is used to retrieve the sprite from the library.

import pygame
import os
import json


class SpriteLibrary:
    # Constructor
    def __init__(self, filenameIndex):
        self.filenameIndex = filenameIndex
        self.sprites = {}
        self.warnings = []

        # Load sprites from index
        self.loadIndex(filenameIndex)

        # Print warnings
        if len(self.warnings) > 0:
            print("Warnings (" + str(len(self.warnings)) + "):")
            for idx, warning in enumerate(self.warnings):
                print(str(idx) + ": " + warning)
        

    # Load sprite sheet index
    # The index is a JSON file that contains a list of spritesheet filenames and the sprites contained in each spritesheet
    def loadIndex(self, filenameIndex):
        # Load the JSON index file
        with open(filenameIndex) as f:
            data = json.load(f)

        # For each spritesheet in the index, load the spritesheet and add the sprites to the library
        count = 0
        for spritesheet in data["spritesheets"]:
            count += self.loadSpritesheet(spritesheet)
        
        print("Loaded " + str(count) + " sprites from " + filenameIndex + ".")
        

    # Add the sprites from a single spritesheet to the library
    def loadSpritesheet(self, spritesheetData):
        sheetName = spritesheetData["sheetName"]
        filename = spritesheetData["filename"]
        tileSize = spritesheetData["tileSize"]
        transparentColor = spritesheetData["transparentColor"]
        sprites = spritesheetData["sprites"]

        # Load the spritesheet
        spritesheet = pygame.image.load(filename).convert()
        spritesheet.set_colorkey(transparentColor)

        # For each sprite in the spritesheet, add it to the library
        count = 0
        for spriteName in sprites:
            sprite = sprites[spriteName]
            spriteX = sprite[0]
            spriteY = sprite[1]

            # Get the sprite from the spritesheet
            spriteRect = pygame.Rect(spriteX * tileSize[0], spriteY * tileSize[1], tileSize[0], tileSize[1])
            spriteImage = spritesheet.subsurface(spriteRect)

            # Add the sprite to the library
            # First, check for duplicate names
            if sheetName + "_" + spriteName in self.sprites:
                self.warnings.append("Duplicate sprite name: " + sheetName + "_" + spriteName + ". Sprite will be overwritten.")
            self.sprites[sheetName + "_" + spriteName] = spriteImage

            count += 1
        
        print("Loaded " + str(count) + " sprites from " + filename + ".")
        return count
        

        


        

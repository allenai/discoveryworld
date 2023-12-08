# DiscoveryWorldAPI.py
import pygame
import os
import json
import random
import time
import subprocess
import psutil

# Sprite library
import SpriteLibrary
from ObjectMaker import ObjectMaker
from World import World
from Layer import Layer
from BuildingMaker import BuildingMaker
from ScenarioMaker import *
from ObjectModel import *
from Agent import *
from ActionSuccess import *
from UserInterface import UserInterface
from DialogTree import DialogMaker
from KnowledgeScorer import *

from JSONEncoder import CustomJSONEncoder


#
#   DiscoveryWorld API
#
class DiscoveryWorldAPI:
    def __init__(self):
        self.viewportSizeX = 16
        self.viewportSizeY = 16

        # Create a random number generator
        self.r = random.Random(seed=0)

        # Create the window
        self.window = self.createHeadlessWindow()



    def loadScenario(self, scenarioName, numUserAgents = 1, randomSeed=0):
        # Create a fresh instance of a random number generator (for deterministic behavior) with a specific seed
        self.r = random.Random(seed=randomSeed)

        # First, create the World -- a blank slate 
        world = World(assetPath = "assets", filenameSpriteIndex = "spriteIndex.json", dataPath = "data/", filenameObjectData = "objects.tsv", filenameMaterialData="materials.tsv", filenameDiscoveryFeed="discoveryFeed.json")

        # Initialize the user interface
        #ui = UserInterface(window, world.spriteLibrary)    

        # Create the town scenario
        scenarioMaker = ScenarioMaker(self.r)
        scenarioMaker.makeScenarioTown(world)

        # Add tasks
        world.addTaskByName("EatMushroomTask")

        # Initial world tick
        world.tick()

        

    def step(self, actionStr):
        pass



    #
    #   Supporting functions
    #




    # Create a headless window -- i.e. a surface that can be used to render to, but no real window is created
    def createHeadlessWindow(self, windowMode="small"):
        # Initialize pygame in headless mode (i.e. no real window is created)
        os.environ["SDL_VIDEODRIVER"] = "dummy"

        # Game parameters
        gameParams = {
            "height": 1024,
            "width": 1024,
            "fps": 60,
            "name": "DiscoveryWorld"            
        }
        
        # Create the window
        window = pygame.display.set_mode((gameParams["width"], gameParams["height"]))
        pygame.display.set_caption("DiscoveryWorld")
    
        # Inititalize the clock
        clock = pygame.time.Clock()

        # Initialize font renderer
        pygame.font.init()

        # Return the window
        return window
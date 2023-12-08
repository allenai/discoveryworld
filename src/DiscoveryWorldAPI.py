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
        self.NAME = "DiscoveryWorld API"
        self.VERSION = "0.1"

        self.viewportSizeX = 16
        self.viewportSizeY = 16

        # Create a random number generator
        self.r = random.Random()        
        self.r.seed(0)

        # Create the window
        self.window = self.createHeadlessWindow()

        # World
        self.world = None

        # User interfaces (one per agent)
        self.numUserAgents = 0
        self.ui = []


    def getNameAndVersion(self):
        return self.NAME + " v" + self.VERSION


    def loadScenario(self, scenarioName, numUserAgents = 1, randomSeed=0):
        # Create a fresh instance of a random number generator (for deterministic behavior) with a specific seed
        self.r = random.Random()
        self.r.seed(randomSeed)

        # Set the number of agents
        self.numUserAgents = numUserAgents

        # First, create the World -- a blank slate 
        self.world = World(assetPath = "assets", filenameSpriteIndex = "spriteIndex.json", dataPath = "data/", filenameObjectData = "objects.tsv", filenameMaterialData="materials.tsv", filenameDiscoveryFeed="discoveryFeed.json")

        # Create the town scenario
        scenarioMaker = ScenarioMaker(self.r)
        scenarioMaker.makeScenarioTown(self.world, self.numUserAgents)

        # Add tasks
        self.world.addTaskByName("EatMushroomTask")

        # Initialize and attach user interfaces to the agents
        userAgents = self.world.getUserAgents()
        for userAgent in userAgents:
            ui = UserInterface(self.window, self.world.spriteLibrary)    # Create a user interface for this agent
            ui.setAgent(userAgent)                                  # Attach this UI to this agent
            self.ui.append(ui)                                      # Store it
        self.numUserAgents = len(userAgents)                        # If the number of user agents happens to be less for some reason (e.g. if the scenario has a maximum number it supports), then update the number of user agents


        # Initial world tick
        self.world.tick()

        

            
    # Gets the current observation of the world from a given agent's perspective 
    def getAgentObservation(self, agentIdx):
        # Check to make sure the agent index is valid
        if (agentIdx < 0) or (agentIdx >= self.numUserAgents):            
            response = {"errors": ["Agent index out of range. Specified agent index: " + str(agentIdx) + ". Number of agents: " + str(self.numUserAgents) + " (i.e. value must be between 0 and " + str(self.numUserAgents - 1) + ")"]}
            return response
        
        # Check that the world is initialized
        if (self.world == None):                        
            response = {"errors": ["World is not initialized"]}
            return response
        
        
        # Get a reference to this agent's UI
        ui = self.ui[agentIdx]

        # Get a reference to the agent        
        agent = ui.currentAgent

        # Get the agent's current location
        agentLocation = agent.getWorldLocation()

        # Clear the viewport
        self.window.fill((0, 0, 0))

        # Step 3: Render the viewport (the world view) for this agent
        worldStartX = agentLocation[0] - int(self.viewportSizeX / 2)
        worldStartY = agentLocation[1] - int(self.viewportSizeY / 2)        
        self.world.renderViewport(self.window, worldStartX, worldStartY, self.viewportSizeX, self.viewportSizeY, 0, 0)

        # Step 5: Render the user interface for this agent
        ui.render()
        uiJSON = ui.renderJSON()

        # Flip the backbuffer, to display this content to the window
        pygame.display.flip()

        # Capture the current window (i.e. through a screenshot) and save it to a file
        FRAME_DIR = "video/frames"
        curStep = self.world.getStepCounter()
        frameFilename = FRAME_DIR + "/ui_agent_" + str(agentIdx) + "_frame_" + str(curStep) + ".png"
        pygame.image.save(self.window, frameFilename)

        response = {"errors": [], "ui": uiJSON} 
        return response

    #
    #   UI
    #
    def setUI(self, agentIdx):
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
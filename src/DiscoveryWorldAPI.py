# DiscoveryWorldAPI.py
import pygame
import os
import json
import random
import time
import subprocess
import psutil

import io
import base64

# Sprite library
import SpriteLibrary
from ObjectMaker import ObjectMaker
from World import World
from Layer import Layer
from BuildingMaker import BuildingMaker
from ScenarioMaker import *
from ObjectModel import *
from Agent import *
from ActionHistory import *
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

        self.FRAME_DIR = "video/frames"

        self.viewportSizeX = 15
        self.viewportSizeY = 15

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

        # Which agents have already performed actions this step
        self.agentsThatHaveActedThisStep = set()


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
        # Start populating response
        response = {"errors": [], "ui": {}, "vision": {}}

        # Check to make sure the agent index is valid
        if (agentIdx < 0) or (agentIdx >= self.numUserAgents):            
            response["errors"].append("Agent index out of range. Specified agent index: " + str(agentIdx) + ". Number of agents: " + str(self.numUserAgents) + " (i.e. value must be between 0 and " + str(self.numUserAgents - 1) + ")")
            return response
        
        # Check that the world is initialized
        if (self.world == None):                                    
            response["errors"].append("World is not initialized")
            return response
        
        
        # Get a reference to this agent's UI
        ui = self.ui[agentIdx]

        # Get a reference to the agent        
        agent = ui.currentAgent

        # Get the agent's current location
        agentLocation = agent.getWorldLocation()
        
        # Define the viewport for this agent
        worldStartX = agentLocation[0] - int(self.viewportSizeX / 2)
        worldStartY = agentLocation[1] - int(self.viewportSizeY / 2)        

        # Step 3: Render the viewport (the world view) and the UI for this agent
        self.window.fill((0, 0, 0)) # Clear the viewport
        self.world.renderViewport(self.window, worldStartX, worldStartY, self.viewportSizeX, self.viewportSizeY, 0, 0, includeGrid=False)        
        ui.render()                 # Render UI
        pygame.display.flip()       # Flip the backbuffer, to display this content to the window

        # Capture the current window, and save to file
        curStep = self.world.getStepCounter()
        filenameOutPNG = self.FRAME_DIR + "/ui_agent_" + str(agentIdx) + "_frame_" + str(curStep) + ".png"
        pygame.image.save(self.window, filenameOutPNG)

        # Also capture just the first 512x512 pixels of the window, and encode it as a base64 string
        # This is for the agent's "vision"
        visionSurface = pygame.Surface((512, 512))
        visionSurface.blit(self.window, (0, 0), (0, 0, 512, 512))
        image_io = io.BytesIO()
        pygame.image.save(visionSurface, image_io, 'PNG')                       # Convert to PNG
        image_io.seek(0)                                                        # Go to the beginning of the BytesIO object
        encodedImageNoGrid = base64.b64encode(image_io.read()).decode('utf-8')       # Convert to base64        
        encodedImageNoGrid = "data:image/png;base64," + encodedImageNoGrid
        response["vision"]["base64_no_grid"] = encodedImageNoGrid

        # Step 4: Also capture the viewport with the grid
        self.window.fill((0, 0, 0)) # Clear the viewport
        self.world.renderViewport(self.window, worldStartX, worldStartY, self.viewportSizeX, self.viewportSizeY, 0, 0, includeGrid=True)
        ui.render()                 # Render UI
        pygame.display.flip()       # Flip the backbuffer, to display this content to the window

        # Capture the first 512x512 pixels of the window, and encode it as a base64 string
        # This is for the agent's "vision"
        visionSurface = pygame.Surface((512, 512))
        visionSurface.blit(self.window, (0, 0), (0, 0, 512, 512))
        image_io = io.BytesIO()
        pygame.image.save(visionSurface, image_io, 'PNG')                       # Convert to PNG
        image_io.seek(0)                                                        # Go to the beginning of the BytesIO object
        encodedImageWithGrid = base64.b64encode(image_io.read()).decode('utf-8')       # Convert to base64        
        encodedImageWithGrid = "data:image/png;base64," + encodedImageWithGrid
        response["vision"]["base64_with_grid"] = encodedImageWithGrid

        # JSON rendering
        uiJSON = ui.renderJSON()
        response["ui"] = uiJSON        

        # Return response        
        return response


    # Lists all known actions (as they are parsed by the JSON action interpreter), by directly enumerating the ActionType enum
    def listKnownActions(self, limited:bool=False):
        return getActionDescriptions(limited)      # from ActionHistory
        
    # Additional helpful information about the action string, for building prompts. 
    def additionalActionDescriptionString(self):
        outStr = ""
        outStr += "Actions are expressed as JSON. The format is as follows: `{\"action\": \"USE\", \"arg1\": 5, \"arg2\": 12}`, where 'action' is the action type, and 'arg1' and 'arg2' refer to the UUIDs of the objects that serve as arguments. Some actions may require arg1, arg2, or no arguments.  Discovery Feed actions require different arguments.  What arguments are required for specific actions is provided in the known actions list.  Attempting actions not in the known actions list will result in an error." 
        return outStr


    # Perform an action for a given agent
    def performAgentAction(self, agentIdx, actionJSON):
        # Check to make sure the agent index is valid
        if (agentIdx < 0) or (agentIdx >= self.numUserAgents):            
            response = {"errors": ["Agent index out of range. Specified agent index: " + str(agentIdx) + ". Number of agents: " + str(self.numUserAgents) + " (i.e. value must be between 0 and " + str(self.numUserAgents - 1) + ")"]}
            return response
        
        # Check that the world is initialized
        if (self.world == None):                        
            response = {"errors": ["World is not initialized"]}
            return response
        
        # Check that this agent has not already acted this step
        if (agentIdx in self.agentsThatHaveActedThisStep):
            response = {"errors": ["Agent has already acted this step.  World tick must be called before this agent can act again."]}
            return response
        
        
        # Get a reference to this agent's UI
        ui = self.ui[agentIdx]

        # Get a reference to the agent        
        agent = ui.currentAgent

        # Parse any action keys
        doTick, jsonParseErrors, success = ui.parseActionJSON(jsonIn = actionJSON)

        # Pack the response
        response = {
            "errors": jsonParseErrors,
            "success": success            
        }

        if (success != None):
            # Update the UI with the message (for the bottom of the screen)
            ui.updateLastActionMessage(success.message)

            # If the message was rated as high importance, also add it to the explicit modal dialog queue
            if (success.importance == MessageImportance.HIGH):
                ui.addTextMessageToQueue(success.message)
        else:
            # Update the UI with the message (for the bottom of the screen)
            ui.updateLastActionMessage("Invalid action")
            response["errors"].append("Invalid action")


        # Mark that this agent has acted this step
        self.agentsThatHaveActedThisStep.add(agentIdx)
        
        return response



    #
    #   World tick
    #
    def tick(self):
        response = {
            "errors": [],
            "success": False
        }

        # Check that the world is initialized
        if (self.world == None):                        
            response["errors"].append("World is not initialized")            
            return response

        # Tick the world
        self.world.tick()

        # Reset the agents that have acted this step
        self.agentsThatHaveActedThisStep = set()

        response["success"] = True
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
            "height": 800,
            "width": 800,
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
    

    # Convert a directory of frames into an agent video, using ffmpeg
    def createAgentVideo(self, agentIdx:int, filenameOut:str):
        # Call FFMPEG (forces overwrite)
        filenameInPrefix = self.FRAME_DIR + "/ui_agent_" + str(agentIdx) + "_frame_%d.png"
        #filenameOut = "output_agent" + str(agentIdx) + ".mp4"

        subprocess.call(["ffmpeg", "-y", "-framerate", "10", "-i", filenameInPrefix, "-c:v", "libx264", "-profile:v", "high", "-crf", "20", "-pix_fmt", "yuv420p", filenameOut])

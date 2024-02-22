# World.py

import SpriteLibrary
from ObjectMaker import ObjectMaker
from Layer import Layer
from ObjectModel import Object
from TaskScorer import *
from UUIDGenerator import *
from DiscoveryFeed import *
import pygame
import time
import zlib
import pickle


# Storage class for the world (including the full environment grid)
class World:
    # Constructor
    def __init__(self, assetPath, filenameSpriteIndex, dataPath, filenameObjectData, filenameMaterialData, filenameDiscoveryFeed):
        # World size (in tiles)
        self.sizeX = 32
        self.sizeY = 32

        # Default parameters of the world that can change (like background radiation level)
        self.parameters = {
            "avgRadiationBackgroundLevelUSVH": 0.05        # Average background radiation level in uSV/h
        }

        # UUID Generator
        self.uuidGenerator = UUIDGenerator()

        # Load sprites
        self.spriteLibrary = SpriteLibrary.SpriteLibrary(assetPath, filenameSpriteIndex)

        # Load object data
        self.objectMaker = ObjectMaker(dataPath, filenameObjectData, filenameMaterialData, world=self, knownSpriteNames=self.spriteLibrary.getSpriteNames())

        # Initialize grid
        self.grid = [[self.mkBlankGridTile() for x in range(self.sizeX)] for y in range(self.sizeY)]

        # Initialize agent array
        self.agents = []

        # Initialize DiscoveryFeed, and load any pre-existing articles and update posts
        self.discoveryFeed = DiscoveryFeed(dataPath + "/" + filenameDiscoveryFeed)

        # Initialize task generator and scorer
        self.taskMaker = TaskMaker(world=self)
        self.taskScorer = TaskScorer(world=self)

        # Load world data
        # TODO

        # Step number (i.e. number of ticks that have passed)
        self.step = 0

        # Font
        self.font = pygame.font.SysFont("Arial", 8)

        # World history
        self.worldHistory = []

        # Add a dictionary of teleport locations (key = location name), to make an agent's navigation task easier
        self.teleportLocations = {}


    #
    #   Initialization (agents, tasks)
    #

    # Add an agent to the world
    def addAgent(self, agent):
        self.agents.append(agent)

    # Return an agent by name
    def getAgentByName(self, agentName):
        for agent in self.agents:
            if agent.name == agentName:
                return agent

        return None

    # Return a list of all agents that are user agents
    def getUserAgents(self):        
        userAgents = []
        for agent in self.agents:
            if (agent.attributes["isNPC"] == False):
                userAgents.append(agent)
        return userAgents
    
    # Return a list of all agents that are NPC agents
    def getNPCAgents(self):        
        npcAgents = []
        for agent in self.agents:
            if (agent.attributes["isNPC"] == True):
                npcAgents.append(agent)
        return npcAgents

    def addTaskByName(self, taskName):
        task = self.taskMaker.makeTask(taskName)
        if task != None:
            self.taskScorer.addTask(task)
            task.taskSetup()
            return True
        else:
            print("Error: Task name not recognized: " + taskName)
            return False



    #
    # Get the current step number.  Starts at 0, increments 1 per call to the world.tick().
    #
    def getStepCounter(self):
        return self.step
    

    #
    #   Grid
    #

    # Create a blank grid tile
    def mkBlankGridTile(self):
        gridTile = {
            "layers": {}
        }

        for layer in Layer:
            gridTile["layers"][layer] = []

        return gridTile


    # Add an object to the world
    def addObject(self, x, y, layer, object:Object):
        # Bound checking: Make sure the object is within the world bounds
        #if x < 0 or x >= self.sizeX or y < 0 or y >= self.sizeY:
        if (self.isWithinBounds(x, y) == False):
            print("Error: Object out of bounds: " + str(x) + ", " + str(y))
            return False


        # Remove the object from its current container
        object.removeSelfFromContainer()

        ## TODO: Does it also have to be removed from the current grid location on the world grid? (e.g. 'addObject'ing the same object to two locations currently appears to render duplicate copies of the same object)
        
        # Set the object's position
        object.setWorldLocation(x, y)

        # World, building, and furniture layers are overwrite layers (i.e. they can hold only a single object)
        # if layer == Layer.WORLD or layer == Layer.BUILDING or layer == Layer.FURNITURE:
        #     self.grid[x][y]["layers"][layer] = []
        #     self.grid[x][y]["layers"][layer].append(object)
        # # Objects layer is an additive layer (i.e. it can hold multiple objects)
        # elif layer == Layer.OBJECTS:
        #     self.grid[x][y]["layers"][layer].append(object)
        # # Player layer is a special layer that can only hold a single object
        # elif layer == Layer.AGENT:
        #     self.grid[x][y]["layers"][layer] = []
        #     self.grid[x][y]["layers"][layer].append(object)

        # All layers can hold multiple objects (prevents objects suddenly disappearing when a new object is moved to the same world location)
        if (layer == Layer.WORLD) or (layer == Layer.BUILDING) or (layer == Layer.FURNITURE) or (layer == Layer.OBJECTS) or (layer == Layer.AGENT):
           self.grid[x][y]["layers"][layer].append(object) 
        else:
            print("Error: Invalid layer: " + str(layer))
            return False


    # Get all objects at a given position
    def getObjectsAt(self, x, y, respectContainerStatus=False, includeParts=False, excludeObjectsOnAgents=False):
        # Bound checking: Make sure the object is within the world bounds
        if x < 0 or x >= self.sizeX or y < 0 or y >= self.sizeY:
            print("Error: Object out of bounds: " + str(x) + ", " + str(y))
            return []

        #print("\t\t\tGetting objects at (" + str(x) + ", " + str(y) + ")")
        # Get the objects
        objects = []
        for layer in Layer:            
            #objects += self.grid[x][y]["layers"][layer]
            objsToAdd = self.grid[x][y]["layers"][layer]
            if (len(objsToAdd) > 0):
                #print("\t\t\t\tLayer: " + str(layer) + " (" + str(len(objsToAdd)) + " objects)") 
                for obj in objsToAdd:
                    objects.append(obj)
                    contents = []
                    # Check if this object is an agent (i.e. is an instance of Agent)
                    if (excludeObjectsOnAgents == True) and (obj.attributes["isAgent"] == True):
                        #print("\t\t\t\t\tSkipping agent " + obj.name)
                        continue

                    # Add contents/parts
                    if (includeParts == False):
                        contents = obj.getAllContainedObjectsRecursive(respectContainerStatus=respectContainerStatus)
                    else:
                        contents = obj.getAllContainedObjectsAndParts(includeContents=True, includeParts=True)
                    if (len(contents) > 0):
                        #print("Contents of " + obj.name + ": " + str(contents))
                        objects += contents
                    
                    

            #objects += objsToAdd


            #for obj in self.grid[x][y]["layers"][layer]:
            #    objects += obj.getAllContainedObjectsRecursive(respectContainerStatus=True)

        return objects

    # Helper to get all world objects (for example, for scoring)
    def getAllWorldObjects(self):
        allObjects = []
        for x in range(self.sizeX):
            for y in range(self.sizeY):
                allObjects += self.getObjectsAt(x, y)
        return allObjects


    # Remove an object from the world
    def removeObject(self, object:Object):
        # First, get the object's position (stored internally in that object)
        objX, objY = object.getWorldLocation()
        # Then, set the object's position to -1 (i.e. not in the world)
        object.setWorldLocation(-1, -1)

        # Remove the object from its current container
        object.removeSelfFromContainer()

        # Remove the object from the world
        if (objX >= 0) and (objY >= 0):
            for layer in Layer:
                if object in self.grid[objX][objY]["layers"][layer]:
                    # Remove object from this layer
                    self.grid[objX][objY]["layers"][layer].remove(object)
                    # Success
                    return True



        # If we reach here, something went wrong -- the object could not be removed from the world.
        #print("WARNING: Object could not be removed from the world (" + object.name + ") at (" + str(objX) + ", " + str(objY) + ")")
        return True

    

    #
    #   Object Generation (light wrapper around ObjectMaker)
    #
    
    def createObject(self, objectReferenceName):
        return self.objectMaker.createObject(objectReferenceName)


    #
    #   Helpers for quickly checking world contents
    #

    # Returns true if the given location has a non-zero number of objects in layers: building, furniture, objects, agent
    def doesTileHaveObjectsOnIt(self, x, y):
        checkLayers = [Layer.BUILDING, Layer.FURNITURE, Layer.OBJECTS, Layer.AGENT]

        # Bound checking: Make sure the object is within the world bounds
        if x < 0 or x >= self.sizeX or y < 0 or y >= self.sizeY:
            print("Error: Object out of bounds: " + str(x) + ", " + str(y))
            return False
                
        # Check if the tile has any objects
        for layer in checkLayers:
            if len(self.grid[x][y]["layers"][layer]) > 0:
                return True

        # If we reach here, the tile has no objects
        return False
        

    #
    #   Traversability
    #
    
    # Check if a tile is passable
    # Returns (bool, obj) where:
    #  - bool is true if the tile is passable, and obj is the first impassable object encountered at that location. 
    #  - If the tile is passable, obj is None.
    def isPassable(self, x, y):
        # Bound checking: Make sure the object is within the world bounds
        if x < 0 or x >= self.sizeX or y < 0 or y >= self.sizeY:
            #print("Error: Object out of bounds: " + str(x) + ", " + str(y))
            return (False, None)

        # Check if the tile is passable
        # Collect all the objects across all layers
        allObjs = self.getObjectsAt(x, y)
        # Check if any of the objects are impassable
        for object in allObjs:
            if (not object.attributes["isPassable"]):
                return (False, object)

        # If we reach here, the tile is passable
        return (True, None)


    #
    #   Bound Checking
    #

    # Returns true if the specified position is within the world grid bounds
    def isWithinBounds(self, x, y):
        return (x >= 0) and (x < self.sizeX) and (y >= 0) and (y < self.sizeY)

    #
    #   World update
    #
    def tick(self):
        # Update all objects in the world

        # First, reset whether each object has had its tick() function called this tick
        for x in range(self.sizeX):
            for y in range(self.sizeY):
                for layer in Layer:
                    for object in self.grid[x][y]["layers"][layer]:                        
                        object.resetTick()

                # alObjs = self.getObjectsAt(x, y, respectContainerStatus=False, includeParts=True)   # We need to do it this way, to make sure we reset the tick for all the nested parts. 
                # for object in alObjs:
                #         object.tickCompleted = False


        # Then, call tick() on each object in the world
        for x in range(self.sizeX):
            for y in range(self.sizeY):
                for layer in Layer:
                    for object in self.grid[x][y]["layers"][layer]:
                        object.tick()


        # Also do a tick of the task scorer, to measure task progress
        self.taskScorer.updateTick()

        # Also save the world history
        self.saveWorldHistory()

        # Collect any signals from posts sent in the current Discovery Feed step
        signalsToBroadcast = self.discoveryFeed.getSignalsFromPosts(curStep = self.step)
        
        # Broadcast those signals to all agents
        for agent in self.agents:
            for signal in signalsToBroadcast:
                print("BROADCASTING SIGNAL " + str(signal) + " to agent " + agent.name)
                agent.addState(signal)            

        # Increment step counter
        self.step += 1


    #
    #   Saving a world history
    #
    def saveWorldHistory(self):
        print("Saving world history...")

        # Keep track of time
        startTime = time.time()

        # First, create a new world history dictionary. 
        packed = {
            "step": self.step,
            "sizeX": self.sizeX,
            "sizeY": self.sizeY,
            "grid": [],    
            "discoveryFeed": self.discoveryFeed.toDict()        
        }

        # Clone everything in the grid into this record
        totalObjects = 0        
        for x in range(self.sizeX):
            packed["grid"].append([])
            for y in range(self.sizeY):                
                # Add all objects in this tile
                allObjs = []
                for layer in Layer:                    
                    for object in self.grid[x][y]["layers"][layer]:

                        # For each object, get all the objects it contains/that are its parts. 
                        allObjContentsAndParts = object.getAllContainedObjectsAndParts()
                        # Add them to the list of objects to save
                        for obj in allObjContentsAndParts:
                            # Pack to dict using the to_dict() method
                            allObjs.append( obj.to_dict() )                        
                            totalObjects += 1            
                            
                packed["grid"][x].append(allObjs)

        # Save the history
        #packed["objects"] = allObjs

        # Compress the world history using zlib and pickle (saves almost 99% of space!)
        packedCompressed = zlib.compress(pickle.dumps(packed))

        self.worldHistory.append(packedCompressed)

        print("Number of items in world history:" + str(len(self.worldHistory)))
        print("Size of most recent item: " + str(len(packedCompressed)) + " bytes " + str(len(packedCompressed) / 1024) + " KB")
                    
        # delta time
        deltaTime = time.time() - startTime        
        print("World history includes " + str(totalObjects) + " objects.")
        print("World history saved in " + str(deltaTime) + " seconds.")


    def getWorldHistoryAtStep(self, step):
        # Return the world history at the specified step
        # Since the world history is pickled then compressed, this will require uncompressing then unpickling
        if (step < 0 or step >= len(self.worldHistory)):
            return None

        # Get compressed history for a given step
        compressedPickled = self.worldHistory[step]

        # Uncompress the history
        pickled = zlib.decompress(compressedPickled)
        # Unpickle the history
        history = pickle.loads(pickled)

        return history
        
    # Export the world history to a (pickled)
    def exportWorldHistory(self, filename):        
        print("Exporting world history to file: " + filename + "...")
        f = open(filename, "wb")
        f.write(pickle.dumps(self.worldHistory))
        f.close()
        print("Export complete.")


    #
    #   Rendering
    #       
    def render(self, window, cameraX, cameraY):
        #world.spriteLibrary.displaySprite("house1_house_corner_tl", window, 0, 0)
        # Render the world
        for y in range(self.sizeY):
            for x in range(self.sizeX):

                # Render the world layer
                for object in self.grid[x][y]["layers"][Layer.WORLD]:
                    #print("Rendering: " + object.name)
                    #self.spriteLibrary.renderSprite(window, object.getSpriteName(), x * 32 - cameraX, y * 32 - cameraY)
                    for spriteName in object.getSpriteNamesWithContents():
                        self.spriteLibrary.renderSprite(window, spriteName, x * 32 - cameraX, y * 32 - cameraY)

                # Render the building layer
                for object in self.grid[x][y]["layers"][Layer.BUILDING]:
                    #print("Rendering: " + object.name)
                    #self.spriteLibrary.renderSprite(window, object.getSpriteName(), x * 32 - cameraX, y * 32 - cameraY)
                    for spriteName in object.getSpriteNamesWithContents():
                        self.spriteLibrary.renderSprite(window, spriteName, x * 32 - cameraX, y * 32 - cameraY)

                # Render the furniture layer
                for object in self.grid[x][y]["layers"][Layer.FURNITURE]:
                    #print("Rendering: " + object.name)
                    #self.spriteLibrary.renderSprite(window, object.getSpriteName(), x * 32 - cameraX, y * 32 - cameraY)
                    for spriteName in object.getSpriteNamesWithContents():
                        self.spriteLibrary.renderSprite(window, spriteName, x * 32 - cameraX, y * 32 - cameraY)

                # Render the objects layer
                for object in self.grid[x][y]["layers"][Layer.OBJECTS]:
                    #print("Rendering: " + object.name)
                    #self.spriteLibrary.renderSprite(window, object.getSpriteName(), x * 32 - cameraX, y * 32 - cameraY)
                    for spriteName in object.getSpriteNamesWithContents():
                        self.spriteLibrary.renderSprite(window, spriteName, x * 32 - cameraX, y * 32 - cameraY)

                # Render the player layer
                for object in self.grid[x][y]["layers"][Layer.AGENT]:
                    #print("Rendering: " + object.name)
                    #self.spriteLibrary.renderSprite(window, object.getSpriteName(), x * 32 - cameraX, y * 32 - cameraY)
                    for spriteName in object.getSpriteNamesWithContents():
                        self.spriteLibrary.renderSprite(window, spriteName, x * 32 - cameraX, y * 32 - cameraY)


    #   Render a viewport, starting from world position (worldStartX, worldStartY), and of size (in tiles) (sizeTilesX, sizeTilesY). 
    #   The offset (in pixels) from the top-left corner of the window is (offsetX, offsetY)
    def renderViewport(self, window, worldStartX, worldStartY, sizeTilesX, sizeTilesY, offsetX, offsetY, scale=1.0, includeGrid=False):
        # Render the viewport
        originalTileSize = int(32)
        tileSize = int(32 * scale)

        # Handle the wonkyness of the scaling as it relates to slight Y drawing offsets (particularly for non-standard (i.e. non-32-pixel) sprites)
        tileDiff = tileSize - originalTileSize
        #offsetY -= tileDiff

        # DEBUG: Enable rendering grid locations
        renderGridLocations = False
        # For agents: Enable rendering grid (expands the tile size by one, to leave a functional black grid line between tiles)
        #if (includeGrid):
        #    tileSize += 1

        for y in range(worldStartY, worldStartY + sizeTilesY):
            for x in range(worldStartX, worldStartX + sizeTilesX):
                # Bound checking: Make sure the object is within the world bounds
                if (x < 0) or (x >= self.sizeX) or (y < 0) or (y >= self.sizeY):
                    #print("Error: Object out of bounds: " + str(x) + ", " + str(y))
                    continue

                # Determine screen x/y coordinates
                screenX = (x - worldStartX) * tileSize + offsetX
                screenY = (y - worldStartY) * tileSize + offsetY

                # Render the world layer
                for object in self.grid[x][y]["layers"][Layer.WORLD]:
                    for spriteName in object.getSpriteNamesWithContents():
                        self.spriteLibrary.renderSprite(window, spriteName, screenX, screenY, scale)

                # Render the building layer
                for object in self.grid[x][y]["layers"][Layer.BUILDING]:
                    for spriteName in object.getSpriteNamesWithContents():
                        self.spriteLibrary.renderSprite(window, spriteName, screenX, screenY, scale)

                # Render the furniture layer
                for object in self.grid[x][y]["layers"][Layer.FURNITURE]:
                    for spriteName in object.getSpriteNamesWithContents():
                        self.spriteLibrary.renderSprite(window, spriteName, screenX, screenY, scale)

                # Render the objects layer
                for object in self.grid[x][y]["layers"][Layer.OBJECTS]:
                    for spriteName in object.getSpriteNamesWithContents():
                        self.spriteLibrary.renderSprite(window, spriteName, screenX, screenY, scale)
                
                # Render the agent layer
                for object in self.grid[x][y]["layers"][Layer.AGENT]:
                    for spriteName in object.getSpriteNamesWithContents():
                        self.spriteLibrary.renderSprite(window, spriteName, screenX, screenY, scale)
    
                # If enabled, render the grid location (for debugging)
                if (renderGridLocations):
                    text = self.font.render(str(x) + "," + str(y), True, (0, 0, 0))
                    window.blit(text, (screenX, screenY))
                if (renderGridLocations) or (includeGrid):
                    # Also draw a rectangle around the tile                    
                    #pygame.draw.rect(window, (0, 0, 0), (screenX, screenY, tileSize, tileSize), 1)
                    pygame.draw.rect(window, (0, 0, 0), (screenX, screenY, tileSize, tileSize), 1)
                    
                    
                    


    #
    #   Teleport locations
    #
    def addTeleportLocation(self, name, gridX, gridY):
        self.teleportLocations[name] = {"gridX": gridX, "gridY": gridY}

    def getTeleportLocations(self):
        return self.teleportLocations
                    



    #
    #   Pathfinding
    #   

    # Get the next step in the path from one location to another
    #def getNextStep(self, fromLocation, toLocation):

    


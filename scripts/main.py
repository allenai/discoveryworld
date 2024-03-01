
import argparse
import pygame
import os
import json
import random
import time
import subprocess
import psutil
from discoveryworld.ActionSuccess import MessageImportance
from discoveryworld.KnowledgeScorer import Measurement
from discoveryworld.UserInterface import UserInterface
from discoveryworld.ScenarioMaker import ScenarioMaker, SCENARIOS

from discoveryworld.World import World

# Sprite library
# import SpriteLibrary
# from ObjectMaker import ObjectMaker
# from World import World
# from Layer import Layer
# from BuildingMaker import BuildingMaker
# from ScenarioMaker import *
# from ObjectModel import *
# from Agent import *
# from ActionSuccess import *
# from UserInterface import UserInterface
# from DialogTree import DialogMaker
# from KnowledgeScorer import *

# from JSONEncoder import CustomJSONEncoder


def main(args):
    print("Initializing...")


    # 32 pixels/tile * 32 tiles = 1024 pixels

    #windowMode = "small"
    windowMode = "big"
    # Game parameters
    if (windowMode == "small"):
        gameParams = {
            "height": 750,
            "width": 800,
            "fps": 60,
            "name": "DiscoveryWorld"
        }

        # Step 2: Define the viewport size (in tiles)
        viewportSizeX = 24
        viewportSizeY = 16
    else:
        gameParams = {
            "height": 1024,
            "width": 1024,
            "fps": 60,
            "name": "DiscoveryWorld"
        }

        # Step 2: Define the viewport size (in tiles)
        viewportSizeX = 32
        viewportSizeY = 32



    # Open window
    #window = pygame.display.set_mode((gameParams["width"], gameParams["height"]))
    # Open window (should open in top left corner)
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50,50)
    window = pygame.display.set_mode((gameParams["width"], gameParams["height"]))
    pygame.display.set_caption(gameParams["name"])

    clock = pygame.time.Clock()

    # Initialize font renderer
    pygame.font.init()

    # Intialize world
    world = World(assetPath=None, filenameSpriteIndex="spriteIndex.json", dataPath=None, filenameObjectData="objects.tsv", filenameMaterialData="materials.tsv", filenameDiscoveryFeed="discoveryFeed.json")
    print ("All sprite names: ")
    print (world.spriteLibrary.getSpriteNames())

    # Initialize the user interface
    ui = UserInterface(window, world.spriteLibrary)

    # Create a new random number generator (for deterministic behavior) with a specific seed
    r = random.Random()

    scenarioMaker = ScenarioMaker(world, rng=r)
    scenarioMaker.setupScenario(args.scenario)

    # Initial world tick
    world.tick()


    # Find a user agent
    userAgents = world.getUserAgents()
    if (len(userAgents) == 0):
        print("ERROR: No user agents found!")
        exit(1)
    currentAgent = userAgents[0]

    # Attach the user interface to the agent
    ui.setAgent(currentAgent)


    # Create a directory "/video" for storing video frames
    VIDEO_DIR = "video"
    FRAME_DIR = "video/frames"
    if (not os.path.exists(VIDEO_DIR)):
        os.mkdir(VIDEO_DIR)
    if (not os.path.exists(FRAME_DIR)):
        os.mkdir(FRAME_DIR)
    # Empty the frames directory
    for filename in os.listdir(FRAME_DIR):
        os.remove(FRAME_DIR + "/" + filename)


    # Main rendering loop
    running = True
    frames = 0
    autoRunCycles = 0
    lastMove = time.time()        # Time of last move (in seconds since start of game)
    lastSize = 0
    while running:
        #print("Frame: " + str(frames))
        exportFrame = False

        curTime = time.time()
        clock.tick(gameParams["fps"])

        # Check for a quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Check for keyboard input
        keys = pygame.key.get_pressed()

        # Signify whether the agent has done their move this turn
        doNextTurn = False

        if (ui.inModal):
            # Pressing any key will close the modal
            if (keys[pygame.K_SPACE] or keys[pygame.K_RETURN]):
                ui.closeModal()
                doNextTurn = True

        else:
            # Escape -- quits the game
            if (keys[pygame.K_ESCAPE]):
                running = False

            # Parse any action keys
            (doTick, success) = ui.parseKeys(keys)

            if (success != None):
                # Export the frame, regardless of whether the action was successful, or whether it was a non-tick (e.g. UI) action
                exportFrame = True

                # Action was performed
                if (doTick):
                    doNextTurn = True

                # Update the UI with the message (for the bottom of the screen)
                ui.updateLastActionMessage(success.message)

                # If the message was rated as high importance, also add it to the explicit modal dialog queue
                if (success.importance == MessageImportance.HIGH):
                    ui.addTextMessageToQueue(success.message)

            else:

                # # Manual state adjustment
                if (keys[pygame.K_1]):
                    pass
                #     # Change the colonist NPC external signal
                #     print("Sending 'eatSignal' to colonist NPC")
                #     for npcColonist in npcColonists:
                #          npcColonist.attributes['states'].add("eatSignal")

                #     doNextTurn = True

                # elif (keys[pygame.K_2]):
                #     # Change the Chef NPC external signal
                #     print("Sending 'collectSignal' to chef NPC")
                #     npcChef.attributes['states'].add("collectSignal")

                #     doNextTurn = True

                # elif (keys[pygame.K_3]):
                #     # Change the Chef NPC external signal
                #     print("Sending 'serveSignal' to chef NPC")
                #     npcChef.attributes['states'].add("serveSignal")

                #     doNextTurn = True

                # elif (keys[pygame.K_4]):
                #     # Change the Farmer's external signal
                #     print("Sending 'plantSignal' to Farmer NPC")
                #     npcFarmer.attributes['states'].add("plantSignal")

                #     doNextTurn = True


                # Manual "wait"
                elif (keys[pygame.K_w]):
                    # Wait a turn
                    print("Waiting (taking no action this turn)...")
                    doNextTurn = True


                # Manual "run for 100 cycles"
                elif (keys[pygame.K_0]):
                    # Run for 100 cycles
                    autoRunCycles = 100
                    print("Setting autorun cycles to 100...")
                    doNextTurn = True

                # Manual "run for 500 cycles"
                elif (keys[pygame.K_9]):
                    # Run for 500 cycles
                    autoRunCycles = 500
                    print("Setting autorun cycles to 500...")
                    doNextTurn = True

                # Test the text message queue
                elif (keys[pygame.K_5]):
                    # Test the text message queue
                    ui.addTextMessageToQueue("This is a test\nThis is an extra long line apple orange banana pineapple fruit flower tree coconut sky water air summer water blue green yellow orange purple this is the end of the second line.\nThis is the second line.")



        # Rendering

        # Fill the window with black
        window.fill((0, 0, 0))

        # Update the world
        # If the agent has taken their turn, then update the world
        if (doNextTurn) or (autoRunCycles > 0):
            # Update the world
            world.tick()

            # Report task progress
            print( world.taskScorer.taskProgressStr() )




            frames += 1
            print("\n\n############################################################################################")
            if (autoRunCycles > 0):
                print("Step: " + str(frames) + " (autorun)")
            else:
                print("Step: " + str(frames))

            # Print current memory usage
            curSize = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
            delta = curSize - lastSize
            print("Current memory usage: " + str( curSize ) + " MB      (delta: " + str(delta) + " MB)")
            lastSize = curSize

            # Show all discovery feed posts
            print("Discovery feed:")
            for post in world.discoveryFeed.updatePosts:
                print(post)


            # Dump the world history to a JSON file
            # prevStep = world.step - 1
            # filenameOut = "history/worldHistory." + str(prevStep) + ".json"
            # with open(filenameOut, 'w') as outfile:
            #     # Get the last step of the world history (requires decompressing)
            #     lastHistoryStep= world.getWorldHistoryAtStep(world.step-1)
            #     if (lastHistoryStep != None):
            #         json.dump(lastHistoryStep, outfile, indent=4, cls=CustomJSONEncoder)

            ## Debug: dump the world history to a JSON file
            ## filenameWorldHistoryOut = "sandbox/worldHistory.pickle"
            ## world.exportWorldHistory(filenameWorldHistoryOut)

            # Test out the knowledge scorer
            print("--------------------")

            knowledgeScorer = currentAgent.knowledgeScorer
            # Create a measurement
    #         jsonStr = """
    # {
    #     "object": {"objectUUID": 1234, "scope":[{"propertyName":"color", "propertyOperator":"equals", "propertyValue":"red"}, {"propertyName":"size", "propertyOperator":"less_than", "propertyValue":5}]},
    #     "property": {"propertyName":"color", "propertyOperator":"equals", "propertyValue":"blue"}
    # }
    #     """
            jsonStr = """
    {
        "object": {"objectType": "mushroom", "scope":[]},
        "property": {"propertyName":"color", "propertyOperator":"equals", "propertyValue":"red"}
    }
        """

            # Convert to a dictionary
            dictIn = json.loads(jsonStr)
            # Create a Measurement
            measurement = Measurement(dictIn, step=world.step-1)
            print(measurement.errors)
            print(measurement)
            # Score the measurement
            score = knowledgeScorer.evaluateMeasurement(measurement)
            print("Score: " + str(score))
            print("Score justification: " + str(measurement.scoreJustification))

            print("############################################################################################\n")
            #time.sleep(0.25)


            if (autoRunCycles > 0):
                autoRunCycles -= 1

            exportFrame = True



        # Render the world
        #world.render(window, cameraX=0, cameraY=0)

        # Render a viewport centered on the agent
        # def renderViewport(self, window, worldStartX, worldStartY, sizeTilesX, sizeTilesY, offsetX, offsetY):
        # Step 1: Get the agent's location
        agentLocation = currentAgent.getWorldLocation()


        # Step 3: Determine the worldStartX and worldStartY coordinates
        worldStartX = agentLocation[0] - int(viewportSizeX / 2)
        worldStartY = agentLocation[1] - int(viewportSizeY / 2)
        # Step 4: Render the viewport
        world.renderViewport(window, worldStartX, worldStartY, viewportSizeX, viewportSizeY, 0, 0, scale=1.0)
        # Step 5: Render the user interface
        ui.render()


        # # Find a usable item at the location the agent is facing
        # facingLocation = currentAgent.getWorldLocationAgentIsFacing()
        # # Bound checking
        # if (world.isWithinBounds(facingLocation[0], facingLocation[1])):
        #     # Get objects at location
        #     objs = world.getObjectsAt(facingLocation[0], facingLocation[1])
        #     # Step 6: Display the object inventory box
        #     ui.renderObjectSelectionBox(objs, curSelectedObjIdx=2)

        #     print("List of objects the agent is facing: " + str(objs))


        # Save the screen frame to a file
        if (exportFrame):
            frameFilename = FRAME_DIR + "/frame_" + str(frames) + ".png"
            pygame.image.save(window, frameFilename)
            time.sleep(0.10)

        # Display the sprite
        #world.spriteLibrary.renderSprite(window, "house1_wall1", 100, 100)

        # Flip the backbuffer
        pygame.display.flip()
        #frames += 1

        #time.sleep(1)

    # If we get here, the game loop is over.
    # Convert the frames to a video
    print("Converting frames to video...")
    # Call FFMPEG (forces overwrite)
    #subprocess.call(["ffmpeg", "-y", "-framerate", "10", "-i", FRAME_DIR + "/frame_%d.png", "-c:v", "libx264", "-profile:v", "high", "-crf", "20", "-pix_fmt", "yuv420p", "output.mp4"])


    # Print the action history of the farmer agent
    #print("Farmer agent action history:")
    #print(npcFarmer.actionHistory)

# Main
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Play DiscoveryWorld.")
    parser.add_argument('--scenario', choices=SCENARIOS, default=SCENARIOS[0])

    args = parser.parse_args()

    # Main function
    main(args)

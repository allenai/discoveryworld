
import argparse
import pygame
import os
import json
import time
import psutil
import textwrap
from os.path import join as pjoin

from discoveryworld.ActionSuccess import MessageImportance
from discoveryworld.KnowledgeScorer import Measurement
from discoveryworld.UserInterface import UserInterface
from discoveryworld.ScenarioMaker import ScenarioMaker, SCENARIOS

from discoveryworld.World import World
from discoveryworld.constants import ASSETS_PATH


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


def dialogPickOption(window, options:list, displayMessage:str=None):
    # Initialize Pygame fonts
    pygame.font.init()
    font = pygame.font.SysFont("monospace", 15)
    fontBold = pygame.font.SysFont("monospace", 15, bold=True)

    # Main loop
    running = True
    currentOption = 0
    arrowKeyDown = False
    while running:
        # Clear the event queue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Quit the game
                pygame.quit()

            if (event.type == pygame.KEYDOWN):
                # Use arrow keys to select options (up/down).  Should move once when key is pressed, then reset when key is released
                if (event.key == pygame.K_UP):
                    if (arrowKeyDown == False):
                        currentOption -= 1
                        if (currentOption < 0):
                            currentOption = len(options) - 1
                        arrowKeyDown = True
                if (event.key == pygame.K_DOWN):
                    if (arrowKeyDown == False):
                        currentOption += 1
                        if (currentOption >= len(options)):
                            currentOption = 0
                        arrowKeyDown = True
                # Pressing RETURN will select the current option
                if (event.key == pygame.K_RETURN):
                    running = False

                # Pressing ESC will quit the dialog, returning NONE
                if (event.key == pygame.K_ESCAPE):
                    return None

            if (event.type == pygame.KEYUP):
                arrowKeyDown = False


        # Clear screen (optional, depends on design)
        window.fill((0, 0, 0))

        # Show DiscoveryWorld Logo at the top
        # For now, just draw this in a large font

        # Display the DiscoveryWorld logo
        # Load the logo image
        logoImage = pygame.image.load(pjoin(ASSETS_PATH, "logo", "logo.png"))
        logoRect = logoImage.get_rect()
        logoRect.center = (window.get_width() // 2, 120)
        window.blit(logoImage, logoRect)

        # Display text message, centered, at 150 pixels down from the top of the screen
        if (displayMessage != None):
            textMessage = fontBold.render(displayMessage, True, (200, 200, 200))
            textRect = textMessage.get_rect()
            textRect.center = (window.get_width() // 2, 250)
            window.blit(textMessage, textRect)

        # Also display a message at the bottom to indicate how to select an option
        textMessage = fontBold.render("Use the arrow keys to scroll between options, and press RETURN to select an option.", True, (200, 200, 200))
        textRect = textMessage.get_rect()
        textRect.center = (window.get_width() // 2, window.get_height() - 50)
        window.blit(textMessage, textRect)

        # Display the options
        for i, optionStr in enumerate(options):
            # Background -- grey if not current option, blue if current option
            # All options should be centered

            textOption = fontBold.render(optionStr, True, (200, 200, 200))
            textRect = textOption.get_rect()
            textRect.center = (window.get_width() // 2, 300 + (i * 40))

            # Draw the background rectangle
            # This should be a new rectangle, that's at least 300 pixels wide, and centered on the same center
            backgroundRect = pygame.Rect(textRect.left - 5, textRect.top - 5, textRect.width + 10, textRect.height + 10)
            # Make at least 300 pixels wide
            if (backgroundRect.width < 300):
                backgroundRect.width = 300
                backgroundRect.left = textRect.center[0] - 150

            if (i == currentOption):
                pygame.draw.rect(window, (0, 0, 200), (backgroundRect.left - 5, backgroundRect.top - 5, backgroundRect.width + 10, backgroundRect.height + 10))
            else:
                pygame.draw.rect(window, (100, 100, 100), (backgroundRect.left - 5, backgroundRect.top - 5, backgroundRect.width + 10, backgroundRect.height + 10))

            # Draw the background text, centered
            window.blit(textOption, textRect)


        # Update the display
        pygame.display.flip()

    # Clean up pygame
    #pygame.quit()

    pass


def pickScenario(window):
    # Initialize Pygame fonts
    pygame.font.init()
    font = pygame.font.SysFont("monospace", 15)
    fontBold = pygame.font.SysFont("monospace", 15, bold=True)

    options = ["Combinatorial Chemistry", "Archaeology Dating", "Plant Nutrients", "Reactor Lab", "Lost in Translation", "Space Sick", "TODO 1", "TODO 2"]
    result = dialogPickOption(window, options, displayMessage="Select a scenario:")

    # Clean up pygame
    #pygame.quit()



    pass


def main(args):
    print("Initializing...")
    displayGrid = args.debug

    # 32 pixels/tile * 32 tiles = 1024 pixels

    windowMode = "small"
    #windowMode = "big"

    # Game parameters
    if windowMode == "small":
        gameParams = {
            "height": 750,
            "width": 800,
            "fps": 60,
            "name": "DiscoveryWorld"
        }

        # Step 2: Define the viewport size (in tiles)
        viewportSizeX = 24
        viewportSizeY = 16

    elif windowMode == "big":
        gameParams = {
            "height": 1024,
            "width": 1024,
            "fps": 30,
            "name": "DiscoveryWorld"
        }

        # Step 2: Define the viewport size (in tiles)
        viewportSizeX = 32
        viewportSizeY = 32

    scale = 1.0
    # if os.environ.get("MARC", False):
    #     scale = 2.0
    #     viewportSizeX //= 2
    #     viewportSizeY //= 2


    # Open window
    #window = pygame.display.set_mode((gameParams["width"], gameParams["height"]))
    # Open window (should open in top left corner)
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50,50)
    window = pygame.display.set_mode((gameParams["width"], gameParams["height"]))
    pygame.display.set_caption(gameParams["name"])

    clock = pygame.time.Clock()

    # Initialize font renderer
    pygame.font.init()

    # Show the screen to pick the scenario
    pickScenario(window)

    # Intialize world
    world = World(assetPath=None, filenameSpriteIndex="spriteIndex.json", dataPath=None, filenameObjectData="objects.tsv", filenameMaterialData="materials.tsv", filenameDiscoveryFeed="discoveryFeed.json")
    print ("All sprite names: ")
    print (world.spriteLibrary.getSpriteNames())

    # Initialize the user interface
    ui = UserInterface(window, world.spriteLibrary)

    # Create a new random number generator (for deterministic behavior) with a specific seed
    #r = random.Random()

    scenarioMaker = ScenarioMaker(world, seed=args.seed)
    smSuccess, smErrorStr = scenarioMaker.setupScenario(args.scenario)
    if (not smSuccess):
        print("ERROR: ScenarioMaker failed to setup scenario: " + smErrorStr)
        exit(1)

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
    taskCompletedMessageShown = False
    confirmingQuit = False

    while running:
        #print("Frame: " + str(frames))
        exportFrame = False

        curTime = time.time()
        clock.tick(gameParams["fps"])

        # Check for a quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Check whether the task has been completed -- and if so, show a message
        tasks = world.taskScorer.tasks
        task = None
        if (len(tasks) > 0):
            task = tasks[0]
            if (task.isCompleted() == True) and (taskCompletedMessageShown == False):
                taskCompletedMessageShown = True
                taskCompletedMessage = "THE GAME HAS COMPLETED.\n"
                if (task.isCompletedSuccessfully() == True):
                    taskCompletedMessage += "Congratulations! You have successfully completed the task successfully.\n"
                else:
                    taskCompletedMessage += "Unfortunately, the task was not completed successfully.\n"
                taskCompletedMessage += "\n"
                taskCompletedMessage += "Task Description:\n"
                taskCompletedMessage += textwrap.fill(task.taskDescription, 80) + "\n\n"

                taskScore = int(task.getScoreNormalized() * 100)
                taskCompletedMessage += "Task Score: " + str(taskScore) + "%\n"
                taskCompletedMessage += "\n"
                taskCompletedMessage += "Press SPACE to close this message. Press ESC to quit the game."

                ui.addTextMessageToQueue(taskCompletedMessage)


        # Check for keyboard input
        keys = pygame.key.get_pressed()

        # Signify whether the agent has done their move this turn
        doNextTurn = False
        if (ui.inModal):
            # # Pressing any key will close the modal
            # if (keys[pygame.K_SPACE] or keys[pygame.K_RETURN]):
            #     ui.closeModal()
            #     doNextTurn = True

            # If a 'quit confirm' modal is open, then pressing 'Y' will quit the game
            if (confirmingQuit == True):
                # Quit modal
                if (keys[pygame.K_y]):
                    running = False
                if (keys[pygame.K_n]):
                    ui.closeModal()
                    confirmingQuit = False
                    time.sleep(0.50)     # wait for half a second for the key to be released
                    # Flush the key buffer
                    pygame.event.clear()

            else:
                # General moedel: Pressing SPACE or RETURN will close the modal
                if (keys[pygame.K_SPACE] or keys[pygame.K_RETURN]):
                    ui.closeModal()
                    doNextTurn = True


        else:
            # Escape -- quits the game
            if (keys[pygame.K_ESCAPE]):
                ui.addTextMessageToQueue("Are you sure you want to quit the game?\nY - Quit\nN - Continue")
                confirmingQuit = True

            # Parse any action keys
            doTick = True
            success = None
            if (taskCompletedMessageShown == False):
                # Only parse action keys if the task has not been completed
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

                if (keys[pygame.K_g]):
                    displayGrid = not displayGrid
                    doNextTurn = True
                    success = True

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


                # # Manual "run for 100 cycles"
                # elif (keys[pygame.K_0]):
                #     # Run for 100 cycles
                #     autoRunCycles = 100
                #     print("Setting autorun cycles to 100...")
                #     doNextTurn = True

                # # Manual "run for 500 cycles"
                # elif (keys[pygame.K_9]):
                #     # Run for 500 cycles
                #     autoRunCycles = 500
                #     print("Setting autorun cycles to 500...")
                #     doNextTurn = True

                # Test the text message queue
                elif (keys[pygame.K_TAB]):
                    # Test the text message queue

                    #ui.addTextMessageToQueue("This is a test\nThis is an extra long line apple orange banana pineapple fruit flower tree coconut sky water air summer water blue green yellow orange purple this is the end of the second line.\nThis is the second line.")
                    #tasks = world.taskScorer.tasks
                    if (task is None):
                        ui.addTextMessageToQueue("Task Information:\n\nNo tasks are currently active.\n\nPress SPACE to close this message.")
                    else:
                        taskDescription = task.taskDescription
                        taskScore = int(task.getScoreNormalized() * 100)
                        isCompleted = task.isCompleted()
                        isCompletedSuccessfully = task.isCompletedSuccessfully()

                        # If the task description is longer than 80 characters, break it up into multiple lines
                        # Use a library to do this
                        #taskDescription = "This is a test of a long task description that will be split into multiple lines. This is a test of a long task description that will be split into multiple lines. This is a test of a long task description that will be split into multiple lines."
                        taskDescriptionWrapped = textwrap.fill(taskDescription, 80)
                        taskStr = "Task Description:\n\n"
                        taskStr += taskDescriptionWrapped + "\n\n"
                        taskStr += "Task Score: " + str(taskScore) + "%\n"
                        taskStr += "Task Completed: " + str(isCompleted) + "\n"
                        taskStr += "Task Completed Successfully: " + str(isCompletedSuccessfully) + "\n\n"
                        taskStr += "Press SPACE to close this message."

                        # Add the task information to the text message queue
                        ui.addTextMessageToQueue(taskStr)

                # Help Screen (question mark/slash key)
                elif (keys[pygame.K_SLASH]) or (keys[pygame.K_QUESTION]):
                    # Display the help screen
                    helpStr = "DiscoveryWorld Help\n\n"
                    helpStr += "Arrow keys: Move the agent\n"
                    helpStr += "TAB:   View current task information\n"
                    helpStr += "SPACE: Pick up object (in Arg 1 slot)\n"
                    helpStr += "D:     Drop inventory item (in Arg 1 slot)\n"
                    helpStr += "P:     Put an item (Arg 1) in a specific container (Arg 2)\n"
                    helpStr += "O/C:   Open/close a container (in Arg 1 slot)\n"
                    helpStr += "A/S:   Activate/deactive a device (in Arg 1 slot)\n"
                    helpStr += "T:     Talk to another character (in Arg 1 slot)\n"
                    helpStr += "E:     Eat an item (in Arg 1 slot)\n"
                    helpStr += "U:     Use an item (Arg 1), optionally on another item (Arg 2)\n"
                    helpStr += "Z:     Teleport to a random important location\n"
                    helpStr += "W:     Wait a step (do nothing)\n"
                    helpStr += "[ / ]: Cycle through inventory items (Arg 1)\n"
                    helpStr += "; / \": Cycle through inventory items (Arg 2)\n"
                    helpStr += "?:     Display this help message\n"
                    helpStr += "ESC:   Quit the game\n"
                    helpStr += "\n"
                    helpStr += "Example: To 'use the shovel on the soil':\n"
                    helpStr += " - Use [ and/or ] keys to select the shovel (arg 1)\n"
                    helpStr += " - Use ; and/or \" keys to select the soil (arg 2)\n"
                    helpStr += " - Press U to use the shovel on the soil.\n"
                    helpStr += "\n"
                    helpStr += "Press SPACE to close this message."

                    # Add the help message to the text message queue
                    ui.addTextMessageToQueue(helpStr)







        # Rendering

        # Fill the window with black
        window.fill((0, 0, 0))

        # Update the world
        # If the agent has taken their turn, then update the world
        if (doNextTurn) or (autoRunCycles > 0):
            # Update the world

            # If the task is completed, then the world will not tick
            if (task is None) or (task.isCompleted() == False):
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

        world.renderViewport(window, worldStartX, worldStartY, viewportSizeX, viewportSizeY, 0, 0, scale=scale, includeGrid=displayGrid)
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

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Play DiscoveryWorld.")
    parser.add_argument('--scenario', choices=SCENARIOS, default=SCENARIOS[0])
    parser.add_argument('--seed', type=int, default=20240404)
    parser.add_argument('--debug', action="store_true")

    args = parser.parse_args()

    print("Starting DiscoveryWorld...")
    print("Scenario: " + args.scenario)
    print("Seed: " + str(args.seed))

    main(args)

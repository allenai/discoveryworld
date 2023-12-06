# UserInterface.py

import pygame
import SpriteLibrary
from Layer import Layer
from ObjectModel import Object
from Agent import Agent
from ActionSuccess import *
import random
import math

#ActionSuccess




class UserInterface:
    # Constructor
    def __init__(self, window, spriteLibrary):
        # Fonts
        self.font = pygame.font.SysFont("monospace", 15)
        self.fontBold = pygame.font.SysFont("monospace", 15, bold=True)

        # Window
        self.window = window
        # Sprite library
        self.spriteLibrary = spriteLibrary
        # Current agent and related values
        self.currentAgent = None
        self.curSelectedInventoryIdx = 0

        # Most recent action result/message (to place on the bottom of the UI)
        self.lastActionMessage = ""

        # Queue of messages to display
        self.messageQueueText = []

        # Dialog to display, if any
        self.dialogToDisplay = None

        # Status
        self.inModal = False

        # What spot in the argument boxes is currently selected
        self.curSelectedArgument1Idx = 0        
        self.curSelectedArgument2Idx = 0
        self.curSelectedArgument1Obj = None
        self.curSelectedArgument2Obj = None

        self.argObjectsList = []        # The (most recently updated) list of all objects that can be selected as arguments
    
    
    # Set the agent
    def setAgent(self, agent):
        self.currentAgent = agent


    #
    #   Message queue
    #
    def addTextMessageToQueue(self, message):
        self.messageQueueText.append(message)

    def popMessageFromQueue(self):
        if (len(self.messageQueueText) > 0):
            self.messageQueueText.pop(0)


    # Close whatever modal is currently active
    def closeModal(self):
        self.popMessageFromQueue()


    # Update last action message
    def updateLastActionMessage(self, messageStr):
        self.lastActionMessage = messageStr


    # 
    #   Argument boxes
    #

    def updateArgumentObjects(self, objList):
        self.argObjectsList = objList

    def changeArgumentBox(self, delta, whichBox):
        # Increment/decrement box
        if (whichBox == 1):
            self.curSelectedArgument1Idx += delta            
        elif (whichBox == 2):
            self.curSelectedArgument2Idx += delta
        else:
            print("ERROR: Invalid argument box: " + str(whichBox))
            exit(1)

        # Bound checking
        if (self.curSelectedArgument1Idx < 0):
            self.curSelectedArgument1Idx = 0
        elif (self.curSelectedArgument1Idx >= len(self.argObjectsList)):
            self.curSelectedArgument1Idx = len(self.argObjectsList) - 1
        if (self.curSelectedArgument2Idx < 0):
            self.curSelectedArgument2Idx = 0
        elif (self.curSelectedArgument2Idx >= len(self.argObjectsList)):
            self.curSelectedArgument2Idx = len(self.argObjectsList) - 1

        # Update references to selected objects
        if (self.curSelectedArgument1Idx >= 0 and self.curSelectedArgument1Idx < len(self.argObjectsList)):
            self.curSelectedArgument1Obj = self.argObjectsList[self.curSelectedArgument1Idx]
        else:
            self.curSelectedArgument1Obj = None

        if (self.curSelectedArgument2Idx >= 0 and self.curSelectedArgument2Idx < len(self.argObjectsList)):
            self.curSelectedArgument2Obj = self.argObjectsList[self.curSelectedArgument2Idx]
        else:
            self.curSelectedArgument2Obj = None

        # Update the agent 'objectToShow' based on arg1
        if (self.currentAgent != None):
            self.currentAgent.updateLastInteractedObject([self.curSelectedArgument1Obj])

        
    #
    #   Rendering
    #

    def render(self):        
        # Reset the modal flag
        self.inModal = False

        # Step 1: Render the inventory        
        #self.renderInventory()

        # Step 1: Render argument boxes
        
        # Step 1A: First, collect all objects (inventory, objects in front of the agent)
        objsInv = []
        objsEnv = []
        if (self.currentAgent != None):
            objsInv = self.currentAgent.getInventory()
            objsEnv += self.currentAgent.getObjectsAgentFacing(respectContainerStatus=True)
        allObjs = objsInv + objsEnv

        # Update the list of objects that can be used as arguments
        self.updateArgumentObjects(allObjs)

        # Render argument 1 box
        if (self.curSelectedArgument1Idx >= len(allObjs)):
            self.curSelectedArgument1Idx = len(allObjs) - 1
        self.changeArgumentBox(delta=0, whichBox=1)     # Bound checking/Make sure the references to the selected objects are up to date
        self.renderObjectSelectionBox(objsInv, objsEnv, self.curSelectedArgument1Idx, offsetX=32, offsetY=-(32*9), labelPrefixStr="Arg 1: ")
        # Render argument 2 box
        if (self.curSelectedArgument2Idx >= len(allObjs)):
            self.curSelectedArgument2Idx = len(allObjs) - 1
        self.changeArgumentBox(delta=0, whichBox=2)     # Bound checking/Make sure the references to the selected objects are up to date
        self.renderObjectSelectionBox(objsInv, objsEnv, self.curSelectedArgument2Idx, offsetX=32, offsetY=-(32*6), labelPrefixStr="Arg 2: ")



        # TODO: Add the rest of the UI elements

        # Step 2: Render any pop-ups (e.g. dialog, or modals from the message queue)
        if (self.dialogToDisplay != None):
            # Pack the string
            # First, add what the NPC said
            dialogBoxStr = self.dialogToDisplay['dialogText'] + "\n\n"
            # Then, add the options the user can say back
            for idx, option in enumerate(self.dialogToDisplay['dialogOptions']):
                dialogBoxStr += str(idx+1) + ": " + option + "\n"

            # Render the dialog box
            self.renderTextBox(dialogBoxStr)
            # Not in a modal
            self.inModal = False            
            
        elif (len(self.messageQueueText) > 0):
            # Render the top message in the message queue
            nextMessage = self.messageQueueText[0]
            self.renderTextBox(nextMessage)            
            # Set the modal flag
            self.inModal = True

        
            

        # Render the last action message
        self.renderLastActionMessage()

        # Render the task progress
        if (self.currentAgent != None):
            taskList = self.currentAgent.world.taskScorer.tasks
            for idx, task in enumerate(taskList):
                # x should be 200 from the right
                # y should start 100 from the bottom
                x = self.window.get_width() - 200
                y = self.window.get_height() - 120
                self.renderTaskProgress(x, y, task)
                                
        pass


    
    #
    #   User interface elements
    #
    
    def renderTaskProgress(self, x, y, task):
        # Write the task name and normalized score (0-1).
        # The background color is based on the task score -- red for 0, green for 1, and a gradient in between.
        taskName = task.taskName
        taskScore = task.getScoreNormalized()

        # Draw the background
        # First, get the color
        color = (0, 0, 0)
        if (taskScore == 0):
            color = (255, 0, 0)
        elif (taskScore == 1):
            color = (0, 255, 0)
        else:
            color = (int(255 * (1-taskScore)), int(255 * (taskScore)), 0)
        # Then, draw the background
        pygame.draw.rect(self.window, color, (x, y, 200, 20))

        # Draw the text
        # First, get the text
        text = taskName + ": " + str(taskScore)
        # Then, render the text
        textSurface = self.font.render(text, True, (0, 0, 0))
        self.window.blit(textSurface, (x, y))



    # Render a long section of boxes at the bottom of the screen that show items in the agent's inventory
    def renderInventory(self):
        offsetX = 32        
        offsetY = -32
        
        # If no agent is currently selected, then exit
        if (self.currentAgent == None):
            return

        # Get the agent's inventory
        inventory = self.currentAgent.getInventory()
        
        # Render the inventory
        scale = 2.0
        inventorySlots = 10
        tileSize = 32

        for idx in range(inventorySlots):
        #for idx, item in enumerate(inventory):
            item = None
            if (idx < len(inventory)):
                item = inventory[idx]

            # Get the X and Y coordinates of the inventory box (starting from the bottom left corner)            
            x = idx * (32 * scale) + offsetX
            y = self.window.get_height() - (32 * scale) + offsetY
                        
            # First, draw a box around this sprite area
            #pygame.draw.rect(self.window, (128, 128, 128), (x, y, 32 * scale, 32 * scale), 1)
            if (idx == self.curSelectedInventoryIdx):
                self.spriteLibrary.renderSprite(self.window, "ui_inventory_selected", x, y - tileSize, scale)
            else:
                self.spriteLibrary.renderSprite(self.window, "ui_inventory_background", x, y - tileSize, scale)

            # Next, draw the sprite
            if (item != None):                
                self._renderObjectSprite(item, x, y - tileSize, scale)
            
            # Add a number to the box            
            label = self.fontBold.render(str(idx + 1), 1, (255, 255, 255))
            self.window.blit(label, (x + 2, y + 2))

            
    # Helper to render an object's sprite(s) at a given x/y location
    def _renderObjectSprite(self, object, x, y, scale=1.0):
        for spriteName in object.getSpriteNamesWithContents():
            self.spriteLibrary.renderSprite(self.window, spriteName, x, y, scale, adjustY=True)


    # Render a box that shows (graphically) a set of objects the agent might select from.  
    # Should look similar to the inventory box, only with the potential to hold more objects. 
    def renderObjectSelectionBox(self, objsInv, objsEnv, curSelectedObjIdx, offsetX, offsetY, labelPrefixStr=""):
        # The object selection box is a single row with 10 columns.  If there are more than 10 objects, then the user can scroll through them.        
        objectList = objsInv + objsEnv
        numObjs = len(objectList)
        numCols = 10        

        # Start rendering the grid (centered on the lower half of the viewport)
        scale = 2.0
        scale1 = 1.5
        tileSize = 32        
        #offsetX = 32
        #offsetY = -32 * 10
        
        xAdj = ((tileSize*scale) - (tileSize*scale1))/2
        yAdj = ((tileSize*scale) - (tileSize*scale1))/2

        # Bound checking on the selected object index

        # Calculate the starting and ending object indices (total window size should be 10).            
        startIdx = 0
        if (curSelectedObjIdx > 5):
            startIdx = curSelectedObjIdx - 5
        endIdx = startIdx + 10
        if (endIdx > numObjs):
            endIdx = numObjs
            startIdx = endIdx - 10
            if (startIdx < 0):
                startIdx = 0
                
        objIdx = startIdx        
        # For each column
        for col in range(numCols):
            # Get the X and Y coordinates of the inventory box (starting from the bottom left corner)
            x = col * (32 * scale) + offsetX            
            y = self.window.get_height() + offsetY + (tileSize * scale)

            # Display the background sprite
            if (objIdx == curSelectedObjIdx):
                self.spriteLibrary.renderSprite(self.window, "ui_inventory_selected", x, y, scale)
            else:
                if (objIdx >= len(objectList)):
                    # Empty inventory spot
                    self.spriteLibrary.renderSprite(self.window, "ui_inventory_empty", x, y, scale)
                elif (objIdx >= len(objsInv)):
                    # Environmental inventory spot (slightly different background)
                    self.spriteLibrary.renderSprite(self.window, "ui_inventory_background_env", x, y, scale)
                else:
                    # Inventory spot                    
                    self.spriteLibrary.renderSprite(self.window, "ui_inventory_background", x, y, scale)

            # Display the object's sprite                
            if (objIdx < endIdx):
                obj = objectList[objIdx]
                #print("Object " + str(objIdx) + " name: " + obj.name + "  Sprite name: " + obj.getSpriteName())
                #self._renderObjectSprite(obj, x+xAdj, y+yAdj, scale=scale1)
                self._renderObjectSprite(obj, x+xAdj, y + tileSize - yAdj, scale=scale1)

            # Display the number
            label = self.fontBold.render(str(objIdx + 1), 1, (255, 255, 255))
            self.window.blit(label, (x + 4, y + (tileSize * scale) - 24))

            # Increment the object index
            objIdx += 1

        # Render the selected object's name
        selectedObjectName = ""
        if (curSelectedObjIdx < len(objectList)):
            selectedObjectName = objectList[curSelectedObjIdx].name        

        # Render the name above the box
        x = 0 * (32 * scale) + offsetX            
        y = self.window.get_height() + offsetY + (tileSize * scale)
        label = self.fontBold.render(labelPrefixStr + selectedObjectName, 1, (255, 255, 255))
        self.window.blit(label, (x+4, y + (tileSize * scale) - 48))

        pass


    # Split a line of text into multiple lines, if it exceeds a maximum length
    def _splitLongTextLines(self, line, MAX_LENGTH=80):        
        lines = []

        curLine = line
        while (True):
            # Get the length of whatever is remaining
            length = len(curLine)

            # If it's less than the maximum length, add it to the list of lines, then exit
            if (length <= MAX_LENGTH):
                lines.append(curLine)
                break

            # Otherwise, find the last space before the maximum length
            spaceIdx = curLine.rfind(" ", 0, MAX_LENGTH)
            if (spaceIdx != -1):
                # Add the line up to the space to the list of lines
                lines.append(curLine[:spaceIdx])

                # Remove the line up to the space
                curLine = curLine[spaceIdx+1:]

            else:
                # No space found. Just add the line up to the maximum length to the list of lines
                lines.append(curLine[:MAX_LENGTH])

                # Remove the line up to the maximum length
                curLine = curLine[MAX_LENGTH:]
        
        return lines



    # Render a multi-line text box
    def renderTextBox(self, text):
        # The text can be multiple lines. Each line is separated by a newline character.
        # Automatically clip any lines with more than 80 characters by adding a newline character at the first space before the 80th character.
        lines = text.split("\n")        
        linesToRender = []
        for line in lines:
            linesToRender.extend(self._splitLongTextLines(line))        

        # Text box should be centered in X, and 1/3 of the way down the screen in Y
        x = self.window.get_width() / 2
        y = self.window.get_height() / 3
        # Calculate total height of the text box
        totalHeight = len(linesToRender) * 16
        # Calculate total width of the text box
        totalWidth = 0
        for line in linesToRender:
            width, height = self.fontBold.size(line)
            if (width > totalWidth):
                totalWidth = width

        # Draw the background
        startX = x - (totalWidth / 2)
        startY = y - (totalHeight / 2)
        pygame.draw.rect(self.window, (128, 128, 128), (startX-16, startY-16, totalWidth + 32, totalHeight + 32), 0)

        # Render each line
        for idx, line in enumerate(linesToRender):
            label = self.fontBold.render(line, 1, (255, 255, 255))
            self.window.blit(label, (startX, startY + (idx * 16)))

        pass
    

    # Render the last action message, as a (maximum) single line message at the bottom of the screen. 
    # If the message is too long, it will be truncated.
    def renderLastActionMessage(self):
        # If the last action message is empty, don't render anything
        if (self.lastActionMessage == ""):
            return

        # Replace newlines with spaces, to merge the message into a single line        
        oneLine = self.lastActionMessage.replace("\n", " ")
        lines = self._splitLongTextLines(oneLine, MAX_LENGTH=80)
        lineToWrite = lines[0]

        # Render the first line
        x = 32
        y = self.window.get_height() - 24
        # Render the background
        width, height = self.fontBold.size(lineToWrite)
        fontSize = 15
        pygame.draw.rect(self.window, (128, 128, 128), (x, y, width, height), 0)
        # Render the text
        label = self.fontBold.render(lineToWrite, 1, (255, 255, 255))
        self.window.blit(label, (x, y))


    #
    # Action abstraction layer
    #


    # Move actions (forward/backward, rotate clockwise/counterclockwise)
    def actionMoveAgentForward(self):
        success = self.currentAgent.actionMoveAgentForwardBackward(direction=+1)
        return success
    
    def actionMoveAgentBackward(self):
        success = self.currentAgent.actionMoveAgentForwardBackward(direction=-1)
        return success

    def actionRotateAgentClockwise(self):
        success = self.currentAgent.actionRotateAgentFacingDirection(direction=+1)
        return success

    def actionRotateAgentCounterclockwise(self):
        success = self.currentAgent.actionRotateAgentFacingDirection(direction=-1)
        return success

    
    # Pick up an object
    def actionPickupObject(self, objToPickUp):
        success = self.currentAgent.actionPickUp(objToPickUp)
        return success

    # Put an object in a specific container
    def actionPutObjectInContainer(self, objToPut, container):        
        success = self.currentAgent.actionPut(objToPut, container)
        return success

    # Drop an object at the current location
    def actionDropObject(self, objToDrop):
        success = self.currentAgent.actionDrop(objToDrop)
        return success


    # Open/Close an object
    def actionOpenObject(self, objToOpen):
        success = self.currentAgent.actionOpenClose(objToOpen, "open")
        return success

    def actionCloseObject(self, objToClose):
        success = self.currentAgent.actionOpenClose(objToClose, "close")
        return success


    # Activate/Deactivate
    def actionActivateObject(self, objToActivate):
        success = self.currentAgent.actionActivateDeactivate(objToActivate, "activate")
        return success

    def actionDeactivateObject(self, objToDeactivate):
        success = self.currentAgent.actionActivateDeactivate(objToDeactivate, "deactiviate")
        return success


    # Talk/Dialog
    def actionTalk(self, agentToTalkTo):
        # TODO: Add checks to make sure agentToTalkTo is an agent (and not just an object)
        success = self.currentAgent.actionDialog(agentToTalkTo = agentToTalkTo, dialogStrToSay = "Hello!")
        return success

    # Eat an object
    def actionEat(self, objToEat):
        success = self.currentAgent.actionEat(objToEat)
        return success

    # Read an object
    def actionRead(self, objToRead):
        success = self.currentAgent.actionRead(objToRead)
        return success

    # Use an object (with another object)
    def actionUse(self, objToUse, objToUseWith):
        success = self.currentAgent.actionUse(objToUse, objToUseWith)
        return success


    # DiscoveryFeed actions
    def getDiscoveryFeedUpdates(self):
        # Show the last 10 updates        
        success = self.currentAgent.actionDiscoveryFeedGetPosts()
        return success        

    def getDiscoveryFeedArticles(self):
        # Show the last 10 articles
        success = self.currentAgent.actionDiscoveryFeedGetArticleTitles()
        return success
    
    def getSpecificDiscoveryFeedPost(self, postID):
        # Show the post with the given ID
        success = self.currentAgent.actionDiscoveryFeedGetByID(postID)
        return success


    #
    #   Action Parser (keys)
    #

    def _parseDialogKeys(self, keys):
        # If we're in the middle of a dialog, we need to parse the dialog keys
        # Valid keys are 0-9. 
        # 0-9: Select the corresponding dialog option
        # ESC: Cancel the dialog
        
        # If the agent is not in a dialog, then return
        if (self.currentAgent.isInDialog() == False):
            return ActionSuccess(success=False, message="Agent is not in a dialog.")

        # First, get an integer representing which key was pressed (0-9).  If it wasn't in that range, then set to -1
        key = -1
        if (keys[pygame.K_0]):
            key = 0
        elif (keys[pygame.K_1]):
            key = 1
        elif (keys[pygame.K_2]):
            key = 2
        elif (keys[pygame.K_3]):
            key = 3
        elif (keys[pygame.K_4]):
            key = 4
        elif (keys[pygame.K_5]):
            key = 5
        elif (keys[pygame.K_6]):
            key = 6
        elif (keys[pygame.K_7]):
            key = 7
        elif (keys[pygame.K_8]):
            key = 8
        elif (keys[pygame.K_9]):
            key = 9
        elif (keys[pygame.K_ESCAPE]):
            # Exit the dialog
            self.currentAgent.exitDialog()

        # Get the current dialog options from the dialog tree
        agentInDialogWith = self.currentAgent.getAgentInDialogWith()
        # Get current node in dialog tree
        npcResponse, nextDialogOptions = agentInDialogWith.dialogTree.getCurrentDialog()

        # If the key is not in range, do nothing
        if (key < 1 or key > len(nextDialogOptions)):
            return (False, ActionSuccess(success=False, message="Unknown dialog option."))

        # If the key is in range, then select that dialog option
        selectedDialogOption = nextDialogOptions[key-1]

        # Say that response back to the NPC
        actionResult = self.currentAgent.actionDialog(agentToTalkTo = agentInDialogWith, dialogStrToSay = selectedDialogOption)

        # Also note that if the new dialog tree state has no options, then we need to exit the dialog. 
        npcResponse, nextDialogOptions = agentInDialogWith.dialogTree.getCurrentDialog()
        self.dialogToDisplay = {}
        self.dialogToDisplay['dialogText'] = npcResponse
        self.dialogToDisplay['dialogOptions'] = nextDialogOptions

        if (len(nextDialogOptions) == 0):
            self.currentAgent.exitDialog()

        return (True, actionResult)


        

    # returns (doTick, success)
    def parseKeys(self, keys):
        # First, check if we're in the middle of a dialog
        if (self.currentAgent.isInDialog()):
            # If so, we need to parse the dialog keys
            print("### IS IN DIALOG")
            return self._parseDialogKeys(keys)
        else:
            self.dialogToDisplay = None
        
        # Move the agent forward
        if (keys[pygame.K_UP]):            
            return (True, self.actionMoveAgentForward())

        # Move the agent backward
        elif (keys[pygame.K_DOWN]):            
            return (True, self.actionMoveAgentBackward())

        # Rotate the agent counterclockwise
        elif (keys[pygame.K_LEFT]):            
            return (True, self.actionRotateAgentCounterclockwise())

        # Rotate the agent clockwise
        elif (keys[pygame.K_RIGHT]):            
            return (True, self.actionRotateAgentClockwise())


        # Pick-up Object in arg1 slot
        elif (keys[pygame.K_SPACE]):
            checkArgSuccess = self._checkArgs(actionName = "pick up object", arg1 = True, arg2 = False)
            if (checkArgSuccess == False):
                return (False, False)

            return (True, self.actionPickupObject(objToPickUp = self.curSelectedArgument1Obj)            )

        # Drop an inventory item in arg1 slot at the agents current location
        elif (keys[pygame.K_d]):        
            checkArgSuccess = self._checkArgs(actionName = "drop item", arg1 = True, arg2 = False)
            if (checkArgSuccess == False):
                return (False, False)

            return (True, self.actionDropObject(objToDrop = self.curSelectedArgument1Obj))

        # Put an item (arg1) in a specific container (arg2)
        elif (keys[pygame.K_p]):            
            checkArgSuccess = self._checkArgs(actionName = "put item in container", arg1 = True, arg2 = True)
            if (checkArgSuccess == False):
                return (False, False)

            return (True, self.actionPutObjectInContainer(objToPut = self.curSelectedArgument1Obj, container = self.curSelectedArgument2Obj))

        # Open a container or passage (arg1) 
        elif (keys[pygame.K_o]):
            checkArgSuccess = self._checkArgs(actionName = "open", arg1 = True, arg2 = False)
            if (checkArgSuccess == False):
                return (False, False)

            return (True, self.actionOpenObject(objToOpen = self.curSelectedArgument1Obj))
        
        # Close a container or passage (arg1)
        elif (keys[pygame.K_c]):
            checkArgSuccess = self._checkArgs(actionName = "close", arg1 = True, arg2 = False)
            if (checkArgSuccess == False):
                return (False, False)

            return (True, self.actionCloseObject(objToClose = self.curSelectedArgument1Obj))
        
        # Activate an object (arg1) 
        elif (keys[pygame.K_a]):
            checkArgSuccess = self._checkArgs(actionName = "activate", arg1 = True, arg2 = False)
            if (checkArgSuccess == False):
                return (False, False)

            return (True, self.actionActivateObject(objToActivate = self.curSelectedArgument1Obj))
            
        # For some read K_d doesn't work. 
        # Should be D key here
        # Deactivate an object (arg1)
        elif (keys[pygame.K_s]):            
            checkArgSuccess = self._checkArgs(actionName = "deactivate", arg1 = True, arg2 = False)
            if (checkArgSuccess == False):
                return (False, False)

            return (True, self.actionDeactivateObject(objToDeactivate = self.curSelectedArgument1Obj))
            
        # Dialog/talk with agent specified in arg1
        elif (keys[pygame.K_t]):
            checkArgSuccess = self._checkArgs(actionName = "talk", arg1 = True, arg2 = False)
            if (checkArgSuccess == False):
                return (False, False)

            actionResult = self.actionTalk(agentToTalkTo = self.curSelectedArgument1Obj)

            # If the agent is in dialog, then we need to display the dialog options
            if (self.currentAgent.isInDialog()):
                npcResponse, nextDialogOptions = self.currentAgent.getAgentInDialogWith().dialogTree.getCurrentDialog()
                self.dialogToDisplay = {}
                self.dialogToDisplay['dialogText'] = npcResponse
                self.dialogToDisplay['dialogOptions'] = nextDialogOptions

            return (True, actionResult)

        # Eat arg1
        elif (keys[pygame.K_e]):
            checkArgSuccess = self._checkArgs(actionName = "eat", arg1 = True, arg2 = False)
            if (checkArgSuccess == False):
                return (False, False)

            return (True, self.actionEat(objToEat = self.curSelectedArgument1Obj))

        # Read arg1
        elif (keys[pygame.K_r]):
            checkArgSuccess = self._checkArgs(actionName = "read", arg1 = True, arg2 = False)
            if (checkArgSuccess == False):
                return (False, False)

            return (True, self.actionRead(objToRead = self.curSelectedArgument1Obj))

        # Use action (use arg1 with arg2)
        elif (keys[pygame.K_u]):
            checkArgSuccess = self._checkArgs(actionName = "use object", arg1 = True, arg2 = True)
            if (checkArgSuccess == False):
                return (False, False)

            result = self.actionUse(objToUse = self.curSelectedArgument1Obj, objToUseWith = self.curSelectedArgument2Obj)

            # # If there is a .generatedItems populated in this result, then process it            
            # if ('generatedItems' in result.data):
            #     for item in result.data['generatedItems']:
            #         self.currentAgent.addObject(item)

            return (True, result)


        # UI element (incrementing argument boxes with [, ], ;, and ')
        elif (keys[pygame.K_LEFTBRACKET]):
            self.changeArgumentBox(delta=-1, whichBox=1)
            return (False, ActionSuccess(success=True, message="Changed argument box 1 to " + str(self.curSelectedArgument1Obj.name)))
            
        elif (keys[pygame.K_RIGHTBRACKET]):
            self.changeArgumentBox(delta=1, whichBox=1)
            return (False, ActionSuccess(success=True, message="Changed argument box 1 to " + str(self.curSelectedArgument1Obj.name)))
            
        elif (keys[pygame.K_SEMICOLON]):
            self.changeArgumentBox(delta=-1, whichBox=2)
            return (False, ActionSuccess(success=True, message="Changed argument box 2 to " + str(self.curSelectedArgument2Obj.name)))
            
        elif (keys[pygame.K_QUOTE]):
            self.changeArgumentBox(delta=1, whichBox=2)
            return (False, ActionSuccess(success=True, message="Changed argument box 2 to " + str(self.curSelectedArgument2Obj.name)))
            

        # DiscoveryFeed Actions
        elif (keys[pygame.K_v]):
            return (False, self.getDiscoveryFeedUpdates())
        elif (keys[pygame.K_b]):
            return (False, self.getDiscoveryFeedArticles())
        elif (keys[pygame.K_n]):
            # TODO: Randomly generate a post ID between 1 and 10 for now. But this needs to be changed to allow the user to specify a specific post they'd like.
            randPostID = math.floor(random.random() * 10) + 1            
            return (False, self.getSpecificDiscoveryFeedPost(postID=randPostID))



        # If we reach here, then no known key was pressed
        return (False, None)


    # Check the arguments for the current action, to make sure they're valid. 
    # Returns None if valid, and a failure ActionSuccess object if not valid
    def _checkArgs(self, actionName:str, arg1:bool, arg2:bool):
        # Both arguments are required
        if (arg1 and arg2):
            if (self.curSelectedArgument1Obj == None and self.curSelectedArgument2Obj == None):                
                return ActionSuccess(success=False, message="Action '" + actionName + "' requires two argument objects. Missing both arguments.")
            if (self.curSelectedArgument1Obj == None):
                return ActionSuccess(success=False, message="Action '" + actionName + "' requires two argument objects. Missing argument 1.")
            if (self.curSelectedArgument2Obj == None):
                return ActionSuccess(success=False, message="Action '" + actionName + "' requires two argument objects. Missing argument 2.")
        
        # Only argument 1 is required
        elif (arg1):
            if (self.curSelectedArgument1Obj == None):
                return ActionSuccess(success=False, message="Action '" + actionName + "' requires argument 1.")
        
        # Only argument 2 is required
        elif (arg2):
            if (self.curSelectedArgument2Obj == None):
                return ActionSuccess(success=False, message="Action '" + actionName + "' requires argument 2.")

        # If we reach here, the arguments should be valid
        return None


# UserInterface.py

import pygame
import SpriteLibrary
from Layer import Layer
from ObjectModel import Object
from Agent import Agent
from ActionSuccess import *
from ActionHistory import *
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

    # A JSON version of the user interface
    def renderJSON(self):
        # Out
        out = {}

        # Add agent location and facing direction
        agentLocation = {}
        agentLocation["x"] = self.currentAgent.attributes["gridX"]
        agentLocation["y"] = self.currentAgent.attributes["gridY"]
        agentLocation["faceDirection"] = self.currentAgent.attributes["faceDirection"]
        validDirections, blockedDirections = self.currentAgent.getValidDirectionsToMoveTo()
        agentLocation["directions_you_can_move"] = validDirections
        agentLocation["directions_blocked"] = blockedDirections
        out.update({"agentLocation": agentLocation})

        # Add the steps taken in the world
        out["world_steps"] = self.currentAgent.world.getStepCounter()


        # Inventory and accessible objects
        objsInv = []
        objsEnv = []
        if (self.currentAgent != None):
            objsInv = self.currentAgent.getInventory()
            objsEnv += self.currentAgent.getObjectsAgentFacing(respectContainerStatus=True)

        invAndEnvObjs = self.renderObjectSelectionBoxJSON(objsInv, objsEnv)        
        out.update(invAndEnvObjs)


        # Show nearby objects
        nearbyObjectsMaxDistance = 2
        nearbyObjectsFull, nearbyObjects, nearbyObjectsByDirection = self.currentAgent.getNearbyVisibleObjects(maxDistance=nearbyObjectsMaxDistance)
        # Note: nearbyObjectsByDirection is smaller
        out["nearbyObjects"] = {
            "note": "The objects below are within " + str(nearbyObjectsMaxDistance) + " tiles of the agent, but may not neccesarily be usable if they're not in the agent inventory, or directly in front of the agent.  This list should help in navigating to objects you'd like to interact with or use.  Objects to interact with or use should be in the 'accessibleEnvironmentObjects' or 'inventoryObjects' lists.",
            #"objects": nearbyObjects
            "objects": nearbyObjectsByDirection
        }

        # For any agents in the nearby objects list, show their recent action history to the user, to show what they're doing. 
        out["nearbyAgents"] = self.getRecentActionHistoryOfAgents(nearbyObjectsFull)

        # Recent posts on Discovery Feed
        out["discoveryFeed"] = self.currentAgent.world.discoveryFeed.getRecentPosts(curStep=self.currentAgent.world.getStepCounter(), lastNSteps=3)

        # Pop-up boxes/Dialog          
        dialogBoxDict = {}
        dialogBoxDict = {"is_in_dialog": False}
        if (self.dialogToDisplay != None):
            dialogBoxDict = {"is_in_dialog": True}
            dialogBoxDict["dialogIn"] = self.dialogToDisplay['dialogText']
            dialogBoxDict["dialogOptions"] = {}            
            # Then, add the options the user can say back
            for idx, option in enumerate(self.dialogToDisplay['dialogOptions']):
                dialogBoxDict["dialogOptions"][idx+1] = option   
            
        out["dialog_box"] = dialogBoxDict         


        out.update(invAndEnvObjs)

        # Text boxes
        out["extended_action_message"] = ""
        if (len(self.messageQueueText) > 0):
            nextMessage = self.messageQueueText[0]
            out["extended_action_message"] = nextMessage
            # Pop that most recent message from the queue, since we've already displayed it
            self.popMessageFromQueue()

        # Last action message
        lastActionMessageStr = self.lastActionMessage
        out["lastActionMessage"] = lastActionMessageStr

        # Task progress
        taskProgressList = []
        if (self.currentAgent != None):
            taskList = self.currentAgent.world.taskScorer.tasks
            for idx, task in enumerate(taskList):
                taskProgressList.append(self.renderTaskProgressJSON(task))
        out["taskProgress"] = taskProgressList    

        # Return the JSON
        return out


    # Gets the recent history of actions taken by nearby agents, and returns it as a JSON object
    # Uses the 'nearbyObjectList' to find agents that are near the current agent
    def getRecentActionHistoryOfAgents(self, nearbyObjectList):
        # NOTE: The argument description parts of this have not been verified yet, since the agent doesn't tend to wander near other agents much right now. (PJ: 12/21)

        # Filter to just include agents
        agentList = []
        for obj in nearbyObjectList:

            if (isinstance(obj, Agent)):
                # Make sure that it's not the current agent
                if (obj.uuid != self.currentAgent.uuid):
                    agentList.append(obj)

        # Get the recent action history of each agent
        out = {}
        out["description"] = "This section lists the recent action history (i.e. within the last few steps) of any agents that are nearby. This can help you understand what other agents are doing, and what they might be planning to do."
        out["list_of_agents"] = {}
        for agent in agentList:
            history = agent.actionHistory.exportToJSONAbleListHumanReadable(lastNSteps=3)
            out["list_of_agents"][agent.name + " uuid " + str(agent.uuid)] = history

        return out

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


    def renderTaskProgressJSON(self, task):
        out = {
            "taskName": task.taskName,
            "description": task.taskDescription,
            "score": task.getScoreNormalized()
        }
        return out


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
        #scale1 = 1.5
        scale1 = 1.5
        tileSize = 32        
        #offsetX = 32
        #offsetY = -32 * 10
        
        xAdj = ((tileSize*scale) - (tileSize*scale1))/2
        yAdj = ((tileSize*scale) - (tileSize*scale1))/2 + 16

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
            self.window.blit(label, (x + 4, y + (tileSize * scale) - 24 - 12 - yAdj))

            # Increment the object index
            objIdx += 1

        # Render the selected object's name
        selectedObjectName = ""
        if (curSelectedObjIdx < len(objectList)):
            selectedObjectName = objectList[curSelectedObjIdx].name + "[uuid: " + str(objectList[curSelectedObjIdx].uuid) + "] : " + objectList[curSelectedObjIdx].getTextDescription()

        # Render the name above the box
        x = 0 * (32 * scale) + offsetX            
        y = self.window.get_height() + offsetY + (tileSize * scale)
        label = self.fontBold.render(labelPrefixStr + selectedObjectName, 1, (255, 255, 255))
        self.window.blit(label, (x+4, y + (tileSize * scale) - 48 - 12 - yAdj))

        pass

    # As above, but renders in JSON format
    def renderObjectSelectionBoxJSON(self, objsInv, objsEnv):        
        invOut = []
        envOut = []
        # Populate
        for obj in objsInv:
            invOut.append({"uuid": obj.uuid, "name": obj.name, "description": obj.getTextDescription()})
        for obj in objsEnv:
            envOut.append({"uuid": obj.uuid, "name": obj.name, "description": obj.getTextDescription()})
        # Sort by UUID (ascending)
        invOut.sort(key=lambda x: x["uuid"], reverse=False)
        envOut.sort(key=lambda x: x["uuid"], reverse=False)
        # Pack
        out = {
            "inventoryObjects": invOut,
            "accessibleEnvironmentObjects": envOut
        }
        # Return
        return out

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
    def getDiscoveryFeedUpdates(self, startFromID=0):
        # Show the last 10 updates        
        success = self.currentAgent.actionDiscoveryFeedGetPosts(startFromID)
        return success        

    def getDiscoveryFeedArticles(self, startFromID=0):
        # Show the last 10 articles
        success = self.currentAgent.actionDiscoveryFeedGetArticleTitles(startFromID)
        return success
    
    def getSpecificDiscoveryFeedPost(self, postID):
        # Show the post with the given ID
        success = self.currentAgent.actionDiscoveryFeedGetByID(postID)
        return success

    def createDiscoveryFeedUpdate(self, contentStr, signals:list=[]):
        # Create a new update post
        success = self.currentAgent.actionDiscoveryFeedMakeUpdatePost(contentStr, signals)    
        return success
    
    def createDiscoveryFeedArticle(self, titleStr, contentStr):
        # Create a new article
        success = self.currentAgent.actionDiscoveryFeedMakeArticle(titleStr, contentStr)
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


    def _parseDialogJSON(self, jsonIn):
        # Get the current dialog options from the dialog tree
        agentInDialogWith = self.currentAgent.getAgentInDialogWith()
        # Get current node in dialog tree
        npcResponse, nextDialogOptions = agentInDialogWith.dialogTree.getCurrentDialog()

        # Look for the "chosen_dialog_option_int" key.
        # If it's not there, then return
        if ("chosen_dialog_option_int" not in jsonIn):
            return (False, ActionSuccess(success=False, message="Missing `chosen_dialog_option_int` key.  Expected a dictionary containing this key with an integer value representing the dialog option to select. No dialog option selected."))

        # Get the chosen dialog option
        chosenDialogOption = jsonIn["chosen_dialog_option_int"]
        # Check that it's an integer
        if (isinstance(chosenDialogOption, int) == False):
            return (False, ActionSuccess(success=False, message="`chosen_dialog_option_int` is not an integer."))
        # Check that it's in range
        if (chosenDialogOption < 1):
            return (False, ActionSuccess(success=False, message="`chosen_dialog_option_int` is less than 1."))
        if (chosenDialogOption > len(nextDialogOptions)):
            return (False, ActionSuccess(success=False, message="`chosen_dialog_option_int` is greater than number of options available (" + str(len(nextDialogOptions)) + ")."))

        # If the key is in range, then select that dialog option
        selectedDialogOption = nextDialogOptions[chosenDialogOption-1]

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
        # Reading articles
        elif (keys[pygame.K_v]):
            return (False, self.getDiscoveryFeedUpdates(startFromID=0))
        elif (keys[pygame.K_b]):
            return (False, self.getDiscoveryFeedArticles(startFromID=0))
        elif (keys[pygame.K_n]):
            # TODO: Randomly generate a post ID between 1 and 10 for now. But this needs to be changed to allow the user to specify a specific post they'd like.
            randPostID = math.floor(random.random() * 10) + 1            
            return (False, self.getSpecificDiscoveryFeedPost(postID=randPostID))
        # Creating articles
        elif (keys[pygame.K_m]):            
            return (False, self.createDiscoveryFeedUpdate(contentStr="This is a test update."))
        elif (keys[pygame.K_COMMA]):
            return (False, self.createDiscoveryFeedArticle(titleStr="Test Article", contentStr="This is a test article."))


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


    def _convertJSONArgsToObjects(self, jsonIn):
        errors = []

        # Get a list of inventory and accessible objects
        accessibleObjs = self.currentAgent.getInventory()
        accessibleObjs += self.currentAgent.getObjectsAgentFacing(respectContainerStatus=True)

        # Convert the JSON args to objects
        arg1Obj = None
        arg2Obj = None

        if ('arg1' in jsonIn) and (jsonIn['arg1'] != None):
            for obj in accessibleObjs:
                if (obj.uuid == jsonIn['arg1']):
                    arg1Obj = obj
                    break
            # If we reach here and the object is still None, then the object was not found
            if (arg1Obj == None):
                errors.append("arg1: Could not find object with UUID '" + str(jsonIn['arg1']) + "'. Are you sure it's accessible (i.e in your inventory, or directly in front of you?)")
        # So things don't break, if arg1 is not specified (or not found), set it to the first object. 
        # if (arg1Obj == None):
        #     if (len(accessibleObjs) > 0):
        #         arg1Obj = accessibleObjs[0]
        #         errors.append("arg1: No object specified. Defaulting to first accessible object.")
        #     else:
        #         errors.append("arg1: No object specified, and no accessible objects found.")                

        if ('arg2' in jsonIn) and (jsonIn['arg2'] != None):
            for obj in accessibleObjs:
                if (obj.uuid == jsonIn['arg2']):
                    arg2Obj = obj
                    break        
            # If we reach here and the object is still None, then the object was not found
            if (arg2Obj == None):
                errors.append("arg2: Could not find object with UUID '" + str(jsonIn['arg2']) + "' Are you sure it's accessible (i.e in your inventory, or directly in front of you?)")
        # So things don't break, if arg2 is not specified (or not found), set it to the first object.
        # if (arg2Obj == None):
        #     if (len(accessibleObjs) > 0):
        #         arg2Obj = accessibleObjs[0]
        #         errors.append("arg2: No object specified. Defaulting to first accessible object.")
        #     else:
        #         errors.append("arg2: No object specified, and no accessible objects found.")

        # Set the current selected objects
        self.curSelectedArgument1Obj = arg1Obj
        self.curSelectedArgument2Obj = arg2Obj

        # Update what the agent last interacted with
        self.currentAgent.updateLastInteractedObject([self.curSelectedArgument1Obj])

        # Return any errors
        return errors
        

    #
    #   Parse actions from JSON
    #
    def parseActionJSON(self, jsonIn):
        # jsonIn format: {"action": "EAT", "arg1": uuid, "arg2": uuid}
        # Except dialog actions, which don't take arg1/arg2, but specific dialog options.                 
        # Action names (from enumeration)
        # Enumeration for layer types
        # class ActionType(Enum):
        #     MOVE_FORWARD    = 0
        #     MOVE_BACKWARD   = 1
        #     ROTATE_CW       = 2
        #     ROTATE_CCW      = 3
        #     PICKUP          = 4
        #     PUT             = 5
        #     DROP            = 6 
        #     OPEN            = 7
        #     CLOSE           = 8
        #     ACTIVATE        = 9
        #     DEACTIVATE      = 10
        #     TALK            = 11
        #     EAT             = 12
        #     READ            = 13
        #     USE             = 14
        #     DISCOVERY_FEED_GET_UPDATES = 15
        #     DISCOVERY_FEED_GET_ARTICLES = 16
        #     DISCOVERY_FEED_GET_POST_BY_ID = 17
        #     DISCOVERY_FEED_CREATE_UPDATE = 18
        #     DISCOVERY_FEED_CREATE_ARTICLE = 19
        #     MOVE_DIRECTION = 20
        #     ROTATE_DIRECTION = 21


        # TODO: Convert 'arg1' and 'arg2' from JSON into internal (arg1, arg2) selection variables for UI
        # TODO: Provide these JSON parse errors in the output
        jsonParseErrors = self._convertJSONArgsToObjects(jsonIn)

        #First, check if we're in the middle of a dialog
        if (self.currentAgent.isInDialog()):
            # If so, we need to parse the dialog keys
            print("### IS IN DIALOG")
            #return self._parseDialogKeys(keys)
            success, result = self._parseDialogJSON(jsonIn)
            return (True, "", result)
        else:
            self.dialogToDisplay = None
        
        # Move the agent forward
        if (jsonIn["action"] == ActionType.MOVE_FORWARD.name):            
            return (True, jsonParseErrors, self.actionMoveAgentForward())

        # Move the agent backward
        elif (jsonIn["action"] == ActionType.MOVE_BACKWARD.name):
            return (True, jsonParseErrors, self.actionMoveAgentBackward())

        # Rotate the agent counterclockwise
        elif (jsonIn["action"] == ActionType.ROTATE_CCW.name):
            return (True, jsonParseErrors, self.actionRotateAgentCounterclockwise())

        # Rotate the agent clockwise
        elif (jsonIn["action"] == ActionType.ROTATE_CW.name):
            return (True, jsonParseErrors, self.actionRotateAgentClockwise())

        # Move in a specific direction (north/east/south/west)
        elif (jsonIn["action"] == ActionType.MOVE_DIRECTION.name):
            #checkArgSuccess = self._checkArgs(actionName = "move direction", arg1 = True, arg2 = False)
            #if (checkArgSuccess == False):
            #    return (False, jsonParseErrors, False)
            # Check if there is a key 'direction' in 'jsonIn', and if it contains a valid direction ('north', 'east', 'south', 'west')
            if ('arg1' not in jsonIn):
                jsonParseErrors.append("Missing 'arg1' key in JSON.")
                return (False, jsonParseErrors, ActionSuccess(False, "Missing 'arg1' key in JSON."))
            if (jsonIn['arg1'] not in ['north', 'east', 'south', 'west']):
                jsonParseErrors.append("Invalid direction '" + str(jsonIn['arg1']) + "' specified in JSON.")
                return (False, jsonParseErrors, ActionSuccess(False, "Invalid direction '" + str(jsonIn['arg1']) + "' specified in JSON."))
        
            # Get the direction from the argument
            direction = jsonIn['arg1']
            return (True, jsonParseErrors, self.currentAgent.actionMoveAgentNorthEastSouthWest(direction))

        # Rotate to a specific direction (north/east/south/west)
        elif (jsonIn["action"] == ActionType.ROTATE_DIRECTION.name):
            # Check if there is a key 'direction' in 'jsonIn', and if it contains a valid direction ('north', 'east', 'south', 'west')
            if ('arg1' not in jsonIn):
                jsonParseErrors.append("Missing 'arg1' key in JSON.")
                return (False, jsonParseErrors, ActionSuccess(False, "Missing 'arg1' key in JSON."))
            if (jsonIn['arg1'] not in ['north', 'east', 'south', 'west']):
                jsonParseErrors.append("Invalid direction '" + str(jsonIn['arg1']) + "' specified in JSON.")
                return (False, jsonParseErrors, ActionSuccess(False, "Invalid direction '" + str(jsonIn['arg1']) + "' specified in JSON."))
        
            # Get the direction from the argument
            direction = jsonIn['arg1']
            return (True, jsonParseErrors, self.currentAgent.actionRotateAgentFacingDirectionAbsolute(direction))

        # Teleport action (teleport to a specific location)
        elif (jsonIn["action"] == ActionType.TELEPORT_TO_LOCATION.name):
            # Check if there is a key 'arg1' that lists the location to teleport to
            if ('arg1' not in jsonIn):
                jsonParseErrors.append("Missing 'arg1' key in JSON.")
                return (False, jsonParseErrors, ActionSuccess(False, "Missing 'arg1' key in JSON."))
            
            # Get the location from the argument
            location = jsonIn['arg1']
            return (True, jsonParseErrors, self.currentAgent.actionTeleportAgentToLocation(location))            
        
        # Teleport action (teleport to a specific object)
        elif (jsonIn["action"] == ActionType.TELEPORT_TO_OBJECT.name):
            # Check if there is a key 'arg1' that lists the object to teleport to
            if ('arg1' not in jsonIn):
                jsonParseErrors.append("Missing 'arg1' key in JSON.")
                return (False, jsonParseErrors, ActionSuccess(False, "Missing 'arg1' key in JSON."))
            
            # Get the object from the argument
            obj = jsonIn['arg1']
            return (True, jsonParseErrors, self.currentAgent.actionTeleportAgentToObject(obj))

        # Pick-up Object in arg1 slot
        elif (jsonIn["action"] == ActionType.PICKUP.name):
            checkArgSuccess = self._checkArgs(actionName = "pick up object", arg1 = True, arg2 = False)
            if (checkArgSuccess != None):
                return (False, jsonParseErrors, checkArgSuccess)

            return (True, jsonParseErrors, self.actionPickupObject(objToPickUp = self.curSelectedArgument1Obj))

        # Drop an inventory item in arg1 slot at the agents current location
        elif (jsonIn["action"] == ActionType.DROP.name):
            checkArgSuccess = self._checkArgs(actionName = "drop item", arg1 = True, arg2 = False)
            if (checkArgSuccess != None):
                return (False, jsonParseErrors, checkArgSuccess)

            return (True, jsonParseErrors, self.actionDropObject(objToDrop = self.curSelectedArgument1Obj))

        # Put an item (arg1) in a specific container (arg2)
        elif (jsonIn["action"] == ActionType.PUT.name):
            checkArgSuccess = self._checkArgs(actionName = "put item in container", arg1 = True, arg2 = True)
            if (checkArgSuccess != None):
                return (False, jsonParseErrors, checkArgSuccess)

            return (True, jsonParseErrors, self.actionPutObjectInContainer(objToPut = self.curSelectedArgument1Obj, container = self.curSelectedArgument2Obj))

        # Open a container or passage (arg1) 
        elif (jsonIn["action"] == ActionType.OPEN.name):
            checkArgSuccess = self._checkArgs(actionName = "open", arg1 = True, arg2 = False)
            if (checkArgSuccess != None):
                return (False, jsonParseErrors, checkArgSuccess)

            return (True, jsonParseErrors, self.actionOpenObject(objToOpen = self.curSelectedArgument1Obj))
        
        # Close a container or passage (arg1)
        elif (jsonIn["action"] == ActionType.CLOSE.name):
            checkArgSuccess = self._checkArgs(actionName = "close", arg1 = True, arg2 = False)
            if (checkArgSuccess != None):
                return (False, jsonParseErrors, checkArgSuccess)

            return (True, jsonParseErrors, self.actionCloseObject(objToClose = self.curSelectedArgument1Obj))
        
        # Activate an object (arg1) 
        elif (jsonIn["action"] == ActionType.ACTIVATE.name):
            checkArgSuccess = self._checkArgs(actionName = "activate", arg1 = True, arg2 = False)
            if (checkArgSuccess != None):
                return (False, jsonParseErrors, checkArgSuccess)

            return (True, jsonParseErrors, self.actionActivateObject(objToActivate = self.curSelectedArgument1Obj))
            
        # For some read K_d doesn't work. 
        # Should be D key here
        # Deactivate an object (arg1)
        elif (jsonIn["action"] == ActionType.DEACTIVATE.name):
            checkArgSuccess = self._checkArgs(actionName = "deactivate", arg1 = True, arg2 = False)
            if (checkArgSuccess != None):
                return (False, jsonParseErrors, checkArgSuccess)

            return (True, jsonParseErrors, self.actionDeactivateObject(objToDeactivate = self.curSelectedArgument1Obj))
            
        # Dialog/talk with agent specified in arg1
        elif (jsonIn["action"] == ActionType.TALK.name):
            checkArgSuccess = self._checkArgs(actionName = "talk", arg1 = True, arg2 = False)
            if (checkArgSuccess != None):
                return (False, jsonParseErrors, checkArgSuccess)

            actionResult = self.actionTalk(agentToTalkTo = self.curSelectedArgument1Obj)

            # If the agent is in dialog, then we need to display the dialog options
            if (self.currentAgent.isInDialog()):
                npcResponse, nextDialogOptions = self.currentAgent.getAgentInDialogWith().dialogTree.getCurrentDialog()
                self.dialogToDisplay = {}
                self.dialogToDisplay['dialogText'] = npcResponse
                self.dialogToDisplay['dialogOptions'] = nextDialogOptions

            return (True, jsonParseErrors, actionResult)

        # Eat arg1
        elif (jsonIn["action"] == ActionType.EAT.name):
            checkArgSuccess = self._checkArgs(actionName = "eat", arg1 = True, arg2 = False)
            if (checkArgSuccess != None):
                return (False, jsonParseErrors, checkArgSuccess)

            return (True, jsonParseErrors, self.actionEat(objToEat = self.curSelectedArgument1Obj))

        # Read arg1
        elif (jsonIn["action"] == ActionType.READ.name):
            checkArgSuccess = self._checkArgs(actionName = "read", arg1 = True, arg2 = False)
            if (checkArgSuccess != None):
                return (False, jsonParseErrors, checkArgSuccess)

            return (True, jsonParseErrors, self.actionRead(objToRead = self.curSelectedArgument1Obj))

        # Use action (use arg1 with arg2)
        elif (jsonIn["action"] == ActionType.USE.name):
            checkArgSuccess = self._checkArgs(actionName = "use object", arg1 = True, arg2 = True)
            if (checkArgSuccess != None):
                return (False, jsonParseErrors, checkArgSuccess)

            result = self.actionUse(objToUse = self.curSelectedArgument1Obj, objToUseWith = self.curSelectedArgument2Obj)

            if (result.success == False):
                # Try switching the arguments around, since the LLMs are terrible at getting the arguments in the correct order.
                result1 = self.actionUse(objToUse = self.curSelectedArgument2Obj, objToUseWith = self.curSelectedArgument1Obj)
                if (result1.success == True):
                    result = result1
                    # Append a message saying the arguments were switched
                    result.message += "\n Note, the original action failed (USE, arg1:" + self.curSelectedArgument1Obj.name + ", arg2:" + self.curSelectedArgument2Obj.name + "), but the arguments were switched and the action succeeded (USE, arg1:" + self.curSelectedArgument2Obj.name + ", arg2:" + self.curSelectedArgument1Obj.name + "). Try to enter the arguments in the correct order next time."

            # # If there is a .generatedItems populated in this result, then process it            
            # if ('generatedItems' in result.data):
            #     for item in result.data['generatedItems']:
            #         self.currentAgent.addObject(item)

            return (True, jsonParseErrors, result)

        # NOTE: These can probably safely be deleted, since the arguments are supplied directly in the JSON
        # # UI element (incrementing argument boxes with [, ], ;, and ')
        # elif (keys[pygame.K_LEFTBRACKET]):
        #     self.changeArgumentBox(delta=-1, whichBox=1)
        #     return (False, ActionSuccess(success=True, message="Changed argument box 1 to " + str(self.curSelectedArgument1Obj.name)))
            
        # elif (keys[pygame.K_RIGHTBRACKET]):
        #     self.changeArgumentBox(delta=1, whichBox=1)
        #     return (False, ActionSuccess(success=True, message="Changed argument box 1 to " + str(self.curSelectedArgument1Obj.name)))
            
        # elif (keys[pygame.K_SEMICOLON]):
        #     self.changeArgumentBox(delta=-1, whichBox=2)
        #     return (False, ActionSuccess(success=True, message="Changed argument box 2 to " + str(self.curSelectedArgument2Obj.name)))
            
        # elif (keys[pygame.K_QUOTE]):
        #     self.changeArgumentBox(delta=1, whichBox=2)
        #     return (False, ActionSuccess(success=True, message="Changed argument box 2 to " + str(self.curSelectedArgument2Obj.name)))
            

        # DiscoveryFeed Actions
        # TODO: These need to be updated to take their arguments from the JSON
        # Reading articles
        elif (jsonIn["action"] == ActionType.DISCOVERY_FEED_GET_UPDATES.name):
            return (False, jsonParseErrors, self.getDiscoveryFeedUpdates(startFromID=0))
        elif (jsonIn["action"] == ActionType.DISCOVERY_FEED_GET_ARTICLES.name):
            return (False, jsonParseErrors, self.getDiscoveryFeedArticles(startFromID=0))
        elif (jsonIn["action"] == ActionType.DISCOVERY_FEED_GET_POST_BY_ID.name):
            # TODO: Randomly generate a post ID between 1 and 10 for now. But this needs to be changed to allow the user to specify a specific post they'd like.
            randPostID = math.floor(random.random() * 10) + 1            
            return (False, jsonParseErrors, self.getSpecificDiscoveryFeedPost(postID=randPostID))
        # Creating articles
        elif (jsonIn["action"] == ActionType.DISCOVERY_FEED_CREATE_UPDATE.name):
            return (False, jsonParseErrors, self.createDiscoveryFeedUpdate(contentStr="This is a test update."))
        elif (jsonIn["action"] == ActionType.DISCOVERY_FEED_CREATE_ARTICLE.name):
            return (False, jsonParseErrors, self.createDiscoveryFeedArticle(titleStr="Test Article", contentStr="This is a test article."))


        # If we reach here, then no known key was pressed
        return (False, jsonParseErrors, ActionSuccess(success=False, message="Unknown action '" + str(jsonIn["action"]) + "'."))


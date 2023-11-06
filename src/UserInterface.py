# UserInterface.py

import pygame
import SpriteLibrary
from Layer import Layer
from ObjectModel import Object
from Agent import Agent
import math



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

        # Queue of messages to display
        self.messageQueueText = []

        # Status
        self.inModal = False

        # What spot in the argument boxes is currently selected
        self.curSelectedArgument1Idx = 0
        self.curSelectedArgument2Idx = 0
    
    
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


    # 
    #   Argument boxes
    #
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
        if (self.curSelectedArgument2Idx < 0):
            self.curSelectedArgument2Idx = 0
        
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
        objects = []
        if (self.currentAgent != None):
            objects = self.currentAgent.getInventory()
            objects += self.currentAgent.getObjectsAgentFacing(respectContainerStatus=True)

        # Render argument 1 box
        if (self.curSelectedArgument1Idx >= len(objects)):
            self.curSelectedArgument1Idx = len(objects) - 1
        self.renderObjectSelectionBox(objects, self.curSelectedArgument1Idx, offsetX=32, offsetY=-(32*10))
        # Render argument 2 box
        if (self.curSelectedArgument2Idx >= len(objects)):
            self.curSelectedArgument2Idx = len(objects) - 1
        self.renderObjectSelectionBox(objects, self.curSelectedArgument2Idx, offsetX=32, offsetY=-(32*5))



        # TODO: Add the rest of the UI elements

        # Step 2: Render the message queue
        if (len(self.messageQueueText) > 0):
            # Render the top message in the message queue
            nextMessage = self.messageQueueText[0]
            self.renderTextBox(nextMessage)            
            # Set the modal flag
            self.inModal = True
            


        pass


    
    #
    #   User interface elements
    #
    
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
            label = self.font.render(str(idx + 1), 1, (255, 255, 255))
            self.window.blit(label, (x + 2, y + 2))

            
    # Helper to render an object's sprite(s) at a given x/y location
    def _renderObjectSprite(self, object, x, y, scale=1.0):
        for spriteName in object.getSpriteNamesWithContents():
            self.spriteLibrary.renderSprite(self.window, spriteName, x, y, scale, adjustY=True)


    # Render a box that shows (graphically) a set of objects the agent might select from.  
    # Should look similar to the inventory box, only with the potential to hold more objects. 
    def renderObjectSelectionBox(self, objectList, curSelectedObjIdx, offsetX, offsetY):
        # The object selection box is a single row with 10 columns.  If there are more than 10 objects, then the user can scroll through them.        
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
                self.spriteLibrary.renderSprite(self.window, "ui_inventory_background", x, y, scale)

            # Display the object's sprite                
            if (objIdx < endIdx):
                obj = objectList[objIdx]
                print("Object " + str(objIdx) + " name: " + obj.name + "  Sprite name: " + obj.getSpriteName())
                #self._renderObjectSprite(obj, x+xAdj, y+yAdj, scale=scale1)
                self._renderObjectSprite(obj, x+xAdj, y + tileSize - yAdj, scale=scale1)

            # Display the number
            label = self.font.render(str(objIdx + 1), 1, (255, 255, 255))
            self.window.blit(label, (x + 4, y + (tileSize * scale) - 24))

            # Increment the object index
            objIdx += 1

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
    


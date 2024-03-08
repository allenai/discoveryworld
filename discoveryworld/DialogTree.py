# DialogTree.py


class DialogTree():
    def __init__(self, agent):
        self.nodes = {}
        self.rootNodeName = None
        self.currentNodeName = None

        # The agent that this dialog tree is associated with (e.g. if this is the dialog for the Chef NPC, this is a reference to the Chef NPC)
        self.agent = agent

        # If this NPC is currently talking with a user/agent, this is a reference to who its talking to
        self.engagingWithAgent = None

    #
    #   Adding nodes
    #
    def addNode(self, node):
        self.nodes[node.name] = node

    def setRoot(self, rootNodeName):
        self.rootNodeName = rootNodeName

    #
    #   Resetting dialog
    #
    def reset(self):
        self.setCurrentNode(self.rootNodeName)
        self.engagingWithAgent = None
        self.agent.setNotInDialog()

    # Call this when an agent stops talking to this dialog tree
    def endDialog(self):
        self.reset()


    #
    #   Performing dialog
    #

    # Returns 'True' if this dialog tree is busy
    def isBusy(self):
        if (self.engagingWithAgent == None):
            # Not engaging with an agent
            return False
        else:
            # Someone is already talking to this dialog tree -- return True
            return True

    # Get what agent this NPC is talking to
    def getAgentTalkingTo(self):
        return self.engagingWithAgent

    # Start dialog with an agent
    def initiateDialog(self, agent):
        self.reset()
        self.engagingWithAgent = agent

    # Set the current node in the dialog tree
    def setCurrentNode(self, nodeName):
        self.currentNodeName = nodeName

        # Add and remove states associated with this node
        currentNode = self.getCurrentNode(nodeName)
        for stateToAdd in currentNode.statesToAdd:
            self.agent.addState(stateToAdd)
        for stateToRemove in currentNode.statesToRemove:
            self.agent.removeState(stateToRemove)


    # Get the current node in the dialog tree
    def getCurrentNode(self, nodeName):
        return self.nodes[nodeName]

    # Returns what the agent is currently saying, and any options that the agent can say next.
    def getCurrentDialog(self):
        # Get the current node
        currentNode = self.getCurrentNode(self.currentNodeName)

        # Get what this agent is currently saying
        currentNodeText = currentNode.currentNodeText
        # Replace any variables in the text. Variables are of the form {varName}, and are replaced with the value of the variable in this agent's self.attributes[] dictionary

        complete = False
        numRuns = 0
        while ("{" in currentNodeText) and (complete == False):
            # Look for the first "{"
            firstBracketIndex = currentNodeText.index("{")
            # Look for the next "}" after it
            secondBracketIndex = currentNodeText.index("}", firstBracketIndex)
            # Get the variable name
            varName = currentNodeText[firstBracketIndex + 1:secondBracketIndex]
            # If the variable name is in the agent's attributes, replace it
            if (varName in self.agent.attributes):
                currentNodeText = currentNodeText[:firstBracketIndex] + str(self.agent.attributes[varName]) + currentNodeText[secondBracketIndex + 1:]
            else:
                #currentNodeText = currentNodeText[:firstBracketIndex] + "UNKNOWN" + currentNodeText[secondBracketIndex + 1:]
                complete = True

            # Just in case something goes wonky, limit the number of runs so we don't go in an infinite loop.
            numRuns += 1
            if (numRuns > 50):
                complete = True




        # Get the options of what the user can say to this agent
        dialogOptions = currentNode.dialogOptions
        # Old: Filter to include only 'thingsToSay'
        #dialogOptions = [dialogOption["thingToSay"] for dialogOption in dialogOptions]
        # New: Filter to include only 'thingsToSay', but make sure that the state requirements are met
        dialogOptionsStrs = []
        for dialogOption in dialogOptions:
            # Check if the state requirements are met
            requiresStates = dialogOption["requiresStates"]
            antiStates = dialogOption["antiStates"]

            hasAllRequired = True
            for state in requiresStates:
                if (not self.agent.hasState(state)):
                    hasAllRequired = False
                    break
            hasNoAnti = True
            for state in antiStates:
                if (self.agent.hasState(state)):
                    hasNoAnti = False
                    break
            if (hasAllRequired and hasNoAnti):
                dialogOptionsStrs.append(dialogOption["thingToSay"])

        # Return the dialog options, and the states to add and remove
        return currentNodeText, dialogOptionsStrs

    # Say something to the agent
    def say(self, thingToSay, agentEngaging):
        # Check if this dialog tree is open
        if (self.engagingWithAgent == None):
            self.engagingWithAgent = agentEngaging

        # Check if this dialog tree is busy with another agent
        if (self.engagingWithAgent != agentEngaging):
            # This agent is not currently talking to this dialog tree
            return False

        # Get the current node
        currentNode = self.getCurrentNode(self.currentNodeName)

        # Get the dialog options
        dialogOptions = currentNode.dialogOptions

        # Find the dialog option that matches what the user said
        for dialogOption in dialogOptions:
            if dialogOption["thingToSay"] == thingToSay:
                # Also, modify any variables, if requested
                varsToModify = dialogOption["floatVariablesToModify"]
                for varName in varsToModify:
                    # Check that the agent has the variable
                    if (varName in self.agent.attributes):
                        # Modify the variable
                        self.agent.attributes[varName] += varsToModify[varName]
                    else:
                        # The agent doesn't have the variable
                        print("ERROR: DialogTree: Agent doesn't have variable '" + varName + "'")

                # Set the current node to the next node
                self.setCurrentNode(dialogOption["nextNodeName"])


                return True

        # If we got here, the agent said something that wasn't a dialog option. Reset
        self.reset()


    def __str__(self):
        return "DialogTree(" + str(self.root) + ")"


# Storage class for one turn of dialog (a think the NPC says, and a set of allowable responses ('dialogOptions') from the user)
class DialogNode():
    def __init__(self, name, currentNodeText, statesToAdd = [], statesToRemove = []):
        self.name = name
        self.currentNodeText = currentNodeText
        self.statesToAdd = statesToAdd
        self.statesToRemove = statesToRemove
        self.dialogOptions = []


    def addDialogOption(self, thingToSay, nextNodeName, requiresStates = [], antiStates = [], floatVariablesToModify = {}):
        packed = {
            "thingToSay": thingToSay,
            "nextNodeName": nextNodeName,
            "requiresStates": requiresStates,
            "antiStates": antiStates,
            "floatVariablesToModify": floatVariablesToModify
        }

        self.dialogOptions.append(packed)

    def __str__(self):
        return "DialogNode(" + str(self.name) + ", " + str(self.currentNodeText) + ", " + str(self.statesToAdd) + ", " + str(self.statesToRemove) + ", " + str(self.dialogOptions) + ")"



#
#   Specific Dialog
#

class DialogMaker():
    # Constructor
    def __init__(self):
        pass

    def mkDialogChef(self, agent):
        tree = DialogTree(agent)

        # Root node (introduce the chef, give options to ask to collect food, or distribute food)
        rootNode = DialogNode("rootNode", "Hello, I am the chef. I can collect food from the farm, or serve food from the pot.", statesToAdd = [], statesToRemove = [])
        rootNode.addDialogOption("Can you collect food from the farm and place it in the pot?", "collectFoodNode")
        rootNode.addDialogOption("Can you serve the food in the pot onto the buffet so it's available for meals?", "serveFoodNode")
        rootNode.addDialogOption("Can you call the colonists for a meal?", "callColonistsNode")
        rootNode.addDialogOption("Goodbye", "endNode")
        tree.addNode(rootNode)
        tree.setRoot(rootNode.name)

        # Collect food node
        collectFoodNode = DialogNode("collectFoodNode", "I will go collect food from the farm, and place it in the pot.", statesToAdd = ["collectSignal"], statesToRemove = [])
        collectFoodNode.addDialogOption("OK", "endNode")
        tree.addNode(collectFoodNode)

        # Serve food node
        serveFoodNode = DialogNode("serveFoodNode", "I will serve food from the pot to the buffet so it's available for meals.", statesToAdd = ["serveSignal"], statesToRemove = [])
        serveFoodNode.addDialogOption("OK", "endNode")
        tree.addNode(serveFoodNode)

        # Call Colonists node
        callColonistsNode = DialogNode("callColonistsNode", "I will call the colonists for a meal.", statesToAdd = ["callColonistsSignal"], statesToRemove = [])
        callColonistsNode.addDialogOption("OK", "endNode")
        tree.addNode(callColonistsNode)

        # End node
        endNode = DialogNode("endNode", "Goodbye.", statesToAdd = [], statesToRemove = [])
        tree.addNode(endNode)

        # Store dialog tree in agent
        agent.setDialogTree(tree)


    def mkDialogFarmer(self, agent):
        tree = DialogTree(agent)

        # Root node (introduce the farmer, give options to ask to plant more seeds)
        rootNode = DialogNode("rootNode", "Hello, I am the farmer. I can plant more seeds.", statesToAdd = [], statesToRemove = [])
        rootNode.addDialogOption("Can you plant more seeds", "plantSeeds")
        rootNode.addDialogOption("Goodbye", "endNode")
        tree.addNode(rootNode)
        tree.setRoot(rootNode.name)

        # Plant seeds node
        plantSeedsNode = DialogNode("plantSeeds", "I will plant more seeds.", statesToAdd = ["plantSignal"], statesToRemove = [])
        plantSeedsNode.addDialogOption("OK", "endNode")
        tree.addNode(plantSeedsNode)


        # End node
        endNode = DialogNode("endNode", "Goodbye.", statesToAdd = [], statesToRemove = [])
        tree.addNode(endNode)

        # Store dialog tree in agent
        agent.setDialogTree(tree)


    def mkDialogColonist(self, agent):
        tree = DialogTree(agent)

        colonistName = agent.name

        # Root node (introduce the colonist, give option to ask the agent to go to the cafeteria to try to eat)
        rootNode = DialogNode("rootNode", "Hello, I am a colonist here on Discovery World. ", statesToAdd = [], statesToRemove = [])
        rootNode.addDialogOption("I think there is food available in the cafeteria.", "eatNode")
        rootNode.addDialogOption("Goodbye", "endNode")
        tree.addNode(rootNode)
        tree.setRoot(rootNode.name)

        # Eat node
        eatNode = DialogNode("eatNode", "I will go to the cafeteria to find something to eat.", statesToAdd = ["eatSignal_" + colonistName], statesToRemove = [])
        eatNode.addDialogOption("OK", "endNode")
        tree.addNode(eatNode)

        # End node
        endNode = DialogNode("endNode", "Goodbye.", statesToAdd = [], statesToRemove = [])
        tree.addNode(endNode)

        # Store dialog tree in agent
        agent.setDialogTree(tree)



    # Dialog tree for the soil nutrient controller
    def mkDialogSoilNutrientController(self, agent, fieldNum):
        tree = DialogTree(agent)

        # ["potassium", "titanium", "lithium", "thorium", "barium"]:

        # Root node (introduce the soil nutrient controller, give options to ask to change the nutrient levels)
        rootNode = DialogNode("rootNode", "Hello, I am the soil nutrient controller for Field #" + str(fieldNum) + ". I can change the nutrient levels in the soil.", statesToAdd = [], statesToRemove = [])
        # Potassium
        rootNode.addDialogOption("Set Potassium Level (Current: Low)", "changePotassiumLevel", requiresStates=["potassiumLowSignal_field" + str(fieldNum)])
        rootNode.addDialogOption("Set Potassium Level (Current: Medium)", "changePotassiumLevel", requiresStates=["potassiumMediumSignal_field" + str(fieldNum)])
        rootNode.addDialogOption("Set Potassium Level (Current: High)", "changePotassiumLevel", requiresStates=["potassiumHighSignal_field" + str(fieldNum)])
        rootNode.addDialogOption("Set Potassium Level (Current: Unset)", "changePotassiumLevel", antiStates=["potassiumLowSignal_field" + str(fieldNum), "potassiumMediumSignal_field" + str(fieldNum), "potassiumHighSignal_field" + str(fieldNum)])
        # Titanium
        rootNode.addDialogOption("Set Titanium Level (Current: Low)", "changeTitaniumLevel", requiresStates=["titaniumLowSignal_field" + str(fieldNum)])
        rootNode.addDialogOption("Set Titanium Level (Current: Medium)", "changeTitaniumLevel", requiresStates=["titaniumMediumSignal_field" + str(fieldNum)])
        rootNode.addDialogOption("Set Titanium Level (Current: High)", "changeTitaniumLevel", requiresStates=["titaniumHighSignal_field" + str(fieldNum)])
        rootNode.addDialogOption("Set Titanium Level (Current: Unset)", "changeTitaniumLevel", antiStates=["titaniumLowSignal_field" + str(fieldNum), "titaniumMediumSignal_field" + str(fieldNum), "titaniumHighSignal_field" + str(fieldNum)])
        # Lithium
        rootNode.addDialogOption("Set Lithium Level (Current: Low)", "changeLithiumLevel", requiresStates=["lithiumLowSignal_field" + str(fieldNum)])
        rootNode.addDialogOption("Set Lithium Level (Current: Medium)", "changeLithiumLevel", requiresStates=["lithiumMediumSignal_field" + str(fieldNum)])
        rootNode.addDialogOption("Set Lithium Level (Current: High)", "changeLithiumLevel", requiresStates=["lithiumHighSignal_field" + str(fieldNum)])
        rootNode.addDialogOption("Set Lithium Level (Current: Unset)", "changeLithiumLevel", antiStates=["lithiumLowSignal_field" + str(fieldNum), "lithiumMediumSignal_field" + str(fieldNum), "lithiumHighSignal_field" + str(fieldNum)])
        # Thorium
        rootNode.addDialogOption("Set Thorium Level (Current: Low)", "changeThoriumLevel", requiresStates=["thoriumLowSignal_field" + str(fieldNum)])
        rootNode.addDialogOption("Set Thorium Level (Current: Medium)", "changeThoriumLevel", requiresStates=["thoriumMediumSignal_field" + str(fieldNum)])
        rootNode.addDialogOption("Set Thorium Level (Current: High)", "changeThoriumLevel", requiresStates=["thoriumHighSignal_field" + str(fieldNum)])
        rootNode.addDialogOption("Set Thorium Level (Current: Unset)", "changeThoriumLevel", antiStates=["thoriumLowSignal_field" + str(fieldNum), "thoriumMediumSignal_field" + str(fieldNum), "thoriumHighSignal_field" + str(fieldNum)])
        # Barium
        rootNode.addDialogOption("Set Barium Level (Current: Low)", "changeBariumLevel", requiresStates=["bariumLowSignal_field" + str(fieldNum)])
        rootNode.addDialogOption("Set Barium Level (Current: Medium)", "changeBariumLevel", requiresStates=["bariumMediumSignal_field" + str(fieldNum)])
        rootNode.addDialogOption("Set Barium Level (Current: High)", "changeBariumLevel", requiresStates=["bariumHighSignal_field" + str(fieldNum)])
        rootNode.addDialogOption("Set Barium Level (Current: Unset)", "changeBariumLevel", antiStates=["bariumLowSignal_field" + str(fieldNum), "bariumMediumSignal_field" + str(fieldNum), "bariumHighSignal_field" + str(fieldNum)])
        # OK
        rootNode.addDialogOption("Imprint current selections on this field (Note: can't be changed)", "endNodeOK")
        # Cancel
        rootNode.addDialogOption("Cancel and exit", "endNodeCancel")
        tree.addNode(rootNode)
        tree.setRoot(rootNode.name)

        # Change nutrient levels node (Potassium)
        changeNutrientLevelsNodePot = DialogNode("changePotassiumLevel", "What level would you like the Potassium to be at in field #" + str(fieldNum) + "?", statesToAdd = [""], statesToRemove = [])
        changeNutrientLevelsNodePot.addDialogOption("Potassium level: low", "nodePotassiumLow")
        changeNutrientLevelsNodePot.addDialogOption("Potassium level: medium", "nodePotassiumMedium")
        changeNutrientLevelsNodePot.addDialogOption("Potassium level: high", "nodePotassiumHigh")
        changeNutrientLevelsNodePot.addDialogOption("Back to main menu", "rootNode")
        tree.addNode(changeNutrientLevelsNodePot)

        # Potassium low node
        potassiumLowNode = DialogNode("nodePotassiumLow", "Potassium level now set to low.", statesToAdd = ["potassiumLowSignal_field" + str(fieldNum)], statesToRemove = ["potassiumMediumSignal_field" + str(fieldNum), "potassiumHighSignal_field" + str(fieldNum)])
        potassiumLowNode.addDialogOption("Back to main menu", "rootNode")
        tree.addNode(potassiumLowNode)
        # Potassium medium node
        potassiumMediumNode = DialogNode("nodePotassiumMedium", "Potassium level now set to medium.", statesToAdd = ["potassiumMediumSignal_field" + str(fieldNum)], statesToRemove = ["potassiumLowSignal_field" + str(fieldNum), "potassiumHighSignal_field" + str(fieldNum)])
        potassiumMediumNode.addDialogOption("Back to main menu", "rootNode")
        tree.addNode(potassiumMediumNode)
        # Potassium high node
        potassiumHighNode = DialogNode("nodePotassiumHigh", "Potassium level now set to high.", statesToAdd = ["potassiumHighSignal_field" + str(fieldNum)], statesToRemove = ["potassiumLowSignal_field" + str(fieldNum), "potassiumMediumSignal_field" + str(fieldNum)])
        potassiumHighNode.addDialogOption("Back to main menu", "rootNode")
        tree.addNode(potassiumHighNode)

        # Change nutrient levels node (Titanium)
        changeNutrientLevelsNodeTit = DialogNode("changeTitaniumLevel", "What level would you like the Titanium to be at in field #" + str(fieldNum) + "?", statesToAdd = [""], statesToRemove = [])
        changeNutrientLevelsNodeTit.addDialogOption("Titanium level: low", "nodeTitaniumLow")
        changeNutrientLevelsNodeTit.addDialogOption("Titanium level: medium", "nodeTitaniumMedium")
        changeNutrientLevelsNodeTit.addDialogOption("Titanium level: high", "nodeTitaniumHigh")
        changeNutrientLevelsNodeTit.addDialogOption("Back to main menu", "rootNode")
        tree.addNode(changeNutrientLevelsNodeTit)

        # Titanium low node
        titaniumLowNode = DialogNode("nodeTitaniumLow", "Titanium level now set to low.", statesToAdd = ["titaniumLowSignal_field" + str(fieldNum)], statesToRemove = ["titaniumMediumSignal_field" + str(fieldNum), "titaniumHighSignal_field" + str(fieldNum)])
        titaniumLowNode.addDialogOption("Back to main menu", "rootNode")
        tree.addNode(titaniumLowNode)
        # Titanium medium node
        titaniumMediumNode = DialogNode("nodeTitaniumMedium", "Titanium level now set to medium.", statesToAdd = ["titaniumMediumSignal_field" + str(fieldNum)], statesToRemove = ["titaniumLowSignal_field" + str(fieldNum), "titaniumHighSignal_field" + str(fieldNum)])
        titaniumMediumNode.addDialogOption("Back to main menu", "rootNode")
        tree.addNode(titaniumMediumNode)
        # Titanium high node
        titaniumHighNode = DialogNode("nodeTitaniumHigh", "Titanium level now set to high.", statesToAdd = ["titaniumHighSignal_field" + str(fieldNum)], statesToRemove = ["titaniumLowSignal_field" + str(fieldNum), "titaniumMediumSignal_field" + str(fieldNum)])
        titaniumHighNode.addDialogOption("Back to main menu", "rootNode")
        tree.addNode(titaniumHighNode)

        # Change nutrient levels node (Lithium)
        changeNutrientLevelsNodeLit = DialogNode("changeLithiumLevel", "What level would you like the Lithium to be at in field #" + str(fieldNum) + "?", statesToAdd = [""], statesToRemove = [])
        changeNutrientLevelsNodeLit.addDialogOption("Lithium level: low", "nodeLithiumLow")
        changeNutrientLevelsNodeLit.addDialogOption("Lithium level: medium", "nodeLithiumMedium")
        changeNutrientLevelsNodeLit.addDialogOption("Lithium level: high", "nodeLithiumHigh")
        changeNutrientLevelsNodeLit.addDialogOption("Back to main menu", "rootNode")
        tree.addNode(changeNutrientLevelsNodeLit)

        # Lithium low node
        lithiumLowNode = DialogNode("nodeLithiumLow", "Lithium level now set to low.", statesToAdd = ["lithiumLowSignal_field" + str(fieldNum)], statesToRemove = ["lithiumMediumSignal_field" + str(fieldNum), "lithiumHighSignal_field" + str(fieldNum)])
        lithiumLowNode.addDialogOption("Back to main menu", "rootNode")
        tree.addNode(lithiumLowNode)
        # Lithium medium node
        lithiumMediumNode = DialogNode("nodeLithiumMedium", "Lithium level now set to medium.", statesToAdd = ["lithiumMediumSignal_field" + str(fieldNum)], statesToRemove = ["lithiumLowSignal_field" + str(fieldNum), "lithiumHighSignal_field" + str(fieldNum)])
        lithiumMediumNode.addDialogOption("Back to main menu", "rootNode")
        tree.addNode(lithiumMediumNode)
        # Lithium high node
        lithiumHighNode = DialogNode("nodeLithiumHigh", "Lithium level now set to high.", statesToAdd = ["lithiumHighSignal_field" + str(fieldNum)], statesToRemove = ["lithiumLowSignal_field" + str(fieldNum), "lithiumMediumSignal_field" + str(fieldNum)])
        lithiumHighNode.addDialogOption("Back to main menu", "rootNode")
        tree.addNode(lithiumHighNode)

        # Change nutrient levels node (Thorium)
        changeNutrientLevelsNodeTho = DialogNode("changeThoriumLevel", "What level would you like the Thorium to be at in field #" + str(fieldNum) + "?", statesToAdd = [""], statesToRemove = [])
        changeNutrientLevelsNodeTho.addDialogOption("Thorium level: low", "nodeThoriumLow")
        changeNutrientLevelsNodeTho.addDialogOption("Thorium level: medium", "nodeThoriumMedium")
        changeNutrientLevelsNodeTho.addDialogOption("Thorium level: high", "nodeThoriumHigh")
        changeNutrientLevelsNodeTho.addDialogOption("Back to main menu", "rootNode")
        tree.addNode(changeNutrientLevelsNodeTho)

        # Thorium low node
        thoriumLowNode = DialogNode("nodeThoriumLow", "Thorium level now set to low.", statesToAdd = ["thoriumLowSignal_field" + str(fieldNum)], statesToRemove = ["thoriumMediumSignal_field" + str(fieldNum), "thoriumHighSignal_field" + str(fieldNum)])
        thoriumLowNode.addDialogOption("Back to main menu", "rootNode")
        tree.addNode(thoriumLowNode)
        # Thorium medium node
        thoriumMediumNode = DialogNode("nodeThoriumMedium", "Thorium level now set to medium.", statesToAdd = ["thoriumMediumSignal_field" + str(fieldNum)], statesToRemove = ["thoriumLowSignal_field" + str(fieldNum), "thoriumHighSignal_field" + str(fieldNum)])
        thoriumMediumNode.addDialogOption("Back to main menu", "rootNode")
        tree.addNode(thoriumMediumNode)
        # Thorium high node
        thoriumHighNode = DialogNode("nodeThoriumHigh", "Thorium level now set to high.", statesToAdd = ["thoriumHighSignal_field" + str(fieldNum)], statesToRemove = ["thoriumLowSignal_field" + str(fieldNum), "thoriumMediumSignal_field" + str(fieldNum)])
        thoriumHighNode.addDialogOption("Back to main menu", "rootNode")
        tree.addNode(thoriumHighNode)

        # Change nutrient levels node (Barium)
        changeNutrientLevelsNodeBar = DialogNode("changeBariumLevel", "What level would you like the Barium to be at in field #" + str(fieldNum) + "?", statesToAdd = [""], statesToRemove = [])
        changeNutrientLevelsNodeBar.addDialogOption("Barium level: low", "nodeBariumLow")
        changeNutrientLevelsNodeBar.addDialogOption("Barium level: medium", "nodeBariumMedium")
        changeNutrientLevelsNodeBar.addDialogOption("Barium level: high", "nodeBariumHigh")
        changeNutrientLevelsNodeBar.addDialogOption("Back to main menu", "rootNode")
        tree.addNode(changeNutrientLevelsNodeBar)

        # Barium low node
        bariumLowNode = DialogNode("nodeBariumLow", "Barium level now set to low.", statesToAdd = ["bariumLowSignal_field" + str(fieldNum)], statesToRemove = ["bariumMediumSignal_field" + str(fieldNum), "bariumHighSignal_field" + str(fieldNum)])
        bariumLowNode.addDialogOption("Back to main menu", "rootNode")
        tree.addNode(bariumLowNode)
        # Barium medium node
        bariumMediumNode = DialogNode("nodeBariumMedium", "Barium level now set to medium.", statesToAdd = ["bariumMediumSignal_field" + str(fieldNum)], statesToRemove = ["bariumLowSignal_field" + str(fieldNum), "bariumHighSignal_field" + str(fieldNum)])
        bariumMediumNode.addDialogOption("Back to main menu", "rootNode")
        tree.addNode(bariumMediumNode)
        # Barium high node
        bariumHighNode = DialogNode("nodeBariumHigh", "Barium level now set to high.", statesToAdd = ["bariumHighSignal_field" + str(fieldNum)], statesToRemove = ["bariumLowSignal_field" + str(fieldNum), "bariumMediumSignal_field" + str(fieldNum)])
        bariumHighNode.addDialogOption("Back to main menu", "rootNode")
        tree.addNode(bariumHighNode)

        # OK node
        endNodeOK = DialogNode("endNodeOK", "Setting the nutrient levels in field " + str(fieldNum) + " to your selections.", statesToAdd = ["soilNutrientController_OK"], statesToRemove = [])
        tree.addNode(endNodeOK)
        # Cancel node
        endNodeCancel = DialogNode("endNodeCancel", "Selections have been canceled.", statesToAdd = ["soilNutrientController_Cancel"], statesToRemove = [])
        tree.addNode(endNodeCancel)

        # Store dialog tree in agent
        agent.setDialogTree(tree)


    # Dialog that shows what the current nutrient levels are in the soil
    def mkDialogSoilNutrientControllerCompleted(self, agent, fieldNum, nutrientSettings):
        tree = DialogTree(agent)

        # Root node (introduce the soil nutrient controller, give options to ask to change the nutrient levels)
        infoText = "Hello, I am the soil nutrient controller for Field #" + str(fieldNum) + ". The nutrient levels in the soil in Field #" + str(fieldNum) + " have already been set, and can not be changed further. They are:\n\n"
        for nutrient in nutrientSettings:
            nutrientLevelStr = "unknown"
            if (nutrientSettings[nutrient] == 1):
                nutrientLevelStr = "low"
            elif (nutrientSettings[nutrient] == 2):
                nutrientLevelStr = "medium"
            elif (nutrientSettings[nutrient] == 3):
                nutrientLevelStr = "high"

            infoText += "- " + str(nutrient) + ": " + nutrientLevelStr + "\n"

        rootNode = DialogNode("rootNode", infoText, statesToAdd = [], statesToRemove = [])
        rootNode.addDialogOption("Exit", "endNode")
        tree.addNode(rootNode)
        tree.setRoot(rootNode.name)

        # End node
        endNode = DialogNode("endNode", "Goodbye.", statesToAdd = [], statesToRemove = [])
        tree.addNode(endNode)


        # Store dialog tree in agent
        agent.setDialogTree(tree)


    # Dialog tree for crystal reactor
    def mkDialogCrystalReactor(self, agent, reactorNum):
        # floatVariablesToModify
        tree = DialogTree(agent)

        # Root node (introduce the soil nutrient controller, give options to ask to change the nutrient levels)
        rootNode = DialogNode("rootNode", "Hello, I am Crystal Reactor #" + str(reactorNum) + ".\nThe current resonance frequence is: {resonanceFreq} Hertz.\nThe allowable range is 0 to 10,000 Hz.", statesToAdd = [], statesToRemove = [])
        # Increase frequency
        rootNode.addDialogOption("Increase frequency by 1000 Hz", "rootNode", floatVariablesToModify={"resonanceFreq": 1000})
        rootNode.addDialogOption("Increase frequency by 100 Hz", "rootNode", floatVariablesToModify={"resonanceFreq": 100})
        rootNode.addDialogOption("Increase frequency by 10 Hz", "rootNode", floatVariablesToModify={"resonanceFreq": 10})
        rootNode.addDialogOption("Increase frequency by 1 Hz", "rootNode", floatVariablesToModify={"resonanceFreq": 1})
        # Decrease frequency
        rootNode.addDialogOption("Decrease frequency by 1000 Hz", "rootNode", floatVariablesToModify={"resonanceFreq": -1000})
        rootNode.addDialogOption("Decrease frequency by 100 Hz", "rootNode", floatVariablesToModify={"resonanceFreq": -100})
        rootNode.addDialogOption("Decrease frequency by 10 Hz", "rootNode", floatVariablesToModify={"resonanceFreq": -10})
        rootNode.addDialogOption("Decrease frequency by 1 Hz", "rootNode", floatVariablesToModify={"resonanceFreq": -1})
        # Exit
        rootNode.addDialogOption("Exit", "endNode")
        tree.addNode(rootNode)
        tree.setRoot(rootNode.name)

        # OK node
        endNodeOK = DialogNode("endNode", "Exiting crystal reactor controls.", statesToAdd = [], statesToRemove = [])
        tree.addNode(endNodeOK)


        # Store dialog tree in agent
        agent.setDialogTree(tree)
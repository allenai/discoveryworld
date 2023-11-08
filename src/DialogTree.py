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
            self.agent.attributes['states'].add(stateToAdd)
        for stateToRemove in currentNode.statesToRemove:
            self.agent.attributes['states'].remove(stateToRemove)            


    # Get the current node in the dialog tree
    def getCurrentNode(self, nodeName):
        return self.nodes[nodeName]

    # Returns what the agent is currently saying, and any options that the agent can say next. 
    def getCurrentDialog(self):
        # Get the current node
        currentNode = self.getCurrentNode(self.currentNodeName)

        # Get what this agent is currently saying
        currentNodeText = currentNode.currentNodeText

        # Get the options of what the user can say to this agent 
        dialogOptions = currentNode.dialogOptions
        # Filter to include only 'thingsToSay'
        dialogOptions = [dialogOption["thingToSay"] for dialogOption in dialogOptions]

        # Return the dialog options, and the states to add and remove
        return currentNodeText, dialogOptions

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
    
    def addDialogOption(self, thingToSay, nextNodeName):
        packed = {
            "thingToSay": thingToSay,
            "nextNodeName": nextNodeName,
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
        rootNode.addDialogOption("Can you collect food?", "collectFoodNode")
        rootNode.addDialogOption("Can you serve food?", "serveFoodNode")
        tree.addNode(rootNode)
        tree.setRoot(rootNode.name)

        # Collect food node
        collectFoodNode = DialogNode("collectFoodNode", "I will go collect food from the farm, and place it in the pot.", statesToAdd = ["collectSignal"], statesToRemove = [])
        collectFoodNode.addDialogOption("OK", "endNode")
        tree.addNode(collectFoodNode)
        

        # Serve food node 
        serveFoodNode = DialogNode("serveFoodNode", "I will serve food from the pot.", statesToAdd = ["serveSignal"], statesToRemove = [])
        serveFoodNode.addDialogOption("OK", "endNode")
        tree.addNode(serveFoodNode)
        
        # End node
        endNode = DialogNode("endNode", "Goodbye.", statesToAdd = [], statesToRemove = [])
        tree.addNode(endNode)

        # Store dialog tree in agent
        agent.setDialogTree(tree)


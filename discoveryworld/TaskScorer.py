# TaskScorer.py
from discoveryworld.objects import *
from discoveryworld.ActionHistory import *


#
#   Task Scorer
#   Holds all active tasks for a given world
#
class TaskScorer():
    # Constructor
    def __init__(self, world):
        self.tasks = []
        self.world = world


    # Add a task to the list
    def addTask(self, task):
        self.tasks.append(task)


    # Update the task progress
    def updateTick(self):
        for task in self.tasks:
            task.updateTick()


    # String representing task progress
    def taskProgressStr(self):
        outStr = "Task Progress:\n"
        for idx, task in enumerate(self.tasks):
            outStr += str(idx) + ": " + task.taskProgressStr() + "\n"

        return outStr



#
#   Task Maker
#   A generator for going from task name to a specific Task object
#
class TaskMaker():
    # Constructor
    def __init__(self, world):
        self.world = world

    # Make a task
    def makeTask(self, taskName:str, scoringInfo:dict=None):
        if (taskName == "EatMushroomTask"):
            return EatMushroomTask(self.world, scoringInfo)
        elif (taskName == "RustedKeyTask"):
            return RustedKeyTask(self.world, scoringInfo)
        elif (taskName == "ArcheologyDigTaskEasy"):
            return ArcheologyDigEasy(self.world, scoringInfo)
        elif (taskName == "ArcheologyDigTaskGenericRadioisotope"):
            return ArcheologyDigGenericRadioisotopes(self.world, scoringInfo)
        elif (taskName == "SoilNutrientTask"):
            return SoilNutrientTask(self.world, scoringInfo)
        elif (taskName == "RosettaStoneTask"):
            #return RosettaStoneTask(self.world, scoringInfo)
            pass
        elif (taskName == "ReactorTask"):
            return ReactorTask(self.world, scoringInfo)
            pass
        else:
            print("ERROR: UNKNOWN TASK NAME: " + taskName)
            exit(1)
            return None

#
#   Abstract class template for a specific task
#
class Task():
    # Constructor
    def __init__(self, taskName:str, taskDescription:str, world, scoringInfo:dict):
        self.taskName = taskName
        self.taskDescription = taskDescription
        self.world = world
        self.scoringInfo = scoringInfo
        self.score = 0                          # Current task score
        self.maxScore = 1                       # Maximum score
        self.completed = False                  # Is this task over?
        self.completedSuccessfully = False      # Did the task complete successfully?
        self.scoreCard = []                     # List of the subtasks in this task's scorecard
        self.criticalHypotheses = []            # List of critical hypotheses for this task


    # Task setup: Add any necessary objects to the world to perform the task.
    def taskSetup(self):
        pass

    def getScore(self):
        return self.score

    def getScoreNormalized(self):
        return self.score / self.maxScore

    def isCompleted(self):
        return self.completed

    def isCompletedSuccessfully(self):
        return self.completedSuccessfully

    # Update the task progress
    def updateTick(self):
        pass

    # String representing task progress
    def taskProgressStr(self):
        outStr = ""
        outStr += "Task Progress (" + self.taskName + "):  Score: " + str(self.score) + ", MaxScore: " + str(self.maxScore) + ", Normalized Score: " + str(format(self.getScoreNormalized(), '.2f')) + ", Completed: " + str(self.completed) + ", Completed Successfully: " + str(self.completedSuccessfully)
        outStr += "\nScorecard:"
        for element in self.scoreCard:
            #outStr += "\n" + element.name + ": " + str(element.score) + "/" + str(element.maxScore) + ", Completed: " + str(element.completed)
            # As above, but with constant witdh formatting, completed should be 'completed' or 'not completed', and the task description should be there too
            isCompleted = "incomplete"
            if (element.completed == True):
                isCompleted = "completed"
            outStr += "\n - " + element.name.ljust(40) + " " + str(element.score).rjust(2) + " /" + str(element.maxScore).rjust(2) + "  " + str(isCompleted).ljust(15) + " " + element.description
        # Critical Hypotheses
        outStr += "\nCritical Hypotheses:"
        for hypothesis in self.criticalHypotheses:
            outStr += "\n - " + hypothesis


        return outStr

    # Get task progress as a dictionary
    def taskProgressDict(self):
        outDict = {}

        outDict["taskName"] = self.taskName
        outDict["taskDescription"] = self.taskDescription
        outDict["score"] = self.score
        outDict["maxScore"] = self.maxScore
        outDict["completed"] = self.completed
        outDict["completedSuccessfully"] = self.completedSuccessfully
        outDict["scoreCard"] = self.getScorecard()
        outDict["criticalHypotheses"] = self.criticalHypotheses

        return outDict

    # Get the scorecard elements as a form that can be serialized to JSON
    def getScorecard(self):
        out = []
        for element in self.scoreCard:
            out.append(element.toDict())
        return out




#
#   Scorecard element: A specific subtask of a larger task
#
class ScorecardElement():
    # Constructor
    def __init__(self, name:str, description:str, maxScore:int):
        self.name = name
        self.description = description
        self.maxScore = maxScore
        self.score = 0
        self.completed = False
        self.associatedUUIDs = []       # List of UUIDs of objects associated with this scorecard element
        self.associatedNotes = ""       # Notes associated with this scorecard element

    # Update the score
    def updateScore(self, score:int, completed:bool, associatedUUIDs:list=[], associatedNotes:str=""):
        self.score = score
        self.completed = completed
        self.associatedUUIDs = associatedUUIDs
        self.associatedNotes = associatedNotes

    def toDict(self):
        out = {}
        out["name"] = self.name
        out["description"] = self.description
        out["maxScore"] = self.maxScore
        out["score"] = self.score
        out["completed"] = self.completed
        out["associatedUUIDs"] = self.associatedUUIDs
        out["associatedNotes"] = self.associatedNotes
        return out


#
#   Specific Task: Agents eating space mushrooms without getting sick
#
class EatMushroomTask(Task):
    # Constructor
    def __init__(self, world, scoringInfo):
        taskDescription = "The only food on this planet are local mushrooms, but after eating them, the colonist are sometimes getting sick.  Your task is to figure out why people are getting sick, and to prevent it.  You must demonstrate this by having 10 colonists successfully eat mushrooms without eventually getting sick."
        taskDescription += "Since the food causes only mild illness, and getting the colony established is important, the colonists have volunteered to be test subjects.  The Chef in the Cafeteria can help you collect mushrooms, serve mushrooms from the cafeteria pot to the tables, and let the colonists know a meal is ready to eat, when you're ready."
        Task.__init__(self, "EatMushroomTask", taskDescription, world, scoringInfo)
        self.score = 0
        self.maxScore = 10                       # Maximum score
        self.agentsToMonitorForSickness = {}        # Key: agent name, value: step they were added


    # Task setup: Add any necessary objects to the world to perform the task.
    def taskSetup(self):
        # Add the colonists?
        pass

    # Update the task progress
    def updateTick(self):
        # Monitoring task 1: Check if any agents have just eaten a mushroom
        # List of names of agents to check for whether they've just eaten a mushroom
        agentsToCheck = []
        for i in range (0, 5):
            agentsToCheck.append("Colonist " + str(i))

        for agent in self.world.agents:
            if agent.name in agentsToCheck:
                # Check if they have eaten a mushroom

                # Check if they successfully ate something on the last tick
                lastAction = agent.actionHistory.getLastStepAction()
                if (lastAction != None) and (lastAction['actionType'] == ActionType.EAT) and (lastAction['success'] == True):
                    # Check if it was a mushroom
                    if (lastAction['arg1'].name == "mushroom"):
                        #self.score += 1
                        self.agentsToMonitorForSickness[agent.name] = self.world.getStepCounter()


        # Monitoring task 2: Check if any agents that recently ate a mushroom are now sick
        agentsToCheckForSickess = list(self.agentsToMonitorForSickness.keys())      # Deep copy, so we can delete from the original without changing keys while iterating
        for agentName in agentsToCheckForSickess:
            # Check if the agent is sick
            agent = self.world.getAgentByName(agentName)
            if (agent.attributes['isPoisoned'] == True):
                # Reset score to 0
                print("Agent " + agentName + " is sick!  Score reset to 0.")
                self.score = 0
            else:
                # Check if the agent has been well for 100 steps
                if (self.world.getStepCounter() - self.agentsToMonitorForSickness[agentName] >= 100):
                    # If they've been well for 100 steps, increment the score, and remove the monitor
                    self.score += 1
                    del self.agentsToMonitorForSickness[agentName]


        # Monitoring task 3: Check if the task is complete
        if (self.score >= self.maxScore):
            self.completed = True
            self.completedSuccessfully = True
            print("Task completed successfully: " + self.taskName)
        elif (self.score < self.maxScore):
            self.completed = False
            self.completedSuccessfully = False


#
#   Specific Task: Rusted key task
#
class RustedKeyTask(Task):
    # Constructor
    def __init__(self, world, scoringInfo):
        taskDescription = "You were venturing into the wilderness of Planet X to a storage shed to fetch some supplies. The shed door locked behind you, and your key appears too rusted to work in the lock. "
        taskDescription += "You remember one of the other colonists mentioning that some combination of the chemicals in the shed could make a rust remover, but you can't remember the details. "
        taskDescription += "You need to figure out a way to remove the rust from the key, and use it to open the shed door, and make your way back to the colony. "
        taskDescription += "You have no means of communication with the other colonists, and must figure this out on your own. \n"
        taskDescription += "Some helpful notes: \n"
        taskDescription += "1. The rusted key is in the shed. \n"
        taskDescription += "2. The shed door is locked, and will only open using a non-rusted key. \n"
        taskDescription += "3. You can mix chemicals in the jar in the shed. Just use a chemical dispenser on the jar to add chemicals to the jar. \n"
        taskDescription += "4. Chemicals placed in the same jar will automatically mix, though it may take a step or two for this to happen. \n"
        taskDescription += "5. Placing the rusted key into the jar will automatically apply the chemicals to the key.  If the chemical mixture is correct, the rust will be removed, though it may take a step or two. \n"
        taskDescription += "6. If you need to clean the jar of chemicals to try a new combination, use the bottle washer on the jar. \n"
        taskDescription += "7. When you have successfully rerusted the key and opened the door, please leave the shed. \n"
        ## taskDescription += "HERE'S A WALKTHROUGH/HINT: To complete this task, you need to pick up the jar, put 1 unit of Chemical A and 2 units of Chemical C into the jar, and then put the key into the jar.  The key will change from rusted to not rusted.  Then you can open the door, walk 3 steps out, and the task will be completed."

        Task.__init__(self, "RustedKeyTask", taskDescription, world, scoringInfo)
        self.score = 0
        self.maxScore = 2                       # Maximum score

        #scoringInfo['dispensers'] = [dispenser1, dispenser2, dispenser3]
        #scoringInfo['mixingJar'] = mixingJar
        #scoringInfo['bottleCleaner'] = BottleCleaner
        #scoringInfo['key'] = rustyKey

        # Scorecard elements (TODO)
        # Taking critical objects
        self.scorecardKey = ScorecardElement("Take key", "The key has been in an agent's inventory", maxScore=1)
        self.scoreCard.append(self.scorecardKey)
        self.scorecardJar = ScorecardElement("Take jar", "The mixing jar has been in an agent's inventory", maxScore=1)
        self.scoreCard.append(self.scorecardJar)

        # Has used each chemical dispenser
        self.scorecardUsedDispensers = ScorecardElement("Use each chemical dispenser", "Each chemical dispenser has been used", maxScore=3)
        self.scoreCard.append(self.scorecardUsedDispensers)

        # Has used the bottle cleaner
        self.scorecardUsedBottleCleaner = ScorecardElement("Use bottle cleaner", "The bottle cleaner has been used", maxScore=1)
        self.scoreCard.append(self.scorecardUsedBottleCleaner)

        # Has a mixture containing more than one chemical in the jar
        self.scorecardMixtureInJar = ScorecardElement("Mix chemicals in jar", "The jar contains a mixture of chemicals", maxScore=1)
        self.scoreCard.append(self.scorecardMixtureInJar)

        # Has placed the key in the jar
        self.scorecardKeyInJar = ScorecardElement("Place key in jar", "The key has been placed in the jar at least once", maxScore=1)
        self.scoreCard.append(self.scorecardKeyInJar)

        # Key is not rusted
        self.scorecardKeyNotRusted = ScorecardElement("Key is not rusted", "The key is not rusted (includes levels for reduced amounts of rust)", maxScore=3)
        self.scoreCard.append(self.scorecardKeyNotRusted)

        # Agent is outside
        self.scorecardAgentOutside = ScorecardElement("Agent is outside", "The agent is outside the shed", maxScore=1)
        self.scoreCard.append(self.scorecardAgentOutside)

        # Add hypotheses from scoringInfo
        self.criticalHypotheses = scoringInfo["criticalHypotheses"]


    # Task setup: Add any necessary objects to the world to perform the task.
    def taskSetup(self):
        # Add the colonists?
        pass

    # Update the task progress
    def updateTick(self):
        # Do not update the score if the task is already marked as completed
        if (self.completed == True):
            return

        # Check whether key has been in agents inventory
        if (not self.scorecardKey.completed):
            key = self.scoringInfo['key']
            if (key.parentContainer != None) and (key.parentContainer.type == "agent"):
                self.scorecardKey.updateScore(1, True, associatedUUIDs=[key.uuid, key.parentContainer.uuid], associatedNotes="The key has been in an agent's (UUID: " + str(key.parentContainer.uuid) + ") inventory")

        # Check whether jar has been in agents inventory
        if (not self.scorecardJar.completed):
            jar = self.scoringInfo['mixingJar']
            if (jar.parentContainer != None) and (jar.parentContainer.type == "agent"):
                self.scorecardJar.updateScore(1, True, associatedUUIDs=[jar.uuid, jar.parentContainer.uuid], associatedNotes="The jar has been in an agent's (UUID: " + str(jar.parentContainer.uuid) + ") inventory")

        # Check whether each chemical dispenser has been used
        if (not self.scorecardUsedDispensers.completed):
            usedDispensers = set()
            for agent in self.world.agents:
                for dispenser in self.scoringInfo['dispensers']:
                    # query the action history
                    foundActions = agent.actionHistory.queryActionObjects(ActionType.USE, arg1=dispenser, arg2=self.scoringInfo['mixingJar'], stopAtFirst=True)
                    if (len(foundActions) > 0):
                        usedDispensers.add(dispenser.uuid)

            isCompleted = False
            if (len(usedDispensers) == 3):
                isCompleted = True
            associatedNotes = str(len(usedDispensers)) + " of " + str(len(self.scoringInfo["dispensers"])) + " dispensers have been used"
            self.scorecardUsedDispensers.updateScore(len(usedDispensers), isCompleted, associatedUUIDs=list(usedDispensers), associatedNotes=associatedNotes)

        # Check whether the bottle cleaner has been used
        if (not self.scorecardUsedBottleCleaner.completed):
            usedBottleCleaner = False
            for agent in self.world.agents:
                foundActions = agent.actionHistory.queryActionObjects(ActionType.USE, arg1=self.scoringInfo['bottleCleaner'], arg2=self.scoringInfo['mixingJar'], stopAtFirst=True)
                if (len(foundActions) > 0):
                    usedBottleCleaner = True
                    break
            if (usedBottleCleaner == True):
                self.scorecardUsedBottleCleaner.updateScore(1, usedBottleCleaner, associatedUUIDs=[self.scoringInfo['bottleCleaner'].uuid], associatedNotes="The bottle cleaner has been used")

        # Check whether the jar contains a mixture of chemicals
        if (not self.scorecardMixtureInJar.completed):
            # Check to see whether the jar contains a substance, and if the substance has a mixture (mixtureDict)
            for cObj in self.scoringInfo['mixingJar'].contents:
                if (cObj.type == "substance"):
                    mixtureSubstances = cObj.attributes['mixtureDict'].keys()
                    if (len(mixtureSubstances) > 1):
                        self.scorecardMixtureInJar.updateScore(1, True, associatedUUIDs=[cObj.uuid], associatedNotes="The mixing jar has contained two or more chemicals in a mixture (" + str(", ".join(mixtureSubstances)) + ")")
                        break

        # Check whether the key is in the jar
        if (not self.scorecardKeyInJar.completed):
            # Check whether the key's parent container is the jar
            key = self.scoringInfo['key']
            if (key.parentContainer != None) and (key.parentContainer.uuid == self.scoringInfo['mixingJar'].uuid):
                self.scorecardKeyInJar.updateScore(1, True, associatedUUIDs=[key.uuid, key.parentContainer.uuid], associatedNotes="The key has been placed in the jar at least once")

        # Check whether the key is not rusted
        if (not self.scorecardKeyNotRusted.completed):
            # Check the rust level of the key
            key = self.scoringInfo['key']
#        self.attributes['isRusted'] = isRusted                    # Is the key rusted?
#        self.attributes['rustLevel'] = 3 if isRusted else 0       # Description of the rust (0=none, 1=light, 2=medium, 3=heavy)
            if (key.attributes['isRusted'] == False):
                self.scorecardKeyNotRusted.updateScore(3, True, associatedUUIDs=[key.uuid], associatedNotes="The key is not rusted")
            else:
                # Partial
                rustScore = 3 - key.attributes['rustLevel']
                if (rustScore == 3):
                    self.scorecardKeyNotRusted.updateScore(rustScore, completed=False, associatedUUIDs=[key.uuid], associatedNotes="The key is fully rusted")
                else:
                    self.scorecardKeyNotRusted.updateScore(rustScore, completed=False, associatedUUIDs=[key.uuid], associatedNotes="The key is partially rusted")

        # Check to see whether one or more agents are outside of the room
        if (not self.scorecardAgentOutside.completed):
            # Bounds
            x0 = 16
            y0 = 10
            x1 = 16+6
            y1 = 10+3
            isOutside = False
            for agent in self.world.agents:
                # Check if the agent is outside the room
                # Get agent position
                isWithinBounds = agent.isWithinLocationBounds(x0, y0, x1, y1)
                if (isWithinBounds == False):
                    isOutside = True
                    break

            if (isOutside == True):
                self.scorecardAgentOutside.updateScore(1, True, associatedUUIDs=[], associatedNotes="The agent is outside the shed")


        # Update score
        score = 0
        maxScore = 0
        for element in self.scoreCard:
            score += element.score
            maxScore += element.maxScore
        self.score = score
        self.maxScore = maxScore

        # Check whether the task is complete
        # Here, the task is complete if the key is not rusted, and the agent is outside
        if (self.scorecardKeyNotRusted.completed and self.scorecardAgentOutside.completed):
            self.completed = True
            self.completedSuccessfully = True
            print("Task completed successfully: " + self.taskName)
        else:
            self.completed = False
            self.completedSuccessfully = False



#
#   Specific Task: Archeology dig task
#
class ArcheologyDigEasy(Task):
    # Constructor
    def __init__(self, world, scoringInfo):
        taskDescription = "You are on an archeological dig on Planet X.  3 ancient sites have been found. "
        taskDescription += "Your task is to excavate the sites, and date any artifacts with the radiocarbon meter.  Then, once completed, place the red flag beside the sign of the dig site with the oldest artifact. "

        Task.__init__(self, "ArcheologyDigTaskEasy", taskDescription, world, scoringInfo)
        self.score = 0
        self.maxScore = 1                       # Maximum score
        self.uncoveredArtifacts = set()

        self.scorecardRadiocarbonMeter = ScorecardElement("Take radiocarbon meter", "The radiocarbon meter has been in an agent's inventory", maxScore=1)
        self.scoreCard.append(self.scorecardRadiocarbonMeter)
        self.scorecardShovel = ScorecardElement("Take shovel", "The shovel has been in an agent's inventory", maxScore=1)
        self.scoreCard.append(self.scorecardShovel)
        self.scorecardFlag = ScorecardElement("Take flag", "The flag has been in an agent's inventory", maxScore=1)
        self.scoreCard.append(self.scorecardFlag)

        self.scorecardArtifactsUncovered = ScorecardElement("Artifacts uncovered", "The artifacts have been uncovered", maxScore=3)
        self.scoreCard.append(self.scorecardArtifactsUncovered)

        self.scorecardArtifactsDated = ScorecardElement("Artifacts dated", "The artifacts have been dated with the radiocarbon meter", maxScore=3)
        self.scoreCard.append(self.scorecardArtifactsDated)

        self.scorecardFlagPlaced = ScorecardElement("Flag placed", "The flag has been placed in the correct location", maxScore=1)
        self.scoreCard.append(self.scorecardFlagPlaced)

        # Critical Hypotheses
        self.criticalHypotheses = scoringInfo["criticalHypotheses"]

    # scoringInfo["unknownArtifacts"] = []
    # scoringInfo["signs"] = []
    # scoringInfo["targetSign"] = sign
    # scoringInfo["radioCarbonMeter"] = radioCarbonMeter
    # scoringInfo["shovel"] = shovel
    # scoringInfo["flag"] = flag


    # Task setup: Add any necessary objects to the world to perform the task.
    def taskSetup(self):
        # Add the colonists?
        pass

    def initialize(self):
        pass

    # Update the task progress
    def updateTick(self):
        # Do not update the score if the task is already marked as completed
        if (self.completed == True):
            return

        # Check if they have the radioisotope meter in an agent's inventory
        if (not self.scorecardRadiocarbonMeter.completed):
            radioisotopeMeterContainer = self.scoringInfo["radioCarbonMeter"].parentContainer
            if (radioisotopeMeterContainer != None):
                if (radioisotopeMeterContainer.type == "agent"):
                    self.scorecardRadiocarbonMeter.updateScore(score=1, completed=True, associatedUUIDs=[self.scoringInfo["radioCarbonMeter"].uuid], associatedNotes="The radiocarbon meter has been in the inventory of the agent with uuid " + str(self.scoringInfo["radioCarbonMeter"].uuid))

        # Check if they have the shovel in an agent's inventory
        if (not self.scorecardShovel.completed):
            shovelContainer = self.scoringInfo["shovel"].parentContainer
            if (shovelContainer != None):
                if (shovelContainer.type == "agent"):
                    self.scorecardShovel.updateScore(score=1, completed=True, associatedUUIDs=[self.scoringInfo["shovel"].uuid], associatedNotes="The shovel has been in the inventory of the agent with uuid " + str(shovelContainer.uuid))

        # Check if they have the flag in an agent's inventory
        if (not self.scorecardFlag.completed):
            flagContainer = self.scoringInfo["flag"].parentContainer
            if (flagContainer != None):
                if (flagContainer.type == "agent"):
                    self.scorecardFlag.updateScore(score=1, completed=True, associatedUUIDs=[self.scoringInfo["flag"].uuid], associatedNotes="The flag has been in the inventory of the agent with uuid " + str(flagContainer.uuid))

        # Check if the 3 unknown objects have been uncovered
        if (not self.scorecardArtifactsUncovered.completed):
            # Measure the number of unknown artifacts that have been uncovered
            for artifact in self.scoringInfo["unknownArtifacts"]:
                parentContainer = artifact.parentContainer
                if (parentContainer != None):
                    if (parentContainer.type == "soil"):
                        if (parentContainer.attributes["hasHole"] == True):
                            self.uncoveredArtifacts.add(artifact.uuid)
                    else:
                        # If not in soil, then it's been moved (which means it must have been uncovered)
                        self.uncoveredArtifacts.add(artifact.uuid)

            numArtifactsUncovered = len(self.uncoveredArtifacts)

            # Update the scorecard
            isComplete = False
            if (numArtifactsUncovered >= 3):
                isComplete = True
            self.scorecardArtifactsUncovered.updateScore(score=numArtifactsUncovered, completed=isComplete, associatedUUIDs=list(self.uncoveredArtifacts), associatedNotes="The following artifacts have been uncovered: " + str(self.uncoveredArtifacts))


        # Check if the radioisotope meter has been used on 3 seed artifacts
        if (not self.scorecardArtifactsDated.completed):
            seedArtifactsDated = set()
            for agent in self.world.getUserAgents():
                for artifact in self.scoringInfo["unknownArtifacts"]:
                    foundActions = agent.actionHistory.queryActionObjects(ActionType.USE, arg1=self.scoringInfo["radioCarbonMeter"], arg2=artifact, stopAtFirst=True)
                    if (len(foundActions) > 0):
                        seedArtifactsDated.add(artifact.uuid)

            numArtifactsDated = len(seedArtifactsDated)
            isComplete = False
            if (numArtifactsDated >= 3):
                isComplete = True
            self.scorecardArtifactsDated.updateScore(score=numArtifactsDated, completed=isComplete, associatedUUIDs=list(seedArtifactsDated), associatedNotes="The following artifacts have been dated: " + str(seedArtifactsDated))


        # Check if the flag has been placed near ANY of the signs (+/- 2 grid spaces).
        if (not self.scorecardFlagPlaced.completed):
            # First, check to see if the flag has been placed
            flagPlaced = False
            placedCorrectly = False
            if (self.scoringInfo["flag"].parentContainer == None):
                for sign in self.scoringInfo["signs"]:
                    distance = sign.distanceTo(self.scoringInfo["flag"])
                    if (distance <= 2):
                        flagPlaced = True
                        placedNearSignUUID = sign.uuid
                        # Check if the flag has been placed near the correct sign
                        if (sign.uuid == self.scoringInfo["targetSign"].uuid):
                            placedCorrectly = True
                        break

            # Update the scorecard
            if (flagPlaced == True):
                if (placedCorrectly == True):
                    self.scorecardFlagPlaced.updateScore(score=1, completed=True, associatedUUIDs=[self.scoringInfo["flag"].uuid, placedNearSignUUID], associatedNotes="The flag has been placed near the correct sign")
                else:
                    self.scorecardFlagPlaced.updateScore(score=0, completed=True, associatedUUIDs=[self.scoringInfo["flag"].uuid, placedNearSignUUID], associatedNotes="The flag has been placed near an incorrect sign")

            # If the flag has been placed, the task is complete
            if (flagPlaced == True):
                self.completed = True
                if (placedCorrectly == True):
                    self.completedSuccessfully = True
                else:
                    self.completedSuccessfully = False
            else:
                self.completed = False
                self.completedSuccessfully = False

        # Update the score, as the sum of the scorecard elements
        self.score = 0
        self.maxScore = 0
        for element in self.scoreCard:
            self.score += element.score
            self.maxScore += element.maxScore



#
#   Specific Task: Archeology dig task (generic radioisotopes)
#
class ArcheologyDigGenericRadioisotopes(Task):
    # Constructor
    def __init__(self, world, scoringInfo):
        # TODO: modify description
        taskDescription = "You are on an archeological dig on Planet X.  6 sites of suspected ancient artifacts have been found, 3 of which have already been uncovered. "
        taskDescription += "It's not clear how or if radioisotope dating works on Planet X, or how it would differ from Earth, but your task is to figure out if it can be used. "
        taskDescription += "Your task is to excavate the remaining sites, and figure out a way to use the radioisotope meter to approximately date the artifacts.  Then, once completed, place the red flag beside the sign of the dig site with the oldest artifact. "

        Task.__init__(self, "ArcheologyDigTaskGenericRadioisotope", taskDescription, world, scoringInfo)
        self.score = 0
        self.maxScore = 1                       # Maximum score

        self.uncoveredArtifacts = set()         # A list of the artifacts that have been uncovered


        # Scorecard elements (TODO)
        # Taking critical objects
        self.scorecardRadioisotopeMeter = ScorecardElement("Take radioisotope meter", "The radioisotope meter has been in an agent's inventory", maxScore=1)
        self.scoreCard.append(self.scorecardRadioisotopeMeter)
        self.scorecardShovel = ScorecardElement("Take shovel", "The shovel has been in an agent's inventory", maxScore=1)
        self.scoreCard.append(self.scorecardShovel)
        self.scorecardFlag = ScorecardElement("Take flag", "The flag has been in an agent's inventory", maxScore=1)
        self.scoreCard.append(self.scorecardFlag)

        # 3 unknown objects uncovered
        self.scorecardUncoveredArtifacts = ScorecardElement("Uncover 3 unknown artifacts", "3 unknown artifacts have been uncovered", maxScore=3)
        self.scoreCard.append(self.scorecardUncoveredArtifacts)

        # Radioisotope meter used on 3 seed artifacts
        self.scorecardRadioisotopeMeterUsedSeed = ScorecardElement("Use radioisotope meter (seed)", "The radioisotope meter has been used on 3 seed artifacts", maxScore=3)
        self.scoreCard.append(self.scorecardRadioisotopeMeterUsedSeed)

        # Radioisotope meter used on 3 unknown artifacts
        self.scorecardRadioisotopeMeterUsedUnknown = ScorecardElement("Use radioisotope meter on (unknown)", "The radioisotope meter has been used on 3 unknown artifacts", maxScore=3)
        self.scoreCard.append(self.scorecardRadioisotopeMeterUsedUnknown)

        # Flag moved to correct location (or not) -- ends task
        self.scorecardFlagPlaced = ScorecardElement("Move flag to correct location", "The flag has been moved to the correct location", maxScore=1)
        self.scoreCard.append(self.scorecardFlagPlaced)

        # Add hypotheses from scoringInfo
        self.criticalHypotheses = scoringInfo["criticalHypotheses"]

        # Scoring Info passed from the scenario
        # scoringInfo["seedArtifacts"] = []
        # scoringInfo["unknownArtifacts"] = []
        # scoringInfo["radioisotopeMeter"] = radioisotopeMeter
        # scoringInfo["shovel"] = shovel
        # scoringInfo["flag"] = flag
        # scoringInfo["signs"] = []
        # scoringInfo["targetSign"]  # The oldest sign, where the flag should be placed

    # Task setup: Add any necessary objects to the world to perform the task.
    def taskSetup(self):
        # Add the colonists?
        pass

    def initialize(self):
        pass

    # Update the task progress
    def updateTick(self):
        # Do not update the score if the task is already marked as completed
        if (self.completed == True):
            return

        # Check if they have the radioisotope meter in an agent's inventory
        if (not self.scorecardRadioisotopeMeter.completed):
            radioisotopeMeterContainer = self.scoringInfo["radioisotopeMeter"].parentContainer
            if (radioisotopeMeterContainer != None):
                if (radioisotopeMeterContainer.type == "agent"):
                    self.scorecardRadioisotopeMeter.updateScore(score=1, completed=True, associatedUUIDs=[self.scoringInfo["radioisotopeMeter"].uuid], associatedNotes="The radioisotope meter has been in the inventory of the agent with uuid " + str(self.scoringInfo["radioisotopeMeter"].uuid))

        # Check if they have the shovel in an agent's inventory
        if (not self.scorecardShovel.completed):
            shovelContainer = self.scoringInfo["shovel"].parentContainer
            if (shovelContainer != None):
                if (shovelContainer.type == "agent"):
                    self.scorecardShovel.updateScore(score=1, completed=True, associatedUUIDs=[self.scoringInfo["shovel"].uuid], associatedNotes="The shovel has been in the inventory of the agent with uuid " + str(shovelContainer.uuid))

        # Check if they have the flag in an agent's inventory
        if (not self.scorecardFlag.completed):
            flagContainer = self.scoringInfo["flag"].parentContainer
            if (flagContainer != None):
                if (flagContainer.type == "agent"):
                    self.scorecardFlag.updateScore(score=1, completed=True, associatedUUIDs=[self.scoringInfo["flag"].uuid], associatedNotes="The flag has been in the inventory of the agent with uuid " + str(flagContainer.uuid))

        # Check if the 3 unknown objects have been uncovered
        if (not self.scorecardUncoveredArtifacts.completed):
            # Measure the number of unknown artifacts that have been uncovered
            for artifact in self.scoringInfo["unknownArtifacts"]:
                parentContainer = artifact.parentContainer
                if (parentContainer != None):
                    if (parentContainer.type == "soil"):
                        if (parentContainer.attributes["hasHole"] == True):
                            self.uncoveredArtifacts.add(artifact.uuid)
                    else:
                        # If not in soil, then it's been moved (which means it must have been uncovered)
                        self.uncoveredArtifacts.add(artifact.uuid)

            numArtifactsUncovered = len(self.uncoveredArtifacts)

            # Update the scorecard
            isComplete = False
            if (numArtifactsUncovered >= 3):
                isComplete = True
            self.scorecardUncoveredArtifacts.updateScore(score=numArtifactsUncovered, completed=isComplete, associatedUUIDs=list(self.uncoveredArtifacts), associatedNotes="The following artifacts have been uncovered: " + str(self.uncoveredArtifacts))


        # Check if the radioisotope meter has been used on 3 seed artifacts
        if (not self.scorecardRadioisotopeMeterUsedSeed.completed):
            seedArtifactsDated = set()
            for agent in self.world.getUserAgents():
                for artifact in self.scoringInfo["seedArtifacts"]:
                    foundActions = agent.actionHistory.queryActionObjects(ActionType.USE, arg1=self.scoringInfo["radioisotopeMeter"], arg2=artifact, stopAtFirst=True)
                    if (len(foundActions) > 0):
                        seedArtifactsDated.add(artifact.uuid)

            numArtifactsDated = len(seedArtifactsDated)
            isComplete = False
            if (numArtifactsDated >= 3):
                isComplete = True
            self.scorecardRadioisotopeMeterUsedSeed.updateScore(score=numArtifactsDated, completed=isComplete, associatedUUIDs=list(seedArtifactsDated), associatedNotes="The following seed artifacts have been dated: " + str(seedArtifactsDated))

        # Check if the radioisotope meter has been used on 3 unknown artifacts
        if (not self.scorecardRadioisotopeMeterUsedUnknown.completed):
            unknownArtifactsDated = set()
            for agent in self.world.getUserAgents():
                for artifact in self.scoringInfo["unknownArtifacts"]:
                    foundActions = agent.actionHistory.queryActionObjects(ActionType.USE, arg1=self.scoringInfo["radioisotopeMeter"], arg2=artifact, stopAtFirst=True)
                    if (len(foundActions) > 0):
                        unknownArtifactsDated.add(artifact.uuid)

            numArtifactsDated = len(unknownArtifactsDated)
            isComplete = False
            if (numArtifactsDated >= 3):
                isComplete = True
            self.scorecardRadioisotopeMeterUsedUnknown.updateScore(score=numArtifactsDated, completed=isComplete, associatedUUIDs=list(unknownArtifactsDated), associatedNotes="The following unknown artifacts have been dated: " + str(unknownArtifactsDated))


        # Check if the flag has been placed near ANY of the signs (+/- 2 grid spaces).
        if (not self.scorecardFlagPlaced.completed):
            # First, check to see if the flag has been placed
            flagPlaced = False
            placedCorrectly = False
            if (self.scoringInfo["flag"].parentContainer == None):
                for sign in self.scoringInfo["signs"]:
                    distance = sign.distanceTo(self.scoringInfo["flag"])
                    if (distance <= 2):
                        flagPlaced = True
                        placedNearSignUUID = sign.uuid
                        # Check if the flag has been placed near the correct sign
                        if (sign.uuid == self.scoringInfo["targetSign"].uuid):
                            placedCorrectly = True
                        break

            # Update the scorecard
            if (flagPlaced == True):
                if (placedCorrectly == True):
                    self.scorecardFlagPlaced.updateScore(score=1, completed=True, associatedUUIDs=[self.scoringInfo["flag"].uuid, placedNearSignUUID], associatedNotes="The flag has been placed near the correct sign")
                else:
                    self.scorecardFlagPlaced.updateScore(score=0, completed=True, associatedUUIDs=[self.scoringInfo["flag"].uuid, placedNearSignUUID], associatedNotes="The flag has been placed near an incorrect sign")

            # If the flag has been placed, the task is complete
            if (flagPlaced == True):
                self.completed = True
                if (placedCorrectly == True):
                    self.completedSuccessfully = True
                else:
                    self.completedSuccessfully = False
            else:
                self.completed = False
                self.completedSuccessfully = False

        # Update the score, as the sum of the scorecard elements
        self.score = 0
        self.maxScore = 0
        for element in self.scoreCard:
            self.score += element.score
            self.maxScore += element.maxScore



#
#   Specific Task: Soil Nutrient Task
#
class SoilNutrientTask(Task):
    # Constructor
    def __init__(self, world, scoringInfo):
        # TODO: modify description
        # ["potassium", "titanium", "lithium", "thorium", "barium"]
        taskDescription = "You are at a botanical research station on Planet X.  An species of plant has been identified that appears to grow very quickly in the presence of an unusual nutrient uncommon on Earth. "
        taskDescription += "Other scientists have narrowed down the nutrient to be one of the following: Potassium, Titanium, Lithium, Thorium, or Barium. "
        taskDescription += "Your task is to figure out which nutrient it is, and what specific amount of the nutrient (low, medium, or high) is required in the soil for the plant to grow. "
        taskDescription += "To support your work, a pilot field was set up with 12 plots of soil, each with a different combination of nutrients.  The pilot field is located to the south west part of the research station. "
        taskDescription += "The research station is equipped with three test fields, where you can configure the nutrient levels in the field using the nearby soil nutrient controller. Once you configure the nutrients for a field, it can't be changed again."
        taskDescription += "Under the right conditions, the plant tends to grow very quickly, so you should be able to see the results of your work within a few steps. "
        taskDescription += "Inside the storage facility are some tools that may be helpful for you work, including a soil nutrient meter, a jar of seeds, and a shovel. "
        taskDescription += "To plant the seeds, dig a hole in the soil, place a seed in the hole, then put the soil back into the hole.  If the conditions are correct, the plant will grow from the seed. "
        taskDescription += "As part of your discovery process, you should grow at least 2 new plants to maturity. "

        Task.__init__(self, "SoilNutrientTask", taskDescription, world, scoringInfo)
        self.score = 0
        self.maxScore = 6                       # Maximum score

        self.newSeedsPlanted = set()            # New seeds planted since the start of the task
        self.newPlantsGrown = set()             # New plants grown since the start of the task

        # Scorecard elements
        self.scorecardSoilNutrientMeterPresent = ScorecardElement("Soil Nutrient Meter Present", "The soil nutrient meter has been in an agent's inventory", maxScore=1)
        self.scoreCard.append(self.scorecardSoilNutrientMeterPresent)
        self.scorecardShovelPresent = ScorecardElement("Shovel Present", "The shovel has been in an agent's inventory", maxScore=1)
        self.scoreCard.append(self.scorecardShovelPresent)
        self.scorecardJarPresent = ScorecardElement("Seed Jar Present", "The seed jar has been in an agent's inventory", maxScore=1)
        self.scoreCard.append(self.scorecardJarPresent)
        self.scorecardUseSoilNutrientMeter = ScorecardElement("Use Soil Nutrient Meter", "The soil nutrient meter has been used on at least 2 squares of soil from the pilot field", maxScore=2)
        self.scoreCard.append(self.scorecardUseSoilNutrientMeter)
        self.scorecardAtLeastTwoSeedsPlanted = ScorecardElement("At Least 2 Seeds Planted", "At least 2 seeds have been planted in the ground", maxScore=2)
        self.scoreCard.append(self.scorecardAtLeastTwoSeedsPlanted)
        self.scorecardAtLeastTwoNewPlants = ScorecardElement("At Least Two New Plants", "At least two new plants (mushrooms) have been grown to maturity", maxScore=2)
        self.scoreCard.append(self.scorecardAtLeastTwoNewPlants)

        # TODO: Add subtask that requires the agent to set the nutrients of at least one field


        # Add hypotheses from scoringInfo
        self.criticalHypotheses = scoringInfo["criticalHypotheses"]

        # Scoring Info passed from the scenario
        # scoringInfo["startingPlants"] = []
        # scoringInfo["startingSeeds"].append(seed)
        # scoringInfo["soilNutrientMeter"] = obj
        # scoringInfo["shovel"] = obj
        # scoringInfo["jar"] = obj            # Seed jar
        # scoringInfo["pilotFieldSoilTiles"]


    # Task setup: Add any necessary objects to the world to perform the task.
    def taskSetup(self):
        # Add the colonists?
        pass

    def initialize(self):
        pass

    # Update the task progress
    def updateTick(self):
        # Do not update the score if the task is already marked as completed
        if (self.completed == True):
            return

        # Clear the previous score and scorecard
        #self.scoreCard = []
        #score = 0

        # Check if they have the soil nutrient meter in an agent's inventory
        if (not self.scorecardSoilNutrientMeterPresent.completed):
            soilNutrientMeterContainer = self.scoringInfo["soilNutrientMeter"].parentContainer
            if (soilNutrientMeterContainer != None):
                if (soilNutrientMeterContainer.type == "agent"):
                    self.scorecardSoilNutrientMeterPresent.updateScore(score=1, completed=True, associatedUUIDs=[self.scoringInfo["soilNutrientMeter"].uuid], associatedNotes="The soil nutrient meter has been in the inventory of the agent with uuid " + str(soilNutrientMeterContainer.uuid))
        #self.scoreCard.append(self.scorecardSoilNutrientMeterPresent)

        # Check if the shovel is in an agent's inventory
        if (not self.scorecardShovelPresent.completed):
            shovelContainer = self.scoringInfo["shovel"].parentContainer
            if (shovelContainer != None):
                if (shovelContainer.type == "agent"):
                    self.scorecardShovelPresent.updateScore(score=1, completed=True, associatedUUIDs=[self.scoringInfo["shovel"].uuid], associatedNotes="The shovel has been in the inventory of the agent with uuid " + str(shovelContainer.uuid))
        #self.scoreCard.append(self.scorecardShovelPresent)

        # Check if the jar is in an agent's inventory
        if (not self.scorecardJarPresent.completed):
            jarContainer = self.scoringInfo["jar"].parentContainer
            if (jarContainer != None):
                if (jarContainer.type == "agent"):
                    self.scorecardJarPresent.updateScore(score=1, completed=True, associatedUUIDs=[self.scoringInfo["jar"].uuid], associatedNotes="The jar has been in the inventory of the agent with uuid " + str(jarContainer.uuid))
        #self.scoreCard.append(self.scorecardJarPresent)

        # Check if the soil nutrient meter has been used on at least 2 squares of soil from the pilot field
        if (not self.scorecardUseSoilNutrientMeter.completed):
            soilTilesChecked = set()
            for agent in self.world.getUserAgents():
                for soilTile in self.scoringInfo["pilotFieldSoilTiles"]:
                    foundActions = agent.actionHistory.queryActionObjects(ActionType.USE, arg1=self.scoringInfo["soilNutrientMeter"], arg2=soilTile, stopAtFirst=True)
                    if (len(foundActions) > 0):
                        soilTilesChecked.add(soilTile.uuid)

            numSoilTilesChecked = len(soilTilesChecked)
            isComplete = False
            if (numSoilTilesChecked >= 2):
                isComplete = True
            self.scorecardUseSoilNutrientMeter.updateScore(score=numSoilTilesChecked, completed=isComplete, associatedUUIDs=list(soilTilesChecked), associatedNotes="The following soil tiles have been checked with the soil nutrient meter: " + str(soilTilesChecked))

        # Check for at least one seed that is not a starting seed to be in the ground
        # First, get all objects
        allObjects = self.world.getAllWorldObjects()

        if (not self.scorecardAtLeastTwoSeedsPlanted.completed):
            for obj in allObjects:
                if (obj.type == "seed"):
                    # Make sure this seed isn't in the list of starting seeds
                    if (obj not in self.scoringInfo["startingSeeds"]):
                        # Check if the seed is in the ground
                        parentContainer = obj.parentContainer
                        if (parentContainer != None):
                            if (parentContainer.type == "soil"):
                                # Make sure there's no hole in the soil (i.e. the hole is filled in/the seed is planted)
                                if (parentContainer.attributes['hasHole'] == False):
                                    self.newSeedsPlanted.add(obj.uuid)
            numNewSeedsPlanted = len(self.newSeedsPlanted)
            isCompleted = False
            if (numNewSeedsPlanted >= 2):
                isCompleted = True
            self.scorecardAtLeastTwoSeedsPlanted.updateScore(score=numNewSeedsPlanted, completed=isCompleted, associatedUUIDs=list(self.newSeedsPlanted), associatedNotes="At least two new seeds have been planted in the ground")


        # Check for at least 2 new plants (Mushrooms) to exist
        if (not self.scorecardAtLeastTwoNewPlants.completed):
            # Check for new plants, that weren't in the simulation when it was initialized
            for obj in allObjects:
                if (isinstance(obj, Mushroom)):
                    if (obj not in self.scoringInfo["startingPlants"]):
                        self.newPlantsGrown.add(obj)

            # Count the number of new plants
            numMaturePlants = len(self.newPlantsGrown)
            completedTwoNewPlants = False
            if (numMaturePlants >= 2):
                numMaturePlants = 2
                completedTwoNewPlants = True

            self.scorecardAtLeastTwoNewPlants.updateScore(score=numMaturePlants, completed=completedTwoNewPlants, associatedUUIDs=[plant.uuid for plant in self.newPlantsGrown], associatedNotes="At least two new plants have been grown to maturity")

            # Ultimately, it's having successfully grown 2 new plants that determines whether the task is complete
            if (completedTwoNewPlants == True):
                self.completed = True
                self.completedSuccessfully = True

        #self.scoreCard.append(self.scorecardAtLeastTwoNewPlants)


        # Count the score, based on the scorecard
        score = 0
        maxScore = 0
        for scorecardElement in self.scoreCard:
            score += scorecardElement.score
            maxScore += scorecardElement.maxScore
        self.score = score
        self.maxScore = maxScore

        # TODO: Add a timeout that marks the task complete 100 steps after the last soil controller has been used?


#
#   Specific Task: Soil Nutrient Task
#
class ReactorTask(Task):
    # Constructor
    def __init__(self, world, scoringInfo):
        # TODO: modify description
        taskDescription = "You are at the Quantum Reactor Lab on Planet X. "
        taskDescription += "Quantum Crystals offer the potential to generate a great deal of power, but require their respective crystal reactors to be tuned to a specific frequency that appears unique for each crystal. "
        taskDescription += "Through great effort, a previous research scientist manually stumbled upon the correct frequencies for Crystal 1 and Crystal 2, which are in their respective reactors. "
        taskDescription += "Your task is to use science to figure out the correct frequency for Crystal 3 and Crystal 4, set their reactors to the appropriate frequency, and install the crystals. "
        taskDescription += "Once all four crystals are installed, the reactor will be able to generate a great deal of power. "
        taskDescription += "To support your task, a number of scientific instruments are available in the lab."

        Task.__init__(self, "ReactorTask", taskDescription, world, scoringInfo)
        self.score = 0
        self.maxScore = 6                       # Maximum score

        self.crystalsTaken = set()              # Crystals that have been taken
        self.instrumentsUsed = set()            # Instruments that have been used
        self.crystalsExamined = set()           # Crystals that have been examined
        self.reactorsChanged = set()            # Reactors that have had their values changed

        # Scorecard elements
        self.scorecardQuantumCrystalsPresent = ScorecardElement("Quantum Crystals Taken", "The quantum crystals have each been in an agent's inventory", maxScore=4)
        self.scoreCard.append(self.scorecardQuantumCrystalsPresent)

        # Each instrument has been used with at least one crystal
        self.scorecardInstrumentsUsed = ScorecardElement("Instruments Used", "Each scientific instrument has been used with at least one crystal", maxScore=4)
        self.scoreCard.append(self.scorecardInstrumentsUsed)

        # Each crystal has been examined by at least one instrument
        self.scorecardCrystalsExamined = ScorecardElement("Crystals Examined", "Each crystal has been examined by at least one instrument", maxScore=4)
        self.scoreCard.append(self.scorecardCrystalsExamined)

        # Unknown reactors (3 and 4) have had their values changed
        self.scorecardReactorsChanged = ScorecardElement("Reactors Changed", "The resonance frequency of the unknown reactors have been changed", maxScore=2)
        self.scoreCard.append(self.scorecardReactorsChanged)

        # Reactors on
        self.scorecardReactorsOn = ScorecardElement("Reactors On", "The reactors have been successfully activated", maxScore=4)
        self.scoreCard.append(self.scorecardReactorsOn)

        # Add hypotheses from scoringInfo
        self.criticalHypotheses = scoringInfo["criticalHypotheses"]

        # Scoring Info passed from the scenario
        # scoringInfo['instruments'] = instruments
        # scoringInfo['quantumCrystals'] = quantumCrystals
        # scoringInfo['reactors'] = crystalReactors
        # scoringInfo['reactorsToChange']


    # Task setup: Add any necessary objects to the world to perform the task.
    def taskSetup(self):
        # Add the colonists?
        pass

    def initialize(self):
        pass

    # Update the task progress
    def updateTick(self):
        # Do not update the score if the task is already marked as completed
        if (self.completed == True):
            return

        # Clear the previous score and scorecard
        #self.scoreCard = []
        #score = 0

        # Check if they have the soil nutrient meter in an agent's inventory
        if (not self.scorecardQuantumCrystalsPresent.completed):
            for crystal in self.scoringInfo["quantumCrystals"]:
                crystalContainer = crystal.parentContainer
                if (crystalContainer != None):
                    if (crystalContainer.type == "agent"):
                        self.crystalsTaken.add(crystal.uuid)

            numCrystalsTaken = len(self.crystalsTaken)
            isComplete = False
            if (numCrystalsTaken >= 4):
                isComplete = True
            self.scorecardQuantumCrystalsPresent.updateScore(score=numCrystalsTaken, completed=isComplete, associatedUUIDs=list(self.crystalsTaken), associatedNotes="The following quantum crystals have been taken: " + str(self.crystalsTaken))

        # Check if the instruments have been used with at least one crystal
        if (not self.scorecardInstrumentsUsed.completed) or (not self.scorecardCrystalsExamined.completed):
            for agent in self.world.getUserAgents():
                for instrument in self.scoringInfo["instruments"]:
                    for crystal in self.scoringInfo["quantumCrystals"]:
                        foundActions = agent.actionHistory.queryActionObjects(ActionType.USE, arg1=instrument, arg2=crystal, stopAtFirst=True)
                        if (len(foundActions) > 0):
                            self.instrumentsUsed.add(instrument.uuid)
                            self.crystalsExamined.add(crystal.uuid)

            numInstrumentsUsed = len(self.instrumentsUsed)
            isCompleteInstruments = False
            if (numInstrumentsUsed >= 4):
                isCompleteInstruments = True
            self.scorecardInstrumentsUsed.updateScore(score=numInstrumentsUsed, completed=isCompleteInstruments, associatedUUIDs=list(self.instrumentsUsed), associatedNotes="The following instruments have been used: " + str(self.instrumentsUsed))

            numCrystalsExamined = len(self.crystalsExamined)
            isCompleteCrystals = False
            if (numCrystalsExamined >= 4):
                isCompleteCrystals = True
            self.scorecardCrystalsExamined.updateScore(score=numCrystalsExamined, completed=isCompleteCrystals, associatedUUIDs=list(self.crystalsExamined), associatedNotes="The following crystals have been examined: " + str(self.crystalsExamined))


        # Check that the resonance frequency of the unknown (last 2) reactors has been changed from the default value
        if (not self.scorecardReactorsChanged.completed):
            for reactor in self.scoringInfo["reactorsToChange"]:
                if (reactor.attributes["resonanceFreq"] != reactor.attributes["resonanceFreqDefault"]):
                    self.reactorsChanged.add(reactor.uuid)

            numReactorsChanged = len(self.reactorsChanged)
            isComplete = False
            if (numReactorsChanged >= 2):
                isComplete = True
            self.scorecardReactorsChanged.updateScore(score=numReactorsChanged, completed=isComplete, associatedUUIDs=list(self.reactorsChanged), associatedNotes="The following reactors have had their resonance frequency changed: " + str(self.reactorsChanged))

        # Check if the reactors have been activated
        if (not self.scorecardReactorsOn.completed):
            numReactorsActivated = 0
            for reactor in self.scoringInfo["reactors"]:
                if (reactor.attributes["isActivated"] == True):
                    numReactorsActivated += 1

            allReactorsOn = False
            if (numReactorsActivated >= 4):
                allReactorsOn = True

            # Score
            self.scorecardReactorsOn.updateScore(score=numReactorsActivated, completed=allReactorsOn, associatedUUIDs=[reactor.uuid for reactor in self.scoringInfo["reactors"]], associatedNotes="The following reactors have been activated: " + str([reactor.uuid for reactor in self.scoringInfo["reactors"]]))

            # If this task is complete, then the task is complete
            if (allReactorsOn == True):
                self.completed = True
                self.completedSuccessfully = True
            else:
                self.completed = False
                self.completedSuccessfully = False


        # Count the score, based on the scorecard
        score = 0
        maxScore = 0
        for scorecardElement in self.scoreCard:
            score += scorecardElement.score
            maxScore += scorecardElement.maxScore
        self.score = score
        self.maxScore = maxScore

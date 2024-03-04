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
        if taskName == "EatMushroomTask":
            return EatMushroomTask(self.world, scoringInfo)
        elif taskName == "RustedKeyTask":
            return RustedKeyTask(self.world, scoringInfo)
        elif taskName == "ArcheologyDigTask":
            return ArcheologyDig(self.world, scoringInfo)
        elif taskName == "ArcheologyDigTaskGenericRadioisotope":
            return ArcheologyDigGenericRadioisotopes(self.world, scoringInfo)
        elif taskName == "SoilNutrientTask":
            return SoilNutrientTask(self.world, scoringInfo)
        else:
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
        outStr += "Task Progress (" + self.taskName + "):  Score: " + str(self.score) + ", Completed: " + str(self.completed) + ", Completed Successfully: " + str(self.completedSuccessfully)
        outStr += "\nScorecard:"
        for element in self.scoreCard:
            #outStr += "\n" + element.name + ": " + str(element.score) + "/" + str(element.maxScore) + ", Completed: " + str(element.completed)
            # As above, but with constant witdh formatting, completed should be 'completed' or 'not completed', and the task description should be there too
            isCompleted = "incomplete"
            if (element.completed == True):
                isCompleted = "completed"
            outStr += "\n - " + element.name.ljust(30) + " " + str(element.score).rjust(2) + " /" + str(element.maxScore).rjust(2) + "  " + str(isCompleted).ljust(15) + " " + element.description
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
        self.keyToMonitor = None


    # Task setup: Add any necessary objects to the world to perform the task.
    def taskSetup(self):
        # Add the colonists?
        pass

    # Update the task progress
    def updateTick(self):
        # Do not update the score if the task is already marked as completed
        if (self.completed == True):
            return

        # Monitoring task 1: Check to see whether there's a key that ISNT rusty
        score = 0
        if (self.keyToMonitor == None):
            # Look for a key in the world.  NOTE: This assumes there's only one key in this entire scenario. If there are multiple keys, need to add some specific way to identify the relevant door key to monitor.
            for obj in self.world.getAllWorldObjects():
                if obj.type == "key":
                    self.keyToMonitor = obj
                    break

        if (self.keyToMonitor != None):
            if (self.keyToMonitor.attributes['isRusted'] == False):
                score += 1

        # Monitoring task 2: Check to see if one or more agents are outside of the room
        # Bounds
        x0 = 16
        y0 = 10
        x1 = 16+6
        y1 = 10+3
        for agent in self.world.agents:
            # Check if the agent is outside the room
            # Get agent position
            isWithinBounds = agent.isWithinLocationBounds(x0, y0, x1, y1)
            if (isWithinBounds == False):
                score += 1
                break

        # Update score
        self.score = score

        # Monitoring task 3: Check if the task is complete
        if (self.score >= self.maxScore):
            self.completed = True
            self.completedSuccessfully = True
            print("Task completed successfully: " + self.taskName)
        elif (self.score < self.maxScore):
            self.completed = False
            self.completedSuccessfully = False




#
#   Specific Task: Archeology dig task
#
class ArcheologyDig(Task):
    # Constructor
    def __init__(self, world, scoringInfo):
        taskDescription = "You are on an archeological dig on Planet X.  3 ancient sites have been found. "
        taskDescription += "Your task is to excavate the sites, and date any artifacts with the radiocarbon meter.  Then, once completed, place the red flag beside the sign of the dig site with the oldest artifact. "

        Task.__init__(self, "ArcheologyDigTask", taskDescription, world, scoringInfo)
        self.score = 0
        self.maxScore = 1                       # Maximum score
        self.flagToMonitor = None
        self.goalSign = (0, 0)
        self.artifacts = []
        self.signs = []


    # Task setup: Add any necessary objects to the world to perform the task.
    def taskSetup(self):
        # Add the colonists?
        pass

    def initialize(self):
        # Find all the artifacts
        self.artifacts = []
        oldestArtifact = None
        oldestAge = 0
        for obj in self.world.getAllWorldObjects():
            if obj.type == "ancient artifact":
                self.artifacts.append(obj)
                if obj.attributes['radiocarbonAge'] > oldestAge:
                    oldestArtifact = obj
                    oldestAge = obj.attributes['radiocarbonAge']

        # Find all the signs
        self.signs = []
        closestSign = None
        closestDistance = 1000000
        for obj in self.world.getAllWorldObjects():
            if obj.type == "sign":
                self.signs.append(obj)
                # Get distance between this sign and the oldest artifact
                distance = obj.distanceTo(oldestArtifact)
                if (distance < closestDistance):
                    closestDistance = distance
                    closestSign = obj
        # Set the flag goal location to be the location of the closest sign
        self.goalSign = closestSign

        # Find the flag
        for obj in self.world.getAllWorldObjects():
            if obj.type == "flag":
                self.flagToMonitor = obj
                self.flagGoalLocation = obj.getWorldLocation()
                break

        # Set the maximum score
        self.maxScore = len(self.artifacts) + 2


    # Update the task progress
    def updateTick(self):
        # Do not update the score if the task is already marked as completed
        if (self.completed == True):
            return

        score = 0

        # If 'artificts' is empty, then initialize the scorer
        if len(self.artifacts) == 0:
            self.initialize()

        # Monitoring task 1: Check to see how many artifacts have been found
        for artifact in self.artifacts:
            # Get the parent container
            parentContainer = artifact.parentContainer
            # Check if the parent container is a soil tile
            if (parentContainer != None) and (parentContainer.type == "soil"):
                # Check that the soil tile "has a hold" (i.e. that the artifact has been exposed)
                if (parentContainer.attributes["hasHole"] == True):
                    score += 1

            else:
                # If the parent container is not a soil tile, then the container is something else, meaning the artifact was found and moved
                score += 1


        # Monitoring task 2: Check to see if the flag has been placed near ANY of the signs (+/- 2 grid spaces).
        # First, check that the flag has no parent container, meaning it's not being held by an agent
        flagPlaced = False
        if (self.flagToMonitor.parentContainer == None):
            for sign in self.signs:
                distance = sign.distanceTo(self.flagToMonitor)
                if (distance <= 2):
                    score += 1
                    flagPlaced = True
                    break

        # Monitoring task 3: Also check to see whether the flag has been placed near the CORRECT sign
        if (flagPlaced == True):
            distance = self.flagToMonitor.distanceTo(self.goalSign)
            flagAtGoal = False
            if (distance <= 2):
                score += 1
                flagAtGoal = True

        # Set the score
        self.score = score

        # If the flag has been placed, the task is complete
        if (flagPlaced == True):
            self.completed = True
            if (flagAtGoal == True):
                self.completedSuccessfully = True
            else:
                self.completedSuccessfully = False
        else:
            self.completed = False
            self.completedSuccessfully = False



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
        self.flagToMonitor = None
        self.goalSign = None
        self.artifacts = []
        self.signs = []


    # Task setup: Add any necessary objects to the world to perform the task.
    def taskSetup(self):
        # Add the colonists?
        pass

    def initialize(self):
        # Find all the artifacts
        self.artifacts = []
        oldestArtifact = None
        oldestAge = 0
        for obj in self.world.getAllWorldObjects():
            if obj.type == "ancient artifact":
                self.artifacts.append(obj)
                if obj.attributes['radiocarbonAge'] > oldestAge:
                    oldestArtifact = obj
                    oldestAge = obj.attributes['radiocarbonAge']

        # Find all the signs
        self.signs = []
        closestSign = None
        closestDistance = 1000000
        for obj in self.world.getAllWorldObjects():
            if obj.type == "sign":
                self.signs.append(obj)
                # Get distance between this sign and the oldest artifact
                distance = obj.distanceTo(oldestArtifact)
                if (distance < closestDistance):
                    closestDistance = distance
                    closestSign = obj
        # Set the flag goal location to be the location of the closest sign
        self.goalSign = closestSign

        # Find the flag
        for obj in self.world.getAllWorldObjects():
            if obj.type == "flag":
                self.flagToMonitor = obj
                self.flagGoalLocation = obj.getWorldLocation()
                break

        # Set the maximum score
        self.maxScore = len(self.artifacts) + 2


    # Update the task progress
    def updateTick(self):
        # Do not update the score if the task is already marked as completed
        if (self.completed == True):
            return

        score = 0

        # If 'artificts' is empty, then initialize the scorer
        if len(self.artifacts) == 0:
            self.initialize()

        #print("GOAL SIGN: " + str(self.goalSign.uuid))

        # Monitoring task 1: Check to see how many artifacts have been found
        for artifact in self.artifacts:
            # Get the parent container
            parentContainer = artifact.parentContainer
            # Check if the parent container is a soil tile
            if (parentContainer != None) and (parentContainer.type == "soil"):
                # Check that the soil tile "has a hold" (i.e. that the artifact has been exposed)
                if (parentContainer.attributes["hasHole"] == True):
                    score += 1

            else:
                # If the parent container is not a soil tile, then the container is something else, meaning the artifact was found and moved
                score += 1


        # Monitoring task 2: Check to see if the flag has been placed near ANY of the signs (+/- 2 grid spaces).
        # First, check that the flag has no parent container, meaning it's not being held by an agent
        flagPlaced = False
        if (self.flagToMonitor.parentContainer == None):
            for sign in self.signs:
                distance = sign.distanceTo(self.flagToMonitor)
                if (distance <= 2):
                    score += 1
                    flagPlaced = True
                    break

        # Monitoring task 3: Also check to see whether the flag has been placed near the CORRECT sign
        if (flagPlaced == True):
            distance = self.flagToMonitor.distanceTo(self.goalSign)
            flagAtGoal = False
            if (distance <= 2):
                score += 1
                flagAtGoal = True

        # Set the score
        self.score = score

        # If the flag has been placed, the task is complete
        if (flagPlaced == True):
            self.completed = True
            if (flagAtGoal == True):
                self.completedSuccessfully = True
            else:
                self.completedSuccessfully = False
        else:
            self.completed = False
            self.completedSuccessfully = False



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

        self.atLeastOneSeedPlanted = False      # Has at least one seed ever been planted
        self.newPlantsGrown = set()             # New plants grown since the start of the task

        # Scorecard elements
        self.scorecardSoilNutrientMeterPresent = ScorecardElement("Soil Nutrient Meter Present", "The soil nutrient meter has been in an agent's inventory", 1)
        self.scoreCard.append(self.scorecardSoilNutrientMeterPresent)
        self.scorecardShovelPresent = ScorecardElement("Shovel Present", "The shovel has been in an agent's inventory", 1)
        self.scoreCard.append(self.scorecardShovelPresent)
        self.scorecardJarPresent = ScorecardElement("Seed Jar Present", "The seed jar has been in an agent's inventory", 1)
        self.scoreCard.append(self.scorecardJarPresent)
        self.scorecardAtLeastOneSeedPlanted = ScorecardElement("At Least One Seed Planted", "At least one seed has been planted in the ground", 1)
        self.scoreCard.append(self.scorecardAtLeastOneSeedPlanted)
        self.scorecardAtLeastTwoNewPlants = ScorecardElement("At Least Two New Plants", "At least two new plants (mushrooms) have been grown to maturity", 2)
        self.scoreCard.append(self.scorecardAtLeastTwoNewPlants)

        # Add hypotheses from scoringInfo
        self.criticalHypotheses = scoringInfo["criticalHypotheses"]

    # Scoring Info passed from the scenario
    # scoringInfo["startingPlants"] = []
    # scoringInfo["startingSeeds"].append(seed)
    # scoringInfo["soilNutrientMeter"] = obj
    # scoringInfo["shovel"] = obj
    # scoringInfo["jar"] = obj            # Seed jar

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

        # Check for at least one seed that is not a starting seed to be in the ground
        # First, get all objects
        allObjects = self.world.getAllWorldObjects()

        if (not self.scorecardAtLeastOneSeedPlanted.completed):
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
                                    self.scorecardAtLeastOneSeedPlanted.updateScore(score=1, completed=True, associatedUUIDs=[obj.uuid], associatedNotes="At least one seed has been planted in the ground (in soil tile with uuid " + str(parentContainer.uuid) + ")")
        #self.scoreCard.append(self.scorecardAtLeastOneSeedPlanted)

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

        #self.scoreCard.append(self.scorecardAtLeastTwoNewPlants)


        # Count the score, based on the scorecard
        score = 0
        maxScore = 0
        for scorecardElement in self.scoreCard:
            score += scorecardElement.score
            maxScore += scorecardElement.maxScore
        self.score = score
        self.maxScore = maxScore

        # Check if the task is complete
        # In this task, the task is complete if all the scorecard elements are complete
        completed = True
        for scorecardElement in self.scoreCard:
            if (scorecardElement.completed == False):
                completed = False
                break
        self.completed = completed
        self.completedSuccessfully = completed

# TaskScorer.py
from ActionHistory import *

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
    def makeTask(self, taskName:str):
        if taskName == "EatMushroomTask":
            return EatMushroomTask(self.world)
        elif taskName == "RustedKeyTask":
            return RustedKeyTask(self.world)
        else:
            return None

#
#   Abstract class template for a specific task
#
class Task():
    # Constructor
    def __init__(self, taskName:str, taskDescription:str, world):
        self.taskName = taskName
        self.taskDescription = taskDescription
        self.world = world
        self.score = 0                          # Current task score
        self.maxScore = 1                       # Maximum score
        self.completed = False                  # Is this task over?
        self.completedSuccessfully = False      # Did the task complete successfully?


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
        return outStr




#
#   Specific Task: Agents eating space mushrooms without getting sick
#
class EatMushroomTask(Task):
    # Constructor
    def __init__(self, world):
        taskDescription = "The only food on this planet are local mushrooms, but after eating them, the colonist are sometimes getting sick.  Your task is to figure out why people are getting sick, and to prevent it.  You must demonstrate this by having 10 colonists successfully eat mushrooms without eventually getting sick."
        taskDescription += "Since the food causes only mild illness, and getting the colony established is important, the colonists have volunteered to be test subjects.  The Chef in the Cafeteria can help you collect mushrooms, serve mushrooms from the cafeteria pot to the tables, and let the colonists know a meal is ready to eat, when you're ready."
        Task.__init__(self, "EatMushroomTask", taskDescription, world)            
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
    def __init__(self, world):
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
        taskDescription += "6. When you have successfully rerusted the key and opened the door, please leave the shed. \n"

        Task.__init__(self, "RustedKeyTask", taskDescription, world)            
        self.score = 0
        self.maxScore = 2                       # Maximum score
        self.keyToMonitor = None


    # Task setup: Add any necessary objects to the world to perform the task.
    def taskSetup(self):
        # Add the colonists?
        pass

    # Update the task progress
    def updateTick(self):
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
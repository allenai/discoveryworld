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
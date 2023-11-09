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
    def __init__(self, taskName:str, world):
        self.taskName = taskName
        self.world = world
        self.score = 0                          # Current task score
        self.completed = False                # Is this task over?
        self.completedSuccessfully = False      # Did the task complete successfully?


    # Task setup: Add any necessary objects to the world to perform the task. 
    def taskSetup(self):
        pass

    def getScore(self):
        return self.score

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
        Task.__init__(self, "EatMushroomTask", world)            
        self.score = 0


    # Task setup: Add any necessary objects to the world to perform the task.
    def taskSetup(self):
        # Add the colonists?
        pass

    # Update the task progress
    def updateTick(self):
        # List of names of agents to monitor
        agentsToMonitor = []
        for i in range (0, 5):
            agentsToMonitor.append("Colonist " + str(i))

        for agent in self.world.agents:
            if agent.name in agentsToMonitor:
                # Check if they have eaten a mushroom

                # Check if they successfully ate something on the last tick
                lastAction = agent.actionHistory.getLastStepAction()                
                if (lastAction != None) and (lastAction['actionType'] == ActionType.EAT) and (lastAction['success'] == True):
                    # Check if it was a mushroom
                    if (lastAction['arg1'].name == "mushroom"):
                        self.score += 1


        if (self.score >= 10):
            self.completed = True
            self.completedSuccessfully = True
            print("Task completed successfully: " + self.taskName)
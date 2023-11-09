# TaskScorer.py


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

    # Task setup: Add any necessary objects to the world to perform the task. 
    def taskSetup(self):
        pass

    # Update the task progress
    def updateTick(self):
        pass



#
#   Specific Task: Agents eating space mushrooms without getting sick
#
class EatMushroomTask(Task):
    # Constructor
    def __init__(self, world):
        Task.__init__(self, "EatMushroomTask", world)
        
        self.mushroomEaten = False


    # Task setup: Add any necessary objects to the world to perform the task.
    def taskSetup(self):
        # Add the colonists?
        pass

    # Update the task progress
    def updateTick(self):
        pass
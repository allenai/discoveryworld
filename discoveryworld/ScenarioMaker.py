# ScenarioMaker.py
from discoveryworld.TaskScorer import *
from discoveryworld.scenarios import *

import random

#
#   Scenario Maker
#

class ScenarioMaker():
    # Constructor
    def __init__(self, world, rng=None):
        self.world = world
        self.rng = rng or random.Random()


    # Make a scenario
    def setupScenario(self, scenarioName:str, numUserAgents:int=1):
        if (scenarioName == "food_illness"):
            makeScenarioTown(self.world, numUserAgents, rng=self.rng)
            self.world.addTaskByName("EatMushroomTask")
            return (True, "")

        elif (scenarioName == "combinatorial_chemistry"):
            makeScenarioStorageShed(self.world, numUserAgents, rng=self.rng)
            self.world.addTaskByName("RustedKeyTask")
            return (True, "")

        elif (scenarioName == "archaeology_dating"):
            makeScenarioArchaeologicalDig(self.world, numUserAgents, rng=self.rng)
            self.world.addTaskByName("ArcheologyDigTask")
            return (True, "")

        elif (scenarioName == "plant_nutrients"):
            makeScenarioPlantGrowing(self.world, numUserAgents, rng=self.rng)
            self.world.addTaskByName("SoilNutrientTask")
            return (True, "")

        # If we reach here, the scenario was not recognized
        print("ERROR: setupScenario: scenarioName not recognized: " + scenarioName)
        return (False, "ERROR: setupScenario: scenarioName not recognized: " + scenarioName)

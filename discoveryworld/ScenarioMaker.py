# ScenarioMaker.py
from discoveryworld.TaskScorer import *
from discoveryworld.scenarios import *

import random

SCENARIOS = ["food_illness", "combinatorial_chemistry", "archaeology_dating", "plant_nutrients", "lost_in_translation"]

class ScenarioMaker():
    # Constructor
    def __init__(self, world, rng=None):
        self.world = world
        self.rng = rng or random.Random()


    # Make a scenario
    def setupScenario(self, scenarioName:str, numUserAgents:int=1):
        if (scenarioName == "food_illness"):
            scoringInfo = makeScenarioTown(self.world, numUserAgents, rng=self.rng)
            self.world.addTaskByName("EatMushroomTask", scoringInfo)
            return (True, "")

        elif (scenarioName == "combinatorial_chemistry"):
            scoringInfo = makeScenarioStorageShed(self.world, numUserAgents, rng=self.rng)
            self.world.addTaskByName("RustedKeyTask", scoringInfo)
            return (True, "")

        elif (scenarioName == "archaeology_dating"):
            scoringInfo = makeScenarioArchaeologicalDig(self.world, numUserAgents, rng=self.rng)
            self.world.addTaskByName("ArcheologyDigTask", scoringInfo)
            return (True, "")

        elif (scenarioName == "plant_nutrients"):
            scoringInfo = makeScenarioPlantGrowing(self.world, numUserAgents, rng=self.rng)
            self.world.addTaskByName("SoilNutrientTask", scoringInfo)
            return (True, "")

        elif (scenarioName == "lost_in_translation"):
            makeScenarioRosettaStone(self.world, numUserAgents, rng=self.rng)
            #self.world.addTaskByName("RosettaStoneTask")
            return (True, "")

        # If we reach here, the scenario was not recognized
        print("ERROR: setupScenario: scenarioName not recognized: " + scenarioName)
        return (False, "ERROR: setupScenario: scenarioName not recognized: " + scenarioName)
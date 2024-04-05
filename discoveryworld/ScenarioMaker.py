# ScenarioMaker.py
from discoveryworld.TaskScorer import *
from discoveryworld.scenarios import *

import random

SCENARIOS = [
    "food_illness",
    "combinatorial_chemistry",
    "archaeology_dating_simple",
    "archaeology_dating_challenge",
    "plant_nutrients",
    "lost_in_translation_easy",
    "lost_in_translation_medium",
    "lost_in_translation_hard",
    "reactor_lab"]

class ScenarioMaker():
    # Constructor
    def __init__(self, world, seed:int=None):
        self.world = world
        self.world.randomSeed = seed
        self.world.rng = random.Random(seed)

    # Make a scenario
    def setupScenario(self, scenarioName:str, numUserAgents:int=1):
        if (scenarioName == "food_illness"):
            scoringInfo = makeScenarioTown(self.world, numUserAgents)
            self.world.addTaskByName("EatMushroomTask", scoringInfo)
            return (True, "")

        elif (scenarioName == "combinatorial_chemistry"):
            scoringInfo = makeScenarioStorageShed(self.world, numUserAgents)
            self.world.addTaskByName("RustedKeyTask", scoringInfo)
            return (True, "")

        elif (scenarioName == "archaeology_dating_simple"):
            scoringInfo = makeScenarioArchaeologicalDig(self.world, numUserAgents)
            self.world.addTaskByName("ArcheologyDigTaskEasy", scoringInfo)
            return (True, "")

        elif (scenarioName == "archaeology_dating_challenge"):
            scoringInfo = makeScenarioArchaeologicalDigGenericRadioisotope(self.world, numUserAgents)
            self.world.addTaskByName("ArcheologyDigTaskGenericRadioisotope", scoringInfo)
            return (True, "")

        elif (scenarioName == "plant_nutrients"):
            scoringInfo = makeScenarioPlantGrowing(self.world, numUserAgents)
            self.world.addTaskByName("SoilNutrientTask", scoringInfo)
            return (True, "")

        elif (scenarioName.startswith("lost_in_translation")):
            difficulty = scenarioName.rsplit("_")[-1]
            scoringInfo = makeScenarioRosettaStone(self.world, numUserAgents, difficulty)
            self.world.addTaskByName("RosettaStoneTask", scoringInfo)
            return (True, "")

        elif (scenarioName == "reactor_lab"):
            scoringInfo = makeScenarioReactorLab(self.world, numUserAgents)
            self.world.addTaskByName("ReactorTask", scoringInfo)
            return (True, "")

        # If we reach here, the scenario was not recognized
        print("ERROR: setupScenario: scenarioName not recognized: " + scenarioName)
        return (False, "ERROR: setupScenario: scenarioName not recognized: " + scenarioName)

# ScenarioMaker.py
from discoveryworld.TaskScorer import *
from discoveryworld.scenarios import *

import random

# Internal names
SCENARIOS = [
    "tutorial",
    "food_illness",
    "combinatorial_chemistry",
    "combinatorial_chemistry_challenge",
    "archaeology_dating_simple",
    "archaeology_dating_challenge",
    "plant_nutrients",
    "lost_in_translation_easy",
    "lost_in_translation_medium",
    "lost_in_translation_hard",
    "reactor_lab"]

# Canonical (outside) names
SCENARIO_NAMES = [
    "Tutorial", "Combinatorial Chemistry", "Archaeology Dating", "Plant Nutrients", "Reactor Lab", "Lost in Translation", "Space Sick",
#    "TODO 1", "TODO 2"
]

SCENARIO_INFOS = {
    "Tutorial": {
        "difficulty": ["Normal"],
        "variations": ["1"],
    },
    "Combinatorial Chemistry": {
        "difficulty": ["Normal", "Challenge"],
        "variations": ["1", "2", "3", "4", "5"],
    },
    "Archaeology Dating": {
        "difficulty": ["Normal", "Challenge"],
        "variations": ["1", "2", "3", "4", "5"],
    },
    "Plant Nutrients": {
        "difficulty": ["Normal"],
        "variations": ["1", "2", "3", "4", "5"],
    },
    "Reactor Lab": {
        "difficulty": ["Normal"],
        "variations": ["1", "2", "3", "4", "5"],
    },
    "Lost in Translation": {
        "difficulty": ["Normal", "Challenge"],
        "variations": ["1", "2", "3", "4", "5"],
    },
    "Space Sick": {
        "difficulty": ["Normal"],
        "variations": ["1", "2", "3", "4", "5"],
    },
    # "TODO 1": {
    #     "difficulty": ["Easy", "Challenge"],
    #     "variations": ["1", "2", "3", "4", "5"],
    # },
    # "TODO 2": {
    #     "difficulty": ["Easy", "Challenge"],
    #     "variations": ["1", "2", "3", "4", "5"],
    # },
}

SCENARIO_DIFFICULTY_OPTIONS = ["Normal", "Challenge"]


# Mapping canonical scenario names to internal scenario names
def getInternalScenarioName(scenarioNameIn:str, difficulty:str):
    # Map between the choice and the scenario name
    scenarioName = None
    # Scenario 0: Tutorial
    if scenarioNameIn == "Tutorial":
        scenarioName = "tutorial"
    # Scenario 1: Combinatorial Chemistry
    elif (scenarioNameIn == "Combinatorial Chemistry") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[0]):
        scenarioName = "combinatorial_chemistry"
    elif (scenarioNameIn == "Combinatorial Chemistry") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[1]):
        scenarioName = "combinatorial_chemistry_challenge"
    # Scenario 2: Archaeology Dating
    elif (scenarioNameIn == "Archaeology Dating") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[0]):
        scenarioName = "archaeology_dating_simple"
    elif (scenarioNameIn == "Archaeology Dating") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[1]):
        scenarioName = "archaeology_dating_challenge"
    # Scenario 3: Plant Nutrients
    elif (scenarioNameIn == "Plant Nutrients") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[0]):
        scenarioName = "plant_nutrients"
    elif (scenarioNameIn == "Plant Nutrients") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[1]):
        scenarioName = None
    # Scenario 4: Reactor Lab
    elif (scenarioNameIn == "Reactor Lab") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[0]):
        scenarioName = "reactor_lab"
    elif (scenarioNameIn == "Reactor Lab") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[1]):
        scenarioName = None
    # Scenario 5: Lost in Translation
    elif (scenarioNameIn == "Lost in Translation") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[0]):
        scenarioName = "lost_in_translation_easy"
    elif (scenarioNameIn == "Lost in Translation") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[1]):
        scenarioName = "lost_in_translation_hard"
    # Scenario 6: Space Sick
    elif (scenarioNameIn == "Space Sick") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[0]):
        scenarioName = "food_illness"
    elif (scenarioNameIn == "Space Sick") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[1]):
        scenarioName = None
    # Scenario 7: TODO 1
    elif (scenarioNameIn == "TODO 1") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[0]):
        scenarioName = None
    elif (scenarioNameIn == "TODO 1") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[1]):
        scenarioName = None
    # Scenario 8: TODO 2
    elif (scenarioNameIn == "TODO 2") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[0]):
        scenarioName = None
    elif (scenarioNameIn == "TODO 2") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[1]):
        scenarioName = None

    # Return the internal scenario name to use
    return scenarioName

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
            self.world.initialFilter()
            return (True, "")

        elif (scenarioName == "combinatorial_chemistry"):
            scoringInfo = makeScenarioStorageShed(self.world, numUserAgents)
            self.world.addTaskByName("RustedKeyTask", scoringInfo)
            self.world.initialFilter()
            return (True, "")

        elif (scenarioName == "combinatorial_chemistry_challenge"):
            scoringInfo = makeScenarioStorageShedChallenge(self.world, numUserAgents)
            self.world.addTaskByName("RustedKeyTaskChallenge", scoringInfo)
            self.world.initialFilter()
            return (True, "")

        elif (scenarioName == "archaeology_dating_simple"):
            scoringInfo = makeScenarioArchaeologicalDig(self.world, numUserAgents)
            self.world.addTaskByName("ArcheologyDigTaskEasy", scoringInfo)
            self.world.initialFilter()
            return (True, "")

        elif (scenarioName == "archaeology_dating_challenge"):
            scoringInfo = makeScenarioArchaeologicalDigGenericRadioisotope(self.world, numUserAgents)
            self.world.addTaskByName("ArcheologyDigTaskGenericRadioisotope", scoringInfo)
            self.world.initialFilter()
            return (True, "")

        elif (scenarioName == "plant_nutrients"):
            scoringInfo = makeScenarioPlantGrowing(self.world, numUserAgents)
            self.world.addTaskByName("SoilNutrientTask", scoringInfo)
            self.world.initialFilter()
            return (True, "")

        elif (scenarioName.startswith("lost_in_translation")):
            difficulty = scenarioName.rsplit("_")[-1]
            scoringInfo = makeScenarioRosettaStone(self.world, numUserAgents, difficulty)
            self.world.addTaskByName("RosettaStoneTask", scoringInfo)
            self.world.initialFilter()
            return (True, "")

        elif (scenarioName == "reactor_lab"):
            scoringInfo = makeScenarioReactorLab(self.world, numUserAgents)
            self.world.addTaskByName("ReactorTask", scoringInfo)
            self.world.initialFilter()
            return (True, "")

        elif (scenarioName.startswith("tutorial")):
            scoringInfo = makeScenarioTutorial(self.world, numUserAgents)
            self.world.addTaskByName("TutorialTask", scoringInfo)
            self.world.initialFilter()
            return (True, "")

        # If we reach here, the scenario was not recognized
        print("ERROR: setupScenario: scenarioName not recognized: " + scenarioName)
        return (False, "ERROR: setupScenario: scenarioName not recognized: " + scenarioName)

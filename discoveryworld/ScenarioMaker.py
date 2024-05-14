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
    "reactor_lab"
    "smallskills_dialog_test",
    "smallskills_pickandplace_test",
    "smallskills_pickandgive_test",
    "smallskills_measurement_test",
    "smallskills_doors_test",
    "smallskills_doors_keys_test",
    "smallskills_navigation_house_test",
    "smallskills_search_test",
    "smallskills_discoveryfeed_test",
    "smallskills_moving_agents_test",
    ]

# Canonical (outside) names
SCENARIO_NAMES = [
    "Tutorial", "Combinatorial Chemistry", "Archaeology Dating", "Plant Nutrients", "Reactor Lab", "Lost in Translation", "Space Sick",
    "Small Skills: Dialog Test",
    "Small Skills: Pick and Place Test",
    "Small Skills: Pick and Give Test",
    "Small Skills: Instrument Measurement Test",
    "Small Skills: Doors Test",
    "Small Skills: Doors with Keys Test",
    "Small Skills: Navigation in a House Test",
    "Small Skills: Search Test",
    "Small Skills: Discovery Feed Test",
    "Small Skills: Moving Agents Test",
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
    "Small Skills: Dialog Test": {
        "difficulty": ["Normal"],
        "variations": ["1"],
    },
    "Small Skills: Pick and Place Test": {
        "difficulty": ["Normal"],
        "variations": ["1"],
    },
    "Small Skills: Pick and Give Test": {
        "difficulty": ["Normal"],
        "variations": ["1"],
    },
    "Small Skills: Instrument Measurement Test": {
        "difficulty": ["Normal"],
        "variations": ["1"],
    },
    "Small Skills: Doors Test": {
        "difficulty": ["Normal"],
        "variations": ["1"],
    },
    "Small Skills: Doors with Keys Test": {
        "difficulty": ["Normal"],
        "variations": ["1"],
    },
    "Small Skills: Navigation in a House Test": {
        "difficulty": ["Normal"],
        "variations": ["1"],
    },
    "Small Skills: Search Test": {
        "difficulty": ["Normal"],
        "variations": ["1"],
    },
    "Small Skills: Discovery Feed Test": {
        "difficulty": ["Normal"],
        "variations": ["1"],
    },
    "Small Skills: Moving Agents Test": {
        "difficulty": ["Normal"],
        "variations": ["1"],
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
    if (scenarioNameIn == "Tutorial") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[0]):
        scenarioName = "tutorial"
    elif (scenarioNameIn == "Tutorial") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[1]):
        scenarioName = None
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

    elif (scenarioNameIn == "Small Skills: Dialog Test") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[0]):
        scenarioName = "smallskills_dialog_test"

    elif (scenarioNameIn == "Small Skills: Pick and Place Test") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[0]):
        scenarioName = "smallskills_pickandplace_test"

    elif (scenarioNameIn == "Small Skills: Pick and Give Test") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[0]):
        scenarioName = "smallskills_pickandgive_test"

    elif (scenarioNameIn == "Small Skills: Instrument Measurement Test") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[0]):
        scenarioName = "smallskills_measurement_test"

    elif (scenarioNameIn == "Small Skills: Doors Test") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[0]):
        scenarioName = "smallskills_doors_test"

    elif (scenarioNameIn == "Small Skills: Doors with Keys Test") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[0]):
        scenarioName = "smallskills_doors_keys_test"

    elif (scenarioNameIn == "Small Skills: Navigation in a House Test") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[0]):
        scenarioName = "smallskills_navigation_house_test"

    elif (scenarioNameIn == "Small Skills: Search Test") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[0]):
        scenarioName = "smallskills_search_test"

    elif (scenarioNameIn == "Small Skills: Discovery Feed Test") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[0]):
        scenarioName = "smallskills_discoveryfeed_test"

    elif (scenarioNameIn == "Small Skills: Moving Agents Test") and (difficulty == SCENARIO_DIFFICULTY_OPTIONS[0]):
        scenarioName = "smallskills_moving_agents_test"

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

        elif (scenarioName == "smallskills_dialog_test"):
            scoringInfo = makeScenarioDialogTest(self.world, numUserAgents)
            self.world.addTaskByName("SmallSkillsDialogTask", scoringInfo)
            self.world.initialFilter()
            return (True, "")

        elif (scenarioName == "smallskills_pickandplace_test"):
            scoringInfo = makeScenarioPickAndPlaceTest(self.world, numUserAgents)
            self.world.addTaskByName("SmallSkillsPickAndPlaceTask", scoringInfo)
            self.world.initialFilter()
            return (True, "")

        elif (scenarioName == "smallskills_pickandgive_test"):
            scoringInfo = makeScenarioPickAndGiveTest(self.world, numUserAgents)
            self.world.addTaskByName("SmallSkillsPickAndGiveTask", scoringInfo)
            self.world.initialFilter()
            return (True, "")

        elif (scenarioName == "smallskills_measurement_test"):
            scoringInfo = makeScenarioInstrumentMeasurementTest(self.world, numUserAgents)
            self.world.addTaskByName("SmallSkillsInstrumentMeasurementTask", scoringInfo)
            self.world.initialFilter()
            return (True, "")

        elif (scenarioName == "smallskills_doors_test"):
            scoringInfo = makeScenarioDoorsTest(self.world, numUserAgents)
            self.world.addTaskByName("SmallSkillsDoorsTask", scoringInfo)
            self.world.initialFilter()
            return (True, "")

        elif (scenarioName == "smallskills_doors_keys_test"):
            scoringInfo = makeScenarioDoorsKeysTest(self.world, numUserAgents)
            self.world.addTaskByName("SmallSkillsDoorsKeysTask", scoringInfo)
            self.world.initialFilter()
            return (True, "")

        elif (scenarioName == "smallskills_navigation_house_test"):
            scoringInfo = makeScenarioNavigationHouseTest(self.world, numUserAgents)
            self.world.addTaskByName("SmallSkillsNavigationHouseTask", scoringInfo)
            self.world.initialFilter()
            return (True, "")

        elif (scenarioName == "smallskills_search_test"):
            scoringInfo = makeScenarioSearchTest(self.world, numUserAgents)
            self.world.addTaskByName("SmallSkillsSearchTask", scoringInfo)
            self.world.initialFilter()
            return (True, "")
        
        elif (scenarioName == "smallskills_discoveryfeed_test"):
            scoringInfo = makeScenarioDiscoveryFeedTest(self.world, numUserAgents)
            self.world.addTaskByName("SmallSkillsDiscoveryFeedTask", scoringInfo)
            self.world.initialFilter()
            return (True, "")
        
        elif (scenarioName == "smallskills_moving_agents_test"):
            scoringInfo = makeScenarioMovingAgentsTest(self.world, numUserAgents)
            self.world.addTaskByName("SmallSkillsMovingAgentsTask", scoringInfo)
            self.world.initialFilter()
            return (True, "")

        # If we reach here, the scenario was not recognized
        print("ERROR: setupScenario: scenarioName not recognized: " + scenarioName)
        return (False, "ERROR: setupScenario: scenarioName not recognized: " + scenarioName)

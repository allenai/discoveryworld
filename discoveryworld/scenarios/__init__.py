from discoveryworld.scenarios.archaeology import makeScenarioArchaeologicalDig
from discoveryworld.scenarios.archaeology import makeScenarioArchaeologicalDigGenericRadioisotope
from discoveryworld.scenarios.plant_growing import makeScenarioPlantGrowing
from discoveryworld.scenarios.rosetta_stone import makeScenarioRosettaStone
from discoveryworld.scenarios.storage_shed import makeScenarioStorageShed, makeScenarioStorageShedChallenge
from discoveryworld.scenarios.reactor_lab import makeScenarioReactorLab
from discoveryworld.scenarios.town import makeScenarioTown
from discoveryworld.scenarios.reactor_lab import makeScenarioReactorLab
from discoveryworld.scenarios.tutorial import makeScenarioTutorial
from discoveryworld.scenarios.smallskills_dialog import *
from discoveryworld.scenarios.smallskills_pickandplace import *
from discoveryworld.scenarios.smallskills_pickandgive import *
from discoveryworld.scenarios.smallskills_measurement import *
from discoveryworld.scenarios.smallskills_doors import *
from discoveryworld.scenarios.smallskills_doors_keys import *
from discoveryworld.scenarios.smallskills_navigation_house import *
from discoveryworld.scenarios.smallskills_search import *
from discoveryworld.scenarios.smallskills_discoveryfeed import *
from discoveryworld.scenarios.smallskills_moving_agents import *


SCENARIOS = {
    "Town": makeScenarioTown,
    "StorageShed": makeScenarioStorageShed,
    "PlantGrowing": makeScenarioPlantGrowing,
    "ArchaeologicalDig": makeScenarioArchaeologicalDig,
    "ArchaeologicalDigGenericRadioisotope": makeScenarioArchaeologicalDigGenericRadioisotope,
    "RosettaStone": makeScenarioRosettaStone,
    "ReactorLab": makeScenarioReactorLab,
    "Tutorial": makeScenarioTutorial,
}

from discoveryworld.scenarios.archaeology import makeScenarioArchaeologicalDig
from discoveryworld.scenarios.archaeology import makeScenarioArchaeologicalDigGenericRadioisotope
from discoveryworld.scenarios.plant_growing import makeScenarioPlantGrowing
from discoveryworld.scenarios.rosetta_stone import makeScenarioRosettaStone
from discoveryworld.scenarios.storage_shed import makeScenarioStorageShed, makeScenarioStorageShedChallenge
from discoveryworld.scenarios.reactor_lab import makeScenarioReactorLab
from discoveryworld.scenarios.town import makeScenarioTown
from discoveryworld.scenarios.reactor_lab import makeScenarioReactorLab
from discoveryworld.scenarios.tutorial import makeScenarioTutorial

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

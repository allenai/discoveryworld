from discoveryworld.scenarios.archaeology import makeScenarioArchaeologicalDig
from discoveryworld.scenarios.archaeology import makeScenarioArchaeologicalDigGenericRadioisotope
from discoveryworld.scenarios.plant_growing import makeScenarioPlantGrowing
from discoveryworld.scenarios.rosetta_stone import makeScenarioRosettaStone
from discoveryworld.scenarios.storage_shed import makeScenarioStorageShed
from discoveryworld.scenarios.town import makeScenarioTown

SCENARIOS = {
    "Town": makeScenarioTown,
    "StorageShed": makeScenarioStorageShed,
    "PlantGrowing": makeScenarioPlantGrowing,
    "ArchaeologicalDig": makeScenarioArchaeologicalDig,
    "ArchaeologicalDigGenericRadioisotope": makeScenarioArchaeologicalDigGenericRadioisotope,
    "RosettaStone": makeScenarioRosettaStone,
}

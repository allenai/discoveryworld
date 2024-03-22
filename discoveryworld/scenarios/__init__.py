from discoveryworld.scenarios.archaeology import makeScenarioArchaeologicalDig
from discoveryworld.scenarios.archaeology import makeScenarioArchaeologicalDigGenericRadioisotope
from discoveryworld.scenarios.plant_growing import makeScenarioPlantGrowing
from discoveryworld.scenarios.rosetta_stone import makeScenarioRosettaStone
from discoveryworld.scenarios.storage_shed import makeScenarioStorageShed
from discoveryworld.scenarios.reactor_lab import makeScenarioReactorLab
from discoveryworld.scenarios.town import makeScenarioTown
# from discoveryworld.scenarios.reactor_lab import makeScenarioReactorLab  # FIXME: cange back when ReactorLab.py is added.

SCENARIOS = {
    "Town": makeScenarioTown,
    "StorageShed": makeScenarioStorageShed,
    "PlantGrowing": makeScenarioPlantGrowing,
    "ArchaeologicalDig": makeScenarioArchaeologicalDig,
    "ArchaeologicalDigGenericRadioisotope": makeScenarioArchaeologicalDigGenericRadioisotope,
    "RosettaStone": makeScenarioRosettaStone,
    "ReactorLab": makeScenarioReactorLab,  # FIXME: cange back when ReactorLab.py is added.
}

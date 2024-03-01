import random
from discoveryworld.Layer import Layer
from discoveryworld.buildings.house import mkBuildingDivided, mkBuildingOneRoom, mkTableAndChairs


def mkBarracks(x, y, world):
    # Create a building (barracks)
    #mkBuildingOneRoom(world, x=x, y=y, width=5, height=5)
    #mkBuildingOneRoom(world, x=x, y=y, width=12, height=5)
    mkBuildingDivided(world, x=x, y=y, width=8, height=7, dividerX=0, apertureX=0, dividerY=3, apertureY=1, doorX=3, signText="Barracks")

    # Add 3 beds and bedside tables (back wall)
    world.addObject(x+2, y+1, Layer.FURNITURE, world.createObject("Bed"))
    world.addObject(x+3, y+1, Layer.FURNITURE, world.createObject("TableBedside"))
    world.addObject(x+5, y+1, Layer.FURNITURE, world.createObject("Bed"))
    world.addObject(x+6, y+1, Layer.FURNITURE, world.createObject("TableBedside"))
    #world.addObject(x+8, y+1, Layer.FURNITURE, Bed(world))
    #world.addObject(x+9, y+1, Layer.FURNITURE, TableBedside(world))

    # Add 3 beds and bedside tables (middle wall)
    world.addObject(x+2, y+4, Layer.FURNITURE, world.createObject("Bed"))
    world.addObject(x+3, y+4, Layer.FURNITURE, world.createObject("TableBedside"))
    world.addObject(x+5, y+4, Layer.FURNITURE, world.createObject("Bed"))
    world.addObject(x+6, y+4, Layer.FURNITURE, world.createObject("TableBedside"))
    #world.addObject(x+8, y+4, Layer.FURNITURE, Bed(world))
    #world.addObject(x+9, y+4, Layer.FURNITURE, TableBedside(world))


    # Add a bed
    #world.addObject(x+1, y+1, Layer.FURNITURE, Bed(world))

    # Add a bedside table
    #world.addObject(x+2, y+1, Layer.FURNITURE, TableBedside(world))


def mkInfirmary(x, y, world):
    # Create a building (barracks)
    mkBuildingOneRoom(world, x=x, y=y, width=8, height=5)

    # Add 4 beds
    world.addObject(x+1, y+1, Layer.FURNITURE, world.createObject("Bed"))
    world.addObject(x+3, y+1, Layer.FURNITURE, world.createObject("Bed"))
    #world.addObject(x+5, y+1, Layer.FURNITURE, Bed(world))
    #world.addObject(x+7, y+1, Layer.FURNITURE, Bed(world))

    # Table
    world.addObject(x+5, y+1, Layer.FURNITURE, world.createObject("Table"))
    # Fridge
    world.addObject(x+6, y+1, Layer.FURNITURE, world.createObject("Fridge"))


def mkCafeteria(x, y, world, rng=None):
    rng = rng or random.Random()
    # Create an L-shaped building (cafeteria)
    #mkBuildingLDivided(world, x=x, y=y, width=10, height=8, dividerX=5)
    # Create a divided building (cafeteria)
    #mkBuildingDivided(world, x=x, y=y, width=8, height=7, dividerX=0, apertureX=0, dividerY=3, apertureY=1, doorX=3, signText="Cafeteria")
    mkBuildingOneRoom(world, x=x, y=y, width=8, height=7, signText="Cafeteria")

    # Front (eating area)
    # Table and chairs
    #mkTableAndChairs(world, x=x+7, y=y+5, chairsPresent=["n", "s", "e", "w"])
    mkTableAndChairs(world, x=x+2, y=y+5, chairsPresent=["", "", "e", "w"])

    # Counter
    tables = []
    for i in range(5):
        tableToAdd = world.createObject("Table")
        #if (i == 2):
        #    tableToAdd.addObject(Mushroom(world, "red"))
        #tableToAdd.addObject(world.createObject("mushroom3"))
        #tableToAdd.addObject(world.createObject("mushroom1"))
        # Randomly choose between mushroom1 and mushroom2
        if (rng.random() < 0.5):
            tableToAdd.addObject(world.createObject("mushroom1"))
        else:
            tableToAdd.addObject(world.createObject("mushroom2"))

        world.addObject(x+i+2, y+3, Layer.FURNITURE, tableToAdd)
        tables.append(tableToAdd)

    #world.addObject(x+2, y+5, Layer.FURNITURE, Table(world))

    # Back (kitchen)
    pot = world.createObject("Pot")
    # add 5 mushrooms to pot
    #for i in range(5):
    #    pot.addObject(Mushroom(world))
    # Put the pot on a table
    kitchenPrepTable = world.createObject("Table")
    kitchenPrepTable.addObject(pot)
    world.addObject(x+3, y+1, Layer.FURNITURE, kitchenPrepTable)
    world.addObject(x+4, y+1, Layer.FURNITURE, world.createObject("Fridge"))
    world.addObject(x+5, y+1, Layer.FURNITURE, world.createObject("Sink"))
    world.addObject(x+6, y+1, Layer.FURNITURE, world.createObject("Stove"))

    # Front (decorations)
    flowerpot = world.createObject("FlowerPot")
    flowerTable = world.createObject("Table")
    flowerTable.addObject(flowerpot)
    world.addObject(x+6, y+5, Layer.FURNITURE, flowerTable)

    ## debug
    return tables, pot


def mkScienceLab(x, y, world):
    # Create a building (science lab)
    #buildingMaker.mkBuildingOneRoom(world, x=x, y=y, width=5, height=5)
    mkBuildingDivided(world, x=x, y=y, width=8, height=6, dividerX=5, apertureX=3, dividerY=0, apertureY=0, doorX=3, signText="Science Lab")

    bench1 = world.createObject("Table")
    world.addObject(x+1, y+1, Layer.FURNITURE, bench1)
    bench1.addObject( world.createObject("Microscope") )

    bench2 = world.createObject("Table")
    world.addObject(x+2, y+1, Layer.FURNITURE, bench2)
    bench2.addObject( world.createObject("Spectrometer") )

    bench3 = world.createObject("Table")
    world.addObject(x+3, y+1, Layer.FURNITURE, bench3)
    bench3.addObject( world.createObject("PHMeter") )

    bench4 = world.createObject("Table")
    world.addObject(x+4, y+1, Layer.FURNITURE, bench4)
    bench4.addObject( world.createObject("RadiationMeter") )


    # Add sampler and sample containers (Petri dishes)
    bench5 = world.createObject("Table")
    world.addObject(x+1, y+4, Layer.FURNITURE, bench5)
    bench5.addObject( world.createObject("Sampler") )

    bench6 = world.createObject("Table")
    world.addObject(x+1, y+3, Layer.FURNITURE, bench6)
    bench6.addObject( world.createObject("PetriDish") )


    bench7 = world.createObject("Table")
    world.addObject(x+4, y+4, Layer.FURNITURE, bench7)
    bench7.addObject( world.createObject("Thermometer") )


    # Add a red mushroom and a pink mushroom
    world.addObject(x+3, y+3, Layer.OBJECTS, world.createObject("mushroom1"))
    world.addObject(x+4, y+3, Layer.OBJECTS, world.createObject("mushroom2"))

    # Add a radioactive check source
    world.addObject(x+6, y+1, Layer.OBJECTS, world.createObject("radioactivechecksource"))

    # Add NPK meter
    world.addObject(x+6, y+4, Layer.OBJECTS, world.createObject("NPKMeter"))


def mkStorageShed(x, y, world, DOOR_KEY_ID):
    # Create a small building
    houseSizeX = 7
    houseSizeY = 4
    mkBuildingOneRoom(world, x=x+1, y=y, width=houseSizeX, height=houseSizeY, signText="Storage Shed", includeDoor=True, doorKeyID = DOOR_KEY_ID)

    # Add a table in the farm house
    compoundTable1 = world.createObject("Table")
    compoundTable2 = world.createObject("Table")
    compoundTable3 = world.createObject("Table")
    compoundTable4 = world.createObject("Table")
    compoundTable5 = world.createObject("Table")

    # Create chemical dispensers
    dispenser1 = world.createObject("ChemicalDispenser")
    dispenser2 = world.createObject("ChemicalDispenser")
    dispenser3 = world.createObject("ChemicalDispenser")
    dispenser1.name = "Dispenser (Substance A)"
    dispenser2.name = "Dispenser (Substance B)"
    dispenser3.name = "Dispenser (Substance C)"

    # Fill with chemicals
    #dispenser1.setAutoFill(checkObjectName="seed", fillObjectName="Seed", minCount=5)
    dispenser1.setAutoFill(checkObjectName="Substance A", fillObjectName="SubstanceA", minCount=1, replenishTime=0)
    dispenser2.setAutoFill(checkObjectName="Substance B", fillObjectName="SubstanceB", minCount=1, replenishTime=0)
    dispenser3.setAutoFill(checkObjectName="Substance C", fillObjectName="SubstanceC", minCount=1, replenishTime=0)

    # Add dispensers to tables
    compoundTable2.addObject(dispenser1)
    compoundTable3.addObject(dispenser2)
    compoundTable4.addObject(dispenser3)

    # Add bottle cleaner
    BottleCleaner = world.createObject("BottleCleaner")
    compoundTable5.addObject(BottleCleaner)

    # Add tables to world
    world.addObject(x+2, y+1, Layer.FURNITURE, compoundTable1)
    world.addObject(x+3, y+1, Layer.FURNITURE, compoundTable2)
    world.addObject(x+4, y+1, Layer.FURNITURE, compoundTable3)
    world.addObject(x+5, y+1, Layer.FURNITURE, compoundTable4)
    world.addObject(x+6, y+1, Layer.FURNITURE, compoundTable5)

    mixingJar = world.createObject("Jar")
    # Add to first table
    compoundTable1.addObject(mixingJar)

    # Add substance
    #substance1 = world.createObject("TestSubstance")
    #substance2 = world.createObject("PurpleSubstance")
    #mixingJar.addObject(substance1)
    #mixingJar.addObject(substance2)

    #substanceCleaner = world.createObject("substanceCleaner")
    #mixingJar.addObject(substanceCleaner)

    # Add rusty key
    rustyKey = world.createObject("Key")
    rustyKey.setKeyID(DOOR_KEY_ID)
    world.addObject(x+2, y+2, Layer.OBJECTS, rustyKey)
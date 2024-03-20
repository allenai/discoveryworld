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


def mkStorageShed(x, y, world, DOOR_KEY_ID, chemicalSolutionDict, scoringInfo):
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
    scoringInfo['dispensers'] = [dispenser1, dispenser2, dispenser3]

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
    scoringInfo['bottleCleaner'] = BottleCleaner

    # Add tables to world
    world.addObject(x+2, y+1, Layer.FURNITURE, compoundTable1)
    world.addObject(x+3, y+1, Layer.FURNITURE, compoundTable2)
    world.addObject(x+4, y+1, Layer.FURNITURE, compoundTable3)
    world.addObject(x+5, y+1, Layer.FURNITURE, compoundTable4)
    world.addObject(x+6, y+1, Layer.FURNITURE, compoundTable5)

    mixingJar = world.createObject("Jar")
    # Add to first table
    compoundTable1.addObject(mixingJar)
    scoringInfo['mixingJar'] = mixingJar

    # Add substance
    #substance1 = world.createObject("TestSubstance")
    #substance2 = world.createObject("PurpleSubstance")
    #mixingJar.addObject(substance1)
    #mixingJar.addObject(substance2)

    #substanceCleaner = world.createObject("substanceCleaner")
    #mixingJar.addObject(substanceCleaner)

    # Add rusty key
    #rustyKey = world.createObject("Key")
    rustyKey = world.createObject("KeyRustyParametric")
    rustyKey.setRustRemovalDict(chemicalSolutionDict)
    rustyKey.setKeyID(DOOR_KEY_ID)
    world.addObject(x+2, y+2, Layer.OBJECTS, rustyKey)
    scoringInfo['key'] = rustyKey


def mkKeyShop(x, y, world):
    # Create a building (shop sellings colored keys)
    signText = "Magasin de clés\n[The logo is a key]"
    mkBuildingOneRoom(world, x=x, y=y, width=7, height=6, signText=signText)

    COLORS = {"r": "red", "g": "green", "b": "blue", "y": "yellow", "k": "black", "w": "white", "o": "orange"}
    layout = [
        "xxxxxxx",
        "xrbywkx",
        "xxxxxxx",
        "xgxxxox",
        "xxxxxxx",
        "xxxxxxx",
    ]
    for i, row in enumerate(layout):
        for j, c in enumerate(row):
            if c in COLORS.keys():
                key = world.createObject("Key", color=COLORS[c], isRusted=False)  # TODO: change sign text to alien language.
                table = world.createObject("TableWithSign", signText=key.name)
                world.addObject(x+j, y+i, Layer.FURNITURE, table)
                table.addObject(key)


def mkPaintShop(x, y, world):
    signText = "Magasin de peinture\n[The logo is a paint bucket]"
    mkBuildingOneRoom(world, x=x, y=y, width=7, height=6, signText=signText)

    COLORS = {"r": "red", "g": "green", "b": "blue", "y": "yellow", "k": "black", "w": "white", "o": "orange"}
    layout = [
        "xxxxxxx",
        "xrbywkx",
        "xxxxxxx",
        "xgxxxox",
        "xxxxxxx",
        "xxxxxxx",
    ]
    for i, row in enumerate(layout):
        for j, c in enumerate(row):
            if c in COLORS.keys():
                paint = world.createObject("PaintBucket", color=COLORS[c])  # TODO: change sign text to alien language.
                table = world.createObject("TableWithSign", signText=paint.name)
                world.addObject(x+j, y+i, Layer.FURNITURE, table)
                table.addObject(paint)


def mkGeneralStore(x, y, world):
    # Create a building (shop sellings colored keys)
    signText = "Magasin général\n[The logo is a shopping cart]"
    mkBuildingOneRoom(world, x=x, y=y, width=9, height=14, signText=signText)

    COLORS = {"r": "red", "g": "green", "b": "blue", "y": "yellow", "k": "black", "w": "white", "o": "orange"}
    OBJECTS = {
        "0": "",
        "1": "Mushroom",
        "2": "Pot",
        "3": "Jar",
        "4": "Shovel",
        "5": "Seed",
        "6": "FlowerPot",
        "7": "Key",
        "8": "Flag",
        # "9": "PaintBucket",
        # "A": "Rock",
    }
    layout = [
        ".........",
        ".0400000.",
        ".........",
        ".100.000.",
        ".........",
        ".002.000.",
        ".........",
        ".003.081.",
        ".........",
        ".040.070.",
        ".........",
        ".500.600.",
        ".........",
    ]
    for i, row in enumerate(layout):
        for j, o in enumerate(row):
            if o in OBJECTS.keys():
                if OBJECTS[o]:
                    obj = world.createObject(OBJECTS[o])  # TODO: change sign text to alien language.
                    table = world.createObject("TableWithSign", signText=obj.name)
                    table.addObject(obj)
                else:
                    table = world.createObject("Table")

                world.addObject(x+j, y+i, Layer.FURNITURE, table)


def mkSchool(x, y, world):
    # Create a building (shop sellings colored keys)
    signText = "École\n[The logo is a student hat]"
    mkBuildingOneRoom(world, x=x, y=y, width=9, height=11, signText=signText)
    PROGRAMS = {
        0: "Remise à zéro",
        1: "Ajoute un",
        2: "Ajoute deux",
        3: "Ajoute trois",
        4: "Ajoute quatre",
        5: "Ajoute cinq",
    }

    OBJECTS = {
        "c": ("Chair", {}),
        "T": ("Table", {}),
        "p": ("Pupitre", {"facing": "south"}),
        "t": ("Pupitre", {"facing": "north"}),
        "<": ("Pupitre", {"facing": "west"}),
        ">": ("Pupitre", {"facing": "east"}),
        "P": ("FlagPole", {"height": 6}),
        "B": ("Bookcase", {}),
    }
    layout = [
        ".........",
        "..B...B..",
        "...TpS.P.",
        ".........",
        ".3.t.t.0.",
        ".........",
        ".t.t.1.5.",
        ".........",
        ".t.2.t.4.",
        ".........",
        ".........",
    ]

    computer = world.createObject("CountingComputer")
    for i, row in enumerate(layout):
        for j, o in enumerate(row):
            if o == "P":
                cls, kwargs = OBJECTS[o]
                flagpole = world.createObject(cls, **kwargs)
                world.addObject(x+j, y+i, Layer.FURNITURE, flagpole)
                computer.flagpole = flagpole
            elif o == "S":
                desk = world.createObject("Table")
                world.addObject(x+j, y+i, Layer.FURNITURE, desk)
                desk.addObject(computer)
            elif str.isdigit(o):
                digit = int(o)
                desk = world.createObject("Pupitre", facing="north")
                world.addObject(x+j, y+i, Layer.FURNITURE, desk)
                disk = world.createObject("FloppyDisk", program=PROGRAMS[digit], value=digit)
                desk.addObject(disk)
            elif o in OBJECTS.keys():
                cls, kwargs = OBJECTS[o]
                obj = world.createObject(cls, **kwargs)
                world.addObject(x+j, y+i, Layer.FURNITURE, obj)

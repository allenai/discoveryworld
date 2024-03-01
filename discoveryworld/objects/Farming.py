import copy
from discoveryworld.ActionSuccess import ActionSuccess, MessageImportance, UseWithSuccess

from discoveryworld.Layer import Layer
from discoveryworld.ScienceHelpers import getNPKContent, livingTemperatureRangeCheck
from discoveryworld.objects.Object import Object


class Dirt(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "dirt", "dirt", defaultSpriteName = "placeholder_dirt_pile")

        self.attributes["isMovable"] = True                       # Can it be moved?
        self.attributes["isPassable"] = True                      # Agen't can't walk over this

    #
    #   Material Property Initialization
    #
    def initializeMaterialProperties(self, materialIndexDict):
        # Randomly choose the material type ("soil_good", "soil_medium", "soil_poor")
        soilTypes = ["soil_good", "soil_medium", "soil_poor"]
        # Randomly choose one
        randIdx = self.rng.randint(0, len(soilTypes) - 1)
        randMaterialName = soilTypes[randIdx]
        # Set the material type
        if (randMaterialName in materialIndexDict):
            material = materialIndexDict[randMaterialName]
            self.attributes["materials"].append( copy.deepcopy(material) )
        else:
            print("Error: Material '" + randMaterialName + "' not found in materialIndexDict")
            print("Material Index Dict: " + str(materialIndexDict))
            exit(1)

        pass


    def tick(self):
        # Call superclass
        Object.tick(self)


class FertilizerBag(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "fertilizer bag", "fertilizer bag", defaultSpriteName = "instruments_fertilizer_bag")

        self.attributes["isMovable"] = True                       # Can it be moved?
        self.attributes["isPassable"] = True                      # Agen't can't walk over this

        # Container
        self.attributes['isContainer'] = True                      # Is it a container?
        self.attributes['isOpenable'] = False                      # Can not be opened (things are stored in the open pot)
        self.attributes['isOpenContainer'] = True                  # If it's a container, then is it open?
        self.attributes['containerPrefix'] = "in"                  # Container prefix (e.g. "in" or "on")
        self.attributes['contentsVisible2D'] = False               # If it is a container, do we render the contents in the 2D representation, or is that already handled (e.g. for pots/jars, that render generic contents if they contain any objects)

    def tick(self):
        # Call superclass
        Object.tick(self)

        # If the bag contains less than 3 fertilizer pellets, then add enough to make 3
        numFertilizerPellets = 0
        for obj in self.contents:
            if (obj.type == "fertilizer"):
                numFertilizerPellets += 1

        if (numFertilizerPellets < 3):
            # Add enough fertilizer pellets to make 3
            for i in range(3 - numFertilizerPellets):
                fertilizerPellet = self.world.createObject("FertilizerPellet")
                self.addObject(fertilizerPellet, force=True)
                fertilizerPellet.tick()


    # Sprite
    # Updates the current sprite name based on the current state of the object
    # def inferSpriteName(self, force:bool=False):
    #     if (not self.needsSpriteNameUpdate and not force):
    #         # No need to update the sprite name
    #         return

    #     # This will be the next last sprite name (when we flip the backbuffer)
    #     self.tempLastSpriteName = self.curSpriteName


class FertilizerPellet(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "fertilizer", "fertilizer", defaultSpriteName = "instruments_fertilizer_pellet")

        self.attributes["isMovable"] = True                       # Can it be moved?
        self.attributes["isPassable"] = True                      # Agen't can't walk over this

        self.attributes["absorbTime"] = 8                         # How many ticks until it absorbs into the soil?

    def tick(self):
        # Call superclass
        Object.tick(self)

        # Check if the conditions for the seed to grow have been met
        # Condition 1: Check if the fertilizer pellet is contained within soil
        nearDirt = None

        # Check if parent container is soil with dirt in it
        if (self.parentContainer is not None):
            if (self.parentContainer.type == "soil"):
                # Get any contained dirt
                parentContinerObjs = self.parentContainer.contents
                for obj in parentContinerObjs:
                    if (obj.type == "dirt"):
                        nearDirt = obj
                        break

        # OR, check if the fertilizer pellet is in no container, but is on the same tile as dirt.
        if (self.parentContainer is None) and (nearDirt is None):
            # Get the tile that this object is on
            objectsAtTile = self.world.getObjectsAt(self.attributes["gridX"], self.attributes["gridY"])
            for object in objectsAtTile:
                if (object.type == "dirt"):
                    nearDirt = object
                    break

        # If the conditions have been met, continue the absorption process
        if (nearDirt is not None):
            self.attributes["absorbTime"] -= 1

            # If the absorb time is 0, then absorb into the soil
            if (self.attributes["absorbTime"] == 0):
                #print("Absorb into soil")

                # Increase the N/P/K of the dirt material by one
                found = False
                for material in nearDirt.attributes["materials"]:
                    if (material["MaterialName"] == "soil"):
                        material["nitrogen"] += 1
                        material["phosphorus"] += 1
                        material["potassium"] += 1
                        break

                # Remove the fertilizer pellet from the world
                self.world.removeObject(self)
                return


class Mold(Object):
    # Constructor
    def __init__(self, world, color:str=""):
        # Default sprite name
        Object.__init__(self, world, "mold", "mold", defaultSpriteName = "forest1_mushroom_pink")

        self.attributes['isLiving'] = True                         # Is it alive?
        # Most properties populated from the external spreadsheet

    def tick(self):
        # Call superclass
        Object.tick(self)

        # Check to make sure this living thing is not subjected to extreme temperatures that may kill it
        livingTemperatureRangeCheck(self)

        # If it's dead, then it's no longer poisonous
        if (self.attributes['isLiving'] == False):
            self.attributes['isPoisonous'] = False
            # Make a note of this in the microscope modifier text.
            ## TODO: This should be refactored -- perhaps only do it in response to a 'generateMicroscopeDesc' string? (i.e. only when the player looks at it)
            self.attributes['microscopeModifierText'].append("This mold appears dead.")


class Mushroom(Object):
    # Constructor
    def __init__(self, world, color:str=""):
        # Default sprite name
        Object.__init__(self, world, "mushroom", "mushroom", defaultSpriteName = "forest1_mushroom_pink")

        #self.attributes["color"] = "pink"                           # Color of the mushroom (valid: "yellow", "pink", "red", "green")
        # Randomly choose a color
        if (color == ""):
            self.attributes["color"] = self.rng.choice(["yellow", "pink", "red", "green"])
        else:
            self.attributes["color"] = color

        # Food attributes
        self.attributes['isEdible'] = True                         # Can it be eaten?

        # Poison/health attributes
        self.attributes['isPoisonous'] = False                     # Is it poisonous?
        # Make red mushrooms poisonous
        #if (self.attributes["color"] == "red"):
        #    self.attributes['isPoisonous'] = True


    def tick(self):
        # Call superclass
        Object.tick(self)

    # Sprite
    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return

        # Infer sprite based on color
        if (self.attributes["color"] == "yellow"):
            self.curSpriteName = "forest1_mushroom_yellow"
        elif (self.attributes["color"] == "pink"):
            self.curSpriteName = "forest1_mushroom_pink"
        elif (self.attributes["color"] == "red"):
            self.curSpriteName = "forest1_mushroom_red"
        elif (self.attributes["color"] == "green"):
            self.curSpriteName = "forest1_mushroom_green"
        else:
            # Throw warning, default to pink
            print("WARNING: Mushroom color not recognized (" + str(self.attributes["color"]) + "). Defaulting to pink.")
            self.curSpriteName = "forest1_mushroom_pink"

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName

    #
    #   Text Observations
    #
    def getTextDescription(self):
        # Get a text description of this object
        return self.attributes["color"] + " " + self.name


class PlantGeneric(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "plant (generic)", "plant (generic)", defaultSpriteName = "forest1_plant1")

    def tick(self):
        # Call superclass
        Object.tick(self)


class PlantTreeBig(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "tree (big)", "tree (big)", defaultSpriteName = "forest1_tree_big")

        self.attributes["isMovable"] = False                       # Can it be moved?
        self.attributes["isPassable"] = False                      # Agen't can't walk over this

    def tick(self):
        # Call superclass
        Object.tick(self)


class Seed(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "seed", "seed", defaultSpriteName = "placeholder_seed")

        self.attributes["isMovable"] = True                       # Can it be moved?
        self.attributes["isPassable"] = True                      # Agen't can't walk over this

        self.attributes["sproutTime"] = -1                        # How many ticks until the seed sprouts?

    def tick(self):
        # Call superclass
        Object.tick(self)

        # Check if the conditions for the seed to grow have been met
        # Condition 1: Check that the seed is contained in a 'SoilTile' object
        inSoilTile = False
        hasHole = False
        if (self.parentContainer is not None):
            #print("*** Parent Container Attributes: " + str(self.parentContainer.attributes))
            if (self.parentContainer.type == "soil"):
                inSoilTile = True

        # Condition 2: Also check that the hole is filled
        if (self.parentContainer is not None):
            if (self.parentContainer.attributes['hasHole'] == True):
                hasHole = True

        # Debug information
        #print("*** Seed: inSoilTile = " + str(inSoilTile) + ", hasHole = " + str(hasHole) + ", sproutTime: " + str(self.attributes["sproutTime"]))

        # If the conditions have been met, continue the growth process
        if (inSoilTile and not hasHole):
            # Perform action based on sprout time
            if (self.attributes["sproutTime"] == 0):
                #print("Turn into plant")
                # Turn into plant
                plant = None
                # Randomly choose one of 4 plants to turn into
                rand = self.rng.randint(0, 3)
                if (rand == 0):
                    plant = self.world.createObject("mushroom1")
                elif (rand == 1):
                    plant = self.world.createObject("mushroom2")
                elif (rand == 2):
                    plant = self.world.createObject("mushroom3")
                elif (rand == 3):
                    plant = self.world.createObject("mushroom4")

                # Replace self with the plant
                #self.replaceSelfWithObject(plant)
                # Return, since this object is no longer valid
                # Add the plant to the same world location as the soil tile
                #self.world.addObjectToLocation(plant, self.parentContainer.parentContainer)
                #def addObject(self, x, y, layer, object:Object):
                seedLocation = self.getWorldLocation()
                self.world.addObject(seedLocation[0], seedLocation[1], Layer.OBJECTS, plant)

                # Remove self
                self.world.removeObject(self)

                return

            elif (self.attributes["sproutTime"] == -1):
                #print("Random sprout time")
                # Sprout time was not set -- so this is the first time the conditions have been met. Set sprout time to a random value between 10 and 20 ticks
                self.attributes["sproutTime"] = self.rng.randint(10, 20)
            else:
                #print("Decrement sprout time")
                # If the sprout time has already been set, then decrement it
                # How fast the plant grows is determined by the quality of its soil. The better the soil, the faster it grows.
                # Soil quality is determined by NPK content. The higher the NPK content, the better the soil.  Use the ScienceHelper.getNPKContent() to calculate this.
                npk = getNPKContent(self.parentContainer)
                sumNPK = npk["nitrogen"] + npk["phosphorus"] + npk["potassium"]
                # NPK is nominally between 0-10, but most of the soil in DiscoveryWorld has starting values between 1-4 for each.  Call the nominal max growth rate at 5.  5*3 = 15, so divide by 15 to get a growth rate.
                growthRate = sumNPK / 30.0
                # Randomly generate a number, and see if that number is less than the growth rate. If it is, then the plant grows.
                randGrowth = self.rng.random()
                if (randGrowth < growthRate):
                    self.attributes["sproutTime"] -= 1
                else:
                    # Plant did not grow this cycle
                    pass


class SeedRequiringNutrients(Object):
    # Constructor
    def __init__(self, world, needsNutrientLevels:dict={}):
        # Default sprite name
        Object.__init__(self, world, "seed", "seed", defaultSpriteName = "placeholder_seed")

        self.attributes["isMovable"] = True                       # Can it be moved?
        self.attributes["isPassable"] = True                      # Agen't can't walk over this

        self.attributes["sproutTime"] = -1                        # How many ticks until the seed sprouts?

        # Nutrient requirements
        #self.attributes["needsNutrientLevels"] = {"potassium": 1, "thorium": 2}                    # Soil nutrients.  If empty, then it's not applicable/inconclusive.
        self.attributes["needsNutrientLevels"] = needsNutrientLevels              # For seeds/plants: What nutrient levels do they need to grow?

    def tick(self):
        # Call superclass
        Object.tick(self)

        # self.attributes["soilNutrients"] = {}                    # Soil nutrients.  If empty, then it's not applicable/inconclusive.
        # self.attributes["needsNutrientLevels"] = {}              # For seeds/plants: What nutrient levels do they need to grow?
        # self.attributes["antirequirementsNutrientLevels"] = []   # A list of dictionaries, each containing a list of nutrient levels under which the seed/plant will NOT grow

        # Check if the conditions for the seed to grow have been met
        # Condition 1: Check that the seed is contained in a 'SoilTile' object
        inSoilTile = False
        hasHole = False
        if (self.parentContainer is not None):
            #print("*** Parent Container Attributes: " + str(self.parentContainer.attributes))
            if (self.parentContainer.type == "soil"):
                inSoilTile = True

        # Condition 2: Also check that the hole is filled
        if (self.parentContainer is not None):
            if (self.parentContainer.attributes['hasHole'] == True):
                hasHole = True

        # Debug information
        #print("*** Seed: inSoilTile = " + str(inSoilTile) + ", hasHole = " + str(hasHole) + ", sproutTime: " + str(self.attributes["sproutTime"]))

        # Check that the soil has the right nutrients
        hasRequiredNutrients = True
        if (inSoilTile):
            soilNutrients = self.parentContainer.attributes["soilNutrients"]
            # Check that the soil has the right level for each nutrient that this seed requires
            for nutrient in self.attributes["needsNutrientLevels"].keys():
                if (nutrient not in soilNutrients):
                    hasRequiredNutrients = False
                    break
                if (soilNutrients[nutrient] != self.attributes["needsNutrientLevels"][nutrient]):
                    hasRequiredNutrients = False
                    break
            print("Checking soil tile (" + str(self.parentContainer.uuid) + ") for meeting the nutrient needs of seed (" + str(self.uuid) + "): " + str(hasRequiredNutrients))

        # Check for anti-requirements
        for antiReq in self.attributes["antirequirementsNutrientLevels"]:
            if (len(antiReq) > 0):
                hasAllAntiReqs = True
                for nutrient in antiReq.keys():
                    if (nutrient in soilNutrients):
                        if (soilNutrients[nutrient] != antiReq[nutrient]):
                            hasRequiredNutrients = False
                            break
                if (hasAllAntiReqs):
                    print("Soil tile (" + str(self.parentContainer.uuid) + ") has antirequisites for seed (" + str(self.uuid) + "): " + str(antiReq))
                    hasRequiredNutrients = False
                    break


        # If the conditions have been met, continue the growth process
        if (inSoilTile) and (not hasHole) and (hasRequiredNutrients):
            # Perform action based on sprout time
            if (self.attributes["sproutTime"] == 0):
                #print("Turn into plant")
                # Turn into plant
                plant = None
                # Randomly choose one of 4 plants to turn into
                rand = self.rng.randint(0, 3)
                if (rand == 0):
                    plant = self.world.createObject("mushroom1")
                elif (rand == 1):
                    plant = self.world.createObject("mushroom2")
                elif (rand == 2):
                    plant = self.world.createObject("mushroom3")
                elif (rand == 3):
                    plant = self.world.createObject("mushroom4")

                # Replace self with the plant
                #self.replaceSelfWithObject(plant)
                # Return, since this object is no longer valid
                # Add the plant to the same world location as the soil tile
                #self.world.addObjectToLocation(plant, self.parentContainer.parentContainer)
                #def addObject(self, x, y, layer, object:Object):
                seedLocation = self.getWorldLocation()
                self.world.addObject(seedLocation[0], seedLocation[1], Layer.OBJECTS, plant)

                # Remove self
                self.world.removeObject(self)

                return

            elif (self.attributes["sproutTime"] == -1):
                # Sprout time was not set -- so this is the first time the conditions have been met. Set sprout time to a random value between 10 and 20 ticks
                self.attributes["sproutTime"] = self.rng.randint(3, 6)
            else:
                # Decrement sprout time
                self.attributes["sproutTime"] -= 1

                #print("Decrement sprout time")
                # If the sprout time has already been set, then decrement it
                # How fast the plant grows is determined by the quality of its soil. The better the soil, the faster it grows.
                # Soil quality is determined by NPK content. The higher the NPK content, the better the soil.  Use the ScienceHelper.getNPKContent() to calculate this.
                #npk = getNPKContent(self.parentContainer)
                #sumNPK = npk["nitrogen"] + npk["phosphorus"] + npk["potassium"]
                # NPK is nominally between 0-10, but most of the soil in DiscoveryWorld has starting values between 1-4 for each.  Call the nominal max growth rate at 5.  5*3 = 15, so divide by 15 to get a growth rate.
                #growthRate = sumNPK / 30.0
                # Randomly generate a number, and see if that number is less than the growth rate. If it is, then the plant grows.
                #randGrowth = self.rng.random()
                #if (randGrowth < growthRate):
                #    self.attributes["sproutTime"] -= 1
                #else:
                #    # Plant did not grow this cycle
                #    pass


class SoilNutrientMeter(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "soil nutrient meter", "soil nutrient meter", defaultSpriteName = "instruments_generic_meter")

        # Default attributes
        self.attributes['isUsable'] = True                       # Can this device be used with another object? (e.g. specifically through the 'use' action)

        pass


    #
    #   Actions (use with)
    #
    def actionUseWith(self, patientObj):
        # Use this object on the patient object
        useDescriptionStr = "You use the soil nutrient meter to investigate the " + patientObj.name + ".\n"

        # Check for the "soilNutrients" attribute in the patient object
        if ("soilNutrients" not in patientObj.attributes):
            useDescriptionStr += "The results are inconclusive.\n"
            return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)

        print("## Soil Nutrient Meter: " + str(patientObj.attributes["soilNutrients"]))
        # Check that the dictionary contains more than one key
        if (len(patientObj.attributes["soilNutrients"]) == 0):
            useDescriptionStr += "The results are inconclusive.\n"
            return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)

        # If there are values, then report the values
        useDescriptionStr += "The results are as follows:\n"
        for key in patientObj.attributes["soilNutrients"].keys():
            value = patientObj.attributes["soilNutrients"][key]
            valueDescription = "unknown"
            if (value == 0):
                valueDescription = "zero"
            elif (value == 1):
                valueDescription = "low"
            elif (value == 2):
                valueDescription = "medium"
            elif (value == 3):
                valueDescription = "high"

            useDescriptionStr += "- " + key + ": " + valueDescription + "\n"

        return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)

    #
    #   Tick
    #
    def tick(self):
        # Call superclass
        Object.tick(self)

    # Sprite
    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return

        self.curSpriteName = self.defaultSpriteName

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName


class SoilTile(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "soil", "soil", defaultSpriteName = "forest1_soil_c")

        self.attributes["isMovable"] = False                       # Can it be moved?
        self.attributes['isShovelable'] = True                     # Can it be shoveled?

        # By default, it contains Dirt, which can be removed by shovelling
        dirt = self.world.createObject("Dirt")
        self.addObject(dirt, force=True)


    #def __init__(self, success, message, generatedItem = None, importance = MessageImportance.NORMAL):
    def useWithShovelResult(self):
        # First, check to see if the object already has a hole -- if so, it can't be shovelled.
        if (self.attributes["hasHole"]):
            return UseWithSuccess(False, "There is already a hole here.")

        # Otherwise, we can dig a hole
        #self.attributes["hasHole"] = True

        # Generate 'dirt' object.
        #generatedObjects = [self.world.createObject("Dirt")]
        # Find 'dirt' object contained in this object
        generatedObjects = []
        dirtList = self.getContainedObjectByType("dirt", maxMatches=1, recursive=False, respectContainerStatus=False)
        if (len(dirtList) == 0):
            # No dirt found -- this shouldn't happen
            return UseWithSuccess(False, "Error: No dirt found in soil tile. This should never happen.")
        else:
            # Dirt found -- remove it from the soil tile, and add it to the list of generated objects
            dirt = dirtList[0]
            self.removeObject(dirt)
            generatedObjects.append(dirt)


        # Return success
        return UseWithSuccess(True, "You dig a hole in the soil, creating a hole and dirt.", generatedObjects)


    def tick(self):
        # Call superclass
        Object.tick(self)

        # Check to see if this object contains dirt (in which case, the 'hasHole' attribute should be False)
        hasDirt = False
        for obj in self.contents:
            if (obj.type == "dirt"):
                hasDirt = True
                break
        if (hasDirt):
            self.attributes["hasHole"] = False
        else:
            self.attributes["hasHole"] = True


        # Check to see if the object has a hole (and if so, change the name, and add the sprite modifier)
        if (self.attributes["hasHole"]):
            # Add the sprite modifier
            self.curSpriteModifiers.add("placeholder_hole")
            # Change the name of the object to "hole"
            if (self.name != "hole"):
                self.name = "hole"
                # If so, then we need to update the sprite name
                self.needsSpriteNameUpdate = True

            # Allow the object to be a container, and be open
            self.attributes["isContainer"] = True
            self.attributes["isOpenContainer"] = True
        else:
            # No sprite modifier needed (they are cleared each tick automatically)
            # Change the name of the object to "soil"
            if (self.name != "soil"):
                self.name = "soil"
                self.needsSpriteNameUpdate = True

            # Object is not a container, and not open
            self.attributes["isContainer"] = False
            self.attributes["isOpenContainer"] = False


    # Check if a tile already contains a "path"
    def _hasObj(self, x, y, type):
        objects = self.world.getObjectsAt(x, y)
        # Then, check to see if any of them are walls
        for object in objects:
            if (object.type == type):
                return True
        return False

    # Sprite
    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return

        # Check to see if the neighbouring tiles have paths
        hasPathNorth = self._hasObj(self.attributes["gridX"], self.attributes["gridY"] - 1, "soil")
        hasPathSouth = self._hasObj(self.attributes["gridX"], self.attributes["gridY"] + 1, "soil")
        hasPathWest = self._hasObj(self.attributes["gridX"] - 1, self.attributes["gridY"], "soil")
        hasPathEast = self._hasObj(self.attributes["gridX"] + 1, self.attributes["gridY"], "soil")

        # 4 positives
        if (hasPathNorth and hasPathSouth and hasPathEast and hasPathWest):
            self.curSpriteName = "forest1_soil_c"

        # 3 positives
        elif (hasPathNorth and hasPathSouth and hasPathEast):
            self.curSpriteName = "forest1_soil_l"
        elif (hasPathNorth and hasPathSouth and hasPathWest):
            self.curSpriteName = "forest1_soil_r"
        elif (hasPathEast and hasPathWest and hasPathNorth):
            self.curSpriteName = "forest1_soil_b"
        elif (hasPathEast and hasPathWest and hasPathSouth):
            self.curSpriteName = "forest1_soil_t"

        # 2 positives (top/left or top/right or bottom/left or bottom/right)
        elif (hasPathNorth and hasPathWest):
            self.curSpriteName = "forest1_soil_br"
        elif (hasPathNorth and hasPathEast):
            self.curSpriteName = "forest1_soil_bl"
        elif (hasPathSouth and hasPathWest):
            self.curSpriteName = "forest1_soil_tr"
        elif (hasPathSouth and hasPathEast):
            self.curSpriteName = "forest1_soil_tl"

        else:
            # If we get here, then we have no path nearby (north/east/south/west)
            self.curSpriteName = "forest1_soil_single"

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName

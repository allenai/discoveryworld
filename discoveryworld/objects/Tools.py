from discoveryworld.ActionSuccess import ActionSuccess
from discoveryworld.objects.Object import Object


class Flag(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "flag", "flag", defaultSpriteName = "instruments_flag")

    def tick(self):
        # Call superclass
        Object.tick(self)


class FlowerPot(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "flowerpot", "flowerpot", defaultSpriteName = "generated_flowerpot")

        self.attributes["isMovable"] = True                       # Can it be moved?
        self.attributes["isPassable"] = True                      # Agen't can't walk over this

        # Container
        self.attributes['isContainer'] = True                      # Is it a container?
        self.attributes['isOpenable'] = False                      # Can not be opened (things are stored in the open pot)
        self.attributes['isOpenContainer'] = True                  # If it's a container, then is it open?
        self.attributes['containerPrefix'] = "in"                  # Container prefix (e.g. "in" or "on")

    def tick(self):
        # Call superclass
        Object.tick(self)


class Jar(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "jar", "jar", defaultSpriteName = "placeholder_jar_empty")

        self.attributes["isMovable"] = True                       # Can it be moved?
        self.attributes["isPassable"] = True                      # Agen't can't walk over this

        # Container
        self.attributes['isContainer'] = True                      # Is it a container?
        self.attributes['isOpenable'] = False                      # Can not be opened (things are stored in the open pot)
        self.attributes['isOpenContainer'] = True                  # If it's a container, then is it open?
        self.attributes['containerPrefix'] = "in"                  # Container prefix (e.g. "in" or "on")
        self.attributes['contentsVisible2D'] = False               # If it is a container, do we render the contents in the 2D representation, or is that already handled (e.g. for pots/jars, that render generic contents if they contain any objects)

        # Auto fill
        self.autoFillCheckForObjectName = None
        self.autoFillFillObjectName = None
        self.lastAddedCount = 0
        self.replenishTime = 5

    # If we want this object to autofill (i.e. perpetually fill with a supply of an object), set it here.
    def setAutoFill(self, checkObjectName:str, fillObjectName:str, minCount:int, replenishTime:int=8):
        self.autoFillCheckForObjectName = checkObjectName
        self.autoFillFillObjectName = fillObjectName
        self.autoFillMinCount = minCount
        self.replenishTime = replenishTime
        self.lastAddedCount = 0



    def tick(self):
        # Call superclass
        Object.tick(self)

        # Auto fill
        #if (self.autoFillObjectName != None and self.autoFillMinCount != None):
        if (self.autoFillCheckForObjectName != None) and (self.autoFillFillObjectName != None) and (self.autoFillMinCount != None):
            # Count how much of the object is contained within the root level of the contents
            count = 0
            for obj in self.contents:
                if (obj.name == self.autoFillCheckForObjectName):
                    count += 1

            # Fill up to the minimum count
            if (count < self.autoFillMinCount):
                # Check to see if the last added count is zero
                if (self.lastAddedCount <= 0):
                    # Add one more
                    objToAdd = self.world.createObject(self.autoFillFillObjectName)
                    self.addObject(objToAdd, force=True)
                    # Tick the object to update its sprite
                    objToAdd.tick()
                    # Invalidate object sprite
                    self.needsSpriteNameUpdate = True
                    # Tick
                    self.lastAddedCount = self.replenishTime     # Wait a few ticks before adding the next one
                else:
                    self.lastAddedCount -= 1




    # Sprite
    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return
        # Infer sprite based on whether empty/non-empty
        if (len(self.contents) == 0):
            self.curSpriteName = "placeholder_jar_empty"
        elif (len(self.contents) == 1):
            self.curSpriteName = "placeholder_jar_full1"
        elif (len(self.contents) == 2):
            self.curSpriteName = "placeholder_jar_full2"
        else:
            self.curSpriteName = "placeholder_jar_full3"

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName


class Key(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "key", "key", defaultSpriteName = "instruments_key")

        self.attributes["isMovable"] = True                       # Can it be moved?
        self.attributes["isPassable"] = True                      # Agen't can't walk over this

        # Container
        self.attributes['isContainer'] = False                    # Is it a container?

        # Rusted
        self.attributes['isRusted'] = True                        # Is the key rusted?
        self.attributes['rustLevel'] = 3                          # Description of the rust (0=none, 1=light, 2=medium, 3=heavy)

        # Key ID
        self.attributes['keyID'] = 1                              # Key ID (1 by default)


    def setKeyID(self, keyID:int):
        self.attributes['keyID'] = keyID


    def tick(self):
        # Call superclass
        Object.tick(self)

        # Clean rust of key (if conditions are met)
        # If the key is in a container, and that container contains SUBSTANCE TODO, and it's rusted, then remove the rust.
        # Check if the key is in a container
        if (self.parentContainer is not None):
            # Get parent container contents
            parentContainerContents = self.parentContainer.contents
            # Check if the parent container contains a specific substance
            containsCleaner = False
            print("### KEY: Checking for cleaner substance in parent container")
            partialEvidenceLevel = 0

            # Check to make sure there are not more than 1 subtances in the container
            numSubstances = 0
            for obj in parentContainerContents:
                if (obj.type == "substance"):
                    numSubstances += 1

            if (numSubstances > 1):
                print("## More than 1 substance in container.  Not evaluating rust reduction further, since those subtances may react later.")
                return

            for obj in parentContainerContents:
                print("## Key: Mixture dictionary: " + str(obj.attributes['mixtureDict']) + " (containsCleaner: " + str(containsCleaner) + ")")
                # Check for "Cleaner"
                if (obj.type == "substance") and (obj.attributes["substanceName"] == "cleaner"):
                    containsCleaner = True
                    break
                # Check for a specific mixture (1 part Substance A, 2 parts substance C)
                if (obj.type == "substance") and (len(obj.attributes['mixtureDict']) == 2):
                    print("### In container with substance  (mixtureDict: " + str(obj.attributes['mixtureDict']) + ")")
                    if ("Substance A" in obj.attributes['mixtureDict']) and ("Substance C" in obj.attributes['mixtureDict']):
                        print("### In container with Substance A and C")
                        if (obj.attributes['mixtureDict']["Substance A"] == 1) and (obj.attributes['mixtureDict']["Substance C"] == 2):
                            print("### In container with Substance A and C, and the right proportions")
                            containsCleaner = True
                            break
                # Partial evidence -- give som[;[][e help for hill-climbing
                if ("Substance A" in obj.attributes['mixtureDict']) and ("Substance B" not in obj.attributes['mixtureDict']):
                    partialEvidenceLevel += 1
                    print("## Partial evidence (Substance A)")
                if ("Substance C" in obj.attributes['mixtureDict']) and ("Substance B" not in obj.attributes['mixtureDict']):
                    partialEvidenceLevel += 1
                    print("## Partial evidence (Substance C)")

            # If the parent container contains the cleaner substance, then remove the rust from the key
            if (containsCleaner):
                self.attributes['isRusted'] = False
                self.attributes['rustLevel'] = 0    # No more rust
                # Invalidate the sprite
                self.needsSpriteNameUpdate = True

            # Handle partial evidence -- describe the key as less rusty, if certain combinations of substances are found
            print("### Partial evidence level: " + str(partialEvidenceLevel))
            if (partialEvidenceLevel > 0):
                # If the partial evidence level is high enough, then remove the rust from the key
                newRustLevel = 3 - partialEvidenceLevel
                if (newRustLevel < self.attributes['rustLevel']):
                    self.attributes['rustLevel'] = newRustLevel
                    self.needsSpriteNameUpdate = True

        # Update key name based on whether it's rusted or not
        # If the key is rusted, then set it's name to key (rusted)
        if (self.attributes['isRusted']):# and (self.name != "rusted key"):
            if (self.attributes['rustLevel'] == 3):
                self.name = "rusted key (heavily rusted)"
            elif (self.attributes['rustLevel'] == 2):
                self.name = "rusted key (moderately rusted)"
            elif (self.attributes['rustLevel'] == 1):
                self.name = "rusted key (lightly rusted)"

        elif (not self.attributes['isRusted']):
            self.name = "key (no rust)"



    # Sprite
    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return

        # If rusted, use the rusty sprite
        if (self.attributes['isRusted']):
            self.curSpriteName = "instruments_key_rusty"
        else:
            self.curSpriteName = "instruments_key"

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName


class Pot(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "pot", "pot", defaultSpriteName = "placeholder_pot_empty")

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

    # Sprite
    # Updates the current sprite name based on the current state of the object
    def inferSpriteName(self, force:bool=False):
        if (not self.needsSpriteNameUpdate and not force):
            # No need to update the sprite name
            return
        # Infer sprite based on whether empty/non-empty
        if (len(self.contents) == 0):
            self.curSpriteName = "placeholder_pot_empty"
        elif (len(self.contents) == 1):
            self.curSpriteName = "placeholder_pot_full1"
        elif (len(self.contents) == 2):
            self.curSpriteName = "placeholder_pot_full2"
        else:
            self.curSpriteName = "placeholder_pot_full3"

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName


class Shovel(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "shovel", "shovel", defaultSpriteName = "placeholder_shovel")

        self.attributes["isMovable"] = True                       # Can it be moved?
        self.attributes["isPassable"] = True                      # Agen't can't walk over this

        self.attributes["isUsable"] = True                        # Can it be used?

    #
    #   Actions (use with)
    #
    def actionUseWith(self, patientObj):
        # Use this object on the patient object

        # Check if the patient object has the 'isShovelable' attribute
        if (not patientObj.attributes["isShovelable"]):
            # Can't use the shovel on this object
            return ActionSuccess(False, "You can't use the shovel on that.")


        # Run the 'useWithShovelResult' function on the patient object
        result = patientObj.useWithShovelResult()

        # Return the result
        return result


    def tick(self):
        # Call superclass
        Object.tick(self)

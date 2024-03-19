import copy

from discoveryworld.ActionSuccess import ActionSuccess, MessageImportance
from discoveryworld.objects.Object import Object
from discoveryworld.ScienceHelpers import getNPKContent, getRadiationLevelAroundLocation


class Microscope(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "microscope", "microscope", defaultSpriteName = "instruments_microscope")

        # Default attributes

        self.attributes['isUsable'] = True                       # Can this device be used with another object? (e.g. specifically through the 'use' action)

    #
    #   Actions (use with)
    #
    def actionUseWith(self, patientObj):
        # Use this object on the patient object
        microscopeDescriptionStr = "You use the microscope to observe the " + patientObj.name + ".\n"
        # Get the description of the object as observed under a microscope
        microscopeDescriptionStr += patientObj.getTextObservationMicroscopic()
        # Return the action response
        return ActionSuccess(True, microscopeDescriptionStr, importance=MessageImportance.HIGH)

    #
    #   Tick
    #
    def tick(self):
        # TODO: Invalidate sprite name if this or neighbouring walls change
        if (False):
            self.needsSpriteNameUpdate = True

        # TODO

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


class NPKMeter(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "NPK field test", "NPK field test", defaultSpriteName = "instruments_npk_fieldtest")

        # Default attributes

        self.attributes['isUsable'] = True                       # Can this device be used with another object? (e.g. specifically through the 'use' action)

        pass


    #
    #   Actions (use with)
    #
    def actionUseWith(self, patientObj):
        # Use this object on the patient object
        useDescriptionStr = "You use the NPK field test to investigate the " + patientObj.name + ".\n"

        npk = getNPKContent(patientObj)
        totalNitrogen = npk["nitrogen"]
        totalPhosphorus = npk["phosphorus"]
        totalPotassium = npk["potassium"]

        # If any numbers are greater than 10, then clip the results to 10
        MAX_READING = 10
        if (totalNitrogen > MAX_READING):
            totalNitrogen = MAX_READING
        if (totalPhosphorus > MAX_READING):
            totalPhosphorus = MAX_READING
        if (totalPotassium > MAX_READING):
            totalPotassium = MAX_READING

        # Report the PH (to 1 decimal place(s)
        useDescriptionStr += "The test ranges from 0 (no presence detected) to 10 (the maximum value of the test has been exceeded). \n"
        useDescriptionStr += "The screen on the field test reports the following numbers: \n"
        useDescriptionStr += " Nitrogen: " + "{:.1f}".format(totalNitrogen) + "\n"
        useDescriptionStr += " Phosphorus: " + "{:.1f}".format(totalPhosphorus) + "\n"
        useDescriptionStr += " Potassium: " + "{:.1f}".format(totalPotassium) + "\n"

        return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)

    #
    #   Tick
    #
    def tick(self):
        # TODO: Invalidate sprite name if this or neighbouring walls change
        if (False):
            self.needsSpriteNameUpdate = True

        # TODO

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


class PetriDish(Object):
    # Constructor
    def __init__(self, world):
        # Default sprite name
        Object.__init__(self, world, "petri dish", "petri dish", defaultSpriteName = "instruments_petri_dish_empty")

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
            self.curSpriteName = "instruments_petri_dish_empty"
        else:
            self.curSpriteName = "instruments_petri_dish_full"

        # This will be the next last sprite name (when we flip the backbuffer)
        self.tempLastSpriteName = self.curSpriteName


class PHMeter(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "PH meter", "PH meter", defaultSpriteName = "instruments_ph_meter")

        # Default attributes

        self.attributes['isUsable'] = True                       # Can this device be used with another object? (e.g. specifically through the 'use' action)

        pass


    #
    #   Actions (use with)
    #
    def actionUseWith(self, patientObj):
        # Use this object on the patient object
        useDescriptionStr = "You use the PH meter to investigate the " + patientObj.name + ".\n"

        # Get the patient object, and all its parts
        # def getAllContainedObjectsAndParts(self, includeContents=True, includeParts=True):
        patientObjAndParts = patientObj.getAllContainedObjectsAndParts(includeContents=False, includeParts=True)
        # Collect the materials of the object and its parts
        patientMaterials = []
        for patientObjOrPart in patientObjAndParts:
            if ("materials" in patientObjOrPart.attributes):
                patientMaterials.extend(patientObjOrPart.attributes["materials"])

        # Get the spectra of the materials
        phs = []
        for patientMaterial in patientMaterials:
            if ("ph" in patientMaterial):
                phs.append(patientMaterial["ph"])

        # If there are no spectra, say the results are inconclusive.
        if (len(phs) == 0):
            useDescriptionStr += "The results are inconclusive.\n"
            return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)

        # Calculate the spectrum (as emission)
        # First, check the length of the spectra, and create a new spectrum of that length

        # Calculate the average PH of the materials (NOTE: this is not physically accurate)
        averagePH = sum(phs) / len(phs)

        # Report the PH (to 1 decimal place(s)
        useDescriptionStr += "The PH meter reports a PH of " + "{:.1f}".format(averagePH) + ".\n"

        return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)

    #
    #   Tick
    #
    def tick(self):
        # TODO: Invalidate sprite name if this or neighbouring walls change
        if (False):
            self.needsSpriteNameUpdate = True

        # TODO

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


class RadiationMeter(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "radiation meter", "radiation meter", defaultSpriteName = "instruments_radiation_meter")

        # Default attributes
        self.attributes['isUsable'] = True                       # Can this device be used with another object? (e.g. specifically through the 'use' action)

    #
    #   Actions (use with)
    #
    def actionUseWith(self, patientObj):
        # Use this object on the patient object
        useDescriptionStr = "You use the radiation meter to investigate the " + patientObj.name + ".\n"

        # Get the patient object, and all its parts
        # def getAllContainedObjectsAndParts(self, includeContents=True, includeParts=True):
        patientObjAndParts = patientObj.getAllContainedObjectsAndParts(includeContents=False, includeParts=True)
        # Collect the materials of the object and its parts
        patientMaterials = []
        for patientObjOrPart in patientObjAndParts:
            if ("materials" in patientObjOrPart.attributes):
                patientMaterials.extend(patientObjOrPart.attributes["materials"])

        # Get the radiation levels of each material
        radiationLevels = []
        for patientMaterial in patientMaterials:
            if ("radiationusvh" in patientMaterial):
                radiationLevels.append(patientMaterial["radiationusvh"])

        # If there are radiation levels, say the results are inconclusive.
        # TODO: Just use background rate, then?
        if (len(radiationLevels) == 0):
            radiationLevels = [0]
            #useDescriptionStr += "The results are inconclusive.\n"
            #return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)

        # Calculate the radiation level of this object (sum of all radiation levels of each material)
        radiationLevelMicroSeivertsPerHour = sum(radiationLevels)
        # Add a random amount of background radiation, drawn from the current background radiation rate.  First, generate a number between 0-avgRadiationBackgroundLevelUSVH
        backgroundRadiation = self.rng.random() * self.world.parameters["avgRadiationBackgroundLevelUSVH"]
        # Add the background radiation to the radiation level
        radiationLevelMicroSeivertsPerHour += backgroundRadiation

        # Also add the radiation from any objects near this location, using the inverse square law.
        backgroundNearLocation = getRadiationLevelAroundLocation(self.world, self.attributes["gridX"], self.attributes["gridY"], excludeObject=patientObj, windowSize=5)
        radiationLevelMicroSeivertsPerHour += backgroundNearLocation

        # TODO: Also add the radiation from any other objects near this location.

        # Report the radiation level (to 2 decimal place(s)
        useDescriptionStr += "The radiation meter reports a level of " + "{:.2f}".format(radiationLevelMicroSeivertsPerHour) + " micro Seiverts per hour.\n"
        useDescriptionStr += "DEBUG:\n Background radiation: " + "{:.2f}".format(backgroundRadiation) + " micro Seiverts per hour.\n"
        useDescriptionStr += "DEBUG:\n Background near location: " + "{:.2f}".format(backgroundNearLocation) + " micro Seiverts per hour.\n"

        return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)
    #
    #   Tick
    #
    def tick(self):
        # TODO: Invalidate sprite name if this or neighbouring walls change
        if (False):
            self.needsSpriteNameUpdate = True

        # TODO

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


class Sample(Object):
    """ A Sample is a special type of object that clones the attributes of another parent object, but not its contents. """
    def __init__(self, world, parentObject):
        # Default sprite name
        Object.__init__(self, world, "sample", "sample of " + parentObject.name, defaultSpriteName = "instruments_sample")

        # Materials
        # Deep copy the materials from the parent object
        self.attributes["materials"] = copy.deepcopy(parentObject.attributes["materials"])

        # Parts (for composite objects -- similar to containers)
        self.parts = []
        # For each part in the parent object, create a new part in this object
        for parentPart in parentObject.parts:
            # Create a new part, and add it to this object
            newPart = Sample(self.world, parentPart)
            self.parts.append(newPart)

        # Poison/health attributes
        self.attributes['isPoisonous'] = parentObject.attributes['isPoisonous'] if ('isPoisonous' in parentObject.attributes) else False
        self.attributes['temperatureC'] = parentObject.attributes['temperatureC'] if ('temperatureC' in parentObject.attributes) else 20.0

        # Remove the parent object's contents
        self.contents = []


class Sampler(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "sampler", "sampler", defaultSpriteName = "instruments_sampler")

        # Default attributes

        self.attributes['isUsable'] = True                       # Can this device be used with another object? (e.g. specifically through the 'use' action)

        pass


    #
    #   Actions (use with)
    #
    def actionUseWith(self, patientObj):
        # Use this object on the patient object
        useDescriptionStr = "You use the sampler to take a sample of the " + patientObj.name + ".\n The sample has been placed in your inventory.\n"

        # Create a sample of the patient
        sample = Sample(self.world, patientObj)
        petriDish = PetriDish(self.world)
        petriDish.addObject(sample)

        # Place the sample in the same parent container as the sampler.
        self.parentContainer.addObject(petriDish)

        return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)

    #
    #   Tick
    #
    def tick(self):
        # TODO: Invalidate sprite name if this or neighbouring walls change
        if (False):
            self.needsSpriteNameUpdate = True

        # TODO

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


class Spectrometer(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "spectrometer", "spectrometer", defaultSpriteName = "instruments_spectrometer")

        # Default attributes

        self.attributes['isUsable'] = True                       # Can this device be used with another object? (e.g. specifically through the 'use' action)

        pass


    #
    #   Actions (use with)
    #
    def actionUseWith(self, patientObj):
        # Use this object on the patient object
        useDescriptionStr = "You use the spectrometer to examine the " + patientObj.name + ".\n"

        # Get the patient object, and all its parts
        # def getAllContainedObjectsAndParts(self, includeContents=True, includeParts=True):
        patientObjAndParts = patientObj.getAllContainedObjectsAndParts(includeContents=False, includeParts=True)
        # Collect the materials of the object and its parts
        patientMaterials = []
        for patientObjOrPart in patientObjAndParts:
            if ("materials" in patientObjOrPart.attributes):
                patientMaterials.extend(patientObjOrPart.attributes["materials"])

        # Get the spectra of the materials
        spectra = []
        for patientMaterial in patientMaterials:
            if ("spectrum" in patientMaterial):
                spectra.append(patientMaterial["spectrum"])

        # If there are no spectra, say the results are inconclusive.
        if (len(spectra) == 0):
            useDescriptionStr += "The results are inconclusive.\n"
            return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)

        # Calculate the spectrum (as emission)
        # First, check the length of the spectra, and create a new spectrum of that length
        spectrumLength = len(spectra[0])
        spectrum = [0] * spectrumLength
        # Then, add the spectra together
        for spectrumToAdd in spectra:
            for i in range(spectrumLength):
                # Check that it's within the bounds of the spectrum
                if (i < len(spectrumToAdd)):
                    spectrum[i] += spectrumToAdd[i]

        # Then, report the spectrum
        useDescriptionStr += "The results are as follows:\n"
        for i in range(spectrumLength):
            #useDescriptionStr += "Channel 1: " + str(spectrum[i]) + "\n"
            # report to 1 decimal place(s)
            useDescriptionStr += "- Channel " + str(i+1) + ": " + "{:.2f}".format(spectrum[i]) + "\n"

        return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)

    #
    #   Tick
    #
    def tick(self):
        # TODO: Invalidate sprite name if this or neighbouring walls change
        if (False):
            self.needsSpriteNameUpdate = True

        # TODO

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


class Thermometer(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "thermometer", "thermometer", defaultSpriteName = "instruments_thermometer")

        # Default attributes

        self.attributes['isUsable'] = True                       # Can this device be used with another object? (e.g. specifically through the 'use' action)

        pass


    #
    #   Actions (use with)
    #
    def actionUseWith(self, patientObj):
        # Use this object on the patient object
        useDescriptionStr = "You use the thermometer to measure the temperature of the " + patientObj.name + ".\n"

        # Get the patient object's temperature
        patientTemperature = patientObj.attributes["temperatureC"]
        if (patientTemperature == None):
            useDescriptionStr += "The results are inconclusive.\n"
            return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)

        # Report the temperature (to 1 decimal place(s)
        useDescriptionStr += "The thermometer reports a temperature of " + "{:.1f}".format(patientTemperature) + " degrees Celsius.\n"

        return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)

    #
    #   Tick
    #
    def tick(self):
        # TODO: Invalidate sprite name if this or neighbouring walls change
        if (False):
            self.needsSpriteNameUpdate = True

        # TODO

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



# TODO: Implement density measurement
class Densitometer(Object):
    # Constructor
    def __init__(self, world):
        Object.__init__(self, world, "densitometer", "densitometer", defaultSpriteName = "instruments_densitometer")

        # Default attributes

        self.attributes['isUsable'] = True                       # Can this device be used with another object? (e.g. specifically through the 'use' action)

        pass


    #
    #   Actions (use with)
    #
    def actionUseWith(self, patientObj):
        ### TODO: CURRENTLY JUST COPIED/PASTED FROM THE SPECTROMETER.

        # Use this object on the patient object
        useDescriptionStr = "You use the densitometer to examine the " + patientObj.name + ".\n"

        # seedMediumArtifact.attributes["radioisotopeValues"]
        # Check for a "radioisotopeValues" attribute in the patient object
        if ("density" not in patientObj.attributes):
            useDescriptionStr += "The results are inconclusive.\n"
            return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)

        # If the list is empty, then the results are inconclusive
        if (patientObj.attributes["density"] <= 0):
            useDescriptionStr += "The results are inconclusive.\n"
            return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)

        # If there are values, then report the values
        useDescriptionStr += "The results are as follows:\n"
        useDescriptionStr += "The density of the " + patientObj.name + " appears to be approximately " + "{:.3f}".format(patientObj.attributes["density"]) + " grams per cubic centimeter.\n"

        return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)

    #
    #   Tick
    #
    def tick(self):
        # TODO: Invalidate sprite name if this or neighbouring walls change
        if (False):
            self.needsSpriteNameUpdate = True

        # TODO

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


class CountingComputer(Object):
    def __init__(self, world):
        Object.__init__(self, world, "computer", "computer", defaultSpriteName="instruments_spectrometer")

        # Default attributes
        self.attributes['isUsable'] = True  # Can this device be used with another object? (e.g. specifically through the 'use' action)

    def actionUseWith(self, otherObject):
        # Use this object on the patient object
        useDescriptionStr = "You use the computer to count numbers.\n"

        # # Get the patient object, and all its parts
        # # def getAllContainedObjectsAndParts(self, includeContents=True, includeParts=True):
        # patientObjAndParts = patientObj.getAllContainedObjectsAndParts(includeContents=False, includeParts=True)
        # # Collect the materials of the object and its parts
        # patientMaterials = []
        # for patientObjOrPart in patientObjAndParts:
        #     if ("materials" in patientObjOrPart.attributes):
        #         patientMaterials.extend(patientObjOrPart.attributes["materials"])

        # # Get the radiation levels of each material
        # radiationLevels = []
        # for patientMaterial in patientMaterials:
        #     if ("radiationusvh" in patientMaterial):
        #         radiationLevels.append(patientMaterial["radiationusvh"])

        # # If there are radiation levels, say the results are inconclusive.
        # # TODO: Just use background rate, then?
        # if (len(radiationLevels) == 0):
        #     radiationLevels = [0]
        #     #useDescriptionStr += "The results are inconclusive.\n"
        #     #return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)

        # # Calculate the radiation level of this object (sum of all radiation levels of each material)
        # radiationLevelMicroSeivertsPerHour = sum(radiationLevels)
        # # Add a random amount of background radiation, drawn from the current background radiation rate.  First, generate a number between 0-avgRadiationBackgroundLevelUSVH
        # backgroundRadiation = self.rng.random() * self.world.parameters["avgRadiationBackgroundLevelUSVH"]
        # # Add the background radiation to the radiation level
        # radiationLevelMicroSeivertsPerHour += backgroundRadiation

        # # Also add the radiation from any objects near this location, using the inverse square law.
        # backgroundNearLocation = getRadiationLevelAroundLocation(self.world, self.attributes["gridX"], self.attributes["gridY"], excludeObject=patientObj, windowSize=5)
        # radiationLevelMicroSeivertsPerHour += backgroundNearLocation

        # # TODO: Also add the radiation from any other objects near this location.

        # # Report the radiation level (to 2 decimal place(s)
        # useDescriptionStr += "The radiation meter reports a level of " + "{:.2f}".format(radiationLevelMicroSeivertsPerHour) + " micro Seiverts per hour.\n"
        # useDescriptionStr += "DEBUG:\n Background radiation: " + "{:.2f}".format(backgroundRadiation) + " micro Seiverts per hour.\n"
        # useDescriptionStr += "DEBUG:\n Background near location: " + "{:.2f}".format(backgroundNearLocation) + " micro Seiverts per hour.\n"

        return ActionSuccess(True, useDescriptionStr, importance=MessageImportance.HIGH)

    

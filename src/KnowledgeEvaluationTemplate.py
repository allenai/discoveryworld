# KnowledgeEvaluationTemplate.py

import argparse
import pickle
import zlib
import json


#
#   Storage class for an object
#
class KEObject():
    # Constructor
    def __init__(self, initDict:dict):
        self.uuid = initDict['uuid']
        self.name = initDict['name']
        self.type = initDict['type']
        self.contents = initDict['contents']
        self.attributes = initDict['attributes']

    # Override __getattr__ to allow any 'attribute' to be accessed as a direct attribute. 
    # If the attribute does not exist, return None
    def __getattr__(self, item):
        # Check if the attribute exists in self.attributes
        value = self.attributes.get(item, None)
        if (value != None):
            return value

        # Check if the attribute exists in self.materials (which is a list of materials)
        for material in self.materials:
            value = material.get(item, None)
            if (value != None):
                return value

        # Otherwise, return None
        return None



#
#   Knowledge Evaluation Template
# 
class KnowledgeEvaluationTemplate():
    # Constructor
    def __init__(self):
        # Step 1: Load the world history
        self.worldHistoryFilename = "sandbox/worldHistory.pickle"
        self.worldHistory = self.loadWorldHistory(self.worldHistoryFilename)

        self.evaluationResults = {}

    #
    #   Import/Export
    #

    # Import the world history from a (pickled) file
    def loadWorldHistory(self, filename):
        print("Importing world history from file: " + filename + "...")
        f = open(filename, "rb")
        worldHistory = pickle.loads(f.read())
        f.close()        
        print("Import complete.")
        return worldHistory

    # Export the results of the evaluation
    def exportEvaluationResults(self, filename):
        print("Exporting evaluation results to file: " + filename + "...")
        f = open(filename, "w")
        f.write(json.dumps(self.evaluationResults))
        f.close()        
        print("Export complete.")


    #
    #   World History access functions
    #
    def getWorldHistoryAtStep(self, step):
        # Return the world history at the specified step
        # Since the world history is pickled then compressed, this will require uncompressing then unpickling
        print( type(self.worldHistory) )
        if (step < 0 or step >= len(self.worldHistory)):
            return None

        # Get compressed history for a given step
        compressedPickled = self.worldHistory[step]

        # Uncompress the history
        pickled = zlib.decompress(compressedPickled)
        # Unpickle the history
        history = pickle.loads(pickled)

        # Convert the history to just a list of all objects at that step
        allObjects = []
        allObjectsByUUID = {}
        # Traverse grid, adding all objects to the list
        grid = history['grid']
        for row in grid:
            for cell in row:                
                for obj in cell:
                    convertedObj = KEObject(obj)
                    allObjects.append(convertedObj)
                    allObjectsByUUID[convertedObj.uuid] = convertedObj

                    if (convertedObj.type == "agent"):
                        print(obj)
                        print("\n\n")

        return allObjects, allObjectsByUUID



    #
    #   Functions for building the hypothesis queries
    #

    def getProperty(self, obj, property):
        # Return the value of the property of the object

        pass


    #
    #   Functions for testing whether the hypothesis assertion (i.e. it's THEN statement) is true    
    #
    def testHypothesisAssertion(self, hypothesisAssertion):
        pass

    #
    #   The hypothesis itself
    #
    def testHypothesis(self):
        pass


    def exampleHypothesis1(self, obj1):
        # If a mushroom exists, and it is either red or pink, then it is poisonous
        #if (obj1.type == "mushroom") and (obj1.color == "red" or obj1.color == "pink"):
        if (obj1.name == "mushroom"):
            if (obj1.MaterialName == "plant matter"):
            #self.testHypothesisAssertion(obj1.poisonous == True)
            #if (obj1.isPoisonous == True):
                return True

        return False        

    def exampleHypothesis2(self):
        # If an agent eats a mushroom, then it will become sick within 50 steps in the future. 
        pass



#
#   Main
#
if __name__ == "__main__":
    # Parse command line arguments to get the export filename 
    # (e.g. python KnowledgeEvaluationTemplate.py --exportFilename=evaluationResults.json)
    parser = argparse.ArgumentParser()
    parser.add_argument("--exportFilename", type=str, default="evaluationResults.json", help="Filename to export the evaluation results to")
    args = parser.parse_args()

    # Step 1: Initialize the knowledge evaluation template (and load the world history)
    knowledgeEvaluationTemplate = KnowledgeEvaluationTemplate()

    # Step 2: Run the hypothesis
    # TODO
    allObjects, allObjectsByUUID = knowledgeEvaluationTemplate.getWorldHistoryAtStep(5)
    #print(allObjectsByUUID)

    print("")
    print("\n------------------\n")
    print("Evaluating Hypothesis 1...")
    for obj in allObjects:
        result = knowledgeEvaluationTemplate.exampleHypothesis1(obj)
        if (result == True):
            print("Hypothesis 1 is true for object: " + obj.name)
            print(str(obj.attributes))
    
    print("")
    print("\n------------------\n")

    # Step 3: Export the results (use command line argument to specify filename)
    knowledgeEvaluationTemplate.exportEvaluationResults(args.exportFilename)
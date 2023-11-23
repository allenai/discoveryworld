# KnowledgeEvaluationTemplate.py

import argparse
import pickle
import zlib
import json

#
#   Load world history
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
        self.worldHistory = pickle.loads(f.read())
        f.close()
        print("Import complete.")

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
        if (step < 0 or step >= len(self.worldHistory)):
            return None

        # Get compressed history for a given step
        compressedPickled = self.worldHistory[step]

        # Uncompress the history
        pickled = zlib.decompress(compressedPickled)
        # Unpickle the history
        history = pickle.loads(pickled)

        return history



    #
    #   Functions for building the hypothesis queries
    #



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


    def exampleHypothesis1(self):
        # If a mushroom exists, and it is either red or pink, then it is poisonous
        pass

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

    # Step 3: Export the results (use command line argument to specify filename)
    knowledgeEvaluationTemplate.exportEvaluationResults(args.exportFilename)
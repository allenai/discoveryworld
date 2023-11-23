# SandboxPython.py




# Class to run a sandboxed hypothesis represented as an 'IF statement' in Python, on the world state history (represented as an external JSON file)
class SandboxPython():
    # Constructor
    def __init__(self, world):
        self.world = world

        # Paths/Filenames        
        self.pathSandbox = "sandbox/"                               # Sandbox path out
        self.worldStateHistoryFilename = "worldStateHistory.json"   # Filename of the world history to export

        self.evaluationTemplateFilename = "src/KnowledgeEvaluationTemplate.py"   # Filename of the evaluation template

    
    def testHypothesis(self, hypothesisPythonStr:str):
        # Step 1: Export the world state history to a JSON file
        exportFilename = self.pathSandbox + self.worldStateHistoryFilename
        self.world.exportWorldStateHistory(exportFilename)

        # Step 2: Export the hypothesis to a Python file

        # Step 3: Run the hypothesis against the world state history, using a `FireJail` sandbox

        # Step 4: Read the output of the sandbox, parsing the result (i.e. whether the hypothesis is true or not -- or rather, the proportion of the time that the hypothesis is true)


        return 0.0    

    
    #
    #   Helper functions
    #

    def __exportHypothesisWithTemplate(self, hypothesisPythonStr:str, exportFilename:str):
        # Export the hypothesis to a Python file, using the evaluation template
        pass

    def __runSandbox(self, sandboxFilename:str):
        # Run the sandboxed Python file
        pass
        
    def __readEvaluationResults(self, evaluationFilename:str):
        # Read the results of the evaluation
        pass



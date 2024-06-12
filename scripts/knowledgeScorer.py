# knowledgeScorer.py
from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI

import os
import time
import json
import openai

# def runRandomAgent(scenarioName:str, difficultyStr:str, seed:int=0, numSteps:int=10, exportVideo:bool=False, threadId:int=1, debug:bool=False):
#     # Load the scenario
#     api = DiscoveryWorldAPI(threadID=threadId)
#     success = api.loadScenario(scenarioName = scenarioName, difficultyStr = difficultyStr, randomSeed = seed, numUserAgents = 1)

class KnowledgeScorer:
    # Constructor
    def __init__(self, model = "gpt-4o"):
        # Make a new DiscoveryWorld API instance
        self.api = DiscoveryWorldAPI()
        # OpenAI Client
        # First, check for a file `openai_key.txt` in the current directory
        # If it exists, read the API key from it
        self.modelName = model
        try:
            with open("openai_key.txt", "r") as f:
                key = f.read().strip()
            self.client = openai.AzureOpenAI(api_key=key) if openai.api_type == "azure" else openai.OpenAI(api_key=key)
        except FileNotFoundError:
            # If the file doesn't exist, check for an environment variable
            if ("OPENAI_API_KEY" in os.environ):
                self.client = openai.AzureOpenAI(api_key=os.getenv("OPENAI_API_KEY")) if openai.api_type == "azure" else openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Keep track of the number of errors (if any) when making requests
        self.OPENAI_REQUESTS_ERRORS = 0
        self.OPENAI_REQUESTS_NOERRORS = 0


    # OpenAI completion -- submit a prompt, get a JSON response back.

    def OpenAIGetCompletion(self, client, promptStr:str, model, temperature=0.0, maxTokens=800, jsonResponse:bool=True):
        while (self.OPENAI_REQUESTS_ERRORS < 5):
            try:
                result = self.OpenAIGetCompletionHelper(client, promptStr, model, temperature, maxTokens, jsonResponse)
                self.OPENAI_REQUESTS_NOERRORS += 1
                # If we get 100 requests without errors, reset the error counter
                if (self.OPENAI_REQUESTS_NOERRORS > 100):
                    self.OPENAI_REQUESTS_ERRORS = 0
                return result

            # Keyboard interrupt
            except KeyboardInterrupt:
                print("Keyboard interrupt detected.  Exiting.")
                exit(1)

            # Kill signal
            except SystemExit:
                print("System exit detected.  Exiting.")
                exit(1)

            except Exception as e:
                print("ERROR: OpenAI request failed.")
                print("ERROR: " + str(e))
                self.OPENAI_REQUESTS_ERRORS += 1
                # Wait a bit before trying again
                print("Waiting 5 seconds before trying again.")
                time.sleep(5)

        # If we get here, we've exceeded the number of errors
        print("ERROR: Exceeded the number of OPEN_AI errors allowed (5 errors within 100 requests).  Exiting.")
        exit(1)

    def OpenAIGetCompletionHelper(self, client, promptStr:str, model:str, temperature=0.0, maxTokens=800, jsonResponse:bool=False):
        content = []

        # Add main prompt
        content.append({"type": "text", "text": promptStr})

        # Create the message prompt, initially including only the prompt string
        messages=[
            {
                "role": "user",
                "content": content,
            }
        ]

        response = {}

        # Get the response
        if (jsonResponse == False):
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=maxTokens,
                temperature=temperature,
            )
        else:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=maxTokens,
                temperature=temperature,
                response_format={ "type": "json_object" },
            )

        # Return the response
        #print("RESPONSE:")
        #print(response)
        #print("")
        print("RESPONSE CONTENT:")
        print(response.choices[0].message.content)


        return response


    # Evaluate the knowledge of an agent
    def evaluateKnowledge(self, scenarioName:str, difficultyStr:str, seed:int, knowledgeToEvaluateStr:str):
        # Load the scenario
        success = self.api.loadScenario(scenarioName = scenarioName, difficultyStr = difficultyStr, randomSeed = seed, numUserAgents = 1)
        if not success:
            print("Failed to load scenario")
            return None

        # Get the task(s)
        world = self.api.world
        if (world == None):
            print("No world found")
            return None

        # Get the tasks
        taskScorer = world.taskScorer
        if (taskScorer == None):
            print("No task scorer found")
            return None

        # Iterate through the tasks to collect helpful information for scoring
        tasks = []
        for task in taskScorer.tasks:
            taskOut = {}
            taskOut["taskName"] = task.taskName
            taskOut["taskDescription"] = task.taskDescription
            taskOut["criticalHypotheses"] = task.criticalHypotheses
            taskOut["criticalQuestions"] = task.criticalQuestions
            tasks.append(taskOut)

        # Evaluate the knowledge
        print(json.dumps(tasks, indent=4))

        for task in tasks:
            task["evaluation"] = []
            totalScore = 0
            for criticalQuestion in task["criticalQuestions"]:
                print("Critical Question: " + criticalQuestion)

                promptStr = "Your task is to evaluate the knowledge of an agent playing a game about scientific discovery, to see if they have figured out the discovery required to solve the task.\n"
                promptStr += "I will supply you with: (1) the task description, (2) the agent's knowledge, and (3) a single critical question about the discovery, that you should answer with either true (1) or false (0). \n"
                promptStr += "\n"
                promptStr += "Task Description:\n"
                promptStr += "```\n"
                promptStr += task["taskDescription"] + "\n"
                promptStr += "```\n"
                promptStr += "\n"
                promptStr += "Agent's Knowledge:\n"
                promptStr += "```\n"
                if (type(knowledgeToEvaluateStr) == str):
                    promptStr += knowledgeToEvaluateStr + "\n"
                else:
                    promptStr += json.dumps(knowledgeToEvaluateStr, indent=4) + "\n"
                promptStr += "```\n"
                promptStr += "\n"
                promptStr += "Critical Question:\n"
                promptStr += "```\n"
                promptStr += criticalQuestion + "\n"
                promptStr += "```\n"
                promptStr += "\n"
                promptStr += "Please answer this question by responding `1` if the agent's knowledege reflects having discovered the information in the critical question, and `0` otherwise.  This response should be in the `evaluation` key of the response.\n"
                promptStr += "The response format is a JSON dictionary containing three keys: `criticalQuestion`, `evaluation`, and `explanation`. \n"
                promptStr += "```\n"
                promptStr += "{\n"
                promptStr += "    \"criticalQuestion\": \"repeat the critical question\",\n"
                promptStr += "    \"evaluation\": 0 or 1 (as integers),\n"
                promptStr += "    \"explanation\": \"provide a brief explanation for evaluation, making reference to the agent's knowledge and whether or not it reflects the critical question.\"\n"
                promptStr += "}\n"
                promptStr += "```\n"

                # Get the response from OpenAI
                response = self.OpenAIGetCompletion(self.client, promptStr, self.modelName, temperature=0.0, maxTokens=800, jsonResponse=True)
                # Try to convert the response to a dictionary
                responseDict = None
                try:
                    responseDict = json.loads(response.choices[0].message.content)
                except:
                    print("ERROR: Failed to convert response to dictionary.")
                    print(response.choices[0].message.content)

                # Add the response to the task
                task["evaluation"].append(responseDict)
                if (responseDict != None) and ("evaluation" in responseDict):
                    # Check type
                    value = responseDict["evaluation"]
                    if (type(value) != int):
                        # Try to convert
                        try:
                            responseDict["evaluation"] = int(value)
                        except:
                            print("ERROR: Evaluation value is not an integer. (" + str(value) + ")" )

                    if (type(value) == int):
                        totalScore += responseDict["evaluation"]

            # Store the total score
            task["evaluation_totalscore_raw"] = totalScore
            if (len(task["criticalQuestions"]) > 0):
                task["evaluation_totalscore"] = totalScore / len(task["criticalQuestions"])
            else:
                task["evaluation_totalscore"] = 0

            # Include the reference knowledge
            task["knowledge_to_evaluate"] = knowledgeToEvaluateStr

        # Return
        return tasks



#
#   Main (example)
#
if __name__ == "__main__":
    # Create a knowledge scorer
    knowledgeScorer = KnowledgeScorer()

    # Evaluate the knowledge
    knowledgeToEvaluate = "The food is infected with space ants."
    evaluation = knowledgeScorer.evaluateKnowledge(scenarioName = "Space Sick", difficultyStr = "Easy", seed = 0, knowledgeToEvaluateStr=knowledgeToEvaluate)

    print("\n\n")
    print("-" * 80)
    print("Evaluation:")
    print(json.dumps(evaluation, indent=4))
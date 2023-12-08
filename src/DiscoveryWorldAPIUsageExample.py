# DiscoveryWorldAPIUsageExample.py


from DiscoveryWorldAPI import DiscoveryWorldAPI

from openai import OpenAI

import json
import time
import random
import copy



# Random agent, that randomly selects an action to take at each step. 
def randomAgent(api, numSteps:int = 10):
    r = random.Random()
    r.seed(0)

    # Record start time
    startTime = time.time()    

    # Run for numSteps steps in the environment
    for i in range(numSteps):
        print("\n\n")
        print("-----------------------------------------------------------")
        print("Step " + str(i) + " of " + str(numSteps))
        print("-----------------------------------------------------------")
        print("")

        # First, get the observation
        observation = api.getAgentObservation(agentIdx=0)

        # Print the observation
        print(json.dumps(observation, indent=4, sort_keys=True))

        # Take the list of accessible objects from the observation
        accessibleObjects = observation["ui"]["inventoryObjects"] + observation["ui"]["accessibleEnvironmentObjects"]

        # Get a dictionary of all possible actions
        # The keys of the dictionary represent the action name. 
        # The 'args' field of a given key represents what arguments must be populated (with objects)
        possibleActions = api.listKnownActions(limited=True)

        # Pick a random action from the list of keys
        actionName = r.choice(list(possibleActions.keys()))
        # Check what arguments are required for this action
        actionArgs = possibleActions[actionName]["args"]

        actionJSONOut = {
            "action": actionName,
            "arg1": None,
            "arg2": None
        }
        for arg in actionArgs:
            # Pick a random object from the list of accessible objects
            obj = r.choice(accessibleObjects)
            # Set the argument
            actionJSONOut[arg] = obj["uuid"]
        
        # Show the action that we've assembled
        print("Random action: " + json.dumps(actionJSONOut))

        # Perform the action
        actionSuccess = api.performAgentAction(agentIdx=0, actionJSON=actionJSONOut)
        print("actionSuccess: " + str(actionSuccess))


        # Perform the world tick
        api.tick()

    # Calculate elapsed time    
    deltaTime = time.time() - startTime
    print("Elapsed time: " + str(deltaTime) + " seconds for " + str(numSteps) + " steps.")
    print("Average time per step: " + str(deltaTime / numSteps) + " seconds.")
    print("Average steps per second: " + str(numSteps / deltaTime) + " steps per second.")


        
# promptImages should be a list of base64-encoded images
# NOTE: JSON response not available for GPT-4 Vision Preview
def OpenAIGetCompletion(client, promptStr:str, promptImages:list, model="gpt-4-vision-preview", temperature=0.0, maxTokens=300, jsonResponse:bool=False):

    # Create the message prompt, initially including only the prompt string
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", 
                 "text": promptStr
                },
            ],
        }
    ]

    # If there are images, include them.
    if (promptImages != None) and (len(promptImages) > 0):
        for image in promptImages:
            packedImage = {
                "type": "image_url",
                "image_url": {
                    "url": image,
                    #"detail": "low",
                },
            }
            messages[0]["content"].append(packedImage)


    # Print the message
    print("MESSAGE:")
    print(messages)
    print("")

    
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
    print("RESPONSE:")
    print(response)

    print("")

    print("RESPONSE CONTENT:")
    print(response.choices[0].message.content)    
    return response

# Extract the JSON from the GPT-4 response
def extractJSONfromGPT4Response(strIn):
    # Find between code brackets ```json
    startMarker = "```json"
    endMarker = "```"

    lines = strIn.split("\n")

    # Find the start and end of the JSON
    startLine = 0
    for idx, line in enumerate(lines):
        # Check if the line starts with the startMarker
        if (line.startswith(startMarker) or line.startswith(endMarker)):        # Could be either ```json or just ```
            startLine = idx + 1
            break

    # Find the end of the JSON
    endLine = 0
    for idx, line in enumerate(lines):
        # Check if the line starts with the endMarker
        if (idx > startLine):
            if (line.startswith(endMarker)):
                endLine = idx
                break

    # Extract the JSON
    jsonStr = "\n".join(lines[startLine:endLine])

    # Try to parse the JSON
    try:
        jsonOut = json.loads(jsonStr)
        return jsonOut
    except:
        print("ERROR: extractJSONfromGPT4Response: Could not parse JSON from string: " + jsonStr)
        return None
    


def GPT4BaselineOneStep(api, client, lastAction):
    # Perform the first step
    observation = api.getAgentObservation(agentIdx=0)

    # Get a copy of the observation JSON without the images in it (that we can give directly to GPT-4 in the prompt)
    # Deep copy the observation dictionary
    observationNoVision = copy.deepcopy(observation)
    # Remove the 'vision' key from the observation
    observationNoVision.pop("vision", None)
        

    # print the response (pretty)
    print(json.dumps(observationNoVision, indent=4, sort_keys=True))

    # Query OpenAI with the observation
    #promptStr = "Please describe in detail what you see in this image."
    promptStr = "You are playing a video game about making scientific discoveries.  The game is in the style of a 2D top-down RPG (you are the agent in the center of the image), and as input you get both an image, as well as information from the user interface (provided in the JSON below) that describes your location, inventory, objects in front of you, the result of your last action, and the task that you're assigned to complete.\n"
    promptStr += "Because this is a game, the actions that you can complete are limited to a set of actions that are defined by the game. Those are also described below.\n"
    promptStr += "This game is played step-by-step.  At each step, you get the input that I am providing, and output a single action to take as the next step.\n"
    promptStr += "\n"
    promptStr += "Environment Observation (as JSON):\n"
    promptStr += "```json\n"
    promptStr += json.dumps(observationNoVision, indent=1, sort_keys=True)
    promptStr += "```\n"
    promptStr += "\n"
    promptStr += "The contents of your memory, which is a scratchpad that you can use to write down information for yourself to remember in the future, is also included in the JSON above.\n"
    promptStr += "Actions:\n"
    promptStr += "```json\n"
    promptStr += json.dumps(api.listKnownActions(limited=True), indent=1, sort_keys=True)
    promptStr += "```\n"
    promptStr += "\n"
    promptStr += "Additional information on actions, and how to format your response:\n"
    promptStr += api.additionalActionDescriptionString() + "\n"
    promptStr += "\n"
    promptStr == "Your last action, explanation for that action, and messages you've left in your scratchpad:\n"
    promptStr += "```json\n"
    promptStr += json.dumps(lastAction, indent=1, sort_keys=True)
    promptStr += "```\n"
    promptStr += "\n"
    promptStr += "Please create your output (the next action you'd like to take) below.  It should be in the JSON form expected above e.g.(`{\"action\": \"USE\", \"arg1\": 5, \"arg2\": 12}`). \n"
    promptStr += "Your response should ONLY be in JSON.  You should include an additional JSON key, \"explanation\", to describe your reasoning for performing this action. e.g. `{\"action\": \"USE\", \"arg1\": 5, \"arg2\": 12, \"explanation\": \"Using the shovel on the soil will allow me to dig a hole to plant a seed\"}`.  Note that even though this explanation is short, yours can be a few hundred tokens, if you'd like.\n"
    promptStr += "Lastly, your response should also include an additional JSON key, \"memory\", that includes any information you'd like to write down and pass on to yourself for the future.  This can be helpful in remembering important results, high-level tasks, low-level subtasks, or anything else you'd like to remember or think would be helpful. e.g. `{\"action\": \"USE\", \"arg1\": 5, \"arg2\": 12, \"explanation\": \"...\", \"memory\": \"...\"}`\n"
    

    imageWithGrid = observation["vision"]["base64_with_grid"]
    promptImages = [imageWithGrid]

    response = OpenAIGetCompletion(client, promptStr=promptStr, promptImages=promptImages, model="gpt-4-vision-preview", temperature=0.0, maxTokens=300)
    print(response)

    # Extract the JSON from the response
    responseStr = response.choices[0].message.content
    responseJSON = extractJSONfromGPT4Response(responseStr)

    # Check if the response is valid
    nextAction = {}
    if (responseJSON == None):
        nextAction = {
            "action": "ERROR: Could not parse the last action that was generated.  Please be careful in generating valid JSON.",
            "explanation": "",
            "memory": lastAction["memory"]
        }
    else:
        nextAction.update(responseJSON)
        # Try to run the action in the environment
        actionSuccess = api.performAgentAction(agentIdx=0, actionJSON=nextAction)
        print("ACTION SUCCESS: ")
        print(actionSuccess)


    # Perform world tick
    api.tick()
    
    # Return the action that it chose (to pass into the next step)
    return nextAction



        



# For testing the API 
def GPT4VBaselineAgent(api, numSteps:int = 10):
    # Get the OpenAI key (stored in a file called "openai_key.txt")
    key = ""
    with open("openai_key.txt", "r") as file:
        key = file.read().strip()

    # Create the OpenAI client
    client = OpenAI(api_key=key)

    # Initial Memory    
    lastAction = {
        "action": "This is the first action",
        "explanation": "This is the first explanation",
        "memory": "This is the first memory",
    }

    # Keep a history of the last actions
    lastActionHistory = []
    lastActionHistory.append(lastAction)

    # Record start time
    startTime = time.time()

    # Run for numSteps steps in the environment
    for i in range(0, numSteps):
        # Run one step
        print("\n\n")
        print("-----------------------------------------------------------")
        print("Step " + str(i) + " of " + str(numSteps))
        print("-----------------------------------------------------------")
        print("")
        lastAction = GPT4BaselineOneStep(api, client, lastAction)
        print("LAST ACTION: ")
        print(lastAction)
        print("")
        lastActionHistory.append(lastAction)


    # Last action history
    print("LAST ACTION HISTORY:")
    for idx, action in enumerate(lastActionHistory):
        print("Step " + str(idx) + ":\n")
        print(json.dumps(action, indent=4, sort_keys=True))
        print("")
              


    # Calculate elapsed time
    deltaTime = time.time() - startTime
    print("Elapsed time: " + str(deltaTime) + " seconds for " + str(numSteps) + " steps.")
    print("Average time per step: " + str(deltaTime / numSteps) + " seconds.")
    print("Average steps per second: " + str(numSteps / deltaTime) + " steps per second.")





# For testing the API 
def testAgent(api):
    # Perform the first step
    response = api.getAgentObservation(agentIdx=0)

    # print the response (pretty)
    print(json.dumps(response, indent=4, sort_keys=True))


    # Try an action
    actionJSON = {
        "action": "MOVE_FORWARD",
        "arg1": "agent",
        "arg2": "north"
    }

    print("")
    print("Known actions: " + str(api.listKnownActions()))
    print("")
    print("Additional action information: " + api.additionalActionDescriptionString())
    print("")
    print("Attempting action: " + json.dumps(actionJSON))
    print("")
    actionSuccess = api.performAgentAction(agentIdx=0, actionJSON=actionJSON)

    # Take another observation, and print it
    print("\n")
    response = api.getAgentObservation(agentIdx=0)
    print(json.dumps(response, indent=4, sort_keys=True))




if __name__ == "__main__":
    print("Initializing DiscoveryWorld API... ")
    
    # Create the API
    api = DiscoveryWorldAPI()
    print(api.getNameAndVersion())

    # Load the scenario
    api.loadScenario(scenarioName="", numUserAgents=1, randomSeed=0)


    # Test the API
    #testAgent(api)

    # GPT4-V Baseline Agent
    GPT4VBaselineAgent(api)
    api.createAgentVideo(agentIdx=0, filenameOut="output_randomAgent.mp4")

    # Random agent
    #randomAgent(api, numSteps=100)
    # Create a video from the random agent
    #api.createAgentVideo(agentIdx=0, filenameOut="output_randomAgent.mp4")
    


    



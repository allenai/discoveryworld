# DiscoveryWorldAPIUsageExample.py


from DiscoveryWorldAPI import DiscoveryWorldAPI

from openai import OpenAI

import json
import time
import random



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
def OpenAIGetCompletion(client, promptStr:str, promptImages:list, model="gpt-4-vision-preview", temperature=0.0, maxTokens=300):

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


    # Get the response
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=maxTokens,
        temperature=temperature,
    )


    # Return the response
    print("RESPONSE:")
    print(response)

    print("")

    print("RESPONSE CONTENT:")
    print(response.choices[0].message.content)    
    return response



# For testing the API 
def GPT4VBaselineAgent(api):
    # Get the OpenAI key (stored in a file called "openai_key.txt")
    key = ""
    with open("openai_key.txt", "r") as file:
        key = file.read().strip()

    # Create the OpenAI client
    client = OpenAI(api_key=key)



    # Perform the first step
    response = api.getAgentObservation(agentIdx=0)

    # print the response (pretty)
    print(json.dumps(response, indent=4, sort_keys=True))


    # Query OpenAI with the observation
    promptStr = "Please describe in detail what you see in this image."
    imageWithGrid = response["vision"]["base64_with_grid"]
    promptImages = [imageWithGrid]

    response = OpenAIGetCompletion(client, promptStr=promptStr, promptImages=promptImages, model="gpt-4-vision-preview", temperature=0.0, maxTokens=300)
    print(response)



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

    # Random agent
    #randomAgent(api, numSteps=250)
    # Create a video from the random agent
    #api.createAgentVideo(agentIdx=0, filenameOut="output_randomAgent.mp4")


    



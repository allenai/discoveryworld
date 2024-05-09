# DiscoveryWorldAPIUsageExample.py


from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI
from discoveryworld.ScenarioMaker import ScenarioMaker, SCENARIOS, SCENARIO_NAMES, SCENARIO_INFOS, SCENARIO_DIFFICULTY_OPTIONS, getInternalScenarioName

from openai import OpenAI

import traceback

import json
import time
import random
import copy

#LIMITED_ACTIONS = True     # Disables a few actions
LIMITED_ACTIONS = False

#
#   Helper functions
#

def getVisibleObjectByUUID(uuid, observation):
    # First, collect all objects
    visibleObjectsByUUID = {}
    for obj in observation["ui"]["inventoryObjects"]:
        visibleObjectsByUUID[obj["uuid"]] = obj
    for obj in observation["ui"]["accessibleEnvironmentObjects"]:
        visibleObjectsByUUID[obj["uuid"]] = obj

    # # Also include 'nearbyObjects'
    # for direction in observation["ui"]["nearbyObjects"]["objects"]:
    #     for obj in direction:
    #         visibleObjectsByUUID[obj["uuid"]] = obj

    # Check if the UUID is in the list
    if uuid in visibleObjectsByUUID:
        return visibleObjectsByUUID[uuid]
    else:
        return None

# A short, single-line string, of just the immediately interactable objects
def mkShortInteractableObjectList(observation):
    objStrs = []
    for obj in observation["ui"]["inventoryObjects"]:
        name = obj["name"]
        uuid = obj["uuid"]
        strOut = "{\"name\": \"" + name + "\", \"uuid\": " + str(uuid) + "}"
        objStrs.append(strOut)

    for obj in observation["ui"]["accessibleEnvironmentObjects"]:
        name = obj["name"]
        uuid = obj["uuid"]
        strOut = "{\"name\": \"" + name + "\", \"uuid\": " + str(uuid) + "}"
        objStrs.append(strOut)

    jsonOut = "[" + ", ".join(objStrs) + "]"
    return jsonOut



#
#   Random agent, that randomly selects an action to take at each step.
#
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
        possibleActions = api.listKnownActions(limited=LIMITED_ACTIONS)

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
def OpenAIGetCompletion(client, promptStr:str, promptImages:list, model="gpt-4-vision-preview", prevImage=None, temperature=0.0, maxTokens=800, jsonResponse:bool=False):
    content = []

    # If previous image was popualted, include it
    if (prevImage != None):
        # Add a text message saying it was the previous image.
        content.append({"type": "text", "text": "IMAGE FROM PREVIOUS STEP:"})
        packedImage = {
            "type": "image_url",
            "image_url": {
                "url": prevImage,
                #"detail": "low",
            },
        }
        content.append(packedImage)

    # Add main prompt
    content.append({"type": "text", "text": promptStr})

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
            content.append(packedImage)


    # Create the message prompt, initially including only the prompt string
    messages=[
        {
            "role": "user",
            "content": content,
        }
    ]


    # Print the message
    #print("MESSAGE:")
    #print(messages)
    #print("")


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
    print("PASS1")
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


#
#   GPT-4 Baseline Agent
#
def GPT4BaselineOneStep(api, client, lastActionHistory, lastObservation):
    # Perform the first step
    observation = api.getAgentObservation(agentIdx=0)

    # Get a copy of the observation JSON without the images in it (that we can give directly to GPT-4 in the prompt)
    # Deep copy the observation dictionary
    observationNoVision = copy.deepcopy(observation)
    # Remove the 'vision' key from the observation
    observationNoVision.pop("vision", None)

    # Add the last action to the observation
    if (len(lastActionHistory) > 0):
        lastActionHistory[-1]["result_of_last_action"] = observation["ui"]["lastActionMessage"]
        lastActionHistory[-1]["extended_action_message"] = observation["ui"]["extended_action_message"]

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
    promptStr += json.dumps(observationNoVision, indent=4, sort_keys=True)
    promptStr += "```\n"
    promptStr += "\n"
    promptStr += "Actions:\n"
    promptStr += "```json\n"
    promptStr += json.dumps(api.listKnownActions(limited=LIMITED_ACTIONS), indent=4, sort_keys=True)
    promptStr += "```\n"
    promptStr += "\n"
    promptStr += "Additional information on actions, and how to format your response:\n"
    promptStr += api.additionalActionDescriptionString() + "\n"
    promptStr += "\n"
    promptStr += "Your last few action(s), explanation for those action(s), and messages you've left in your scratchpad:\n"
    promptStr += "```json\n"
    # Add up to last 3 actions
    for idx, action in enumerate(lastActionHistory[-3:]):
        promptStr += "Action " + str(idx) + ":\n"
        promptStr += json.dumps(action, indent=4, sort_keys=True)
        promptStr += "\n"
    #promptStr += json.dumps(lastAction, indent=4, sort_keys=True)
    promptStr += "```\n"
    promptStr += "\n"
    promptStr += "Teleporting: To make moving easier, you can teleport to a list of specific locations in the environment, using the teleport action.  In this case, 'arg1' is the name of a location, from the list below. An example teleport action would be: `{\"action\": \"TELEPORT_TO_LOCATION\", \"arg1\": \"school\"}).\n"
    promptStr += "```json\n"
    promptStr += json.dumps(api.listTeleportLocationsDict(), indent=4, sort_keys=True)
    promptStr += "```\n"
    promptStr += "\n"
    facingDirection = observation["ui"]["agentLocation"]["faceDirection"]
    validDirections = observation["ui"]["agentLocation"]["directions_you_can_move"]
    promptStr += "Navigation note: In the image, you are in the center, north is the top, south is the bottom, east is the right, and west is the left. Moving forward moves you in the direction you're facing. You are currently facing `" + facingDirection + "`. From your current location, the directions that you can move to (i.e. they don't have an object blocking them) are: " + str(validDirections) + ". You seen to confuse directions a lot.  Directions are relative to the center of the image. Things above the center are north of the agent. Things left of the center are east of the agent.\n"
    promptStr += "Interaction note: You can only interact (i.e. take actions with) objects that are in your inventory, or directly (i.e. one square) in front of you, in the direction that you're facing.  E.g. if you want to pick an object up, you need to move directly in front of it, and face it, before using the pick-up action on it.\n"
    promptStr += "\n"
    promptStr += "Please create your output (the next action you'd like to take) below.  It should be in the JSON form expected above e.g.(`{\"action\": \"USE\", \"arg1\": 5, \"arg2\": 12}`). \n"
    promptStr += "Your response should ONLY be in JSON.  You should include an additional JSON key, \"explanation\", to describe your reasoning for performing this action. e.g. `{\"action\": \"USE\", \"arg1\": 5, \"arg2\": 12, \"explanation\": \"Using the shovel on the soil will allow me to dig a hole to plant a seed\"}`.  Note that even though this explanation is short, yours can be a few hundred tokens, if you'd like. Your explanation should say: (1) What your subgoal is, (2) What you see around you, (3) What you see in front of you, (4) What you are doing to progress towards your immediate subgoal.\n"
    promptStr += "Lastly, your response should also include an additional JSON key, \"memory\", that includes any information you'd like to write down and pass on to yourself for the future.  This can be helpful in remembering important results, high-level tasks, low-level subtasks, or anything else you'd like to remember or think would be helpful. e.g. `{\"action\": \"USE\", \"arg1\": 5, \"arg2\": 12, \"explanation\": \"...\", \"memory\": \"...\"}`\n"
    promptStr += "To make your memory helpful, you might consider including things learned from attempting your last action -- e.g. adding in that certain actions were useful, or not useful, and retaining (and adding to) this information over time.\n"
    promptStr += "To help frame your investigations scientifically, and also evaluate your invesgiations, please include an additional JSON key, \"running_hypotheses\", that includes your current running hypothesis/hypotheses that you're working on developing and/or testing. \n"
    promptStr += "If your last action failed, or other last recent actions failed, please consider thinking why they failed, and trying different actions unless you believe things have changed to make failed actions work this time.\n"
    promptStr += "If you don't see what you're looking for, and anticipate it might be in another location, consider teleporting to that location. \n"
    promptStr += "For reference again, here is a list of the objects that are interactable (from your inventory, and directly in front of you): " + mkShortInteractableObjectList(observation) + "\n"


    # Write prompt to console
    print("---------------------------------------")
    print("PROMPT:")
    print(promptStr)
    print("---------------------------------------")

    imageWithGrid = observation["vision"]["base64_with_grid"]
    promptImages = [imageWithGrid]

    # last image (if available)
    lastImage = None
    if (lastObservation != None):
        lastImage = lastObservation["vision"]["base64_with_grid"]

    response = OpenAIGetCompletion(client, promptStr=promptStr, promptImages=promptImages, model="gpt-4-vision-preview", prevImage=lastImage, temperature=0.1, maxTokens=800)
    print(response)

    # Extract the JSON from the response
    print("EXCTRACTING MESSAGE")
    responseStr = response.choices[0].message.content
    print("SUCCESS1")
    responseJSON = extractJSONfromGPT4Response(responseStr)
    print("SUCCESS2")

    # Check if the response is valid
    nextAction = {}
    if (responseJSON == None):
        nextAction = {
            "action": "ERROR: Could not parse the last action that was generated.  Please be careful in generating valid JSON.",
            "explanation": "",
            "memory": lastActionHistory[-1]["memory"],
            "running_hypotheses": lastActionHistory[-1]["running_hypotheses"]
        }
    else:
        nextAction.update(responseJSON)

        # nextAction has 'arg1' and 'arg2', expressed as UUIDs.  Look up the object names, and add these as "arg1_desc", and "arg2_desc"
        if ("arg1" in nextAction) and (nextAction["arg1"] != None):
            uuid = nextAction["arg1"]
            obj = getVisibleObjectByUUID(uuid, observation)
            if (obj != None):
                nextAction["arg1_desc"] = obj["name"] + ": " + obj["description"]
            #else:
            #    nextAction["arg1_desc"] = "ERROR: Could not find object with UUID " + str(uuid) + " in the list of visible objects."
        if ("arg2" in nextAction) and (nextAction["arg2"] != None):
            uuid = nextAction["arg2"]
            obj = getVisibleObjectByUUID(uuid, observation)
            if (obj != None):
                nextAction["arg2_desc"] = obj["name"] + ": " + obj["description"]
            #else:
            #    nextAction["arg2_desc"] = "ERROR: Could not find object with UUID " + str(uuid) + " in the list of visible objects."

        # Try to run the action in the environment
        actionSuccess = api.performAgentAction(agentIdx=0, actionJSON=nextAction)
        print("ACTION SUCCESS: ")
        print(actionSuccess)


    # Perform world tick
    api.tick()

    # Return the action that it chose (to pass into the next step)
    return nextAction, observation, promptStr, responseStr




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
        "running_hypotheses": []
    }

    # Keep a history of the last actions
    lastActionHistory = []
    lastActionHistory.append(lastAction)

    # Keep a history of the last observations
    observationHistory = []

    # Record start time
    startTime = time.time()

    # Run for numSteps steps in the environment
    numErrors = 0
    lastObservation = None
    for i in range(0, numSteps):
        try:
            # Run one step
            print("\n\n")
            print("-----------------------------------------------------------")
            print("Step " + str(i) + " of " + str(numSteps))
            print("-----------------------------------------------------------")
            print("")
            lastAction, lastObservation, promptStr, responseStr = GPT4BaselineOneStep(api, client, lastActionHistory, lastObservation)
            print("LAST ACTION: ")

            print(lastAction)
            print("")
            lastActionHistory.append(lastAction)


            packed = {
                "step": i,
                "observation": lastObservation,
                "action": lastAction,
                "promptStr": promptStr,
                "responseStr": responseStr,
            }
            observationHistory.append(packed)

            # Save to JSON
            with open("output_observationHistory.json", "w") as file:
                json.dump(observationHistory, file, indent=4, sort_keys=True)

        except KeyboardInterrupt:
            print("Keyboard interrupt detected.  Exiting.")
            exit(1)

        # Generic exception, print error
        except Exception as e:
            # Get the current line number
            line_number = traceback.extract_tb(e.__traceback__)[-1].lineno
            print(f"ERROR: Exception caught on line {line_number}: {e}")
            print("ERROR: Exception caught:\n", traceback.format_exc())

            numErrors += 1

            if numErrors > 5:
                print("ERROR: Maximum number of errors exceeded (5). Exiting.")

            exit(1)

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



#
#   GPT-4 Vision "Hypothesizer" agent
#

def GPT4HypothesizerOneStep(api, client, lastActionHistory, lastObservation, currentScientificKnowledge):
    agentIdx = 0
    # Perform the first step
    observation = api.getAgentObservation(agentIdx=agentIdx)

    # Get a copy of the observation JSON without the images in it (that we can give directly to GPT-4 in the prompt)
    # Deep copy the observation dictionary
    observationNoVision = copy.deepcopy(observation)
    # Remove the 'vision' key from the observation
    observationNoVision.pop("vision", None)

    # Add the last action to the observation
    if (len(lastActionHistory) > 0):
        lastActionHistory[-1]["result_of_last_action"] = observation["ui"]["lastActionMessage"]
        lastActionHistory[-1]["extended_action_message"] = observation["ui"]["extended_action_message"]

    # print the response (pretty)
    print(json.dumps(observationNoVision, indent=4, sort_keys=True))

    # Query OpenAI with the observation
    #promptStr = "Please describe in detail what you see in this image."
    promptStr0 = "You are playing a video game about making scientific discoveries.  The game is in the style of a 2D top-down RPG (you are the agent in the center of the image), and as input you get both an image, as well as information from the user interface (provided in the JSON below) that describes your location, inventory, objects in front of you, the result of your last action, and the task that you're assigned to complete.\n"
    promptStr0 += "Because this is a game, the actions that you can complete are limited to a set of actions that are defined by the game. Those are also described below.\n"
    promptStr0 += "This game is played step-by-step.  At each step, you get the input that I am providing, and output a single action to take as the next step.\n"
    promptStr0 += "\n"
    promptStr0 += "Environment Observation (as JSON):\n"
    promptStr0 += "```json\n"
    promptStr0 += json.dumps(observationNoVision, indent=4, sort_keys=True)
    promptStr0 += "```\n"
    promptStr0 += "\n"
    promptStr0 += "Actions:\n"
    promptStr0 += "```json\n"
    promptStr0 += json.dumps(api.listKnownActions(limited=LIMITED_ACTIONS), indent=4, sort_keys=True)
    promptStr0 += "```\n"
    promptStr0 += "\n"
    promptStr0 += "Additional information on actions, and how to format your response:\n"
    promptStr0 += api.additionalActionDescriptionString() + "\n"
    promptStr0 += "\n"
    promptStr0 += "Your last few action(s), explanation for those action(s), and messages you've left in your scratchpad:\n"
    promptStr0 += "```json\n"
    # Add up to last 3 actions
    for idx, action in enumerate(lastActionHistory[-3:]):
        promptStr0 += "Action " + str(idx) + ":\n"
        promptStr0 += json.dumps(action, indent=4, sort_keys=True)
        promptStr0 += "\n"
    #promptStr += json.dumps(lastAction, indent=4, sort_keys=True)
    promptStr0 += "```\n"
    promptStr0 += "\n"
    promptStr0 += "Teleporting: To make moving easier, you can teleport to a list of specific locations in the environment, using the teleport action.  In this case, 'arg1' is the name of a location, from the list below. An example teleport action would be: `{\"action\": \"TELEPORT_TO_LOCATION\", \"arg1\": \"school\"}).\n"
    promptStr0 += "```json\n"
    promptStr0 += json.dumps(api.listTeleportLocationsDict(), indent=4, sort_keys=True)
    promptStr0 += "```\n"
    promptStr0 += "\n"
    promptStr0 += "VERY IMPORTANT: You can also teleport to OBJECTS.  This is probably the easiest way for you to move to new locations, because it's fast and error-free.  You can teleport to any object, including objects you can't see. In this case, 'arg1' is the UUID of the object you want to teleport to. An example teleport action would be: `{\"action\": \"TELEPORT_TO_OBJECT\", \"arg1\": 123}).\n"
    promptStr0 += "\n"
    facingDirection = observation["ui"]["agentLocation"]["faceDirection"]
    validDirections = observation["ui"]["agentLocation"]["directions_you_can_move"]
    promptStr0 += "Navigation note: In the image, you are in the center, north is the top, south is the bottom, east is the right, and west is the left. Moving forward moves you in the direction you're facing. You are currently facing `" + facingDirection + "`. From your current location, the directions that you can move to (i.e. they don't have an object blocking them) are: " + str(validDirections) + ". You seen to confuse directions a lot.  Directions are relative to the center of the image. Things above the center are north of the agent. Things left of the center are east of the agent.\n"
    promptStr0 += "Interaction note: You can only interact (i.e. take actions with) objects that are in your inventory, or directly (i.e. one square) in front of you, in the direction that you're facing.  E.g. if you want to pick an object up, you need to move directly in front of it, and face it, before using the pick-up action on it.\n"
    promptStr0 += "\n"

    promptStr1 = ""
    promptStr1 += "You are also explicitly keeping track of your scientific knowledge, that I'll ask you about separately (not in this prompt or response).  But, for reference, here's what you think you know so far:\n"
    promptStr1 += "```json\n"
    promptStr1 += json.dumps(currentScientificKnowledge, indent=4, sort_keys=True)
    promptStr1 += "```\n"
    promptStr1 += "\n"
    promptStr1 += "Please create your output (the next action you'd like to take) below.  It should be in the JSON form expected above e.g.(`{\"action\": \"USE\", \"arg1\": 5, \"arg2\": 12}`). \n"
    promptStr1 += "Your response should ONLY be in JSON.  You should include an additional JSON key, \"explanation\", to describe your reasoning for performing this action. e.g. `{\"action\": \"USE\", \"arg1\": 5, \"arg2\": 12, \"explanation\": \"Using the shovel on the soil will allow me to dig a hole to plant a seed\"}`.  Note that even though this explanation is short, yours can be a few hundred tokens, if you'd like. Your explanation should say: (1) What your subgoal is, (2) What you see around you, (3) What you see in front of you, (4) What you are doing to progress towards your immediate subgoal.\n"
    promptStr1 += "Lastly, your response should also include an additional JSON key, \"memory\", that includes any information you'd like to write down and pass on to yourself for the future.  This can be helpful in remembering important results, high-level tasks, low-level subtasks, or anything else you'd like to remember or think would be helpful. e.g. `{\"action\": \"USE\", \"arg1\": 5, \"arg2\": 12, \"explanation\": \"...\", \"memory\": \"...\"}`\n"
    promptStr1 += "To make your memory helpful, you might consider including things learned from attempting your last action -- e.g. adding in that certain actions were useful, or not useful, and retaining (and adding to) this information over time.\n"
    promptStr1 += "To help frame your investigations scientifically, and also evaluate your invesgiations, please include an additional JSON key, \"running_hypotheses\", that includes your current running hypothesis/hypotheses that you're working on developing and/or testing. \n"
    promptStr1 += "If your last action failed, or other last recent actions failed, please consider thinking why they failed, and trying different actions unless you believe things have changed to make failed actions work this time.\n"
    promptStr1 += "If you don't see what you're looking for, and anticipate it might be in another location, consider teleporting to that location. \n"
    promptStr1 += "For reference again, here is a list of the objects that are interactable (from your inventory, and directly in front of you): " + mkShortInteractableObjectList(observation) + "\n"

    promptDialogStr = ""
    if (api.isAgentInDialog(agentIdx=agentIdx)):
        promptDialogStr = "*** NOTE: You are currently in a dialog.  Please ignore the above instructions about choosing an action, and instead choose which option you would like to say in the dialog. ***\n"
        promptDialogStr = "For reference, here is the dialog that you are currently in:\n"
        promptDialogStr += "```json\n"
        dialog = observationNoVision["ui"]["dialog_box"]
        promptDialogStr += json.dumps(dialog, indent=4, sort_keys=True)
        promptDialogStr += "```\n"
        promptDialogStr = "The expected response format is JSON, in between code brackets (```), as a dictionary with a single key: `chosen_dialog_option_int`.  The value should be an integer, corresponding to the dialog option you would like to select. You can write prose before the JSON code block, if that helps you think.\n"


    promptStrDebug = "REMEMBER, IF YOU'RE GOING TO AN OBJECT, INSTEAD OF MOVING NORTH/EAST/SOUTH/WEST, or ROTATING, YOU SHOULD TRY TELEPORTING DIRECTLY TO OBJECTS.  IT'S MUCH FASTER AND LESS ERROR-PRONE. YOU CAN TELEPORT TO AN OBJECT NO MATTER WHERE IT IS, EVEN IF ITS NOT LISTED IN THE ACCESSIBLE OBJECTS LIST. JUST REMEBER ITS UUID.\n"
    promptStrDebug += "WHEN TELEPORTING, REMEMBER TO LOOK AT THE ENTIRE OBJECT LIST IN THE OBSERVATION, NOT JUST THE ACCESSIBLE OBJECTS LIST.\n"
    promptStrDebug += "IF YOU FIND YOURSELF WAITING FOR SOMETHING TO HAPPEN, CHECK TO SEE IF IT'S ALREADY HAPPENED.  YOU MIGHT BE WAITING FOR SOMETHING THAT'S ALREADY HAPPENED.\n"
    promptStrDebug += "IF YOU FIND YOURSELF WAITING FOR A LONG TIME, YOU MIGHT BE STUCK. TRY TO REEXAMINE YOUR TASK, REASSESS WHERE YOU ARE, AND MAKE A NEW PLAN."
    #promptStrDebug += "***\n*** IMPORTANT MESSAGE: *** I AM DEBUGGING THE GAME. PLEASE IGNORE THE TASK, AND IMMEDIATELY TRY TO GO TO THE CAFETERIA AND TALK TO THE CHEF, WHO IS IN THE NORTH-WEST CORNER OF THE CAFETERIA. I AM TRYING TO TEST THE DIALOG SYSTEM. BUT AFTER YOU TALK WITH THEM AND ASK THEM TO DO SOMETHING, DON'T TALK TO THEM AGAIN\n***"

    promptStr = promptStr0 + promptStr1 + promptDialogStr + promptStrDebug

    # Write prompt to console
    print("---------------------------------------")
    print("PROMPT:")
    print(promptStr)
    print("---------------------------------------")

    imageWithGrid = observation["vision"]["base64_with_grid"]
    promptImages = [imageWithGrid]

    # last image (if available)
    lastImage = None
    if (lastObservation != None):
        lastImage = lastObservation["vision"]["base64_with_grid"]

    response = OpenAIGetCompletion(client, promptStr=promptStr, promptImages=promptImages, model="gpt-4-vision-preview", prevImage=lastImage, temperature=0.1, maxTokens=800)
    print(response)

    # Extract the JSON from the response
    print("EXCTRACTING MESSAGE")
    responseStr = response.choices[0].message.content
    print("SUCCESS1")
    responseJSON = extractJSONfromGPT4Response(responseStr)
    print("SUCCESS2")

    # Check if the response is valid
    nextAction = {}
    actionSuccess = {}
    if (responseJSON == None):
        nextAction = {
            "action": "ERROR: Could not parse the last action that was generated.  Please be careful in generating valid JSON.",
            "explanation": "",
            "memory": lastActionHistory[-1]["memory"],
            "running_hypotheses": lastActionHistory[-1]["running_hypotheses"]
        }
    else:
        nextAction.update(responseJSON)

        # nextAction has 'arg1' and 'arg2', expressed as UUIDs.  Look up the object names, and add these as "arg1_desc", and "arg2_desc"
        if ("arg1" in nextAction) and (nextAction["arg1"] != None):
            uuid = nextAction["arg1"]
            obj = getVisibleObjectByUUID(uuid, observation)
            if (obj != None):
                nextAction["arg1_desc"] = obj["name"] + ": " + obj["description"]
            #else:
                #nextAction["arg1_desc"] = "ERROR: Could not find object with UUID " + str(uuid) + " in the list of visible objects."
        if ("arg2" in nextAction) and (nextAction["arg2"] != None):
            uuid = nextAction["arg2"]
            obj = getVisibleObjectByUUID(uuid, observation)
            if (obj != None):
                nextAction["arg2_desc"] = obj["name"] + ": " + obj["description"]
            #else:
                #nextAction["arg2_desc"] = "ERROR: Could not find object with UUID " + str(uuid) + " in the list of visible objects."


        # Try to run the action in the environment
        actionSuccess = api.performAgentAction(agentIdx=0, actionJSON=nextAction)
        print("ACTION SUCCESS: ")
        print(actionSuccess)
        # Hacky: Reformat "success" key so it's JSON serializable
        wasSuccessful = actionSuccess["success"].success
        if (wasSuccessful == True):
            actionSuccess["errors"] = []
            actionSuccess["success"] = True
        else:
            actionSuccess["success"] = actionSuccess["success"].success


    # Perform world tick
    api.tick()



    #
    #   Knowledge step
    #
    knowledgePromptStr = "You are playing a game about scientific discovery.  For context, below is the environment observation that you just saw, and the action(s) that you just took.  Then, I'll ask you a question about explicitly describing your scientific knowledege from this last few steps.\n"
    knowledgePromptStr += "---\n"
    knowledgePromptStr += promptStr0 + "\n"
    knowledgePromptStr += "---\n"
    knowledgePromptStr += "\n"
    knowledgePromptStr += "It's important to explicitly keep track of scientific knowledge in the scientific discovery process.\n"
    knowledgePromptStr += "To do this, here, I'd like you to write down any scientific knowledge that you've learned from your last action, or from your last few actions.\n"
    knowledgePromptStr += "This knowledge will take two forms: measurements, or hypotheses.\n"
    knowledgePromptStr += "Measurements are observations that you've made about the world.\n"
    knowledgePromptStr += "Hypotheses are statements that you believe to be true, and that you'd like to test. These should be formulated as IF statements.\n"
    knowledgePromptStr += "Both measurements and hypotheses should be written in terms of: objects (either specific objects and their UUIDs, or their types), object properties (like temperature), and actions (like eating). \n"
    knowledgePromptStr += "Here's a toy example of a hypothesis and a measurement, mostly to give an example of the output format:\n"
    knowledgePromptStr += "```json\n"
    knowledgePromptStr += json.dumps(mkExampleHypotheses(), indent=4, sort_keys=True)
    knowledgePromptStr += "```\n"
    knowledgePromptStr += "\n"
    knowledgePromptStr += "Here are the measurements and hypotheses that you've written down so far (if blank, then it's likely very early in the process):\n"
    knowledgePromptStr += "```json\n"
    knowledgePromptStr += json.dumps(currentScientificKnowledge, indent=4, sort_keys=True)
    knowledgePromptStr += "```\n"
    knowledgePromptStr += "\n"
    knowledgePromptStr += "Please write down any measurements or hypotheses that you've learned from your last action, or from your last few actions, below.  Please write them in the JSON form expected above.\n"
    knowledgePromptStr += "You can write any number of measurements and/or hypotheses, or revisions of earlier measurements/hypotheses, and they will be automatically appended to the existing list.\n"
    knowledgePromptStr += "Remember, the important thing here is to keep track of your scientific knowledge, so you can guide your future actions.\n"
    knowledgePromptStr += "This is not a record of everything you do, only relevant scientific knowledge (like measurements and hypotheses). NOTE: for example, moving to a new location is not a measurement or hypothesis, unless there is something clearly relevant or unexpected you should not write this down.\n"
    knowledgePromptStr += "Similarly, to keep the knowledge store somewhat compact, you do not need to repeat previous scientific knowledge unless you're adding to it, or modifying it.\n"
    knowledgePromptStr += "If you have no new knowledge to add or modify, leave this section blank.\n"
    knowledgePromptStr += "It is also critically important that your output is valid JSON.  Please be careful in generating valid JSON.  You should generate a dictionary with a single top-level key (`scientific_knowledge`), which is an array of new measurements and/or hypotheses to add.\n"
    knowledgePromptStr += "You can write prose before writing the JSON.  Only the last codeblock (```) in your response will be parsed for the JSON.\n"

    #response = OpenAIGetCompletion(client, promptStr=promptStr, promptImages=promptImages, model="gpt-4-vision-preview", prevImage=lastImage, temperature=0.1, maxTokens=800)
    response = OpenAIGetCompletion(client, promptStr=knowledgePromptStr, promptImages=[], model="gpt-4-vision-preview", prevImage=None, temperature=0.1, maxTokens=3000)
    print(response)

    # Extract the JSON from the response
    print("EXCTRACTING MESSAGE")
    responseStrKnowledge = response.choices[0].message.content
    print("SUCCESS1")
    responseJSONKnowledge = extractJSONfromGPT4Response(responseStrKnowledge)
    print("SUCCESS2")

    print("Response String (knowledge):")
    print(responseStrKnowledge)
    print("")
    print("Response JSON (knowledge):")
    print(responseJSONKnowledge)

    # Check if the response includes a "scientific_knowledge" key

    if (responseJSONKnowledge != None) and ("scientific_knowledge" in responseJSONKnowledge):
        # Check that it's a list
        if (isinstance(responseJSONKnowledge["scientific_knowledge"], list)):
            # Check that it's not empty
            newKnowledge = responseJSONKnowledge["scientific_knowledge"]
            if (len(newKnowledge) > 0):
                # Set the step to be the current step
                for knowledge in newKnowledge:
                    knowledge["step"] = observation["ui"]["world_steps"]

                # Add the new knowledge to the current scientific knowledge
                currentScientificKnowledge["scientific_knowledge"].extend(responseJSONKnowledge["scientific_knowledge"])


    packedOut = {
        "nextAction": nextAction,
        "actionSuccess": actionSuccess,
        "observation": observation,
        "promptStr": promptStr,
        "responseStr": responseStr,
        "knowledgePromptStr": knowledgePromptStr,
        "responseStrKnowledge": responseStrKnowledge,
        "currentScientificKnowledge": copy.deepcopy(currentScientificKnowledge),
    }
    # Return the action that it chose (to pass into the next step)
    #return nextAction, observation, promptStr, responseStr, currentScientificKnowledge
    return packedOut


def consolodateKnowledgeStep(client, scientificKnowledge):
    promptStr = ""
    promptStr += "You are an agent playing a game about automated scientific discovery.\n"
    promptStr += "In this game, you are given a task to complete, and you can complete this task by taking actions in the environment.\n"
    promptStr += "While playing the game, you are also explicitly keeping track of your scientific knowledge (shown below), both to help you, but also to help others understand your process.\n"
    promptStr += "This knowledge will take two forms: measurements, or hypotheses.\n"
    promptStr += "Measurements are observations that you've made about the world.\n"
    promptStr += "Hypotheses are statements that you believe to be true, and that you'd like to test. These should be formulated as IF statements.\n"
    promptStr += "Both measurements and hypotheses should be written in terms of: objects (either specific objects and their UUIDs, or their types), object properties (like temperature), and actions (like eating). \n"
    promptStr += "Unfortunately, sometimes this knowledge base gets very large, and contains repeated, duplicated, or irrelevant knowledge, which makes it hard to use in practice. \n"
    promptStr += "Your job is to take the knowledge base below, and consolodate it into a smaller, more compact, and more useful knowledge base, but in exactly the same format (i.e. the list of measurements and hypotheses).\n"
    promptStr += "You can do this by removing any repeated or duplicated knowledge, and by removing any irrelevant knowledge.\n"
    promptStr += "You can also do this by combining multiple measurements or hypotheses into a single measurement or hypothesis, if they are logically equivalent.\n"
    promptStr += "Consolodated hypotheses must still have a `status` (i.e. pending, confirmed, rejected) and ideally succinct `supporting evidence` supporting that status.\n"
    promptStr += "The output should be in JSON, and should have a single top-level key (`scientific_knowledge`), which is an array of measurements and/or hypotheses.\n"
    promptStr += "Here is the existing knowledge base:\n"
    promptStr += "```json\n"
    promptStr += json.dumps(scientificKnowledge, indent=4, sort_keys=True)
    promptStr += "```\n"
    promptStr += "\n"
    promptStr += "Please write down your new, consolodated knowledge base below.  Please write it in the JSON form expected above. You can write a short amount of prose before if that's helpful for your thought process, and only the last item in code blocks (```) will be parsed as JSON.\n"


    response = OpenAIGetCompletion(client, promptStr=promptStr, promptImages=[], model="gpt-4-vision-preview", prevImage=None, temperature=0.1, maxTokens=3000)
    print(response)

    # Extract the JSON from the response
    print("EXCTRACTING MESSAGE")
    responseStrKnowledge = response.choices[0].message.content
    print("SUCCESS1")
    responseJSONKnowledge = extractJSONfromGPT4Response(responseStrKnowledge)
    print("SUCCESS2")

    if (responseJSONKnowledge == None):
        # Failed for some reason -- return original knowledge base
        #return scientificKnowledge # Deep copy
        return copy.deepcopy(scientificKnowledge)


    # Check if the response includes a "scientific_knowledge" key
    if (responseJSONKnowledge != None) and ("scientific_knowledge" in responseJSONKnowledge):
        # Check that it's a list
        if (isinstance(responseJSONKnowledge["scientific_knowledge"], list)):
            # Check that it's not empty
            newKnowledge = responseJSONKnowledge["scientific_knowledge"]
            if (len(newKnowledge) > 0):
                # Return the new KB to replace the old one.
                return {"scientific_knowledge": newKnowledge}

    # Otherwise, return the old one
    #return scientificKnowledge # deep copy
    return copy.deepcopy(scientificKnowledge)



def mkExampleHypotheses():
    out = {
        "scientific_knowledge_examples": [
            {"step": 1, "measurement": "The tree (uuid: 123) has a temperature of 10 degrees celsius when measured using the thermometer."},
            {"step": 3, "hypothesis": "if (object:substance) is (action:heated) then (object:substance) will have (property:temperature) increase.", "supporting evidence": "...", "status": "<confirmed, rejected, or pending>"},
        ]
    }

    return out

def mkInitialHypotheses():
    out = {
        "scientific_knowledge": [
        ]
    }

    return out





# For testing the API
def GPT4VHypothesizerAgent(api, numSteps:int = 10, logFileSuffix:str = ""):
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
        "running_hypotheses": []
    }

    # Keep a history of the last actions
    lastActionHistory = []
    lastActionHistory.append(lastAction)

    # Keep a history of the last observations
    observationHistory = []

    # Record start time
    startTime = time.time()

    # Run for numSteps steps in the environment
    numErrors = 0
    lastObservation = None
    currentScientificKnowledge = mkInitialHypotheses()
    allHistory = []

    for i in range(0, numSteps):
        try:
            # Run one step
            print("\n\n")
            print("-----------------------------------------------------------")
            print("Step " + str(i) + " of " + str(numSteps))
            print("-----------------------------------------------------------")
            print("")
            #lastAction, lastObservation, promptStr, responseStr
            outHypothesizer = GPT4HypothesizerOneStep(api, client, lastActionHistory, lastObservation, currentScientificKnowledge)
            # Unpack
            lastAction = outHypothesizer["nextAction"]
            lastObservation = outHypothesizer["observation"]
            promptStr = outHypothesizer["promptStr"]
            responseStr = outHypothesizer["responseStr"]
            actionSuccess = outHypothesizer["actionSuccess"]

            # Store any detailed parsing errors in the last action, so these are stored in the history for reference
            if ("errors" in actionSuccess):
                lastAction["errors"] = actionSuccess["errors"]

            allHistory.append(outHypothesizer)


            print("LAST ACTION: ")

            print(lastAction)
            print("")
            lastActionHistory.append(lastAction)


            packed = {
                "step": i,
                "observation": lastObservation,
                "action": lastAction,
                "promptStr": promptStr,
                "responseStr": responseStr,
            }
            observationHistory.append(packed)

            # Every 10 steps, consolodate the knowledge
            if (i % 10 == 0) and (i > 0):
                print("Consolodating Scientific Knowledge:")
                currentScientificKnowledge = consolodateKnowledgeStep(client, currentScientificKnowledge)

                # Add to history
                allHistory.append({"consolodated_scientific_knowledge": currentScientificKnowledge})


            # Save to JSON
            with open("output_observationHistory" + logFileSuffix + ".json", "w") as file:
                json.dump(observationHistory, file, indent=4, sort_keys=True)
            with open("output_allhistory" + logFileSuffix + ".json", "w") as file:
                json.dump(allHistory, file, indent=4, sort_keys=True)

            # Check if the task has been completed
            #if (api.isTaskComplete()):
            #    print("Task has been completed.  Exiting.")
            #    break
            if (api.areTasksComplete()):
                print("All tasks have been completed.  Exiting.")
                break

        except KeyboardInterrupt:
            print("Keyboard interrupt detected.  Exiting.")
            exit(1)

        # Generic exception, print error
        except Exception as e:
            # Get the current line number
            line_number = traceback.extract_tb(e.__traceback__)[-1].lineno
            print(f"ERROR: Exception caught on line {line_number}: {e}")
            print("ERROR: Exception caught:\n", traceback.format_exc())

            numErrors += 1

            if numErrors > 5:
                print("ERROR: Maximum number of errors exceeded (5). Exiting.")

            exit(1)

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





#
#   API test agent
#
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
    print("Known actions: " + str(api.listKnownActions(limited=LIMITED_ACTIONS)))
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



# Run the random agent on a given scenario
def runHypothesizerAgent(scenarioName:str, difficultyStr:str, seed:int=0, numSteps:int=10, exportVideo:bool=False, debug:bool=False):
    # Load the scenario
    api = DiscoveryWorldAPI()
    success = api.loadScenario(scenarioName = scenarioName, difficultyStr = difficultyStr, randomSeed = seed, numUserAgents = 1)
    if (success == False):
        print("Error: Could not load scenario '" + scenarioName + "' with difficulty '" + difficultyStr + "'.")
        return None

    startTime = time.time()
    # Hypothesizer
    logFileSuffix = "." + scenarioName + "-" + difficultyStr + "-s" + str(seed)
    GPT4VHypothesizerAgent(api, numSteps=numSteps, logFileSuffix=logFileSuffix)
    deltaTime = time.time() - startTime
    print("Elapsed time: " + str(deltaTime) + " seconds for " + str(numSteps) + " steps.")
    stepsPerSecond = numSteps / deltaTime

    # Get the final score
    finalScorecard = api.getTaskScorecard()
    print("Final scorecard: ")
    print(json.dumps(finalScorecard, indent=4, sort_keys=True))

    # Final normalized score
    taskName = finalScorecard[0]["taskName"]
    finalNormalizedScore = finalScorecard[0]["scoreNormalized"]
    print("Final normalized score for task '" + taskName + "': " + str(finalNormalizedScore))
    print("Number of steps: " + str(api.getStepCounter()))
    print("Steps per second: " + str(stepsPerSecond))

    # Create a video from the random agent
    if (exportVideo == True):
        filenameOut = "output_random_agent." + scenarioName + ".mp4"
        api.createAgentVideo(agentIdx=0, filenameOut=filenameOut)

    out = {
        "agentName": "GPT4VHypothesizerAgent",
        "finalNormalizedScore": finalNormalizedScore,
        "stepsPerSecond": stepsPerSecond
    }
    return out


#
#   Main
#
#if __name__ == "__main__":
    # print("Initializing DiscoveryWorld API... ")


    # # Parse command line arguments
    # import argparse
    # parser = argparse.ArgumentParser(description="Play DiscoveryWorld using Random Baseline Agent.")
    # parser.add_argument('--scenario', choices=SCENARIO_NAMES, default=None)
    # parser.add_argument('--difficulty', choices=SCENARIO_DIFFICULTY_OPTIONS, default=None)
    # parser.add_argument('--seed', type=int, default=0)
    # parser.add_argument('--numSteps', type=int, default=100)
    # parser.add_argument('--runall', action='store_true', help='Run all scenarios with random agent')
    # parser.add_argument('--video', action='store_true', help='Export video of agent actions')

    # args = parser.parse_args()

    # # Create the API
    # api = DiscoveryWorldAPI()
    # print(api.getNameAndVersion())


    # # Load the scenario
    # #scenarioName = "food_illness"
    # #scenarioName = "combinatorial_chemistry"
    # #scenarioName = "archaeology_dating_simple"
    # #scenarioName = "archaeology_dating_challenge"
    # #scenarioName = "plant_nutrients"
    # #scenarioName = "lost_in_translation"
    # #scenarioName = "reactor_lab"
    # #api.loadScenario(scenarioName = "combinatorial_chemistry", numUserAgents = 1, randomSeed = 0)

    # # Run a single scenario.
    # # Check the scenario and difficulty
    # if (args.scenario == None):
    #     print("Error: Must specify a scenario (or use --runall to run all scenarios).")
    #     print("Available scenarios: " + str(SCENARIO_NAMES))
    #     exit()
    # if (args.difficulty == None):
    #     print("Error: Must specify a difficulty.")
    #     print("Available difficulties: " + str(SCENARIO_DIFFICULTY_OPTIONS))
    #     exit()

    # # Get the internal scenario name
    # exportVideo = args.video
    # #finalScore = runRandomAgent(scenarioName=args.scenario, difficultyStr=args.difficulty, seed=args.seed, numSteps=args.numSteps, exportVideo=exportVideo, debug=False)
    # #api.loadScenario(scenarioName = scenarioName, numUserAgents = 1, randomSeed = 0)
    # difficultyStr = args.difficulty
    # seed = args.seed
    # success = api.loadScenario(scenarioName = args.scenario, difficultyStr = difficultyStr, randomSeed = seed, numUserAgents = 1)
    # if (success == False):
    #     print("Error: Could not load scenario '" + args.scenario + "' with difficulty '" + difficultyStr + "'.")
    #     exit(1)


    # # Test the API
    # #testAgent(api)

    # # GPT4-V Baseline Agent
    # #GPT4VBaselineAgent(api, numSteps=250)
    # #api.createAgentVideo(agentIdx=0, filenameOut="output_gpt4v.mp4")

    # # GPT4-V Hypothesizer Agent
    # GPT4VHypothesizerAgent(api, numSteps=50)
    # filenameOut = "output_gpt4v_hypothesizer." + internalScenarioName + ".mp4"
    # api.createAgentVideo(agentIdx=0, filenameOut=filenameOut)

    # # Random agent
    # #randomAgent(api, numSteps=10)
    # # Create a video from the random agent

    # #api.createAgentVideo(agentIdx=0, filenameOut="output_randomAgent.mp4")

#
#   Main
#
if __name__ == "__main__":
    print("Initializing Hypothesizer Agent... ")

    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Play DiscoveryWorld using Hypothesizer Agent.")
    parser.add_argument('--scenario', choices=SCENARIO_NAMES, default=None)
    parser.add_argument('--difficulty', choices=SCENARIO_DIFFICULTY_OPTIONS, default=None)
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--numSteps', type=int, default=100)
    ##parser.add_argument('--runall', action='store_true', help='Run all scenarios with random agent')      ## Disabled -- would be extremely expensive and time consuming to do this
    parser.add_argument('--video', action='store_true', help='Export video of agent actions')

    args = parser.parse_args()
    args.runall = False

    # Check for mode
    stepsPerSecond = []
    if (args.runall == True):
        # Run all scenarios
        scores = {}
        for scenarioName in SCENARIO_NAMES:
            # Get the valid difficulty settings and random seeds for this scenario
            validDifficulties = SCENARIO_INFOS[scenarioName]["difficulty"]
            validSeeds = SCENARIO_INFOS[scenarioName]["variations"]
            validSeeds = [int(x) for x in validSeeds]

            for difficulty in validDifficulties:
                for seed in validSeeds:
                    print("Running scenario: " + scenarioName + " with difficulty " + difficulty)
                    result = runHypothesizerAgent(scenarioName=scenarioName, difficultyStr=difficulty, seed=seed, numSteps=args.numSteps, exportVideo=False, debug=False)
                    finalScore = result["finalNormalizedScore"]
                    stepsPerSecond.append(result["stepsPerSecond"])


                    scoreKey = scenarioName + "-" + difficulty
                    if (scoreKey not in scores):
                        scores[scoreKey] = []
                    scores[scoreKey].append(finalScore)


            # Calculate average scores
            scoresAvg = {}
            for key in scores:
                scoreList = scores[key]
                # Remove any Nones from the list
                scoreList = [x for x in scoreList if x != None]
                averageScore = None
                if (len(scoreList) > 0):
                    averageScore = sum(scoreList) / len(scoreList)
                scoresAvg[key + "-avg"] = averageScore
                scoresAvg[key + "-raw"] = scoreList

            print("Final scores: ")
            packed = {
                "scores_raw": scores,
                "scores_avg": scoresAvg,
                "numSteps": args.numSteps,
            }
            print(json.dumps(packed, indent=4, sort_keys=True))



    else:
        # Run a single scenario.
        # Check the scenario and difficulty
        if (args.scenario == None):
            print("Error: Must specify a scenario (or use --runall to run all scenarios).")
            print("Available scenarios: " + str(SCENARIO_NAMES))
            exit()
        if (args.difficulty == None):
            print("Error: Must specify a difficulty.")
            print("Available difficulties: " + str(SCENARIO_DIFFICULTY_OPTIONS))
            exit()

        # Get the internal scenario name
        internalScenarioName = getInternalScenarioName(args.scenario, args.difficulty)
        if (internalScenarioName == None):
            print("Error: Could not find internal scenario name for scenario '" + args.scenario + "' and difficulty '" + args.difficulty + "'.")
            print("Available scenarios: " + str(SCENARIO_NAMES))
            print("Available difficulties: " + str(SCENARIO_DIFFICULTY_OPTIONS))
            exit()

        exportVideo = args.video
        finalScore = runHypothesizerAgent(scenarioName=args.scenario, difficultyStr=args.difficulty, seed=args.seed, numSteps=args.numSteps, exportVideo=exportVideo, debug=False)

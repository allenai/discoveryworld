
# DiscoveryWorldAPIUsageExample.py


from discoveryworld.DiscoveryWorldAPI import DiscoveryWorldAPI
from discoveryworld.ScenarioMaker import ScenarioMaker, SCENARIOS, SCENARIO_NAMES, SCENARIO_INFOS, SCENARIO_DIFFICULTY_OPTIONS, getInternalScenarioName

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
def randomAgent(api, numSteps:int = 10, seed:int = None, debug:bool = False):
    r = random.Random()
    if (seed == None):
        # Use the current time (in integer form) as a seed
        intTime = int(time.time())
        r.seed(intTime)
        print("Random Agent Seed: " + str(intTime))
    else:
        r.seed(seed)
        print("Random Agent Seed: " + str(seed))

    # Record start time
    startTime = time.time()

    uis = api.ui
    print(uis)

    print("Number of agents: " + str(len(uis)))
    firstAgent = uis[0]
    print(firstAgent)
    print(type(firstAgent))
    print(firstAgent.currentAgent)



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
        if (debug == True):
            print(json.dumps(observation, indent=4, sort_keys=True))

        # Get task progress
        taskScorecard = api.getTaskScorecard()
        if (debug == True):
            print("Task Scorecard: ")
            print(json.dumps(taskScorecard, indent=4, sort_keys=True))
        else:
            print("Task Score (normalized): " + str(taskScorecard[0]["scoreNormalized"]))


        # Take an action
        if (api.isAgentInDialog(agentIdx=0)):
            # Agent is in dialog -- must be a dialog option
            dialog = observation["ui"]["dialog_box"]
            print("Agent is in dialog")
            print(json.dumps(dialog, indent=4, sort_keys=True))
            #promptDialogStr = "The expected response format is JSON, in between code brackets (```), as a dictionary with a single key: `chosen_dialog_option_int`.  The value should be an integer, corresponding to the dialog option you would like to select. You can write prose before the JSON code block, if that helps you think.\n"
            # They keys in `dialog` are: `dialogIn` (the text from the NPC the agent is talking to), `dialogOptions` (a dictionary, keys: option string to select, value: what to say)
            possibleOptions = dialog["dialogOptions"].keys()
            # Randomly select one option
            chosenOption = r.choice(list(possibleOptions))

            # NOTE: The option keys are provided as strings, for some reason. Try to convert the option to an integer
            try:
                chosenOptionInt = int(chosenOption)
            except:
                chosenOptionInt = random.randint(1, len(possibleOptions)+1)

            dialogActionJSONOut = {
                "chosen_dialog_option_int": chosenOptionInt
            }

            actionSuccess = api.performAgentAction(agentIdx=0, actionJSON=dialogActionJSONOut)
            print("actionSuccess: " + str(actionSuccess))

        else:
            # Normal action

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
def runRandomAgent(scenarioName:str, difficultyStr:str, seed:int=0, numSteps:int=10, exportVideo:bool=False, threadId:int=1, debug:bool=False):
    # Load the scenario
    api = DiscoveryWorldAPI(threadID=threadId)
    success = api.loadScenario(scenarioName = scenarioName, difficultyStr = difficultyStr, randomSeed = seed, numUserAgents = 1)
    if (success == False):
        print("Error: Could not load scenario '" + scenarioName + "' with difficulty '" + difficultyStr + "'.")
        return None

    startTime = time.time()
    # Random agent
    logFileSuffix = "." + scenarioName + "-" + difficultyStr + "-s" + str(seed) + "-thread" + str(api.THREAD_ID)
    randomAgent(api, numSteps=numSteps, debug=debug)
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
        filenameOut = "output_random_agent." + logFileSuffix + ".mp4"
        api.createAgentVideo(agentIdx=0, filenameOut=filenameOut)

    completed = 0
    if (finalScorecard[0]["completed"] == True):
        completed = 1
    completedSuccessfully = 0
    if (finalScorecard[0]["completedSuccessfully"] == True):
        completedSuccessfully = 1

    out = {
        "agentName": "RandomAgent",
        "finalNormalizedScore": finalNormalizedScore,
        "completed": completed,
        "completedSuccessfully": completedSuccessfully,
        "stepsPerSecond": stepsPerSecond,
    }
    return out


#
#   Main
#
if __name__ == "__main__":
    print("Initializing DiscoveryWorld API... ")

    # Randomly generate a thread ID, in case one isn't specified
    # Random seed based on the current time
    rThread = random.Random()
    rThread.seed(int(time.time()))
    randomThreadId = rThread.randint(1, 10000000)

    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Play DiscoveryWorld using Random Baseline Agent.")
    parser.add_argument('--scenario', choices=SCENARIO_NAMES, default=None)
    parser.add_argument('--difficulty', choices=SCENARIO_DIFFICULTY_OPTIONS, default=None)
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--numSteps', type=int, default=100)
    parser.add_argument('--runall', action='store_true', help='Run all scenarios with random agent')
    parser.add_argument('--video', action='store_true', help='Export video of agent actions')
    parser.add_argument('--threadId', type=int, default=randomThreadId)

    args = parser.parse_args()
    print("Using Thread ID: " + str(args.threadId))
    print("This can be specified with the '--threadId' argument.")
    time.sleep(1)

    # Check for mode
    stepsPerSecond = []
    if (args.runall == True):
        import datetime
        now = datetime.datetime.now()
        dateStr = now.strftime("%Y-%m-%d_%H-%M-%S")

        # Run all scenarios
        scores = {}
        completed = {}
        completedSuccessfully = {}
        for scenarioName in SCENARIO_NAMES:
            # Get the valid difficulty settings and random seeds for this scenario
            validDifficulties = SCENARIO_INFOS[scenarioName]["difficulty"]
            validSeeds = SCENARIO_INFOS[scenarioName]["variations"]
            validSeeds = [int(x)-1 for x in validSeeds]     # -1 to convert from 1-indexed to 0-indexed

            for difficulty in validDifficulties:
                for seed in validSeeds:
                    print("Running scenario: " + scenarioName + " with difficulty " + difficulty)
                    result = runRandomAgent(scenarioName=scenarioName, difficultyStr=difficulty, seed=seed, numSteps=args.numSteps, exportVideo=False, threadId = args.threadId, debug=False)
                    finalScore = result["finalNormalizedScore"]
                    stepsPerSecond.append(result["stepsPerSecond"])
                    completed1 = result["completed"]
                    completedSuccessfully1 = result["completedSuccessfully"]

                    scoreKey = scenarioName + "-" + difficulty
                    if (scoreKey not in scores):
                        scores[scoreKey] = []
                        completed[scoreKey] = []
                        completedSuccessfully[scoreKey] = []

                    scores[scoreKey].append(finalScore)
                    completed[scoreKey].append(completed1)
                    completedSuccessfully[scoreKey].append(completedSuccessfully1)


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

            # Completed average scores
            completedAvg = {}
            for key in completed:
                completedList = completed[key]
                completedList = [x for x in completedList if x != None]
                completedAvg[key + "-avg"] = sum(completedList) / len(completedList)
                completedAvg[key + "-raw"] = completedList

            # Completed Successfully average scores
            completedSuccessfullyAvg = {}
            for key in completedSuccessfully:
                completedSuccessfullyList = completedSuccessfully[key]
                completedSuccessfullyList = [x for x in completedSuccessfullyList if x != None]
                completedSuccessfullyAvg[key + "-avg"] = sum(completedSuccessfullyList) / len(completedSuccessfullyList)
                completedSuccessfullyAvg[key + "-raw"] = completedSuccessfullyList

            print("Final scores: ")
            packed = {
                "numSteps": args.numSteps,
                "scores_raw": scores,
                "scores_avg": scoresAvg,
                "completed_raw": completed,
                "completed_avg": completedAvg,
                "completedSuccessfully_raw": completedSuccessfully,
                "completedSuccessfully_avg": completedSuccessfullyAvg,
            }
            print(json.dumps(packed, indent=4, sort_keys=True))

            # Save to file with a verbose filename
            # Add date/time
            filenameOut = "output_random_agent-allscenarios-numSteps" + str(args.numSteps) + "-thread" + str(args.threadId) + "." + dateStr + ".json"
            with open(filenameOut, "w") as f:
                json.dump(packed, f, indent=4, sort_keys=True)



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
        finalScore = runRandomAgent(scenarioName=args.scenario, difficultyStr=args.difficulty, seed=args.seed, numSteps=args.numSteps, exportVideo=exportVideo, threadId=args.threadId, debug=False)

# # Analysis.py

import json
import os


def getPerformance(filenameIn:str):
    # Load the JSON file
    with open(filenameIn) as f:
        data = json.load(f)

    # Go through each record, and find either (1) the first one where the task is completed, or (2) if none are completed, the last one
    scoreCard = None
    lastStepIdx = 0
    for idx, stepRecord in enumerate(data):
        #print("Step: " + str(idx))
        if ("oracle_scorecard" in stepRecord):
            scoreCard = stepRecord["oracle_scorecard"]
            # All tasks have only a single scorecard, but it's stored as a list -- so just take the first one
            scoreCard = scoreCard[0]
            lastStepIdx = idx
            if (scoreCard["completed"] == True):
                # Break on the first step when the task is marked completed
                break

    print(scoreCard)
    if (scoreCard == None):
        print("No scorecard found")
        return

    try:
        # Get the performance
        taskName = scoreCard["taskName"]
        scoreNormalized = scoreCard["scoreNormalized"]
        scoreRaw = scoreCard["score"]
        scoreMax = scoreCard["maxScore"]
        completed = scoreCard["completed"]
        completedSuccessfully = scoreCard["completedSuccessfully"]
        # Change completed and completed successfully to ints (0/1) instead of bools
        if (completed == True):
            completed = 1
        else:
            completed = 0

        if (completedSuccessfully == True):
            completedSuccessfully = 1
        else:
            completedSuccessfully = 0

        # Try and extract metadata from the filename
        # Filenames are of the form: output_allhistory.Small Skills/ Search Test-Normal-s0-imagesFalse-modelgpt-3.5-turbo-0125-thread5108.20240510-164312.json
        # Want to extract: Task name (Small Skills Search Test), Difficulty (normal), seed (s0), images true/false, model name, thread, timestamp
        # Remove the "output_allhistory." prefix
        processedFilename = filenameIn.split("output_allhistory.")[1]
        # remove the ".json"
        processedFilename = processedFilename.split(".json")[0]
        # Everything before the first "-" is the task name
        taskName = processedFilename.split("-")[0]
        # Everything between the first and second "-" is the difficulty
        difficulty = processedFilename.split("-")[1]
        # Everything between the second and third "-" is the seed
        seed = processedFilename.split("-")[2]
        # Remove the 's' from the seed
        seed = int(seed[1:])
        # Everything between the third and fourth "-" is the images flag
        images = processedFilename.split("-")[3]
        # Remove the 'images' prefix
        imagesStr = images[6:]
        if (imagesStr == "True"):
            images = True
        else:
            images = False

        # Everything between "-model" and "-thread" is the model name
        model = processedFilename.split("-model")[1]
        model = model.split("-thread")[0]
        # Everything between "-thread" and "." is the thread
        thread = processedFilename.split("-thread")[1]
        thread = thread.split(".")[0]
        # The timestamp is everything after "thread<num>."
        timestamp = processedFilename.split("thread" + thread + ".")[1]

        # Also try to load the "cost analysis" file
        costFilename = filenameIn.replace("output_allhistory", "output_costAnalysis")
        costData = None
        totalCost = None
        totalSteps = None
        totalTokensReceived = None
        totalTokensSent = None
        try:
            with open(costFilename) as f:
                costData = json.load(f)
                totalCost = costData["total_cost"]
                totalSteps = costData["total_steps"]
                totalTokensReceived = costData["total_tokens_received"]
                totalTokensSent = costData["total_tokens_sent"]
        except:
            print("No cost analysis file found: " + costFilename)


        # Return
        packed = {
            "taskName": taskName,
            "difficulty": difficulty,
            "seed": seed,
            "images": images,
            "model": model,
            "thread": thread,
            "timestamp": timestamp,
            "scoreNormalized": scoreNormalized,
            "scoreRaw": scoreRaw,
            "scoreMax": scoreMax,
            "completed": completed,
            "completedSuccessfully": completedSuccessfully,
            "lastStepIdx": lastStepIdx,
            "filename": filenameIn,
            "totalCost": totalCost,
            "totalSteps": totalSteps,
            "totalTokensReceived": totalTokensReceived,
            "totalTokensSent": totalTokensSent
        }

        return packed

    except:
        print("Error: unable to extract metadata from filename (" + filenameIn + ")")
        return None


# Calculate the average performance -- essentially the mean of the scores across all seeds for each task/difficulty/model
def calculateAveragePerformance(allPerformance):
    outAvg = []
    # Grouping must have same: taskName, difficulty, model, images
    # First make a `groupID` for each record
    for performance in allPerformance:
        performance["groupID"] = str(performance["taskName"]) + "-" + str(performance["difficulty"]) + "-" + str(performance["model"]) + str(performance["images"]) + "-"

    def mkBlankPerformance():
        packed = {
            "taskName": None,
            "difficulty": None,
            "model": None,
            "images": None,
            "groupID": None,
            "numSamples": 0,
            "timestamps": [],
            "seeds": [],
            "threads": [],
            "filenames": [],
            "scores": {
                "scoreNormalized": 0,
                "scoreRaw": 0,
                "scoreMax": 0,
                "completed": 0,
                "completedSuccessfully": 0,
                "lastStepIdx": 0,
                "totalCost": 0,
                "totalSteps": 0,
                "totalTokensReceived": 0,
                "totalTokensSent": 0,
            }
        }
        return packed

    # Now, sum up the scores for each group
    groupScores = {}
    for performance in allPerformance:
        groupID = performance["groupID"]
        if (groupID not in groupScores):
            groupScores[groupID] = mkBlankPerformance()
            groupScores[groupID]["taskName"] = performance["taskName"]
            groupScores[groupID]["difficulty"] = performance["difficulty"]
            groupScores[groupID]["model"] = performance["model"]
            groupScores[groupID]["images"] = performance["images"]
            groupScores[groupID]["groupID"] = groupID

        groupScores[groupID]["timestamps"].append(performance["timestamp"])
        groupScores[groupID]["seeds"].append(performance["seed"])
        groupScores[groupID]["threads"].append(performance["thread"])
        groupScores[groupID]["filenames"].append(performance["filename"])

        # Sort threads, seeds
        groupScores[groupID]["threads"] = sorted(list(set(groupScores[groupID]["threads"])))
        groupScores[groupID]["seeds"] = sorted(list(set(groupScores[groupID]["seeds"])))

        # Add the scores to the group
        for key in groupScores[groupID]["scores"]:
            groupScores[groupID]["scores"][key] += performance[key]

        groupScores[groupID]["numSamples"] += 1


    # Now, calculate the average
    for groupID in groupScores:
        for key in groupScores[groupID]["scores"]:
            if (groupScores[groupID]["numSamples"] > 0):
                groupScores[groupID]["scores"][key] = groupScores[groupID]["scores"][key] / groupScores[groupID]["numSamples"]

        # Move the keys from "scores" to the top level
        for key in groupScores[groupID]["scores"]:
            groupScores[groupID]["avg_"+key] = groupScores[groupID]["scores"][key]
        del groupScores[groupID]["scores"]

        # Also keep non-average copies of the following keys: totalCost, totalSteps, totalTokensReceived, totalTokensSent
        groupScores[groupID]["totalCost"] = groupScores[groupID]["avg_totalCost"] * groupScores[groupID]["numSamples"]
        groupScores[groupID]["totalSteps"] = groupScores[groupID]["avg_totalSteps"] * groupScores[groupID]["numSamples"]
        groupScores[groupID]["totalTokensReceived"] = groupScores[groupID]["avg_totalTokensReceived"] * groupScores[groupID]["numSamples"]
        groupScores[groupID]["totalTokensSent"] = groupScores[groupID]["avg_totalTokensSent"] * groupScores[groupID]["numSamples"]


        outAvg.append(groupScores[groupID])

    # Return
    return outAvg


#
#   Main
#
if __name__ == "__main__":

    #dataPath = "."   # Current directory
    #dataPath = "output-hypothesizer-8unit/"
    #dataPath = "output-hypothesizer-gpt4o-9discovery/"

    #dataPath = "paper-results/output-may24-hypothesizer-unittest/"       # Unit test results for paper
    dataPath = "paper-results/output-may24-hypothesizer-discovery-easy/" # Discovery task (difficulty: easy) results for paper

    # Step 1: Find a list of files that start with "output_allhistory" that end with ".json"
    filterPrefix = "output_allhistory"
    jsonFiles = [pos_json for pos_json in os.listdir(dataPath) if pos_json.endswith('.json')]
    jsonFiles = [file for file in jsonFiles if file.startswith(filterPrefix)]

    # Step 2: Get the summary statistics for each file
    allPerformance = []
    for idx, filename in enumerate(jsonFiles):
        print("--------------------------------------------------")
        print("File " + str(idx+1) + " of " + str(len(jsonFiles)))
        print("Processing file: " + filename)
        performance = getPerformance(dataPath + "/" + filename)
        print(performance)
        if (performance != None):
            allPerformance.append(performance)
        print("")

    # Calculate average performance
    averagePerformance = calculateAveragePerformance(allPerformance)

    # Sort by taskName, then by difficulty, then model, then images, then by seed, then date
    allPerformance.sort(key=lambda x: str(x["taskName"]) + str(x["difficulty"]) + str(x["model"]) + str(x["images"]) + str(x["seed"]) + str(x["timestamp"]))

    # Step 3: Export as JSON
    filenameOut = dataPath + "/performanceSummary.json"
    print("Writing " + filenameOut + "...")
    with open(filenameOut, "w") as f:
        f.write(json.dumps(allPerformance, indent=4))

    # Step 4: Export as TSV
    filenameOut = dataPath + "/performanceSummary.tsv"
    print("Writing " + filenameOut + "...")
    with open(filenameOut, "w") as f:
        # Write the header
        header = ["taskName", "difficulty", "seed", "images", "model", "thread", "timestamp", "scoreNormalized", "scoreRaw", "scoreMax", "completed", "completedSuccessfully", "lastStepIdx", "filename", "totalCost", "totalSteps", "totalTokensReceived", "totalTokensSent"]
        f.write("\t".join(header) + "\n")
        # Write the data
        for performance in allPerformance:
            print(performance)
            row = []#[str(performance[key]) for key in header]
            for key in header:
                if (key in performance):
                    row.append(str(performance[key]))
                else:
                    row.append("")
            print("row: " + str(row))
            f.write("\t".join(row) + "\n")

    print("\n")
    print("Wrote " + str(len(allPerformance)) + " records to " + filenameOut)

    # Now write the averages
    averagePerformance.sort(key=lambda x: str(x["taskName"]) + str(x["difficulty"]) + str(x["model"]) + str(x["images"]))
    filenameOut = dataPath + "/performanceSummary.average.json"
    print("Writing " + filenameOut + "...")
    with open(filenameOut, "w") as f:
        f.write(json.dumps(averagePerformance, indent=4))

    # Step 4: Export as TSV
    filenameOut = dataPath + "/performanceSummary.average.tsv"
    print("Writing " + filenameOut + "...")
    with open(filenameOut, "w") as f:
        # Write the header
        header = ["taskName", "difficulty", "images", "model", "seeds", "numSamples", "avg_scoreNormalized", "avg_scoreRaw", "avg_scoreMax", "avg_completed", "avg_completedSuccessfully", "avg_lastStepIdx", "avg_totalCost", "avg_totalSteps", "avg_totalTokensReceived", "avg_totalTokensSent", "totalCost", "totalSteps", "totalTokensReceived", "totalTokensSent", "threads", "timestamps", "filenames"]
        f.write("\t".join(header) + "\n")
        # Write the data
        for performance in averagePerformance:
            row = [str(performance[key]) for key in header]
            f.write("\t".join(row) + "\n")

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
    


#
#   Main
#
if __name__ == "__main__":

    dataPath = "."   # Current directory

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


    # Sort by taskName, then by difficulty, then model, then images, then by seed, then date
    allPerformance.sort(key=lambda x: str(x["taskName"]) + str(x["difficulty"]) + str(x["model"]) + str(x["images"]) + str(x["seed"]) + str(x["timestamp"]))

    # Step 3: Export as JSON
    print("Writing performanceSummary.json...")
    with open("performanceSummary.json", "w") as f:
        f.write(json.dumps(allPerformance, indent=4))

    # Step 4: Export as TSV
    print("Writing performanceSummary.tsv...")
    with open("performanceSummary.tsv", "w") as f:
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

    
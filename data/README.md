# DiscoveryWorld -- Data Release (June 2024)

This archive contains the data release for the experiments in the DiscoveryWorld paper (June 2024). 

## Download Link

Full data: [Google Drive](https://drive.google.com/drive/folders/14FucVzVCm1HZ0EfPEKoPwdRsFnZi769k?usp=drive_link)

Only the agent videos (mp4): [Google Drive](https://drive.google.com/file/d/1I34EMVRUIIOppQFX3RueG4Nl75n8_zlJ/view?usp=drive_link)

Note that to reduce download time for those requiring only a subset of the data, data is provided as separate archives for each agent and task difficulty level. 

## Data Location

### Agent Data

Agent data can be found in the following directories:

- ReACT: `/react/`
- Plan and Execute: `/p+e/`
- Hypothesizer: `/hypothesizer/`
- Random Baseline: `/random-agent/`


### Human Scientist Data

High-level results distilled from all human playlogs can be found in the `/human-performance/` directory. 
These contain: 
- Scores and scorecards for each attempted human run
- The action history (i.e. each action the person took, at each time step).  This is extracted from the large log files. 

The human scientist raw log files are in: `/human-raw/`. 
The pre-processed log files (using the process described below) are in: `/human-performance/`.

The script to extract the high-level information from the full log files is as follows.  *Note this typically takes a few hours to run, and can consume quite a bit of RAM, since the log files are very large. *
- Step 1: Consolidate summary information (scores, actions, etc.) for runs into a single log file: https://github.com/allenai/discoveryworld/blob/main/scripts/analysisHumanPerformance.py
- Step 2: Extract the subset of the runs that participants completed first, calculate summary statistics: https://github.com/allenai/discoveryworld/blob/main/scripts/analysisHumanPerformanceFollowOn.py


## Data Format

### Performance Summaries

Folders include `performanceSummary.{json/tsv}` and `performanceSummary.average.{json/tsv}` files that contain high-level statistics for each run (former), as well as averages across all seeds in each run (latter).  

These files are generated using the `TODO` scripts.


### World Logs
World logs store nearly all of the current world state (i.e. everything that is easily serializable), for every step in a given run.  The format is a JSON array, with each array element representing one step in the game. The high-level keys are:
- `step`: The step index
- `sizeX` and `sizeY`: The world grid size (nominally, always 32)
- `grid`: a sizeX * sizeY * N array, containing all the objects at a given location.
- `discoveryFeed`: All the DiscoveryFeed posts
- `taskScores`: The detailed task scorecard
- `runtime_seconds`: The total elapsed time since the run was started.

Since these files can be very large, they are typically parted into a number of ZIP files (`...partXofY.zip`), each containing a maximum of 100 steps.  To assemble the full world history, one must load the (up to) 100 steps from each file, in turn. 


### Videos

The run of each agent is usually saved as a video, in `mp4` format.  Sometimes (as in the human studies), a directory of `PNG` frames (one frame per step) are provided instead. 


## Agent Logs

### ReAct, Plan and Execute

These save separate files that constitute the agent's actions and `thought` string at each time step.  The `tought` string was used for the knowledge evaluation step.

### Hypothesizer

Hypothesizer exports detailed logs containing the entire history of the run, with the prefix `output_allhistory_*.json`.  This file is an array of steps, with each step including the following information: 
- `currentScientificKnowledge`: The agent's scientific working memory
- `nextAction`: The action the agent chose to perform during this step (which typically also includes an explanation, and other information about planning that's passed between steps
- `observation`: The observation, as returned from the DiscoveryWorld environment
- `oracle_scorecard`: The detailed task scorecard
- `actionSuccess`: Was the action parsed correctly?
- `knowledgePromptStr`: The reflection prompt used to produce the knowledgePromptStr
- `promptStr`: The prompt used to produce the next action

In addition, every 10 steps is a "knowledge consolidation step".  These steps contain only a single key, `consolidated_scientific_knowledge`, which shows the result of condensing the agent's scientific working memory to prevent it from becoming large.


## Recommended Parsing Approach

If you're building a custom parser for these log files, it's recommended that you develop the parser on either the `unit test` or `easy difficulty` runs -- those log files are usually much smaller, and more easily visible with text editors. 


## Human Notes

The notes taken by the human participants are provided in sanitized (TXT/TSV) format, in the human data release.

## Running the complete analysis pipeline

For agents, there are two separate scripts for performing the full scoring pipeline (one for the React/Plan+Execute agent, the other for the Hypothesizer agent).  These scripts:
- Read all the verbose log files for all an agent's runs
- Combine and average the performance scores across seeds (nominally, seeds 0-4 for a given *{task theme, difficulty}* setting
- Run the external *discovery knowledge scoring* utility, using OpenAI GPT-4o.

The scripts to run the complete scoring are: 
- `Hypothesizer`: https://github.com/allenai/discoveryworld/blob/main/scripts/analysisAgent.py
- `ReAct/Plan+Execute`: https://github.com/allenai/discoveryworld/blob/main/scripts/analysisReactKnowledge.py

The script files export both a file containing all the extracted performance values of each run (`performanceSummary.{json/tsv}`), as well as the average performance (`performanceSummary.average.{json/tsv}`) that you might use for a table.  The knowledge scoring can take tens of minutes, depending on the API speed -- you can comment this out if you are only looking for `task completion` and `procedural progress` scores.  The OpenAI calls to evaluate `discovery knowledge` are not metered and do not have a hard cost cutoff -- if you're evaluating an unknown amount of knowledge, or otherwise would likely the safety of a hard cost cutoff, you may wish to add this.

If you're using or adapting these analysis scripts to your own agents, it's recommended that you inspect the raw performance values (i.e. `performanceSummary.tsv`) to make sure everything looks okay before looking at the averages (`performanceSummary.average.tsv`), to make sure that all the expected seeds ran successfully, etc.  Much of this information is provided in the *average* file to help you notice any errors, but double-checking your run data manually before running follow-on analyses is always a good idea.

## Errata

- The Lost in Translation and Rocket Science scorers contained bugs when the human participants played them, and were corrected post-hoc.  The scores used in the current DiscoveryWorld release are more fine-grained, and do not contain these issues.  More specifically: (1) Lost in Translation: (a) scorecard made more fine-grained, (b) scorecard was not properly scoring some components. (2) Rocket Science: (a) scorecard made more fine-grained, (b) final success condition was not being detected correctly.

- Earlier versions of DiscoveryWorld had a bug where dialog actions were not saved to the log file, so these may be missing from some logs.  Dialog actions are both dialogs between the agent and a non-player character (NPC) agent, but also between some devices that contain dialog trees (like the crystal reactor, or soil computer). 

- Knowledge Scorer: Earlier (pre-release) versions of discoveryworld contained a mix of descriptive and explanatory knowledge in a different scorecard key (`criticalHypotheses`), before migrating to the current method of short, binary questions that typically evaluate explanatory knowledge (in `criticalQuestions`).  Beause of this, for most of the agent/human log files, the scorecards are missing the `criticalQuestions` to directly evaluate against.  As such, the Knowledge Scorerer takes the `{task theme, difficulty, seed}` as input, initializes a DiscoveryWorld task using these, and then extracts the `criticalQuestions` from it's scorecard.  If you notice fresh environments being instantiated while running the knowledge scorer, this is why.

- Agent videos: Agent videos are automatically created by exporting frames (frame_1.png, frame_2.png, etc.) as an agent runs, then assembling these into an `mp4` file at the end of the run using `ffmpeg`.  For the Plant Nutrient (Normal and Challenge) tasks, for an internal reason (i.e. letting the simulation run for 10 ticks before the user plays, to allow plants to grow naturally), the frames start at 10, which `ffmpeg` doesn't pick up automatically, so videos were not automatically generated for these runs.  As such, some of these videos are not included in the repository.

# DiscoveryWorld: A Virtual Environment for Developing and Evaluating Automated Scientific Discovery Agents
NeurIPS Datasets and Benchmarks 2024 (Spotlight)

![discoveryworld](doc/discoveryworld-logo.png)

## Example Agent Video
Below is a short 60 second clip of one of the baseline agents *(Hypothesizer)* attempting a task (Proteomics, Normal Difficulty, Seed 0).  For comparison, a narrated walkthrough of a human playing this same scenario is available on [Youtube](https://www.youtube.com/watch?v=hKWd-pwF0_E).

![discoveryworld-video](doc/output_hypothesizer_agent.Proteomics-Normal-s0-imagesTrue-modelgpt-4o-thread2007.20240525-142057-first60sec.gif)

## 1. Quick Start

### 1.1. I want to read about DiscoveryWorld
The DiscoveryWorld paper (NeurIPS 2024, Spotlight) is available here: [https://openreview.net/forum?id=cDYqckEt6d](https://openreview.net/forum?id=cDYqckEt6d)

A short summary is also available on the [project website](https://allenai.github.io/discoveryworld/).

### 1.2. I want to play DiscoveryWorld using the graphical user interface intended for humans
Installing and running DiscoveryWorld is easy, and generally takes just a few minutes.  To run as a human, please follow the installation instructions in `Section 2` below.

*NOTE: The paper contains spoilers for the DiscoveryWorld tasks.  If you'd like to complete them as the human scientist participants did, without prior knowledge, we would recommend trying the tasks before reading the paper in detail.*

### 1.3. I want to make my own DiscoveryWorld agent, or examine the baseline agents.
The baseline agents are provided in `/agents`, with a special README intended to help you get started quickly, and callout helpful portions of the code that you might be interested in viewing or reusing:
https://github.com/allenai/discoveryworld/tree/main/agents

API documentation is provided below in `Section 3`.

### 1.4. I want to examine the raw data from the agent runs or human runs described in the paper, or see videos of agents playing DiscoveryWorld.
Links to full data releases, including instructions for downloading, as well as their format and other datacard information, is provided in `/data`:
https://github.com/allenai/discoveryworld/tree/main/data

A direct link to a limited archive containing only videos of the baseline agents playing DiscoveryWorld is [available here](https://drive.google.com/file/d/1I34EMVRUIIOppQFX3RueG4Nl75n8_zlJ/view?usp=drive_link).

### 1.5. I want to view the instructions provided to the human scientists when they played DiscoveryWorld.
Please find the instructions provided to the human scientists in `README-USERSTUDY.md`.

### 1.6. I want to see a human scientist playthrough of a DiscoveryWorld task.

Please find a narrated human playthrough of one of the shortest tasks, Proteomics (on Normal difficulty), [available on Youtube](https://www.youtube.com/watch?v=hKWd-pwF0_E).

## 2. Installation and Running

### 2.1. Installation

#### Cloning the repository

Clone this repository:
```
git clone https://github.com/allenai/codescientist
cd codescientist
```

Create a conda environment:
```
conda create --name codescientist python=3.12
conda activate codescientist
```

Install the dependencies:
```
pip install -r requirements.txt
```

#### Modal Setup

TODO

#### API Key Setup

- Make sure you have keys with limited, specified budgets
  
TODO



### 2.2. Running the Server and GUI
The back-end server can be spawned with the following command:
```
python src/ExperimentWebServer.py
```

In another terminal window, you can spawn the front-end GUI using the following command:
```
python src/ExperimentWebInterface.py
```

You should then see a message that looks something like: 
```
 * Running on http://127.0.0.1:8080/ (Press CTRL+C to quit)
```

Pointing your web browser to that URL should show the main menu:

![codescientist-main-menu](images/codescientist-main-menu.png)



## 4. Citation
If you use this work, please reference the following citation:
```
TODO
```

## 7. License

CodeScientist is released under an Apache 2.0 License.  The text of that license is included in this repository.

```
Disclaimer of Warranty. Unless required by applicable law or
agreed to in writing, Licensor provides the Work (and each
Contributor provides its Contributions) on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied, including, without limitation, any warranties or conditions
of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
PARTICULAR PURPOSE. You are solely responsible for determining the
appropriateness of using or redistributing the Work and assume any
risks associated with Your exercise of permissions under this License.
```

## 8. Contact

For any questions, please contact Peter Jansen (`peterj@allenai.org`).  For issues, bugs, or feature requests, please submit a Github Issue.



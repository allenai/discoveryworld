# DiscoveryWorld

This is the repository for DiscoveryWorld (currently under development)

![discoveryworld](doc/screenshot.png)

## Installation and Running

### Installation

Clone this repository:
```
git clone https://github.com/allenai/discoveryworld.git
cd discoveryworld
```

Create a conda environment:
```
conda create --name discoveryworld python=3.9
conda activate discoveryworld
```

Install the dependencies:
```
pip install -r requirements.txt
pip install -e .
```


### Running

The graphical interface can be run with the following command from the `discoveryworld` root:
```
python scripts/userstudy.py
```


## Controls

The following controls are supported:
* **Arrow keys for movement:** `left/right` keys rotate the agent, `up/down` move forward/backward
* **Arguments:** The objects the agent interacts with are specified by the argument boxes, at the bottom. Use number keys to select specific inventory item of the top argument box, hold shift + number keys for the bottom argument box. Alternatively, `[` and `]` cycle the selection through the top argument box, and `;` and `'` for the bottom argument box.
* **TAB:** View the current task information.
* **Pick up object:** `Space` will attempt to pick up the object in `arg1`
* **Drop object:** `d` will drop the object in `arg1`
* **Put object in container:** `p` will attempt to put the object in `arg1` in the container in `arg2`
* **Give object to another character:** `p` will attempt to give the object in `arg1` to the character in `arg2`
* **Open/Close:** `o` and `c` will attempt to open/close `arg1`
* **Activate/Deactivate:** `a` and *`s`* will attempt to activate/deactivate `arg1`
* **Use:** `u` will attempt to use `arg1` on `arg2` (e.g. use shovel on soil)
* **Talk:** `t` will attempt to talk to the agent in `arg1`
* **Read:** `r` will read the object in `arg1`
* **Eat:** `e` will eat `arg1`
* **Wait:** `w` will do nothing.
* **DiscoveryFeed:** `v` will view the most recent posts on the Discovery Feed.
* **Help:** `?` or `F1` to display help message.
* **Quit:** `ESC` will exit.


## Logging

The `userstudy.py` user interface saves extensive logs after each run, including the full game state at each step, the user actions, and frame captures of the game at each step (to assemble a video).  These are stored in the `logs` subdirectory.

## Contact

For any questions, find `Peter Jansen` on Slack (or e-mail `peterj@allenai.org`)

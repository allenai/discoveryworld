# Rosetta Stone

The goal of a Rosetta Stone game is to discover the meaning of some words in an alien language.
With that new knowledge, the agent should be able to complete a task given by the elder in that alien language.


# Tasks:
#   put  [X] in/on [Y] (where X is an object and Y is receptacle/container),
#   open [X] with  [Y] (where X is a door/chest and Y is a key),
#   give [X] to    [Y] (where X is an object and Y is a person),
#   take [X] of    [Y] (where X is a number and Y is an object),

# Variant with color/adjective
#   put  [C] [X] in/on    [Y] (where X is an object and Y is receptacle/container, where is C is a color/adjective),
#   open     [X] with [C] [Y] (where X is a door/chest and Y is a key, where is C is a color/adjective),
#   give [C] [X] to       [Y] (where X is an object and Y is a person, where is C is a color/adjective),
#   take     [X] of   [C] [Y] (where X is a number and Y is an object, where is C is a color/adjective),


# Store selling keys
# Store selling color paint

  # We get an instruction in an alien language
  # e.g. You need the blue key to unlock the door.
  # e.g. Open/close chest/door
  # e.g. lock/unlock chest/door with color key
  # e.g. give water/object to someone
  # Open/close is learned from flipping a lever and hearing a click, need to go and see the outcome.

## How to learn numbers
We have a flag pole, a counting computer, and several programs on different floppy disks.
When the agent use the computer with a floppy disk, the flagpole will raise a flag according to the value contained within the program.
The flagpole cannot be raised higher than a predetermined height (5 at the momen).
We have a special program that resets the flagpole to 0.
The floppy disks label represent the number they contain.

## How to learn people's names
We have multiple house with a doorbell. We can press the doorbell to hear the name of the person living in that house.
Maybe we could have a house with twins.

## How to learn object names
We have many different shops that display different projects with a sign next to it with their name.
We could have a single supertmarket to display all the products.


## How to learn the "give" and "take/receive" concept
In the shops/supermarket/mall we could have a sign with emojis showing:
  - Give: [money] -> [vendor]
  - Put: [money] -> [chest]
  - Receive: [product] -> [you]

## How to learn the "put" and "open" concept
We could have a chest with a sign showing:
  - Open: [chest] with [key]
  - Put: [object] in [chest]

## How to learn the "color" concept
We could have a shop selling paint with a sign showing:
  - [color] paint
We could have a color wheel with the name of all the colors written on it. (this let you know that the word is a color or not)
Paint cans be used to paint some objects (e.g., keys)

## How to learn the "number" concept
We could have address with a numbers on it.
We could have a map of the village with the houses number and people names on it. (this let you know that the word is a number or a person's name).


# Random thoughts
 - Agent should start with some money to limit brute force.



# TODO
- [ ] Use "v" logbook to log the conversation you had so far.
- [ ] How to keep track of the words learned?
- [X] When facing up at the top border of the map, we don't see items to be picked up.
- [X] In the key shop, use pile of keys to display.
- [X] Remove black items?
- [X] Randomize the placement of multiple objects on a same table (to avoid items overlapping).
- [X] Change name of the key in general store to remove "rusted"
- [X] Use count and color and the taskscorer
- [X] Add flower and mushrom to the general store to display their name.
- [X] Add color keys.
- [X] Add color flowers.
- [X] Add color mushrooms.
- [X] Randomize the color.
- [X] Randomize the count.
- [X] Add NPC to give the agent a task.
- [X] Implement TaskScorer
- [X] Add a top ball to the flagpole.
- [X] Init the flagpole at the 4th position to force the use of the reset card.
- [X] Find how to teach "bring me" concept.
- [X] Add NPCs playing with their dogs They throw a stick, they shout out the alien word for "bring me", and the dog brings it back to them.
  - [X] Add NPC
  - [X] Add dog
  - [X] Add stick
  - [X] Add throwing stick routine
  - [X] Add shouting "bring me" routine
  - [X] Add dog fetching stick routine

# Abandonned
- [ ] Use Measuring tape on flag or vice-versa?
- [ ] Player needs to pay to get items?
- [ ] Elder message upong bringing valid/invalid item.


## Tasks
### Simple.
 - Bring me key.
 - Bring me flower.
 - Bring me mushroom.

### Medium.
 - Bring me color key.
 - Bring me color flower.
 - Bring me color mushroom.

 - Bring me number key.
 - Bring me number flower.
 - Bring me number mushroom.

### Hard.
 - Bring me number color key.
 - Bring me number color flower.
 - Bring me number color mushroom.


# Long-term TODO
- [ ] Add vendor to the shop
- [ ] Before taking an object in the shop, you should give money to vendor
- [ ] Create a map of the village
- [ ] Create a list of people's name
- [ ] Create a list of object's name
- [ ] Create a list of color's name
- [ ] Create a list of number's name
- [ ] Create a list of shop's name
- [ ] Add color wheel and add it somewhere in the village (e.g., in the shop selling paint)





# Extensions

Creating a 2D grid game with a language-learning element sounds fascinating! Here are some ideas to help players discover the meaning of an alien word that represents “bringing something to a person”:

Pictorial Clues: Scatter images throughout the game that visually represent the action of bringing something. Players can match the alien word with the action shown in the pictures.
Contextual Learning: Introduce NPCs (non-player characters) who use the alien word in various contexts where the action of bringing something is happening, helping players infer the meaning through repeated exposure.
Mini-Games: Design mini-games or puzzles where the player must bring items to NPCs to proceed or gain rewards. The alien word could be prominently displayed as part of these interactions.
Word Construction: Break down the alien word into syllables or components that the player can collect. Each part could be associated with a part of the action, teaching the word’s meaning as they assemble it.
Dialogue Choices: Give players dialogue options that include the alien word. The consequences of their choices can help them understand the word’s meaning based on NPCs’ reactions.
Gesture-Based Learning: Implement a feature where the player character makes a gesture associated with the word, like extending a hand out to give something, which is then labeled with the alien word.
Language Database: Create an in-game dictionary or database where players can reference words they’ve encountered, complete with definitions and usage examples.
Cultural Artifacts: Introduce artifacts or inscriptions in the alien language that relate to the concept of giving or bringing, which players can translate.
Audio Cues: Use distinct audio cues or voice-overs in the alien language when the action of bringing something occurs, reinforcing the word’s meaning.
Story Integration: Weave the concept into the game’s storyline, where understanding this word might be key to progressing or unlocking a mystery.
Remember, the key to teaching a new language in a game is repetition, context, and engagement. Good luck with your game development! 🚀


Here are some additional concepts you could teach in your 2D grid game with an alien language:

Navigation: Words for directions (left, right, up, down) and landmarks (mountain, river, building).
Numbers: Teach counting, quantities, and perhaps even basic arithmetic.
Colors: Introduce a spectrum of colors and associate them with various objects in the game.
Emotions: Use facial expressions or actions of characters to convey different emotions.
Time: Concepts of time such as day, night, past, present, and future.
Weather: Terms for different weather conditions like sunny, rainy, or snowy.
Family: Words for family members and social relationships.
Food and Drink: Names of common food items and drinks, along with actions like eating and drinking.
Clothing: Various clothing items and accessories.
Nature: Flora and fauna names, along with verbs related to interaction with nature (like grow, bloom, fly).
Each concept can be introduced through interactive elements, puzzles, and story-driven content to make the learning process engaging and intuitive.




# How to build a rocket (it's not rocket science...).

### Unknown variables
- Gravity
- Air resistance
- Fuel energy output

### Controllable variables
- Thrust
- Fuel source
- Angle of launch

### Target variables
- Orbit distance from planet
- Orbital speed


## Small experiments to figure out the unknown variables
- Drop a ball from different heights to measure gravity.
  - Or we keep the same constant G but we have to figure out the mass of the planet.
- Drop a feather and a ball to measure air resistance.
- Burn different fuels to measure energy output.

## Bigger experiments to figure out the optimal launch parameters to reach orbit
- Launch a rocket at different angles to measure the optimal angle for orbit.
- Launch a rocket with different fuel sources to measure the optimal fuel source for orbit.
- Launch a rocket with different thrust to measure the optimal thrust for orbit.

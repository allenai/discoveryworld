# Pathfinding.py

from Layer import Layer

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder



class Pathfinder():
    # Constructor
    def __init__(self):
        pass

    # Find a path
    def findPathNextStep(self, world, startX, startY, endX, endY):

        # Step 1: Construct a cost grid representing the world, where each cell contains whether it's passable or not
        costGrid = []
        for y in range(world.sizeY):
            costGrid.append([])
            for x in range(world.sizeX):

                # By default, moving to the next cell has a base cost of 1
                passableScore = 1

                # Check if the cell is passable
                allObjs = world.getObjectsAt(x, y)

                # Check if any of the objects are impassable
                for object in allObjs:
                    if (not object.attributes["isPassable"]):
                        # Check to see if the object is a door, and therefore potentially passable
                        if (object.attributes["isPassage"]):
                            # Potentially passable, with a cost
                            passableScore = 20
                        else:
                            # Not passable (score of -1)
                            passableScore = -1

                        break
                # If this tile has any agents in it, increase its traversal cost
                if (passableScore > 0):
                    if (len(world.grid[x][y]["layers"][Layer.AGENT]) > 0):
                        passableScore += 10


                # Store the passability score
                costGrid[y].append(passableScore)

        # Step 2: Find a path using A*
        print("Finding path from (" + str(startX) + ", " + str(startY) + ") to (" + str(endX) + ", " + str(endY) + ")")
        
        # Use A* library to find a path
        grid = Grid(matrix=costGrid)

        start = grid.node(startX, startY)
        end = grid.node(endX, endY)

        finder = AStarFinder(diagonal_movement=DiagonalMovement.never)
        path, runs = finder.find_path(start, end, grid)

        #print('operations:', runs, 'path length:', len(path))
        #print(grid.grid_str(path=path, start=start, end=end))

        # Get the next step in the path
        if (len(path) > 1):
            nextX = path[1].x
            nextY = path[1].y
            return (True, nextX, nextY)
        else:
            return (False, -1, -1)
        
        
        




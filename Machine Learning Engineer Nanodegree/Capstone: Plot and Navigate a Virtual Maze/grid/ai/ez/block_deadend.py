# Copyright (C) 2016 - Srikanth Pagadala, Conscious Computing
# email: srikanth.pagadala@gmail.com

import random

from grid.ai.abstract_ai import AbstractAI

class BlockDeadend(AbstractAI):
    '''
    This algorithm is similar to Random Turn, except that any dead ends are remembered and a virtual 
    wall is placed at the opening so that the robot does not re-enter. The big idea here is that once 
    we start blocking dead ends, eventually only the correct ways from start to finish will remain 
    unblocked.  
    '''
    
    def __init__(self, maze_model, loc, heading, ui):
        '''
        Initialize the AI module
        
        @param maze_model: instance of maze_model class
        @type maze_model: grid.ai.model.maze_model.MazeModel
        @param loc: start location of the robot
        @type loc: [0, 0]. Array of len 2 specifying x and y coordinates of robot
        @param heading: initial heading direction of the robot. Up
        @type heading: one of the strings 'up', 'right', 'down', left'
        @param ui: handle to instance of ui class
        @type ui: slam_ui.SlamUi
        '''
        
        self.dead_end = []
        super(BlockDeadend, self).__init__(maze_model, loc, heading, ui)
        
    def title(self):
        '''
        Name of the AI algorithm that will be shown as title on UI screen 
        '''
        return "BLOCK DEADEND"
    
    def canReset(self):
        '''
        Return whether AI algorithm is ready to reset. Block Deadend algo resets when robot has reached center.
        '''
        return self.hasReachedCenter

    def currentPathDrawTail(self):
        '''
        Specify whether to show turtle tail. Block Deadend does not show tail for current path
        '''
        return False

    # look for bias
    def getBestDirection(self, sensors):
        '''
        Return the best next direction based on sensor data. Function is biased towards taking goalroom cell and unexplored cells.
        Otherwise it will pick a random direction from the set of possible openings from the current cell.
        
        @param sensors: Sensor inputs are a list of three distances from the robot's left, front, and right-facing sensors, in that order.
        @type sensors: array containing three distances from three walls.
        '''
        
        goalRoomOpenings = []
        unExploredOpenings = []
        openings = []
        
        for i, reading in enumerate(sensors):
            if reading > 0:
                
                opening = self.dir_sensors[self.heading][i]
                
                next_cell = self.maze_model.findNeighbor([self.x, self.y], opening)
                if not next_cell in self.dead_end:
                    
                    if self.isGoalRoomCell(next_cell):
                        goalRoomOpenings.append(opening)
                    
                    openings.append(opening)
                    
                    hasExplored = self.maze_model.explored[next_cell[1]][next_cell[0]]
                    if not hasExplored:
                        unExploredOpenings.append(opening)
                else:
                    print "Skipped Deadend at ", next_cell

        if goalRoomOpenings:
            bestDirection = random.choice(goalRoomOpenings)
        elif unExploredOpenings:            
            bestDirection = random.choice(unExploredOpenings)
        elif openings:
            bestDirection = random.choice(openings)     
        else:
            bestDirection =  self.dir_reverse[self.heading] # go reverse

            loc = [self.x, self.y]
            if loc != [0, 0]: # don't block your start pos
                self.maze_model.setWall(loc, bestDirection, 0)
                self.signalUi({'command': 'block-deadend', 'loc': loc, 'block_direction': bestDirection.value})
                self.dead_end.append(loc)
            else:
                print "Safely didn't block my start pos"


        return bestDirection
    

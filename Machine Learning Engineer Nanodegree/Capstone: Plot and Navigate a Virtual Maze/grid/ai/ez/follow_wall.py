# Copyright (C) 2016 - Srikanth Pagadala, Conscious Computing
# email: srikanth.pagadala@gmail.com

import random

from grid.ai.abstract_ai import AbstractAI
from grid.model.maze_model import Direction


class FollowWall(AbstractAI):
    '''
    The wall follower, the best-known rule for traversing mazes, is also known as either 
    the left-hand rule or the right-hand rule. If the maze is simply connected, that is, 
    all its walls are connected together or to the maze's outer boundary, then by keeping 
    one hand in contact with one wall of the maze the solver is guaranteed not to get lost 
    and will reach a different exit if there is one; otherwise, he or she will return to 
    the entrance having traversed every corridor next to that connected section of walls 
    at least once.
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
        
        self.follow_wall = random.choice([Direction.Left, Direction.Right])
        super(FollowWall, self).__init__(maze_model, loc, heading, ui)

    def title(self):
        '''
        Name of the AI algorithm that will be shown as title on UI screen 
        '''
        return "FOLLOW WALL"
    
    def canReset(self):
        '''
        Return whether AI algorithm is ready to reset. Follow Wall can never reset, as it never reaches the center.
        '''
        
        if self.x == 0 and self.y == 0:
            loc = [0, 0]
            walls = [Direction.Down.value]
            self.maze_model.setWall(loc, Direction.Down, 0)
            self.signalUi({'command': 'cell-explored', 'loc': loc, 'walls': walls})
            self.signalUi({'command': 'erase-path-current' })
            self.signalUi({'command': 'draw-path-current', 'path_current': ([0, 0], 90, self.heading.value) })
            
            self.follow_wall = random.choice([Direction.Left, Direction.Right])
            
        return False
           
    def currentPathDrawTail(self):
        '''
        Specify whether to show turtle tail. Follow Wall shows tail for current path
        '''
        return True
 
    # look for bias
    def getBestDirection(self, sensors):
        '''
        Return the best next direction based on sensor data. In Follow Wall, robot simply grazes along the outer wall of the maze.
        
        @param sensors: Sensor inputs are a list of three distances from the robot's left, front, and right-facing sensors, in that order.
        @type sensors: array containing three distances from three walls.
        '''
        
        my_right = self.dir_right[self.heading]
        my_left = self.dir_left[self.heading]
        
        openings = []
        for i, reading in enumerate(sensors):
            if reading > 0:
                opening = self.dir_sensors[self.heading][i]
                openings.append(opening)
        
        # no choice turn
        if len(openings) == 0:
            return self.dir_reverse[self.heading]  # go reverse
        
        # preferred turn
        if self.follow_wall == Direction.Right:
            if my_right in openings:
                return my_right
        
        # preferred turn
        if self.follow_wall == Direction.Left:
            if my_left in openings:
                return my_left
            
        # default turns
        if self.heading in openings:
            return self.heading
        else:
            return my_left if (self.follow_wall == Direction.Right) else my_right
            
        

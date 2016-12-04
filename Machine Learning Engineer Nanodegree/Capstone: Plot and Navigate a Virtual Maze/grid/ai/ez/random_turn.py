# Copyright (C) 2016 - Srikanth Pagadala, Conscious Computing
# email: srikanth.pagadala@gmail.com

from grid.ai.abstract_ai import AbstractAI


class RandomTurn(AbstractAI):
    '''
    This is a trivial method that can be implemented by a very unintelligent robot. At each 
    step of the way, robot randomly picks a direction to proceed, with slight bias toward 
    'unexplored' cells. At a dead end, it turns around. Although such a method would always 
    eventually find a solution, this algorithm can be extremely slow. 
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
        
        super(RandomTurn, self).__init__(maze_model, loc, heading, ui)

    def title(self):
        '''
        Name of the AI algorithm that will be shown as title on UI screen 
        '''
        return "RANDOM TURN"
    
    def canReset(self):
        '''
        Return whether AI algorithm is ready to reset. Random Turn algo resets when robot has reached center.
        '''
        return self.hasReachedCenter

    def currentPathDrawTail(self):
        '''
        Specify whether to show turtle tail. Random Turn does not show tail for current path
        '''
        return False


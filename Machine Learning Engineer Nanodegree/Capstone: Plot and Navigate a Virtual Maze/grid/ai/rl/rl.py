# Copyright (C) 2016 - Srikanth Pagadala, Conscious Computing
# email: srikanth.pagadala@gmail.com

from grid.ai.abstract_ai import AbstractAI


class ReinforcementLearning(AbstractAI):
    '''
    Parent class of all reinforcement learning AI implementations. Carries the bulk of the logic 
    and taps into concrete sub class implementation (ValueIteration, QLearning) 
    for AI specific interpretation at relevant points in the flow.
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
        
        super(ReinforcementLearning, self).__init__(maze_model, loc, heading, ui)

    def nextMove(self, sensors):
        '''
        Return the next best movement and rotation based on the AI algorithm's best guess provided sensors information.
        
        @param sensors: Sensor inputs are a list of three distances from the robot's left, front, and right-facing sensors, in that order.
        @type sensors: array containing three distances from three walls.
        '''
        
        if self.maze_explored == True:
            nextDirection = self.agent.getPolicy((self.x, self.y))
            ret = self.nextStep(nextDirection)
            self.setStatus("run = {}, step = {}".format(self.run, self.run_count))
            return ret
        else:
            return self.exploreMaze(sensors)
        
    def canReset(self):
        '''
        Return whether AI algorithm is ready to reset. RL resets when robot has reached center 
        and atleast once and 80% of maze has been explored.
        '''
        return self.hasReachedCenter and self.percentExplored() >= 80.0
            
    def currentPathDrawTail(self):
        '''
        Specify whether to show turtle tail. RL does not show tail for current path
        '''
        return False

    def drawRecentPath(self):
        '''
        Specify whether to show the recent traversed path (GREEN line). RL shows 
        recent path only for run=2 (exploitation run).
        '''
        if self.run > 0:
            return True
        else:
            return False


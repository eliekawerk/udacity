# Copyright (C) 2016 - Srikanth Pagadala, Conscious Computing
# email: srikanth.pagadala@gmail.com

import path

from grid.ai.abstract_ai import AbstractAI
from grid.model.maze_model import Direction

class GraphSearch(AbstractAI):
    '''
    Parent class of all graph search AI implementations. Carries the bulk of the logic 
    and taps into concrete sub class implementation (dfs, bfs, ucs, A*) 
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
        
        self.searched_path = None
        
        super(GraphSearch, self).__init__(maze_model, loc, heading, ui)

    def nextMove(self, sensors):
        '''
        Return the next best movement and rotation based on the AI algorithm's best guess provided sensors information.
        
        @param sensors: Sensor inputs are a list of three distances from the robot's left, front, and right-facing sensors, in that order.
        @type sensors: array containing three distances from three walls.
        '''
        
        if self.maze_explored:
            nextDirection = self.searched_path.pop(0)
            ret = self.nextStep(nextDirection)
            self.setStatus("run = {}, step = {}".format(self.run, self.run_count))
            return ret
        else:
            return self.exploreMaze(sensors)
        
    def canReset(self):
        '''
        Return whether AI algorithm is ready to reset. Graph Search resets when robot has reached center 
        and atleast once and 80% of maze has been explored.
        '''
        return self.hasReachedCenter and self.percentExplored() >= 80.0
            
    def currentPathDrawTail(self):
        '''
        Specify whether to show turtle tail. Graph Search does not show tail for current path
        '''
        return False

    def drawRecentPath(self):
        '''
        Specify whether to show the recent traversed path (GREEN line). Graph Search shows 
        recent path only for run=2 (exploitation run).
        '''
        if self.run > 0:
            return True
        else:
            return False

    def graphSearch(self, problem, frontier):
        '''
        Perform the graph search DFS BFS UCS or A* based on the injected fringe implementation.
        
        @param problem: given PositionSearchProblem instance
        @type problem: grid.ai.gs.graph_search.PositionSearchProblem
        @param frontier: injected fringe impl
        @type frontier: grid.util.util.Stack or grid.util.util.PriorityQueue
        '''
        
        # print "Start:", problem.getStartState()
        # print "Is the start a goal?", problem.isGoalState(problem.getStartState())
        # print "Start's successors:", problem.getSuccessors(problem.getStartState())
        
        self.setStatus("Exploration complete. Starting Graph search")
        
        explored = []
        frontier.push([(problem.getStartState(), Direction.Up , 0)])
        
        while not frontier.isEmpty():
            path = frontier.pop()
            
            s = path[-1]
            s = s[0]
            if problem.isGoalState(s):
                self.setStatus("Graph search complete")
                return [x[1] for x in path][1:]
                
            if s not in explored:
                explored.append(s)
                
                for successor in problem.getSuccessors(s):
                    if successor[0] not in explored:
                        successorPath = path[:]
                        successorPath.append(successor)
                        frontier.push(successorPath)
    
        return []   
    
class PositionSearchProblem():
    """
    A search problem defines the state space, start state, goal test, successor
    function and cost function.  This search problem can be used to find paths
    to a particular point in the maze.The state space consists of (x,y) positions 
    in a pacman game.
    """

    def __init__(self, maze_model, start=[0, 0], goal=[100, 100], costFn=lambda x: 1):
        '''
        Stores the start and goal.
        
        @param maze_model:
        @type maze_model:
        @param start: Start position in the maze
        @type start: [0, 0], python array
        @param goal: Goal position in the maze
        @type goal: [6, 6], python array
        @param costFn: A function from a search state (tuple) to a non-negative number
        @type costFn: python function
        '''
        
        self.maze_model = maze_model
        self.start = start
        self.goal = goal
        self.costFn = costFn

    def getStartState(self):
        '''
        Return the start location in the maze
        '''
        
        return self.start

    def isGoalState(self, state):
        '''
        Return whether given location is the goal cell
        
        @param state: given cell
        @type state: [6, 6], python array
        '''
        
        isGoal = state == self.goal
        return isGoal

    def getSuccessors(self, state):
        '''
        Returns successor states, the actions they require, and a cost of 1. For a given state, 
        this should return a list of triples, (successor, action, stepCost), where 
        'successor' is a successor to the current state, 'action' is the action required to 
        get there, and 'stepCost' is the incremental cost of expanding to that successor
        
        @param state: given cell
        @type state: [6, 6], python array
        '''
        
        successors = []
        for direction in list(Direction):
            x, y = state
            if not self.maze_model.hasWall([x, y], direction):
                nextState = self.maze_model.findNeighbor([x, y], direction)
                cost = self.costFn(nextState)
                successors.append((nextState, direction, cost))

        return successors

    def getCostOfActions(self, directions):
        '''
        Returns the cost of a particular sequence of actions. If those actions
        include an illegal move, return 999999.
        
        @param directions: possible open directions
        @type directions: python array of grid.model.maze_model.Direction
        '''
        
        if directions == None: return 999999
        x, y = self.getStartState()
        cost = 0
        for direction in directions:
            # Check figure out the next state and see whether its' legal
            if self.maze_model.hasWall([x, y], direction): return 999999
            cost += self.costFn((x, y))
        return cost


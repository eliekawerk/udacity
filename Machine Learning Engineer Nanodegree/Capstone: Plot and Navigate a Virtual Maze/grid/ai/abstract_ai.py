# Copyright (C) 2016 - Srikanth Pagadala, Conscious Computing
# email: srikanth.pagadala@gmail.com

from abc import ABCMeta
import random
import sys

from grid.model.maze_model import Direction

class AbstractAI:
    '''
    AbstractAI is the parent class of all the AI implementations. Carries the bulk of the logic 
    and taps into each AI implementation for AI specific interpretation at relevant points in the flow.
    '''

    __metaclass__ = ABCMeta

    BIG_NUM = sys.maxint
    
    # current tester run number. Values can be 1 or 2
    run = 0
    
    # movement counters
    run_count = 0 # num of movements in current run
    count_center = 0 # num of movements towards center goal from start loc
    count_start = 0 # num of movements towards start loc from goal loc
    
    # array of path coordinates
    path_first = [([0, 0], 90, 0)]  # starts at 0,0 facing up
    path_current = [([0, 0], 90, 0)]  # starts at 0,0 facing up
    path_best = []
    
    # flag indicating whether robot has reached center goal atleast once
    path_first_recorded = False
    
    # maps for various types of direction lookup
    heading_convert = {'up': Direction.Up, 'right': Direction.Right, 'down': Direction.Down, 'left': Direction.Left}
    
    dir_right = { 
        Direction.Up : Direction.Right,
        Direction.Right : Direction.Down,
        Direction.Down : Direction.Left,
        Direction.Left : Direction.Up }
    
    dir_left = { 
        Direction.Up : Direction.Left,
        Direction.Right : Direction.Up,
        Direction.Down : Direction.Right,
        Direction.Left : Direction.Down }
    
    dir_reverse = {
        Direction.Up : Direction.Down,
        Direction.Right : Direction.Left,
        Direction.Down : Direction.Up,
        Direction.Left : Direction.Right }
    
    dir_sensors = {
        Direction.Up: [Direction.Left, Direction.Up, Direction.Right],
        Direction.Right: [Direction.Up, Direction.Right, Direction.Down],
        Direction.Down: [Direction.Right, Direction.Down, Direction.Left],
        Direction.Left: [Direction.Down, Direction.Left, Direction.Up]}


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
        
        self.maze_model = maze_model
        self.dim = maze_model.dim
        self.ui = ui
        
        # usually starts at [0, 0]
        self.x = loc[0]
        self.y = loc[1]
        
        self.heading = self.heading_convert[heading]  # 'up', 'right', 'down', left'
        
        self.goal = "CENTER"  # can be CENTER or START
        self.hasReachedCenter = False
        self.maze_explored = False
        self.goalLoc = [0, 0]  # will change to something more correct
        
        self.setTitle(self.title())
        self.signalUi({'command': 'draw-path-current', 'path_current': self.path_current[0], 'draw_tail': self.currentPathDrawTail() })

    def title(self):
        '''
        Name of the AI algorithm that will be shown as title on UI screen 
        '''
        pass

    def nextMove(self, sensors):
        '''
        Return the next best movement and rotation based on the AI algorithm's best guess provided sensors information.
        
        @param sensors: Sensor inputs are a list of three distances from the robot's left, front, and right-facing sensors, in that order.
        @type sensors: array containing three distances from three walls.
        '''
        return self.exploreMaze(sensors)
    
    def exploreMaze(self, sensors):
        '''
        Robot explores the maze randomly or based on some Heuristics. This function is called only during run=1. 
        
        @param sensors: Sensor inputs are a list of three distances from the robot's left, front, and right-facing sensors, in that order.
        @type sensors: array containing three distances from three walls.
        '''

        if self.run == 0:
            self.setStatus("Exploring maze. run = {}, step = {}".format(self.run, self.run_count))
        else:
            self.setStatus("run = {}, step = {}".format(self.run, self.run_count))
        
        if (not self.hasExplored()):
            self.setWalls(sensors);
            self.markExplored()
        
        if self.hasReachedGoal(): self.onReachedGoal()
        
        if self.canReset(): return self.onReset()
            
        nextDirection = self.getBestDirection(sensors)
        return self.nextStep(nextDirection)
    
    def beforeReset(self):
        '''
        A callback function that gives AI algorithm an opportunity to perform any last minute 
        calculations before sending (reset, reset) signal to Tester.
        '''
        pass
    
    def onReset(self):
        '''
        This function is invoked when AI algorithm has sufficiently explored the maze in run=1.
        After some state re initialization, Robot sends reset signal to Tester
        '''
        if self.run == 0:
            
            self.beforeReset()
            
            self.run += 1
            self.x = 0
            self.y = 0
            self.heading = Direction.Up
            self.rotation = 90
            self.goal = "CENTER"
            self.path_current = [([self.x, self.y], self.rotation, self.heading.value)]
            self.maze_explored = True
            self.hasReachedCenter = False
            self.run_count = 0
            
            self.setStatus("Exploration complete. Resetting tester.")
            
            return ('Reset', 'Reset')
    
    def nextStep(self, nextDirection):
        '''
        Compute the (rotation, movement) tuple for Tester from the next best direction that was produced by AI algorithm.
        
        @param nextDirection: Next best direction computed by AI algorithm
        @type nextDirection: grid.model.maze_model.Direction
        '''
        
        if (nextDirection == self.dir_reverse[self.heading]):
            self.rotation = 90
            self.movement = 0
            self.heading = self.dir_right[self.heading]
        else:
            if (nextDirection == self.heading):
                self.rotation = 0
                self.movement = 1
            elif (nextDirection == self.dir_right[self.heading]):
                self.rotation = 90
                self.movement = 1
            elif (nextDirection == self.dir_left[self.heading]):
                self.rotation = -90
                self.movement = 1
                    
            next_cell = self.maze_model.findNeighbor([self.x, self.y], nextDirection)
            self.x = next_cell[0]
            self.y = next_cell[1]
            self.heading = nextDirection
            
        # increment run counters
        self.incrementCounters()
        self.drawRunPaths()
        
        return (self.rotation, self.movement)
    
    def incrementCounters(self):
        '''
        Keep track of number of movements from start to goal and goal to start. Shown as nice status message on ui.
        '''
        
        self.run_count += 1
        
        path_current = ([self.x, self.y], self.rotation, self.heading.value)

        if not self.path_first_recorded:
            self.path_first.append(path_current)
        
        self.path_current.append(path_current)
        self.signalUi({'command': 'draw-path-current', 'path_current': path_current, 'draw_tail': self.currentPathDrawTail() })

    def currentPathDrawTail(self):
        '''
        Specify whether to show turtle tail. By default tail is not shown in exploration mode (run=1)
        '''
        if self.run > 0:
            return True
        else:
            return False
        
    def drawFirstPath(self):
        '''
        Specify whether to show the first traversed path (BLUE line). By default first path is not shown as it is not applicable 
        for most of the AI algorithm, except for FloodFill
        '''
        return False
    
    def drawBestPath(self):
        '''
        Specify whether to show the best traversed path (RED line). By default best path is not shown as it is not applicable 
        for most of the AI algorithm, except for FloodFill
        '''
        return False
    
    def drawRecentPath(self):
        '''
        Specify whether to show the recent traversed path (GREEN line). By default recent path is shown as it is applicable 
        for all the AI algorithm
        '''
        return True
    
    def pathRecentXyOffset(self):
        '''
        Return the xy offset of the path line in cell. 0.5 means, line will appear right in the middle.
        '''
        
        return 0.5
        
    def drawRunPaths(self):
        '''
        Draw First, Best, Current and Resent paths, as needed
        '''
        
        if self.hasReachedGoal():
            
            # display path_first
            if not self.path_first_recorded:
                self.path_first_recorded = True
                if self.drawFirstPath(): self.signalUi({'command': 'draw-path-first', 'path_first': self.path_first})
            
            # display path_best
            if len(self.path_best) == 0 or len(self.path_current) < len(self.path_best):
                self.path_best = self.path_current
                if self.drawBestPath(): self.signalUi({'command': 'draw-path-best', 'path_best': self.path_best})
                
            # display path_recent
            self.signalUi({'command': 'erase-path-current'})
            if self.drawRecentPath(): self.signalUi({'command': 'draw-path-recent', 'path_recent': self.path_current, 'xy_offset': self.pathRecentXyOffset()})
            self.path_current = [([self.x, self.y], self.rotation, self.heading.value)]

    def hasReachedGoal(self):
        '''
        Return true of the robot has reached any of the 4 goal rooms
        '''
        
        if (self.goal == "CENTER") and \
           (self.x == self.dim / 2 or self.x == self.dim / 2 - 1) and \
           (self.y == self.dim / 2 or self.y == self.dim / 2 - 1):
            return True
        elif self.goal == "START" and self.x == 0 and self.y == 0:
            return True
        else:
            return False
    
    def onReachedGoal(self):
        '''
        Function that gets called back when Robot reaches the center. Gives an opportunity to AI algorithm to do 
        any specific task on reaching the goal cell. By default goalLoc is noted and goalRoom walls are drawn.
        '''
        
        if self.goal == "CENTER":
            self.hasReachedCenter = True
            self.goalLoc = [self.x, self.y]
            self.maze_model.markGoalRoom([self.x, self.y])

    def setWalls(self, sensors):
        '''
        Set wall information of the current cell as provided by sensors
        
        @param sensors: Sensor inputs are a list of three distances from the robot's left, front, and right-facing sensors, in that order.
        @type sensors: array containing three distances from three walls.
        '''
        
        self.maze_model.setWalls([self.x, self.y], self.heading, sensors)
        
    def hasExplored(self):
        '''
        Return whether current has been already explored
        '''
        
        return self.maze_model.hasExplored([self.x, self.y])
        
    def markExplored(self):
        '''
        Mark a given cell as explored
        '''
        
        return self.maze_model.markExplored([self.x, self.y])
    
    def percentExplored(self):
        '''
        Return the percentage of cells that have been explored. Is used to determine if maze has been explored enough?
        '''
        
        s = sum(map(sum, self.maze_model.explored))
        t = self.dim * self.dim
        return s / float(t) * 100

    def setTitle(self, title):
        '''
        Title to be shown on ui
        @param title: title string
        @type title: python string
        '''
        
        args = {}
        args['command'] = 'write-title'
        args['line'] = title
        self.signalUi(args)
    
    def setStatus(self, status):
        '''
        Status string to be shown on ui
        @param status: status string
        @type status: python string
        '''
        
        args = {}
        args['command'] = 'write-status'
        args['line'] = status
        self.signalUi(args)
        
    # update ui
    def signalUi(self, args):
        '''
        Send a render command to UI. 
        
        @param args: dictionary of parameters that UI can use. Eg: coordinates of current path is sent to render current path.
        @type args: python dictionary
        '''
        
        self.ui.stdin.write(str(args) + "\n")
        response = self.ui.stdout.readline()
        # print response # debug

    # extra optimization
    def isGoalRoomCell(self, loc):
        '''
        Return true of the given cell location is one of the four goal room cells.
        @param loc: current location of the robot
        @type loc: [8, 9]. Array of len 2 specifying x and y coordinates of robot
        '''
        
        goal_bounds = [self.maze_model.dim / 2 - 1, self.maze_model.dim / 2]
        if loc[0] in goal_bounds and loc[1] in goal_bounds:
            return True
        else:
            return False
        
    # look for bias
    def getBestDirection(self, sensors):
        '''
        Return the best next direction based on sensor data. Function is biased towards taking goalroom cell and unexplored cells.
        Otherwise it will pick a random direction from the set of possible openings from the current cell.
        
        @param sensors: Sensor inputs are a list of three distances from the robot's left, front, and right-facing sensors, in that order.
        @type sensors: array containing three distances from three walls.
        '''
        
        bestDirection = None
        
        goalRoomOpenings = []
        unExploredOpenings = []
        openings = []
        
        for i, reading in enumerate(sensors):
            if reading > 0:
                opening = self.dir_sensors[self.heading][i]
                
                # extra optimization
                neighbor = self.maze_model.findNeighbor([self.x, self.y], opening)
                if self.hasReachedCenter and self.isGoalRoomCell(neighbor):
                    continue
                
                openings.append(opening)
                
                if self.isGoalRoomCell(neighbor):
                    goalRoomOpenings.append(opening)
                
                hasExplored = self.maze_model.explored[neighbor[1]][neighbor[0]]
                if not hasExplored:
                    unExploredOpenings.append(opening)
         
        if goalRoomOpenings:
            bestDirection = random.choice(goalRoomOpenings)
        elif unExploredOpenings:            
            bestDirection = random.choice(unExploredOpenings)
        elif openings:
            bestDirection = random.choice(openings)
        else:
            bestDirection = self.dir_reverse[self.heading]  # go reverse
                
        return bestDirection

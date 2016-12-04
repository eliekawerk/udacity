# Copyright (C) 2016 - Srikanth Pagadala, Conscious Computing
# email: srikanth.pagadala@gmail.com

from grid.ai.abstract_ai import AbstractAI
from grid.model.maze_model import Direction


class FloodFill(AbstractAI):
    '''
    This algorithm is much more complex than the other algorithms. It involves an initial 
    assumption that there are no walls in the maze. A number is assigned to each cell. The 
    number corresponds to the distance to the goal. This algorithm has the advantage of 
    always finding the shortest path between start and finish. However, the shortest path 
    is only in terms of distance; depending on the number of turns and the associated time 
    to turn, the shortest path may not be the quickest. 
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
        
        self.dim = maze_model.dim
        self.depth = [[self.BIG_NUM for _ in range(self.dim)] for _ in range(self.dim)]
        
        super(FloodFill, self).__init__(maze_model, loc, heading, ui)

    def title(self):
        '''
        Name of the AI algorithm that will be shown as title on UI screen 
        '''
        return "FLOOD FILL"
    
    def setDepth(self, cell, depth):
        '''
        Set the flood fill depth for the given cell
        
        @param cell: given cell
        @type cell: [0, 0]. python array
        @param depth: flood fill depth
        @type depth: python int
        '''
        
        x = cell[0]
        y = cell[1]
        self.depth[y][x] = depth
      
    def getDepth(self, cell):  
        '''
        Return the flood fill depth of the given cell
        
        @param cell: given cell
        @type cell: [0, 0]. python array
        '''
        
        x = cell[0]
        y = cell[1]
        return self.depth[y][x]
        
    def floodfill(self):
        '''
        Flood fill the maze. The big idea here is that we imagine maze has a convex plane, 
        with goal at the bottom of plane and start cell at the top. Numbers on each cell 
        is in a way indicating how far higher each cell is compared to the goal cell. We now 
        imagine flooding the convex plane with some fluid and follow the path of the liquid 
        downstream to the goal cell. Following the algorithm strictly will improve the average 
        time to finish in any maze. This algorithm always works, and is not random - it is 
        systematic and predictable. 
        '''
        
        queue = []
        
        self.depth = [[FloodFill.BIG_NUM for _ in range(self.dim)] for _ in range(self.dim)]
        
        if self.goal == "START":
            
            start_cell = [0, 0]
            self.setDepth(start_cell, 0)
            queue.append(start_cell)
            
        else:
            
            center1 = [self.dim / 2 - 1, self.dim / 2]  # top-left cell in goal room
            center2 = [self.dim / 2, self.dim / 2]  # top-right cell in goal room
            center3 = [self.dim / 2, self.dim / 2 - 1]  # bottom-right cell in goal room
            center4 = [self.dim / 2 - 1, self.dim / 2 - 1]  # bottom-left cell in goal room
            
            self.setDepth(center1, 0)
            self.setDepth(center2, 0)
            self.setDepth(center3, 0)
            self.setDepth(center4, 0)
            
            queue.append(center1)
            queue.append(center2)
            queue.append(center3)
            queue.append(center4)
        
        while len(queue) > 0:
            
            cell = queue.pop(0)
            curr_depth = self.getDepth(cell)
            
            for direction in list(Direction):
                
                if (not self.maze_model.hasWall(cell, direction)):
                    
                    neighbor = self.maze_model.findNeighbor(cell, direction)
        
                    if neighbor:
                        neighbor_depth = self.getDepth(neighbor) 
                        
                        if (curr_depth + 1) < neighbor_depth:
                            queue.append(neighbor)
                            self.setDepth(neighbor, curr_depth + 1)
           
#        self.showDepths()

        # update ui
        self.signalUi({'command': 'depths-changed', 'depths': self.depth})
    
    def canReset(self):
        '''
        Return whether AI algorithm is ready to reset. Flood Fill algo resets when robot has reached center 
        and it has explored much of maze.
        '''
        return self.hasReachedCenter and self.count_center == self.count_start

    def currentPathDrawTail(self):
        '''
        Specify whether to show turtle tail. Flood Fill shows tail for current path
        '''
        return True
        
    def drawFirstPath(self):
        '''
        Specify whether to show first path. 
        '''
        return True
    
    def drawBestPath(self):
        '''
        Specify whether to show best path. 
        '''
        return True
    
    def pathRecentXyOffset(self):
        '''
        Return the xy offset of the path line in cell. 0.5 means, line will appear right in the middle. 
        None means UI will decide which offset is appropriate.
        '''
        return None

    def onReachedGoal(self):
        '''
        Function that gets called back when Robot reaches the center. Gives an opportunity to AI algorithm to do 
        any specific task on reaching the goal cell. By default goalLoc is noted and goalRoom walls are drawn.
        Flood Fill additionally re calculates the depths for each cell reverses its destination.
        '''
        
        if self.goal == "CENTER":
            self.hasReachedCenter = True
            self.maze_model.markGoalRoom([self.x, self.y])
        
        if self.goal == "CENTER":
            self.count_center = self.run_count
        else:
            self.count_start = self.run_count
            
        self.run_count = 0
        
        if self.count_center == self.count_start:
            return
        
        self.goal = "START" if self.goal == "CENTER" else "CENTER"
        self.floodfill()

    # look for bias
    def getBestDirection(self, sensors):
        '''
        Return the best next direction based on sensor data. Function follows the depths downstream.
        
        @param sensors: Sensor inputs are a list of three distances from the robot's left, front, and right-facing sensors, in that order.
        @type sensors: array containing three distances from three walls.
        '''
        
        # flood fill does not use 'sensors' here
        curr_cell = [self.x, self.y]
        bestDepth = self.getDepth(curr_cell)
        bestDirection = None
        
        for direction in list(Direction):
            
            if (not self.maze_model.hasWall(curr_cell, direction)):
                
                neighbor = self.maze_model.findNeighbor(curr_cell, direction)
                neighbor_depth = self.getDepth(neighbor) if neighbor else FloodFill.BIG_NUM
            
                if bestDepth > neighbor_depth:
                    bestDirection = direction;
                    bestDepth = neighbor_depth
        
        if not bestDirection:
            self.floodfill()
            return self.getBestDirection(sensors)
        else:
            return bestDirection

    def showDepths(self):
        '''
        Used for debugging. Prints maze depths data structure in robot coordinate system to console
        '''
        
        reverse_index = len(self.depth)
        while reverse_index > 0:
            row = self.depth[reverse_index - 1]
            print row  # keep it
            reverse_index -= 1
            

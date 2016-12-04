# Copyright (C) 2016 - Srikanth Pagadala, Conscious Computing
# email: srikanth.pagadala@gmail.com

from enum import Enum 

class Direction(Enum):
    '''
    Enum class of 4 cardinal directions
    '''
    Up = 0
    Right = 1
    Down = 2
    Left = 3
    
class MazeModel(object):
    '''
    Maze Model stores the 'state' of the maze (walls, explored cell etc). 
    '''
    
    dir_sensors = {
               Direction.Up: [Direction.Left, Direction.Up, Direction.Right],
               Direction.Right: [Direction.Up, Direction.Right, Direction.Down],
               Direction.Down: [Direction.Right, Direction.Down, Direction.Left],
               Direction.Left: [Direction.Down, Direction.Left, Direction.Up]}

    def __init__(self, maze_dim, ui, assumeOpenWalls=True):
        '''
        Initializing Maze Model
        
        @param maze_dim: dimension of the maze, usually 12x12 or 16x16
        @type maze_dim: int
        @param ui: handle to instance of ui class
        @type ui: slam_ui.SlamUi
        @param assumeOpenWalls: initialize model with open walls or not
        @type assumeOpenWalls: boolean
        '''
        
        self.dim = maze_dim
        self.ui = ui
        self.assumeOpenWalls = assumeOpenWalls
        
        self.explored = [[False for _ in range(self.dim)] for _ in range(self.dim)]
        
        '''
        Initializing the maze_walls 3d array 
        
        Typically array is of dimension: 16 x 16 x 4; which is of the form
        (maze_width x maze_height x 4-booleans for 4 walls of the cell)
        
        Sample value found in the 3rd dimension is: [0, 1, 1, 0] 
        where, each bit specifies which side of the cell is walled.
        where, wall values are stored from left-to-right in the order Up, Right, Down and Left
        where, 0 means Closed wall (walled)
        where, 1 means Open Wall (no wall)
        
        Initially, it is assumed that there are no walls in the maze. Hence all wall-bits for 
        all cells are initialized with 1 (no wall). As robot roams around in the maze and 
        senses walls, we will flip the appropriate bits in the array
        '''
        
        wallValue = 1 if (assumeOpenWalls == True) else 0
        self.maze_walls = [[[wallValue] * 4 for _ in range(maze_dim)] for _ in range(maze_dim)]
        
    # update maze model with newly discovered walls by robot sensors
    def setWalls(self, loc, heading, sensors):
        '''
        Set walls for the current location as detected by sensors
        
        @param loc: robot's current location
        @type loc: [x, y] array
        @param heading: robot's current heading. Up or Down or Left or Right
        @type heading: string
        @param sensors: Sensor inputs are a list of three distances from the robot's left, front, and right-facing sensors, in that order.
        @type sensors: array containing three distances from three walls.
        '''
        
        walls = []
        
        for i, reading in enumerate(sensors):
            wall = self.dir_sensors[heading][i]
            if reading == 0:  # ui wall
                walls.append(wall.value)

            if self.assumeOpenWalls and reading == 0:  # look for closed walls and flip appropriate bits
                self.setWall(loc, wall, 0)
            if not self.assumeOpenWalls and reading > 0:  # look for open walls and flip appropriate bits
                self.setWall(loc, wall, 1)
             
        self.signalUi({'command': 'cell-explored', 'loc': loc, 'walls': walls})
        
    def signalUi(self, args):
        '''
        Send a render command to UI. 
        
        @param args: dictionary of parameters that UI can use. Eg: coordinates of current path is sent to render current path.
        @type args: python dictionary
        '''
        
        self.ui.stdin.write(str(args) + "\n")
        response = self.ui.stdout.readline()
        # print response  # debug
                
    # set walls of the given cell and appropriate neighbors
    def setWall(self, loc, direction, wallValue):
        '''
        Set or open the wall for the given location
        
        @param loc: given location (cell)
        @type loc: [x, y] array 
        @param direction: Direction in which wall is to be set/opened. Up, Down, Right, Left
        @type direction: grid.model.maze_model.Direction
        @param wallValue: 0=closed wall, 1=open
        @type wallValue: int
        '''
        
        x = loc[0]
        y = loc[1]
        
        # set wall of the current cell
        self.maze_walls[y][x][direction.value] = wallValue
        
        # also set walls of neighboring cells appropriately - because neighbors share walls :)
        neighbor = self.findNeighbor(loc, direction)
        
        if neighbor:
            
            x = neighbor[0]
            y = neighbor[1]
            
            # set walls of neighbors
            if direction == Direction.Up:
                self.maze_walls[y][x][Direction.Down.value] = wallValue
            elif direction == Direction.Right:
                self.maze_walls[y][x][Direction.Left.value] = wallValue
            elif direction == Direction.Down:
                self.maze_walls[y][x][Direction.Up.value] = wallValue
            elif direction == Direction.Left:
                self.maze_walls[y][x][Direction.Right.value] = wallValue
    
    def hasWall(self, loc, direction):
        '''
        Return whether current location has a wall in the requested direction
        
        @param loc: current location (cell)
        @type loc: [x, y] array 
        @param direction: Direction in which wall is to be checked. Up, Down, Right, Left
        @type direction: grid.model.maze_model.Direction
        '''
        
        x = loc[0]
        y = loc[1]
        
        if direction == Direction.Up and (y == (self.dim - 1)):
            return True
        elif direction == Direction.Right and (x == (self.dim - 1)):
            return True
        elif direction == Direction.Down and (y == 0):
            return True
        elif direction == Direction.Left and (x == 0):
            return True
        else:
            return self.maze_walls[y][x][direction.value] == 0
        
    def findNeighbor(self, loc, direction):
        '''
        Return adjacent cell in the requested direction
        
        @param loc: current location (cell)
        @type loc: [x, y] array 
        @param direction: Direction in which neighbor is sought. Up, Down, Right, Left
        @type direction: grid.model.maze_model.Direction
        '''
        
        x = loc[0]
        y = loc[1]
        
        if direction == Direction.Up and (y != (self.dim - 1)):
            return [x, y + 1]
        elif direction == Direction.Right and (x != (self.dim - 1)):
            return [x + 1, y]
        elif direction == Direction.Down and (y != 0):
            return [x, y - 1]
        elif direction == Direction.Left and (x != 0):
            return [x - 1, y]
        else:
            return None
        

    def markGoalRoom(self, curr_cell):
        '''
        Goal Room consists of 4 cells in the middle of the maze. When robot reaches one of these 4
        cells, we automatically mark the other 3 cells and complete the goal room by drawing walls
        around it.
        
        @param curr_cell: goal room cell where robot has reached
        @type curr_cell: [6, 6] array
        '''
        
        center1 = [self.dim / 2 - 1, self.dim / 2]  # top-left cell in goal room
        center2 = [self.dim / 2, self.dim / 2]  # top-right cell in goal room
        center3 = [self.dim / 2, self.dim / 2 - 1]  # bottom-right cell in goal room
        center4 = [self.dim / 2 - 1, self.dim / 2 - 1]  # bottom-left cell in goal room
        
        if curr_cell != center1:
            self.setWall(center1, Direction.Up, 0)
            self.setWall(center1, Direction.Left, 0)
        
        if curr_cell != center2:
            self.setWall(center2, Direction.Up, 0)
            self.setWall(center2, Direction.Right, 0)
             
        if curr_cell != center3:
            self.setWall(center3, Direction.Right, 0)
            self.setWall(center3, Direction.Down, 0)
             
        if curr_cell != center4:
            self.setWall(center4, Direction.Down, 0)
            self.setWall(center4, Direction.Left, 0)
    
    def hasExplored(self, loc):
        '''
        Return whether the given maze has been already explored
        
        @param loc: given location (maze cell)
        @type loc: [0, 0] array
        '''
        
        x = loc[0]
        y = loc[1]
        return self.explored[y][x]
        
    def markExplored(self, loc):
        '''
        Mark the given maze cell as explored
        
        @param loc: given location (maze cell)
        @type loc: [0, 0] array
        '''
        
        x = loc[0]
        y = loc[1]
        self.explored[y][x] = True
      
    def show(self):
        '''
        Used for debugging. Prints maze walls data structure in robot coordinate system to console
        '''
        
        reverse_index = len(self.maze_walls)
        while reverse_index > 0:
            row = self.maze_walls[reverse_index - 1]
            print row
            reverse_index -= 1

    def showExplored(self):
        '''
        Used for debugging. Prints maze explored data structure in robot coordinate system to console
        '''
        
        reverse_index = len(self.explored)
        while reverse_index > 0:
            row = self.explored[reverse_index - 1]
            print row  # keep it
            reverse_index -= 1



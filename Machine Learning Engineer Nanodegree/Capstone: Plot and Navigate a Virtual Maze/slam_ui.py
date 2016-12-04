# Copyright (C) 2016 - Srikanth Pagadala, Conscious Computing
# email: srikanth.pagadala@gmail.com

import sys
import time
import traceback

from grid.model.maze_model import Direction
from grid.util.myturtle import Screen
from grid.util.myturtle import *

class SlamUi(object):
    '''
    Does all the hard work of bringing boring AI algorithms to life and make them look good. Implemented using python turtle library.
    '''

    def __init__(self, maze_dim):
        '''
        Initialize UI
        
        @param maze_dim: dimension of the maze. Usually 12x12 or 16x16
        @type maze_dim: int
        '''
        
        self.maze_dim = maze_dim
        self.maze_model = {}
        self.erasers = {}
        self.depth = None
        
        self.path_first = []
        self.path_recent = []
        self.path_best = []
        
        self.path_current_start_loc = None
        
        # Intialize the window and drawing turtle.
        self.screen = Screen()

        self.screen.setup(width=1.0, height=1.0, startx=None, starty=None)
        screen_width, screen_height = self.screen.window_width(), self.screen.window_height()
        if screen_height <= screen_width:
            bottom_margin = 1
            top_margin = 2
            self.sq_size = screen_height / (bottom_margin + maze_dim + top_margin)
            origin_x = (screen_width - (self.sq_size * maze_dim)) / 2
            origin_y = bottom_margin * self.sq_size
        else:
            left_margin = 1
            right_margin = 1
            self.sq_size = screen_width / (left_margin + maze_dim + right_margin)
            origin_x = left_margin * self.sq_size
            origin_y = (screen_height - (self.sq_size * maze_dim)) / 2
            
        self.screen.setworldcoordinates(-origin_x, -origin_y, screen_width - origin_x, screen_height - origin_y)
        
        self.screen.tracer(0, 0)
        self.wally = Turtle()
        self.wally.speed(0)
        self.wally.hideturtle()
        self.wally.penup()
        
        # draw maze border
        self.wally.fillcolor("white")
        self.wally.begin_fill()
        self.wally.pencolor("#E5E4E2")  # light gray - Platinum
        self.wally.setheading(90)
        self.wally.pendown()
        self.wally.forward(self.sq_size * self.maze_dim)
        self.wally.right(90)
        self.wally.forward(self.sq_size * self.maze_dim)
        self.wally.right(90)
        self.wally.forward(self.sq_size * self.maze_dim)
        self.wally.right(90)
        self.wally.forward(self.sq_size * self.maze_dim)
        self.wally.penup()
        self.wally.end_fill()
        
        # draw dots
        for x in range(self.maze_dim):
            for y in range(self.maze_dim):
                self.drawPatch(x, y)
                self.drawDot(x, y)
                
        # write text legend/footer
        args = {}
        args['command'] = "write-footer"
        args['line'] = "when shown, BLUE: First path, RED: Best path, GREEN: Recent path, GRAY: Current path"
        self.writeLine(args)
         
    def writeLine(self, args):
        '''
        Write a line of text on UI. Used to write status or title
        
        @param args: dict of parameters. command=title|status|footer. line=txt
        @type args: dict
        '''
        
        _, top = self.screen.screensize()
        
        command = args['command']
        line = args['line']
        
        key = command
        eraser = self.getEraseableTurtle(key, color="#566D7E", hideTurtle=True)
        eraser.clear()
        
        x = (self.sq_size * self.maze_dim) / 2
        
        if command == "write-title":
            y = top - self.sq_size - self.sq_size / 2
            font = ("Arial", 18, "bold")
        elif command == "write-status":
            y = top - self.sq_size * 2 - self.sq_size / 2
            font = ("Arial", 14, "normal")
        elif command == "write-footer":
            y = -self.sq_size + self.sq_size / 2
            font = ("Arial", 10, "normal")
            
        eraser.goto(x, y)
        eraser.write(line, move=False, align="center", font=font)
        
        self.screen.update()
  
    def drawPatch(self, x, y, color="#E5E4E2", key_prefix=""):
        '''
        Patch is a gray square that signifies unexplored cell. When a cell is visited, we remove this patch and
        cell becomes white.
        
        @param x: x coord of cell
        @type x: int 
        @param y: y coord of cell
        @type y: int
        @param color: color of patch. Default is a gray color
        @type color: Hex color code
        @param key_prefix: prefix used to uniquely identify eraseable turtle to draw this patch
        @type key_prefix: string
        '''
        
        key = key_prefix + "patch-" + str((x, y))
        eraser = self.getEraseableTurtle(key, color=color)
        
        eraser.fillcolor(color)
        eraser.begin_fill()
        eraser.pencolor(color)
        eraser.goto(x * self.sq_size, y * self.sq_size)
        eraser.setheading(90)
        eraser.pendown()
        eraser.forward(self.sq_size)
        eraser.right(90)
        eraser.forward(self.sq_size)
        eraser.right(90)
        eraser.forward(self.sq_size)
        eraser.right(90)
        eraser.forward(self.sq_size)
        eraser.penup()
        eraser.end_fill()
        
    def drawDot(self, x, y):
        '''
        Draws red dots at the intersection of grid lines
        
        @param x: x coord of cell
        @type x: int
        @param y: y coord of cell
        @type y: int
        '''
        
        self.wally.pencolor("brown")
        xys = [[x, y], [x + 1, y], [x + 1, y + 1], [x, y + 1]]
        for xy in xys: 
            self.wally.goto(self.sq_size * xy[0], self.sq_size * xy[1])
            self.wally.dot(5)
        
    def drawWall(self, x, y, direction, color="black"):
        '''
        Draw wall of a cell in the given direction
        
        @param x: x coord of cell
        @type x: int 
        @param y: y coord of cell
        @type y: int
        @param direction: Up, Right, Left, Down
        @type direction: grid.model.maze_model.MazeModel
        @param color: color of the wall. Default is black
        @type color: Hex color code
        '''
        
        if direction == Direction.Up:
            y = y + 1
            heading = 0
        elif direction == Direction.Right:
            x = x + 1
            heading = 90
        elif direction == Direction.Down:
            heading = 0
        elif direction == Direction.Left:
            heading = 90
         
        self.wally.pencolor(color)
        self.wally.goto(x * self.sq_size, y * self.sq_size)
        self.wally.setheading(heading)
        self.wally.pendown()
        self.wally.forward(self.sq_size)
        self.wally.penup() 
        
    def cellExplored(self, x, y):
        '''
        Mark cell as explored by turning bgcolor from gray to white
        
        @param x: x coord of cell
        @type x: int
        @param y: y coord of cell
        @type y: int
        '''
        
        key = "patch-" + str((x, y))
        eraser = self.getEraseableTurtle(key, color="lightgray")
        eraser.clear()
        
        key = (x, y)
        walls = self.maze_model[key]
        for direction in walls:
            self.drawWall(x, y, direction)
          
    def wait(self):
        '''
        Wait for user input, such as, close the UI window
        '''
        
        self.screen._root.mainloop()
 
    def getEraseableTurtle(self, key, color="black", pensize=1, hideTurtle=True):
        '''
        Create or return an eraseable Turtle with given properties
        
        @param key: key to lookup eraseable turtle
        @type key: string
        @param color: hex color code
        @type color: string
        @param pensize: size of the turtle pen
        @type pensize: int
        @param hideTurtle: whether to hide turtle
        @type hideTurtle: boolean
        '''
         
        if self.erasers.has_key(key):
            eraser = self.erasers[key]
        else:
            eraser = Turtle()
            eraser.penup()
            eraser.color(color)
            eraser.pensize(pensize)
            eraser.speed(0)

            if hideTurtle:
                eraser.hideturtle()
                
            self.erasers[key] = eraser
             
        return eraser
            
    def eraseCurrentPath(self):
        '''
        Erase current Path (gray line)
        '''
        
        self.path_current_start_loc = None
        
        eraser = self.getEraseableTurtle("draw-path-current")
        eraser.clear()
        eraser.hideturtle()
        self.screen.update()
        
    def drawCurrentPath(self, args):
        '''
        Draw current path (gray line)
        
        @param args: dict of parameters to be used to draw current path
        @type args: dict
        '''
        
        command = args['command']
        path_current = args['path_current']
        draw_tail = args.get('draw_tail', True)
        
        eraser = self.getEraseableTurtle(command, color="gray", pensize=3, hideTurtle=False)
        eraser.showturtle()
        
        xy_offset = 0.50
        
        if not self.path_current_start_loc:
            
            entry = path_current
            loc = entry[0]
            rotation = int(entry[1])
            heading = Direction(int(entry[2]))
            
            # account for U-Turns
            if heading == Direction.Down:
                heading = -90
            elif heading == Direction.Left:
                heading = 180
            elif heading == Direction.Right:
                heading = 0
            elif heading == Direction.Up:
                heading = 90
                  
            self.path_current_start_loc = loc
            eraser.setheading(heading)
        else:
            entry = path_current
            loc = entry[0]
            rotation = int(entry[1])
            
            eraser.goto((self.path_current_start_loc[0] + xy_offset) * self.sq_size, (self.path_current_start_loc[1] + xy_offset) * self.sq_size)
            eraser.right(rotation)
            if draw_tail:
                eraser.pendown()
                eraser.forward(0 if loc == self.path_current_start_loc else self.sq_size)
                eraser.penup()
            else:
                eraser.goto((loc[0] + xy_offset) * self.sq_size, (loc[1] + xy_offset) * self.sq_size)
            
            key = "patch-" + str((loc[0], loc[1]))
            eraser = self.getEraseableTurtle(key, color="lightgray")
            eraser.clear()
            
            self.path_current_start_loc = loc
            self.screen.update()
        
    def drawPath(self, command, args):
        '''
        Draw first, best or recent path
        
        @param command: command = first|best|recent
        @type command: string
        @param args: dict of parameters to be used
        @type args: dict
        '''
        
        xy_offset = 0.0
        if 'xy_offset' in args and args['xy_offset']:
            xy_offset = args['xy_offset']
        
        if command == "draw-path-first":
            paths = self.path_first
            eraser = self.getEraseableTurtle(command, color="lightblue", pensize=3)
            xy_offset = 0.25 if not xy_offset else xy_offset
        elif command == "draw-path-best":
            paths = self.path_best
            eraser = self.getEraseableTurtle(command, color="#E8ADAA", pensize=3)
            xy_offset = 0.5 if not xy_offset else xy_offset
        elif command == "draw-path-recent":
            paths = self.path_recent
            eraser = self.getEraseableTurtle(command, color="lightgreen", pensize=3)
            xy_offset = 0.75 if not xy_offset else xy_offset
          
        eraser.clear()
         
        start_loc = None
        for entry in paths:
              
            loc = entry[0]
            rotation = int(entry[1])
            heading = Direction(int(entry[2]))
               
            if not start_loc:
                   
                # account for U-Turns
                if heading == Direction.Down:
                    heading = -90
                elif heading == Direction.Left:
                    heading = 180
                elif heading == Direction.Right:
                    heading = 0
                elif heading == Direction.Up:
                    heading = 90
                      
                start_loc = loc
                eraser.setheading(heading)
                   
            else:
                eraser.goto((start_loc[0] + xy_offset) * self.sq_size, (start_loc[1] + xy_offset) * self.sq_size)
                eraser.right(rotation)
                eraser.pendown()
                eraser.forward(0 if loc == start_loc else self.sq_size)
                eraser.penup()
                
                start_loc = loc
        
        self.screen.update()

    def doBlockDeadend(self, args):
        '''
        Execute block deadend cell command. Close the cell with red line and change background color to red.
        
        @param args: dict of parameters to be used
        @type args: dict
        '''
        # parse input args
        loc = args['loc']  # [0, 0]
        x = loc[0]
        y = loc[1]
        
        block_direction = Direction(args['block_direction'])
        
        self.drawPatch(x, y, color="#FFDFDD", key_prefix="deadend-")
        
        self.drawDot(x, y)
        
        for direction in list(Direction): 
            color = "red" if direction == block_direction else "black"
            self.drawWall(x, y, direction, color=color)
        
        self.screen.update()
        
    def doCellExplored(self, args):
        '''
        Execute cell explored ui command. Change cell's background from gray to white
        
        @param args: dict of parameters to be used
        @type args: dict
        '''
        
        # parse input args
        loc = args['loc']  # [0, 0]
        x = loc[0]
        y = loc[1]
         
        direction_values = args['walls']  # [1, 2, 3] for [Right, Down, Left]
 
        directions = []
        for value in direction_values:
            direction = Direction(value)
            directions.append(direction)
     
        # perform operation
        key = (x, y)
        self.maze_model[key] = directions
        self.cellExplored(x, y)
         
        self.screen.update()
    
    def doDepthsChanged(self, args):
        '''
        Execute depths changed ui command. Write new depth numbers in each cell.
        
        @param args: dict of parameters to be used
        @type args: dict
        '''
        
        self.depth = args['depths']
         
        key = "depth-turtle"
        eraser = self.getEraseableTurtle(key, color="#566D7E", hideTurtle=True)
        eraser.clear()
        
        for x in range(self.maze_dim):
            for y in range(self.maze_dim):
                eraser.goto((x + 0.5) * self.sq_size, (y + 0.5) * self.sq_size - 5)
                eraser.write(self.depth[y][x], move=False, align="center", font=("Arial", 10, "normal"))
  
        self.screen.update()

    def doQLearningChanged(self, args):
        '''
        Execute QLearning values changed ui command. Draw policy arrows in each cell
        
        @param args: dict of parameters to be used
        @type args: dict
        '''
        
        rl_policy = args['policy']
        
        key = 'qlearning-turtle'
        policy_eraser = self.getEraseableTurtle(key, color="lightgray", hideTurtle=False)
        policy_eraser.clear()
        
        for loc, policy in rl_policy.iteritems():
            
            if loc == "TERMINAL_STATE":
                continue
            
            x, y = loc
            
            # stamp policy arrow
            if type(policy) == int:
                policy = Direction(policy)
                if policy == Direction.Down:
                    policy = -90
                elif policy == Direction.Left:
                    policy = 180
                elif policy == Direction.Right:
                    policy = 0
                elif policy == Direction.Up:
                    policy = 90
                    
                policy_eraser.goto((x + 0.5) * self.sq_size, (y + 0.5) * self.sq_size)
                
                policy_eraser.setheading(policy)
                policy_eraser.stamp()
                
        self.screen.update()
        
    def doValueIterationChanged(self, args):
        '''
        Execute Values changed ui command. Update value iteration values in each cell.
        
        @param args: dict of parameters to be used
        @type args: dict
        '''
        
        values = args['values']
        policy = args['policy']
        
        key = "valueiteration-turtle"
        eraser = self.getEraseableTurtle(key, color="#566D7E", hideTurtle=True)
        eraser.clear()
        
        key = 'policy-' + key
        policy_eraser = self.getEraseableTurtle(key, color="lightgray", hideTurtle=False)
        policy_eraser.clear()
        
        for loc, value in values.iteritems():
            
            if loc == "TERMINAL_STATE":
                continue
            
            if loc in policy:
                p = policy[loc]
            else:
                continue
            
            x, y = loc
            value = "{:0.3f}".format(value)
            
            eraser.goto((x + 0.5) * self.sq_size, (y) * self.sq_size)
            eraser.write(value, move=False, align="center", font=("Arial", 10, "normal"))
            
            # stamp policy arrow
            if type(p) == int:
                p = Direction(p)
                if p == Direction.Down:
                    p = -90
                elif p == Direction.Left:
                    p = 180
                elif p == Direction.Right:
                    p = 0
                elif p == Direction.Up:
                    p = 90
                    
                policy_eraser.goto((x + 0.5) * self.sq_size, (y + 0.5) * self.sq_size)
                      
                policy_eraser.setheading(p)
                policy_eraser.stamp()
  
        self.screen.update()

    def doDrawPath(self, args):
        '''
        Execute draw path (best, first recent) ui command.
        
        @param args: dict of parameters to be used
        @type args: dict
        '''
        
        command = args['command']
        
        if command == "draw-path-first":
            self.path_first = args['path_first']
        elif command == "draw-path-best":
            self.path_best = args['path_best']
        elif command == "draw-path-recent":
            self.path_recent = args['path_recent']
            
        self.drawPath(command, args)
        
if __name__ == '__main__':
    
    if sys.argv and len(sys.argv) > 1:
        maze_dim = sys.argv[1]
    else:
        maze_dim = 12

    ui = SlamUi(int(maze_dim))
    
    while True:
        try:
            args = eval(raw_input())
            # time.sleep(0.05) # fiddle if slow down needed

            command = args['command']
            
            if command == "depths-changed":
                ui.doDepthsChanged(args)
            elif command == "cell-explored":
                ui.doCellExplored(args)
            elif command == "draw-path-current":
                ui.drawCurrentPath(args)
            elif command == "erase-path-current":
                ui.eraseCurrentPath()
            elif command.startswith("draw-path-"):
                ui.doDrawPath(args)
            elif command.startswith("write-"):
                ui.writeLine(args)
            elif command == "block-deadend":
                ui.doBlockDeadend(args)
            elif command == "qlearning-changed":
                ui.doQLearningChanged(args)
            elif command == "valueiteration-changed":
                ui.doValueIterationChanged(args)
                
            print "ok"
        except:
            # traceback.print_exc() # debug
            ui.wait()
            break

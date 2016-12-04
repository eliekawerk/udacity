# Copyright (C) 2016 - Srikanth Pagadala, Conscious Computing
# email: srikanth.pagadala@gmail.com

from subprocess import PIPE, Popen

from grid.ai.ez.block_deadend import BlockDeadend
from grid.ai.ez.follow_wall import FollowWall
from grid.ai.ez.random_turn import RandomTurn
from grid.ai.ff.flood_fill import FloodFill
from grid.ai.gs.astar import AstarSearch
from grid.ai.gs.bfs import BfsSearch
from grid.ai.gs.dfs import DfsSearch
from grid.ai.gs.ucs import UcsSearch
from grid.ai.rl.q_learning import QLearning
from grid.ai.rl.value_iteration import ValueIteration
from grid.model.maze_model import MazeModel


class Robot(object):
    
    # RANDOM_TURN, FOLLOW_WALL, BLOCK_DEADEND
    # GRAPH_SEARCH_DFS, GRAPH_SEARCH_BFS, GRAPH_SEARCH_UCS, GRAPH_SEARCH_ASTAR
    # RL_VALUE_ITERATION, RL_Q_LEARNING
    # FLOOD_FILL
    
    use = "FLOOD_FILL"
    
    def __init__(self, maze_dim):
        '''
        Use the initialization function to set up attributes that your robot
        will use to learn and navigate the maze. Some initial attributes are
        provided based on common information, including the size of the maze
        the robot is placed in.
        '''

        location = [0, 0]
        heading = 'up'
        
        ui = Popen(["python", "-u", "slam_ui.py", str(maze_dim)], stdin=PIPE, stdout=PIPE, bufsize=1)
        
        assumeOpenWalls = False if (self.use.startswith("GRAPH_SEARCH") or self.use.startswith("RL")) else True
        maze_model = MazeModel(maze_dim, ui, assumeOpenWalls)
        
        if self.use == "RANDOM_TURN":
            self.ai = RandomTurn(maze_model, location, heading, ui)
        elif self.use == "FOLLOW_WALL":
            self.ai = FollowWall(maze_model, location, heading, ui)
        elif self.use == "BLOCK_DEADEND":
            self.ai = BlockDeadend(maze_model, location, heading, ui)
        elif self.use == "GRAPH_SEARCH_DFS":
            self.ai = DfsSearch(maze_model, location, heading, ui)
        elif self.use == "GRAPH_SEARCH_BFS":
            self.ai = BfsSearch(maze_model, location, heading, ui)
        elif self.use == "GRAPH_SEARCH_UCS":
            self.ai = UcsSearch(maze_model, location, heading, ui)
        elif self.use == "GRAPH_SEARCH_ASTAR":
            self.ai = AstarSearch(maze_model, location, heading, ui)
        elif self.use == "RL_VALUE_ITERATION":
            self.ai = ValueIteration(maze_model, location, heading, ui)
        elif self.use == "RL_Q_LEARNING":
            self.ai = QLearning(maze_model, location, heading, ui)
        elif self.use == "FLOOD_FILL":
            self.ai = FloodFill(maze_model, location, heading, ui)

    def next_move(self, sensors):
        '''
        Use this function to determine the next move the robot should make,
        based on the input from the sensors after its previous move. Sensor
        inputs are a list of three distances from the robot's left, front, and
        right-facing sensors, in that order.

        Outputs should be a tuple of two values. The first value indicates
        robot rotation (if any), as a number: 0 for no rotation, +90 for a
        90-degree rotation clockwise, and -90 for a 90-degree rotation
        counterclockwise. Other values will result in no rotation. The second
        value indicates robot movement, and the robot will attempt to move the
        number of indicated squares: a positive number indicates forwards
        movement, while a negative number indicates backwards movement. The
        robot may move a maximum of three units per turn. Any excess movement
        is ignored.

        If the robot wants to end a run (e.g. during the first training run in
        the maze) then returing the tuple ('Reset', 'Reset') will indicate to
        the tester to end the run and return the robot to the start.
        '''

        return self.ai.nextMove(sensors)

# Copyright (C) 2016 - Srikanth Pagadala, Conscious Computing
# email: srikanth.pagadala@gmail.com

from grid.ai.gs.graph_search import GraphSearch, PositionSearchProblem
from grid.util.util import *


class BfsSearch(GraphSearch):
    '''
    Breadth first search (BFS) is an uninformed algorithm for traversing or searching tree 
    or graph data structures, where it starts at the tree root and explores the neighbor 
    nodes first, before moving to the next level neighbors. It uses FIFO queue to remember 
    fringe nodes. 
    '''
    
    def title(self):
        '''
        Name of the AI algorithm that will be shown as title on UI screen 
        '''
        return "GRAPH SEARCH: BREADTH FIRST SEARCH"

    def beforeReset(self):
        '''
        A callback function that gives AI algorithm an opportunity to perform any last minute 
        calculations before sending (reset, reset) signal to Tester. BFS algo performs graph search
        and comes up with a path from start to goal before reseting.
        '''
        
        problem = PositionSearchProblem(self.maze_model, goal=self.goalLoc)
        frontier = PriorityQueueWithFunction(len)
        self.searched_path = self.graphSearch(problem, frontier) 
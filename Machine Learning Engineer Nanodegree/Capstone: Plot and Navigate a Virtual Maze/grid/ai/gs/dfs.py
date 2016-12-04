# Copyright (C) 2016 - Srikanth Pagadala, Conscious Computing
# email: srikanth.pagadala@gmail.com

from grid.ai.gs.graph_search import GraphSearch, PositionSearchProblem
from grid.util.util import *


class DfsSearch(GraphSearch):
    '''
    Depth first search (DFS) is an uninformed algorithm for traversing or searching 
    tree or graph data structures, where one starts at the root and explores as far 
    as possible along each branch before backtracking. It uses stack to remember 
    the next vertex to start a search.
    '''
 
    def title(self):
        '''
        Name of the AI algorithm that will be shown as title on UI screen 
        '''
        return "GRAPH SEARCH: DEPTH FIRST SEARCH"
   
    def beforeReset(self):
        '''
        A callback function that gives AI algorithm an opportunity to perform any last minute 
        calculations before sending (reset, reset) signal to Tester. DFS algo performs graph search
        and comes up with a path from start to goal before reseting.
        '''
        
        problem = PositionSearchProblem(self.maze_model, goal=self.goalLoc)
        frontier = Stack()
        self.searched_path = self.graphSearch(problem, frontier) 
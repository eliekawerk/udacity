# Copyright (C) 2016 - Srikanth Pagadala, Conscious Computing
# email: srikanth.pagadala@gmail.com

from grid.ai.gs.graph_search import GraphSearch, PositionSearchProblem
from grid.util.util import *


class UcsSearch(GraphSearch):
    '''
    Uniform Cost Search is like BFS. The difference is rather than going evenly across 
    the layers, prioritizing them by their depth, instead we prioritize them by their 
    cost. So that cheap things get done first, even if they are multiple steps into the 
    tree.
    '''
   
    def title(self):
        '''
        Name of the AI algorithm that will be shown as title on UI screen 
        '''
        return "GRAPH SEARCH: UNIFORM COST SEARCH"
 
    def beforeReset(self):
        '''
        A callback function that gives AI algorithm an opportunity to perform any last minute 
        calculations before sending (reset, reset) signal to Tester. UCS algo performs graph search
        and comes up with a path from start to goal before reseting.
        '''
        
        problem = PositionSearchProblem(self.maze_model, goal=self.goalLoc)
        
        cost = lambda aPath: problem.getCostOfActions([x[1] for x in aPath])
        frontier = PriorityQueueWithFunction(cost)
        
        self.searched_path = self.graphSearch(problem, frontier) 
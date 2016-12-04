# Copyright (C) 2016 - Srikanth Pagadala, Conscious Computing
# email: srikanth.pagadala@gmail.com

from grid.ai.gs.graph_search import GraphSearch, PositionSearchProblem
from grid.util.util import *


class AstarSearch(GraphSearch):
    '''
    A* is an informed search algorithm, or a best-first search, meaning that it solves 
    problems by searching among all possible paths to the solution for the one that 
    incurs the smallest cost (least distance travelled, shortest time, etc.), and among 
    these paths it first considers the ones that appear to lead most quickly to the solution. 
    It is formulated in terms of weighted graphs: starting from a specific node of a graph, 
    it constructs a tree of paths starting from that node, expanding paths one step at a time, 
    until one of its paths ends at the predetermined goal node.
    
    At each iteration of its main loop, A* needs to determine which of its partial paths to 
    expand into one or more longer paths. It does so based on an estimate of the cost (total weight) 
    still to go to the goal node. Specifically, A* selects the path that minimizes

    f(n) = g(n) + h(n)

    where n is the last node on the path, g(n) is the cost of the path from the start node to n, 
    and h(n) is a heuristic that estimates the cost of the cheapest path from n to the goal. 
    The heuristic is problem-specific. For the algorithm to find the actual shortest path, the heuristic 
    function must be admissible, meaning that it never overestimates the actual cost to get to the 
    nearest goal node. Typical implementations of A* use a priority queue to perform the repeated 
    selection of minimum (estimated) cost nodes to expand.
    '''

    def title(self):
        '''
        Name of the AI algorithm that will be shown as title on UI screen 
        '''
        return "GRAPH SEARCH: A-STAR SEARCH, manhattanHeuristic"
    
    def beforeReset(self):
        '''
        A callback function that gives AI algorithm an opportunity to perform any last minute 
        calculations before sending (reset, reset) signal to Tester. A* algo performs graph search
        and comes up with a path from start to goal before reseting.
        '''
        
        problem = PositionSearchProblem(self.maze_model, goal=self.goalLoc)

        cost = lambda aPath: problem.getCostOfActions([x[1] for x in aPath]) + self.manhattanHeuristic(aPath[len(aPath) - 1][0], problem)
        frontier = PriorityQueueWithFunction(cost)
        
        self.searched_path = self.graphSearch(problem, frontier) 
        
    def nullHeuristic(self, state, problem=None):
        '''
        Blank heuristic for a PositionSearchProblem. A heuristic function estimates the cost from 
        the current state to the nearest goal in the provided SearchProblem. This heuristic is trivial.
        
        @param position: current cell
        @type position: [0, 0], python array
        @param problem: given PositionSearchProblem instance
        @type problem: grid.ai.gs.graph_search.PositionSearchProblem
        '''
        
        return 0
    
    def manhattanHeuristic(self, position, problem):
        '''
        The Manhattan distance heuristic for a PositionSearchProblem
        
        @param position: current cell
        @type position: [0, 0], python array
        @param problem: given PositionSearchProblem instance
        @type problem: grid.ai.gs.graph_search.PositionSearchProblem
        '''
        xy1 = position
        xy2 = problem.goal
        return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])

    def euclideanHeuristic(self, position, problem):
        '''
        The Euclidean distance heuristic for a PositionSearchProblem
        
        @param position: current cell
        @type position: [0, 0], python array
        @param problem: given PositionSearchProblem instance
        @type problem: grid.ai.gs.graph_search.PositionSearchProblem
        '''

        xy1 = position
        xy2 = problem.goal
        return ((xy1[0] - xy2[0]) ** 2 + (xy1[1] - xy2[1]) ** 2) ** 0.5

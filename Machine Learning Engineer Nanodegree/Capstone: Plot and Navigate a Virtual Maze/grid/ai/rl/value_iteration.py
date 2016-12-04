# Copyright (C) 2016 - Srikanth Pagadala, Conscious Computing
# email: srikanth.pagadala@gmail.com

from grid.model.maze_model import Direction
from grid.util.util import *
from grid.ai.rl.rl import ReinforcementLearning

class ValueIteration(ReinforcementLearning):
    '''
    Value iteration is a method of computing an optimal MDP policy and its value. Value 
    iteration starts at the "end" and then works backward, refining an estimate of either 
    Q* or V*. There is really no end, so it uses an arbitrary end point. 
    Let Vk be the value function assuming there are k stages to go, and let Qk be the Q-function 
    assuming there are k stages to go. These can be defined recursively. Value iteration starts with 
    an arbitrary function V0 and uses the following equations to get the functions for k+1 stages to 
    go from the functions for k stages to go:


    Qk+1(s,a) = sigma-s' P(s' | s,a) (R(s,a,s') + gamma * Vk(s')) for k >= 0
    
    Vk(s) = maxa Qk(s,a) for k > 0
    
    It can either save the V[S] array or the Q[S,A] array. Saving the V array results in less storage, 
    but it is more difficult to determine an optimal action, and one more iteration is needed to determine 
    which action results in the greatest value. 
    
    Here Living Reward is 0.0, Robot Noise is 0.0 and Goal State Reward is 1.0. Discount (gamma) is set to 
    0.9, and num of iterations (k) is set to 100. The transition probability for a state (cell location) 
    is based on the number of wall openings in that state.
    '''
    
    def title(self):
        '''
        Name of the AI algorithm that will be shown as title on UI screen 
        '''
        return "REINFORCEMENT LEARNING: VALUE ITERATION"

    def beforeReset(self):
        '''
        A callback function that gives AI algorithm an opportunity to perform any last minute 
        calculations before sending (reset, reset) signal to Tester. ValueIteration algo runs its iterations 
        and computers Values (and Policy) for each state (cell location) and comes up with a path 
        from start to goal before reseting.
        '''
        
        self.world = MazeWorld(self.maze_model, self.goalLoc)
        
        self.setStatus("Exploration complete. Starting Value Iteration")
        self.agent = ValueIterationAgent(self.world, self.maze_model, self)
        
        print "Value Iteration values:"
        print self.agent.getValues()
        
        self.signalUi({'command': 'valueiteration-changed', 'values': self.agent.getValues(), 'policy': self.agent.getFullPolicy()})
        self.setStatus("Value Iteration complete")

class MazeWorld():
    '''
    MazeWorld provides startState, possibleActions in a given state and next state for a given action
    '''
    
    def __init__(self, maze_model, goalLoc):
        '''
        Initialize MazeWorld
        
        @param maze_model: handle to maze_model that provides information about cells explored, walls etc
        @type maze_model: grid.model.maze_model.MazeModel
        @param goalLoc: goal cell coordinates
        @type goalLoc: [x, y] array
        '''
        
        self.maze_model = maze_model
        self.goalLoc = (goalLoc[0], goalLoc[1])
        self.terminalState = 'TERMINAL_STATE'

        # parameters
        self.livingReward = 0.0
        self.noise = 0.0

    def getPossibleActions(self, state):
        '''
        Returns list of valid actions for 'state'.
        
        @param state: given tuple state (location) of robot
        @type state: tuple
        '''
        
        if state == self.terminalState:
            return []
        
        if state == self.goalLoc:
            return ('exit',)
        
        x, y = state
    
        possibleActions = []
        for direction in list(Direction):
            if not self.maze_model.hasWall([x, y], direction):
                possibleActions.append(direction)
                
        return possibleActions

    def getStates(self):
        '''
        Return list of all states.
        '''
        
        # The true terminal state.
        states = [self.terminalState]
        for x in range(self.maze_model.dim):
            for y in range(self.maze_model.dim):
                if self.maze_model.hasExplored([x, y]):
                    state = (x, y)
                    states.append(state)
                    
        return states

    def getReward(self, state, action, nextState):
        '''
        Get reward for state, action, nextState transition.
        
        @param state: given tuple state (location) of robot
        @type state: tuple
        @param action: Direction of movement in Maze. Up, Down, Right, Left
        @type action: grid.model.maze_model.Direction
        @param nextState: next resulting state of robot after taking action
        @type nextState: tuple
        @param reward: reward received from current state by taking action
        @type reward: float
        '''
        
        if state == self.terminalState:
            return 0.0
        
        if state == self.goalLoc:
            return 1.0

        return self.livingReward

    def getStartState(self):
        '''
        Return the start state of maze world, typically (0, 0)
        '''
        
        return (0, 0)

    def isTerminal(self, state):
        '''
        Return whether given state is the terminal state. Only the TERMINAL_STATE state is *actually* 
        a terminal state. The other "exit" states are technically non-terminals with a single 
        action "exit" which leads to the true terminal state. This convention is to make the 
        grids line up with the examples in the R+N textbook.
        
        @param state: given tuple state (location) of robot
        @type state: tuple
        '''
        
        return state == self.terminalState

    def getTransitionStatesAndProbs(self, state, action):
        '''
        Returns list of (nextState, prob) pairs representing the states reachable from 'state' 
        by taking 'action' along with their transition probabilities.
        
        @param state: given tuple state (location) of robot
        @type state: tuple
        @param action: Direction of movement in Maze. Up, Down, Right, Left
        @type action: grid.model.maze_model.Direction
        '''
        possibleActions = self.getPossibleActions(state)
        if action not in possibleActions:
            raise "Illegal action!"

        if self.isTerminal(state):
            return []
        
        if state == self.goalLoc:
            termState = self.terminalState
            return [(termState, 1.0)]

        nextState = self.maze_model.findNeighbor(state, action)
        
        return [((nextState[0], nextState[1]), 1.0 / len(possibleActions))]


class ValueIterationAgent():
    '''
    A ValueIterationAgent takes a Markov decision process on initialization and runs value iteration
    for a given number of iterations using the supplied discount factor.
    '''
    def __init__(self, mdp, maze_model, parent, discount=0.9, iterations=100):
        '''
        Initialize ValueIterationAgent
        
        @param mdp: handle to mazeWorld that provides startState, possibleActions in a given state and next state for a given action
        @type mdp: grid.ai.rl.value_iteration.MazeWorld
        @param maze_model: handle to maze_model that provides information about cells explored, walls etc
        @type maze_model: grid.model.maze_model.MazeModel
        @param parent: handle to ui class, so that agent can publish status periodically
        @type parent: grid.ai.rl.value_iteration.ValueIteration
        @param discount: Discount Rate
        @type discount: float
        @param iterations: num of iterations to run to compute Values
        @type iterations: int
        '''
        self.mdp = mdp
        self.maze_model = maze_model
        self.discount = discount
        self.iterations = iterations
        self.values = Counter()  # A Counter is a dict with default 0

        for iteration in range(self.iterations):
            for state in self.mdp.getStates():
                possibleActions = self.mdp.getPossibleActions(state)    
                valuesForActions = Counter()
                for action in possibleActions:
                    transitionStatesAndProbs = self.mdp.getTransitionStatesAndProbs(state, action)
                    valueState = 0
                    for transition in transitionStatesAndProbs:
                        valueState += transition[1] * (self.mdp.getReward(state, action, transition[0]) + self.discount * self.values[transition[0]])
                    valuesForActions[action] = valueState
                self.values[state] = valuesForActions[valuesForActions.argMax()]
            parent.setStatus("Value Iteration: Running iteration {}/{}".format(iteration, self.iterations))
        
    def getValues(self):
        '''
        Return all computed values by state (location)
        '''
        
        return self.values
    
    def getValue(self, state):
        '''
        Return the value of the state (computed in __init__).
        
        @param state: given tuple state (location) of robot
        @type state: tuple
        '''
        
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        '''
        Compute the Q-value of action in state from the value function stored in self.values.
        
        @param state: given tuple state (location) of robot
        @type state: tuple
        @param action: Direction of movement in Maze. Up, Down, Right, Left
        @type action: grid.model.maze_model.Direction
        '''
        transitionStatesAndProbs = self.mdp.getTransitionStatesAndProbs(state, action)
        qValue = 0
        for transition in transitionStatesAndProbs:
            qValue += transition[1] * self.mdp.getReward(state, action, transition[0]) + self.values[transition[0]]
        
        return qValue


    def computeActionFromValues(self, state):
        '''
        The policy is the best action in the given state according to the values currently stored in self.values.
        
        @param state: given tuple state (location) of robot
        @type state: tuple
        '''
        if self.mdp.isTerminal(state):
            return None
    
        possibleActions = self.mdp.getPossibleActions(state)
        
        valuesForActions = Counter()
        for action in possibleActions:
            transitionStatesAndProbs = self.mdp.getTransitionStatesAndProbs(state, action)
            valueState = 0
            for transition in transitionStatesAndProbs:
                valueState += transition[1] * (self.mdp.getReward(state, action, transition[0]) + self.discount * self.values[transition[0]])
            valuesForActions[action] = valueState
            
        # print "FROM ", state, ": ",valuesForActions
        if valuesForActions.totalCount() == 0:
            import random
            return possibleActions[int(random.random() * len(possibleActions))]
        else:
            valueToReturn = valuesForActions.argMax()
            # print "RETURNING: ", valueToReturn
            return valueToReturn

    def getPolicy(self, state):
        '''
        Return the computed policy (Direction of movement) from the given state
        
        @param state: given tuple state (location) of robot
        @type state: tuple
        '''
        
        return self.computeActionFromValues(state)

    def getAction(self, state):
        '''
        Returns the policy at the state (no exploration).
        
        @param state: given tuple state (location) of robot
        @type state: tuple
        '''
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        '''
        Returns Q(state,action).
        
        @param state: given tuple state (location) of robot
        @type state: tuple
        @param action: Direction of movement in Maze. Up, Down, Right, Left
        @type action: grid.model.maze_model.Direction
        '''
        
        return self.computeQValueFromValues(state, action)
    
    def getFullPolicy(self):
        '''
        Return dict of policy for every cell in the maze 
        '''
        
        policy = {}
        for x in range(self.maze_model.dim):
            for y in range(self.maze_model.dim):
                if self.maze_model.hasExplored([x, y]):
                    state = (x, y)
                    action = self.getAction(state)
                    if type(action) == Direction:
                        policy[state] = action.value
                    else:
                        policy[state] = action
        return policy
    

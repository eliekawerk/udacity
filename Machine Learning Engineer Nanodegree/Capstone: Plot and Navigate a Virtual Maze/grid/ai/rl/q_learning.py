# Copyright (C) 2016 - Srikanth Pagadala, Conscious Computing
# email: srikanth.pagadala@gmail.com

from grid.ai.rl.rl import ReinforcementLearning
from grid.ai.rl.value_iteration import MazeWorld
from grid.model.maze_model import Direction
from grid.util.util import *


class QLearning(ReinforcementLearning):
    '''
    In Q-learning and related algorithms, an agent tries to learn the optimal policy from 
    its history of interaction with the environment. A history of an agent is a 
    sequence of state-action-rewards:
    
    <s0,a0,r1,s1,a1,r2,s2,a2,r3,s3,a3,r4,s4...>,

    which means that the agent was in state s0 and did action a0, which resulted in it receiving 
    reward r1 and being in state s1; then it did action a1, received reward r2, and ended up in 
    state s2; then it did action a2, received reward r3, and ended up in state s3; and so on. 
    Q*(s,a), where a is an action and s is a state, is the expected value (cumulative discounted 
    reward) of doing a in state s and then following the optimal policy. Q-learning uses temporal 
    differences to estimate the value of Q*(s,a). In Q-learning, the agent maintains a table of Q[S,A], 
    where S is the set of states and A is the set of actions. Q[s,a] represents its current estimate 
    of Q*(s,a). An experience <s,a,r,s'> provides one data point for the value of Q(s,a). The data point 
    is that the agent received the future value of r + gamma * V(s'), where V(s') = maxa' Q(s',a'); this is the 
    actual current reward plus the discounted estimated future value. This new data point is called 
    a return. The agent can use the temporal difference equation to update its estimate for Q(s,a):
    
    Q[s,a] <- Q[s,a] + alpha(r+ gamma * maxa' Q[s',a'] - Q[s,a]) or, equivalently, 
    Q[s,a] <- (1-alpha) Q[s,a] + alpha(r+ gamma * maxa' Q[s',a'])
    
    Q-learning learns an optimal policy no matter which policy the agent is actually following (i.e., 
    which action a it selects for any state s) as long as there is no bound on the number of times it 
    tries an action in any state (i.e., it does not always do the same subset of actions in a state). 
    Because it learns an optimal policy no matter which policy it is carrying out, it is called an off-policy method.

    Here total num of learning episodes is set to 100. Learning rate, alpha=0.5, Discount, gamma=0.9 and 
    Exploration, epsilon=0.3. Both state transition function and reward function are missing. Agent learns 
    both by interacting with the environment during its learning episodes.
    '''
    
    def title(self):
        '''
        Name of the AI algorithm that will be shown as title on UI screen 
        '''
        return "REINFORCEMENT LEARNING: Q-LEARNING"

    def beforeReset(self):
        '''
        A callback function that gives AI algorithm an opportunity to perform any last minute 
        calculations before sending (reset, reset) signal to Tester. QLearning algo runs its iterations 
        of learning episodes and comes up with a path from start to goal before reseting.
        '''
        
        self.totalEpisodes = 100
        
        self.world = MazeWorld(self.maze_model, self.goalLoc)
        
        self.setStatus("Exploration complete. Starting Q-Learning")
        self.mazeEnv = MazeEnvironment(self.world)
        self.agent = QLearningAgent(self.world, self.maze_model)
        
        for episode in range(self.totalEpisodes):
            self.runEpisode(self.agent, self.mazeEnv, episode)
            
            # update ui
            self.signalUi({'command': 'qlearning-changed', 'policy': self.agent.getFullPolicy()})

        self.setStatus("Q-Learning complete")
        
    def runEpisode(self, agent, environment, episode):
        '''
        Perform QLearning episode iteration
        
        @param agent: Instance of QLearningAgent interacting with MazeEnvironment and receiving rewards
        @type agent: grid.ai.rl.q_learning.QLearningAgent
        @param environment: Handle to environment instance in which agent is QLearning and receiving rewards from 
        @type environment: grid.ai.rl.q_learning.MazeEnvironment
        @param episode: current episode number
        @type episode: int 
        '''
        
        environment.reset()
        agent.startEpisode()
        # print("BEGINNING EPISODE: " + str(episode) + "\n")
        self.setStatus("Q-Learning: Running episode {}/{}".format(episode, self.totalEpisodes))
        while True:
    
            # DISPLAY CURRENT STATE
            state = environment.getCurrentState()
    
            # END IF IN A TERMINAL STATE
            actions = environment.getPossibleActions(state)
            if len(actions) == 0:
                # print("EPISODE " + str(episode) + " COMPLETE.\n")
                return 
    
            # GET ACTION (USUALLY FROM AGENT)
            action = agent.getAction(state)
            if action == None:
                raise 'Error: Agent returned None action'
    
            # EXECUTE ACTION
            nextState, reward = environment.doAction(action)
            # print("Started in state: " + str(state) + "\nTook action: " + str(action) + "\nEnded in state: " + str(nextState) + "\nGot reward: " + str(reward) + "\n")
            # UPDATE LEARNER
            agent.update(state, action, nextState, reward)
    
        agent.stopEpisode()
       

class MazeEnvironment():
    '''
    Environment simulator for Maze. Provides functions for agent to perform actions in it 
    and receive reward and next state. 
    '''

    def __init__(self, mazeWorld):
        '''
        
        @param mazeWorld: handle to mazeWorld that provides startState, possibleActions in a given state and next state for a given action
        @type mazeWorld: grid.ai.rl.value_iteration.MazeWorld
        '''
        
        self.mazeWorld = mazeWorld
        self.reset()

    def reset(self):
        '''
        Reset the agent in the env. Is invoked before every episode
        '''
        
        self.state = self.mazeWorld.getStartState()
        
    def getCurrentState(self):
        '''
        Return the current state (location) of robot in the env.
        '''
        
        return self.state

    def getPossibleActions(self, state):
        '''
        Return the possible actions from the given state (location). Basically returns the openings in wall in that cell
        
        @param state: tuple of (x, y) cooridnates of the given state (location)
        @type state: tuple
        '''
        
        return self.mazeWorld.getPossibleActions(state)

    def doAction(self, action):
        '''
        Take action in the env, receive reward and nextState
        
        @param action: Direction of movement in Maze. Up, Down, Right, Left
        @type action: grid.model.maze_model.Direction
        '''
        
        state = self.getCurrentState()
        (nextState, reward) = self.getRandomNextState(state, action)
        self.state = nextState
        return (nextState, reward)

    def getRandomNextState(self, state, action):
        '''
        Get next state by performing an action in current state
        
        @param state: current state tuple (x, y)
        @type state: tuple
        @param action: Direction of movement in Maze. Up, Down, Right, Left
        @type action: grid.model.maze_model.Direction
        '''
        
        successor = self.mazeWorld.getTransitionStatesAndProbs(state, action)
        nextState, prob = successor[0]
        reward = self.mazeWorld.getReward(state, action, nextState)
        return (nextState, reward)
    
class QLearningAgent():
    '''
      Q-Learning Agent. Takes action in MazeEnvironment and receives rewards - QLearning.
    '''
    
    def __init__(self, mdp, maze_model, alpha=0.5, gamma=0.9, epsilon=0.3):
        '''
        Initialize QLearningAgent
        
        @param mdp: handle to mazeWorld that provides startState, possibleActions in a given state and next state for a given action
        @type mdp: grid.ai.rl.value_iteration.MazeWorld
        @param maze_model: handle to maze_model that provides information about cells explored, walls etc
        @type maze_model: grid.model.maze_model.MazeModel
        @param alpha: Learning Rate
        @type alpha: float
        @param gamma: Discount Rate
        @type gamma: float
        @param epsilon: Exploration Factor
        @type epsilon: float
        '''
        
        self.mdp = mdp
        self.maze_model = maze_model
        self.qValues = Counter()
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        
        # print "LEARNING RATE", self.alpha
        # print "DISCOUNT", self.gamma
        # print "EXPLORATION", self.epsilon

    def getQValue(self, state, action):
        '''
        Returns Q(state,action). Returns 0.0 if we have never seen a state or the Q node value otherwise
        
        @param state: given tuple state (location) of robot
        @type state: tuple
        @param action: Direction of movement in Maze. Up, Down, Right, Left
        @type action: grid.model.maze_model.Direction
        '''

        return self.qValues[(state, action)]

    def computeValueFromQValues(self, state):
        '''
        Returns max_action Q(state,action) where the max is over legal actions.  Note that if there 
        are no legal actions, which is the case at the terminal state, we return a value of 0.0.
          
        @param state: given tuple state (location) of robot
        @type state: tuple
        '''
        
        possibleStateQValues = Counter()
        for action in self.mdp.getPossibleActions(state):
            possibleStateQValues[action] = self.getQValue(state, action)
        
        return possibleStateQValues[possibleStateQValues.argMax()]

    def computeActionFromQValues(self, state):
        '''
        Compute the best action to take in a state.  Note that if there are no legal actions, 
        which is the case at the terminal state, we return None.
          
        @param state: given tuple state (location) of robot
        @type state: tuple
        '''
        possibleStateQValues = Counter()
        possibleActions = self.mdp.getPossibleActions(state)
        if len(possibleActions) == 0:
            return None
        
        for action in possibleActions:
            possibleStateQValues[action] = self.getQValue(state, action)
        
        if possibleStateQValues.totalCount() == 0:
            return random.choice(possibleActions)
        else:
            return possibleStateQValues.argMax()

    def getAction(self, state):
        '''
        Compute the action to take in the current state.  With probability self.epsilon, 
        we take a random action and take the best policy action otherwise.  Note 
        that if there are no legal actions, which is the case at the terminal state, we
        choose None as the action.
        
        @param state: given tuple state (location) of robot
        @type state: tuple
        '''
        # Pick Action
        legalActions = self.mdp.getPossibleActions(state)
        action = None

        if len(legalActions) > 0:
            if flipCoin(self.epsilon):
                action = random.choice(legalActions)
            else:
                action = self.getPolicy(state)
        
        return action
        
    def update(self, state, action, nextState, reward):
        '''
        The parent class calls this to observe a state = action => nextState and reward transition. 
        We do our Q-Value update here
          
        @param state: given tuple state (location) of robot
        @type state: tuple
        @param action: Direction of movement in Maze. Up, Down, Right, Left
        @type action: grid.model.maze_model.Direction
        @param nextState: next resulting state of robot after taking action
        @type nextState: tuple
        @param reward: reward received from current state by taking action
        @type reward: float
        '''
        
        # print "State: ", state, " , Action: ", action, " , NextState: ", nextState, " , Reward: ", reward
        # print "QVALUE", self.getQValue(state, action)
        # print "VALUE", self.getValue(nextState)
        self.qValues[(state, action)] = self.getQValue(state, action) + self.alpha * (reward + self.gamma * self.getValue(nextState) - self.getQValue(state, action))

    def getPolicy(self, state):
        '''
        Return the computed policy (Direction of movement) from the given state
        
        @param state: given tuple state (location) of robot
        @type state: tuple
        '''
        
        return self.computeActionFromQValues(state)

    def getValue(self, state):
        '''
        Return the Value for the given state. It is computed from QValues by argmax
        
        @param state: given tuple state (location) of robot
        @type state: tuple
        '''
        
        return self.computeValueFromQValues(state)

    def startEpisode(self):
        '''
          Called by environment when new episode is starting
        '''
        self.lastState = None
        self.lastAction = None

    def stopEpisode(self):
        '''
          Called by environment when episode is done
        ''''''
        Return dict of policy for every cell in the maze 
        '''
        self.episodesSoFar += 1
        if self.episodesSoFar >= self.numTraining:
            # Take off the training wheels
            self.epsilon = 0.0  # no exploration
            self.alpha = 0.0  # no learning

    def getValues(self):
        '''
        Return Q-Values table
        '''
        
        return self.qValues
    
    def getFullPolicy(self):
        '''
        Return dict of policy for every cell in the maze 
        '''
        
        policy = {}
        for x in range(self.maze_model.dim):
            for y in range(self.maze_model.dim):
                if self.maze_model.hasExplored([x, y]):
                    state = (x, y)
                    action = self.getPolicy(state)
                    if type(action) == Direction:
                        policy[state] = action.value
                    else:
                        policy[state] = action
        return policy
    

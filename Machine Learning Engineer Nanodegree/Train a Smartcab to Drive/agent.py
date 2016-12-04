import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
from operator import itemgetter

import numpy as np
import pandas as pd

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        
        # TODO: Initialize any additional variables here
        self.actions = [None, 'forward', 'left', 'right']
        self.q = {}
        self.alpha = -1
        self.gamma = -1
        self.epsilon = 0.01
        self.lastState = None
        self.lastAction = None
        self.run_mode = None
        self.enforce_deadline = False

        self.trial_num = 0
        self.report_stats = [] # collect data for visualization and reporting

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

    def update(self, t):
        
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = (inputs['light'], inputs['left'], inputs['oncoming'], self.next_waypoint)
        
        # TODO: Select action according to your policy
        if self.run_mode == 'random-actions':
            action = random.choice(self.actions)
        else:
            action = self.chooseAction(self.state)

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        if self.run_mode != 'random-actions':
            self.updateQ(self.lastState, self.lastAction, reward, self.state)

        self.lastState = self.state
        self.lastAction = action

        # print "LearningAgent.update(): t={}, deadline = {}, next_waypoint = {}, inputs = {}, action = {}, reward = {}".format(t, deadline, self.next_waypoint, inputs, action, reward)  # [debug]

        ## All lines below this - Added by me
        ## Collect data for visualization and reporting
        step_num = t
        if step_num == 0:
            self.trial_num = self.trial_num + 1

        self.collectStats(self.trial_num, step_num, deadline, inputs, self.next_waypoint, action, reward)

    # This is a new function added by me
    def collectStats(self, trial_num, step_num, deadline, inputs, next_waypoint, action, reward):
        """collect execution stats that will be later used for analysis."""

        # Collect data for visualization and reporting
        d = {
            'trial_num': trial_num,
            'step_num' : step_num,
            'deadline': deadline,
            'light': str(inputs['light']),
            'traffic_left': str(inputs['left']),
            'traffic_right' : str(inputs['right']),
            'traffic_oncoming' : str(inputs['oncoming']),
            'next_waypoint': str(next_waypoint),
            'action': str(action),
            'reward': reward
            }
        
        self.report_stats.append(pd.Series(d))

    # This is a new function added by me
    def genReport(self):
        """save collected execution stats to csv for analysis in jupyter."""

        report_df = pd.DataFrame(self.report_stats)

        # export to csv to be explored later in jupyter
        filename = "{}_{}_{}_{}.csv".format(self.run_mode, self.enforce_deadline, self.alpha, self.gamma)
        report_df.to_csv(filename, index=False)
        
    def getQ(self, state, action):
        """retunr the q value for the given state and action"""

        return self.q.get((state, action), 0.0)

    def chooseAction(self, state):
        """return the best possible action for the given state"""

        if random.random() < self.epsilon:
            action = random.choice(self.actions)
        else:
            q = [self.getQ(state, a) for a in self.actions]
            maxQ = max(q)
            count = q.count(maxQ)
            if count > 1:
                best = [i for i in range(len(self.actions)) if q[i] == maxQ]
                i = random.choice(best)
            else:
                i = q.index(maxQ)

            action = self.actions[i]
        return action

    def updateQ(self, lastState, lastAction, reward, newState):
        """update q value for lastState, lastAction pair"""

        maxqnew = max([self.getQ(newState, a) for a in self.actions])
        value = reward + self.gamma * maxqnew

        oldValue = self.q.get((lastState, lastAction), None)

        if oldValue is None:
            self.q[(lastState, lastAction)] = reward
        else:
            self.q[(lastState, lastAction)] = oldValue + self.alpha * ((value) - oldValue)


    def setRunParameters(self, run_mode="NA", enforce_deadline=False, alpha=0.0, gamma=0.0):
        """set different run parameters. used while tuning the parameters"""

        self.alpha = alpha
        self.gamma = gamma
        self.run_mode = run_mode
        self.enforce_deadline = enforce_deadline

def run(enforce_deadline=False, run_mode="NA", alpha=0.0, gamma=0.0):
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent

    # set agent parameters
    a.setRunParameters(run_mode, enforce_deadline, alpha, gamma)

    e.set_primary_agent(a, enforce_deadline=enforce_deadline)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.0, display=False)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line

    # This is a new function added by me
    # generate report
    a.genReport()

    
# This is a new function added by me
def execute():
    """Run the agent with different parameters."""

    parameters = {
        'random-actions'   : { 'enforce_deadline' : False, 'alphas': [0.0], 'gammas': [0.0] },
        'basic-q-learning' : { 'enforce_deadline' : False,  'alphas': [0.1], 'gammas': [0.4] },
        'tuned-q-learning' : { 'enforce_deadline' : True,  'alphas': [0.01, 0.1, 0.3, 0.5, 0.7, 0.9], 'gammas': [0.1, 0.3, 0.5, 0.7, 0.9, 0.98] }
        }


    for run_mode in parameters:

        run_parameters = parameters[run_mode]

        enforce_deadline = run_parameters['enforce_deadline']
        alphas = run_parameters['alphas']
        gammas = run_parameters['gammas']

        for alpha in alphas:
            for gamma in gammas:
                run(enforce_deadline, run_mode, alpha, gamma)

    print "Done!"

if __name__ == '__main__':
    execute()

import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

import numpy as np
import pandas as pd

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        
        # TODO: Initialize any additional variables here
        self.q_table = {}
        self.alpha = -1
        self.gamma = -1
        self.run_mode = None

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
        self.state = {'light': inputs['light'], 'left': inputs['left'], 'oncoming': inputs['oncoming'], 'next_waypoint': self.next_waypoint}
        
        # TODO: Select action according to your policy
        if self.run_mode == 'random-actions':
            action = random.choice([None, 'forward', 'left', 'right'])
        else:
            action = self.select_action()

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        if self.run_mode != 'random-actions':
            self.update_q(action=action, reward=reward)

        # print "LearningAgent.update(): t={}, deadline = {}, next_waypoint = {}, inputs = {}, action = {}, reward = {}".format(t, deadline, self.next_waypoint, inputs, action, reward)  # [debug]

        ## All lines below this - Added by me
        ## Collect data for visualization and reporting
        if t == 0:
            self.trial_num = self.trial_num + 1

        self.collect_stats(self.trial_num, deadline, inputs, self.next_waypoint, action, reward)

    # This is a new function added by me
    def collect_stats(self, trial_num, deadline, inputs, next_waypoint, action, reward):
        """collect execution stats that will be later used for analysis."""

        # Collect data for visualization and reporting
        d = {
            'trial_num': trial_num,
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
    def gen_report(self):
        """save collected execution stats to csv for analysis in jupyter."""

        report_df = pd.DataFrame(self.report_stats)

        # export to csv to be explored later in jupyter
        filename = "{}_{}_{}.csv".format(self.run_mode, self.alpha, self.gamma)
        report_df.to_csv(filename, index=False)
        
    # This is a new function added by me
    def table_key(self, action=None):
        """my q-table is a dictionary (instead of 2d array). this function builds the dictionary key"""

        light = self.state['light']
        left = self.state['left']
        oncoming = self.state['oncoming']
        next_waypoint = self.state['next_waypoint']

        return "{}:{}:{}:{}:{}".format(light, left, oncoming, next_waypoint, action)

    # This is a new function added by me
    def q_value(self, action=None):
        """return the q-value from the q-table for the given action."""

        key = self.table_key(action=action)

        if key in self.q_table.keys():
            return self.q_table[key]
        else:
            return 0

    # This is a new function added by me
    def select_action(self):
        """return the best-action in the current state"""

        wait = self.q_value(action=None)

        go = self.q_value(action=self.state['next_waypoint'])

        if go >= wait:
            return self.state['next_waypoint']
        else:
            return None

    # This is a new function added by me
    def max_q(self):
        """return the max q-value in the current state"""

        q_values = []
        
        for action in [None, 'left', 'right', 'forward']:
            q_values.append(self.q_value(action=action))

        return max(q_values)

    # This is a new function added by me
    def update_q(self, action=None, reward=0.0):
        """update the q-table value for the given action in the current state after applying q-learning"""

        old_value = self.q_value(action=action)

        new_value = old_value * (1 - self.alpha) + self.alpha * (reward + self.gamma * self.max_q())

        key = self.table_key(action=action)

        self.q_table[key] = new_value

    def set_run_parameters(self, run_mode="NA", alpha=0.0, gamma=0.0):
        """set different run parameters. used while tuning the parameters"""

        self.alpha = alpha
        self.gamma = gamma
        self.run_mode = run_mode

def run(enforce_deadline=False, run_mode="NA", alpha=0.0, gamma=0.0):
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent

    # set agent parameters
    a.set_run_parameters(run_mode, alpha, gamma)

    e.set_primary_agent(a, enforce_deadline=enforce_deadline)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=1.0, display=False)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line

    # This is a new function added by me
    # generate report
    a.gen_report()

    
# This is a new function added by me
def execute():
    """Run the agent with different parameters."""

    parameters = {
        'random-actions'   : { 'enforce_deadline' : False, 'alphas': [0.0], 'gammas': [0.0] },
        'basic-q-learning' : { 'enforce_deadline' : True,  'alphas': [0.4], 'gammas': [0.4] },
        'tuned-q-learning' : { 'enforce_deadline' : True,  'alphas': [0.1, 0.3, 0.5, 0.7, 0.9], 'gammas': [0.1, 0.3, 0.5, 0.7, 0.9] },
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

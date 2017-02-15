
from helpers.planning_problem import PlanningProblem
from helpers.lp_utils import FluentState, encode_state, decode_state, run_search

from aimacode.logic import PropKB
from aimacode.planning import Action
from aimacode.search import InstrumentedProblem, Node
from aimacode.search import breadth_first_search, astar_search, breadth_first_tree_search
from aimacode.search import depth_first_graph_search, uniform_cost_search, greedy_best_first_graph_search
from aimacode.search import depth_limited_search, recursive_best_first_search
from aimacode.utils import expr

from my_planning_graph import PlanningGraph


class AirCargoProblem(PlanningProblem):

    def __init__(self, cargos, planes, airports, initial: FluentState, goal: list):
        self.cargos = cargos
        self.planes = planes
        self.airports = airports
        PlanningProblem.__init__(self, initial, goal)

    def get_actions(self):
        '''
        This method creates concrete actions for all actions in the problem
        domain. It is computationally expensive to call this method directly;
        however, it is called in the PlanningProblem constructor and the
        results cached in the `actions_list` property inherited by all
        PlanningProblem subclasses.

        Returns:
        ----------
        list<Action>
            list of Action objects
        '''
        #TODO Part 2 create concrete actions for the problem instance based on the domain actions: Load, Unload, and Fly

        def load_actions():
            '''Create all concrete Load actions and return a list

            :return: list of Action objects
            '''
            loads = []
            # TODO Part 2 using instance variables, create all load ground actions from the domain Load action
            for c in self.cargos:
                for p in self.planes:
                    for a in self.airports:
                        precond_pos = [expr("At({}, {})".format(c, a)),
                                       expr("At({}, {})".format(p, a)),
                                       ]
                        precond_neg = []
                        effect_add = [expr("In({}, {})".format(c, p))]
                        effect_rem = [expr("At({}, {})".format(c, a))]
                        load = Action(expr("Load({}, {}, {})".format(c, p, a)),
                                      [precond_pos, precond_neg],
                                      [effect_add, effect_rem])
                        loads.append(load)
            return loads

        def unload_actions():
            '''Create all concrete Unload actions and return a list

            :return: list of Action objects
            '''
            unloads = []
            # TODO Part 2 using instance variables, create all Unload ground actions from the domain Unload action
            for c in self.cargos:
                for p in self.planes:
                    for a in self.airports:
                        precond_pos = [expr("In({}, {})".format(c, p)),
                                       expr("At({}, {})".format(p, a)),
                                       ]
                        precond_neg = []
                        effect_add = [expr("At({}, {})".format(c, a))]
                        effect_rem = [expr("In({}, {})".format(c, p))]
                        unload = Action(expr("Unload({}, {}, {})".format(c, p, a)),
                                        [precond_pos, precond_neg],
                                        [effect_add, effect_rem])
                        unloads.append(unload)
            return unloads

        def fly_actions():
            '''Create all concrete Fly actions and return a list

            :return: list of Action objects
            '''
            flys = []
            # TODO Part 2 using instance variables, create all Fly ground actions from the domain Fly action
            for f in self.airports:
                for p in self.planes:
                    for to in self.airports:
                        if f != to:
                            precond_pos = [expr("At({}, {})".format(p, f)),
                                           ]
                            precond_neg = []
                            effect_add = [expr("At({}, {})".format(p, to))]
                            effect_rem = [expr("At({}, {})".format(p, f))]
                            fly = Action(expr("Fly({}, {}, {})".format(p, f, to)),
                                         [precond_pos, precond_neg],
                                         [effect_add, effect_rem])
                            flys.append(fly)
            return flys

        return load_actions() + unload_actions() + fly_actions()

    def actions(self, state: str) -> list:
        # TODO Part 2 implement (see PlanningProblem in helpers.planning_problem)
        possible_actions = []
        kb = PropKB()
        kb.tell(decode_state(state, self.state_map).pos_sentence())
        for action in self.actions_list:
            is_possible = True
            for clause in action.precond_pos:
                if clause not in kb.clauses:
                    is_possible = False
            for clause in action.precond_neg:
                if clause in kb.clauses:
                    is_possible = False
            if is_possible:
                possible_actions.append(action)
        return possible_actions

    def result(self, state: str, action: Action):
        # TODO implement (see PlanningProblem in helpers.planning_problem)
        new_state = FluentState([], [])
        old_state = decode_state(state, self.state_map)
        for fluent in old_state.pos:
            if fluent not in action.effect_rem:
                new_state.pos.append(fluent)
        for fluent in action.effect_add:
            if fluent not in new_state.pos:
                new_state.pos.append(fluent)
        for fluent in old_state.neg:
            if fluent not in action.effect_add:
                new_state.neg.append(fluent)
        for fluent in action.effect_rem:
            if fluent not in new_state.neg:
                new_state.neg.append(fluent)
        return encode_state(new_state, self.state_map)

    def goal_test(self, state: str) -> bool:
        kb = PropKB()
        kb.tell(decode_state(state, self.state_map).pos_sentence())
        for clause in self.goal:
            if clause not in kb.clauses:
                return False
        return True

    def h_1(self, node: Node):
        # note that this is not a true heuristic
        h_const = 1
        return h_const

    def h_pg_setlevel(self, node: Node):
        '''
        This heuristic uses a planning graph representation of the problem
        state space to estimate the minimum number of actions that must be
        carried out from the current state in order to satisfy all of the goal
        conditions.
        '''
        # TODO: Complete the implmentation of this heuristic in the 
        # PlanningGraph class
        pg = PlanningGraph(self, node.state)
        pg_setlevel = pg.h_setlevel()
        return pg_setlevel

    def h_pg_levelsum(self, node: Node):
        '''
        This heuristic uses a planning graph representation of the problem
        state space to estimate the sum of all actions that must be carried
        out from the current state in order to satisfy each individual goal
        condition.
        '''
        # TODO: Complete the implmentation of this heuristic in the 
        # PlanningGraph class
        pg = PlanningGraph(self, node.state)
        pg_levelsum = pg.h_levelsum()
        return pg_levelsum

    def h_ignore_preconditions(self, node: Node):
        '''
        This heuristic estimates the minimum number of actions that must be
        carried out from the current state in order to satisfy all of the goal
        conditions by ignoring the preconditions required for an action to be
        executed.
        '''
        # TODO Part 3 implement (see Russell-Norvig Edition-3 10.2.3  or Russell-Norvig Edition-2 11.2)
        count = 0
        for i, fluent in enumerate(self.state_map):
            # count number of fluents not correct
            if fluent in self.goal:
                if node.state[i] == 'F':
                    count += 1
        # print("Count = {}".format(count))
        return count

def air_cargo_p1()->AirCargoProblem:
    cargos = ['C1', 'C2']
    planes = ['P1', 'P2']
    airports = ['JFK', 'SFO']
    pos = [expr('At(C1, SFO)'),
           expr('At(C2, JFK)'),
           expr('At(P1, SFO)'),
           expr('At(P2, JFK)'),
           ]
    neg = [expr('At(C2, SFO)'),
           expr('In(C2, P1)'),
           expr('In(C2, P2)'),
           expr('At(C1, JFK)'),
           expr('In(C1, P1)'),
           expr('In(C1, P2)'),
           expr('At(P1, JFK)'),
           expr('At(P2, SFO)'),
           ]
    init = FluentState(pos, neg)
    goal = [expr('At(C1, JFK)'),
            expr('At(C2, SFO)'),
            ]
    return AirCargoProblem(cargos, planes, airports, init, goal)

def air_cargo_p2()->AirCargoProblem:
    # TODO Part 2 implement Problem 2 definition
    cargos = ['C1', 'C2', 'C3']
    planes = ['P1', 'P2', 'P3']
    airports = ['JFK', 'SFO', 'ATL']
    pos = [expr('At(C1, SFO)'),
           expr('At(C2, JFK)'),
           expr('At(P1, SFO)'),
           expr('At(P2, JFK)'),
           expr('At(C3, ATL)'),
           expr('At(P3, ATL)'),
           ]
    neg = [expr('At(C2, SFO)'),
           expr('At(C2, ATL)'),
           expr('In(C2, P1)'),
           expr('In(C2, P2)'),
           expr('In(C2, P3)'),
           expr('At(C1, JFK)'),
           expr('At(C1, ATL)'),
           expr('In(C1, P1)'),
           expr('In(C1, P2)'),
           expr('In(C1, P3)'),
           expr('At(P1, JFK)'),
           expr('At(P1, ATL)'),
           expr('At(P2, SFO)'),
           expr('At(P2, ATL)'),
           expr('At(P3, SFO)'),
           expr('At(P3, JFK)'),
           expr('At(C3, SFO)'),
           expr('At(C3, JFK)'),
           expr('In(C3, P1)'),
           expr('In(C3, P2)'),
           expr('In(C3, P3)'),
           ]
    init = FluentState(pos, neg)
    goal = [expr('At(C1, JFK)'),
            expr('At(C2, SFO)'),
            expr('At(C3, SFO)'),
            ]
    return AirCargoProblem(cargos, planes, airports, init, goal)

def air_cargo_p3()->AirCargoProblem:
    # TODO Part 2 implement Problem 3 definition
    cargos = ['C1', 'C2', 'C3', 'C4']
    planes = ['P1', 'P2']
    airports = ['JFK', 'SFO', 'ATL', 'ORD']
    pos = [
        expr('At(C1, SFO)'),
        expr('At(C2, JFK)'),
        expr('At(C3, ATL)'),
        expr('At(C4, ORD)'),
        expr('At(P1, SFO)'),
        expr('At(P2, JFK)'),
    ]
    neg = [
        expr('At(C1, JFK)'),
        expr('At(C1, ATL)'),
        expr('At(C1, ORD)'),
        expr('At(C2, SFO)'),
        expr('At(C2, ATL)'),
        expr('At(C2, ORD)'),
        expr('At(C3, JFK)'),
        expr('At(C3, SFO)'),
        expr('At(C3, ORD)'),
        expr('At(C4, SFO)'),
        expr('At(C4, ATL)'),
        expr('At(C4, JFK)'),
        expr('In(C1, P1)'),
        expr('In(C1, P2)'),
        expr('In(C2, P1)'),
        expr('In(C2, P2)'),
        expr('In(C3, P1)'),
        expr('In(C3, P2)'),
        expr('In(C4, P1)'),
        expr('In(C4, P2)'),
        expr('At(P1, JFK)'),
        expr('At(P1, ATL)'),
        expr('At(P1, ORD)'),
        expr('At(P2, SFO)'),
        expr('At(P2, ATL)'),
        expr('At(P2, ORD)'),
    ]
    init = FluentState(pos, neg)
    goal = [
        expr('At(C1, JFK)'),
        expr('At(C2, SFO)'),
        expr('At(C3, JFK)'),
        expr('At(C4, SFO)'),
    ]
    return AirCargoProblem(cargos, planes, airports, init, goal)

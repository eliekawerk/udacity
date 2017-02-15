from aimacode.planning import PDLL
from aimacode.planning import Action
from aimacode.utils import expr

# this method not included with student code
def ac_actions():
    ## Actions
    #  Load
    precond_pos = [expr("At(c, a)"), expr("At(p, a)"), expr("Cargo(c)"), expr("Plane(p)"), expr("Airport(a)")]
    precond_neg = []
    effect_add = [expr("In(c, p)")]
    effect_rem = [expr("At(c, a)")]
    load = Action(expr("Load(c, p, a)"), [precond_pos, precond_neg], [effect_add, effect_rem])

    #  Unload
    precond_pos = [expr("In(c, p)"), expr("At(p, a)"), expr("Cargo(c)"), expr("Plane(p)"), expr("Airport(a)")]
    precond_neg = []
    effect_add = [expr("At(c, a)")]
    effect_rem = [expr("In(c, p)")]
    unload = Action(expr("Unload(c, p, a)"), [precond_pos, precond_neg], [effect_add, effect_rem])

    #  Fly
    precond_pos = [expr("At(p, f)"), expr("Plane(p)"), expr("Airport(f)"), expr("Airport(t)")]
    precond_neg = []
    effect_add = [expr("At(p, t)")]
    effect_rem = [expr("At(p, f)")]
    fly = Action(expr("Fly(p, f, t)"), [precond_pos, precond_neg], [effect_add, effect_rem])

    return [load, unload, fly]

def acp1_pddl() -> PDLL:
    """Definition for Problem 1

        2 cargo items: {C1, C2}
        2 airplanes: {P1, P2}
        2 airports: {SFO, JFK}
        initial: C1 and P1 are at SFO, P2 and C2 are at JFK
        goal: C1 at JFK, C2 at SFO
        """

    init = [
        # TODO define the initial state as a list of fluent expressions
        expr('At(C1, SFO)'),
        expr('At(C2, JFK)'),
        expr('At(P1, SFO)'),
        expr('At(P2, JFK)'),
        expr('Cargo(C1)'),
        expr('Cargo(C2)'),
        expr('Plane(P1)'),
        expr('Plane(P2)'),
        expr('Airport(JFK)'),
        expr('Airport(SFO)')
    ]

    def goal_test(kb):
        required = [
            # TODO define the goal test requirements as a list of fluent expressions
            expr('At(C1 , JFK)'),
            expr('At(C2 ,SFO)'),
        ]
        for q in required:
            if kb.ask(q) is False:
                return False
        return True

    ## Actions
    # TODO define the load, Unload, and Fly actions using first order logic and the Action class
    # Hint: take a look at the aimacode.planning module in the code base

    #  Load
    # load = Action(expr("Load(c, p, a)"), [precond_pos, precond_neg], [effect_add, effect_rem])

    #  Unload
    # unload = Action(expr("Unload(c, p, a)"), [precond_pos, precond_neg], [effect_add, effect_rem])

    #  Fly
    # fly = Action(expr("Fly(p, f, t)"), [precond_pos, precond_neg], [effect_add, effect_rem])

    # return PDLL(init, [load, unload, fly], goal_test)


    return PDLL(init, ac_actions(), goal_test)


def acp2_pddl() -> PDLL:
    """Definition for Problem 2

        3 cargo items: {C1, C2, C3}
        3 airplanes: {P1, P2, P3}
        3 airports: {SFO, JFK, ATL}
        initial: C1 and P1 are at SFO, C2 and P2 are at JFK, C3 and P3 are at ATL
        goal: C1 at JFK, C2 at SFO, C3 at SFO
        """
    # TODO implement problem 2
    init = [expr('At(C1, SFO)'),
            expr('At(C2, JFK)'),
            expr('At(C3, ATL)'),
            expr('At(P1, SFO)'),
            expr('At(P2, JFK)'),
            expr('At(P3, ATL)'),
            expr('Cargo(C1)'),
            expr('Cargo(C2)'),
            expr('Cargo(C3)'),
            expr('Plane(P1)'),
            expr('Plane(P2)'),
            expr('Plane(P3)'),
            expr('Airport(ATL)'),
            expr('Airport(JFK)'),
            expr('Airport(SFO)')]

    def goal_test(kb):
        required = [
            expr('At(C1, JFK)'),
            expr('At(C2, SFO)'),
            expr('At(C3, SFO)'),
        ]
        for q in required:
            if kb.ask(q) is False:
                return False
        return True

    return PDLL(init, ac_actions(), goal_test)


def acp3_pddl() -> PDLL:
    """Definition for Problem 3

        4 cargo items: {C1, C2, C3, C4}
        2 airplanes: {P1, P2}
        4 airports: {SFO, JFK, ATL, ORD}
        initial: C1 and P1 are at SFO, C2 and P2 are at JFK, C3 at ATL, C4 at ORD
        goal: C1, C3 at JFK, C2, C4 at SFO
        """
    # TODO implement problem 3
    init = [expr('At(C1, SFO)'),
            expr('At(C2, JFK)'),
            expr('At(C3, ATL)'),
            expr('At(C4, ORD)'),
            expr('At(P1, SFO)'),
            expr('At(P2, JFK)'),
            expr('Cargo(C1)'),
            expr('Cargo(C2)'),
            expr('Cargo(C3)'),
            expr('Cargo(C4)'),
            expr('Plane(P1)'),
            expr('Plane(P2)'),
            expr('Airport(ORD)'),
            expr('Airport(ATL)'),
            expr('Airport(JFK)'),
            expr('Airport(SFO)')]

    def goal_test(kb):
        required = [
            expr('At(C1, JFK)'),
            expr('At(C3, JFK)'),
            expr('At(C2, SFO)'),
            expr('At(C4, SFO)'),
            ]
        for q in required:
            if kb.ask(q) is False:
                return False
        return True

    return PDLL(init, ac_actions(), goal_test)

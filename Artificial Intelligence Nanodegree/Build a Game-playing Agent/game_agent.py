"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""
import random


def in_bounds(game, row, col):
    return 0 <= row < game.height and 0 <= col < game.width


def valid_moves(game, player):
    """
    Generate the list of possible moves for an L-shaped motion (like a
    knight in chess). EXCEPT doesn't matter if occupied
    """

    move = game.__last_player_move__[player]
    r, c = move
    directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                  (1, -2), (1, 2), (2, -1), (2, 1)]

    valid_moves = [(r + dr, c + dc) for dr, dc in directions if in_bounds(game, r + dr, c + dc)]

    return valid_moves


class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass


def custom_score(game, player):  # formerly class CustomEval
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    ----------
    float
        The heuristic value of the current game state to the specified player.
    """

    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    bonus = 0.

    center = (int(game.width/2), int(game.height/2))
    r, c = center
    directions = [(-1, -2), (-1, 2), (1, -2), (1, 2),
                  (2, -1), (2, 1), (-2, -1), (-2, 1)]

    off_center = [(r + dr, c + dc) for dr, dc in directions if in_bounds(game, r + dr, c + dc)]
    player_location = game.get_player_location(player)
    if player_location == center:
        bonus = 1.5
    elif player_location in off_center:
            bonus = 0.5
    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    return float(own_moves - opp_moves) + bonus


def boxed_improved_score(game, player):  # formerly class BoxedImproved
    """
    Calculate the heuristic value of a game state from the point of view of
    the given player.
    determines self and opponent differnce of
    number of legal moves / valid moves; edges have fewer valid moves


    Args:
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : hashable
        One of the objects registered by the game object as a valid player.
        (i.e., `player` should be either game.__player_1__ or
        game.__player_2__).

    Returns:
    ----------
    float
        The heuristic value of the current game state.
    """

    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    own_ratio = float(len(game.get_legal_moves(player)))/float(len(valid_moves(game, player)))
    opp_ratio = float(len(game.get_legal_moves(player)))/float(len(valid_moves(game, game.get_opponent(player))))
    return own_ratio - opp_ratio


def boxed_ratio_score(game, player): # formerly class BoxedRatio
    """
    Calculate the heuristic value of a game state from the point of view of
    the given player.

    Args:
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : hashable
        One of the objects registered by the game object as a valid player.
        (i.e., `player` should be either game.__player_1__ or
        game.__player_2__).

    Returns:
    ----------
    float
        The heuristic value of the current game state.
    """

    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    return float(len(game.get_legal_moves(player)))/float(len(valid_moves(game, player)))


def runaway_score(game, player):  # formerly class RunAway
    """
    Calculate the heuristic value of a game state from the point of view of
    the given player.
    Determines Manhattan distance from player to oppornent

    Args:
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : hashable
        One of the objects registered by the game object as a valid player.
        (i.e., `player` should be either game.__player_1__ or
        game.__player_2__).

    Returns:
    ----------
    float
        The heuristic value of the current game state.
    """

    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    own_location = game.get_player_location(player)
    opp_location = game.get_player_location(game.get_opponent(player))
    distance = abs(own_location[0]-opp_location[0]) + abs(own_location[1]-opp_location[1])
    return float(distance)


def centerbias_score(game, player):  # formerly class CenterBias
    """
    Calculate the heuristic value of a game state from the point of view of
    the given player.
    Determines Manhattan distance from player to oppornent

    Args:
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : hashable
        One of the objects registered by the game object as a valid player.
        (i.e., `player` should be either game.__player_1__ or
        game.__player_2__).

    Returns:
    ----------
    float
        The heuristic value of the current game state.
    """

    # TODONE: finish this function!
    # improved on improved by biasing to use dominant center position if possible

    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    bonus = 0.

    center = (int(game.width/2), int(game.height/2))
    r, c = center
    directions = [(-1, -2), (-1, 2), (1, -2), (1, 2),
                  (2, -1), (2, 1), (-2, -1), (-2, 1)]

    off_center = [(r + dr, c + dc) for dr, dc in directions if in_bounds(game, r + dr, c + dc)]
    player_location = game.get_player_location(player)
    if player_location == center:
        bonus = 1.5
    elif player_location in off_center:
            bonus = 0.5
    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    return float(own_moves - opp_moves) + bonus


class CustomPlayer:
    """Game-playing agent that chooses a move using your evaluation function
    and a depth-limited minimax algorithm with alpha-beta pruning. You must
    finish and test this player to make sure it properly uses minimax and
    alpha-beta to return a good move before the search time limit expires.

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    iterative : boolean (optional)
        Flag indicating whether to perform fixed-depth search (False) or
        iterative deepening search (True).

    method : {'minimax', 'alphabeta'} (optional)
        The name of the search method to use in get_move().

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """

    def __init__(self, search_depth=3, score_fn=custom_score,
                 iterative=True, method='minimax', timeout=10.):
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout

    def get_move(self, game, legal_moves, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        This function must perform iterative deepening if self.iterative=True,
        and it must use the search method (minimax or alphabeta) corresponding
        to the self.method value.

        **********************************************************************
        NOTE: If time_left < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        legal_moves : list<(int, int)>
            A list containing legal moves. Moves are encoded as tuples of pairs
            of ints defining the next (row, col) for the agent to occupy.

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        ----------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """

        self.time_left = time_left

        # TODO: finish this function!
        best_move = (-1, -1)
        if game.move_count < 2:
            return random.choice(legal_moves)

        if not legal_moves:
            return (-1, -1)

        # Perform any required initializations, including selecting an initial
        # move from the game board (i.e., an opening book)
        depth = 1 if self.iterative else self.search_depth

        try:
            # The search method call (alpha beta or minimax) should happen in
            # here in order to avoid timeout. The try/except block will
            # automatically catch the exception raised by the search method
            # when the timer gets close to expiring
            new_move = best_move
            while True:

                if self.method == "minimax":
                    
                    _, new_move = self.minimax(game, depth)

                elif self.method == "alphabeta":
                    _, new_move = self.alphabeta(game, depth)

                best_move = new_move

                if not self.iterative:
                    break

                depth += 1

        except Timeout:
            # Handle any actions required at timeout, if necessary
            pass

        # Return the best move from the last completed search iteration
        return best_move

    def minimax(self, game, depth, maximizing_player=True):
        """Implement the minimax search algorithm as described in the lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        ----------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        # TODO: finish this function!
        legal_moves = game.get_legal_moves()

        if not legal_moves or depth <= 0:
            return self.score(game, self), None

        best_move = None
        if maximizing_player:
            best_value = float("-inf")
            for move in legal_moves:
                next_state = game.forecast_move(move)
                value, _ = self.minimax(next_state, depth - 1, False)
                if value > best_value:
                    best_value, best_move = value, move
        else:
            best_value = float("inf")
            for move in legal_moves:
                next_state = game.forecast_move(move)
                value, _ = self.minimax(next_state, depth - 1, True)
                if value < best_value:
                    best_value, best_move = value, move

        return best_value, best_move

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf"), maximizing_player=True):
        """Implement minimax search with alpha-beta pruning as described in the
        lectures.

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        maximizing_player : bool
            Flag indicating whether the current search depth corresponds to a
            maximizing layer (True) or a minimizing layer (False)

        Returns
        ----------
        float
            The score for the current search branch

        tuple(int, int)
            The best move for the current branch; (-1, -1) for no legal moves
        """

        # TODO: finish this function!
        if self.time_left() < self.TIMER_THRESHOLD:
            raise Timeout()

        legal_moves = game.get_legal_moves()

        if not legal_moves or depth <= 0:
            return self.score(game, self), None

        best_move = None
        if maximizing_player:
            best_value = float("-inf")
            for move in legal_moves:
                next_state = game.forecast_move(move)
                value, _ = self.alphabeta(next_state, depth - 1, alpha, beta, False)
                alpha = max(alpha, value)
                if value > best_value:
                    best_value, best_move = value, move

                if alpha >= beta:
                    break
        else:
            best_value = float("inf")
            for move in legal_moves:
                next_state = game.forecast_move(move)
                value, _ = self.alphabeta(next_state, depth - 1, alpha, beta, True)
                beta = min(beta, value)
                if value < best_value:
                    best_value, best_move = value, move

                if alpha >= beta:
                    break

        return best_value, best_move

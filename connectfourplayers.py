"""Player classes for the ConnectFour game.

A player class must implement the following methods:
    set_player_colour(self, player_colour):
        player_colour: RED or WHITE as defined connectfour.py

        This is called when a player is first created.

    propose_move(self, game_grid, player_colour):
        game_grid: instance of ConnectFour() giving current game positions

        Must return int signifying the column to which to add a disc

    receive_reward(self, reward):
        reward: integer signifying reward for last move (the higher the better)

Classes:
    RandomPlayer: Makes random but always legal moves.
    HumanPlayer: Takes input from user when deciding on move.
    AfterStatePlayer: (Abstract) base class for player classes using afterstates.
    SimpleFeaturePlayer: Uses linear function approximation on afterstates.
"""

import random
import numpy as np
import connectfour
import connectfourutils

class RandomPlayer:
    """A player making a random legal move each turn."""

    def set_player_colour(self, player_colour):
        """Ignored"""
        pass

    def propose_move(self, game_grid):
        """Propose next move.

        Args:
            game_grid: ConnectFour() game_grid with current position
            player_colour: The colour for this player

        Returns:
            The column to which to add a disc (int)
        """
        return random.choice(game_grid.legal_moves())

    def receive_reward(self, reward):
        """Record the reward for the last move.

        Being a random player, rewards are ignored.

        Args:
            reward: The reward for the last move
        """
        pass

class HumanPlayer:
    """A player taking input from user"""

    def __init__(self):
        """Init HumanPlayer()"""
        self._player_colour_string = None

    def set_player_colour(self, player_colour):
        """Register the colour of this player's discs"""
        if player_colour == connectfour.WHITE:
            self._player_colour_string = 'white'
        elif player_colour == connectfour.RED:
            self._player_colour_string = 'red'
        else:
            raise ValueError('Unhandled colour: {}'.format(player_colour))

    def propose_move(self, game_grid):
        """Propose next move.

        Args:
            game_grid: ConnectFour() game_grid with current position
            player_colour: The colour for this player

        Returns:
            The column to which to add a disc (int)
        """
        print('You a playing {}'.format(self._player_colour_string))
        print(game_grid)
        print('Choose column (0 (left) to {} (right):'.format(connectfour.COLUMNS-1))
        while True:
            try:
                user_choice = int(input())
            except ValueError:
                continue
            break

        return user_choice

    def receive_reward(self, reward):
        """Record the reward for the last move.

        Args:
            reward: The reward for the last move
        """
        pass

class AfterStatePlayer:
    """A base class for players using function approximation on state values.

    Subclasses must override:
        _state_value:
        _parameter_vector:
        _set_parameter_vector:
        _nabla_parameter_vector:
    """

    def __init__(self):
        """Init AfterStatePlayer()"""
        self._is_learning = True
        self._epsilon = 0.05
        self._alpha = 0.001
        self._player_colour = None

        self._next_afterstate_value = None
        self._next_afterstate_matrix = None
        self._last_afterstate_matrix = None
        self._last_afterstate_value = None

    def set_player_colour(self, player_colour):
        """Register the colour of this player's discs

        Args:
            player_colour: Either RED or WHITE as defined in connectfour.py
        """
        self._player_colour = player_colour

    def propose_move(self, game_grid):
        """Propose next move.

        Args:
            game_grid: ConnectFour() game_grid with current position
            player_colour: The colour for this player

        Returns:
            The column to which to add a disc (int)
        """

        potential_moves = game_grid.legal_moves()
        grid_matrix = game_grid.grid_copy()

        if self._is_learning and random.random() < self._epsilon:
            chosen_move = random.choice(potential_moves)

            # We set _last_... to None to stop learning from this move.
            self._last_afterstate_value = None
            self._last_afterstate_matrix = None

            # As it is guaranteed to be a legal move, we don't need exception protection.
            for row in range(connectfour.ROWS):
                if grid_matrix[row, chosen_move] == connectfour.EMPTY:
                    grid_matrix[row, chosen_move] = self._player_colour
                    break

            self._next_afterstate_value = self._state_value(grid_matrix)
            self._next_afterstate_matrix = grid_matrix
        else:
            best_afterstate_matrix = None
            best_afterstate_value = - np.inf

            for proposed_move in potential_moves:
                # As it is guaranteed to be a legal move, we don't need exception protection.
                for row in range(connectfour.ROWS):
                    if grid_matrix[row, proposed_move] == connectfour.EMPTY:
                        grid_matrix[row, proposed_move] = self._player_colour
                        break

                afterstate_value = self._state_value(grid_matrix)
                if afterstate_value > best_afterstate_value:
                    best_afterstate_value = afterstate_value
                    best_afterstate_matrix = grid_matrix.copy()
                    chosen_move = proposed_move

                # Back to original state
                grid_matrix[row, proposed_move] = connectfour.EMPTY

            # At this point we are guaranteed to have a best_afterstate_matrix
            # as propose_move is contractually only called when there are legal
            # moves available.

            self._next_afterstate_value = best_afterstate_value
            self._next_afterstate_matrix = best_afterstate_matrix

        return chosen_move

    def receive_reward(self, reward):
        """Record the reward for the last move.

        Args:
            reward: The reward for the last move
        """

        # Update the parameters for the self._last_afterstate_matrix state
        # unless we are explicitly not learning or it's the reward after the
        # first move in which case there is no previous afterstate.

        if self._is_learning and self._last_afterstate_matrix is not None:
            # We update the parameters based on going from self._last_afterstate_matrix
            # to self._next_afterstate_matrix. The reward input is for the transition
            # between the two (this holds true for game endings as well).

            next_value = self._next_afterstate_value + reward
            last_value = self._last_afterstate_value
            nabla_vector = self._nabla_parameter_vector(self._last_afterstate_matrix)

            delta_parameter_vector = self._alpha * (next_value - last_value) * nabla_vector
            new_parameter_vector = self._parameter_vector() + delta_parameter_vector
            self._set_parameter_vector(new_parameter_vector)

        self._last_afterstate_value = self._next_afterstate_value
        self._last_afterstate_matrix = self._next_afterstate_matrix

    def set_learning_state(self, is_on):
        """Toggle learning and exploration on and off.

        Args:
            is_on (boolean): If True, player will henceforth explore and update parameters.
                If False, it will not.
        """
        self._is_learning = is_on

    def _state_value(self, grid_matrix):
        """The estimated value of the given state matrix.

        This should depend on self._parameter_vector and be in sync with
        self._nabla_parameter_vector().

        MUST BE OVERRIDEN IN SUBCLASSES.

        Args:
            grid_matrix (np.array): The Connect Four grid as a matrix (as defined in connectfour.py)

        Returns:
            Estimated value of the state corresponding to the input matrix.
        """
        pass

    def _parameter_vector(self):
        """Return the parameter vector.

        MUST BE OVERRIDDEN IN SUBCLASS.

        Returns:
            The parameter vector used to estimate state values
        """
        pass

    def _set_parameter_vector(self, new_vector):
        """Set the parameter vector.

        MUST BE OVERRIDDEN IN SUBCLASS.

        Args:
            new_vector (np.array): The parameter vector for estimating state
                values.
        """
        pass

    def _nabla_parameter_vector(self, grid_matrix):
        """Nabla of state value func with respect to parameter vector in the
        state defined by grid_matrix.

        MUST BE OVERRIDDEN IN SUBCLASS

        Args:
            grid_matrix (np.array): The state point in which to calculate nabla.

        Returns:
            np.array. Nabla of state grid_matrix with respect to parameter vector.
        """
        pass

class SimpleFeaturePlayer(AfterStatePlayer):
    """Player using linear value approximation"""

    def __init__(self):
        """Init SimpleFeaturePlayer()"""
        super().__init__()
        self._alpha = 0.001
        # First 4 parameters are opportunities for the player; last 4 for the other player.
        # See calculation of features.
        self._parameters = np.concatenate([np.random.rand(4), -np.random.rand(4)])
        self._other_colour = None # Defined in set_player_colour

    def set_player_colour(self, colour):
        """Register the colour of the player."""
        self._other_colour = connectfour.other_colour(colour)
        return super().set_player_colour(colour)

    def _features(self, grid_matrix):
        """Return feature vector.

        Args:
            grid_matrix (np.array): The game grid as matrix

        Returns:
            Vector (np.array) of the feature values
        """
        # As features we use how many lines there are on the board containing N discs of
        # our colour and none of the other player's colour (N=1,...,4).
        # Also include those 4 numbers from the opponent's perspective.
        our_openings = connectfourutils.count_open_positions(grid_matrix, self._player_colour)[1:]
        opponents_openings = connectfourutils.count_open_positions(grid_matrix, self._other_colour)[1:]

        return np.concatenate([our_openings, opponents_openings])

    def _state_value(self, grid_matrix):
        """The estimated value of the given state matrix.


        Args:
            grid_matrix (np.array): The Connect Four grid as a matrix (as defined in connectfour.py)

        Returns:
            Estimated value of the state corresponding to the input matrix.
        """
        features = self._features(grid_matrix)
        parameter_vector = self._parameter_vector()
        return np.dot(features, parameter_vector)

    def _parameter_vector(self):
        """Return the parameter vector.

        Returns:
            The parameter vector used to estimate state values
        """
        return self._parameters

    def _set_parameter_vector(self, new_vector):
        """Set the parameter vector.

        Args:
            new_vector (np.array): The parameter vector for estimating state
                values.
        """
        self._parameters = new_vector

    def _nabla_parameter_vector(self, grid_matrix):
        """Nabla of state value func with respect to parameter vector in the
        state defined by grid_matrix.

        Args:
            grid_matrix (np.array): The state point in which to calculate nabla.

        Returns:
            np.array. Nabla of state grid_matrix with respect to parameter vector.
        """
        return self._features(grid_matrix)

class AdvancedFeaturePlayer(AfterStatePlayer):
    """Playing using linear function approximation and experience replay"""

    def __init__(self):
        super().__init__()
        self._other_colour = None
        self._number_experiences_remembered = 1000
        self._episode_size = 100
        self._learning_frequency = 100
        self._experiences = []
        self._parameters = np.concatenate([np.random.rand(4), -np.random.rand(4)])

    def set_player_colour(self, colour):
        """Register the colour of the player."""
        self._other_colour = connectfour.other_colour(colour)
        return super().set_player_colour(colour)

    def receive_reward(self, reward):
        """Record the reward for the last move.

        Args:
            reward: The reward for the last move
        """

        if self._last_afterstate_matrix is not None:
            self._experiences.append((self._last_afterstate_matrix, self._next_afterstate_matrix, reward))

        # Update the parameters for the self._last_afterstate_matrix state
        # unless we are explicitly not learning or it's the reward after the
        # first move in which case there is no previous afterstate.

        if self._is_learning and len(self._experiences)%self._learning_frequency == 0 and len(self._experiences) != 0:
            if len(self._experiences) > self._number_experiences_remembered:
                self._experiences = self._experiences[-self._number_experiences_remembered:]

            episode_experiences = random.sample(self._experiences, min(self._episode_size, len(self._experiences)))

            feature_matrix = []
            target_values = []
            for last_matrix, next_matrix, reward in episode_experiences:
                target_values.append(self._state_value(next_matrix)+reward)
                feature_matrix.append(self._features(last_matrix))

            target_values = np.array(target_values)
            feature_matrix = np.array(feature_matrix)

            parameters = self._parameter_vector()
            nabla_error = 2 * np.dot(feature_matrix.T, np.dot(feature_matrix, parameters) - target_values)

            delta_parameter_vector = - self._alpha * nabla_error
            new_parameter_vector = parameters + delta_parameter_vector
            self._set_parameter_vector(new_parameter_vector)

        self._last_afterstate_value = self._next_afterstate_value
        self._last_afterstate_matrix = self._next_afterstate_matrix

    def _features(self, grid_matrix):
        """Return feature vector.

        Args:
            grid_matrix (np.array): The game grid as matrix

        Returns:
            Vector (np.array) of the feature values
        """
        # As features we use how many lines there are on the board containing N discs of
        # our colour and none of the other player's colour (N=1,...,4).
        # Also include those 4 numbers from the opponent's perspective.
        # Try to normalize each feature so its magnitude is about 1
        multiplier = np.array([0.05, 0.2, 0.8, 1])
        our_openings = connectfourutils.count_open_positions(grid_matrix, self._player_colour)[1:] * multiplier
        opponents_openings = connectfourutils.count_open_positions(grid_matrix, self._other_colour)[1:] * multiplier

        return np.concatenate([our_openings, opponents_openings])

    def _state_value(self, grid_matrix):
        """The estimated value of the given state matrix.


        Args:
            grid_matrix (np.array): The Connect Four grid as a matrix (as defined in connectfour.py)

        Returns:
            Estimated value of the state corresponding to the input matrix.
        """
        features = self._features(grid_matrix)
        parameter_vector = self._parameter_vector()
        return np.dot(features, parameter_vector)

    def _parameter_vector(self):
        """Return the parameter vector.

        Returns:
            The parameter vector used to estimate state values
        """
        return self._parameters

    def _set_parameter_vector(self, new_vector):
        """Set the parameter vector.

        Args:
            new_vector (np.array): The parameter vector for estimating state
                values.
        """
        self._parameters = new_vector

    def _nabla_parameter_vector(self, grid_matrix):
        """Nabla of state value func with respect to parameter vector in the
        state defined by grid_matrix.

        Args:
            grid_matrix (np.array): The state point in which to calculate nabla.

        Returns:
            np.array. Nabla of state grid_matrix with respect to parameter vector.
        """
        return self._features(grid_matrix)


def test_simplefeatureplayer():
    """Run match of 2 SimpleFeaturePlayer() instances"""
    import connectfourgame
    player_white = SimpleFeaturePlayer()
    player_red = SimpleFeaturePlayer()
    match = connectfourgame.ConnectFourMatch(player_white, player_red)
    match.play()

def test_advancedfeatureplayer():
    """Run match of 2 AdvancedFeaturePlayer() instances"""
    import connectfourgame
    player_white = AdvancedFeaturePlayer()
    player_red = AdvancedFeaturePlayer()
    match = connectfourgame.ConnectFourMatch(player_white, player_red)
    match.play()

def test():
    """Execute all tests for this module"""
    test_simplefeatureplayer()

if __name__ == '__main__':
    test()

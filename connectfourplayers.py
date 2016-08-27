"""Player classes for the ConnectFour game.

A player class must implement the following methods:
    propose_move(self, game_grid, player_colour):
        game_grid: instance of ConnectFour() giving current game positions
        player_colour: the colour of the player

        Must return int signifying the column to which to add a disc

    receive_reward(self, reward):
        reward: integer signifying reward for last move (the higher the better)

Classes:
    RandomPlayer
"""
import random

class RandomPlayer:
    """A player making a random legal move each turn."""

    def propose_move(self, game_grid, player_colour):
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

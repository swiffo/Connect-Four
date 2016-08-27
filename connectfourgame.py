"""The structure around a match.

Classes:
    ConnectFourMatch
"""
import connectfour
import connectfourplayers

REWARD_DRAW = 0
REWARD_LEGAL_MOVE = 0
REWARD_ILLEGAL_MOVE = -2
REWARD_LOSS = -1
REWARD_WIN = 1

class ConnectFourMatch:
    """Implements the architecture around a Connect Four match.
    """

    def __init__(self, player_white, player_red):
        """Init ConnectFourMatch() with players.

        Args:
            player_white: player object for white discs (goes first)
            player_red: player object for red discs (goes second)
        """

        self._player_white = player_white
        self._player_red = player_red

    def play(self):
        """Play match of Connect Four"""

        max_number_of_moves = connectfour.ROWS * connectfour.COLUMNS
        players = ((self._player_white, connectfour.WHITE), (self._player_red, connectfour.RED))
        game_grid = connectfour.ConnectFour()

        for move_number in range(max_number_of_moves):
            current_player, current_colour = players[move_number%2]
            move = current_player.propose_move(game_grid, current_colour)
            try:
                game_grid.add_disc(move, current_colour)
            except connectfour.IllegalMove:
                current_player.receive_reward(REWARD_ILLEGAL_MOVE)
                other_player = players[(move_number+1)%2][0]
                other_player.receive_reward(REWARD_WIN)
                break

            if game_grid.winner() is not None:
                current_player.receive_reward(REWARD_WIN)
                other_player = players[(move_number+1)%2][0]
                other_player.receive_reward(REWARD_LOSS)
                break
            else:
                current_player.receive_reward(REWARD_LEGAL_MOVE)
        else:
            for player, dummy_colour in players:
                player.receive_reward(REWARD_DRAW)


def test_random_players():
    """Tests whether a game can be played without raising exceptions"""
    match = ConnectFourMatch(connectfourplayers.RandomPlayer(), connectfourplayers.RandomPlayer())
    match.play()

if __name__ == '__main__':
    test_random_players()

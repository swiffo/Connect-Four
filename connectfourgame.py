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

        player_white.set_player_colour(connectfour.WHITE)
        player_red.set_player_colour(connectfour.RED)
        self._player_white = player_white
        self._player_red = player_red

    def play(self):
        """Play match of Connect Four. Return colour of winner.

        Each player will have alternately propose_move and receive_reward called in that order
        and the same amount of times. That is, the last a player experiences of a game is always
        a call to receive_reward and it always starts with propose_move.

        Returns:
            Colour of winner (connectfour -> RED/WHITE) or None in case of draw.
        """

        max_number_of_moves = connectfour.ROWS * connectfour.COLUMNS
        players = ((self._player_white, connectfour.WHITE), (self._player_red, connectfour.RED))
        game_grid = connectfour.ConnectFour()

        for move_number in range(max_number_of_moves):
            current_player, current_colour = players[move_number%2]
            other_player, other_colour = players[(move_number+1)%2]

            move = current_player.propose_move(game_grid)

            try:
                game_grid.add_disc(move, current_colour)
            except connectfour.IllegalMove:
                current_player.receive_reward(REWARD_ILLEGAL_MOVE)
                other_player.receive_reward(REWARD_WIN)
                return other_colour

            if game_grid.winner() is not None:
                current_player.receive_reward(REWARD_WIN)
                other_player.receive_reward(REWARD_LOSS)
                return current_colour
            else:
                # If this is the last move of the game, we have a draw 
                if move_number == max_number_of_moves - 1:
                    current_player.receive_reward(REWARD_DRAW)
                    other_player.receive_reward(REWARD_DRAW)
                    return None
                # Otherwise the other player is simply rewarded with REWARD_LEGAL_MOVE
                else:
                    other_player.receive_reward(REWARD_LEGAL_MOVE)

        # Note that we should never reach this line (if we do the code is wrong)

def test_random_players():
    """Tests whether a game can be played without raising exceptions"""
    match = ConnectFourMatch(connectfourplayers.RandomPlayer(), connectfourplayers.RandomPlayer())
    match.play()

def test():
    """Execute full test suite"""
    test_random_players()

if __name__ == '__main__':
    test()

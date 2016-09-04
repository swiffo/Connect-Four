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

    def play(self, verbose=False):
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
                # Only reward a player if he has moved to preserve the contract that
                # we always call propose_move and receive_reward in that order
                if move_number > 0:
                    other_player.receive_reward(REWARD_WIN)

                if verbose:
                    print('Bad move: {}'.format(move))
                    print('Winner is {}'.format(other_colour))
                    print(game_grid)

                return other_colour

            if game_grid.winner() is not None:
                current_player.receive_reward(REWARD_WIN)
                other_player.receive_reward(REWARD_LOSS)

                if verbose:
                    print('Winner is {}'.format(current_colour))
                    print(game_grid)

                return current_colour
            else:
                # If this is the last move of the game, we have a draw
                if move_number == max_number_of_moves - 1:
                    current_player.receive_reward(REWARD_DRAW)
                    other_player.receive_reward(REWARD_DRAW)
                    if verbose:
                        print('Draw')
                        print(game_grid)
                    return None
                # Otherwise the other player is simply rewarded with REWARD_LEGAL_MOVE
                else:
                    if move_number > 0:
                        other_player.receive_reward(REWARD_LEGAL_MOVE)

        # Note that we should never reach this line (if we do the code is wrong)

def test_random_players():
    """Tests whether a game can be played without raising exceptions"""
    match = ConnectFourMatch(connectfourplayers.RandomPlayer(), connectfourplayers.RandomPlayer())
    match.play()

def test_method_call_sequence():
    """Test whether propose_move and receive_reward are called in alternating sequence.

    The contract is that the propose_move and receive_reward are called one after the
    other, beginning with propose_move, and the same number of times in total.

    This tests that contract.
    """
    class AssertiveRandomPlayer(connectfourplayers.RandomPlayer):
        """On the fly class for testing method call sequence"""
        def __init__(self):
            super().__init__()
            self.propose_move_call_count = 0
            self.receive_reward_call_count = 0
            self._colour = None

        def set_player_colour(self, colour):
            self._colour = colour

        def propose_move(self, game_grid):
            self.propose_move_call_count += 1
            assert self.propose_move_call_count == self.receive_reward_call_count + 1
            return super().propose_move(game_grid)

        def receive_reward(self, reward):
            self.receive_reward_call_count += 1
            assert self.receive_reward_call_count == self.propose_move_call_count
            return super().receive_reward(reward)

    player1 = AssertiveRandomPlayer()
    player2 = AssertiveRandomPlayer()
    match = ConnectFourMatch(player1, player2)
    match.play()
    assert player1.propose_move_call_count > 0
    assert player2.propose_move_call_count > 0
    assert player1.propose_move_call_count == player1.receive_reward_call_count
    assert player2.propose_move_call_count == player2.receive_reward_call_count


def test():
    """Execute full test suite"""
    test_random_players()
    test_method_call_sequence()

if __name__ == '__main__':
    test()

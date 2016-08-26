"""Connect Four gameboard.

Classes:
    ConnectFour: Gameboard with rules inherent

Exceptions:
    Error: Module base exception (never raised directly)
    IllegalMove: Exception signalling illegal move (e.g., adding disc to full column)
"""
import numpy as np

ROWS = 6
COLUMNS = 7

EMPTY = 0
WHITE = 1
RED = 2

PLAYER_WHITE = 0
PLAYER_RED = 1

def _entry_to_character(entry):
    """Convert grid entry (cell) to displayable character.

    Args:
        entry: One of EMPTY, WHITE and RED

    Returns:
        Single character used for display purposes
    """
    if entry == EMPTY:
        return '.'
    elif entry == WHITE:
        return 'W'
    elif entry == RED:
        return 'R'
    else:
        raise ValueError('Unknown grid entry')

class ConnectFour:
    """The grid for the game 'Connect Four'. Implements rules and moves.
    """

    def __init__(self):
        """Init ConnectFour()"""

        # Position (0, 0) is interpreted as lower left
        self._grid = np.full((ROWS, COLUMNS), EMPTY, dtype='i1')

        self._winner = None

    def legal_moves(self):
        """Return the legal moves.

        Returns:
            List of columns with room for at least one more disc
        """

        return [col for col in range(COLUMNS) if self._grid[ROWS-1, col] == EMPTY]

    def add_disc(self, column, colour):
        """Add disc to game grid

        Args:
            column: The column to which to add a disc (must be one of the constants, RED/WHITE)
            colour: The colour of the added disc

        Returns:
            None
        """
        for row in range(ROWS):
            if self._grid[row, column] == EMPTY:
                self._grid[row, column] = colour
                if self._check_winner_at_location(row, column):
                    self._winner = colour
                break
        else:
            raise IllegalMove

    def state_identifier(self):
        """Return hashable identifier

        Returns:
            A hashable identifier for the state of the grid.
        """

        column_identifiers = []

        for column in range(COLUMNS):
            column_identifier = 0
            row_multiplier = 1
            for colour in self._grid[:, column]:
                if colour == WHITE:
                    column_identifier += 2 * row_multiplier
                elif colour == RED:
                    column_identifier += row_multiplier
                else:
                    break
                row_multiplier *= 3
            column_identifiers.append(column_identifier)

        identifier = tuple(column_identifiers)

        return identifier

    def next_state_identifier(self, column, colour):
        """Return hashable identifier for the state following the specified move.

        Returns:
            Hashable identifier of the state that follows from the current grid state
                if a disc of the specified colour is dropped into the specified
                column
        """

        # TODO: Ensure consistency between this method and state_identifier

        for row in range(ROWS):
            if self._grid[row, column] == EMPTY:
                break
        else:
            raise IllegalMove

        identifier = self.state_identifier()
        if colour == WHITE:
            additional_identifier = 2 * 3**row
        elif colour == RED:
            additional_identifier = 3**row
        else:
            raise ValueError('Unhandled colour')

        identifier = list(identifier)
        identifier[column] += additional_identifier
        identifier = tuple(identifier)

        return identifier

    def winner(self):
        """Return winner of the game

        Returns:
            Winner of the game (PLAYER_WHITE or PLAYER_RED) if there is a winner.
            Otherwise returns None.
        """
        return self._winner

    def _check_winner_at_location(self, row, column):
        """Check whether there are 4 in a row involving the disc at the
        specified location.

        Returns:
            Boolean indicating whether the specified location is part of
            four in a row.
        """

        colour_at_location = self._grid[row, column]
        if colour_at_location == EMPTY:
            return False

        for x_jump, y_jump in [(1, 0), (0, 1), (1, 1), (1, -1)]:
            same_colour_in_sequence_count = 1
            for direction in [1, -1]:
                x_pos, y_pos = row, column
                x_jump *= direction
                y_jump *= direction

                while True:
                    x_pos += x_jump
                    y_pos += y_jump
                    try:
                        new_colour = self._grid[x_pos, y_pos]
                    except IndexError:
                        break

                    if new_colour == colour_at_location:
                        same_colour_in_sequence_count += 1
                    else:
                        break
            if same_colour_in_sequence_count >= 4:
                return True

        # If we have made it here, it means no winning condition is satisfied
        return False

    def __str__(self):
        """Grid as string

        Returns:
            The game grid as a string
        """
        lines = []
        for row in range(ROWS-1, -1, -1):
            lines.append(''.join(map(_entry_to_character, self._grid[row, :])))

        return '\n'.join(lines)

class Error(Exception):
    """Module base error"""

class IllegalMove(Error):
    """Indicates illegal move.

    An illegal move would be to add a disc to a full column or a non-existing column
    """
    pass

def test():
    """Run simple tests of the module."""

    # Test winner and state identifier
    game = ConnectFour()
    assert game.legal_moves() == list(range(COLUMNS))
    assert game.winner() is None

    last_state_id = None
    for column, disc_colour in [(3, WHITE), (2, RED), (4, WHITE), (1, RED), (5, WHITE), (0, RED)]:
        next_state_id = game.next_state_identifier(column, disc_colour)
        game.add_disc(column, disc_colour)

        state_id = game.state_identifier()
        assert state_id != last_state_id
        assert next_state_id == state_id
        last_state_id = state_id
        assert game.legal_moves() == list(range(COLUMNS))
        assert game.winner() is None

    game.add_disc(6, WHITE)
    assert game.winner() == WHITE

    # Test legal_moves
    game = ConnectFour()
    assert game.legal_moves() == list(range(COLUMNS))

    colour = None
    for _move in range(ROWS):
        if colour == RED:
            colour = WHITE
        else:
            colour = RED

        game.add_disc(3, colour)

    assert game.legal_moves() == [column for column in range(COLUMNS) if column != 3]


if __name__ == '__main__':
    test()

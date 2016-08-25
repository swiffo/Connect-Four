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
        self._grid = np.full((ROWS, COLUMNS), EMPTY, dtype='i1')

        hash_matrix = np.empty((ROWS, COLUMNS), dtype='i8')
        for row in range(ROWS):
            for col in range(COLUMNS):
                hash_matrix[row, col] = 3**(row+col*ROWS)

        self._hash_matrix = hash_matrix

        self._winner = None

    def legal_moves(self):
        """Return the legal moves.

        Returns:
            List of columns with room for at least one more disc
        """

        return [col for col in range(COLUMNS) if self._grid[ROWS-1, col] != EMPTY]

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
            An hashable identifier for the state of the grid.
        """
        return np.sum(self._hash_matrix * self._grid)

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

        present_identifier = self.state_identifier()
        next_identifier = present_identifier + self._hash_matrix[row, column] * colour

        return next_identifier

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

        colour = self._grid[row, column]

        # vertical
        vertical_count = 1
        for check_row in range(row-1, -1, -1):
            if self._grid[check_row, column] == colour:
                vertical_count += 1
            else:
                break

        for check_row in range(row+1, ROWS):
            if self._grid[check_row, column] == colour:
                vertical_count += 1
            else:
                break

        if vertical_count >= 4:
            return True

        # horizontal_count
        horizontal_count = 1
        for check_column in range(column-1, -1, -1):
            if self._grid[row, check_column] == colour:
                horizontal_count += 1
            else:
                break

        for check_column in range(column+1, COLUMNS):
            if self._grid[row, check_column] == colour:
                horizontal_count += 1
            else:
                break

        if horizontal_count >= 4:
            return True

        # lower-left, upper-right diagonal
        slash_count = 1
        for check_row, check_column in zip(range(row+1, ROWS), range(column+1, COLUMNS)):
            if self._grid[check_row, check_column] == colour:
                slash_count += 1
            else:
                break

        for check_row, check_column in zip(range(row-1, -1, -1), range(column-1, -1, -1)):
            if self._grid[check_row, check_column] == colour:
                slash_count += 1
            else:
                break

        if slash_count >= 4:
            return True

        # upper-left, lower-right diagonal
        backslash_count = 1
        for check_row, check_column in zip(range(row+1, ROWS), range(column-1, -1, -1)):
            if self._grid[check_row, check_column] == colour:
                backslash_count += 1
            else:
                break

        for check_row, check_column in zip(range(row-1, -1, -1), range(column+1, COLUMNS)):
            if self._grid[check_row, check_column] == colour:
                backslash_count += 1
            else:
                break

        if backslash_count >= 4:
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

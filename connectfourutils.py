"""Functions related to Connect Four"""

import numpy as np
import connectfour

def _count_element(array, element):
    """Count occurrences of element in array.

    Args:
        array (np.array): 1-dimensional np.array
        element: any object that can be in an np.array

    Returns:
        How many times element occurs in array (int)
    """
    count = 0
    for entry in array:
        if entry == element:
            count += 1

    return count

def count_open_positions(game_grid, player_colour):
    """Count number of possible 4-in-a-row sequences bucketed by how many cells
    are filled in with the player's colour.

    Args:
        game_grid (np.array): a 2-dimensional array specifying the grid of Connect
            Four. Entries must be RED, WHITE or EMPTY as defined in connectfour.py.
        player_colour: The colour belonging to the player (RED or WHITE).

    Returns:
        An np.array of shape (5). Entry n indicates the number of lines of 4 (horizontal,
        vertical or diagonal) that have n discs of specified player colour and the rest
        empty.
    """
    if player_colour == connectfour.RED:
        other_colour = connectfour.WHITE
    else:
        other_colour = connectfour.RED

    counts = np.zeros(5)

    flat_game_grid = game_grid.reshape(game_grid.size)
    num_rows, num_cols = game_grid.shape

    for row in range(num_rows):
        for col in range(num_cols):
            for direction in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                # Do the four jumps exceed the grid boundaries? If so skip to next
                if (row + 3 * direction[0] >= num_rows or col + 3 * direction[1] >= num_cols
                        or col + 3 * direction[1] < 0):
                    continue

                start = row * num_cols + col
                jump = direction[0]*num_cols + direction[1]

                indices = [index for index in range(start, start + 4 * jump, jump)
                           if index >= 0 and index < game_grid.size]
                entries = flat_game_grid[indices]

                if other_colour in entries:
                    continue
                else:
                    player_colour_count = _count_element(entries, player_colour)
                    counts[player_colour_count] += 1

    return counts

def test_count_open_positions():
    """Test count_open_positions function"""

    game_grid = np.full((4, 4), connectfour.EMPTY, dtype=np.int)
    assert all(count_open_positions(game_grid, connectfour.WHITE) == [10, 0, 0, 0, 0])
    game_grid[0, 0] = connectfour.WHITE
    assert all(count_open_positions(game_grid, connectfour.WHITE) == [7, 3, 0, 0, 0])
    game_grid[0, 1] = connectfour.RED
    assert all(count_open_positions(game_grid, connectfour.RED) == [6, 1, 0, 0, 0])
    game_grid[:, 1] = np.full(4, connectfour.RED, dtype=np.int)
    assert all(count_open_positions(game_grid, connectfour.RED) == [2, 4, 0, 0, 1])

def test():
    """Run all tests"""
    test_count_open_positions()

if __name__ == '__main__':
    test()

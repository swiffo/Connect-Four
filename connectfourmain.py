"""Main entry point to the connectfour infrastructure.

This contains the code for interacting with the user.
"""

import connectfourgame
import connectfourplayers

def train_players(player_white, player_red, number_of_matches):
    """Play specified number of matches between player_white and player_red

    Args:
        player_white: The player object playing white (goes first)
        player_red: The player object playing red
        number_of_matches: Number of matches to play

    Returns:
        None
    """

    match = connectfourgame.ConnectFourMatch(player_white, player_red)
    for match_count in range(1, number_of_matches+1):
        match.play()
        if match_count%100 == 0:
            print('Has trained {} times'.format(match_count))

def choose_player():
    """Ask user to choose a player object.

    Returns:
        Instance of chosen player class.
    """
    print('Choices:')
    print('(R)andom player')
    print('(H)uman player')
    print('(S)imple player')

    while True:
        choice = input().upper()
        if choice == 'R':
            return connectfourplayers.RandomPlayer()
        elif choice == 'H':
            return connectfourplayers.HumanPlayer()
        elif choice == 'S':
            return connectfourplayers.SimpleFeaturePlayer()


def main():
    """..."""
    print('WHITE PLAYER')
    player_white = choose_player()
    print('RED PLAYER')
    player_red = choose_player()
    num_training_matches = int(input('How many training matches?'))
    train_players(player_white, player_red, num_training_matches)

    while True:
        human_player = connectfourplayers.HumanPlayer()
        match = connectfourgame.ConnectFourMatch(human_player, player_red)
        match.play()

        match = connectfourgame.ConnectFourMatch(player_white, human_player)
        match.play()

        continue_playing = input('Play again? (Y/N)')
        if not continue_playing == 'Y':
            break

main()

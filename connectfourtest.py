"""Full test suite for Connect Four"""

import connectfour
import connectfourgame
import connectfourplayers

def full_test():
    """Run all tests for Connect Four"""
    connectfour.test()
    connectfourgame.test()
    connectfourplayers.test()

if __name__ == '__main__':
    full_test()

"""Pynsour Bootstrap"""

import sys
from src import *

def main(argv):
    pynsour = Pynsour('config/bot.yaml')
    return pynsour.run()

if __name__ == "__main__":
    sys.exit(main(sys.argv))

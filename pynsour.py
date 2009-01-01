"""Bootstrap file
"""

import sys
from app import *

def main(argv):
    pynsour = Pynsour('conf/bot.yaml')
    return pynsour.run()

if __name__ == "__main__":
    sys.exit(main(sys.argv))

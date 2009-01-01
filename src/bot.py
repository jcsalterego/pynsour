"""Bot class"""

import os
from pprint import pprint

class Bot:
    def __init__(self):
        self.__load_defaults()

    def __load_defaults(self):
        self.username = os.getlogin()
        self.password = None
        self.nicks = ["nick", "altnick"]
        self.realname = "Default pynsour user"
        self.handlers = []

    def asDict(self):
        """Return object as dictionary

        Ignores doc variables
        """
        info = {}
        for attr in dir(self):
            if attr[0] == "_" or attr[:2] == "__":
                continue

            i = getattr(self, attr)
            if type(i).__name__ == "instancemethod":
                continue
            else:
                info[attr] = i
        return info

    def event(self):
        print ""

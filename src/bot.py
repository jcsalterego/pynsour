"""Bot class
"""

class Bot:
    def __init__(self):
        self.config = Config()
        self.__load_defaults()

    def __load_defaults(self):
        self.username = username
        self.password = ""
        self.nicks = ""
        self.name = ""


import bot
import os.path
import sys
import yaml

class Pynsour:
    def __init__(self, config_file):
        if not os.path.exists(config_file):
            # this should throw an exception
            # but let's just be messy for the time being
            print("Config file does not exist!")
            sys.exit(1)
        
        # otherwise, load the configuration
        self.config = Config()
        print self.config.read(config_file)
            
all = ['config', 'bot']

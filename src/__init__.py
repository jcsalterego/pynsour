"""Pynsour Initialization"""

from config import Config
from events import Events
import bot
import os.path
import sys
import yaml

class Pynsour:
    def __init__(self, config_file):
        if not os.path.exists(config_file):
            # this should throw an exception
            # but let's just be messy for the time being
            print("Config file '%s' does not exist!" % config_file)
            sys.exit(1)
        
        # otherwise, load the configuration
        self.bot = bot.Bot()
        conf = Config(config_file)
        conf.push(self.bot)

        self.events = Events(self.bot)
        
    def run(self):
        self.events.run()
            
all = ['config', 'bot']

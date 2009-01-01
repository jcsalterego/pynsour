"""Pynsour Initialization"""

from config import Config
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
        
    def run(self):
        self.bot.run()
            
all = ['config', 'bot']

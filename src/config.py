"""Configuration

Read config file
"""
from pprint import pprint
import botcode
import re
import sys
import yaml

class Config:
    def __init__(self, file_):
        self.data = self.read(file_)

        # sanity checks go here
        if 'version' not in self.data or self.data['version'] != 1:
            print("Incorrect or missing configuration version number!")
            sys.exit(1)
                
    def push(self, bot):
        """Push the configuration to a bot
        """
        conf = self.data

        fields = ("name", "nicks", "version")
        for field in fields:
            if field in conf:
                setattr(bot, field, conf[field])
        
        # in conf v1, use connections[0], ignoring the rest
        if ('connections' in conf
            and type(conf['connections']) == list
            and len(conf['connections']) > 0):
            
            # connection fields
            fields = ("hostname",
                      "name",
                      "port",
                      "realname",
                      "username",
                      "nicks",
                      "on_connect",
                      "mode")
            for field in fields:
                if field in conf['connections'][0]:

                    # lazy type checking
                    if ((field == "nicks"
                         and type(conf['connections'][0][field]) != list)
                        or (field == "port"
                            and type(conf['connections'][0][field]) != int)
                        or (field == "on_connect"
                            and type(conf['connections'][0][field]) != list)):
                        continue

                    if field in ("on_connect", "mode"):
                        setattr(bot, field,
                                self.process_ops(conf['connections'][0][field]))
                    else:
                        setattr(bot, field, conf['connections'][0][field])

        # handler fields
        if 'handlers' in conf and type(conf['handlers']) == list:
            for handler in conf['handlers']:
                if 'channel' in handler and 'script' in handler:
                    # precompile regex
                    handler['channel_re'] = re.compile(handler['channel'])
                    bot.handlers.append(handler)

        # pprint(bot.asDict())

    @staticmethod
    def process_ops(instructions):
        """Convert configuration directives into botcodes
        """
        ops = []

        for instruction in instructions:
            words = [word for word in instruction.split(" ") if word]

            words[0] = words[0].upper()
            args = words[1:]

            if words[0] == botcode.OP_JOIN:
                if len(args) > 0:
                    ops += (botcode.OP_JOIN, args[0]),
            elif words[0] == botcode.OPMODE:
                if len(args) > 0:
                    ops += (botcode.OP_MODE, args[0]),

        return ops

    @staticmethod
    def read(file_):
        data = yaml.load(open(file_))
        return data

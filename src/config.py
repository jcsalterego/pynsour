"""Configuration

Read config file
"""
import re
import yaml

class Config:
    def __init__(self, file_):
        self.data = self.read(file_)

        # sanity checks go here
        if 'version' not in self.data or self.data['version'] != 1:
            print("Incorrect or missing configuration version number!")
            sys.exit(1)
                
    def push(self, bot):
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
                      "nicks",)
            for field in fields:
                if field in conf['connections'][0]:

                    # lazy type checking
                    if ((field == "nicks"
                         and type(conf['connections'][0][field]) != list)
                        or (field == "port"
                            and type(conf['connections'][0][field]) != int)):
                        continue

                    setattr(bot, field, conf['connections'][0][field])

        # handler fields
        if 'handlers' in conf and type(conf['handlers']) == list:
            for handler in conf['handlers']:
                if ('channel' in handler and 'script' in handler):
                    # precompile regex
                    handler['channel_re'] = re.compile(handler['channel'])
                    bot.handlers.append(handler)

    @staticmethod
    def read(file_):
        data = yaml.load(open(file_))
        return data

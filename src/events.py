"""Events Manager"""

import time

class Events:
    def __init__(self, bot):
        self.bot = bot

    def run(self):
        while True:
            time.sleep(0.75)
            try:
                self.bot.event()
            except KeyboardInterrupt, e:
                raise e
            except Exception, e:
                raise e

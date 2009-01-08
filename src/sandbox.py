"""Sandbox"""

import __builtin__
import botcode
import new
import os

SCRIPT_ROOT = "./scripts/"

class Sandbox:        
    """Sandbox

    Creates an isolated environment for scripts to execute
    """
    def __init__(self):
        """Constructor
        """
        pass

    def execute(self, script_ops):
        ops = []

        for script_op in script_ops:
            op_code, script_path, args = script_op
            sender, action, recipient, msg = args

            script_path = "%s%s" % (SCRIPT_ROOT, script_path)

            if not os.path.exists(script_path):
                continue

            script = file(script_path).read()
            script = script.replace("\r", "") + "\n\n"
        
            try:
                compiled = compile(script, '<string>', 'exec')
            except:
                # script error
                ops += (botcode.OP_ERROR, (traceback.format_exc())),
                continue

            # set up a main module
            main = new.module('__main__')
            import __builtin__
            main.__builtins__ = __builtin__

            # add the parameters
            main.__dict__['sender'] = sender
            main.__dict__['recipient'] = recipient
            main.__dict__['action'] = action

            # shorthand parameters
            main.__dict__['from'] = sender
            main.__dict__['recp'] = recipient
            main.__dict__['cmd'] = action

            # irc module
            main.__dict__['irc'] = self.irc()

            # execute the code
            exec compiled in main.__dict__

            ops += main.__dict__['irc'].ops

        return ops

    class irc:
        """Interface for IRC
        """

        def __init__(self):
            self.ops = []

        def privmsg(self, recp, msg):
            """Private Message

            Sends a PRIVMSG to a channel or nick.
            """
            self.ops += (botcode.OP_PRIVMSG, recp, msg,),

        def notice(self, recp, msg):
            """Notice
            """
            self.ops += (botcode.OP_NOTICE, recp, msg,),

        def topic(self, channel, topic):
            """Sets a channel topic

            Implicitly requires the proper topic mode or
            sufficient privileges.
            """
            self.ops += (botcode.OP_TOPIC, channel, topic,),

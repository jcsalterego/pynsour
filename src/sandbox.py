"""Sandbox"""

import __builtin__
import botcode
import md5
import new
import os
import traceback

SCRIPT_ROOT = "./scripts/"

class Sandbox:        
    """Sandbox

    Creates an isolated environment for scripts to execute
    """
    def __init__(self):
        """Constructor
        """
        self.scripts = {}

    def execute(self, script_ops):
        ops = []

        for script_op in script_ops:
            op_code, script_path, args = script_op
            sender, action, recipient, msg = args

            script_path = "%s%s" % (SCRIPT_ROOT, script_path)
            if not os.path.exists(script_path):
                continue

            read_from_disk = True

            if (script_path in self.scripts
                and (self.scripts[script_path]['st_mtime'] ==
                     os.stat(script_path).st_mtime)):

                # don't reread from disk if it has a newer modified time
                read_from_disk = False

            if read_from_disk:
                script = file(script_path).read()
                script = script.replace("\r", "") + "\n\n"
                st_mtime = os.stat(script_path).st_mtime

                try:
                    compiled = compile(script, '<string>', 'exec')
                except:
                    # script error
                    ops += (botcode.OP_ERROR, (traceback.format_exc())),
                    continue

                # set up a main module
                main = new.module('__main__')
                main.__builtins__ = __builtin__

                self.scripts[script_path] = { 'compiled': compiled,
                                              'main': main,
                                              'script': script,
                                              'st_mtime': st_mtime }
            else:
                compiled = self.scripts[script_path]['compiled']
                main = self.scripts[script_path]['main']

            # add or update environment parameters
            main.__dict__['sender'] = Sandbox.User(sender)
            main.__dict__['recipient'] = recipient
            if recipient[0] == '#':
                main.__dict__['channel'] = recipient
            else:
                main.__dict__['channel'] = None

            main.__dict__['action'] = action
            main.__dict__['msg'] = msg
            main.__dict__['argv'] = [arg for arg in msg.split(" ") if arg]
                
            # shorthand parameters
            main.__dict__['recp'] = recipient
                
            # irc module
            main.__dict__['irc'] = Sandbox.Irc()

            # execute the code
            try:
                exec compiled in main.__dict__
                ops += main.__dict__['irc'].ops
            except:
                # script error
                ops += (botcode.OP_ERROR, (traceback.format_exc())),

        return ops

    class User:
        """Interface for User
        """
        def __init__(self, whois_info):
            """Constructor
            """
            self.nick = ""
            self.ident = ""
            self.has_ident = False
            self.hostname = ""

            # this could be done via regex but this will suffice for now
            words = whois_info.split("!", 1)
            if len(words) != 2:
                return

            self.nick, remainder = words

            words = remainder.split("@", 1)
            if len(words) != 2:
                return

            self.ident, self.hostname = words

            # not sure if the tilde is part of the RFC or just convention.
            self.has_ident = (self.ident[0] != "~")
            self.full = whois_info

        def __repr__(self):
            """Default representation is a nick
            """
            return self.nick

    class Irc:
        """Interface for IRC
        """

        def __init__(self):
            """Constructor
            """
            self.ops = []

        def reset(self):
            """Reset botcode ops
            """
            self.ops = []

        def msg(self, recp, msg):
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

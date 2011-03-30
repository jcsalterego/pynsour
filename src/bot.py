"""Bot class"""

import os
import socket

from parser import Parser
from logger import Logger
from sandbox import Sandbox
import botcode

MAX_CONSOLE_LEN = 50
BUFFER_SIZE = 1024
STATE_DISCONNECTED = 0
STATE_CONNECTING = 1
STATE_HANDSHAKE = 2
STATE_CONNECTED = 3
STATE_ONLINE = 4

class Bot:

    def __init__(self):
        """Constructor
        """
        self.__state = STATE_DISCONNECTED
        self.__load_defaults()
        self.parser = Parser()
        self.logger = Logger()
        self.sandbox = Sandbox()

    def __load_defaults(self):
        """Loads default settings
        """
        if os.name == "posix":
            self.username = os.getlogin()
        else:
            self.username = os.environ.get( "USERNAME" )
        self.password = None
        self.nicks = ["nick", "altnick"]
        self.realname = "Default pynsour user"
        self.handlers = []
        self.localhost = 'localhost'
        self.on_connect = []
        self.ops = []
        self.name = ""

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

    def connect(self):
        """Connect the bot to the IRC server
        """
        self.__state = STATE_CONNECTING
        self.__connection = socket.socket(socket.AF_INET,
                                          socket.SOCK_STREAM)
        self.logger.console("+++ Connecting to %s:%s" %
                            (self.hostname, self.port))
        self.__connection.connect((self.hostname, self.port))

    def event(self):
        """Event fire
        """
        if self.__state == STATE_DISCONNECTED:
            return
        elif self.__state == STATE_CONNECTING:
            if self.password:
                self.write("PASS %s" % self.password)
            self.write("NICK %s" % self.nicks[0])
            self.write("USER %s %s %s :%s" %
                       (self.username,
                        self.localhost,
                        self.hostname,
                        self.realname))

            self.__state = STATE_HANDSHAKE
        elif self.__state == STATE_HANDSHAKE:
            pass

        self.read()
        self.ops += self.parser.parse()
        self.execute()
    
    def execute(self):
        """Execute botcode
        """
        # Expand meta-ops, e.g. connect events
        new_ops = []
        for operation in self.ops:
            if operation[0] == botcode.OP_EVENT_CONNECT:
                new_ops += self.on_connect
                self.__state = STATE_ONLINE
            elif operation[0] == botcode.OP_EVENT_PRIVMSG:
                sandbox_ops = self.filter_eval(operation[1])
                if sandbox_ops:
                    new_ops += self.sandbox.execute(sandbox_ops)
            else:
                new_ops.append(operation)
        self.ops = new_ops

        while len(self.ops) > 0:
            new_ops = []
            for operation in self.ops:
                if operation[0] == botcode.OP_PONG:
                    self.write("PONG :%s" % operation[1])
                elif operation[0] == botcode.OP_JOIN:
                    if len(operation) == 2:
                        self.write("JOIN %s :%s" % operation[1])
                    elif len(operation) == 1:
                        self.write("JOIN %s" % operation[1])
                elif operation[0] == botcode.OP_MODE:
                    self.write("MODE %s" % operation[1])
                elif operation[0] == botcode.OP_PRIVMSG:
                    self.write("PRIVMSG %s :%s" % operation[1:3])
                elif operation[0] == botcode.OP_ERROR:
                    self.logger.console("ERR\n"
                                        "%s" % operation[1])
            self.ops = new_ops

        # self.ops will be empty by here

    def filter_eval(self, line):
        """Filter based on channel
        """
        ops = []
        words = line.split(":", 1)
        if len(words) == 1:
            return ops

        args, msg = words
        argv = args.split(" ")

        if len(argv) < 4:
            return ops

        sender, action, recipient = argv[:3]

        path = "%s/%s" % (self.name, recipient)
        
        for handler in self.handlers:
            re = handler['channel_re']
            if re.match(path):
                # self.logger.console("F: %s %s" % (path, argv))
                script_path = re.sub(handler['script'].replace("$", "\\"),
                                     path)
                ops += (botcode.OP_EVENT_SCRIPT,
                        script_path,
                        (sender, action, recipient, msg)),

        return ops

    def read(self):
        """Reading from connection
        """
        if self.__state > STATE_DISCONNECTED:
            incoming = self.__connection.recv(BUFFER_SIZE)
            self.parser.append(incoming)

            read_bytes = len(incoming)

            first_line = incoming.split("\n")[0]
            if len(first_line) > MAX_CONSOLE_LEN:
                first_line = "%s..." % first_line[:MAX_CONSOLE_LEN]
            self.logger.console(" IN [%4d] %s" % (read_bytes,
                                                  first_line))

    def write(self, outgoing):
        """Writing to connection
        """
        first_line = outgoing

        outgoing = "".join((outgoing, "\r\n"))
        write_bytes = len(outgoing)

        if len(first_line) > MAX_CONSOLE_LEN:
            first_line = "%s..." % first_line[:MAX_CONSOLE_LEN]
        self.logger.console("OUT [%4d] %s" % (write_bytes,
                                              first_line))
        self.__connection.send(outgoing)
